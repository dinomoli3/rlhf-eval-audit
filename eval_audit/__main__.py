"""Command-line entry point."""

import argparse
import json
import sys
from pathlib import Path

from .core import AuditError, audit, load_pairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paired binary model-evaluation outcomes")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--group-a", required=True)
    parser.add_argument("--group-b", required=True)
    parser.add_argument("--min-pairs", type=int, default=20)
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", type=Path, help="Also write machine-readable report")
    args = parser.parse_args()
    try:
        pairs = load_pairs(args.csv_file, args.group_a, args.group_b)
        report = audit(pairs, args.group_a, args.group_b, min_pairs=args.min_pairs,
                       bootstrap_reps=args.bootstrap_reps, seed=args.seed)
        payload = json.dumps(report, indent=2)
        print(payload)
        if args.json:
            args.json.write_text(payload + "\n", encoding="utf-8")
    except (AuditError, OSError) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
