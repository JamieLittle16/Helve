"""Twelfth actual out-left Ap2 source-owner synthetic guard regression.

Synthetic frames and JDK compilation test only transport and fail-closed
boundaries; neither is new original-JVM runtime evidence.
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


class TwelfthOutLeftAp2SourceOwnerTests(unittest.TestCase):
    def frames(self) -> str:
        old = twelfth.prior.load()
        shape = (
            twelfth.CLASS + "TwoArgumentSimpleFunction$Type", "MUL",
            twelfth.CLASS + "Noise", twelfth.CLASS + "Constant",
        )
        lines = ["untrusted logging never authorizes a source-owner observation"]
        for group, seed in enumerate(twelfth.FINAL.SEEDS):
            lines.append("|".join((twelfth.HEAD, str(group), seed, *shape)))
            for j in range(32):
                index = group * 32 + j
                parent = old[index][3]
                # Synthetic identity MUL: first=parent, second=+1.0.
                # The real out-left Ap2 operation and children are NOT known.
                lines.append("|".join(
                    (twelfth.VALUE, str(index),
                     parent, "3ff0000000000000", parent)
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
            "new_twelfth_outleft_ap2_children_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "arithmetic_candidate_telemetry":
                twelfth.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in twelfth.GATES},
        }

    def test_128_independently_frozen_old_parent_anchors(self):
        shapes, vectors = twelfth.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(
            vectors[0]["old_out_left_bits"][2:], twelfth.prior.load()[0][3]
        )
        self.assertEqual(shapes[0]["ap2_op"], "MUL")
        self.assertEqual(
            shapes[0]["ap2_enum_class"],
            twelfth.CLASS + "TwoArgumentSimpleFunction$Type"
        )
        self.assertEqual(
            twelfth.candidate_telemetry(
                shapes, vectors
            )["direct_arithmetic_candidate_mismatches"],
            0,
        )
        twelfth.validate(self.report())

    def test_true_original_selected_path_weight_justifies_ap2_frontier(self):
        eleventh = twelfth.prior.load()
        tenth = twelfth.prior.prior.load()
        self.assertEqual((len(tenth), len(eleventh)), (128, 128))
        counts = {"in_left": 0, "in_right": 0, "out_left": 0, "out_right": 0}
        for i, (choice, operands) in enumerate(zip(tenth, eleventh, strict=True)):
            selector = twelfth.value("0x" + choice[0])
            actual_min_right = (
                twelfth.value("0x" + operands[2])
                < twelfth.value("0x" + operands[1])
            )
            actual_max_right = (
                twelfth.value("0x" + operands[4])
                > twelfth.value("0x" + operands[3])
            )
            inside = -1_000_000.0 <= selector < 1.5625
            if inside:
                counts["in_right" if actual_min_right else "in_left"] += 1
            else:
                counts["out_right" if actual_max_right else "out_left"] += 1
            if i == 110:
                # Real original MAX right-wins sample; outer choice selects
                # the in-range branch, so it does not influence that root.
                self.assertTrue(actual_max_right)
                self.assertTrue(inside)
        self.assertEqual(
            counts, {"in_left": 67, "in_right": 1, "out_left": 60, "out_right": 0}
        )
        root_path = (
            Path(__file__).resolve().parents[2]
            / "crates/world/helve-world-gen/tests/data/"
              "stock_finaldensity_min_root_128_rawbits.tsv"
        )
        roots = [line.split("\t") for line in root_path.read_text(
            encoding="ascii"
        ).splitlines()]
        self.assertEqual(len(roots), 128)
        root_left = root_right = root_left_out_ap2 = root_left_inright = 0
        for index, (original_root, original_choice, observed) in enumerate(
            zip(roots, tenth, eleventh, strict=True)
        ):
            self.assertEqual(len(original_root), 3)
            left = twelfth.value("0x" + original_root[0])
            right = twelfth.value("0x" + original_root[1])
            self.assertNotEqual(left, right)
            left_wins = left < right
            self.assertEqual(
                original_root[2],
                original_root[0] if left_wins else original_root[1]
            )
            root_left += int(left_wins)
            root_right += int(not left_wins)
            choice_inside = (
                -1_000_000.0
                <= twelfth.value("0x" + original_choice[0])
                < 1.5625
            )
            min_right = (
                twelfth.value("0x" + observed[2])
                < twelfth.value("0x" + observed[1])
            )
            max_right = (
                twelfth.value("0x" + observed[4])
                > twelfth.value("0x" + observed[3])
            )
            root_left_out_ap2 += int(left_wins and not choice_inside and not max_right)
            root_left_inright += int(left_wins and choice_inside and min_right)
        self.assertEqual(
            (root_left, root_right, root_left_out_ap2, root_left_inright),
            (124, 4, 57, 0)
        )

    def test_adversarial_source_shape_seed_and_old_parent_mutations(self):
        original = self.frames().splitlines()
        changes = [
            lambda lines: lines.pop(2),
            lambda lines: lines.append(lines[-1]),
            lambda lines: lines.__setitem__(1, lines[1].replace(
                "TwoArgumentSimpleFunction$Type", "FakeType", 1)),
            lambda lines: lines.__setitem__(1, lines[1].replace(
                "|MUL|", "|UNSUPPORTED|", 1)),
            lambda lines: lines.__setitem__(1, lines[1].replace(
                "|Noise", "|invalid.class", 1)),
            lambda lines: lines.__setitem__(1, lines[1].replace(
                "|Constant", "|also.invalid", 1)),
        ]

        def old_parent_mutation(lines: list[str]) -> None:
            fields = lines[2].split("|")
            fields[-1] = "0000000000000000"
            lines[2] = "|".join(fields)

        changes.append(old_parent_mutation)
        for i, change in enumerate(changes):
            rows = original.copy()
            change(rows)
            with self.subTest(i=i), self.assertRaises(twelfth.TwelfthLayerError):
                twelfth.parse_output("\n".join(rows))
        report = self.report()
        report["shapes"][2]["ap2_op"] = "ADD"
        with self.assertRaises(twelfth.TwelfthLayerError):
            twelfth.validate(report)

    def test_source_receipt_all_laws_false_and_candidate_mismatch_telemetry(self):
        for key in (
            "source_text_included", "prior_eleventh_fixture_sha256",
            "prior_eleventh_report_sha256", "official_server_sha256",
            "source_archive_sha256", "sample_context",
            "new_twelfth_outleft_ap2_children_observed",
        ):
            report = self.report()
            report[key] = (
                False if key == "new_twelfth_outleft_ap2_children_observed" else True
            )
            with self.subTest(field=key), self.assertRaises(twelfth.TwelfthLayerError):
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

        # Real source child values cannot be censored merely because a
        # plausible primitive arithmetic candidate disagrees on some point.
        report = self.report()
        for shape in report["shapes"]:
            shape["ap2_op"] = "ADD"
        report["arithmetic_candidate_telemetry"] = twelfth.candidate_telemetry(
            report["shapes"], report["vectors"]
        )
        self.assertGreater(
            report["arithmetic_candidate_telemetry"][
                "direct_arithmetic_candidate_mismatches"],
            0,
        )
        twelfth.validate(report)

    def test_missing_private_original_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "do-not-create.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = twelfth.main([
                    "--source", str(Path(td) / "absent.zip"),
                    "--db", str(Path(td) / "absent.sqlite"),
                    "--lock", str(Path(td) / "absent.toml"),
                    "--server-jar", str(Path(td) / "absent.jar"),
                    "--output", str(dest),
                ])
            self.assertEqual(code, 2)
            self.assertFalse(dest.exists())
            self.assertIn("TWELFTH LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "JDK javac required")
    def test_source_free_java_twelfth_compiles(self):
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
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
