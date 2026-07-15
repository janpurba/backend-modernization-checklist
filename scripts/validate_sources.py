#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KNOWN_SOURCES = {
    "NIST-SSDF",
    "OWASP-SAMM",
    "OWASP-ASVS",
    "GOOGLE-SRE",
    "DORA",
    "SPRING-BOOT",
    "SPRING-BOOT-UPGRADE",
    "SPRING-FRAMEWORK",
    "JAVA-MIGRATION",
}
RELATIONSHIPS = {"inspired", "practitioner-synthesis"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    catalog_ids = {row["id"].strip() for row in read_rows(ROOT / "checklist" / "catalog.csv")}
    source_rows = read_rows(ROOT / "checklist" / "source-map.csv")
    source_ids = [row["id"].strip() for row in source_rows]

    errors: list[str] = []
    if len(source_ids) != len(set(source_ids)):
        errors.append("source map contains duplicate ids")

    missing = sorted(catalog_ids - set(source_ids))
    unknown = sorted(set(source_ids) - catalog_ids)
    if missing:
        errors.append(f"missing source mappings: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown source mappings: {', '.join(unknown)}")

    for row in source_rows:
        check_id = row["id"].strip()
        sources = {source.strip() for source in row["sources"].split(";")}
        unknown_sources = sorted(sources - KNOWN_SOURCES)
        if unknown_sources:
            errors.append(f"{check_id} has unknown sources: {', '.join(unknown_sources)}")
        if row["relationship"].strip() not in RELATIONSHIPS:
            errors.append(f"{check_id} has unsupported relationship")
        if not row["rationale"].strip():
            errors.append(f"{check_id} has no mapping rationale")

    if errors:
        for error in errors:
            print(f"source-map error: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(source_rows)} source mappings across {len(KNOWN_SOURCES)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
