"""Eighteenth genuine original JVM Clamp bounds/inner transport; synthetic fixtures."""
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
import worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture as frozen  # noqa: E402
import worldgen_26_2_stock_final_density_eighteenth_layer as owner  # noqa: E402


class EighteenthClampSourceOwnerTransport(unittest.TestCase):
    def frames(self, *, mismatch: bool = False) -> str:
        old = frozen.load()
        shape = (
            owner.CLASS + "Clamp", owner.CLASS + "Noise",
            "c059000000000000", "4059000000000000",  # -100, +100
        )
        lines = ["original JVM unrelated logger"]
        for i, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(i), seed, *shape)))
            for j in range(32):
                k = i * 32 + j
                parent = old[k][1]
                new = "3ff0000000000000" if mismatch else parent
                lines.append("|".join((owner.VALUE, str(k), new, parent)))
            lines.append("|".join((owner.END, str(i), "32")))
        return "\n".join(lines) + "\n"

    def methods(self):
        methods = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            node, signature, body, norm = owner.ROOT.frozen_final.METHODS[name]
            methods[name] = {
                "owner": node, "signature": signature, "body_sha256": body,
                "normalized_sha256": norm, "reviewed": False,
            }
        methods["mapped_delegate_compute"] = {
            "owner": owner.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": owner.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return methods

    def report(self, *, mismatch: bool = False):
        shapes, vectors = owner.parse_output(self.frames(mismatch=mismatch))
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": owner.sixteenth_fixture.prior.SHA256,
            "prior_sixteenth_fixture_sha256": owner.sixteenth_fixture.SHA256,
            "prior_seventeenth_fixture_sha256": frozen.SHA256,
            "prior_thirteenth_report_sha256": owner.sixteenth_fixture.prior.REPORT_SHA256,
            "prior_fourteenth_report_sha256":
                owner.sixteenth_fixture.receipt.owner.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": owner.sixteenth_fixture.receipt.REPORT_SHA256,
            "prior_sixteenth_report_sha256": owner.sixteenth_fixture.REPORT_SHA256,
            "prior_seventeenth_report_sha256": frozen.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_eighteenth_actual_clamp_input_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "clamp_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_replay_exact_one_new_one_old_original_clamp(self):
        shapes, vectors = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(shapes[0]["clamp_class"], owner.CLASS + "Clamp")
        self.assertEqual(shapes[0]["clamp_input_class"], owner.CLASS + "Noise")
        self.assertEqual(vectors[0]["old_seventeenth_clamp_bits"][2:], frozen.load()[0][1])
        tel = owner.candidate_telemetry(shapes, vectors)
        self.assertEqual(tel["clamp_candidate_mismatches"], 0)
        self.assertEqual(tel["observed_within_inclusive_bounds"], 128)
        self.assertFalse(tel["source_law_admitted"])
        owner.validate(self.report())

    def test_mismatched_original_clamp_candidate_not_censored(self):
        r = self.report(mismatch=True)
        self.assertGreater(r["clamp_candidate_telemetry"]["clamp_candidate_mismatches"], 0)
        self.assertFalse(r["clamp_candidate_telemetry"]["source_law_admitted"])
        owner.validate(r)

    def test_bounds_are_real_ordered_finite_ieee_and_provenance_fail_closed(self):
        lines = self.frames().splitlines()
        bad = [
            lines[:2] + lines[3:],
            lines + [lines[-1]],
            [lines[0], lines[1].replace("DensityFunctions$Clamp", "Wrong$Type"), *lines[2:]],
            [lines[0], lines[1].replace("DensityFunctions$Noise", "fake.Type"), *lines[2:]],
            [lines[0], lines[1].replace("c059000000000000", "7ff0000000000000"), *lines[2:]],
            [lines[0], lines[1].replace("c059000000000000", "4059000000000000"), *lines[2:]],
            [lines[0], lines[1].replace("4059000000000000", "c059000000000000"), *lines[2:]],
        ]
        row = lines[2].split("|")
        row[3] = "8000000000000000"
        bad.append([*lines[:2], "|".join(row), *lines[3:]])
        for i, item in enumerate(bad):
            with self.subTest(index=i), self.assertRaises(owner.EighteenthLayerError):
                owner.parse_output("\n".join(item))
        for field in (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_sixteenth_fixture_sha256",
            "prior_seventeenth_fixture_sha256", "prior_thirteenth_report_sha256",
            "prior_fourteenth_report_sha256", "prior_fifteenth_report_sha256",
            "prior_sixteenth_report_sha256", "prior_seventeenth_report_sha256",
            *owner.GATES,
        ):
            r = self.report()
            r[field] = not r[field] if isinstance(r[field], bool) else "invalid"
            with self.subTest(field=field), self.assertRaises(owner.EighteenthLayerError):
                owner.validate(r)

    def test_local_original_source_missing_never_emits_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            target = p / "should_not_exist.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                result = owner.main([
                    "--source", str(p / "no-original-source.zip"),
                    "--db", str(p / "no-db.sqlite"),
                    "--lock", str(p / "no-lock.toml"),
                    "--server-jar", str(p / "missing.jar"),
                    "--output", str(target),
                ])
            self.assertEqual(result, 2)
            self.assertFalse(target.exists())
            self.assertIn("EIGHTEENTH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "requires source-free JDK compilation")
    def test_full_eighteenth_original_jdk_bridge_chain_compiles(self):
        f = owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            owner.seventeenth.sixteenth.JAVA_SOURCE,
            owner.seventeenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(x) for x in sources)],
                capture_output=True, text=True, check=False, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
