# Sources and Traceability

This repository is an opinionated practitioner synthesis. It does not reproduce, implement, or certify conformance with any framework listed below. The source mapping records conceptual influence so reviewers can distinguish external guidance from author-defined scoring and implementation detail.

## Primary Sources

| Key | Primary source | Used for |
| --- | --- | --- |
| `NIST-SSDF` | [NIST SP 800-218, Secure Software Development Framework (SSDF) Version 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | Secure development lifecycle, software integrity, dependency management, vulnerability response, and release provenance |
| `OWASP-SAMM` | [OWASP Software Assurance Maturity Model](https://owasp.org/www-project-samm/) | Risk-driven security maturity, governance, design, implementation, verification, and operations |
| `OWASP-ASVS` | [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/) | Technical verification of authentication, authorization, input handling, and other application-security controls |
| `GOOGLE-SRE` | [Google Site Reliability Engineering](https://sre.google/) and its [Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/) | SLOs, symptom-based alerting, incident roles, on-call preparation, runbooks, capacity, and recovery exercises |
| `DORA` | [DORA Guides](https://dora.dev/guides/) and [Continuous Delivery capability](https://dora.dev/capabilities/continuous-delivery/) | Delivery performance, continuous delivery, feedback, loosely coupled architecture, and measurable improvement |
| `SPRING-BOOT` | [Spring Boot reference documentation](https://docs.spring.io/spring-boot/index.html) | Java/Spring Boot compatibility, configuration, runtime, production-readiness, and upgrade verification |
| `SPRING-BOOT-UPGRADE` | [Upgrading Spring Boot](https://docs.spring.io/spring-boot/upgrading.html) | Release migration guides, changed configuration properties, and version-specific upgrade work |
| `SPRING-FRAMEWORK` | [Spring Framework reference documentation](https://docs.spring.io/spring-framework/reference/) | Dependency injection, data access, transaction semantics, testing, web integration, and framework extension points |
| `JAVA-MIGRATION` | [Oracle JDK Migration Guide](https://docs.oracle.com/en/java/javase/21/migrate/) | Removed APIs, internal JDK usage, tooling, and source or behavioral migration risk |

## Domain Mapping

| Checklist domain | Main influences | Repository interpretation |
| --- | --- | --- |
| Runtime | NIST SSDF, Spring Boot, Google SRE | Explicit platform, dependency inventory, configuration, and resource settings |
| Upgrade Compatibility | Oracle JDK Migration Guide, Spring Boot upgrade guidance | Removed APIs, changed properties, namespaces, integrations, and extension points |
| Architecture | Spring Framework, DORA | Enforceable boundaries, explicit dependencies, and isolated integrations |
| Data and Persistence | Spring Framework, Google SRE, DORA | Backward-compatible migrations, explicit ORM and transaction behavior, bounded data access |
| Reliability and Concurrency | Spring Framework, Google SRE | Explicit failure semantics, bounded remote calls, messaging safety, and concurrency controls |
| Security | NIST SSDF, OWASP SAMM, OWASP ASVS | Secure lifecycle plus verifiable technical controls |
| Testing and Verification | Spring Framework, NIST SSDF, DORA | Regression, integration, contract, and deterministic-test evidence |
| Observability Instrumentation | Spring Boot, Google SRE | Structured logs, metrics, tracing propagation, health, and readiness signals |
| Maintainability and Code Health | NIST SSDF, DORA | Controlled complexity, reduced migration surface, and repeatable static analysis |
| API and Integration Contracts | Spring Framework, OWASP ASVS, DORA | Machine-readable contracts, backward compatibility, error semantics, and serialization |

The row-level mapping is maintained in [`checklist/source-map.csv`](../checklist/source-map.csv). `inspired` means a check directly reflects a concept in one or more cited sources. `practitioner-synthesis` means the check combines cited principles with Java/Spring Boot modernization experience; it should not be attributed to a single framework.

The [repository scanner](repository-scanner.md) uses this mapping to cite the conceptual basis of each prefilled row. Static detection rules and confidence levels are implementation choices in this repository; they are not prescribed by the mapped source.

## Important Limits

- Passing this checklist does not establish NIST SSDF conformance.
- The security checks are not a substitute for a complete OWASP SAMM assessment or versioned ASVS verification.
- Google SRE publications are engineering guidance, not a certification standard.
- DORA research and capabilities support improvement measurement; this repository's weighted score is not a DORA score.
- The `critical`, `high`, and `medium` weights and the `READY`, `CONDITIONAL`, and `BLOCKED` thresholds are author-defined.
- The source-code score does not assess ownership, delivery maturity, on-call readiness, disaster recovery, SLO effectiveness, or measured production performance.
- Organizations should map applicable legal, regulatory, privacy, and internal controls separately.
