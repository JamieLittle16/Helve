"""Actual twentieth source-owned RIGHT MulOrAdd child transport stays unadmitted."""
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
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as previous  # noqa: E402
import worldgen_26_2_stock_final_density_twentieth_layer as owner  # noqa: E402


class TwentiethOriginalMulOrAddSourceTransport(unittest.TestCase):
    def frames(self, *, altered_inner: bool = False) -> str:
        old = previous.load()
        shape = (
            owner.CLASS + "MulOrAdd$Type", "ADD",
            "0000000000000000", owner.CLASS + "Noise",
        )
        lines = ["unrelated original boot log"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(group), seed, *shape)))
            for j in range(32):
                i = group * 32 + j
                parent = old[i][1]
                inner = "3ff0000000000000" if altered_inner else parent
                lines.append("|".join((owner.VALUE, str(i), inner, parent)))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self):
        items = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            cls, sig, body, normalized = owner.ROOT.frozen_final.METHODS[name]
            items[name] = {
                "owner": cls, "signature": sig, "body_sha256": body,
                "normalized_sha256": normalized, "reviewed": False,
            }
        items["mapped_delegate_compute"] = {
            "owner": owner.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": owner.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64, "reviewed": False,
        }
        return items

    def report(self, *, altered_inner: bool = False):
        shapes, vectors = owner.parse_output(self.frames(altered_inner=altered_inner))
        fixture = owner.nineteenth.seventeenth_fixture
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": fixture.prior.prior.SHA256,
            "prior_sixteenth_fixture_sha256": fixture.prior.SHA256,
            "prior_seventeenth_fixture_sha256": fixture.SHA256,
            "prior_eighteenth_override_fixture_sha256": previous.prior.SHA256,
            "prior_nineteenth_fixture_sha256": previous.SHA256,
            "prior_thirteenth_report_sha256": fixture.prior.prior.REPORT_SHA256,
            "prior_fourteenth_report_sha256": fixture.prior.receipt.owner.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": fixture.prior.receipt.REPORT_SHA256,
            "prior_sixteenth_report_sha256": fixture.prior.REPORT_SHA256,
            "prior_seventeenth_report_sha256": fixture.REPORT_SHA256,
            "prior_eighteenth_report_sha256": previous.prior.REPORT_SHA256,
            "prior_nineteenth_report_sha256": previous.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_twentieth_actual_muloradd_child_observed": True,
            "source_text_included": False,
            "shapes": shapes,
            "vectors": vectors,
            "muloradd_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_source_owned_nineteenth_real_right_anchor(self):
        old = previous.load()
        self.assertEqual(len(old), 128)
        self.assertEqual(previous.REPORT_BYTES, 43278)
        self.assertEqual(previous.REPORT_SHA256,
                         "a79b4d191a42f3f264d5e44757aa75c56cdf5077258d36c967207b058695e1f1")
        self.assertEqual(previous.SHA256,
                         "77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4")

    def test_one_new_one_prior_real_right_original_4x32(self):
        shapes, rows = owner.parse_output(self.frames())
        self.assertEqual(len(shapes), 4)
        self.assertEqual(len(rows), 128)
        self.assertEqual(shapes[0]["muloradd_op"], "ADD")
        self.assertEqual(rows[0]["old_nineteenth_right_bits"], "0xbfb579b4d551ef7b")
        candidate = owner.candidate_telemetry(shapes, rows)
        self.assertEqual(candidate["muloradd_candidate_mismatches"], 0)
        self.assertFalse(candidate["source_law_admitted"])
        owner.validate(self.report())

    def test_actual_arithmetic_disagreement_is_not_silenced(self):
        report = self.report(altered_inner=True)
        self.assertGreater(report["muloradd_candidate_telemetry"]["muloradd_candidate_mismatches"], 0)
        owner.validate(report)

    def test_source_frame_ancestry_and_every_gate_fail_closed(self):
        base = self.frames().splitlines()
        invalid = [
            base[:-1],
            base + [base[-1]],
            [base[0], base[1].replace("MulOrAdd$Type", "Invalid$Type"), *base[2:]],
            [base[0], base[1].replace("|ADD|", "|BAD|"), *base[2:]],
            [base[0], base[1].replace("|0000000000000000|", "|7ff0000000000000|"), *base[2:]],
            [base[0], base[1].replace("DensityFunctions$Noise", "false.Class"), *base[2:]],
        ]
        wrong_parent = base[2].split("|")
        wrong_parent[3] = "0000000000000000"
        invalid.append([*base[:2], "|".join(wrong_parent), *base[3:]])
        for i, item in enumerate(invalid):
            with self.subTest(frame=i), self.assertRaises(owner.TwentiethLayerError):
                owner.parse_output("\n".join(item))
        for key in (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_sixteenth_fixture_sha256",
            "prior_seventeenth_fixture_sha256",
            "prior_eighteenth_override_fixture_sha256", "prior_nineteenth_fixture_sha256",
            "prior_thirteenth_report_sha256", "prior_fourteenth_report_sha256",
            "prior_fifteenth_report_sha256", "prior_sixteenth_report_sha256",
            "prior_seventeenth_report_sha256", "prior_eighteenth_report_sha256",
            "prior_nineteenth_report_sha256", *owner.GATES,
        ):
            r = self.report()
            r[key] = not r[key] if isinstance(r[key], bool) else "wrong"
            with self.subTest(pin=key), self.assertRaises(owner.TwentiethLayerError):
                owner.validate(r)

    def test_missing_stock_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            output = p / "must-not-exist.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                result = owner.main([
                    "--source", str(p / "not-source.zip"),
                    "--db", str(p / "not-atlas.sqlite"),
                    "--lock", str(p / "not-lock.toml"),
                    "--server-jar", str(p / "not-official.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(result, 2)
            self.assertFalse(output.exists())
            self.assertIn("TWENTIETH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_twentieth_full_source_bridge_compiles(self):
        f = owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.seventeenth.JAVA_SOURCE,
            owner.nineteenth.eighteenth.JAVA_SOURCE,
            owner.nineteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
