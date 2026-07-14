#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assessment_core import (
    AssessmentError,
    evaluate,
    load_answers,
    load_catalog,
    render_json,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score a Java/Spring Boot modernization assessment."
    )
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument(
        "--catalog", type=Path, default=ROOT / "checklist" / "catalog.csv"
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Return exit code 2 when the decision is BLOCKED.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = evaluate(load_catalog(args.catalog), load_answers(args.assessment))
    except AssessmentError as exc:
        print(f"assessment error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        rendered = render_json(result)
    else:
        rendered = render_markdown(result, args.assessment.stem)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 2 if args.fail_on_blocked and result["decision"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
