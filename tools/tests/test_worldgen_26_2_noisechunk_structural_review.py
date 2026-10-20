"""Bounded source-free 26.2 lifecycle structural review; no source disclosure."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_noisechunk_structural_review as review  # noqa: E402


SYNTHETIC="""package test;
public class Synthetic {
  void doFill() {
    initializeForFirstCellX();
    for (int cellX = 0; cellX < 2; cellX++) {
      advanceCellX(cellX);
      for (int cellY = 17; cellY >= 15; cellY--) {
        selectCellYZ(cellY, 0);
        for (int y=7; y>=0; y--) {
          updateForY(y, 0.125);
        }
      }
      swapSlices();
    }
    stopInterpolation();
  }
}
"""


class StructuralReviewTests(unittest.TestCase):
    def profile(self,source=SYNTHETIC):
        tokens,method,braces,parens=review._find_method(
            source,"test.Synthetic","doFill()"
        )
        return review.structural_profile(tokens,method,braces,parens)

    def test_nested_actual_brace_anatomy_distinguishes_outer_and_inner_calls(self):
        profile=self.profile()
        controls=profile["control_blocks"]
        self.assertEqual([c["kind"] for c in controls],["for","for","for"])
        self.assertEqual([c["enclosing_controls"] for c in controls],
                         [[],[0],[0,1]])
        self.assertEqual([c["loop_direction_hint"] for c in controls],
                         ["increment_hint_only","decrement_hint_only","decrement_hint_only"])
        expected={
            "initializeForFirstCellX":[],
            "advanceCellX":[0],
            "selectCellYZ":[0,1],
            "updateForY":[0,1,2],
            "swapSlices":[0],
            "stopInterpolation":[],
        }
        self.assertEqual({c["name"]:c["enclosing_controls"]
                          for c in profile["selected_calls"]},expected)
        self.assertEqual(profile["unbraced_control_count"],0)
        self.assertTrue(profile["lexical_control_only"])
        self.assertFalse(profile["canonical_control_flow_source_reviewed"])

    def test_only_sanitized_operator_shapes_and_sha_are_visible(self):
        profile=self.profile()
        serialized=json.dumps(profile,sort_keys=True)
        for raw_source in ("cellX","cellY","0.125","int y","y>=0","for ("):
            self.assertNotIn(raw_source,serialized)
        for control in profile["control_blocks"]:
            self.assertEqual(len(control["header"]["normalized_sha256"]),64)
        self.assertEqual(len(profile["selected_calls"]),6)
        for call in profile["selected_calls"]:
            self.assertEqual(len(call["argument_shape"]["normalized_sha256"]),64)
            self.assertFalse(call.get("argument_source_text_included",False))

    def test_unbraced_or_unsupported_control_marks_review_unqualified(self):
        source=SYNTHETIC.replace(
            "    stopInterpolation();",
            "    if (true) stopInterpolation();"
        )
        report=self.profile(source)
        self.assertEqual(report["unbraced_control_count"],1)
        self.assertFalse(report["canonical_control_flow_source_reviewed"])

    def test_missing_method_and_wrong_owner_rejected(self):
        for owner,signature in (
            ("test.Wrong","doFill()"),
            ("test.Synthetic","doFill(int x)"),
        ):
            with self.subTest(owner=owner),self.assertRaises(
                review.StructureReviewError
            ):
                review._find_method(SYNTHETIC,owner,signature)

    def test_no_source_archive_or_db_cannot_produce_invented_review(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            stderr=io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status=review.main([
                    "--source",str(p/"private-source.zip"),
                    "--db",str(p/"missing.sqlite"),
                    "--lock",str(p/"missing.lock.toml"),
                    "--output",str(p/"report.json")
                ])
            self.assertEqual(status,2)
            self.assertFalse((p/"report.json").exists())
            self.assertIn("STRUCTURAL REVIEW OPEN",stderr.getvalue())


if __name__=="__main__":
    unittest.main()
