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
| `HYBRID` | Repository evidence or a non-deterministic risk signal exists and needs review | `partial` or `unknown` |
| `MANUAL` | No sufficient static signal exists or the check requires target-aware build and test evidence | `unknown` |

The scanner does not emit `pass`. A file, annotation, dependency, or configuration key proves presence only. Human review must verify behavior, scope, and enforcement. Positive implementation signals prefill `partial`; potential risk patterns such as hidden coupling or broad suppressions remain `unknown` so their presence does not increase the score.

## Detection Matrix

| Domain | Static signals | Evidence that remains manual |
| --- | --- | --- |
| Runtime | Maven/Gradle versions, typed configuration, JVM/container/pool settings | Vendor support policy, resolved convergence, runtime behavior |
| Upgrade Compatibility | Internal JDK APIs, legacy namespaces, deprecated Spring patterns, extension points | Complete target-specific compiler, deprecation, and migration output |
| Architecture | ArchUnit/Modulith, module descriptors, domain packages, adapters, hidden-coupling patterns | Boundary quality and complete dependency-cycle analysis |
| Data and Persistence | Flyway/Liquibase, ORM mappings, transactions, pagination and batching | Semantic compatibility, rollback correctness, production data behavior |
| Reliability and Concurrency | Error models, timeout, retry, isolation, DLQ, executors, schedulers | Failure-injection, idempotency, replay, and concurrency correctness |
| Security | Secret patterns, Spring Security, validation, sensitive sinks, SBOM and scan tools | Complete authorization, credential rotation, and vulnerability disposition |
| Testing and Verification | Test sources, Testcontainers, contracts, isolation and deterministic-time signals | Critical-behavior coverage and test effectiveness |
| Observability Instrumentation | Structured logs, Actuator/Micrometer, tracing, health and readiness | Production telemetry quality, dashboards, alerts, and SLO effectiveness |
| Maintainability and Code Health | Complexity tools, oversized files, debt markers, static-analysis configuration | Semantic duplication, justified suppressions, and actual remediation quality |
| API and Integration Contracts | OpenAPI/AsyncAPI/schema files, compatibility tools, error models, serialization | Consumer inventory and proven old/new behavior compatibility |

## Build Metadata

Maven descriptors are parsed as XML using the Python standard library. The scanner resolves common Java and Spring Boot properties and inventories dependency/plugin coordinates. Gradle has no standard static model available without executing the build, so Gradle detection uses bounded text patterns and is reported as inventory evidence rather than a resolved dependency graph.

Version detection does not make support-lifecycle claims. Support depends on the selected distribution, commercial agreement, and date. Review detected versions against the [official Spring Boot documentation](https://docs.spring.io/spring-boot/index.html) and the chosen Java vendor's policy. The scanner also does not execute `jdeprscan`, a compiler, dependency resolution, or Spring's migration tooling.

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
- [Google SRE](https://sre.google/): observability instrumentation and bounded failure handling.
- [DORA](https://dora.dev/guides/): loosely coupled architecture, feedback, and incremental improvement.
- [Oracle JDK Migration Guide](https://docs.oracle.com/en/java/javase/21/migrate/): removed APIs, internal APIs, and JDK migration risks.
- [Spring Boot upgrade guidance](https://docs.spring.io/spring-boot/upgrading.html): version-specific API, property, and behavior changes.
- [Spring Framework reference](https://docs.spring.io/spring-framework/reference/): dependency injection, transactions, data access, testing, and integration behavior.

The scanner rules, confidence model, status prefill, and thresholds are author-defined. See [Sources and Traceability](references.md) and the [per-check source map](../checklist/source-map.csv).
