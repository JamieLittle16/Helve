"""Source-free synthetic twelfth MulOrAdd bridge, all old-oracle guards.

These four synthetic seed groups are NOT real JVM evidence. The genuine
original-JVM execution remains an explicit single future source-owner step.
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
import worldgen_26_2_stock_final_density_twelfth_layer as twelfth  # noqa: E402


class TwelfthSourceOwnerTests(unittest.TestCase):
    def frames(self) -> str:
        old = twelfth.prior.load()
        shape = (
            twelfth.CLASS + "MulOrAdd$Type", "MUL",
            "3ff0000000000000", twelfth.CLASS + "Noise",
        )
        lines = ["untrusted Java logger content must never become a source frame"]
        for group, seed in enumerate(twelfth.FINAL.SEEDS):
            lines.append("|".join((twelfth.HEAD, str(group), seed, *shape)))
            for j in range(32):
                index = group * 32 + j
                parent = old[index][2]
                # Identity-MUL synthetic control; not a claim about real shape.
                lines.append("|".join(
                    (twelfth.VALUE, str(index), parent, parent)
                ))
            lines.append("|".join((twelfth.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self) -> dict:
        methods = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            owner, signature, body, normalized = twelfth.ROOT.frozen_final.METHODS[name]
            methods[name] = {
                "owner": owner, "signature": signature,
                "body_sha256": body, "normalized_sha256": normalized,
                "reviewed": False,
            }
        methods["mapped_delegate_compute"] = {
            "owner": twelfth.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": twelfth.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return methods

    def report(self) -> dict:
        shapes, vectors = twelfth.parse_output(self.frames())
        return {
            "schema": 1, "kind": twelfth.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": twelfth.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": twelfth.FINAL.frozen.SERVER_SHA256,
            "prior_eleventh_fixture_sha256": twelfth.prior.SHA256,
            "prior_eleventh_report_sha256": twelfth.prior.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(twelfth.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_twelfth_inright_direct_child_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "arithmetic_candidate_telemetry":
                twelfth.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in twelfth.GATES},
        }

    def test_128_fixed_original_parent_boundaries_in_synthetic_transport(self):
        shapes, vectors = twelfth.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(vectors[0]["old_in_right_bits"][2:],
                         twelfth.prior.load()[0][2])
        self.assertEqual(shapes[0]["mul_op"], "MUL")
        self.assertEqual(shapes[0]["mul_argument_bits"], "0x3ff0000000000000")
        self.assertEqual(twelfth.candidate_telemetry(
            shapes, vectors
        )["direct_arithmetic_candidate_mismatches"], 0)
        twelfth.validate(self.report())

    def test_nontrivial_source_shape_and_old_parent_mutations_fail_closed(self):
        original = self.frames().splitlines()
        changes = [
            lambda r: r.pop(2),
            lambda r: r.append(r[-1]),
            lambda r: r.__setitem__(1, r[1].replace(
                "MulOrAdd$Type", "FakeType", 1)),
            lambda r: r.__setitem__(1, r[1].replace(
                "|MUL|", "|MIN|", 1)),
            lambda r: r.__setitem__(1, r[1].replace(
                "3ff0000000000000", "7ff0000000000000", 1)),
            lambda r: r.__setitem__(1, r[1].replace(
                "|Noise", "|invalid.class", 1)),
        ]
        def change_old_parent(rows: list[str]) -> None:
            fields = rows[2].split("|")
            fields[-1] = "0000000000000000"
            rows[2] = "|".join(fields)
        changes.append(change_old_parent)
        for index, mutation in enumerate(changes):
            lines = original.copy()
            mutation(lines)
            with self.subTest(case=index), self.assertRaises(twelfth.TwelfthLayerError):
                twelfth.parse_output("\n".join(lines))
        report = self.report()
        report["shapes"][1]["mul_op"] = "ADD"
        with self.assertRaises(twelfth.TwelfthLayerError):
            twelfth.validate(report)

    def test_source_receipt_and_all_gates_must_remain_false(self):
        for field in (
            "source_text_included", "prior_eleventh_fixture_sha256",
            "prior_eleventh_report_sha256", "official_server_sha256",
            "source_archive_sha256", "sample_context",
            "new_twelfth_inright_direct_child_observed",
        ):
            report = self.report()
            report[field] = False if field == "new_twelfth_inright_direct_child_observed" else True
            with self.subTest(field=field), self.assertRaises(twelfth.TwelfthLayerError):
                twelfth.validate(report)
        for gate in twelfth.GATES:
            report = self.report()
            report[gate] = True
            with self.subTest(gate=gate), self.assertRaises(twelfth.TwelfthLayerError):
                twelfth.validate(report)
        report = self.report()
        report["arithmetic_candidate_telemetry"]["source_law_admitted"] = True
        with self.assertRaises(twelfth.TwelfthLayerError):
            twelfth.validate(report)
        # Mismatching a real arithmetic candidate must be observable, but it
        # cannot censor authentic source values or auto-admit an all-input law.
        report = self.report()
        report["shapes"][0]["mul_argument_bits"] = "0x4000000000000000"
        report["shapes"][1]["mul_argument_bits"] = "0x4000000000000000"
        report["shapes"][2]["mul_argument_bits"] = "0x4000000000000000"
        report["shapes"][3]["mul_argument_bits"] = "0x4000000000000000"
        report["arithmetic_candidate_telemetry"] = twelfth.candidate_telemetry(
            report["shapes"], report["vectors"]
        )
        self.assertGreater(
            report["arithmetic_candidate_telemetry"][
                "direct_arithmetic_candidate_mismatches"], 0
        )
        twelfth.validate(report)

    def test_private_original_source_absence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "must-not-exist.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = twelfth.main([
                    "--source", str(Path(td) / "missing.zip"),
                    "--db", str(Path(td) / "missing.sqlite"),
                    "--lock", str(Path(td) / "missing.toml"),
                    "--server-jar", str(Path(td) / "missing.jar"),
                    "--output", str(dest),
                ])
            self.assertEqual(rc, 2)
            self.assertFalse(dest.exists())
            self.assertIn("TWELFTH LAYER OPEN", stderr.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK javac required")
    def test_source_free_java_bridge_compiles_without_original_java_zip(self):
        f = twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            twelfth.eleventh.tenth.JAVA_SOURCE,
            twelfth.eleventh.JAVA_SOURCE,
            twelfth.JAVA_SOURCE,
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
