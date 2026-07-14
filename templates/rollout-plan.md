# Modernization Rollout Plan

## Scope

- Change:
- Owners:
- Artifact/version:
- Affected consumers:
- Migration window:

## Preconditions

- [ ] Critical regression and contract tests pass
- [ ] Schema and message changes are backward-compatible
- [ ] Dashboards and alerts are active
- [ ] Rollback and data recovery were rehearsed
- [ ] On-call and stakeholder communication are confirmed

## Rollout Stages

| Stage | Population | Duration | Entry criteria | Success signals | Abort thresholds |
| --- | ---: | ---: | --- | --- | --- |
| Dark/shadow | 0% authoritative | | | | |
| Canary | | | | | |
| Partial | | | | | |
| Full | 100% | | | | |

## Business Reconciliation

Define compared records, acceptable differences, delayed outcomes, owners, and correction procedure.

## Rollback

1. Stop further rollout.
2. Restore routing or previous artifact.
3. Preserve and reconcile writes created during the affected window.
4. Confirm user-visible and dependency recovery signals.
5. Record the decision timeline and follow-up owner.

## Completion

- [ ] Observation window passed
- [ ] Old callers and data forms removed
- [ ] Temporary compatibility code removed
- [ ] Runbooks and ownership updated
- [ ] Final assessment and ADR archived
