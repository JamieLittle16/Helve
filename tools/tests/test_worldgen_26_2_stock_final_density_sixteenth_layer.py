"""15th authentic CacheOnce->Ap2 receipt and 16th strict original JVM transport."""
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
import worldgen_26_2_stock_finaldensity_fifteenth_layer_receipt as authentic  # noqa: E402
import worldgen_26_2_stock_final_density_sixteenth_layer as owner  # noqa: E402


class GenuineFifteenthAndSixteenthJVM(unittest.TestCase):
    def frames(self, *, disagree: bool = False) -> str:
        old = owner.prior.load()
        shape = (
            owner.CLASS + "TwoArgumentSimpleFunction$Type",
            "ADD", owner.CLASS + "Noise", owner.CLASS + "Constant",
        )
        lines = ["non-frame Java logger line"]
        for i, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(i), seed, *shape)))
            for j in range(32):
                k = i * 32 + j
                parent = old[k][1]
                left = "3ff0000000000000" if disagree else parent
                lines.append("|".join((
                    owner.VALUE, str(k), left, "0000000000000000", parent
                )))
            lines.append("|".join((owner.END, str(i), "32")))
        return "\n".join(lines) + "\n"

    def methods(self):
        root = owner.ROOT
        result = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            a, b, c, d = root.frozen_final.METHODS[name]
            result[name] = {
                "owner": a, "signature": b,
                "body_sha256": c, "normalized_sha256": d,
                "reviewed": False,
            }
        result["mapped_delegate_compute"] = {
            "owner": root.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": root.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return result

    def report(self, *, disagree: bool = False):
        shapes, vectors = owner.parse_output(self.frames(disagree=disagree))
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": owner.prior.SHA256,
            "prior_thirteenth_report_sha256": owner.prior.REPORT_SHA256,
            "prior_fourteenth_report_sha256": owner.fifteenth.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": authentic.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_sixteenth_cacheonce_ap2_children_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "ap2_arithmetic_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_actual_fifteenth_receipt_pins_shape_and_no_redundant_numbers(self):
        self.assertEqual(authentic.REPORT_BYTES, 43502)
        self.assertEqual(
            authentic.REPORT_SHA256,
            "bc1df68c3245c55735df84c4c2e36bc35b4d349d4a5c9623db24ac9630cbe0f0",
        )
        self.assertEqual(authentic.SHAPE["marker_type"], "CacheOnce")
        self.assertEqual(authentic.SHAPE["marker_wrapped_class"], owner.CLASS + "Ap2")
        self.assertEqual(authentic.TELEMETRY["marker_wrapped_candidate_mismatches"], 0)
        self.assertFalse(authentic.TELEMETRY["source_law_admitted"])
        self.assertFalse(hasattr(authentic, "FIXTURE"))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake-original.json"
            path.write_text('{"worldgen": "forged"}')
            with self.assertRaisesRegex(authentic.FifteenthReceiptError, "length/SHA"):
                authentic.validate_original(path)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(authentic.main(["--capture", str(path)]), 2)
            self.assertIn("FIFTEENTH RECEIPT OPEN", errors.getvalue())

    def test_16th_two_new_children_anchor_old_thirteenth_right(self):
        shapes, rows = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(rows)), (4, 128))
        self.assertEqual(shapes[0]["ap2_op"], "ADD")
        self.assertEqual(rows[0]["old_thirteenth_right_bits"][2:], owner.prior.load()[0][1])
        telemetry = owner.candidate_telemetry(shapes, rows)
        self.assertEqual(telemetry["arithmetic_candidate_mismatches"], 0)
        self.assertIs(telemetry["source_law_admitted"], False)
        owner.validate(self.report())

    def test_genuine_mismatch_never_censored_or_admitted(self):
        r = self.report(disagree=True)
        self.assertGreater(
            r["ap2_arithmetic_candidate_telemetry"]["arithmetic_candidate_mismatches"], 0
        )
        owner.validate(r)

    def test_bad_source_frames_and_parent_failure(self):
        frame = self.frames().splitlines()
        def mutate(line: int, old: str, new: str):
            v = frame.copy()
            v[line] = v[line].replace(old, new)
            return "\n".join(v)
        changed = [
            "\n".join(frame[:-1]),
            "\n".join(frame + [frame[-1]]),
            mutate(1, "TwoArgumentSimpleFunction$Type", "Marker$Type"),
            mutate(1, "|ADD|", "|XOR|"),
            mutate(1, "DensityFunctions$Noise", "bad.Density"),
            mutate(2, "3fda6dfd96e05940", "7ff0000000000000"),
            "\n".join([
                *frame[:2],
                "|".join([
                    *frame[2].split("|")[:2],
                    "3fda6dfd96e05941",
                    *frame[2].split("|")[3:],
                ]),
                *frame[3:],
            ]),
        ]
        # Valid finite child mutation only: must not claim arithmetic source admission.
        for i, v in enumerate(changed):
            with self.subTest(case=i):
                if i == 6:
                    shapes, rows = owner.parse_output(v)
                    self.assertGreater(
                        owner.candidate_telemetry(shapes, rows)["arithmetic_candidate_mismatches"],
                        0,
                    )
                else:
                    with self.assertRaises(owner.SixteenthLayerError):
                        owner.parse_output(v)

    def test_every_source_law_gate_prior_sha_and_telemetry_fail_closed(self):
        base = self.report()
        owner.validate(base)
        fields = (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_fourteenth_report_sha256",
            "prior_fifteenth_report_sha256", "prior_thirteenth_report_sha256",
            "source_text_included", "new_sixteenth_cacheonce_ap2_children_observed",
        )
        for key in (*fields, *owner.GATES):
            r = self.report()
            r[key] = not r[key] if type(r[key]) is bool else "not-authentic"
            with self.subTest(field=key), self.assertRaises(owner.SixteenthLayerError):
                owner.validate(r)
        r = self.report()
        r["ap2_arithmetic_candidate_telemetry"]["source_law_admitted"] = True
        with self.assertRaises(owner.SixteenthLayerError):
            owner.validate(r)

    def test_missing_private_original_source_never_emits_a_capture(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            output = path / "forbidden.json"
            messages = io.StringIO()
            with contextlib.redirect_stderr(messages):
                rc = owner.main([
                    "--source", str(path / "missing.zip"),
                    "--db", str(path / "missing.sqlite"),
                    "--lock", str(path / "missing.toml"),
                    "--server-jar", str(path / "missing.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(rc, 2)
            self.assertFalse(output.exists())
            self.assertIn("SIXTEENTH LAYER OPEN", messages.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK javac required")
    def test_source_free_sixteenth_javac_complete_owner_chain(self):
        f = owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.fifteenth.fourteenth.JAVA_SOURCE,
            owner.fifteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            process = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(x) for x in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)


if __name__ == "__main__":
    unittest.main()
