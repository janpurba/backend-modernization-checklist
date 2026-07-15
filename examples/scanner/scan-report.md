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

- Statuses: partial=13, unknown=27
- Assessment types: HYBRID=13, MANUAL=27

The scanner intentionally does not emit `pass`. Human review must confirm completeness and effectiveness before changing `partial` or `unknown` to `pass`.

## Findings

| ID | Status | Type | Confidence | Evidence | Source basis |
| --- | --- | --- | --- | --- | --- |
| RUN-01 | partial | HYBRID | high | Detected Java=21, Spring Boot=3.4.0 from pom.xml | NIST-SSDF;SPRING-BOOT |
| RUN-02 | partial | HYBRID | medium | Dependency inventory contains 4 coordinates from pom.xml | NIST-SSDF;SPRING-BOOT |
| RUN-03 | partial | HYBRID | medium | Typed configuration or startup validation: src/main/java/example/AppConfig.java | OWASP-ASVS;SPRING-BOOT |
| RUN-04 | partial | HYBRID | medium | Explicit runtime and resource settings: Dockerfile, src/main/resources/application.yml | GOOGLE-SRE;SPRING-BOOT |
| CMP-01 | unknown | MANUAL | none | No known JDK migration-risk pattern found; target-aware compiler and jdeprscan output are still required | JAVA-MIGRATION;NIST-SSDF |
| CMP-02 | unknown | MANUAL | none | No known Spring migration-risk pattern found; target release migration output is still required | SPRING-BOOT-UPGRADE |
| CMP-03 | unknown | MANUAL | none | No conclusive repository evidence for: namespace, bytecode-tool, or library-integration compatibility hotspots | JAVA-MIGRATION;SPRING-BOOT-UPGRADE |
| CMP-04 | unknown | MANUAL | none | No repository signal found for: Framework extension-point migration hotspots | JAVA-MIGRATION;SPRING-BOOT-UPGRADE |
| ARC-01 | partial | HYBRID | medium | Enforced package or module boundaries: pom.xml, src/test/java/example/ArchitectureTest.java | DORA;SPRING-FRAMEWORK |
| ARC-02 | unknown | MANUAL | none | No repository signal found for: Framework-neutral application or domain boundaries | DORA;SPRING-FRAMEWORK |
| ARC-03 | unknown | MANUAL | none | No repository signal found for: External integration adapters or clients | DORA;SPRING-FRAMEWORK |
| ARC-04 | unknown | MANUAL | none | No known hidden-coupling pattern found; cycle analysis is still required | DORA;SPRING-FRAMEWORK |
| DAT-01 | partial | HYBRID | medium | Versioned database migrations: src/main/resources/db/migration/V1__create_sample.sql | DORA |
| DAT-02 | unknown | MANUAL | none | No repository signal found for: Explicit persistence mapping or locking signals | SPRING-FRAMEWORK |
| DAT-03 | unknown | MANUAL | none | No repository signal found for: Explicit transaction semantics | SPRING-FRAMEWORK |
| DAT-04 | unknown | MANUAL | none | No repository signal found for: Bounded query, pagination, or batch access | GOOGLE-SRE;SPRING-FRAMEWORK |
| REL-01 | unknown | MANUAL | none | No repository signal found for: Explicit exception and failure semantics | GOOGLE-SRE;SPRING-FRAMEWORK |
| REL-02 | unknown | MANUAL | none | No repository signal found for: Remote-call deadlines, bounded retry, isolation, or idempotency | GOOGLE-SRE |
| REL-03 | unknown | MANUAL | none | No repository signal found for: Duplicate or poison-message handling | GOOGLE-SRE |
| REL-04 | unknown | MANUAL | none | No repository signal found for: Async, scheduler, executor, or shared-state controls | GOOGLE-SRE;SPRING-FRAMEWORK |
| SEC-01 | partial | HYBRID | medium | Secret-scanning configuration: .github/workflows/ci.yml | NIST-SSDF;OWASP-SAMM |
| SEC-02 | partial | HYBRID | low | Spring Security boundary configuration: pom.xml, src/main/java/example/SecurityConfig.java | OWASP-ASVS;OWASP-SAMM |
| SEC-03 | partial | HYBRID | low | Trust-boundary validation or redaction: src/main/java/example/AppConfig.java | OWASP-ASVS;OWASP-SAMM |
| SEC-04 | partial | HYBRID | medium | Component vulnerability or SBOM analysis: .github/workflows/ci.yml | NIST-SSDF;OWASP-SAMM |
| TST-01 | partial | HYBRID | low | Automated tests (2 test source files): src/test/java/example/ArchitectureTest.java, src/test/java/example/RepositoryIntegrationTest.java | DORA;NIST-SSDF |
| TST-02 | partial | HYBRID | medium | Realistic integration-test infrastructure: pom.xml, src/test/java/example/RepositoryIntegrationTest.java | NIST-SSDF;SPRING-FRAMEWORK |
| TST-03 | unknown | MANUAL | none | No repository signal found for: Consumer or provider contract testing | DORA;NIST-SSDF |
| TST-04 | unknown | MANUAL | none | No repository signal found for: Test isolation or deterministic-time controls | NIST-SSDF;SPRING-FRAMEWORK |
| OBS-01 | unknown | MANUAL | none | No repository signal found for: Structured, correlated, or redacted logging | GOOGLE-SRE;SPRING-BOOT |
| OBS-02 | partial | HYBRID | low | Actuator or Micrometer metrics instrumentation: pom.xml | GOOGLE-SRE;SPRING-BOOT |
| OBS-03 | unknown | MANUAL | none | No repository signal found for: Distributed tracing instrumentation | GOOGLE-SRE;SPRING-BOOT |
| OBS-04 | unknown | MANUAL | none | No repository signal found for: Health, readiness, or startup-state instrumentation | GOOGLE-SRE;SPRING-BOOT |
| MNT-01 | unknown | MANUAL | none | No complexity analysis configuration found; source complexity remains unverified | DORA |
| MNT-02 | unknown | MANUAL | none | No repository signal found for: Duplicate, dead-code, or unused-dependency analysis | DORA;NIST-SSDF |
| MNT-03 | unknown | MANUAL | none | No debt marker found; scope and actionability of technical debt remain unverified | DORA |
| MNT-04 | unknown | MANUAL | none | No repository signal found for: Versioned static-analysis configuration | NIST-SSDF;DORA |
| API-01 | unknown | MANUAL | none | No repository signal found for: Machine-readable API or message contracts | OWASP-ASVS;SPRING-FRAMEWORK |
| API-02 | unknown | MANUAL | none | No repository signal found for: Automated backward-compatibility checks | DORA;SPRING-FRAMEWORK |
| API-03 | unknown | MANUAL | none | No repository signal found for: Versioning or consistent public error semantics | OWASP-ASVS;SPRING-FRAMEWORK |
| API-04 | unknown | MANUAL | none | No repository signal found for: Explicit serialization compatibility rules | OWASP-ASVS;SPRING-FRAMEWORK |

## Source Citations

- [DORA](https://dora.dev/guides/)
- [GOOGLE-SRE](https://sre.google/)
- [JAVA-MIGRATION](https://docs.oracle.com/en/java/javase/21/migrate/)
- [NIST-SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP-ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP-SAMM](https://owasp.org/www-project-samm/)
- [SPRING-BOOT](https://docs.spring.io/spring-boot/index.html)
- [SPRING-BOOT-UPGRADE](https://docs.spring.io/spring-boot/upgrading.html)
- [SPRING-FRAMEWORK](https://docs.spring.io/spring-framework/reference/)

## Required Human Review

- Verify detected Java and Spring Boot versions against the selected target support policy.
- Run target-aware compiler, dependency convergence, and JDK deprecation analysis.
- Review authorization, transaction, concurrency, and compatibility behavior.
- Validate repository signals by compiling and testing the target application separately.
- Investigate secret findings without committing credential values to assessment artifacts.
- Replace scanner-generated evidence only after a reviewer confirms the final status.
