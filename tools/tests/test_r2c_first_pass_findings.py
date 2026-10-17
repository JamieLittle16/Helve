"""Source-free R2C first-pass findings are anchored and never grant admission."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import r2c_final_review_focus as focus

REPORT = ROOT / "vanilla/reviews/network/r2c-first-pass-source-free-observations.json"
WIRE_INSPECTION = ROOT / "docs/qualification/R2C_26_2_SOURCE_WIRE_INSPECTION.md"
FINDINGS = ROOT / "docs/qualification/R2C_FIRST_PASS_PINNED_SOURCE_FINDINGS.md"

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class FirstPassFindingsTests(unittest.TestCase):
    def test_source_identity_and_exact_review_roots(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], 1)
        self.assertEqual(report["kind"], "r2c-26_2-first-pass-source-free-observations-v1")
        self.assertEqual(report["source_archive_sha256"], focus.existing.EXPECTED_SHA)
        self.assertEqual(
            report["focus_sha256"],
            "68881bbb15f77cefea774551d7f32735ba50dcaa4727960f2245689b751b3ee6",
        )
        self.assertRegex(report["source_rich_local_review_file_sha256"], HEX_SHA256)
        self.assertTrue(report["first_pass_inspected"])
        self.assertFalse(report["source_text_committed"])
        for key in (
            "independent_human_source_review_complete",
            "independent_atlas_gate_passed",
            "delegate_closure_proven",
            "client_biome_ids_admitted",
            "heightmap_per_state_semantics_admitted",
            "outer_wire_admitted",
            "production_admitted",
        ):
            self.assertIs(report[key], False, key)

        expected_roots = focus.BIOME + focus.WIRE
        self.assertEqual(len(expected_roots), 19)
        methods = report["methods"]
        self.assertEqual(len(methods), len(expected_roots))
        self.assertEqual(
            [method["review_index"] for method in methods],
            list(range(1, len(expected_roots) + 1)),
        )
        for index, item in enumerate(methods):
            self.assertEqual(set(item),
                             {"review_index", "group", "body_sha256", "source_excerpt_sha256"})
            self.assertEqual(
                item["group"], "biome_priority" if index < len(focus.BIOME)
                else "outer_wire_priority",
            )
            self.assertRegex(item["body_sha256"], HEX_SHA256)
            self.assertRegex(item["source_excerpt_sha256"], HEX_SHA256)
        self.assertEqual(len(set(x["body_sha256"] for x in methods)), len(methods))
        self.assertEqual(len(set(x["source_excerpt_sha256"] for x in methods)), len(methods))
        # The official Java source, local excerpts, and copied source-line
        # fragments must never enter the repository review record.
        raw = REPORT.read_text(encoding="utf-8")
        self.assertNotIn('"source_excerpt"', raw)
        self.assertNotIn('"source_path"', raw)
        self.assertNotIn("private void sendChunk", raw)
        self.assertNotIn("public Holder.Reference", raw)

    def test_semantic_observations_cover_exact_roots_not_delegates(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(
            set(index for observation in report["observations"]
                for index in observation["indices"]), set(range(1, 20))
        )
        self.assertEqual(
            sum(len(observation["indices"]) for observation in report["observations"]), 19
        )
        self.assertEqual(
            len(set(item["id"] for item in report["observations"])),
            len(report["observations"]),
        )
        for observation in report["observations"]:
            self.assertTrue(observation["finding"])
            self.assertTrue(observation["indices"])
        self.assertGreaterEqual(len(report["unresolved"]), 5)
        doc = FINDINGS.read_text(encoding="utf-8")
        self.assertIn(report["source_archive_sha256"], doc)
        self.assertIn(report["focus_sha256"], doc)
        self.assertIn(report["source_rich_local_review_file_sha256"], doc)
        self.assertIn("not a complete delegation closure", doc)
        self.assertIn("ID 11", doc)

    def test_wire_doc_keeps_distinct_server_and_client_batch_ids(self) -> None:
        inspected = WIRE_INSPECTION.read_text(encoding="utf-8")
        self.assertIn("serverbound `chunk_batch_received = 11`", inspected)
        self.assertIn("`chunk_batch_finished = 11`", inspected)
        self.assertIn("`chunk_batch_start = 12`", inspected)
        self.assertNotIn("serverbound `chunk_batch_received = 12`", inspected)


if __name__ == "__main__":
    unittest.main()
