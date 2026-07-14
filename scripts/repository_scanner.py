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

    codeowners = view.paths([r"(^|/)CODEOWNERS$"])
    architecture_docs = view.find(
        [r"\b(context diagram|service boundary|architecture|capabilit(?:y|ies))\b"],
        path_patterns=[r"README", r"docs/", r"\.md$"],
    )
    consumer_docs = view.find(
        [r"\b(consumer|caller|dependency|integration|openapi|asyncapi)\b"],
        path_patterns=[r"README", r"docs/", r"openapi", r"asyncapi", r"\.ya?ml$"],
    )
    measurable_goals = view.find(
        [r"\b(SLO|baseline|target latency|error budget|deployment frequency|change fail)\b"],
        path_patterns=[r"README", r"docs/", r"\.ya?ml$"],
    )

    hybrid("OWN-01", "Ownership metadata", codeowners, confidence="low")
    hybrid("OWN-02", "Architecture or capability documentation", architecture_docs)
    hybrid("OWN-03", "Consumer or integration inventory", consumer_docs, confidence="low")
    hybrid("OWN-04", "Measurable modernization or reliability goals", measurable_goals)

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

    dependency_scan = view.find(
        [r"dependency-check|dependencytrack|dependabot|renovate|snyk|trivy|grype"],
        path_patterns=[r"pom\.xml", r"gradle", r"\.github/", r"Jenkinsfile", r"\.ya?ml$"],
    )
    if build_paths:
        scan_suffix = (
            f"; vulnerability scan configuration: {', '.join(dependency_scan)}"
            if dependency_scan
            else "; no vulnerability scan configuration detected"
        )
        results["RUN-02"] = Prefill(
            "RUN-02",
            "partial",
            f"Dependency inventory contains {len(inventory.dependencies)} coordinates from "
            f"{', '.join(build_paths)}{scan_suffix}",
            "Inventory is static and unresolved; vulnerability and end-of-life status require tool output and review.",
            "HYBRID",
            source_map.get("RUN-02", ""),
            "high" if dependency_scan else "medium",
        )
    else:
        manual("RUN-02", "No Maven or Gradle dependency descriptor found")
    graceful = view.find(
        [r"server\.shutdown\s*[:=]\s*graceful", r"shutdown\s*:\s*graceful", r"graceful[ -]shutdown"]
    )
    startup_validation = view.find([r"@ConfigurationProperties", r"@Validated", r"fail[- ]fast"])
    hybrid("RUN-03", "Startup validation or graceful shutdown", graceful + startup_validation)
    runtime_limits = view.find(
        [r"MaxRAMPercentage|-Xmx|-Xms|resources:\s*$|memory:\s*\d|JAVA_TOOL_OPTIONS"],
        path_patterns=[r"Dockerfile", r"\.ya?ml$", r"\.properties$", r"Jenkinsfile"],
    )
    hybrid("RUN-04", "Explicit JVM or container resource settings", runtime_limits)

    transaction_signals = view.find(
        [r"@Transactional|TransactionTemplate|transaction boundary|data owner"],
        path_patterns=[r"\.java$", r"\.kt$", r"\.md$"],
    )
    hybrid("ARC-01", "Transaction or data ownership signals", transaction_signals, confidence="low")
    architecture_tests = view.find([r"ArchUnit|layeredArchitecture|slices\(\)|SpringModulith"])
    hybrid("ARC-02", "Enforced module or architecture boundaries", architecture_tests)
    adapter_signals = view.find(
        [r"\b(adapter|gateway|port)\b|WebClient|RestClient|FeignClient|RestTemplate"],
        path_patterns=[r"src/main/.*\.(java|kt)$"],
    )
    hybrid("ARC-03", "External integration adapters or clients", adapter_signals, confidence="low")
    shared_library_docs = view.find(
        [r"shared librar|compatibility policy|version policy"], path_patterns=[r"\.md$"]
    )
    hybrid("ARC-04", "Shared-library ownership or compatibility policy", shared_library_docs)

    migration_paths = view.paths([r"db/migration/", r"liquibase", r"changelog.*\.(xml|ya?ml|json)$"])
    hybrid("DAT-01", "Versioned database migrations", migration_paths)
    plan_evidence = view.find(
        [r"EXPLAIN(?: ANALYZE)?|query digest|rows examined"],
        path_patterns=[r"\.md$", r"evidence/", r"artifacts/", r"\.sql$"],
    )
    hybrid("DAT-02", "Query plans or digest evidence", plan_evidence)
    pool_config = view.find(
        [
            r"maximum[-_.]?pool[-_.]?size",
            r"connection[-_.]?timeout",
            r"validation[-_.]?timeout",
            r"idle[-_.]?timeout",
            r"maximumPoolSize",
        ],
        path_patterns=[r"\.properties$", r"\.ya?ml$", r"\.java$", r"\.kt$"],
    )
    hybrid("DAT-03", "Bounded connection-pool configuration", pool_config)
    retention = view.find(
        [r"retention|archive|cleanup|purge|delete.*older than|@Scheduled"],
        path_patterns=[r"src/", r"docs/", r"\.sql$", r"\.md$"],
    )
    hybrid("DAT-04", "Retention or cleanup implementation", retention, confidence="low")

    retry = view.find([r"@Retryable|resilience4j\.retry|RetryTemplate|retryWhen"])
    idempotency = view.find([r"idempoten|dedup|Idempotency-Key|processed_event"])
    hybrid("REL-01", "Retry and idempotency signals", retry + idempotency, confidence="low")
    timeouts = view.find(
        [r"connect[-_.]?timeout|read[-_.]?timeout|response[-_.]?timeout|callTimeout|TimeLimiter"],
        path_patterns=[r"src/", r"\.properties$", r"\.ya?ml$"],
    )
    isolation = view.find([r"CircuitBreaker|Bulkhead|resilience4j\.(circuitbreaker|bulkhead)"])
    hybrid("REL-02", "Remote-call deadlines or failure isolation", timeouts + isolation)
    messaging_safety = view.find(
        [r"dead[-_. ]?letter|DLQ|DeadLetter|idempoten|dedup|DefaultAfterRollbackProcessor"]
    )
    hybrid("REL-03", "Duplicate or poison-message handling", messaging_safety, confidence="low")
    load_tests = view.paths([r"(^|/)(k6|jmeter|gatling|load-tests?|performance-tests?)(/|\.)"])
    load_tests += view.find([r"http_reqs|constant-arrival-rate|jmeter|gatling"], limit=4)
    hybrid("REL-04", "Load or degradation test assets", load_tests)

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
    security = view.find([r"SecurityFilterChain|EnableMethodSecurity|spring-boot-starter-security"])
    hybrid("SEC-02", "Spring Security boundary configuration", security, confidence="low")
    validation = view.find([r"jakarta\.validation|@Valid\b|@Validated\b|ConstraintValidator"])
    redaction = view.find([r"redact|mask(?:ing)?|sensitive.*log|JsonIgnore"])
    hybrid("SEC-03", "Input validation or sensitive-data handling", validation + redaction, confidence="low")
    artifact_security = dependency_scan + view.find(
        [r"cyclonedx|spdx|sbom|cosign|provenance|attest"],
        path_patterns=[r"pom\.xml", r"gradle", r"\.github/", r"Jenkinsfile", r"\.ya?ml$"],
    )
    hybrid("SEC-04", "Artifact provenance, SBOM, or vulnerability scanning", artifact_security)

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
    hybrid("TST-04", "Performance-test assets", load_tests)

    slo = view.find([r"serviceLevelObjective|service_level_objective|error budget|\bSLOs?\b"])
    hybrid("OBS-01", "SLI, SLO, or error-budget configuration", slo)
    structured_logs = view.find(
        [r"logstash-logback|ecs-logging|logging\.structured|correlation[-_. ]?id|traceId|MDC\.put"],
        path_patterns=[r"pom\.xml", r"gradle", r"src/", r"\.properties$", r"\.ya?ml$"],
    )
    hybrid("OBS-02", "Structured or correlated logging", structured_logs, confidence="low")
    metrics = view.find([r"spring-boot-starter-actuator|micrometer|/actuator/prometheus|MeterRegistry"])
    hybrid("OBS-03", "Actuator, metrics, or dependency-health instrumentation", metrics, confidence="low")
    tracing = view.find([r"opentelemetry|micrometer-tracing|zipkin|brave|ObservationRegistry"])
    hybrid("OBS-04", "Distributed tracing instrumentation", tracing, confidence="low")

    ci = view.paths([r"^\.github/workflows/.*\.ya?ml$", r"(^|/)Jenkinsfile$", r"\.gitlab-ci\.yml$"])
    container_build = view.paths([r"(^|/)Dockerfile$"])
    hybrid("DEL-01", "CI pipeline and repeatable build assets", ci + container_build, confidence="low")
    rollout = view.find(
        [r"canary|blue[- ]green|rollback|rollout|abort threshold"],
        path_patterns=[r"\.github/", r"deploy", r"helm", r"k8s", r"docs/", r"\.md$", r"\.ya?ml$"],
    )
    hybrid("DEL-02", "Incremental rollout or rollback procedure", rollout, confidence="low")
    config_validation = view.find([r"@ConfigurationProperties|@Validated|BindValidationException"])
    hybrid("DEL-03", "Configuration binding or startup validation", config_validation, confidence="low")
    message_compatibility = view.find([r"schema registry|compatibility|expand[- ]contract|event version"])
    hybrid("DEL-04", "Ordered compatibility or release sequencing", migration_paths + message_compatibility, confidence="low")

    on_call = view.find([r"on[- ]call|escalation|pagerduty|opsgenie"], path_patterns=[r"docs/", r"README", r"\.ya?ml$"])
    hybrid("OPS-01", "On-call or escalation metadata", on_call, confidence="low")
    runbooks = view.paths([r"runbooks?/", r"runbook.*\.md$"])
    hybrid("OPS-02", "Operational runbooks", runbooks, confidence="low")
    recovery = view.find(
        [r"backup|restore|disaster recovery|\bRPO\b|\bRTO\b"],
        path_patterns=[r"docs/", r"runbook", r"README", r"\.ya?ml$"],
    )
    hybrid("OPS-03", "Backup or recovery documentation", recovery, confidence="low")
    capacity = view.find(
        [r"capacity|cost baseline|cost per|forecast|autoscal"],
        path_patterns=[r"docs/", r"README", r"\.ya?ml$", r"terraform", r"helm"],
    )
    hybrid("OPS-04", "Capacity or cost-management evidence", capacity, confidence="low")

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
        writer = csv.writer(handle)
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
            "- Verify vendor support dates and commercial support agreements.",
            "- Review authorization behavior, data ownership, and transaction boundaries.",
            "- Attach runtime evidence for SLOs, query plans, capacity, rollback, restore, and incident readiness.",
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


def _scan_secrets(view: RepositoryView) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    exact_patterns = [
        ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ]
    assignment = re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?([^'\"\s#,;]+)"
    )
    for path, text in view.files.items():
        for line_number, line in enumerate(text.splitlines(), start=1):
            for kind, pattern in exact_patterns:
                if pattern.search(line):
                    findings.append(SecretFinding(path, line_number, kind, "high"))
            match = assignment.search(line)
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
