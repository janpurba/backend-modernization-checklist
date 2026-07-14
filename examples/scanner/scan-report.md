# Repository Scan: spring-service

> Static prefill only. A detected signal is not proof that a control is effective, complete, or production-ready.

## Inventory

- Build system: Maven
- Java version: 21
- Spring Boot version: 3.4.0
- Files scanned: 11
- Java source files: 4
- Test source files: 2
- Dependency coordinates: 4

## Prefill Summary

- Statuses: partial=23, unknown=17
- Assessment types: HYBRID=23, MANUAL=17

The scanner intentionally does not emit `pass`. Human review must confirm completeness and effectiveness before changing `partial` or `unknown` to `pass`.

## Findings

| ID | Status | Type | Confidence | Evidence | Source basis |
| --- | --- | --- | --- | --- | --- |
| OWN-01 | partial | HYBRID | low | Ownership metadata: .github/CODEOWNERS | GOOGLE-SRE;OWASP-SAMM |
| OWN-02 | partial | HYBRID | medium | Architecture or capability documentation: README.md | DORA;OWASP-SAMM |
| OWN-03 | partial | HYBRID | low | Consumer or integration inventory: README.md | DORA;GOOGLE-SRE |
| OWN-04 | partial | HYBRID | medium | Measurable modernization or reliability goals: README.md | DORA |
| RUN-01 | partial | HYBRID | high | Detected Java=21, Spring Boot=3.4.0 from pom.xml | NIST-SSDF;SPRING-BOOT |
| RUN-02 | partial | HYBRID | high | Dependency inventory contains 4 coordinates from pom.xml; vulnerability scan configuration: .github/workflows/ci.yml | NIST-SSDF;OWASP-SAMM |
| RUN-03 | partial | HYBRID | medium | Startup validation or graceful shutdown: src/main/resources/application.yml, src/main/java/example/AppConfig.java | DORA;GOOGLE-SRE;SPRING-BOOT |
| RUN-04 | partial | HYBRID | medium | Explicit JVM or container resource settings: Dockerfile | GOOGLE-SRE;SPRING-BOOT |
| ARC-01 | unknown | MANUAL | none | No repository signal found for: Transaction or data ownership signals | DORA;OWASP-SAMM |
| ARC-02 | partial | HYBRID | medium | Enforced module or architecture boundaries: pom.xml, src/test/java/example/ArchitectureTest.java | DORA |
| ARC-03 | unknown | MANUAL | none | No repository signal found for: External integration adapters or clients | DORA;OWASP-SAMM |
| ARC-04 | unknown | MANUAL | none | No repository signal found for: Shared-library ownership or compatibility policy | DORA |
| DAT-01 | partial | HYBRID | medium | Versioned database migrations: src/main/resources/db/migration/V1__create_sample.sql | DORA |
| DAT-02 | unknown | MANUAL | none | No repository signal found for: Query plans or digest evidence | DORA;GOOGLE-SRE |
| DAT-03 | partial | HYBRID | medium | Bounded connection-pool configuration: src/main/resources/application.yml | GOOGLE-SRE |
| DAT-04 | unknown | MANUAL | none | No repository signal found for: Retention or cleanup implementation | GOOGLE-SRE |
| REL-01 | unknown | MANUAL | none | No repository signal found for: Retry and idempotency signals | GOOGLE-SRE |
| REL-02 | unknown | MANUAL | none | No repository signal found for: Remote-call deadlines or failure isolation | GOOGLE-SRE |
| REL-03 | unknown | MANUAL | none | No repository signal found for: Duplicate or poison-message handling | GOOGLE-SRE |
| REL-04 | unknown | MANUAL | none | No repository signal found for: Load or degradation test assets | DORA;GOOGLE-SRE |
| SEC-01 | partial | HYBRID | medium | Secret-scanning configuration: .github/workflows/ci.yml | NIST-SSDF;OWASP-SAMM |
| SEC-02 | partial | HYBRID | low | Spring Security boundary configuration: pom.xml, src/main/java/example/SecurityConfig.java | OWASP-ASVS;OWASP-SAMM |
| SEC-03 | partial | HYBRID | low | Input validation or sensitive-data handling: src/main/java/example/AppConfig.java | OWASP-ASVS;OWASP-SAMM |
| SEC-04 | partial | HYBRID | medium | Artifact provenance, SBOM, or vulnerability scanning: .github/workflows/ci.yml | NIST-SSDF;OWASP-SAMM |
| TST-01 | partial | HYBRID | low | Automated tests (2 test source files): src/test/java/example/ArchitectureTest.java, src/test/java/example/RepositoryIntegrationTest.java | DORA;NIST-SSDF |
| TST-02 | partial | HYBRID | medium | Realistic integration-test infrastructure: pom.xml, src/test/java/example/RepositoryIntegrationTest.java | DORA;NIST-SSDF |
| TST-03 | unknown | MANUAL | none | No repository signal found for: Consumer or provider contract testing | DORA;NIST-SSDF |
| TST-04 | unknown | MANUAL | none | No repository signal found for: Performance-test assets | DORA;GOOGLE-SRE |
| OBS-01 | partial | HYBRID | medium | SLI, SLO, or error-budget configuration: README.md | GOOGLE-SRE |
| OBS-02 | unknown | MANUAL | none | No repository signal found for: Structured or correlated logging | GOOGLE-SRE |
| OBS-03 | partial | HYBRID | low | Actuator, metrics, or dependency-health instrumentation: pom.xml | GOOGLE-SRE |
| OBS-04 | unknown | MANUAL | none | No repository signal found for: Distributed tracing instrumentation | GOOGLE-SRE |
| DEL-01 | partial | HYBRID | low | CI pipeline and repeatable build assets: .github/workflows/ci.yml, Dockerfile | DORA;NIST-SSDF |
| DEL-02 | partial | HYBRID | low | Incremental rollout or rollback procedure: README.md | DORA |
| DEL-03 | partial | HYBRID | low | Configuration binding or startup validation: src/main/java/example/AppConfig.java | DORA;SPRING-BOOT |
| DEL-04 | partial | HYBRID | low | Ordered compatibility or release sequencing: src/main/resources/db/migration/V1__create_sample.sql | DORA |
| OPS-01 | unknown | MANUAL | none | No repository signal found for: On-call or escalation metadata | GOOGLE-SRE |
| OPS-02 | unknown | MANUAL | none | No repository signal found for: Operational runbooks | GOOGLE-SRE |
| OPS-03 | unknown | MANUAL | none | No repository signal found for: Backup or recovery documentation | GOOGLE-SRE |
| OPS-04 | unknown | MANUAL | none | No repository signal found for: Capacity or cost-management evidence | DORA;GOOGLE-SRE |

## Source Citations

- [DORA](https://dora.dev/guides/)
- [GOOGLE-SRE](https://sre.google/)
- [NIST-SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP-ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP-SAMM](https://owasp.org/www-project-samm/)
- [SPRING-BOOT](https://docs.spring.io/spring-boot/index.html)

## Required Human Review

- Verify vendor support dates and commercial support agreements.
- Review authorization behavior, data ownership, and transaction boundaries.
- Attach runtime evidence for SLOs, query plans, capacity, rollback, restore, and incident readiness.
- Investigate secret findings without committing credential values to assessment artifacts.
- Replace scanner-generated evidence only after a reviewer confirms the final status.
