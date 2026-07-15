#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from assessment_core import load_catalog


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a conservative source-code modernization worksheet."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--catalog", type=Path, default=ROOT / "checklist" / "catalog.csv"
    )
    args = parser.parse_args()

    checks = load_catalog(args.catalog)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["id", "status", "evidence", "owner", "target_date", "notes"])
        for check in checks:
            writer.writerow(
                [
                    check.check_id,
                    "fail",
                    "Not assessed",
                    "",
                    "",
                    check.evidence_required,
                ]
            )
    print(f"Created {args.output} with {len(checks)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
