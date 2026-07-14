# Modernization Discovery Questionnaire

## Outcomes

- What user or business outcome must improve?
- Which baseline proves the current problem?
- What target and observation window define success?
- What constraints are fixed?

## Ownership and Scope

- Who owns product decisions, technical decisions, data, security, and operations?
- Which capabilities are in scope and explicitly out of scope?
- Which consumers and dependencies are critical?
- Which manual workflows or scheduled jobs are easy to miss?

## Runtime and Delivery

- Which runtime, framework, build, and container versions are deployed?
- Can any commit be rebuilt and deployed reproducibly?
- How are configuration and secrets supplied and validated?
- What is the tested rollback time?

## Data and Integration

- Which component owns each table and write path?
- Where are cross-system transactions assumed?
- Which API and message contracts require backward compatibility?
- What are the largest tables, highest-impact queries, and retention risks?

## Reliability and Recovery

- What are the top three production failure modes?
- Which calls retry and which operations are idempotent?
- How are duplicates, poison messages, and partial failure handled?
- When was backup restoration or disaster recovery last rehearsed?

## Verification

- Which critical journeys have automated regression coverage?
- What production-like test data and infrastructure are available?
- Which SLOs, dashboards, traces, and alerts prove the target behavior?
- What condition stops or reverses the migration?
