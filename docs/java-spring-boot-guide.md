# Java and Spring Boot Upgrade Guide

This guide deliberately avoids hard-coding a "latest" version. Select a vendor-supported Java runtime and Spring Boot line using the target release's official compatibility matrix and migration notes.

## Inventory Before Editing

Capture:

- Java vendor, runtime, compiler target, and container base image
- Spring Boot, Spring Framework, Spring Cloud, build plugins, and test libraries
- Direct dependencies, transitive overrides, internal starters, and shared libraries
- `javax.*` usage, removed JDK modules, reflection, agents, custom class loading, and native libraries
- Configuration keys, active profiles, environment variables, secrets, and defaults
- Serialization contracts, database drivers, dialects, migrations, and timestamp handling
- Security filter chains, method security, CORS, CSRF, session, and token behavior
- Actuator exposure, metrics names, tracing propagation, and health semantics

Commit the inventory as an assessment artifact so compatibility decisions remain reviewable.

## Recommended Upgrade Sequence

1. Make the current application build reproducibly.
2. Add regression coverage around critical behavior and serialization.
3. Remove unused dependencies and deprecated APIs on the current version.
4. Upgrade build plugins and testing tools.
5. Move to the supported Java target while keeping the framework stable when compatible.
6. Upgrade framework lines incrementally and apply each official migration guide.
7. Update dependent Spring projects and third-party integrations.
8. Rebuild the container image and validate JVM/resource behavior.
9. Run contract, database migration, security, startup, shutdown, and load tests.

## High-Risk Compatibility Areas

### API and Namespace Changes

- Search imports, reflection strings, XML descriptors, generated sources, and vendor APIs.
- Treat namespace migration as a compile-and-runtime concern; serialization and container integrations can fail after compilation succeeds.

### Configuration Binding

- Fail startup on missing required values.
- Review renamed or removed framework properties.
- Compare effective configuration across environments without exposing secrets.

### Security Defaults

- Preserve an explicit access-control matrix.
- Test anonymous access, wrong roles, expired credentials, CORS, CSRF, and management endpoints.
- Do not accept "application starts" as evidence that security behavior is unchanged.

### Persistence and Transactions

- Verify driver and dialect compatibility.
- Re-run schema migrations on a production-like copy.
- Test lazy loading, locking, isolation, generated identifiers, timestamp precision, and rollback behavior.
- Compare query plans and pool saturation under representative concurrency.

### HTTP and Messaging Contracts

- Snapshot JSON fields, nullability, date/time formats, status codes, headers, and error bodies.
- Validate event schema, routing, acknowledgement, retry, dead-letter, and replay behavior.
- Run old producer/new consumer and new producer/old consumer compatibility tests during rolling migration.

### Observability

- Check renamed metrics and changed tag cardinality.
- Verify trace context across HTTP, messaging, and scheduled work.
- Ensure readiness does not report success before critical dependencies and migrations are ready.

## Definition of Done

- Supported target runtime and framework line
- Reproducible build and immutable artifact
- No failed critical assessment checks
- Regression and contract suites green
- Backward-compatible migration and tested rollback
- Representative performance within agreed thresholds
- Dashboards, alerts, runbooks, ownership, and recovery evidence updated
