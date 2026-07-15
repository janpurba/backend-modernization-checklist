from __future__ import annotations

import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assessment_core import load_catalog  # noqa: E402
from repository_scanner import (  # noqa: E402
    ScanError,
    build_inventory,
    collect_repository,
    load_source_map,
    prefill_assessment,
)


FIXTURE = ROOT / "tests" / "fixtures" / "spring-service"


class RepositoryScannerTest(unittest.TestCase):
    def scan_fixture(self):
        view = collect_repository(FIXTURE)
        inventory = build_inventory(view)
        prefills = prefill_assessment(
            view,
            inventory,
            load_catalog(ROOT / "checklist" / "catalog.csv"),
            load_source_map(ROOT / "checklist" / "source-map.csv"),
        )
        return inventory, {item.check_id: item for item in prefills}

    def test_detects_maven_java_and_spring_boot_inventory(self) -> None:
        inventory, _ = self.scan_fixture()
        self.assertEqual(("Maven",), inventory.build_systems)
        self.assertEqual("21", inventory.java_version)
        self.assertEqual("3.4.0", inventory.spring_boot_version)
        self.assertEqual(2, inventory.test_files)

    def test_prefills_all_catalog_checks_with_source_basis(self) -> None:
        _, prefills = self.scan_fixture()
        self.assertEqual(40, len(prefills))
        self.assertTrue(all(item.source_basis for item in prefills.values()))
        self.assertEqual("partial", prefills["RUN-01"].status)
        self.assertEqual("HYBRID", prefills["ARC-01"].assessment_type)
        self.assertEqual("unknown", prefills["CMP-01"].status)
        self.assertEqual("partial", prefills["OBS-02"].status)
        self.assertEqual("partial", prefills["TST-02"].status)
        self.assertNotIn("DEL-03", prefills)

    def test_catalog_has_four_checks_in_each_final_domain(self) -> None:
        checks = load_catalog(ROOT / "checklist" / "catalog.csv")
        self.assertEqual(
            {
                "API and Integration Contracts",
                "Architecture",
                "Data and Persistence",
                "Maintainability and Code Health",
                "Observability Instrumentation",
                "Reliability and Concurrency",
                "Runtime",
                "Security",
                "Testing and Verification",
                "Upgrade Compatibility",
            },
            {check.domain for check in checks},
        )
        self.assertEqual({4}, set(Counter(check.domain for check in checks).values()))
        self.assertFalse(
            any(check.check_id.startswith(("OWN-", "DEL-", "OPS-")) for check in checks)
        )

    def test_detects_upgrade_maintainability_and_api_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pom.xml").write_text(
                "<project><modelVersion>4.0.0</modelVersion>"
                "<build><plugins><plugin><artifactId>maven-checkstyle-plugin</artifactId>"
                "</plugin></plugins></build></project>",
                encoding="utf-8",
            )
            source = root / "src" / "main" / "java" / "example"
            source.mkdir(parents=True)
            (source / "LegacyFilter.java").write_text(
                "package example;\n"
                "import javax.servlet.Filter;\n"
                "class LegacyFilter implements Filter { // TODO migrate\n"
                "  Object mapper = new ObjectMapper();\n"
                "}\n",
                encoding="utf-8",
            )
            (root / "openapi.yaml").write_text("openapi: 3.0.3\n", encoding="utf-8")
            view = collect_repository(root)
            prefills = {
                item.check_id: item
                for item in prefill_assessment(
                    view,
                    build_inventory(view),
                    load_catalog(ROOT / "checklist" / "catalog.csv"),
                    load_source_map(ROOT / "checklist" / "source-map.csv"),
                )
            }
            self.assertEqual("unknown", prefills["CMP-03"].status)
            self.assertEqual("HYBRID", prefills["CMP-03"].assessment_type)
            self.assertEqual("partial", prefills["CMP-04"].status)
            self.assertEqual("unknown", prefills["MNT-03"].status)
            self.assertEqual("HYBRID", prefills["MNT-03"].assessment_type)
            self.assertEqual("partial", prefills["MNT-04"].status)
            self.assertEqual("partial", prefills["API-01"].status)
            self.assertEqual("partial", prefills["API-04"].status)

    def test_domain_specific_detectors_ignore_unrelated_similar_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "main" / "java" / "example"
            source.mkdir(parents=True)
            (source / "Request.java").write_text(
                "package example;\n"
                "@Validated class Request {\n"
                '  String externalUrl = "https://example.test/v1/items";\n'
                "  int timeout = 10;\n"
                "}\n",
                encoding="utf-8",
            )
            view = collect_repository(root)
            prefills = {
                item.check_id: item
                for item in prefill_assessment(
                    view,
                    build_inventory(view),
                    load_catalog(ROOT / "checklist" / "catalog.csv"),
                    load_source_map(ROOT / "checklist" / "source-map.csv"),
                )
            }
            self.assertEqual("unknown", prefills["RUN-03"].status)
            self.assertEqual("unknown", prefills["DAT-03"].status)
            self.assertEqual("unknown", prefills["API-03"].status)

    def test_placeholder_secret_is_not_reported(self) -> None:
        inventory, prefills = self.scan_fixture()
        self.assertEqual((), inventory.secret_findings)
        self.assertEqual("partial", prefills["SEC-01"].status)
        self.assertIn("Secret-scanning configuration", prefills["SEC-01"].evidence)

    def test_high_confidence_secret_produces_automated_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "application.properties").write_text(
                "api_key=ProductionSecret123!\n", encoding="utf-8"
            )
            view = collect_repository(root)
            inventory = build_inventory(view)
            prefills = {
                item.check_id: item
                for item in prefill_assessment(
                    view,
                    inventory,
                    load_catalog(ROOT / "checklist" / "catalog.csv"),
                    load_source_map(ROOT / "checklist" / "source-map.csv"),
                )
            }
            self.assertEqual("fail", prefills["SEC-01"].status)
            self.assertEqual("AUTOMATED", prefills["SEC-01"].assessment_type)
            self.assertNotIn("ProductionSecret123", prefills["SEC-01"].evidence)

    def test_method_call_assignment_is_not_a_hardcoded_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Secrets.java").write_text(
                "class Secrets {\n"
                "  String secret = secretManager.getSecret(secretName);\n"
                "  String apiKey = parameters.getSystemParameter(key);\n"
                "}\n",
                encoding="utf-8",
            )
            inventory = build_inventory(collect_repository(root))
            self.assertEqual((), inventory.secret_findings)

    def test_java_string_literal_secret_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Secrets.java").write_text(
                'class Secrets { String apiKey = "ProductionSecret123!"; }\n',
                encoding="utf-8",
            )
            inventory = build_inventory(collect_repository(root))
            self.assertEqual(1, len(inventory.secret_findings))
            self.assertEqual("high", inventory.secret_findings[0].confidence)

    def test_file_limit_is_enforced(self) -> None:
        with self.assertRaisesRegex(ScanError, "max-files"):
            collect_repository(FIXTURE, max_files=1)

    def test_detects_gradle_kotlin_dsl_versions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build.gradle.kts").write_text(
                'plugins { id("org.springframework.boot") version "4.1.0" }\n'
                "java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }\n"
                'dependencies { implementation("org.springframework.boot:spring-boot-starter-web") }\n',
                encoding="utf-8",
            )
            inventory = build_inventory(collect_repository(root))
            self.assertEqual(("Gradle",), inventory.build_systems)
            self.assertEqual("21", inventory.java_version)
            self.assertEqual("4.1.0", inventory.spring_boot_version)


if __name__ == "__main__":
    unittest.main()
