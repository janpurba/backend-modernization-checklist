from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


STATUS_SCORES = {
    "pass": 1.0,
    "partial": 0.5,
    "fail": 0.0,
    "unknown": 0.0,
    "na": None,
}
PRIORITY_WEIGHTS = {"critical": 5, "high": 3, "medium": 1}


class AssessmentError(ValueError):
    pass


@dataclass(frozen=True)
class Check:
    check_id: str
    domain: str
    priority: str
    description: str
    evidence_required: str
    recommended_action: str


@dataclass(frozen=True)
class Answer:
    check_id: str
    status: str
    evidence: str
    owner: str
    target_date: str
    notes: str


def load_catalog(path: Path) -> list[Check]:
    rows = _read_csv(path)
    required = {
        "id",
        "domain",
        "priority",
        "check",
        "evidence_required",
        "recommended_action",
    }
    _require_columns(rows, required, path)

    checks: list[Check] = []
    seen: set[str] = set()
    for row in rows:
        check_id = row["id"].strip()
        priority = row["priority"].strip().lower()
        if not check_id or check_id in seen:
            raise AssessmentError(f"Duplicate or empty catalog id: {check_id!r}")
        if priority not in PRIORITY_WEIGHTS:
            raise AssessmentError(f"Unsupported priority for {check_id}: {priority}")
        seen.add(check_id)
        checks.append(
            Check(
                check_id=check_id,
                domain=row["domain"].strip(),
                priority=priority,
                description=row["check"].strip(),
                evidence_required=row["evidence_required"].strip(),
                recommended_action=row["recommended_action"].strip(),
            )
        )
    return checks


def load_answers(path: Path) -> list[Answer]:
    rows = _read_csv(path)
    required = {"id", "status", "evidence", "owner", "target_date", "notes"}
    _require_columns(rows, required, path)
    answers: list[Answer] = []
    seen: set[str] = set()
    for row in rows:
        check_id = row["id"].strip()
        status = row["status"].strip().lower()
        if not check_id or check_id in seen:
            raise AssessmentError(f"Duplicate or empty assessment id: {check_id!r}")
        if status not in STATUS_SCORES:
            raise AssessmentError(f"Unsupported status for {check_id}: {status!r}")
        evidence = row["evidence"].strip()
        if status != "na" and not evidence:
            raise AssessmentError(f"Evidence is required for {check_id} ({status})")
        seen.add(check_id)
        answers.append(
            Answer(
                check_id=check_id,
                status=status,
                evidence=evidence,
                owner=row["owner"].strip(),
                target_date=row["target_date"].strip(),
                notes=row["notes"].strip(),
            )
        )
    return answers


def evaluate(checks: Iterable[Check], answers: Iterable[Answer]) -> dict:
    check_list = list(checks)
    answer_map = {answer.check_id: answer for answer in answers}
    check_ids = {check.check_id for check in check_list}
    missing = sorted(check_ids - answer_map.keys())
    unknown = sorted(answer_map.keys() - check_ids)
    if missing:
        raise AssessmentError(f"Missing assessment ids: {', '.join(missing)}")
    if unknown:
        raise AssessmentError(f"Unknown assessment ids: {', '.join(unknown)}")

    earned = 0.0
    possible = 0
    domains: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"earned": 0.0, "possible": 0, "assessed": 0}
    )
    blockers: list[dict[str, str]] = []
    actions: list[dict[str, str]] = []

    for check in check_list:
        answer = answer_map[check.check_id]
        status_score = STATUS_SCORES[answer.status]
        if status_score is None:
            continue
        weight = PRIORITY_WEIGHTS[check.priority]
        item_earned = weight * status_score
        earned += item_earned
        possible += weight
        domains[check.domain]["earned"] += item_earned
        domains[check.domain]["possible"] += weight
        domains[check.domain]["assessed"] += 1

        item = {
            "id": check.check_id,
            "domain": check.domain,
            "priority": check.priority,
            "check": check.description,
            "status": answer.status,
            "owner": answer.owner or "Unassigned",
            "target_date": answer.target_date or "Unscheduled",
            "action": check.recommended_action,
        }
        if check.priority == "critical" and answer.status in {"fail", "unknown"}:
            blockers.append(item)
        if answer.status in {"fail", "partial", "unknown"}:
            actions.append(item)

    score = round((earned / possible * 100) if possible else 0.0, 1)
    if blockers or score < 65:
        decision = "BLOCKED"
    elif score < 85:
        decision = "CONDITIONAL"
    else:
        decision = "READY"

    domain_results = []
    for name in sorted(domains):
        values = domains[name]
        domain_score = round(values["earned"] / values["possible"] * 100, 1)
        domain_results.append(
            {"domain": name, "score": domain_score, "assessed": values["assessed"]}
        )

    actions.sort(
        key=lambda item: (
            -PRIORITY_WEIGHTS[item["priority"]],
            {"fail": 0, "unknown": 1, "partial": 2}[item["status"]],
            item["domain"],
            item["id"],
        )
    )
    return {
        "decision": decision,
        "score": score,
        "assessed_checks": sum(item["assessed"] for item in domains.values()),
        "domain_scores": domain_results,
        "critical_blockers": blockers,
        "priority_actions": actions,
    }


def render_markdown(result: dict, assessment_name: str) -> str:
    lines = [
        f"# Modernization Assessment: {assessment_name}",
        "",
        f"**Decision:** {result['decision']}",
        f"**Weighted score:** {result['score']:.1f}%",
        f"**Assessed checks:** {result['assessed_checks']}",
        "",
        "## Domain Scores",
        "",
        "| Domain | Score | Checks |",
        "| --- | ---: | ---: |",
    ]
    for domain in result["domain_scores"]:
        lines.append(
            f"| {domain['domain']} | {domain['score']:.1f}% | {domain['assessed']} |"
        )

    lines.extend(["", "## Critical Blockers", ""])
    if result["critical_blockers"]:
        for item in result["critical_blockers"]:
            lines.append(
                f"- **{item['id']} ({item['domain']})**: {item['check']} "
                f"Owner: {item['owner']}. Target: {item['target_date']}."
            )
    else:
        lines.append("No failed or unknown critical checks.")

    lines.extend(["", "## Priority Actions", ""])
    if result["priority_actions"]:
        lines.extend(
            [
                "| ID | Priority | Status | Owner | Target | Recommended action |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in result["priority_actions"]:
            lines.append(
                f"| {item['id']} | {item['priority']} | {item['status']} | "
                f"{item['owner']} | {item['target_date']} | {item['action']} |"
            )
    else:
        lines.append("No failed or partial checks.")
    return "\n".join(lines) + "\n"


def render_json(result: dict) -> str:
    return json.dumps(result, indent=2) + "\n"


def _read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        raise AssessmentError(f"File not found: {path}") from exc


def _require_columns(rows: list[dict[str, str]], required: set[str], path: Path) -> None:
    if not rows:
        raise AssessmentError(f"CSV has no data rows: {path}")
    columns = set(rows[0].keys())
    missing = required - columns
    if missing:
        raise AssessmentError(f"Missing columns in {path}: {', '.join(sorted(missing))}")
