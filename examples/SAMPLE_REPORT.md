# Modernization Assessment: sample-assessment

**Decision:** BLOCKED
**Weighted score:** 56.5%
**Assessed checks:** 40

## Domain Scores

| Domain | Score | Checks |
| --- | ---: | ---: |
| Architecture | 66.7% | 4 |
| Data | 37.5% | 4 |
| Delivery | 83.3% | 4 |
| Observability | 33.3% | 4 |
| Operations | 79.2% | 4 |
| Ownership | 83.3% | 4 |
| Reliability | 25.0% | 4 |
| Runtime | 41.7% | 4 |
| Security | 65.6% | 4 |
| Testing | 45.8% | 4 |

## Critical Blockers

- **RUN-01 (Runtime)**: The Java runtime and Spring Boot line are vendor-supported Owner: Backend Lead. Target: 2026-09-30.
- **REL-01 (Reliability)**: Retries are bounded, classified, and safe for the operation Owner: Backend Lead. Target: 2026-08-29.

## Priority Actions

| ID | Priority | Status | Owner | Target | Recommended action |
| --- | --- | --- | --- | --- | --- |
| REL-01 | critical | fail | Backend Lead | 2026-08-29 | Retry only transient failures with backoff and jitter |
| RUN-01 | critical | fail | Backend Lead | 2026-09-30 | Choose a supported target and document the upgrade sequence |
| DAT-01 | critical | partial | Database Lead | 2026-08-29 | Separate additive and destructive schema changes |
| OBS-01 | critical | partial | SRE | 2026-08-29 | Measure user-visible success, latency, and availability |
| SEC-02 | critical | partial | Security Lead | 2026-08-29 | Centralize policy while retaining endpoint-level enforcement |
| TST-01 | critical | partial | QA Lead | 2026-08-22 | Protect behavior before refactoring implementation |
| DAT-02 | high | fail | Database Lead | 2026-08-22 | Optimize using representative parameters and validate result equality |
| OBS-03 | high | fail | SRE | 2026-09-12 | Alert on symptoms and capacity risk, not raw log volume |
| SEC-04 | high | fail | Platform Lead | 2026-09-26 | Gate releases on actionable severity thresholds |
| TST-03 | high | fail | Integration Lead | 2026-09-19 | Validate compatibility before independent deployment |
| ARC-02 | high | partial | Backend Lead | 2026-09-19 | Introduce enforceable package or module boundaries |
| ARC-03 | high | partial | Backend Lead | 2026-09-26 | Wrap remote clients, messaging, filesystem, and vendor SDKs |
| DAT-03 | high | partial | SRE | 2026-09-05 | Set limits from measured concurrency and database capacity |
| DEL-02 | high | partial | Platform Lead | 2026-08-29 | Use incremental rollout with explicit abort thresholds |
| OBS-02 | high | partial | SRE | 2026-09-05 | Propagate correlation context across HTTP, messaging, and jobs |
| OPS-03 | high | partial | Database Lead | 2026-09-19 | Measure actual RPO and RTO instead of relying on configuration |
| OWN-03 | high | partial | Integration Lead | 2026-08-15 | Capture synchronous, asynchronous, batch, and manual consumers |
| REL-02 | high | partial | Backend Lead | 2026-09-05 | Define connect, read, and total deadlines plus circuit or bulkhead policy |
| REL-03 | high | partial | Integration Lead | 2026-09-12 | Make handlers idempotent and define replay ownership |
| RUN-02 | high | partial | Backend Lead | 2026-08-29 | Remove unused libraries and plan high-risk upgrades separately |
| ARC-04 | medium | fail | Architecture Lead | 2026-10-03 | Prefer small stable contracts over shared business logic |
| OBS-04 | medium | fail | SRE | 2026-10-03 | Instrument boundaries and retain enough context for diagnosis |
| OPS-04 | medium | fail | Product Owner | 2026-10-10 | Track unit cost and define scaling or optimization triggers |
| REL-04 | medium | fail | SRE | 2026-10-10 | Test saturation and preserve critical journeys first |
| TST-04 | medium | fail | QA Lead | 2026-09-26 | Track latency, throughput, saturation, and error rate |
| DAT-04 | medium | partial | Database Lead | 2026-09-19 | Bound table growth and rehearse cleanup failure recovery |
| DEL-04 | medium | partial | Release Lead | 2026-09-05 | Keep old and new versions interoperable during rollout |
| OWN-04 | medium | partial | Product Owner | 2026-08-22 | Define targets for reliability, delivery speed, cost, and maintainability |
| RUN-04 | medium | partial | SRE | 2026-09-12 | Version configuration and test it under representative load |
