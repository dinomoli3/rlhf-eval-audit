"""Simple, explicit statistics for a paired binary evaluation."""

import csv
import math
import random
from collections import Counter
from pathlib import Path


class AuditError(ValueError):
    """Invalid evaluation data or configuration."""


def load_pairs(path: str | Path, group_a: str, group_b: str) -> list[tuple[int, int]]:
    if not group_a or not group_b or group_a == group_b:
        raise AuditError("Choose two different, nonempty group labels")
    pairs: dict[str, dict[str, int]] = {}
    try:
        with open(path, newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise AuditError("CSV must have a header without duplicate columns")
            if not {"pair_id", "group", "outcome"}.issubset(reader.fieldnames):
                raise AuditError("CSV needs pair_id, group, outcome columns")
            for line, row in enumerate(reader, start=2):
                if None in row:
                    raise AuditError(f"Row {line}: more values than header columns")
                pair_id, group, outcome = (row[k] for k in ("pair_id", "group", "outcome"))
                if not pair_id or not pair_id.strip():
                    raise AuditError(f"Row {line}: empty pair_id")
                if group not in (group_a, group_b):
                    raise AuditError(f"Row {line}: unexpected group {group!r}")
                if outcome not in ("0", "1"):
                    raise AuditError(f"Row {line}: outcome must be exactly 0 or 1")
                if group in pairs.setdefault(pair_id, {}):
                    raise AuditError(f"Row {line}: duplicate pair_id/group")
                pairs[pair_id][group] = int(outcome)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise AuditError(f"Could not read CSV: {exc}") from exc
    if not pairs:
        raise AuditError("CSV has no data rows")
    missing = sum(set(v) != {group_a, group_b} for v in pairs.values())
    if missing:
        raise AuditError(f"{missing} incomplete pair(s); both groups are required")
    return [(v[group_a], v[group_b]) for v in pairs.values()]


def _wilson(successes: int, n: int) -> list[float]:
    z = 1.959963984540054
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _sign_test(a_only: int, b_only: int) -> float | None:
    n = a_only + b_only
    if n == 0:
        return None
    k = min(a_only, b_only)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def audit(
    pairs: list[tuple[int, int]], group_a: str, group_b: str,
    *, min_pairs: int = 20, bootstrap_reps: int = 2000, seed: int = 42,
) -> dict:
    if min_pairs < 1 or bootstrap_reps < 1:
        raise AuditError("min_pairs and bootstrap_reps must be positive")
    if not pairs or any(len(p) != 2 or any(v not in (0, 1) for v in p) for p in pairs):
        raise AuditError("Expected nonempty pairs of binary outcomes")
    n = len(pairs)
    counts = Counter(pairs)
    a_success = sum(a for a, _ in pairs)
    b_success = sum(b for _, b in pairs)
    a_only, b_only = counts[(1, 0)], counts[(0, 1)]
    diffs = [a - b for a, b in pairs]
    rng = random.Random(seed)
    sampled = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(bootstrap_reps))
    lower = sampled[int((bootstrap_reps - 1) * 0.025)]
    upper = sampled[int((bootstrap_reps - 1) * 0.975)]
    return {
        "status": "REVIEW" if n >= min_pairs else "INSUFFICIENT_COVERAGE",
        "scope": "paired binary rubric outcomes; diagnostic, not a fairness or compliance finding",
        "pairs": n,
        "min_pairs": min_pairs,
        "groups": {
            group_a: {"successes": a_success, "rate": a_success / n, "wilson_95": _wilson(a_success, n)},
            group_b: {"successes": b_success, "rate": b_success / n, "wilson_95": _wilson(b_success, n)},
        },
        "paired_difference": (a_success - b_success) / n,
        "paired_bootstrap_95": [lower, upper],
        "bootstrap_reps": bootstrap_reps,
        "seed": seed,
        "flip_rate": (a_only + b_only) / n,
        "a_only": a_only,
        "b_only": b_only,
        "exact_two_sided_sign_p": _sign_test(a_only, b_only),
        "note": "Review rubric, run conditions, sampling, abstentions, and multiple comparisons before interpreting differences.",
    }
