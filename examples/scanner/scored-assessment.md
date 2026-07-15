# Source-Code Modernization Assessment: prefilled-assessment

**Decision:** BLOCKED
**Weighted score:** 20.4%
**Assessed checks:** 40

## Domain Scores

| Domain | Score | Checks |
| --- | ---: | ---: |
| API and Integration Contracts | 0.0% | 4 |
| Architecture | 20.8% | 4 |
| Data and Persistence | 20.8% | 4 |
| Maintainability and Code Health | 0.0% | 4 |
| Observability Instrumentation | 15.0% | 4 |
| Reliability and Concurrency | 0.0% | 4 |
| Runtime | 50.0% | 4 |
| Security | 50.0% | 4 |
| Testing and Verification | 33.3% | 4 |
| Upgrade Compatibility | 0.0% | 4 |

## Critical Blockers

- **CMP-01 (Upgrade Compatibility)**: Source code is free of removed, deprecated-for-removal, and internal JDK APIs for the selected target Owner: Unassigned. Target: Unscheduled.
- **REL-02 (Reliability and Concurrency)**: Remote calls use deadlines, bounded retries, failure isolation, and operation-safe idempotency Owner: Unassigned. Target: Unscheduled.
- **API-02 (API and Integration Contracts)**: Request, response, and event changes preserve backward compatibility Owner: Unassigned. Target: Unscheduled.

## Priority Actions

| ID | Priority | Status | Owner | Target | Recommended action |
| --- | --- | --- | --- | --- | --- |
| API-02 | critical | unknown | Unassigned | Unscheduled | Prefer additive evolution and retain compatibility during the migration window |
| REL-02 | critical | unknown | Unassigned | Unscheduled | Set connect and response deadlines and retry only safe transient failures |
| CMP-01 | critical | unknown | Unassigned | Unscheduled | Replace unsupported JDK APIs before changing the runtime |
| ARC-01 | critical | partial | Unassigned | Unscheduled | Define boundaries and enforce them with architecture tests |
| DAT-01 | critical | partial | Unassigned | Unscheduled | Separate additive and destructive changes across a compatibility window |
| RUN-01 | critical | partial | Unassigned | Unscheduled | Select a supported target pair and make compiler and runtime versions explicit |
| SEC-01 | critical | partial | Unassigned | Unscheduled | Remove and rotate confirmed credentials and use an external secret source |
| SEC-02 | critical | partial | Unassigned | Unscheduled | Enforce endpoint and method authorization with deny-by-default behavior |
| TST-01 | critical | partial | Unassigned | Unscheduled | Protect current behavior before refactoring or upgrading |
| API-01 | high | unknown | Unassigned | Unscheduled | Version contract artifacts with the code that implements them |
| API-03 | high | unknown | Unassigned | Unscheduled | Standardize public error semantics and make deprecation explicit |
| ARC-02 | high | unknown | Unassigned | Unscheduled | Move business decisions behind framework-neutral application or domain interfaces |
| ARC-03 | high | unknown | Unassigned | Unscheduled | Isolate external clients so integrations can be upgraded and tested independently |
| DAT-02 | high | unknown | Unassigned | Unscheduled | Remove risky implicit ORM behavior and document intentional mappings |
| DAT-03 | high | unknown | Unassigned | Unscheduled | Place transaction boundaries in the service layer and configure non-default semantics deliberately |
| MNT-01 | high | unknown | Unassigned | Unscheduled | Split high-complexity code along cohesive responsibilities |
| MNT-02 | high | unknown | Unassigned | Unscheduled | Remove unused paths and consolidate duplicated behavior before migration |
| OBS-01 | high | unknown | Unassigned | Unscheduled | Use structured events and propagate correlation context across boundaries |
| OBS-04 | high | unknown | Unassigned | Unscheduled | Report readiness only after required application state is usable |
| REL-01 | high | unknown | Unassigned | Unscheduled | Preserve failure semantics and remove catch-all success responses |
| REL-03 | high | unknown | Unassigned | Unscheduled | Make handlers idempotent and define bounded recovery paths |
| REL-04 | high | unknown | Unassigned | Unscheduled | Use bounded executors and remove unsafe shared mutable state |
| TST-03 | high | unknown | Unassigned | Unscheduled | Run compatibility tests before changing public contracts |
| CMP-02 | high | unknown | Unassigned | Unscheduled | Apply each skipped migration guide and remove temporary migration helpers |
| CMP-03 | high | unknown | Unassigned | Unscheduled | Upgrade or replace incompatible integrations before the framework change |
| OBS-02 | high | partial | Unassigned | Unscheduled | Expose traffic, error, latency, and saturation signals at code boundaries |
| RUN-02 | high | partial | Unassigned | Unscheduled | Centralize versions, remove duplicate overrides, and resolve dependency convergence failures |
| RUN-03 | high | partial | Unassigned | Unscheduled | Replace scattered property lookups with validated typed configuration |
| SEC-03 | high | partial | Unassigned | Unscheduled | Validate at trust boundaries and prevent injection or sensitive-data disclosure |
| SEC-04 | high | partial | Unassigned | Unscheduled | Automate component analysis and review actionable findings |
| TST-02 | high | partial | Unassigned | Unscheduled | Test real framework integration instead of relying only on mocks |
| API-04 | medium | unknown | Unassigned | Unscheduled | Make wire-format behavior explicit and tolerant where compatibility requires it |
| ARC-04 | medium | unknown | Unassigned | Unscheduled | Replace hidden coupling with constructor-injected explicit dependencies |
| DAT-04 | medium | unknown | Unassigned | Unscheduled | Add pagination or batching and prevent unbounded data loading |
| MNT-03 | medium | unknown | Unassigned | Unscheduled | Replace broad suppressions and convert migration debt into explicit actions |
| MNT-04 | medium | unknown | Unassigned | Unscheduled | Adopt enforceable rules and keep exclusions narrow and documented |
| OBS-03 | medium | unknown | Unassigned | Unscheduled | Preserve trace context across every asynchronous or remote boundary |
| TST-04 | medium | unknown | Unassigned | Unscheduled | Remove shared state, timing assumptions, and environment-dependent test behavior |
| CMP-04 | medium | unknown | Unassigned | Unscheduled | Review each extension point against target release notes and make critical defaults explicit |
| RUN-04 | medium | partial | Unassigned | Unscheduled | Declare resource settings and avoid environment-dependent implicit defaults |
