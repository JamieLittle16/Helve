"""Pinned five-method discrete-shape findings never constitute VAR/SEM admission."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import official_r2c_heightmap_facts as official
import r2c_heightmap_delegate_exact_review as extractor

REPORT = ROOT / "vanilla/reviews/network/r2c-discrete-shape-five-source-free-findings.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class DiscreteShapeFindingsTests(unittest.TestCase):
    def test_five_source_roots_and_abstract_declarations(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], 1)
        self.assertEqual(report["kind"], "r2c-26_2-five-discrete-shape-delegates-source-free-v1")
        self.assertEqual(report["source_archive_sha256"], official.SOURCE_ARCHIVE_SHA256)
        self.assertRegex(report["local_source_rich_sha256"], SHA256)
        self.assertEqual(report["selection_scope"], "pending-discrete")
        self.assertEqual(report["expected_selected_roots"], 5)
        self.assertEqual(report["extracted_methods"], 5)
        self.assertEqual(report["missing_optional_methods"], 0)
        roots = extractor.PENDING_DISCRETE_ROOTS
        methods = report["methods"]
        self.assertEqual(len(roots), len(methods))
        self.assertEqual([m["index"] for m in methods], [1, 2, 3, 4, 5])
        self.assertEqual([m["source_identity"].split("#")[0] for m in methods],
                         [r.owner for r in roots])
        self.assertEqual(
            [m["source_identity"].split("#")[1].split("(")[0] for m in methods],
            [r.method for r in roots],
        )
        for method in methods:
            self.assertRegex(method["atlas_body_sha256"], SHA256)
            self.assertRegex(method["source_excerpt_sha256"], SHA256)
            self.assertIs(method["first_pass_source_inspected"], True)
            self.assertIs(method["semantics_admitted"], False)

        for i in [1, 2]:
            self.assertEqual(methods[i]["declaration_kind"], "abstract")
            self.assertIs(methods[i]["has_executable_body"], False)
            self.assertEqual(
                methods[i]["atlas_body_sha256"], extractor.EMPTY_BODY_SHA256,
            )
        for i in [0, 3, 4]:
            self.assertEqual(methods[i]["declaration_kind"], "executable")
            self.assertIs(methods[i]["has_executable_body"], True)
        self.assertIn(
            "has_source_body=true", report["original_extractor_abstract_method_reporting_defect"]
        )

    def test_source_laws_keep_dispatch_boundary_explicit(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(i for entry in report["source_laws"] for i in entry["methods"]),
            list(range(1, 6)),
        )
        combined = " ".join(entry["text"] for entry in report["source_laws"])
        for term in (
            "firstFull", "lastFull", "AXIS_VALUES", "abstract",
            "Direction.Axis.choose", "getCoords", "getDouble",
        ):
            self.assertIn(term, combined)
        self.assertGreaterEqual(len(report["outstanding"]), 4)

    def test_local_source_and_promotion_are_not_checked_in(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertIs(report["contains_official_source_text"], False)
        self.assertIn("NO_VAR_SEM_OR_PRODUCTION", report["commit_policy"])
        for flag in (
            "executable_delegates_fully_closed",
            "independent_atlas_gate_passed", "source_semantics_admitted",
            "client_biome_ids_admitted", "production_admitted",
        ):
            self.assertIs(report[flag], False, flag)
        source_free = REPORT.read_text(encoding="utf-8")
        for forbidden in ('"excerpt"', '"source_text"', '"source_path"'):
            self.assertNotIn(forbidden, source_free)


if __name__ == "__main__":
    unittest.main()
