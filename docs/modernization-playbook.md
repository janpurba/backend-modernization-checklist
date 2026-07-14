# Modernization Playbook

Modernization is a sequence of risk-reduction decisions, not a framework upgrade followed by cleanup. Preserve business behavior, establish evidence, and make each release independently reversible.

This is an opinionated practitioner playbook. Its phase gates synthesize secure-development guidance from [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) and [OWASP SAMM](https://owasp.org/www-project-samm/), reliability guidance from [Google SRE](https://sre.google/), and incremental-delivery guidance from [DORA](https://dora.dev/capabilities/continuous-delivery/). The sequence and exit gates are author-defined, not normative requirements from those sources.

## Phase 0: Frame the Decision

Answer four questions before estimating implementation:

1. What measurable outcome must improve?
2. Which critical journeys must not regress?
3. What is the tolerated migration window and operational risk?
4. Which constraint cannot change, such as database ownership, deployment topology, or regulatory controls?

**Exit gate:** named owners, measurable goals, explicit constraints, and agreed stop criteria.

## Phase 1: Discover and Baseline

- Map inbound consumers, outbound dependencies, batch flows, and manual operations.
- Capture runtime, framework, dependency, schema, and infrastructure inventories.
- Establish latency, traffic, error, saturation, cost, build-time, and recovery baselines.
- Protect critical behavior with regression and contract tests.
- Complete the assessment worksheet and attach evidence for every status.

**Exit gate:** no unknown critical consumer, transaction boundary, data owner, or recovery owner.

## Phase 2: Stabilize

- Remove secrets and unsafe defaults.
- Add bounded timeouts, classified retries, and idempotency where needed.
- Fix deployment reproducibility and configuration validation.
- Add health, dependency, saturation, and critical-journey signals.
- Rehearse rollback and restore before increasing change volume.

**Exit gate:** failed critical checks have owners and either pass or have an approved containment plan.

## Phase 3: Upgrade the Platform

Use small compatibility steps:

1. Remove unused dependencies and deprecated APIs.
2. Upgrade build plugins and test infrastructure.
3. Move to a supported Java runtime.
4. Upgrade one framework line at a time when migration guidance requires it.
5. Address namespace, configuration, serialization, security-default, and observability changes.
6. Re-run behavioral, contract, migration, and performance tests after each step.

Do not combine a runtime upgrade, database redesign, and service extraction in one release unless rollback remains independently possible.

**Exit gate:** the supported target runs under representative load with no unresolved critical compatibility issue.

## Phase 4: Improve Structure

- Enforce module boundaries with architecture tests.
- Move business rules away from controllers, listeners, repositories, and vendor clients.
- Put external systems behind adapters with contract tests.
- Replace shared mutable schemas with owned interfaces or events where the benefit justifies the migration cost.
- Extract a service only when independent ownership, scaling, reliability, or delivery provides measurable value.

**Exit gate:** target boundaries are enforceable and the migration does not create distributed transactions without a recovery design.

## Phase 5: Roll Out Incrementally

- Use expand-contract for schemas and messages.
- Deploy dark reads, shadow traffic, or parallel calculations before switching authority.
- Release to a limited population and compare technical and business signals.
- Define abort thresholds before rollout starts.
- Remove compatibility code only after old producers, consumers, and stored data are gone.

**Exit gate:** target SLOs and business reconciliation hold through the agreed observation window.

## Phase 6: Close the Work

- Remove dead code, old configuration, temporary bridges, and stale dashboards.
- Archive migration evidence and decisions.
- Update ownership, runbooks, recovery procedures, and cost baselines.
- Record remaining debt as owned work with an explicit impact, not a generic cleanup backlog.

**Exit gate:** the old path is no longer callable and every temporary control has been removed or accepted permanently.

## Evidence Standard

`pass` requires observable evidence. A meeting statement or expected behavior is not sufficient.

- Configuration claim: committed configuration plus startup or runtime proof.
- Reliability claim: failure-injection result and recovery signal.
- Performance claim: representative workload, parameters, plan, and before/after result.
- Compatibility claim: producer/consumer or old/new version test.
- Recovery claim: timestamped restore or rollback rehearsal.
- Security claim: automated scan or negative test plus remediation ownership.

See [Sources and Traceability](references.md) for citation scope and limitations.
