#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assessment_core import AssessmentError, load_catalog
from repository_scanner import (
    ScanError,
    build_inventory,
    collect_repository,
    load_source_map,
    prefill_assessment,
    render_scan_report,
    write_assessment,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Statically prefill a modernization assessment from a Java/Spring Boot repository."
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--catalog", type=Path, default=ROOT / "checklist" / "catalog.csv")
    parser.add_argument(
        "--source-map", type=Path, default=ROOT / "checklist" / "source-map.csv"
    )
    parser.add_argument("--max-files", type=int, default=10_000)
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        checks = load_catalog(args.catalog)
        source_map = load_source_map(args.source_map)
        view = collect_repository(
            args.repo,
            max_files=args.max_files,
            max_file_bytes=args.max_file_bytes,
        )
        inventory = build_inventory(view)
        prefills = prefill_assessment(view, inventory, checks, source_map)
        write_assessment(args.output, prefills)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(render_scan_report(inventory, prefills), encoding="utf-8")
    except (AssessmentError, ScanError, OSError, KeyError) as exc:
        print(f"scan error: {exc}", file=sys.stderr)
        return 1

    counts: dict[str, int] = {}
    for item in prefills:
        counts[item.status] = counts.get(item.status, 0) + 1
    summary = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    print(
        f"Scanned {inventory.repository_name}: {inventory.files_scanned} files; "
        f"wrote {len(prefills)} checks ({summary}) to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
