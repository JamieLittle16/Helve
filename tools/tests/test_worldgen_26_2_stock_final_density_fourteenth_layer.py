"""Fourteenth original 26.2 MIN-right Holder source-owner transport tests.

Synthetic target/holder frames validate protocol only, not genuine original
JVM runtime evidence. No source-law, NoiseChunk, or production admission.
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
import worldgen_26_2_stock_final_density_fourteenth_layer as owner  # noqa: E402


class FourteenthHolderTargetSourceTests(unittest.TestCase):
    def frames(self, *, different_target: bool = False) -> str:
        old = owner.prior.load()
        shapes = (
            owner.CLASS + "HolderHolder",
            "net.minecraft.core.Holder$Direct",
            owner.CLASS + "YClampedGradient",
        )
        frames = ["untrusted original JVM stdout logging ignored"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            frames.append("|".join((owner.HEAD, str(group), seed, *shapes)))
            for n in range(32):
                i = group * 32 + n
                previous_right = old[i][1]
                new_target = (
                    "3ff0000000000000" if different_target
                    else previous_right
                )
                frames.append("|".join(
                    (owner.VALUE, str(i), new_target, previous_right)
                ))
            frames.append("|".join((owner.END, str(group), "32")))
        return "\n".join(frames) + "\n"

    def methods(self) -> dict:
        r = owner.ROOT
        methods = {}
        for key in ("ap2_compute", "holder_holder_compute"):
            a, b, c, d = r.frozen_final.METHODS[key]
            methods[key] = {
                "owner": a, "signature": b,
                "body_sha256": c, "normalized_sha256": d,
                "reviewed": False,
            }
        methods["mapped_delegate_compute"] = {
            "owner": r.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": r.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return methods

    def report(self, *, different_target: bool = False) -> dict:
        shapes, vectors = owner.parse_output(
            self.frames(different_target=different_target)
        )
        return {
            "schema": 1,
            "kind": owner.KIND,
            "minecraft": "26.2",
            "protocol": 776,
            "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": owner.prior.SHA256,
            "prior_thirteenth_report_sha256": owner.prior.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_fourteenth_minright_holder_direct_target_observed": True,
            "source_text_included": False,
            "shapes": shapes,
            "vectors": vectors,
            "holder_forward_candidate_telemetry":
                owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_independent_128_old_thirteenth_holder_anchors(self):
        shapes, vectors = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(
            vectors[0]["old_thirteenth_right_holder_bits"][2:],
            owner.prior.load()[0][1]
        )
        self.assertEqual(
            shapes[0]["holder_container_class"], "net.minecraft.core.Holder$Direct"
        )
        telemetry = owner.candidate_telemetry(shapes, vectors)
        self.assertEqual(telemetry["direct_target_forward_candidate_mismatches"], 0)
        self.assertIs(telemetry["source_law_admitted"], False)
        owner.validate(self.report())

    def test_numeric_target_mismatch_preserves_genuine_JVM_frames(self):
        report = self.report(different_target=True)
        telemetry = report["holder_forward_candidate_telemetry"]
        self.assertGreater(telemetry["direct_target_forward_candidate_mismatches"], 0)
        self.assertEqual(telemetry["direct_target_forward_first_mismatch_index"], 0)
        self.assertFalse(telemetry["source_law_admitted"])
        owner.validate(report)

    def test_reject_malformed_shapes_frames_and_old_thirteenth_anchor(self):
        original = self.frames().splitlines()
        def alter_parent(lines: list[str]) -> None:
            row = lines[2].split("|")
            row[-1] = "7ff0000000000000"
            lines[2] = "|".join(row)
        variants = [
            lambda x: x.pop(2),
            lambda x: x.append(x[-1]),
            lambda x: x.__setitem__(1, x[1].replace("HolderHolder", "FakeHolder")),
            lambda x: x.__setitem__(1, x[1].replace("Holder$Direct", "Holder$Reference")),
            lambda x: x.__setitem__(1, x[1].replace(owner.CLASS + "YClampedGradient", "bogus")),
            alter_parent,
        ]
        for i, edit in enumerate(variants):
            lines = original.copy()
            edit(lines)
            with self.subTest(i=i), self.assertRaises(owner.FourteenthLayerError):
                owner.parse_output("\n".join(lines))

    def test_cross_seed_target_class_drift_and_nonfinite_target_fail_closed(self):
        # A class is genuine only when all four separately instantiated
        # original RandomState/holder records agree in this bounded corpus.
        initial = self.frames().splitlines()
        changed = initial.copy()
        header = next(
            i for i, line in enumerate(changed)
            if line.startswith(owner.HEAD + "|1|")
        )
        changed[header] = changed[header].replace(
            owner.CLASS + "YClampedGradient",
            owner.CLASS + "Constant",
        )
        with self.assertRaises(owner.FourteenthLayerError):
            owner.parse_output("\n".join(changed))
        changed = initial.copy()
        first = changed[2].split("|")
        first[2] = "7ff0000000000000"
        changed[2] = "|".join(first)
        with self.assertRaises(owner.FourteenthLayerError):
            owner.parse_output("\n".join(changed))
        changed = initial.copy()
        first = changed[2].split("|")
        first[2] = "8000000000000000"
        changed[2] = "|".join(first)
        # Signed zero is an allowed *finite original sample word* here:
        # do not silently turn sampled delegate forwarding into a universal
        # signed-zero law or reject a genuine observation without source.
        shapes, rows = owner.parse_output("\n".join(changed))
        self.assertEqual(rows[0]["holder_target_bits"], "0x8000000000000000")
        self.assertGreater(
            owner.candidate_telemetry(
                shapes, rows
            )["direct_target_forward_candidate_mismatches"], 0
        )

    def test_source_provenance_and_every_admission_gate_must_remain_false(self):
        owner.validate(self.report())
        for key in (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_thirteenth_report_sha256",
            "source_text_included", "new_fourteenth_minright_holder_direct_target_observed",
        ):
            v = self.report()
            v[key] = not v[key] if type(v[key]) is bool else "forged"
            with self.subTest(key=key), self.assertRaises(owner.FourteenthLayerError):
                owner.validate(v)
        for gate in owner.GATES:
            v = self.report()
            v[gate] = True
            with self.subTest(gate=gate), self.assertRaises(owner.FourteenthLayerError):
                owner.validate(v)
        v = self.report()
        v["holder_forward_candidate_telemetry"]["source_law_admitted"] = True
        with self.assertRaises(owner.FourteenthLayerError):
            owner.validate(v)

    def test_missing_private_original_source_cannot_emit_capture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dest = root / "should-not-exist.json"
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = owner.main([
                    "--source", str(root / "missing-source.zip"),
                    "--db", str(root / "missing.sqlite"),
                    "--lock", str(root / "missing.toml"),
                    "--server-jar", str(root / "missing.jar"),
                    "--output", str(dest),
                ])
            self.assertEqual(code, 2)
            self.assertFalse(dest.exists())
            self.assertIn("FOURTEENTH LAYER OPEN", errors.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK required")
    def test_fourteenth_source_free_original_bridge_compiles(self):
        f = owner.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.thirteenth.twelfth.JAVA_SOURCE,
            owner.thirteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(p) for p in sources)],
                capture_output=True, text=True, check=False, timeout=90,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
