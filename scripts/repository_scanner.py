from __future__ import annotations

import csv
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from assessment_core import Check


SKIP_DIRECTORIES = {
    ".git",
    ".gradle",
    ".idea",
    ".mvn-cache",
    ".pycache",
    ".settings",
    ".vscode",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "vendor",
}
TEXT_SUFFIXES = {
    ".conf",
    ".gradle",
    ".groovy",
    ".java",
    ".json",
    ".kts",
    ".kt",
    ".md",
    ".properties",
    ".sql",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {
    ".env",
    ".gitleaks.toml",
    "CODEOWNERS",
    "Dockerfile",
    "Jenkinsfile",
    "Makefile",
    "mvnw",
}
SOURCE_URLS = {
    "NIST-SSDF": "https://csrc.nist.gov/pubs/sp/800/218/final",
    "OWASP-SAMM": "https://owasp.org/www-project-samm/",
    "OWASP-ASVS": "https://owasp.org/www-project-application-security-verification-standard/",
    "GOOGLE-SRE": "https://sre.google/",
    "DORA": "https://dora.dev/guides/",
    "SPRING-BOOT": "https://docs.spring.io/spring-boot/index.html",
    "SPRING-BOOT-UPGRADE": "https://docs.spring.io/spring-boot/upgrading.html",
    "SPRING-FRAMEWORK": "https://docs.spring.io/spring-framework/reference/",
    "JAVA-MIGRATION": "https://docs.oracle.com/en/java/javase/21/migrate/",
}


class ScanError(ValueError):
    pass


@dataclass(frozen=True)
class SecretFinding:
    path: str
    line: int
    kind: str
    confidence: str

    def evidence(self) -> str:
        return f"{self.path}:{self.line} ({self.kind}, {self.confidence} confidence)"


@dataclass(frozen=True)
class Inventory:
    repository_name: str
    files_scanned: int
    java_files: int
    test_files: int
    build_systems: tuple[str, ...]
    java_version: str
    spring_boot_version: str
    dependencies: tuple[str, ...]
    plugins: tuple[str, ...]
    secret_findings: tuple[SecretFinding, ...]


@dataclass(frozen=True)
class Prefill:
    check_id: str
    status: str
    evidence: str
    notes: str
    assessment_type: str
    source_basis: str
    confidence: str


class RepositoryView:
    def __init__(self, root: Path, files: dict[str, str]):
        self.root = root
        self.files = files

    def paths(self, patterns: Iterable[str], limit: int = 6) -> list[str]:
        compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        return [
            path
            for path in sorted(self.files)
            if any(pattern.search(path) for pattern in compiled)
        ][:limit]

    def find(
        self,
        patterns: Iterable[str],
        *,
        path_patterns: Iterable[str] | None = None,
        limit: int = 6,
    ) -> list[str]:
        content_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in patterns]
        path_filters = (
            [re.compile(pattern, re.IGNORECASE) for pattern in path_patterns]
            if path_patterns
            else []
        )
        matches: list[str] = []
        for path in sorted(self.files):
            if path_filters and not any(pattern.search(path) for pattern in path_filters):
                continue
            text = self.files[path]
            if any(pattern.search(text) for pattern in content_patterns):
                matches.append(path)
                if len(matches) == limit:
                    break
        return matches


def collect_repository(
    root: Path, *, max_files: int = 10_000, max_file_bytes: int = 1_000_000
) -> RepositoryView:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ScanError(f"Repository directory does not exist: {root}")

    files: dict[str, str] = {}
    eligible_count = 0
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in SKIP_DIRECTORIES
            and not (current_path / directory).is_symlink()
        )
        for filename in sorted(filenames):
            path = current_path / filename
            if path.is_symlink() or not _is_text_candidate(path):
                continue
            eligible_count += 1
            if eligible_count > max_files:
                raise ScanError(f"Repository exceeds --max-files limit ({max_files})")
            try:
                if path.stat().st_size > max_file_bytes:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            files[path.relative_to(root).as_posix()] = text
    if not files:
        raise ScanError("No supported text files found in repository")
    return RepositoryView(root, files)


def build_inventory(view: RepositoryView) -> Inventory:
    maven = _maven_inventory(view)
    gradle = _gradle_inventory(view)
    dependencies = sorted(set(maven[2]) | set(gradle[2]))
    plugins = sorted(set(maven[3]) | set(gradle[3]))
    build_systems = []
    if view.paths([r"(^|/)pom\.xml$"]):
        build_systems.append("Maven")
    if view.paths([r"(^|/)build\.gradle(?:\.kts)?$"]):
        build_systems.append("Gradle")

    java_version = maven[0] if maven[0] != "not detected" else gradle[0]
    boot_version = maven[1] if maven[1] != "not detected" else gradle[1]
    java_files = len(view.paths([r"\.java$"], limit=len(view.files)))
    test_files = len(
        [
            path
            for path in view.files
            if re.search(r"(^|/)(src/test|src/integrationTest|test)/", path, re.IGNORECASE)
            and path.endswith((".java", ".kt", ".groovy"))
        ]
    )
    return Inventory(
        repository_name=view.root.name,
        files_scanned=len(view.files),
        java_files=java_files,
        test_files=test_files,
        build_systems=tuple(build_systems) or ("not detected",),
        java_version=java_version,
        spring_boot_version=boot_version,
        dependencies=tuple(dependencies),
        plugins=tuple(plugins),
        secret_findings=tuple(_scan_secrets(view)),
    )


def prefill_assessment(
    view: RepositoryView,
    inventory: Inventory,
    checks: Iterable[Check],
    source_map: dict[str, str],
) -> list[Prefill]:
    check_list = list(checks)
    results: dict[str, Prefill] = {}

    def manual(check_id: str, reason: str) -> None:
        results[check_id] = Prefill(
            check_id,
            "unknown",
            reason,
            "Manual review required; static repository evidence is insufficient.",
            "MANUAL",
            source_map.get(check_id, ""),
            "none",
        )

    def hybrid(
        check_id: str,
        description: str,
        paths: Iterable[str],
        *,
        confidence: str = "medium",
        missing_reason: str | None = None,
    ) -> None:
        found = list(dict.fromkeys(paths))
        if found:
            evidence = f"{description}: {', '.join(found)}"
            results[check_id] = Prefill(
                check_id,
                "partial",
                evidence,
                "Repository signal found, but effectiveness and completeness require review.",
                "HYBRID",
                source_map.get(check_id, ""),
                confidence,
            )
        else:
            manual(check_id, missing_reason or f"No repository signal found for: {description}")

    def review(
        check_id: str,
        description: str,
        paths: Iterable[str],
        *,
        confidence: str = "low",
        missing_reason: str | None = None,
    ) -> None:
        found = list(dict.fromkeys(paths))
        if found:
            results[check_id] = Prefill(
                check_id,
                "unknown",
                f"Review finding - {description}: {', '.join(found)}",
                "Potential risk signal found; confirm the context before deciding pass, partial, or fail.",
                "HYBRID",
                source_map.get(check_id, ""),
                confidence,
            )
        else:
            manual(check_id, missing_reason or f"No conclusive repository evidence for: {description}")

    build_paths = view.paths([r"(^|/)(pom\.xml|build\.gradle(?:\.kts)?)$"])
    version_evidence = (
        f"Detected Java={inventory.java_version}, Spring Boot={inventory.spring_boot_version}"
    )
    if build_paths:
        results["RUN-01"] = Prefill(
            "RUN-01",
            "partial",
            f"{version_evidence} from {', '.join(build_paths)}",
            "Detected versions must be checked against the selected vendor support policy; the scanner does not encode lifecycle dates.",
            "HYBRID",
            source_map.get("RUN-01", ""),
            "high",
        )
    else:
        manual("RUN-01", "No Maven or Gradle build descriptor found")

    if build_paths:
        results["RUN-02"] = Prefill(
            "RUN-02",
            "partial",
            f"Dependency inventory contains {len(inventory.dependencies)} coordinates from "
            f"{', '.join(build_paths)}",
            "Inventory is static and unresolved; version convergence and plugin compatibility require build-tool output and review.",
            "HYBRID",
            source_map.get("RUN-02", ""),
            "medium",
        )
    else:
        manual("RUN-02", "No Maven or Gradle dependency descriptor found")
    startup_validation = view.find(
        [r"@ConfigurationProperties", r"BindValidationException", r"spring\.config\.on-not-found", r"fail[- ]fast"],
        path_patterns=[r"src/main/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("RUN-03", "Typed configuration or startup validation", startup_validation)
    runtime_limits = view.find(
        [
            r"MaxRAMPercentage|-Xmx|-Xms|resources:\s*$|memory:\s*\d|JAVA_TOOL_OPTIONS",
            r"maximum[-_.]?pool[-_.]?size|core[-_.]?pool[-_.]?size|max[-_.]?pool[-_.]?size",
            r"ThreadPoolTaskExecutor|ExecutorService",
        ],
        path_patterns=[r"Dockerfile", r"\.ya?ml$", r"\.properties$", r"\.java$", r"\.kt$"],
    )
    hybrid("RUN-04", "Explicit runtime and resource settings", runtime_limits)

    jdk_migration_risks = view.find(
        [
            r"\b(?:sun|com\.sun|jdk\.internal)\.",
            r"\bThread\.(?:stop|suspend|resume)\s*\(",
            r"\bSystem\.setSecurityManager\s*\(",
        ],
        path_patterns=[r"src/main/.*\.(?:java|kt|groovy)$"],
    )
    review(
        "CMP-01",
        "potential removed, internal, or deprecated-for-removal JDK API usage",
        jdk_migration_risks,
        confidence="medium",
        missing_reason="No known JDK migration-risk pattern found; target-aware compiler and jdeprscan output are still required",
    )
    spring_migration_risks = view.find(
        [
            r"WebSecurityConfigurerAdapter|HandlerInterceptorAdapter",
            r"EnableGlobalMethodSecurity|\.antMatchers\s*\(",
            r"spring-boot-properties-migrator",
        ]
    )
    review(
        "CMP-02",
        "potential deprecated Spring API, configuration, or migration helper",
        spring_migration_risks,
        confidence="medium",
        missing_reason="No known Spring migration-risk pattern found; target release migration output is still required",
    )
    integration_compatibility = view.find(
        [
            r"import\s+javax\.(?:annotation|persistence|servlet|transaction|validation|ws\.rs)\.",
            r"\b(?:aspectj|byte-buddy|lombok|mapstruct|javaagent)\b",
        ],
        path_patterns=[r"src/", r"pom\.xml$", r"build\.gradle", r"Dockerfile"],
    )
    review(
        "CMP-03",
        "namespace, bytecode-tool, or library-integration compatibility hotspots",
        integration_compatibility,
        confidence="low",
    )
    extension_points = view.find(
        [
            r"(?:Filter|HandlerInterceptor|Converter|Serializer|Deserializer)\b",
            r"@Aspect\b|BeanPostProcessor|ApplicationContextInitializer",
            r"AutoConfiguration\.imports|spring\.factories|@AutoConfiguration",
        ],
        path_patterns=[r"src/main/", r"META-INF/", r"\.factories$"],
    )
    hybrid("CMP-04", "Framework extension-point migration hotspots", extension_points, confidence="low")

    architecture_tests = view.find([r"ArchUnit|layeredArchitecture|slices\(\)|SpringModulith"])
    module_descriptors = view.paths([r"module-info\.java$", r"package-info\.java$"])
    hybrid("ARC-01", "Enforced package or module boundaries", architecture_tests + module_descriptors)
    domain_boundaries = view.find(
        [r"package\s+[\w.]*\.(?:domain|application)(?:\.|;)", r"\b(?:UseCase|DomainService)\b"],
        path_patterns=[r"src/main/.*\.(?:java|kt)$"],
    )
    hybrid("ARC-02", "Framework-neutral application or domain boundaries", domain_boundaries, confidence="low")
    adapter_signals = view.find(
        [r"\b(adapter|gateway|port)\b|WebClient|RestClient|FeignClient|RestTemplate"],
        path_patterns=[r"src/main/.*\.(java|kt)$"],
    )
    hybrid("ARC-03", "External integration adapters or clients", adapter_signals, confidence="low")
    hidden_coupling = view.find(
        [
            r"ApplicationContext\s*\.\s*getBean|applicationContext\.getBean",
            r"static\s+(?:ApplicationContext|BeanFactory)",
            r"@Autowired\s+(?:private|protected|public)?\s*[\w<>?,. ]+\s+\w+\s*;",
        ],
        path_patterns=[r"src/main/.*\.(?:java|kt)$"],
    )
    review(
        "ARC-04",
        "hidden framework coupling",
        hidden_coupling,
        confidence="medium",
        missing_reason="No known hidden-coupling pattern found; cycle analysis is still required",
    )

    migration_paths = view.paths([r"db/migration/", r"liquibase", r"changelog.*\.(xml|ya?ml|json)$"])
    hybrid("DAT-01", "Versioned database migrations", migration_paths)
    persistence_mappings = view.find(
        [
            r"@Entity\b|@Document\b|@Table\b",
            r"fetch\s*=\s*FetchType\.|cascade\s*=|@Lock\b|ddl-auto",
        ],
        path_patterns=[r"src/main/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("DAT-02", "Explicit persistence mapping or locking signals", persistence_mappings, confidence="low")
    transaction_signals = view.find(
        [
            r"@Transactional\b|TransactionTemplate",
            r"PlatformTransactionManager|setPropagationBehavior|setIsolationLevel|setTransactionTimeout",
        ],
        path_patterns=[r"src/main/.*\.(?:java|kt)$"],
    )
    hybrid("DAT-03", "Explicit transaction semantics", transaction_signals, confidence="low")
    bounded_data_access = view.find(
        [
            r"\bPageable\b|\bPageRequest\b|setMaxResults\s*\(",
            r"batchUpdate\s*\(|saveAllAndFlush\s*\(|chunk\s*\(",
            r"\bLIMIT\s+(?:\?|:\w+|\d+)",
        ],
        path_patterns=[r"src/main/", r"\.sql$"],
    )
    hybrid("DAT-04", "Bounded query, pagination, or batch access", bounded_data_access, confidence="low")

    exception_semantics = view.find(
        [r"@(?:Rest)?ControllerAdvice|ProblemDetail|ResponseStatusException|ExceptionHandler\s*\("],
        path_patterns=[r"src/main/.*\.(?:java|kt)$"],
    )
    hybrid("REL-01", "Explicit exception and failure semantics", exception_semantics, confidence="low")
    retry = view.find([r"@Retryable|resilience4j\.retry|RetryTemplate|retryWhen"])
    idempotency = view.find([r"idempoten|dedup|Idempotency-Key|processed_event"])
    timeouts = view.find(
        [r"connect[-_.]?timeout|read[-_.]?timeout|response[-_.]?timeout|callTimeout|TimeLimiter"],
        path_patterns=[r"src/", r"\.properties$", r"\.ya?ml$"],
    )
    isolation = view.find([r"CircuitBreaker|Bulkhead|resilience4j\.(circuitbreaker|bulkhead)"])
    hybrid(
        "REL-02",
        "Remote-call deadlines, bounded retry, isolation, or idempotency",
        timeouts + retry + isolation + idempotency,
        confidence="low",
    )
    messaging_safety = view.find(
        [r"dead[-_. ]?letter|DLQ|DeadLetter|idempoten|dedup|DefaultAfterRollbackProcessor"]
    )
    hybrid("REL-03", "Duplicate or poison-message handling", messaging_safety, confidence="low")
    concurrency = view.find(
        [
            r"@Async\b|@Scheduled\b|ThreadPoolTaskExecutor|ExecutorService",
            r"core[-_.]?pool[-_.]?size|max[-_.]?pool[-_.]?size|queue[-_.]?capacity",
            r"synchronized\s*\(|Atomic(?:Integer|Long|Reference)|ReentrantLock",
        ],
        path_patterns=[r"src/main/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("REL-04", "Async, scheduler, executor, or shared-state controls", concurrency, confidence="low")

    high_confidence_secrets = [
        finding for finding in inventory.secret_findings if finding.confidence == "high"
    ]
    secret_scanners = view.find(
        [r"gitleaks|trufflehog|detect-secrets|secretlint"],
        path_patterns=[r"\.github/", r"Jenkinsfile", r"Makefile", r"\.toml$", r"\.ya?ml$"],
    )
    if high_confidence_secrets:
        results["SEC-01"] = Prefill(
            "SEC-01",
            "fail",
            "Potential hardcoded credential material: "
            + ", ".join(finding.evidence() for finding in high_confidence_secrets[:6]),
            "Values are intentionally redacted. Review and rotate confirmed credentials before removal.",
            "AUTOMATED",
            source_map.get("SEC-01", ""),
            "high",
        )
    elif inventory.secret_findings:
        results["SEC-01"] = Prefill(
            "SEC-01",
            "partial",
            "Potential hardcoded development defaults or examples: "
            + ", ".join(finding.evidence() for finding in inventory.secret_findings[:6]),
            "Review context and externalize any value used outside disposable local or test environments.",
            "HYBRID",
            source_map.get("SEC-01", ""),
            "medium",
        )
    else:
        hybrid(
            "SEC-01",
            "Secret-scanning configuration",
            secret_scanners,
            confidence="medium",
            missing_reason="No high-confidence secret found, but no secret-scanning configuration was detected; absence is not proof",
        )
    security = view.find(
        [
            r"SecurityFilterChain|WebSecurityConfigurerAdapter",
            r"EnableMethodSecurity|EnableWebSecurity|spring-boot-starter-security",
        ]
    )
    hybrid("SEC-02", "Spring Security boundary configuration", security, confidence="low")
    validation = view.find(
        [
            r"jakarta\.validation|javax\.validation|@Valid\b|@Validated\b|ConstraintValidator",
            r"redact|mask(?:ing)?|sensitive.*log|JsonIgnore",
        ]
    )
    sensitive_sinks = view.find(
        [r"ObjectInputStream|Runtime\.getRuntime\(\)\.exec|ProcessBuilder|Paths?\.get\("]
    )
    if validation:
        hybrid(
            "SEC-03",
            "Trust-boundary validation or redaction"
            + ("; sensitive sinks also require review" if sensitive_sinks else ""),
            validation + sensitive_sinks,
            confidence="low",
        )
    else:
        review(
            "SEC-03",
            "sensitive sinks without detected validation or redaction",
            sensitive_sinks,
            confidence="low",
            missing_reason="No validation or redaction signal found; manual trust-boundary review is required",
        )
    dependency_scan = view.find(
        [r"dependency-check|dependencytrack|dependabot|renovate|snyk|trivy|grype"],
        path_patterns=[r"pom\.xml", r"gradle", r"\.github/", r"Jenkinsfile", r"\.ya?ml$"],
    )
    component_security = dependency_scan + view.find(
        [r"cyclonedx|spdx|sbom"],
        path_patterns=[r"pom\.xml", r"gradle", r"\.github/", r"Jenkinsfile", r"\.ya?ml$"],
    )
    hybrid("SEC-04", "Component vulnerability or SBOM analysis", component_security)

    test_paths = view.paths([r"(^|/)src/test/.*\.(java|kt|groovy)$"], limit=8)
    hybrid("TST-01", f"Automated tests ({inventory.test_files} test source files)", test_paths, confidence="low")
    realistic_integration_tests = view.find([r"Testcontainers|@Container|jdbc:tc:"])
    spring_integration_tests = view.find([r"@SpringBootTest"])
    hybrid(
        "TST-02",
        "Realistic integration-test infrastructure",
        realistic_integration_tests or spring_integration_tests,
        confidence="medium" if realistic_integration_tests else "low",
    )
    contract_tests = view.find([r"spring-cloud-contract|pact-jvm|@Pact|ContractVerifier"])
    hybrid("TST-03", "Consumer or provider contract testing", contract_tests)
    deterministic_tests = view.find(
        [r"@DirtiesContext|@Sql\b|@ResourceLock|Clock\b|Awaitility|junit\.jupiter\.execution\.parallel"],
        path_patterns=[r"src/test/", r"pom\.xml$", r"build\.gradle", r"junit-platform\.properties$"],
    )
    hybrid("TST-04", "Test isolation or deterministic-time controls", deterministic_tests, confidence="low")

    structured_logs = view.find(
        [r"logstash-logback|ecs-logging|logging\.structured|correlation[-_. ]?id|traceId|MDC\.put"],
        path_patterns=[r"pom\.xml", r"gradle", r"src/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("OBS-01", "Structured, correlated, or redacted logging", structured_logs, confidence="low")
    metrics = view.find([r"spring-boot-starter-actuator|micrometer|/actuator/prometheus|MeterRegistry"])
    hybrid("OBS-02", "Actuator or Micrometer metrics instrumentation", metrics, confidence="low")
    tracing = view.find([r"opentelemetry|micrometer-tracing|zipkin|brave|ObservationRegistry"])
    hybrid("OBS-03", "Distributed tracing instrumentation", tracing, confidence="low")
    health = view.find(
        [r"HealthIndicator|ReactiveHealthIndicator|AvailabilityChangeEvent", r"management\.endpoint\.health|readiness|liveness"],
        path_patterns=[r"src/main/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("OBS-04", "Health, readiness, or startup-state instrumentation", health, confidence="low")

    complexity_analysis = view.find(
        [r"sonar\.complexity|cyclomatic|pmd|checkstyle"],
        path_patterns=[r"pom\.xml$", r"build\.gradle", r"sonar", r"pmd", r"checkstyle"],
    )
    oversized_sources = _large_source_files(view)
    if complexity_analysis:
        hybrid(
            "MNT-01",
            "Complexity analysis configuration"
            + ("; oversized sources also require review" if oversized_sources else ""),
            complexity_analysis + oversized_sources,
            confidence="low",
        )
    else:
        review(
            "MNT-01",
            "oversized source files without detected complexity analysis",
            oversized_sources,
            confidence="low",
            missing_reason="No complexity analysis configuration found; source complexity remains unverified",
        )
    code_cleanup = view.find(
        [r"duplicate-finder|maven-dependency-analyzer|dependencyAnalysis|deptrim|sonar\.cpd"],
        path_patterns=[r"pom\.xml$", r"build\.gradle", r"\.ya?ml$", r"\.properties$"],
    )
    hybrid("MNT-02", "Duplicate, dead-code, or unused-dependency analysis", code_cleanup, confidence="low")
    debt_markers = view.find(
        [r"\b(?:TODO|FIXME|HACK|XXX)\b", r"@SuppressWarnings|noinspection"],
        path_patterns=[r"src/main/.*\.(?:java|kt|groovy)$"],
    )
    review(
        "MNT-03",
        "technical-debt markers or suppressions",
        debt_markers,
        confidence="low",
        missing_reason="No debt marker found; scope and actionability of technical debt remain unverified",
    )
    static_analysis = view.find(
        [r"checkstyle|pmd|spotbugs|errorprone|sonar|detekt"],
        path_patterns=[r"pom\.xml$", r"build\.gradle", r"\.github/", r"Jenkinsfile", r"\.ya?ml$", r"\.xml$"],
    )
    hybrid("MNT-04", "Versioned static-analysis configuration", static_analysis, confidence="medium")

    contracts = view.paths(
        [
            r"openapi.*\.(?:ya?ml|json)$",
            r"asyncapi.*\.(?:ya?ml|json)$",
            r"\.(?:avsc|proto|graphqls)$",
            r"json.?schema.*\.json$",
        ]
    )
    contracts += view.find(
        [r"@OpenAPIDefinition|@Operation\b|springdoc-openapi"],
        path_patterns=[r"src/main/", r"pom\.xml$", r"build\.gradle"],
    )
    hybrid("API-01", "Machine-readable API or message contracts", contracts, confidence="medium")
    compatibility_checks = view.find(
        [r"openapi-diff|oasdiff|revapi|japicmp|schema.?registry.*compatib|compatibilityLevel"],
        path_patterns=[r"pom\.xml$", r"build\.gradle", r"\.github/", r"src/test/", r"\.ya?ml$"],
    )
    hybrid("API-02", "Automated backward-compatibility checks", compatibility_checks, confidence="medium")
    api_semantics = view.find(
        [
            r"@(?:Rest)?ControllerAdvice|ProblemDetail|ErrorResponse",
            r"@(?:Request|Get|Post|Put|Delete|Patch)Mapping\s*\([^)]*['\"]/v\d+",
            r"ApiVersion|deprecated\s*=\s*true",
        ],
        path_patterns=[r"src/main/", r"openapi", r"asyncapi", r"\.ya?ml$", r"\.json$"],
    )
    hybrid("API-03", "Versioning or consistent public error semantics", api_semantics, confidence="low")
    serialization = view.find(
        [
            r"ObjectMapper|Jackson2ObjectMapperBuilder|@JsonFormat|@JsonEnumDefaultValue",
            r"FAIL_ON_UNKNOWN_PROPERTIES|READ_UNKNOWN_ENUM_VALUES|JsonInclude",
        ],
        path_patterns=[r"src/main/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("API-04", "Explicit serialization compatibility rules", serialization, confidence="low")

    for check in check_list:
        if check.check_id not in results:
            manual(check.check_id, f"Manual evidence required: {check.evidence_required}")
    return [results[check.check_id] for check in check_list]


def load_source_map(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["id"].strip(): row["sources"].strip()
            for row in csv.DictReader(handle)
        }


def write_assessment(path: Path, prefills: Iterable[Prefill]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "id",
                "status",
                "evidence",
                "owner",
                "target_date",
                "notes",
                "assessment_type",
                "source_basis",
                "confidence",
            ]
        )
        for item in prefills:
            writer.writerow(
                [
                    item.check_id,
                    item.status,
                    item.evidence,
                    "",
                    "",
                    item.notes,
                    item.assessment_type,
                    item.source_basis,
                    item.confidence,
                ]
            )


def render_scan_report(inventory: Inventory, prefills: Iterable[Prefill]) -> str:
    items = list(prefills)
    status_counts = Counter(item.status for item in items)
    type_counts = Counter(item.assessment_type for item in items)
    lines = [
        f"# Repository Scan: {inventory.repository_name}",
        "",
        "> Static prefill only. A detected signal is not proof that a control is effective, complete, or production-ready.",
        "",
        "## Inventory",
        "",
        f"- Build system: {', '.join(inventory.build_systems)}",
        f"- Java version: {inventory.java_version}",
        f"- Spring Boot version: {inventory.spring_boot_version}",
        f"- Files scanned: {inventory.files_scanned}",
        f"- Java source files: {inventory.java_files}",
        f"- Test source files: {inventory.test_files}",
        f"- Dependency coordinates: {len(inventory.dependencies)}",
        "",
        "## Prefill Summary",
        "",
        f"- Statuses: {', '.join(f'{key}={value}' for key, value in sorted(status_counts.items()))}",
        f"- Assessment types: {', '.join(f'{key}={value}' for key, value in sorted(type_counts.items()))}",
        "",
        "The scanner intentionally does not emit `pass`. Human review must confirm completeness and effectiveness before changing `partial` or `unknown` to `pass`.",
        "",
        "## Findings",
        "",
        "| ID | Status | Type | Confidence | Evidence | Source basis |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| {item.check_id} | {item.status} | {item.assessment_type} | "
            f"{item.confidence} | {_markdown_cell(item.evidence)} | {item.source_basis} |"
        )

    lines.extend(["", "## Source Citations", ""])
    used_sources = sorted(
        {
            source
            for item in items
            for source in item.source_basis.split(";")
            if source
        }
    )
    for source in used_sources:
        url = SOURCE_URLS.get(source)
        lines.append(f"- [{source}]({url})" if url else f"- {source}")

    lines.extend(
        [
            "",
            "## Required Human Review",
            "",
            "- Verify detected Java and Spring Boot versions against the selected target support policy.",
            "- Run target-aware compiler, dependency convergence, and JDK deprecation analysis.",
            "- Review authorization, transaction, concurrency, and compatibility behavior.",
            "- Validate repository signals by compiling and testing the target application separately.",
            "- Investigate secret findings without committing credential values to assessment artifacts.",
            "- Replace scanner-generated evidence only after a reviewer confirms the final status.",
        ]
    )
    return "\n".join(lines) + "\n"


def _maven_inventory(view: RepositoryView) -> tuple[str, str, list[str], list[str]]:
    java_version = "not detected"
    boot_version = "not detected"
    dependencies: list[str] = []
    plugins: list[str] = []
    for relative_path in view.paths([r"(^|/)pom\.xml$"], limit=len(view.files)):
        try:
            root = ET.fromstring(view.files[relative_path])
        except ET.ParseError:
            continue
        prefix = ""
        if root.tag.startswith("{"):
            prefix = root.tag.split("}", 1)[0] + "}"

        properties: dict[str, str] = {}
        properties_node = root.find(f"{prefix}properties")
        if properties_node is not None:
            for child in properties_node:
                properties[_local_name(child.tag)] = (child.text or "").strip()

        for key in ("java.version", "maven.compiler.release", "maven.compiler.target", "maven.compiler.source"):
            if properties.get(key):
                java_version = properties[key]
                break

        parent = root.find(f"{prefix}parent")
        if parent is not None and _child_text(parent, prefix, "artifactId") == "spring-boot-starter-parent":
            boot_version = (
                _resolve_property(_child_text(parent, prefix, "version"), properties)
                or boot_version
            )
        if properties.get("spring-boot.version"):
            boot_version = properties["spring-boot.version"]

        for dependency in root.iter(f"{prefix}dependency"):
            group = _child_text(dependency, prefix, "groupId")
            artifact = _child_text(dependency, prefix, "artifactId")
            version = _resolve_property(_child_text(dependency, prefix, "version"), properties)
            if group and artifact:
                dependencies.append(f"{group}:{artifact}" + (f":{version}" if version else ""))
        for plugin in root.iter(f"{prefix}plugin"):
            group = _child_text(plugin, prefix, "groupId") or "org.apache.maven.plugins"
            artifact = _child_text(plugin, prefix, "artifactId")
            if artifact:
                plugins.append(f"{group}:{artifact}")
                if artifact == "spring-boot-maven-plugin":
                    version = _resolve_property(_child_text(plugin, prefix, "version"), properties)
                    if version:
                        boot_version = version
    return java_version, boot_version, dependencies, plugins


def _gradle_inventory(view: RepositoryView) -> tuple[str, str, list[str], list[str]]:
    java_version = "not detected"
    boot_version = "not detected"
    dependencies: list[str] = []
    plugins: list[str] = []
    for path in view.paths([r"(^|/)build\.gradle(?:\.kts)?$"], limit=len(view.files)):
        text = view.files[path]
        version_match = re.search(
            r"(?:JavaLanguageVersion\.of|jvmToolchain)\s*\(?\s*(\d+)", text
        ) or re.search(r"sourceCompatibility\s*=\s*(?:JavaVersion\.VERSION_)?(\d+)", text)
        if version_match:
            java_version = version_match.group(1)
        boot_match = re.search(
            r"(?:id\s*\(?\s*['\"]org\.springframework\.boot['\"]\s*\)?|id\s+['\"]org\.springframework\.boot['\"])\s*version\s*['\"]([^'\"]+)",
            text,
        )
        if boot_match:
            boot_version = boot_match.group(1)
            plugins.append("org.springframework.boot")
        for match in re.finditer(r"['\"]([\w.-]+:[\w.-]+)(?::[^'\"]+)?['\"]", text):
            dependencies.append(match.group(1))
    return java_version, boot_version, dependencies, plugins


def _large_source_files(view: RepositoryView, *, line_limit: int = 500) -> list[str]:
    matches: list[str] = []
    for path in sorted(view.files):
        if not re.search(r"src/main/.*\.(?:java|kt|groovy)$", path, re.IGNORECASE):
            continue
        nonblank_lines = sum(1 for line in view.files[path].splitlines() if line.strip())
        if nonblank_lines > line_limit:
            matches.append(path)
            if len(matches) == 6:
                break
    return matches


def _scan_secrets(view: RepositoryView) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    exact_patterns = [
        ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ]
    config_assignment = re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?([^'\"\s#,;]+)"
    )
    code_assignment = re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*=\s*['\"]([^'\"]+)['\"]"
    )
    for path, text in view.files.items():
        for line_number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in exact_patterns:
                if pattern.search(line):
                    findings.append(SecretFinding(path, line_number, kind, "high"))
            match = (
                code_assignment.search(line)
                if Path(path).suffix.lower() in {".java", ".kt", ".groovy"}
                else config_assignment.search(line)
            )
            if not match:
                continue
            value = match.group(2).strip()
            if _looks_like_placeholder(value):
                continue
            confidence = _assignment_confidence(value, path)
            findings.append(
                SecretFinding(path, line_number, f"hardcoded {match.group(1).lower()}", confidence)
            )
    unique = {(item.path, item.line, item.kind, item.confidence): item for item in findings}
    return sorted(unique.values(), key=lambda item: (item.path, item.line, item.kind))


def _looks_like_placeholder(value: str) -> bool:
    normalized = value.lower()
    return (
        value.startswith(("${", "$(", "{{", "<"))
        or normalized in {"", "null", "none", "redacted", "masked", "example", "placeholder"}
        or "env" in normalized
        or set(value) <= {"*", "x", "X"}
    )


def _assignment_confidence(value: str, path: str) -> str:
    if (
        re.search(r"(^|/)(test|tests|examples?|docs?)(/|$)", path, re.IGNORECASE)
        or path.lower().endswith(".md")
        or value.lower() in {"guest", "root", "password", "changeme", "admin", "test"}
    ):
        return "medium"
    character_classes = sum(
        bool(pattern.search(value))
        for pattern in (
            re.compile(r"[a-z]"),
            re.compile(r"[A-Z]"),
            re.compile(r"\d"),
            re.compile(r"[^A-Za-z0-9]"),
        )
    )
    return "high" if len(value) >= 12 and character_classes >= 3 else "medium"


def _is_text_candidate(path: Path) -> bool:
    return (
        path.name in TEXT_FILENAMES
        or path.name.startswith(".env")
        or path.suffix.lower() in TEXT_SUFFIXES
    )


def _child_text(parent: ET.Element, prefix: str, name: str) -> str:
    child = parent.find(f"{prefix}{name}")
    return (child.text or "").strip() if child is not None else ""


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _resolve_property(value: str, properties: dict[str, str]) -> str:
    match = re.fullmatch(r"\$\{([^}]+)}", value)
    return properties.get(match.group(1), value) if match else value


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
