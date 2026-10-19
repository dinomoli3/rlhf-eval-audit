"""Optional import of Inspect AI sample summaries into the paired audit."""

from pathlib import Path
from typing import Iterable

from .core import AuditError, pairs_from_rows


def pairs_from_summaries(
    summaries: Iterable[object], group_a: str, group_b: str, scorer: str
) -> list[tuple[int, int]]:
    """Use only metadata and one explicitly selected, numeric binary score."""
    if not scorer:
        raise AuditError("Select an Inspect scorer with --scorer")
    rows = []
    for index, sample in enumerate(summaries, start=1):
        if getattr(sample, "error", None):
            raise AuditError(f"Sample {index}: errored samples need separate review")
        metadata = getattr(sample, "metadata", None) or {}
        if not isinstance(metadata, dict):
            raise AuditError(f"Sample {index}: missing metadata")
        pair_id, group = metadata.get("pair_id"), metadata.get("group")
        scores = getattr(sample, "scores", None) or {}
        if scorer not in scores:
            raise AuditError(f"Sample {index}: scorer {scorer!r} is missing")
        value = scores[scorer].value
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value not in (0, 1):
            raise AuditError(f"Sample {index}: scorer value must be numeric 0 or 1")
        rows.append((index, pair_id, group, str(int(value))))
    return pairs_from_rows(rows, group_a, group_b)


def load_inspect_pairs(
    path: str | Path, group_a: str, group_b: str, scorer: str
) -> list[tuple[int, int]]:
    """Read Inspect's compact sample summaries without loading full transcripts."""
    try:
        from inspect_ai.log import read_eval_log_sample_summaries
    except ImportError as exc:
        raise AuditError("Install inspect-ai to read .eval or Inspect .json logs") from exc
    try:
        summaries = read_eval_log_sample_summaries(path)
    except Exception as exc:
        raise AuditError(f"Could not read Inspect log: {exc}") from exc
    return pairs_from_summaries(summaries, group_a, group_b, scorer)
