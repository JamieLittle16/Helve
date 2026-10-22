"""Thirteenth source-owned selected twelfth MIN-left Ap2 transport gates.

Synthetic frames are NOT the original 26.2 stock JVM receipt.
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
import worldgen_26_2_stock_final_density_thirteenth_layer as thirteenth  # noqa: E402


class ThirteenthSelectedLeftAp2Tests(unittest.TestCase):
    def frames(self) -> str:
        old = thirteenth.prior.load()
        shape = (
            thirteenth.CLASS + "TwoArgumentSimpleFunction$Type",
            "MUL",
            thirteenth.CLASS + "Noise",
            thirteenth.CLASS + "Constant",
        )
        lines = ["untrusted JVM stdout noise ignored"]
        for group, seed in enumerate(thirteenth.FINAL.SEEDS):
            lines.append("|".join((thirteenth.HEAD, str(group), seed, *shape)))
            for point in range(32):
                index = group * 32 + point
                parent = old[index][0]
                # Synthetic identity multiplication; genuine Ap2 operation
                # and both child classes are still entirely UNKNOWN.
                lines.append("|".join(
                    (thirteenth.VALUE, str(index), parent, "3ff0000000000000", parent)
                ))
            lines.append("|".join((thirteenth.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self) -> dict:
        root = thirteenth.ROOT
        methods = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            owner, sig, sha, normalized = root.frozen_final.METHODS[name]
            methods[name] = {
                "owner": owner, "signature": sig,
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

    def report(self) -> dict:
        shapes, vectors = thirteenth.parse_output(self.frames())
        return {
            "schema": 1,
            "kind": thirteenth.KIND,
            "minecraft": "26.2",
            "protocol": 776,
            "data_version": 4903,
            "source_archive_sha256": thirteenth.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": thirteenth.FINAL.frozen.SERVER_SHA256,
            "prior_twelfth_fixture_sha256": thirteenth.prior.SHA256,
            "prior_twelfth_report_sha256": thirteenth.prior.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(thirteenth.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "new_thirteenth_selected_left_ap2_children_observed": True,
            "source_text_included": False,
            "shapes": shapes,
            "vectors": vectors,
            "arithmetic_candidate_telemetry":
                thirteenth.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in thirteenth.GATES},
        }

    def test_independent_128_twelfth_left_anchors_and_unadmitted_telemetry(self):
        shapes, vectors = thirteenth.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(
            vectors[0]["old_twelfth_left_bits"][2:],
            thirteenth.prior.load()[0][0],
        )
        self.assertEqual(shapes[0]["ap2_op"], "MUL")
        telemetry = thirteenth.candidate_telemetry(shapes, vectors)
        self.assertEqual(telemetry["direct_arithmetic_candidate_mismatches"], 0)
        self.assertFalse(telemetry["source_law_admitted"])
        thirteenth.validate(self.report())

    def test_original_selected_root_path_is_55_left_and_2_right(self):
        data = Path(__file__).resolve().parents[2] / (
            "crates/world/helve-world-gen/tests/data/"
        )
        twelfth = thirteenth.prior.load()
        tenth = thirteenth.prior.prior.prior.load()
        eleventh = thirteenth.prior.prior.load()
        roots = [line.split("\t") for line in
                 (data / "stock_finaldensity_min_root_128_rawbits.tsv")
                 .read_text(encoding="ascii").splitlines()]
        self.assertEqual((len(tenth), len(eleventh), len(twelfth), len(roots)),
                         (128, 128, 128, 128))
        left = right = 0
        witnesses = []
        for i, (t, e, pair, root) in enumerate(
            zip(tenth, eleventh, twelfth, roots, strict=True)
        ):
            root_left = (
                thirteenth.value("0x" + root[0])
                < thirteenth.value("0x" + root[1])
            )
            tenth_out = not (
                -1_000_000.0 <= thirteenth.value("0x" + t[0]) < 1.5625
            )
            max_left = (
                thirteenth.value("0x" + e[3])
                > thirteenth.value("0x" + e[4])
            )
            if root_left and tenth_out and max_left:
                if thirteenth.value("0x" + pair[0]) < thirteenth.value("0x" + pair[1]):
                    left += 1
                else:
                    right += 1
                    witnesses.append(i)
        self.assertEqual((left, right, witnesses), (55, 2, [97, 106]))

    def test_reject_shapes_mutated_old_parent_missing_frames_and_false_gate_forgery(self):
        initial = self.frames().splitlines()
        variants = [
            lambda v: v.pop(2),
            lambda v: v.append(v[-1]),
            lambda v: v.__setitem__(
                1, v[1].replace("TwoArgumentSimpleFunction$Type", "BadType")),
            lambda v: v.__setitem__(
                1, v[1].replace("|MUL|", "|DIV|")),
            lambda v: v.__setitem__(
                1, v[1].replace(thirteenth.CLASS + "Noise", "invalid.class")),
            lambda v: v.__setitem__(
                1, v[1].replace(thirteenth.CLASS + "Constant", "invalid.class")),
        ]
        def change_old_parent(lines: list[str]) -> None:
            cells = lines[2].split("|")
            cells[-1] = "7ff0000000000000"
            lines[2] = "|".join(cells)
        variants.append(change_old_parent)
        for i, fn in enumerate(variants):
            lines = initial.copy()
            fn(lines)
            with self.subTest(i=i), self.assertRaises(thirteenth.ThirteenthLayerError):
                thirteenth.parse_output("\n".join(lines))
        for key in (
            "source_archive_sha256", "official_server_sha256",
            "prior_twelfth_fixture_sha256", "prior_twelfth_report_sha256",
            "source_text_included",
        ):
            report = self.report()
            report[key] = True
            with self.subTest(key=key), self.assertRaises(thirteenth.ThirteenthLayerError):
                thirteenth.validate(report)
        for gate in thirteenth.GATES:
            report = self.report()
            report[gate] = True
            with self.subTest(gate=gate), self.assertRaises(thirteenth.ThirteenthLayerError):
                thirteenth.validate(report)
        report = self.report()
        report["arithmetic_candidate_telemetry"]["source_law_admitted"] = True
        with self.assertRaises(thirteenth.ThirteenthLayerError):
            thirteenth.validate(report)

    def test_candidate_mismatch_is_observed_not_rewritten(self):
        report = self.report()
        for shape in report["shapes"]:
            shape["ap2_op"] = "ADD"
        report["arithmetic_candidate_telemetry"] = thirteenth.candidate_telemetry(
            report["shapes"], report["vectors"]
        )
        self.assertGreater(
            report["arithmetic_candidate_telemetry"][
                "direct_arithmetic_candidate_mismatches"], 0)
        thirteenth.validate(report)

    def test_missing_private_original_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "must-not-exist.json"
            log = io.StringIO()
            with contextlib.redirect_stderr(log):
                rc = thirteenth.main([
                    "--source", str(Path(td) / "missing.zip"),
                    "--db", str(Path(td) / "missing.sqlite"),
                    "--lock", str(Path(td) / "missing.toml"),
                    "--server-jar", str(Path(td) / "missing.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(rc, 2)
            self.assertFalse(output.exists())
            self.assertIn("THIRTEENTH LAYER OPEN", log.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK javac required")
    def test_source_free_thirteenth_bridge_compiles(self):
        f = thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            thirteenth.twelfth.eleventh.JAVA_SOURCE,
            thirteenth.twelfth.JAVA_SOURCE,
            thirteenth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(p) for p in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
