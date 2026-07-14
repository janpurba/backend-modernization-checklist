# Java and Spring Boot Repository Scanner

The scanner is a conservative static prefill tool. It gathers repository evidence without compiling, running, importing, or contacting services from the target project.

## Usage

```bash
python3 scripts/scan_repository.py \
  --repo /path/to/spring-service \
  --output assessment-spring-service.csv \
  --report scan-spring-service.md
```

The generated assessment is directly compatible with `score_assessment.py`:

```bash
python3 scripts/score_assessment.py \
  --assessment assessment-spring-service.csv \
  --output scored-spring-service.md
```

## Evidence Model

| Assessment type | Meaning | Typical status |
| --- | --- | --- |
| `AUTOMATED` | A bounded static rule found deterministic negative evidence | `fail` |
| `HYBRID` | Repository evidence exists but completeness or effectiveness needs review | `partial` |
| `MANUAL` | The check requires organizational, runtime, or production evidence | `unknown` |

The scanner does not emit `pass`. A file, annotation, dependency, or configuration key proves presence only. Human review must verify behavior, scope, enforcement, and production use.

## Detection Matrix

| Domain | Static signals | Evidence that remains manual |
| --- | --- | --- |
| Ownership | `CODEOWNERS`, architecture and consumer documentation | Actual business owner, escalation acceptance, complete consumer inventory |
| Runtime | Maven/Gradle, Java and Spring Boot versions, graceful shutdown, JVM limits | Vendor support agreement, runtime behavior under load |
| Architecture | Transactions, ArchUnit/Modulith, adapters and clients | True data ownership, boundary quality, cross-service consistency |
| Data | Flyway/Liquibase, query-plan artifacts, pool limits, cleanup code | Backward compatibility, representative plans, database capacity |
| Reliability | Retry, idempotency, timeout, circuit breaker, DLQ, load-test assets | Failure classification, replay safety, degradation behavior |
| Security | Secret patterns, Spring Security, validation, redaction, SBOM and scan tools | Complete authorization, credential rotation, vulnerability disposition |
| Testing | Test sources, Testcontainers, contracts, load-test assets | Critical-journey coverage, production compatibility, threshold approval |
| Observability | SLO terms, structured logs, Actuator/Micrometer, tracing | Correct SLIs, actionable alerts, usable production telemetry |
| Delivery | CI, Docker, rollout/rollback text, configuration validation, migrations | Artifact promotion, tested rollback, ordered cross-system release |
| Operations | On-call metadata, runbooks, recovery and capacity documents | Active ownership, restore rehearsal, measured RPO/RTO and cost trends |

## Build Metadata

Maven descriptors are parsed as XML using the Python standard library. The scanner resolves common Java and Spring Boot properties and inventories dependency/plugin coordinates. Gradle has no standard static model available without executing the build, so Gradle detection uses bounded text patterns and is reported as inventory evidence rather than a resolved dependency graph.

Version detection does not make support-lifecycle claims. Support depends on the selected distribution, commercial agreement, and date. Review detected versions against the [official Spring Boot documentation](https://docs.spring.io/spring-boot/index.html) and the chosen Java vendor's policy.

## Secret Detection

The scanner detects private-key markers, common token formats, and hardcoded credential assignments. Findings include only repository-relative path, line, category, and confidence; the value is never copied into the assessment or Markdown report.

- Environment placeholders such as `${DB_PASSWORD}` are ignored.
- Common local defaults and values under tests, examples, or documentation are medium-confidence review findings.
- High-entropy assignments and known credential formats outside those paths can produce an automated `fail` for `SEC-01`.
- The scanner is not a replacement for a dedicated secret-scanning product or credential rotation process.

This behavior supports the secure-development intent of [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) and [OWASP SAMM](https://owasp.org/www-project-samm/); it does not establish conformance with either framework.

## Safety Boundaries

- Does not execute Maven, Gradle, shell scripts, application code, or tests from the target repository.
- Does not follow symbolic links.
- Skips generated and dependency directories including `.git`, `target`, `build`, and `node_modules`.
- Scans supported text files only and skips files larger than `--max-file-bytes`.
- Stops when the repository exceeds `--max-files`.
- Performs no network calls and does not query a vulnerability database.

Defaults:

```text
--max-files      10000
--max-file-bytes 1000000
```

## Standards and Guidance

The detector selection is an opinionated synthesis:

- [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final): secure development, dependency and artifact integrity, and vulnerability practices.
- [OWASP SAMM](https://owasp.org/www-project-samm/): security maturity across governance, design, implementation, verification, and operations.
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/): technical application-security verification areas.
- [Google SRE](https://sre.google/): SLOs, observability, bounded failure, incident readiness, capacity, and recovery.
- [DORA](https://dora.dev/capabilities/continuous-delivery/): continuous delivery, feedback, architecture, and measurable improvement.
- [Spring Boot documentation](https://docs.spring.io/spring-boot/index.html): build, configuration, testing, production-ready features, and upgrade guidance.

The scanner rules, confidence model, status prefill, and thresholds are author-defined. See [Sources and Traceability](references.md) and the [per-check source map](../checklist/source-map.csv).
