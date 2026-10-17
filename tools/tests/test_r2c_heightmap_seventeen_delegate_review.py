"""17-method pinned source-free heightmap review and new discrete frontier checks."""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import official_r2c_heightmap_facts as official
import r2c_heightmap_delegate_exact_review as extractor

REVIEW = ROOT / "vanilla/reviews/network/r2c-heightmap-seventeen-delegate-review.json"
ELEVEN = ROOT / "vanilla/reviews/network/r2c-heightmap-eleven-delegate-first-pass.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SeventeenDelegateReviewTests(unittest.TestCase):
    def test_exact_17_method_identity_and_no_upstream_duplication(self) -> None:
        report = json.loads(REVIEW.read_text(encoding="utf-8"))
        prior = json.loads(ELEVEN.read_text(encoding="utf-8"))
        self.assertEqual(report["schema"], 1)
        self.assertEqual(
            report["kind"], "r2c-26_2-17-method-heightmap-delegate-source-free-review-v1"
        )
        self.assertEqual(report["source_archive_sha256"], official.SOURCE_ARCHIVE_SHA256)
        self.assertRegex(report["source_rich_artifact_sha256"], SHA256)
        self.assertEqual(report["prior_method_count"], len(prior["reviewed_methods"]))
        self.assertEqual(report["source_excerpt_count"], 17)
        self.assertEqual(len(report["reviewed_new_methods"]), 6)
        self.assertEqual(
            [item["index"] for item in report["reviewed_new_methods"]],
            list(range(12, 18)),
        )
        self.assertEqual(len(extractor.ROOTS), 23)
        old_plus_new = extractor.ROOTS[:17]
        self.assertEqual(
            [item["source_identity"].split("#")[0] for item in report["reviewed_new_methods"]],
            [r.owner for r in old_plus_new[11:17]],
        )
        self.assertEqual(
            [item["source_identity"].split("#")[1].split("(")[0]
             for item in report["reviewed_new_methods"]],
            [r.method for r in old_plus_new[11:17]],
        )
        for item in report["reviewed_new_methods"]:
            self.assertRegex(item["body_sha256"], SHA256)
            self.assertRegex(item["source_excerpt_sha256"], SHA256)
            self.assertTrue(item["source_inspected"])
            self.assertFalse(item["source_admitted"])
        self.assertEqual(
            report["optional_method_not_found"]["owner"],
            "net.minecraft.world.level.material.FlowingFluid",
        )
        self.assertEqual(report["optional_method_not_found"]["method"], "isEmpty")
        self.assertEqual(report["optional_method_not_found"]["parameters"], 0)
        self.assertFalse(report["source_text_committed"])
        self.assertIn("NOT_SOURCE_ADMISSION", report["commit_policy"])
        for key in (
            "all_reached_delegates_reviewed", "source_semantics_admitted",
            "independent_atlas_gate_passed", "production_admitted",
        ):
            self.assertFalse(report[key], key)
        text = REVIEW.read_text(encoding="utf-8")
        for forbidden in ('"excerpt"', '"source_text"', '"source_path"'):
            self.assertNotIn(forbidden, text)

    def test_five_new_direct_callees_with_explicit_pending_only_selection(self) -> None:
        report = json.loads(REVIEW.read_text(encoding="utf-8"))
        expected = [
            ("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "isEmpty", 0),
            ("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "firstFull", 1),
            ("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "lastFull", 1),
            ("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "getSize", 1),
            ("net.minecraft.world.phys.shapes.VoxelShape", "get", 2),
        ]
        pending = extractor.PENDING_DISCRETE_ROOTS
        self.assertEqual(
            [(r.owner, r.method, r.parameters) for r in pending], expected
        )
        self.assertTrue(all(r.required for r in pending))
        self.assertEqual(tuple(extractor.ROOTS[-5:]), pending)
        self.assertEqual(len({(r.owner, r.method, r.parameters)
                              for r in extractor.ROOTS}), len(extractor.ROOTS))
        self.assertEqual(len(report["unresolved_direct_callees"]), 5)
        self.assertEqual(
            [item.split("#")[0] for item in report["unresolved_direct_callees"]],
            [r.owner for r in pending],
        )
        with patch.object(extractor, "run", return_value={
            "output": "/tmp/test-only.json",
            "review_methods": 5,
            "missing_optional_methods": 0,
            "source_admitted": False,
        }) as runner, contextlib.redirect_stdout(io.StringIO()):
            status = extractor.main(["--pending-only", "--output", "/tmp/test-only.json"])
        self.assertEqual(status, 0)
        self.assertEqual(tuple(runner.call_args.kwargs["roots"]), pending)

    def test_source_findings_distinguish_shape_dispatch_and_aabb_axis_laws(self) -> None:
        report = json.loads(REVIEW.read_text(encoding="utf-8"))
        ids = sorted(i for observation in report["findings"] for i in observation["methods"])
        self.assertEqual(ids, list(range(12, 18)))
        rules = " ".join(item["rule"] for item in report["findings"])
        for needed in (
            "maxX-minX", "maxZ-minZ", "Math.min/Math.max",
            "DiscreteVoxelShape.isEmpty", "firstFull", "lastFull",
            "POSITIVE_INFINITY", "NEGATIVE_INFINITY",
        ):
            self.assertIn(needed, rules)
        self.assertGreaterEqual(len(report["other_unresolved"]), 4)


if __name__ == "__main__":
    unittest.main()
