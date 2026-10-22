"""Genuine 14th Marker identity receipt and 15th bounded Java transport tests.

Synthetic original-JVM records validate the tool, NOT new source-law evidence.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_fourteenth_layer_receipt as genuine  # noqa: E402
import worldgen_26_2_stock_final_density_fifteenth_layer as next_owner  # noqa: E402


class ActualFourteenthReceiptAndFifteenthTransport(unittest.TestCase):
    def frames(self, *, different_child: bool = False) -> str:
        old = next_owner.prior.load()
        shape = (
            next_owner.CLASS + "Marker$Type",
            "CacheOnce",
            next_owner.CLASS + "RangeChoice",
        )
        lines = ["irrelevant JVM stdout ignored"]
        for group, seed in enumerate(next_owner.FINAL.SEEDS):
            lines.append("|".join((next_owner.HEAD, str(group), seed, *shape)))
            for point in range(32):
                i = group * 32 + point
                anchor = old[i][1]
                new_word = "3ff0000000000000" if different_child else anchor
                lines.append("|".join((
                    next_owner.VALUE, str(i), new_word, anchor, anchor,
                )))
            lines.append("|".join((next_owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self) -> dict:
        root = next_owner.ROOT
        methods = {}
        for key in ("ap2_compute", "holder_holder_compute"):
            owner, signature, sha, normalized = root.frozen_final.METHODS[key]
            methods[key] = {
                "owner": owner, "signature": signature,
                "body_sha256": sha, "normalized_sha256": normalized,
                "reviewed": False,
            }
        methods["mapped_delegate_compute"] = {
            "owner": root.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": root.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return methods

    def report(self, *, different_child: bool = False) -> dict:
        shapes, vectors = next_owner.parse_output(
            self.frames(different_child=different_child)
        )
        return {
            "schema": 1, "kind": next_owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": next_owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": next_owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": next_owner.prior.SHA256,
            "prior_fourteenth_report_sha256": genuine.REPORT_SHA256,
            "prior_thirteenth_report_sha256": next_owner.prior.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(next_owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_fifteenth_marker_wrapped_child_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "marker_wrapped_candidate_telemetry":
                next_owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in next_owner.GATES},
        }

    def test_genuine_fourteenth_report_pinned_no_duplicate_tsv(self):
        self.assertEqual(genuine.REPORT_BYTES, 36371)
        self.assertEqual(
            genuine.REPORT_SHA256,
            "8d258327bb24a5b8f6d6a3a64ad6ab751fd5dea7706b80ca88e42ca6a2b43492"
        )
        self.assertEqual(genuine.SHAPE["target_class"], next_owner.CLASS + "Marker")
        self.assertEqual(genuine.TELEMETRY["direct_target_forward_candidate_mismatches"], 0)
        self.assertIs(genuine.TELEMETRY["source_law_admitted"], False)
        self.assertFalse(hasattr(genuine, "FIXTURE"))  # Avoid 128 duplicate old words.
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "forged-private.json"
            path.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(
                genuine.FourteenthReceiptError, "length/SHA"
            ):
                genuine.validate_original(path)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(genuine.main(["--capture", str(path)]), 2)
            self.assertIn("FOURTEENTH RECEIPT OPEN", err.getvalue())

    def test_marker_source_shape_and_twice_independent_prior_anchor(self):
        shapes, rows = next_owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(rows)), (4, 128))
        self.assertEqual(shapes[0]["marker_type"], "CacheOnce")
        self.assertEqual(shapes[0]["marker_wrapped_class"], next_owner.CLASS + "RangeChoice")
        self.assertEqual(
            rows[0]["old_marker_target_bits"][2:],
            next_owner.prior.load()[0][1],
        )
        self.assertEqual(
            rows[0]["old_thirteenth_right_holder_bits"],
            rows[0]["old_marker_target_bits"],
        )
        next_owner.validate(self.report())

    def test_marker_numeric_mismatch_is_not_censored_or_admitted(self):
        report = self.report(different_child=True)
        self.assertGreater(
            report["marker_wrapped_candidate_telemetry"][
                "marker_wrapped_candidate_mismatches"], 0
        )
        self.assertIs(
            report["marker_wrapped_candidate_telemetry"]["source_law_admitted"],
            False
        )
        next_owner.validate(report)

    def test_reject_missing_or_false_ancestry_and_class_or_record_mutation(self):
        initial = self.frames().splitlines()
        def old_marker_changed(lines: list[str]) -> None:
            row = lines[2].split("|")
            row[3] = "7ff0000000000000"
            lines[2] = "|".join(row)
        def old_holder_changed(lines: list[str]) -> None:
            row = lines[2].split("|")
            row[4] = "8000000000000000"
            lines[2] = "|".join(row)
        edits = [
            lambda a: a.pop(2),
            lambda a: a.append(a[-1]),
            lambda a: a.__setitem__(1, a[1].replace("Marker$Type", "Incorrect$Type")),
            lambda a: a.__setitem__(1, a[1].replace("|CacheOnce|", "|not.valid|")),
            lambda a: a.__setitem__(1, a[1].replace("RangeChoice", "bad.Density")),
            old_marker_changed,
            old_holder_changed,
        ]
        for i, fn in enumerate(edits):
            changed = initial.copy()
            fn(changed)
            with self.subTest(i=i), self.assertRaises(next_owner.FifteenthLayerError):
                next_owner.parse_output("\n".join(changed))
        v = self.report()
        v["prior_fourteenth_report_sha256"] = "0" * 64
        with self.assertRaises(next_owner.FifteenthLayerError):
            next_owner.validate(v)
        for gate in next_owner.GATES:
            v = self.report()
            v[gate] = True
            with self.subTest(gate=gate), self.assertRaises(next_owner.FifteenthLayerError):
                next_owner.validate(v)

    def test_missing_private_source_fails_without_writing_a_capture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dest = root / "unwritten.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = next_owner.main([
                    "--source", str(root / "missing.zip"),
                    "--db", str(root / "missing.sqlite"),
                    "--lock", str(root / "missing.toml"),
                    "--server-jar", str(root / "missing.jar"),
                    "--output", str(dest),
                ])
            self.assertEqual(code, 2)
            self.assertFalse(dest.exists())
            self.assertIn("FIFTEENTH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK javac required")
    def test_source_free_fifteenth_full_original_bridge_compiles(self):
        f = next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE, f.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            next_owner.fourteenth.thirteenth.JAVA_SOURCE,
            next_owner.fourteenth.JAVA_SOURCE,
            next_owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
