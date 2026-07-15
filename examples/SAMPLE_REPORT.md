# Source-Code Modernization Assessment: sample-assessment

**Decision:** BLOCKED
**Weighted score:** 41.2%
**Assessed checks:** 40

## Domain Scores

| Domain | Score | Checks |
| --- | ---: | ---: |
| API and Integration Contracts | 25.0% | 4 |
| Architecture | 33.3% | 4 |
| Data and Persistence | 45.8% | 4 |
| Maintainability and Code Health | 31.2% | 4 |
| Observability Instrumentation | 45.0% | 4 |
| Reliability and Concurrency | 21.4% | 4 |
| Runtime | 62.5% | 4 |
| Security | 75.0% | 4 |
| Testing and Verification | 50.0% | 4 |
| Upgrade Compatibility | 12.5% | 4 |

## Critical Blockers

- **CMP-01 (Upgrade Compatibility)**: Source code is free of removed, deprecated-for-removal, and internal JDK APIs for the selected target Owner: Backend Lead. Target: 2026-08-15.
- **REL-02 (Reliability and Concurrency)**: Remote calls use deadlines, bounded retries, failure isolation, and operation-safe idempotency Owner: Backend Lead. Target: 2026-08-29.
- **API-02 (API and Integration Contracts)**: Request, response, and event changes preserve backward compatibility Owner: Integration Lead. Target: 2026-08-29.

## Priority Actions

| ID | Priority | Status | Owner | Target | Recommended action |
| --- | --- | --- | --- | --- | --- |
| API-02 | critical | fail | Integration Lead | 2026-08-29 | Prefer additive evolution and retain compatibility during the migration window |
| REL-02 | critical | fail | Backend Lead | 2026-08-29 | Set connect and response deadlines and retry only safe transient failures |
| CMP-01 | critical | fail | Backend Lead | 2026-08-15 | Replace unsupported JDK APIs before changing the runtime |
| ARC-01 | critical | partial | Architecture Lead | 2026-08-29 | Define boundaries and enforce them with architecture tests |
| DAT-01 | critical | partial | Database Lead | 2026-08-29 | Separate additive and destructive changes across a compatibility window |
| RUN-01 | critical | partial | Backend Lead | 2026-08-15 | Select a supported target pair and make compiler and runtime versions explicit |
| SEC-02 | critical | partial | Security Lead | 2026-08-29 | Enforce endpoint and method authorization with deny-by-default behavior |
| TST-01 | critical | partial | QA Lead | 2026-08-29 | Protect current behavior before refactoring or upgrading |
| ARC-02 | high | fail | Architecture Lead | 2026-09-19 | Move business decisions behind framework-neutral application or domain interfaces |
| MNT-01 | high | fail | Backend Lead | 2026-09-19 | Split high-complexity code along cohesive responsibilities |
| REL-04 | high | fail | Backend Lead | 2026-09-05 | Use bounded executors and remove unsafe shared mutable state |
| TST-03 | high | fail | Integration Lead | 2026-09-12 | Run compatibility tests before changing public contracts |
| CMP-03 | high | fail | Backend Lead | 2026-09-05 | Upgrade or replace incompatible integrations before the framework change |
| API-01 | high | partial | Integration Lead | 2026-09-05 | Version contract artifacts with the code that implements them |
| API-03 | high | partial | Backend Lead | 2026-09-12 | Standardize public error semantics and make deprecation explicit |
| ARC-03 | high | partial | Integration Lead | 2026-09-05 | Isolate external clients so integrations can be upgraded and tested independently |
| DAT-02 | high | partial | Database Lead | 2026-09-05 | Remove risky implicit ORM behavior and document intentional mappings |
| DAT-03 | high | partial | Backend Lead | 2026-09-05 | Place transaction boundaries in the service layer and configure non-default semantics deliberately |
| MNT-02 | high | partial | Backend Lead | 2026-09-26 | Remove unused paths and consolidate duplicated behavior before migration |
| OBS-01 | high | partial | Backend Lead | 2026-09-05 | Use structured events and propagate correlation context across boundaries |
| OBS-02 | high | partial | Backend Lead | 2026-09-12 | Expose traffic, error, latency, and saturation signals at code boundaries |
| OBS-04 | high | partial | Backend Lead | 2026-09-12 | Report readiness only after required application state is usable |
| REL-01 | high | partial | Backend Lead | 2026-08-22 | Preserve failure semantics and remove catch-all success responses |
| REL-03 | high | partial | Integration Lead | 2026-09-12 | Make handlers idempotent and define bounded recovery paths |
| RUN-02 | high | partial | Backend Lead | 2026-08-22 | Centralize versions, remove duplicate overrides, and resolve dependency convergence failures |
| SEC-04 | high | partial | Security Lead | 2026-09-05 | Automate component analysis and review actionable findings |
| CMP-02 | high | partial | Security Lead | 2026-08-22 | Apply each skipped migration guide and remove temporary migration helpers |
| API-04 | medium | fail | Backend Lead | 2026-09-05 | Make wire-format behavior explicit and tolerant where compatibility requires it |
| ARC-04 | medium | fail | Architecture Lead | 2026-09-12 | Replace hidden coupling with constructor-injected explicit dependencies |
| DAT-04 | medium | fail | Database Lead | 2026-08-22 | Add pagination or batching and prevent unbounded data loading |
| OBS-03 | medium | fail | Backend Lead | 2026-09-19 | Preserve trace context across every asynchronous or remote boundary |
| CMP-04 | medium | unknown | Backend Lead | 2026-09-12 | Review each extension point against target release notes and make critical defaults explicit |
| MNT-03 | medium | partial | Backend Lead | 2026-09-19 | Replace broad suppressions and convert migration debt into explicit actions |
| MNT-04 | medium | partial | Backend Lead | 2026-09-26 | Adopt enforceable rules and keep exclusions narrow and documented |
| RUN-04 | medium | partial | Platform Engineer | 2026-08-29 | Declare resource settings and avoid environment-dependent implicit defaults |
| TST-04 | medium | partial | QA Lead | 2026-09-05 | Remove shared state, timing assumptions, and environment-dependent test behavior |
