# Backend Modernization Checklist

An opinionated, evidence-based assessment toolkit for modernizing Java and Spring Boot systems without turning a framework upgrade into an uncontrolled rewrite.

It converts 40 practitioner-defined checks across ownership, runtime, architecture, data, reliability, security, testing, observability, delivery, and operations into a weighted decision and prioritized action list.

The checklist is inspired by [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final), [OWASP SAMM](https://owasp.org/www-project-samm/) and [ASVS](https://owasp.org/www-project-application-security-verification-standard/), [Google SRE](https://sre.google/), and [DORA](https://dora.dev/). It is not an official profile, certification, or compliance standard for any of them.

## What You Get

- A version-neutral Java/Spring Boot modernization checklist
- Evidence requirements for every check
- Weighted scoring with explicit critical blockers
- A repeatable `READY`, `CONDITIONAL`, or `BLOCKED` decision
- A sample legacy-service assessment and generated report
- Discovery, ADR, rollout, and migration-strategy templates
- A standard-library Python CLI with automated tests and CI

## Scope and Provenance

The 40 checks, ten-domain taxonomy, priority weights, and `65%`/`85%` decision thresholds are the author's opinionated synthesis. They are intended to support engineering conversations and modernization sequencing, not to certify compliance.

The source frameworks influence different parts of the toolkit:

- [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) informs secure development lifecycle, dependency, artifact, and software supply-chain practices.
- [OWASP SAMM](https://owasp.org/www-project-samm/) informs security-program maturity and improvement planning; [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) informs technical application-security verification.
- [Google SRE](https://sre.google/) informs SLOs, observability, bounded failure handling, on-call readiness, incident response, and recovery exercises.
- [DORA](https://dora.dev/guides/) informs measurable delivery outcomes, continuous delivery, feedback, and incremental improvement.

See [Sources and Traceability](docs/references.md) for the citation scope and [the per-check source map](checklist/source-map.csv) for conceptual influences. A mapped source does not mean that a check is a verbatim or normative requirement from that source.

## Start in 60 Seconds

Create a conservative worksheet where every item starts as `fail` and `Not assessed`:

```bash
python3 scripts/new_assessment.py --output assessment-my-service.csv
```

Replace each status with `pass`, `partial`, `fail`, or `na`, and attach concrete evidence. Then score it:

```bash
python3 scripts/score_assessment.py \
  --assessment assessment-my-service.csv \
  --output report-my-service.md
```

Run the included example and tests:

```bash
make check
```

The generated [sample report](examples/SAMPLE_REPORT.md) shows the expected output for an incomplete legacy-service modernization.

## Decision Rules

| Decision | Rule |
| --- | --- |
| `READY` | Weighted score is at least 85% and no critical check failed |
| `CONDITIONAL` | Weighted score is 65-84.9% and no critical check failed |
| `BLOCKED` | Score is below 65% or any critical check failed |

Priority weights are `critical = 5`, `high = 3`, and `medium = 1`. Status values score as `pass = 100%`, `partial = 50%`, `fail = 0%`, while `na` is excluded from the denominator.

A high score cannot hide a failed critical control. A check only passes when its evidence is reviewable; expectations and verbal confirmation are not evidence.

## Assessment Workflow

```mermaid
flowchart LR
    D[Discover system] --> B[Capture baseline]
    B --> A[Complete assessment]
    A --> E[Attach evidence]
    E --> S[Score risks]
    S --> P[Sequence changes]
    P --> R[Incremental rollout]
    R --> V[Verify outcomes]
    V --> C[Remove legacy path]
```

Use the [modernization playbook](docs/modernization-playbook.md) for phase gates, the [Java/Spring Boot guide](docs/java-spring-boot-guide.md) for upgrade risk areas, and [migration strategies](docs/migration-strategies.md) before deciding to rewrite or extract a service.

## Evidence Examples

| Claim | Acceptable evidence |
| --- | --- |
| Query is faster | Representative parameters, execution plans, equal business results, before/after measurements |
| Rollback is safe | Timestamped rehearsal with recovery time and data reconciliation |
| API is compatible | Old/new producer-consumer contract results |
| Retry is safe | Failure-injection result, bounded policy, and idempotency proof |
| Service is observable | SLI definition, dashboard, alert route, and incident owner |

## CLI Options

Emit JSON for automation:

```bash
python3 scripts/score_assessment.py \
  --assessment assessment-my-service.csv \
  --format json
```

Fail a pipeline when modernization is blocked:

```bash
python3 scripts/score_assessment.py \
  --assessment assessment-my-service.csv \
  --fail-on-blocked
```

## Repository Structure

```text
checklist/catalog.csv             Versioned checks and evidence requirements
checklist/source-map.csv          Per-check conceptual source mapping
scripts/                          Worksheet generator and scoring CLI
examples/                         Sanitized assessment and generated reports
docs/                             Playbook, guidance, and source citations
templates/                        Discovery, ADR, and rollout templates
tests/                            Scoring and validation tests
```

## Use in Real Projects

Treat the score as a decision aid, not a substitute for engineering judgment or a compliance audit. Tailor checks only through a reviewed change, record why an item is `na`, and keep evidence close to the assessment. Re-score at agreed gates so risk reduction is visible rather than inferred from completed tickets.

## License

[MIT](LICENSE)
