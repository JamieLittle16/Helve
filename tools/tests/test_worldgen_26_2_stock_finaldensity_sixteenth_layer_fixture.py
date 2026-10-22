"""Immutable original 26.2 actual sixteenth MIN two-child numeric fixture."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture as original  # noqa: E402


class GenuineSixteenthNumericalFixture(unittest.TestCase):
    def test_actual_new_only_operands_and_independent_thirteenth_right_anchor(self):
        pairs = original.load()
        self.assertEqual(len(pairs), 128)
        self.assertEqual(pairs[0], ("3fe945aad175ec76", "3fda6dfd96e05940"))
        self.assertEqual(pairs[1], ("3fe31f37ec2a8f0c", "3fedc8aee7a77f12"))
        self.assertEqual(pairs[-1], ("3feb5515a9b74d4c", "3fd44719e77631df"))
        self.assertEqual(original.SHA256,
                         "bd56e08412141819e938a0370b5375c458ff131d2cda12882826108b196b99d9")
        self.assertEqual(original.REPORT_BYTES, 41479)
        self.assertEqual(original.main([]), 0)

    def test_strict_sha_format_nonfinite_tie_parent_winner_mutations(self):
        raw = original.FIXTURE.read_bytes()
        self.assertEqual(len(raw), 4352)
        mutants = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"3fe945aad175ec76", b"3fe945aad175ec77", 1),
            raw.replace(b"3fda6dfd96e05940", b"7ff0000000000000", 1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "falsified.tsv"
            for i, candidate in enumerate(mutants):
                path.write_bytes(candidate)
                with self.subTest(index=i), self.assertRaises(original.SixteenthFixtureError):
                    original.load(path)
            # Bypassing checksum MUST still reject wrong old parent.
            path.write_bytes(
                raw.replace(b"3fda6dfd96e05940", b"3fda6dfd96e05941", 1)
            )
            with self.assertRaises(original.SixteenthFixtureError):
                original.load(path, require_sha=False)
            # Also modify the left operand so that it wins and changes old result.
            path.write_bytes(
                raw.replace(b"3fe945aad175ec76", b"3fb0000000000000", 1)
            )
            with self.assertRaises(original.SixteenthFixtureError):
                original.load(path, require_sha=False)
            # Real IEEE signed zeros are not source-admitted via sample-only MIN.
            with self.assertRaises(original.SixteenthFixtureError):
                original.native_sample_min("0000000000000000", "8000000000000000")

    def test_pin_genuine_original_report_source_shapes_telemetry_and_no_admission(self):
        self.assertEqual(
            original.REPORT_SHA256,
            "648f5636c00f88c964c5b847abc57227157c2d53955cee971af05519126dcb5e"
        )
        self.assertEqual(original.SHAPE["ap2_op"], "MIN")
        self.assertEqual(original.SHAPE["ap2_left_class"], original.owner.CLASS + "Ap2")
        self.assertEqual(original.SHAPE["ap2_right_class"], original.owner.CLASS + "Ap2")
        self.assertEqual(original.TELEMETRY["observed_left_strictly_less"], 57)
        self.assertEqual(original.TELEMETRY["observed_right_strictly_less"], 71)
        self.assertEqual(original.TELEMETRY["arithmetic_candidate_mismatches"], 0)
        self.assertFalse(original.TELEMETRY["source_law_admitted"])
        with tempfile.TemporaryDirectory() as td:
            forged = Path(td) / "fake-original-sixteenth.json"
            forged.write_text('{"production_worldgen_enabled": true}', encoding="ascii")
            with self.assertRaisesRegex(original.SixteenthFixtureError, "report length/SHA"):
                original.validate_original(forged)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(original.main(["--capture", str(forged)]), 2)
            self.assertIn("SIXTEENTH FIXTURE OPEN", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
