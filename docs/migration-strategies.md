# Migration Strategy Selection

Select the smallest strategy that satisfies the modernization outcome. Splitting a service is not automatically more modern than improving a well-owned modular monolith.

This strategy matrix is an opinionated practitioner synthesis influenced by [DORA continuous-delivery guidance](https://dora.dev/capabilities/continuous-delivery/), [Google SRE](https://sre.google/), and the risk-driven design approach in [OWASP SAMM](https://owasp.org/www-project-samm/). The strategy names and decision rules are guidance, not normative requirements from those sources.

| Strategy | Best fit | Main risk | Required evidence |
| --- | --- | --- | --- |
| In-place upgrade | Boundaries are acceptable and primary risk is unsupported runtime or framework | Large compatibility step | Regression suite, dependency analysis, rollback rehearsal |
| Modular refactor | Delivery friction comes from tangled code within one deployment | Cosmetic packages without enforceable boundaries | Dependency rules, module ownership, architecture tests |
| Strangler migration | A capability can be routed independently and coexistence is affordable | Long-lived dual paths and inconsistent behavior | Routing controls, reconciliation, old-path removal criteria |
| Parallel run | Output can be compared before authority switches | Side effects or comparison blind spots | Shadow mode, reconciliation thresholds, divergence alerts |
| Service extraction | Independent ownership, scaling, or reliability has measurable value | Distributed transactions and higher operational load | Data ownership, failure model, contract tests, capacity plan |
| Replace with managed capability | The capability is commodity and ownership cost exceeds differentiation | Vendor lock-in and migration gaps | Exit plan, data portability, security and resilience review |

## Decision Questions

1. Can the outcome be achieved without changing deployment boundaries?
2. Who owns the target capability and its on-call responsibility?
3. Can source and target run concurrently?
4. How will writes remain consistent during coexistence?
5. How will business output be reconciled?
6. What signal causes rollback, and how long does rollback take?
7. What explicitly proves the legacy path can be deleted?

## Patterns

### Expand-Contract

1. Add backward-compatible schema or message fields.
2. Deploy readers that tolerate old and new forms.
3. Deploy writers for the new form.
4. Backfill and reconcile stored data.
5. Verify no old reader or writer remains.
6. Remove the old form in a separate release.

### Dark Read

Send a copy of reads to the target and compare results without using its response. Define field-level comparison rules, acceptable drift, and sampling before enabling it.

### Shadow Write

Replicate writes only when duplicate side effects are prevented. Prefer a transactional event or change stream over uncoordinated dual writes. Reconcile state before switching authority.

### Incremental Routing

Route by stable tenant, account, geography, or percentage. Keep cohorts observable so failures can be isolated and rolled back without ambiguity.

## Reject the Migration When

- No owner accepts the target service's operational responsibility.
- Data ownership or transaction semantics are unresolved.
- Rollback depends on manually reconstructing lost writes.
- Success is defined only as deploying the new technology.
- The legacy path has no deletion criteria or funded completion window.

See [Sources and Traceability](references.md) for citation scope and limitations.
