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

## Domain Mapping

| Checklist domain | Main influences | Repository interpretation |
| --- | --- | --- |
| Ownership | OWASP SAMM, Google SRE, DORA | Named decision, service, and operational ownership |
| Runtime | NIST SSDF, Spring Boot, Google SRE | Supported platform, dependency hygiene, deterministic runtime behavior |
| Architecture | OWASP SAMM, DORA | Enforceable boundaries and independently changeable integrations |
| Data | Google SRE, DORA | Backward-compatible change, measured query behavior, bounded database use |
| Reliability | Google SRE, DORA | Explicit failure behavior, bounded retries, idempotency, and degradation |
| Security | NIST SSDF, OWASP SAMM, OWASP ASVS | Secure lifecycle plus verifiable technical controls |
| Testing | NIST SSDF, OWASP ASVS, DORA | Regression, integration, contract, security, and performance evidence |
| Observability | Google SRE | User-facing SLIs, actionable alerts, structured telemetry, and dependency signals |
| Delivery | NIST SSDF, DORA | Reproducible artifacts, progressive rollout, compatibility, and rollback |
| Operations | Google SRE, DORA | On-call readiness, tested runbooks, recovery evidence, capacity and cost awareness |

The row-level mapping is maintained in [`checklist/source-map.csv`](../checklist/source-map.csv). `inspired` means a check directly reflects a concept in one or more cited sources. `practitioner-synthesis` means the check combines cited principles with Java/Spring Boot modernization experience; it should not be attributed to a single framework.

## Important Limits

- Passing this checklist does not establish NIST SSDF conformance.
- The security checks are not a substitute for a complete OWASP SAMM assessment or versioned ASVS verification.
- Google SRE publications are engineering guidance, not a certification standard.
- DORA research and capabilities support improvement measurement; this repository's weighted score is not a DORA score.
- The `critical`, `high`, and `medium` weights and the `READY`, `CONDITIONAL`, and `BLOCKED` thresholds are author-defined.
- Organizations should map applicable legal, regulatory, privacy, and internal controls separately.
