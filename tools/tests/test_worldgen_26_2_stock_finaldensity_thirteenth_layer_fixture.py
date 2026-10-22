"""Immutable source-owned 26.2 thirteenth selected Ap2(MIN) fixture tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture as thirteenth  # noqa: E402


class ThirteenthActualSourceFixtureTests(unittest.TestCase):
    def test_new_only_original_operands_and_independently_frozen_twelfth_parent(self):
        rows = thirteenth.load()
        self.assertEqual(len(rows), 128)
        self.assertEqual(
            rows[0], ("3fd36cd350602ed8", "3fda6dfd96e05940")
        )
        self.assertEqual(
            rows[2], ("3fd8cc3c84dfd0f0", "3fd13497cc08e0e6")
        )
        self.assertEqual(
            rows[-1], ("3fd7ca385b5abe61", "3fd44719e77631df")
        )
        self.assertEqual(
            thirteenth.LEFT_WINS,
            (0, 1, 9, 10, 11, 12, 31, 32, 41, 53, 62, 117),
        )
        self.assertEqual(thirteenth.main([]), 0)

    def test_mutated_fixture_rejects_sha_shape_nonfinite_order_and_independent_parent(self):
        raw = thirteenth.FIXTURE.read_bytes()
        self.assertEqual(len(raw), 4352)
        altered = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"3fd36cd350602ed8", b"3fd36cd350602ed9", 1),
            raw.replace(b"3fda6dfd96e05940", b"7ff0000000000000", 1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "mutated.tsv"
            for i, candidate in enumerate(altered):
                path.write_bytes(candidate)
                with self.subTest(i=i), self.assertRaises(
                    thirteenth.ThirteenthFixtureError
                ):
                    thirteenth.load(path)
            # Parent-bound test must reject a tampered selected value with
            # fixture-SHA check disabled (not merely reject any byte change).
            path.write_bytes(
                raw.replace(b"3fd36cd350602ed8", b"3fd36cd350602ed9", 1)
            )
            with self.assertRaises(thirteenth.ThirteenthFixtureError):
                thirteenth.load(path, require_sha=False)
            # Test genuine right-winner sample, not only a selected left.
            path.write_bytes(
                raw.replace(b"3fd13497cc08e0e6", b"3fd13497cc08e0e7", 1)
            )
            with self.assertRaises(thirteenth.ThirteenthFixtureError):
                thirteenth.load(path, require_sha=False)
            with self.assertRaises(thirteenth.ThirteenthFixtureError):
                thirteenth.selected_min(
                    "0000000000000000", "8000000000000000"
                )

    def test_authentic_full_report_source_gates_and_shape_are_fixed(self):
        self.assertEqual(thirteenth.REPORT_BYTES, 41610)
        self.assertEqual(
            thirteenth.REPORT_SHA256,
            "e50e4ef14a7d3716613e0bb77982a5693c0395ac1f32e24325930dbf0c8d79db",
        )
        self.assertEqual(
            thirteenth.SHA256,
            "cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a",
        )
        self.assertEqual(thirteenth.SHAPE["ap2_op"], "MIN")
        self.assertEqual(
            thirteenth.SHAPE["ap2_left_class"], thirteenth.CLASS + "Ap2"
        )
        self.assertEqual(
            thirteenth.SHAPE["ap2_right_class"], thirteenth.CLASS + "HolderHolder"
        )
        self.assertEqual(
            thirteenth.TELEMETRY["direct_arithmetic_candidate_mismatches"], 0
        )
        self.assertIs(thirteenth.TELEMETRY["source_law_admitted"], False)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "forged-original.json"
            path.write_text('{"production_worldgen_enabled": true}', encoding="ascii")
            with self.assertRaisesRegex(
                thirteenth.ThirteenthFixtureError, "JVM report bytes/SHA"
            ):
                thirteenth.validate_original(path)
            out = io.StringIO()
            with contextlib.redirect_stderr(out):
                self.assertEqual(thirteenth.main(["--capture", str(path)]), 2)
            self.assertIn("THIRTEENTH FIXTURE OPEN", out.getvalue())


if __name__ == "__main__":
    unittest.main()
