"""Real 26.2 source-owned NoiseChunk loop ancestry, fail-closed and private."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_noisechunk_structural_fixture as fixture  # noqa: E402
import worldgen_26_2_stock_noisechunk_adjacent_fixture as adjacent  # noqa: E402


class GenuineStructuralReceiptTests(unittest.TestCase):
    @staticmethod
    def report():
        summary=fixture.load_summary()
        methods=[]
        expected=adjacent.source_methods()
        for label,shape in summary["method_structures"].items():
            stamp=expected[label]
            controls=[
                {
                    "id":idx,"kind":kind,"relative_line":line,
                    "enclosing_controls":ancestors,"loop_direction_hint":direction,
                    "header":{"operators":operators,"normalized_sha256":"0"*64},
                }
                for idx,(kind,line,ancestors,direction,operators)
                in enumerate(shape["controls"])
            ]
            calls=[
                {
                    "name":name,"relative_line":line,
                    "enclosing_controls":ancestors,
                    "argument_shape":{"normalized_sha256":"0"*64},
                }
                for name,line,ancestors in shape["calls"]
            ]
            methods.append({
                "label":label,**{k:stamp[k] for k in (
                    "owner","signature","body_sha256","normalized_sha256"
                )},
                "source_method_reviewed":False,
                "structure":{
                    "control_blocks":controls,"selected_calls":calls,
                    "lexical_control_only":True,
                    "argument_expressions_source_text_included":False,
                    "canonical_control_flow_source_reviewed":False,
                    "unbraced_control_count":0,
                },
            })
        return {
            "schema":1,
            "kind":"official_26_2_stock_noisechunk_private_structural_nesting_review",
            "minecraft":"26.2","protocol":776,"data_version":4903,
            "source_archive_sha256":summary["source_archive_sha256"],
            "analysis_kind":"lexical_brace_and_call_nesting_not_semantic_control_flow",
            "methods":methods,
            **{gate:False for gate in fixture.GATES},
        }

    def test_source_free_11_method_receipt_and_exact_control_nesting(self):
        summary=fixture.load_summary()
        self.assertEqual(list(summary["method_structures"]),list(fixture.METHOD_LABELS))
        self.assertEqual(len(summary["method_structures"]["generator_do_fill"]["controls"]),10)
        calls=summary["method_structures"]["generator_do_fill"]["calls"]
        self.assertEqual([c[0] for c in calls],[
            "initializeForFirstCellX","advanceCellX","selectCellYZ",
            "updateForY","updateForX","updateForZ","swapSlices",
            "stopInterpolation"
        ])
        self.assertEqual(calls[-2][2],[0])
        self.assertEqual(calls[-1][2],[])
        self.assertEqual(calls[5][2],[0,1,2,3,5,6])
        self.assertEqual(summary["method_structures"]["generator_fill"]["calls"],
                         [["doFill",17,[1]]])
        for flag in (
            "source_method_reviewed","canonical_control_flow_source_reviewed",
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "independent_var_sem_admitted","production_worldgen_enabled",
        ):
            self.assertIs(summary[flag],False)

    def test_compact_source_free_receipt_rejects_mutations(self):
        raw=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(raw),fixture.FIXTURE_BYTES)
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"altered.json"
            for data in (raw[:-1],raw+b" ",b"0"+raw[1:]):
                file.write_bytes(data)
                with self.subTest(bytes=len(data)),self.assertRaises(
                    fixture.FrozenStructuralReviewError
                ):
                    fixture.load_summary(file)

    def test_synthetic_matching_original_shape_and_mutations(self):
        report=self.report()
        self.assertEqual(fixture.summarize_original(report),fixture.load_summary())
        bad_cases=(
            lambda o:o["methods"][0]["structure"]["selected_calls"][5].__setitem__(
                "enclosing_controls",[0,1]),
            lambda o:o["methods"][0].__setitem__("body_sha256","0"*64),
            lambda o:o["methods"][0]["structure"].__setitem__("unbraced_control_count",1),
            lambda o:o["methods"][0]["structure"].__setitem__(
                "canonical_control_flow_source_reviewed",True),
            lambda o:o.__setitem__("production_worldgen_enabled",True),
            lambda o:o["methods"].reverse(),
            lambda o:o["methods"][1]["structure"]["control_blocks"][0]["header"].__setitem__(
                "normalized_sha256","not sha"),
        )
        for i,mutate in enumerate(bad_cases):
            altered=copy.deepcopy(report)
            mutate(altered)
            with self.subTest(case=i):
                try:
                    derived=fixture.summarize_original(altered)
                except fixture.FrozenStructuralReviewError:
                    continue
                self.assertNotEqual(derived,fixture.load_summary())

    def test_cannot_forge_private_original_from_source_free_reconstruction(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"reconstruction.json"
            path.write_text(json.dumps(self.report()))
            with self.assertRaisesRegex(fixture.FrozenStructuralReviewError,"bytes/SHA"):
                fixture.verify_original(path)

    def test_offline_cli_does_not_upgrade_gates(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(fixture.main([]),0)
        status=json.loads(out.getvalue())
        self.assertEqual(status["do_fill_nested_for_loops"],6)
        self.assertEqual(status["source_methods"],11)
        self.assertFalse(status["stock_noisechunk_canonical_traversal_qualified"])
        self.assertFalse(status["production_worldgen_enabled"])


if __name__=="__main__":
    unittest.main()
