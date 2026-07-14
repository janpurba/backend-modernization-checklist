# Modernization Assessment: prefilled-assessment

**Decision:** BLOCKED
**Weighted score:** 31.9%
**Assessed checks:** 40

## Domain Scores

| Domain | Score | Checks |
| --- | ---: | ---: |
| Architecture | 12.5% | 4 |
| Data | 33.3% | 4 |
| Delivery | 50.0% | 4 |
| Observability | 33.3% | 4 |
| Operations | 0.0% | 4 |
| Ownership | 50.0% | 4 |
| Reliability | 0.0% | 4 |
| Runtime | 50.0% | 4 |
| Security | 50.0% | 4 |
| Testing | 33.3% | 4 |

## Critical Blockers

- **ARC-01 (Architecture)**: Transactional boundaries and data ownership are explicit Owner: Unassigned. Target: Unscheduled.
- **REL-01 (Reliability)**: Retries are bounded, classified, and safe for the operation Owner: Unassigned. Target: Unscheduled.
- **OPS-01 (Operations)**: On-call ownership and incident escalation are defined Owner: Unassigned. Target: Unscheduled.

## Priority Actions

| ID | Priority | Status | Owner | Target | Recommended action |
| --- | --- | --- | --- | --- | --- |
| ARC-01 | critical | unknown | Unassigned | Unscheduled | Resolve cross-service writes before extracting components |
| OPS-01 | critical | unknown | Unassigned | Unscheduled | Assign responders before production migration |
| REL-01 | critical | unknown | Unassigned | Unscheduled | Retry only transient failures with backoff and jitter |
| DAT-01 | critical | partial | Unassigned | Unscheduled | Separate additive and destructive schema changes |
| DEL-01 | critical | partial | Unassigned | Unscheduled | Build once, promote the same artifact, and record provenance |
| OBS-01 | critical | partial | Unassigned | Unscheduled | Measure user-visible success, latency, and availability |
| OWN-01 | critical | partial | Unassigned | Unscheduled | Assign owners before changing production behavior |
| RUN-01 | critical | partial | Unassigned | Unscheduled | Choose a supported target and document the upgrade sequence |
| SEC-01 | critical | partial | Unassigned | Unscheduled | Use a managed secret store and short-lived credentials where possible |
| SEC-02 | critical | partial | Unassigned | Unscheduled | Centralize policy while retaining endpoint-level enforcement |
| TST-01 | critical | partial | Unassigned | Unscheduled | Protect behavior before refactoring implementation |
| ARC-03 | high | unknown | Unassigned | Unscheduled | Wrap remote clients, messaging, filesystem, and vendor SDKs |
| DAT-02 | high | unknown | Unassigned | Unscheduled | Optimize using representative parameters and validate result equality |
| OBS-02 | high | unknown | Unassigned | Unscheduled | Propagate correlation context across HTTP, messaging, and jobs |
| OPS-02 | high | unknown | Unassigned | Unscheduled | Write decision-oriented recovery steps and rehearse them |
| OPS-03 | high | unknown | Unassigned | Unscheduled | Measure actual RPO and RTO instead of relying on configuration |
| REL-02 | high | unknown | Unassigned | Unscheduled | Define connect, read, and total deadlines plus circuit or bulkhead policy |
| REL-03 | high | unknown | Unassigned | Unscheduled | Make handlers idempotent and define replay ownership |
| TST-03 | high | unknown | Unassigned | Unscheduled | Validate compatibility before independent deployment |
| ARC-02 | high | partial | Unassigned | Unscheduled | Introduce enforceable package or module boundaries |
| DAT-03 | high | partial | Unassigned | Unscheduled | Set limits from measured concurrency and database capacity |
| DEL-02 | high | partial | Unassigned | Unscheduled | Use incremental rollout with explicit abort thresholds |
| DEL-03 | high | partial | Unassigned | Unscheduled | Version configuration and reject missing or invalid values |
| OBS-03 | high | partial | Unassigned | Unscheduled | Alert on symptoms and capacity risk, not raw log volume |
| OWN-02 | high | partial | Unassigned | Unscheduled | Document callers, dependencies, and business responsibilities |
| OWN-03 | high | partial | Unassigned | Unscheduled | Capture synchronous, asynchronous, batch, and manual consumers |
| RUN-02 | high | partial | Unassigned | Unscheduled | Remove unused libraries and plan high-risk upgrades separately |
| RUN-03 | high | partial | Unassigned | Unscheduled | Fail fast on invalid configuration and drain traffic before shutdown |
| SEC-03 | high | partial | Unassigned | Unscheduled | Reject invalid input and prevent sensitive fields from logs and responses |
| SEC-04 | high | partial | Unassigned | Unscheduled | Gate releases on actionable severity thresholds |
| TST-02 | high | partial | Unassigned | Unscheduled | Use disposable infrastructure and production-compatible schemas |
| ARC-04 | medium | unknown | Unassigned | Unscheduled | Prefer small stable contracts over shared business logic |
| DAT-04 | medium | unknown | Unassigned | Unscheduled | Bound table growth and rehearse cleanup failure recovery |
| OBS-04 | medium | unknown | Unassigned | Unscheduled | Instrument boundaries and retain enough context for diagnosis |
| OPS-04 | medium | unknown | Unassigned | Unscheduled | Track unit cost and define scaling or optimization triggers |
| REL-04 | medium | unknown | Unassigned | Unscheduled | Test saturation and preserve critical journeys first |
| TST-04 | medium | unknown | Unassigned | Unscheduled | Track latency, throughput, saturation, and error rate |
| DEL-04 | medium | partial | Unassigned | Unscheduled | Keep old and new versions interoperable during rollout |
| OWN-04 | medium | partial | Unassigned | Unscheduled | Define targets for reliability, delivery speed, cost, and maintainability |
| RUN-04 | medium | partial | Unassigned | Unscheduled | Version configuration and test it under representative load |
