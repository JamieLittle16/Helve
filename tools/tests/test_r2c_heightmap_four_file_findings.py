"""Source-free pinned heightmap predicate observations must never imply admission."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import official_r2c_heightmap_facts as official
import r2c_heightmap_candidate_bytes as candidate

REPORT = ROOT / "vanilla/reviews/network/r2c-heightmap-four-file-source-findings.json"
DOC = ROOT / "docs/qualification/R2C_HEIGHTMAP_FOUR_FILE_REVIEW_FINDINGS.md"

EXPECTED_LAWS = {
    "WORLD_SURFACE": "non_air",
    "MOTION_BLOCKING": "blocks_motion or fluid_non_empty",
    "MOTION_BLOCKING_NO_LEAVES":
        "(blocks_motion or fluid_non_empty) and not leaves",
}
EXPECTED_MASKS = [0, 1, 6, 7, 6, 7, 6, 7, 0, 1, 2, 3, 2, 3, 2, 3]
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class FourFileHeightmapFindingsTests(unittest.TestCase):
    def test_exact_source_and_original_runtime_commitments(self) -> None:
        document = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], 1)
        self.assertEqual(document["kind"], "r2c-26_2-four-file-heightmap-source-inspection-v1")
        self.assertEqual(document["source_archive_sha256"], official.SOURCE_ARCHIVE_SHA256)
        self.assertEqual(document["source_file_sha256"], official.SOURCE_FILE_SHA256)
        self.assertEqual(document["state_count"], official.EXPECTED_STATE_COUNT)
        self.assertEqual(
            document["frozen_runtime_candidate_sha256"], candidate.EXPECTED_DENSE_SHA256
        )
        self.assertEqual(document["target"], candidate.EXPECTED_TARGET)
        for digest in document["source_file_sha256"].values():
            self.assertRegex(digest, SHA256)

    def test_predicates_and_full_four_flag_space(self) -> None:
        record = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(
            {name: record["formula_semantics"][name] for name in EXPECTED_LAWS},
            EXPECTED_LAWS,
        )
        self.assertEqual(
            record["truth_table_mask_bits"],
            {"WORLD_SURFACE": 0, "MOTION_BLOCKING": 1,
             "MOTION_BLOCKING_NO_LEAVES": 2},
        )
        self.assertEqual(record["four_flag_truth_table_kinds_mask"], EXPECTED_MASKS)
        for flags, observed in enumerate(EXPECTED_MASKS):
            non_air = bool(flags & 1)
            motion = bool(flags & 2)
            fluid = bool(flags & 4)
            leaves = bool(flags & 8)
            self.assertEqual(
                observed,
                int(non_air) | (int(motion or fluid) << 1)
                | (int((motion or fluid) and not leaves) << 2),
                flags,
            )
        self.assertEqual(EXPECTED_MASKS[0b0101], 7)
        self.assertEqual(EXPECTED_MASKS[0b1111], 3)

    def test_line_anchors_and_unresolved_delegates(self) -> None:
        record = json.loads(REPORT.read_text(encoding="utf-8"))
        observations = record["observations"]
        self.assertEqual(len(observations), 8)
        self.assertEqual(len({o["id"] for o in observations}), len(observations))
        for observation in observations:
            self.assertIn(observation["file"], official.SOURCE_FILE_SHA256)
            self.assertEqual(len(observation["lines"]), 2)
            start, end = observation["lines"]
            self.assertTrue(0 < start <= end < 2000)
            self.assertTrue(observation["finding"])
        self.assertGreaterEqual(len(record["source_delegate_closure"]), 8)
        self.assertEqual(
            len({d["target"] for d in record["source_delegate_closure"]}),
            len(record["source_delegate_closure"]),
        )

    def test_no_source_text_or_unauthorized_promotion(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        for key in (
            "all_reached_delegates_reviewed", "independent_atlas_gate_passed",
            "source_var_sem_admitted", "client_biome_ids_admitted",
            "production_admitted",
        ):
            self.assertIs(report[key], False)
        self.assertTrue(report["first_pass_source_inspected"])
        self.assertFalse(report["contains_official_source_text"])
        self.assertIn("NOT_ADMISSION", report["commit_policy"])
        raw = REPORT.read_text(encoding="utf-8")
        self.assertNotIn('"source_text"', raw)
        self.assertNotIn('"source_excerpt"', raw)
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("not independently reviewed", doc)
        self.assertIn("NO_LEAVES", doc)
        self.assertIn("Production", doc)
        self.assertIn(official.SOURCE_ARCHIVE_SHA256, doc)


if __name__ == "__main__":
    unittest.main()
