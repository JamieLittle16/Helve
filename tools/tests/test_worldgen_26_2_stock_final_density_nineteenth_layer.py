"""Strict source-free nineteenth Clamp-wrapped Ap2 two NEW child JVM frames."""
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
import worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt as previous  # noqa: E402
import worldgen_26_2_stock_final_density_nineteenth_layer as owner  # noqa: E402


class NineteenthOriginalAp2SourceTransport(unittest.TestCase):
    def frames(self, *, arithmetic_mismatch: bool = False) -> str:
        old = previous.load()
        shapes = (
            owner.CLASS + "TwoArgumentSimpleFunction$Type",
            "ADD", owner.CLASS + "Noise", owner.CLASS + "Constant",
        )
        lines = ["unrelated original logger output"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(group), seed, *shapes)))
            for j in range(32):
                i = group * 32 + j
                left = "3ff0000000000000" if arithmetic_mismatch else old[i]
                lines.append("|".join((owner.VALUE, str(i), left, "0000000000000000", old[i])))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self):
        entries = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            cls, sig, body, normalized = owner.ROOT.frozen_final.METHODS[name]
            entries[name] = {
                "owner": cls, "signature": sig, "body_sha256": body,
                "normalized_sha256": normalized, "reviewed": False,
            }
        entries["mapped_delegate_compute"] = {
            "owner": owner.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": owner.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return entries

    def report(self, *, arithmetic_mismatch: bool = False):
        shapes, vectors = owner.parse_output(self.frames(arithmetic_mismatch=arithmetic_mismatch))
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": owner.seventeenth_fixture.prior.prior.SHA256,
            "prior_sixteenth_fixture_sha256": owner.seventeenth_fixture.prior.SHA256,
            "prior_seventeenth_fixture_sha256": owner.seventeenth_fixture.SHA256,
            "prior_eighteenth_override_fixture_sha256": previous.SHA256,
            "prior_thirteenth_report_sha256": owner.seventeenth_fixture.prior.prior.REPORT_SHA256,
            "prior_fourteenth_report_sha256":
                owner.seventeenth_fixture.prior.receipt.owner.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": owner.seventeenth_fixture.prior.receipt.REPORT_SHA256,
            "prior_sixteenth_report_sha256": owner.seventeenth_fixture.prior.REPORT_SHA256,
            "prior_seventeenth_report_sha256": owner.seventeenth_fixture.REPORT_SHA256,
            "prior_eighteenth_report_sha256": previous.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_nineteenth_actual_clampwrapped_ap2_children_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "ap2_arithmetic_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_actual_real_eighteenth_two_new_word_parent_receipt(self):
        self.assertEqual(previous.REPORT_BYTES, 36555)
        self.assertEqual(previous.REPORT_SHA256,
                         "4e8279f53b06a6de9154f18df073b742ad091acfe6b156611bc916dbbf8781ae")
        self.assertEqual(previous.SHA256,
                         "e1b4da2ef965a0e92ad2bb56931de16dce95318f3aadabd4e78be2721a5b2811")
        self.assertEqual(previous.OVERRIDES, {18: "3ff5c1c9c20d14a4", 28: "3ff219c5d9c551b1"})
        self.assertEqual(len(previous.load()), 128)

    def test_bounded_two_new_one_frozen_old_ieee_and_real_4_seeds(self):
        shapes, rows = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(rows)), (4, 128))
        self.assertEqual(shapes[0]["ap2_op"], "ADD")
        self.assertEqual(rows[18]["old_eighteenth_clamp_inner_bits"][2:], previous.OVERRIDES[18])
        self.assertEqual(rows[28]["old_eighteenth_clamp_inner_bits"][2:], previous.OVERRIDES[28])
        candidate = owner.candidate_telemetry(shapes, rows)
        self.assertEqual(candidate["arithmetic_candidate_mismatches"], 0)
        self.assertFalse(candidate["source_law_admitted"])
        owner.validate(self.report())

    def test_original_arithmetic_mismatches_are_not_silenced(self):
        report = self.report(arithmetic_mismatch=True)
        self.assertGreater(
            report["ap2_arithmetic_candidate_telemetry"]["arithmetic_candidate_mismatches"], 0
        )
        owner.validate(report)

    def test_wrong_original_frames_ancestry_and_gates_are_rejected(self):
        base = self.frames().splitlines()
        invalid = [
            base[:-1],
            base + [base[-1]],
            [base[0], base[1].replace("TwoArgumentSimpleFunction$Type", "Wrong$Type"), *base[2:]],
            [base[0], base[1].replace("|ADD|", "|XOR|"), *base[2:]],
            [base[0], base[1].replace("DensityFunctions$Noise", "fake.Class"), *base[2:]],
        ]
        old_parent = base[2].split("|")
        old_parent[4] = "0000000000000000"
        invalid.append([*base[:2], "|".join(old_parent), *base[3:]])
        for i, item in enumerate(invalid):
            with self.subTest(index=i), self.assertRaises(owner.NineteenthLayerError):
                owner.parse_output("\n".join(item))
        for key in (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_sixteenth_fixture_sha256",
            "prior_seventeenth_fixture_sha256", "prior_eighteenth_override_fixture_sha256",
            "prior_thirteenth_report_sha256", "prior_fourteenth_report_sha256",
            "prior_fifteenth_report_sha256", "prior_sixteenth_report_sha256",
            "prior_seventeenth_report_sha256", "prior_eighteenth_report_sha256",
            *owner.GATES,
        ):
            report = self.report()
            report[key] = not report[key] if isinstance(report[key], bool) else "fake"
            with self.subTest(key=key), self.assertRaises(owner.NineteenthLayerError):
                owner.validate(report)

    def test_original_stock_source_missing_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            output = directory / "must-not-exist.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                result = owner.main([
                    "--source", str(directory / "not-owned.zip"),
                    "--db", str(directory / "not-atlas.sqlite"),
                    "--lock", str(directory / "not-a-lock.toml"),
                    "--server-jar", str(directory / "not-server.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(result, 2)
            self.assertFalse(output.exists())
            self.assertIn("NINETEENTH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_original_nineteenth_complete_source_bridge_compiles(self):
        f = owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.JAVA_SOURCE,
            owner.eighteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
