"""Immutable original twelfth source-only two-Ap2-child fixture guards."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_twelfth_layer_fixture as twelfth  # noqa: E402


class TwelfthAp2FixtureTests(unittest.TestCase):
    def test_only_two_new_original_words_and_independent_eleventh_parent(self):
        rows = twelfth.load()
        self.assertEqual((len(rows), len(rows) * 2), (128, 256))
        self.assertEqual(
            rows[0], ("3fd36cd350602ed8", "3ff02e79237aeeb3")
        )
        self.assertEqual(
            rows[-1], ("3fd44719e77631df", "3ff011a1ef89c716")
        )
        self.assertEqual(
            rows[21], ("3fdd6a4ff536d815", "3fb6a36ffc3c01f8")
        )
        self.assertEqual(
            rows[97], ("3fd7b2b69c38ba1c", "3fc31fbfdb8186ab")
        )
        self.assertEqual(
            rows[106], ("3fd6d6f8e710dc69", "3fc0c75f4921555c")
        )
        self.assertEqual(twelfth.RIGHT_WIN_INDICES, (21, 97, 106))
        self.assertEqual(twelfth.main([]), 0)

    def test_wrong_sha_format_order_nonfinite_and_old_parent_mismatch(self):
        raw = twelfth.FIXTURE.read_bytes()
        self.assertEqual(len(raw), 4352)
        mutations = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"3fd36cd350602ed8", b"3fd36cd350602ed9", 1),
            raw.replace(b"3ff02e79237aeeb3", b"7ff0000000000000", 1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "mutated.tsv"
            for i, changed in enumerate(mutations):
                path.write_bytes(changed)
                with self.subTest(i=i), self.assertRaises(twelfth.TwelfthFixtureError):
                    twelfth.load(path)
            # Even without SHA enforcement, actual MIN selection MUST agree
            # with the independently frozen earlier eleventh Ap2 parent.
            path.write_bytes(raw.replace(
                b"3fd36cd350602ed8", b"3fd36cd350602ed9", 1
            ))
            with self.assertRaises(twelfth.TwelfthFixtureError):
                twelfth.load(path, require_sha=False)
            # Preserve an actual selected right operand; not a constant.
            lines = raw.splitlines(keepends=True)
            lines[21] = lines[21].replace(
                b"3fb6a36ffc3c01f8", b"3fe0000000000000", 1
            )
            path.write_bytes(b"".join(lines))
            with self.assertRaises(twelfth.TwelfthFixtureError):
                twelfth.load(path, require_sha=False)
            # No source qualification for an unreviewed numerical MIN tie.
            with self.assertRaises(twelfth.TwelfthFixtureError):
                twelfth.selected_min("0000000000000000", "8000000000000000")

    def test_exact_original_owner_provenance_and_false_gates(self):
        self.assertEqual(twelfth.REPORT_BYTES, 39658)
        self.assertEqual(
            twelfth.REPORT_SHA256,
            "041eadc4a4174b4bace6eed2270c129cad6c65fe06cdbd7396268216bf26ab26"
        )
        self.assertEqual(twelfth.SHAPE["ap2_op"], "MIN")
        self.assertEqual(twelfth.SHAPE["ap2_left_class"], twelfth.CLASS + "Ap2")
        self.assertEqual(twelfth.SHAPE["ap2_right_class"], twelfth.CLASS + "Ap2")
        self.assertEqual(
            twelfth.TELEMETRY["direct_arithmetic_candidate_mismatches"], 0
        )
        self.assertIs(twelfth.TELEMETRY["source_law_admitted"], False)
        with tempfile.TemporaryDirectory() as td:
            forged = Path(td) / "forged.json"
            forged.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(twelfth.TwelfthFixtureError, "report bytes/SHA"):
                twelfth.validate_original(forged)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                ret = twelfth.main(["--capture", str(forged)])
            self.assertEqual(ret, 2)
            self.assertIn("TWELFTH FIXTURE OPEN", err.getvalue())


if __name__ == "__main__":
    unittest.main()
