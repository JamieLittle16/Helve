"""Source-free exact 26.2 heightmap delegate review; never claim source admission."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import official_r2c_heightmap_facts as oracle
import r2c_heightmap_delegate_exact_review as delegate

REPORT = ROOT / "vanilla/reviews/network/r2c-heightmap-eleven-delegate-first-pass.json"
DOC = ROOT / "docs/qualification/R2C_HEIGHTMAP_FOUR_FILE_REVIEW_FINDINGS.md"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SourceFreeDelegateFindingsTests(unittest.TestCase):
    def test_pinned_review_identity_and_local_excerpts_not_committed(self) -> None:
        r = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(r["kind"], "r2c-26_2-heightmap-eleven-delegate-first-pass-findings-v1")
        self.assertEqual(r["source_archive_sha256"], oracle.SOURCE_ARCHIVE_SHA256)
        self.assertRegex(r["source_rich_local_artifact_sha256"], SHA256)
        self.assertEqual(len(r["reviewed_methods"]), 11)
        self.assertFalse(r["contains_official_source_text"])
        self.assertIn("NOT_ADMISSION", r["commit_policy"])
        raw = REPORT.read_text(encoding="utf-8")
        self.assertNotIn('"excerpt"', raw)
        self.assertNotIn('"source_text"', raw)
        self.assertNotIn('"source_path"', raw)

        observed = r["reviewed_methods"]
        self.assertEqual([x["index"] for x in observed], list(range(1, 12)))
        self.assertEqual(len({x["method"] for x in observed}), 11)
        self.assertEqual(len({x["source_excerpt_sha256"] for x in observed}), 11)
        for x in observed:
            self.assertRegex(x["source_excerpt_sha256"], SHA256)
            self.assertIs(x["first_pass_inspected"], True)
            self.assertIs(x["semantics_admitted"], False)

        # Producer's original eleven exact method selections remain a prefix;
        # follow-up methods extend it, never replace or silently broaden it.
        self.assertEqual(len(delegate.ROOTS), 18)
        self.assertEqual(
            [f"{root.owner.rsplit('.', 1)[-1]}#{root.method}" for root in delegate.ROOTS[:11]],
            [item["method"].split("(")[0] for item in observed],
        )

    def test_observed_semantics_and_open_virtual_dispatch(self) -> None:
        r = json.loads(REPORT.read_text(encoding="utf-8"))
        ids = [index for item in r["observations"] for index in item["ids"]]
        self.assertEqual(sorted(ids), list(range(1, 12)))
        facts = " ".join(o["rule"] for o in r["observations"])
        for term in ("arithmetic mean", "EmptyFluid", "getXsize", "getYsize",
                     "getZsize", "SHAPE_FULL_BLOCK_CACHE", "initCache"):
            if term == "initCache":
                self.assertIn(term, " ".join(r["unreviewed"]))
            else:
                self.assertIn(term, facts)
        self.assertGreaterEqual(len(r["unreviewed"]), 6)
        for key in (
            "all_reached_delegates_reviewed", "heightmap_predicates_source_admitted",
            "independent_atlas_gate_passed", "client_biome_ids_admitted",
            "production_admitted",
        ):
            self.assertIs(r[key], False)

    def test_new_source_roots_are_exact_named_callees_with_fail_closed_optional_leads(self) -> None:
        expected_required = [
            ("net.minecraft.world.phys.AABB", "getXsize", 0),
            ("net.minecraft.world.phys.AABB", "getZsize", 0),
            ("net.minecraft.world.phys.shapes.VoxelShape", "isEmpty", 0),
            ("net.minecraft.world.phys.shapes.VoxelShape", "min", 1),
            ("net.minecraft.world.phys.shapes.VoxelShape", "max", 1),
        ]
        self.assertEqual(
            [(x.owner, x.method, x.parameters) for x in delegate.ROOTS[11:16]],
            expected_required,
        )
        self.assertTrue(all(x.required for x in delegate.ROOTS[11:16]))
        self.assertFalse(any(x.required for x in delegate.ROOTS[16:]))
        documentation = DOC.read_text(encoding="utf-8")
        self.assertIn("getSize", documentation)
        self.assertIn("NOT", documentation)
        self.assertIn("VAR/SEM", documentation)


if __name__ == "__main__":
    unittest.main()
