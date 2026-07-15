# Backend Modernization Checklist

An opinionated, evidence-based source-code assessment toolkit for modernizing Java and Spring Boot systems without turning a framework upgrade into an uncontrolled rewrite.

It converts 40 practitioner-defined checks across runtime, upgrade compatibility, architecture, data and persistence, reliability and concurrency, security, testing, observability instrumentation, maintainability, and API contracts into a weighted decision and prioritized action list.

The checklist is inspired by [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final), [OWASP SAMM](https://owasp.org/www-project-samm/) and [ASVS](https://owasp.org/www-project-application-security-verification-standard/), [Google SRE](https://sre.google/), and [DORA](https://dora.dev/). It is not an official profile, certification, or compliance standard for any of them.

## What You Get

- A version-neutral Java/Spring Boot source-code modernization checklist
- Evidence requirements for every check
- Weighted scoring with explicit critical blockers
- A repeatable `READY`, `CONDITIONAL`, or `BLOCKED` decision
- A sample legacy-service assessment and generated report
- Discovery, ADR, rollout, and migration-strategy templates
- A standard-library Python CLI with automated tests and CI
- A static Java/Spring Boot repository scanner that prefills evidence without executing target code

## Scope and Provenance

The 40 checks, ten-domain taxonomy, priority weights, and `65%`/`85%` decision thresholds are the author's opinionated synthesis. They are intended to identify repository-visible migration risk and sequence source-code work, not to certify compliance or represent full production readiness.

The score deliberately excludes business ownership, delivery-process maturity, on-call readiness, disaster recovery, production SLO effectiveness, and measured runtime performance. Assess those separately before making a production modernization decision.

The source frameworks influence different parts of the toolkit:

- [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) informs secure development lifecycle, dependency, artifact, and software supply-chain practices.
- [OWASP SAMM](https://owasp.org/www-project-samm/) informs security-program maturity and improvement planning; [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) informs technical application-security verification.
- [Google SRE](https://sre.google/) informs bounded failure handling and repository-visible observability instrumentation.
- [DORA](https://dora.dev/guides/) informs loosely coupled architecture, feedback, and incremental improvement.
- The [Oracle JDK Migration Guide](https://docs.oracle.com/en/java/javase/21/migrate/) and [Spring Boot upgrade guidance](https://docs.spring.io/spring-boot/upgrading.html) inform source-level compatibility checks.
- The [Spring Framework reference](https://docs.spring.io/spring-framework/reference/) informs dependency injection, data access, transactions, testing, and integration boundaries.

See [Sources and Traceability](docs/references.md) for the citation scope and [the per-check source map](checklist/source-map.csv) for conceptual influences. A mapped source does not mean that a check is a verbatim or normative requirement from that source.

## Scan a Java/Spring Boot Repository

Run a bounded, read-only static scan:

```bash
python3 scripts/scan_repository.py \
  --repo /path/to/spring-service \
  --output assessment-spring-service.csv \
  --report scan-spring-service.md
```

The scanner inventories Maven/Gradle metadata, Java and Spring Boot versions, dependency coordinates, source and tests, database migrations, runtime configuration, security signals, resilience and concurrency configuration, observability instrumentation, maintainability signals, and API contracts. It then prefills all 40 checks with:

- `assessment_type`: `AUTOMATED`, `HYBRID`, or `MANUAL`
- `confidence`: `high`, `medium`, `low`, or `none`
- `source_basis`: keys linked to the cited primary sources
- repository-relative evidence paths without secret values

The scanner deliberately never emits `pass`. Static presence cannot prove that a practice is complete or effective. It emits `partial` when a relevant signal exists, `unknown` when human or runtime evidence is required, and `fail` only for deterministic negative evidence such as high-confidence hardcoded credential material.

Review the prefilled CSV, assign reviewers, attach compiler, build, static-analysis, and test evidence, and promote statuses to `pass` only after verification. See the [scanner design and detection matrix](docs/repository-scanner.md).

## Manual Assessment

Create a conservative worksheet where every item starts as `fail` and `Not assessed`:

```bash
python3 scripts/new_assessment.py --output assessment-my-service.csv
```

Replace each status with `pass`, `partial`, `fail`, `unknown`, or `na`, and attach concrete evidence. Then score it:

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
| `READY` | Weighted score is at least 85% and no critical check is `fail` or `unknown` |
| `CONDITIONAL` | Weighted score is 65-84.9% and no critical check is `fail` or `unknown` |
| `BLOCKED` | Score is below 65% or any critical check is `fail` or `unknown` |

Priority weights are `critical = 5`, `high = 3`, and `medium = 1`. Status values score as `pass = 100%`, `partial = 50%`, `fail = 0%`, and `unknown = 0%`, while `na` is excluded from the denominator.

A high score cannot hide a failed or unverified critical control. A check only passes when its evidence is reviewable; expectations and verbal confirmation are not evidence.

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
| Target JDK is compatible | Target compiler output, `jdeprscan`, and tests on the selected JDK |
| Data access is bounded | Repository query, pagination or batch configuration, and boundary tests |
| API is compatible | Old/new producer-consumer contract results |
| Retry is safe | Failure-injection result, bounded policy, and idempotency proof |
| Code is instrumented | Logging, metrics, tracing, and health configuration plus focused tests |

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

Treat the score as a source-code decision aid, not a substitute for engineering judgment, runtime validation, or a compliance audit. Tailor checks only through a reviewed change, record why an item is `na`, and keep evidence close to the assessment. Use a separate production-readiness review for ownership, delivery, operations, recovery, SLOs, and measured performance.

## License

[MIT](LICENSE)
