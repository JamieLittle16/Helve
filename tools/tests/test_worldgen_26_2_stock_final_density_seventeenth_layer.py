"""Original 16th immutable MIN parity + 17th real right Ap2 JVM frame tests.

All fixtures, node type claims and numbers are grounded in actual original
source-only observations; SYNTHETIC test records assert transport only.
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
import worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture as old  # noqa: E402
import worldgen_26_2_stock_final_density_seventeenth_layer as owner  # noqa: E402


class OriginalSeventeenthRightAp2Transport(unittest.TestCase):
    def frames(self, *, nonmatching: bool = False):
        lines = ["ignored Java logger"]
        shape = (
            owner.CLASS + "TwoArgumentSimpleFunction$Type",
            "ADD", owner.CLASS + "Noise", owner.CLASS + "Constant",
        )
        frozen = old.load()
        for seed_idx, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(seed_idx), seed, *shape)))
            for point in range(32):
                i = seed_idx * 32 + point
                old_parent = frozen[i][1]
                new = "3ff0000000000000" if nonmatching else old_parent
                lines.append("|".join(
                    (owner.VALUE, str(i), new, "0000000000000000", old_parent)
                ))
            lines.append("|".join((owner.END, str(seed_idx), "32")))
        return "\n".join(lines) + "\n"

    def methods(self):
        result = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            owned, signature, body, normalized = owner.ROOT.frozen_final.METHODS[name]
            result[name] = {
                "owner": owned, "signature": signature,
                "body_sha256": body, "normalized_sha256": normalized,
                "reviewed": False,
            }
        result["mapped_delegate_compute"] = {
            "owner": owner.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": owner.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return result

    def report(self, *, nonmatching: bool = False):
        shapes, vectors = owner.parse_output(self.frames(nonmatching=nonmatching))
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": owner.fifteenth_receipt.prior.SHA256,
            "prior_sixteenth_fixture_sha256": old.SHA256,
            "prior_fourteenth_report_sha256":
                owner.fifteenth_receipt.owner.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": owner.fifteenth_receipt.REPORT_SHA256,
            "prior_sixteenth_report_sha256": old.REPORT_SHA256,
            "prior_thirteenth_report_sha256": owner.fifteenth_receipt.prior.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_seventeenth_sixteenth_minright_ap2_children_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "ap2_arithmetic_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_actual_previous_sixteenth_is_frozen_not_refrozen(self):
        self.assertEqual(old.REPORT_BYTES, 41479)
        self.assertEqual(
            old.REPORT_SHA256,
            "648f5636c00f88c964c5b847abc57227157c2d53955cee971af05519126dcb5e",
        )
        self.assertEqual(old.SHA256,
                         "bd56e08412141819e938a0370b5375c458ff131d2cda12882826108b196b99d9")
        self.assertEqual(old.SHAPE["ap2_op"], "MIN")
        self.assertEqual(old.SHAPE["ap2_left_class"], owner.CLASS + "Ap2")
        self.assertEqual(old.SHAPE["ap2_right_class"], owner.CLASS + "Ap2")
        self.assertEqual(old.TELEMETRY["observed_left_strictly_less"], 57)
        self.assertEqual(old.TELEMETRY["observed_right_strictly_less"], 71)
        self.assertFalse(old.TELEMETRY["source_law_admitted"])
        self.assertEqual(old.load()[0],
                         ("3fe945aad175ec76", "3fda6dfd96e05940"))

    def test_two_new_ap2_children_old_sixteenth_right_and_telemetry(self):
        shape, samples = owner.parse_output(self.frames())
        self.assertEqual((len(shape), len(samples)), (4, 128))
        self.assertEqual(shape[0]["ap2_op"], "ADD")
        self.assertEqual(samples[0]["old_sixteenth_right_bits"][2:], old.load()[0][1])
        result = owner.candidate_telemetry(shape, samples)
        self.assertEqual(result["arithmetic_candidate_mismatches"], 0)
        self.assertFalse(result["source_law_admitted"])
        owner.validate(self.report())

    def test_arithmetic_mismatch_remains_uncensored_observational(self):
        report = self.report(nonmatching=True)
        self.assertGreater(
            report["ap2_arithmetic_candidate_telemetry"]["arithmetic_candidate_mismatches"], 0
        )
        owner.validate(report)
        self.assertIs(report["ap2_arithmetic_candidate_telemetry"]["source_law_admitted"], False)

    def test_reject_bad_java_frames_classes_old_parent_and_provenance(self):
        lines = self.frames().splitlines()
        changed = [
            "\n".join(lines[:-1]),
            "\n".join(lines + [lines[-1]]),
            "\n".join([lines[0], lines[1].replace("$Type", "Wrong$Type"), *lines[2:]]),
            "\n".join([lines[0], lines[1].replace("|ADD|", "|BAD|"), *lines[2:]]),
            "\n".join([lines[0], lines[1].replace("DensityFunctions$Noise", "fake.Name"), *lines[2:]]),
        ]
        row = lines[2].split("|")
        row[4] = "7ff0000000000000"
        changed.append("\n".join([*lines[:2], "|".join(row), *lines[3:]]))
        row = lines[2].split("|")
        row[4] = "8000000000000000"
        changed.append("\n".join([*lines[:2], "|".join(row), *lines[3:]]))
        for i, item in enumerate(changed):
            with self.subTest(index=i), self.assertRaises(owner.SeventeenthLayerError):
                owner.parse_output(item)
        for name in [
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_sixteenth_fixture_sha256",
            "prior_thirteenth_report_sha256", "prior_fourteenth_report_sha256",
            "prior_fifteenth_report_sha256", "prior_sixteenth_report_sha256",
            *owner.GATES,
        ]:
            report = self.report()
            report[name] = (
                not report[name] if isinstance(report[name], bool)
                else "untrusted-forgery"
            )
            with self.subTest(metadata=name), self.assertRaises(owner.SeventeenthLayerError):
                owner.validate(report)

    def test_no_private_original_source_no_report_written(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            output = p / "must-not-exist.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                status = owner.main([
                    "--source", str(p / "missing-src.zip"),
                    "--db", str(p / "missing.sqlite"),
                    "--lock", str(p / "missing.toml"),
                    "--server-jar", str(p / "missing.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(status, 2)
            self.assertFalse(output.exists())
            self.assertIn("SEVENTEENTH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "javac required")
    def test_all_seventeenth_original_source_free_jdk_bridges_compile(self):
        f = owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.sixteenth.fifteenth.JAVA_SOURCE,
            owner.sixteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(path) for path in sources)],
                text=True, capture_output=True, check=False, timeout=90,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
