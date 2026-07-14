from __future__ import annotations

import sys
import tempfile
import unittest
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
        self.assertEqual("HYBRID", prefills["ARC-02"].assessment_type)
        self.assertEqual("partial", prefills["DAT-03"].status)
        self.assertEqual("partial", prefills["TST-02"].status)
        self.assertEqual("partial", prefills["DEL-03"].status)

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
