"""Immutable source-only eleventh five-child fixture and mutation guards."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_eleventh_layer_fixture as eleventh  # noqa: E402


class EleventhActualSourceFixtureTests(unittest.TestCase):
    def test_only_real_new_words_and_independently_frozen_tenth_parents(self):
        rows = eleventh.load()
        self.assertEqual(len(rows), 128)
        self.assertEqual(
            rows[0],
            (
                "402ec6c8407d1d3d", "402ec6c8407d1d3d",
                "400084be7e4c37c8", "3fd36cd350602ed8",
                "c12e848000000000",
            ),
        )
        self.assertEqual(
            rows[-1],
            (
                "402b486e660f3a02", "402b486e660f3a02",
                "3ff958e06153be57", "3fd44719e77631df",
                "c12e848000000000",
            ),
        )
        self.assertEqual(
            rows[110][3:],
            ("3fde51afdb79aeec", "3fdf83606ba08263"),
        )
        self.assertEqual(eleventh.main([]), 0)

    def test_mutations_reject_wrong_sha_shape_and_selected_results(self):
        raw = eleventh.FIXTURE.read_bytes()
        self.assertEqual(len(raw), 10880)
        changes = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"402ec6c8407d1d3d", b"402ec6c8407d1d3e", 1),
            raw.replace(b"402ec6c8407d1d3d", b"7ff0000000000000", 1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "changed.tsv"
            for i, changed in enumerate(changes):
                with self.subTest(i=i), self.assertRaises(eleventh.EleventhFixtureError):
                    path.write_bytes(changed)
                    eleventh.load(path)
            # An actually selected MIN operand must not change the old Ap2.
            path.write_bytes(raw.replace(
                b"400084be7e4c37c8", b"400084be7e4c37c9", 1
            ))
            with self.assertRaises(eleventh.EleventhFixtureError):
                eleventh.load(path, require_sha=False)
            # The rare right MAX winner must remain active, even without SHA.
            lines = raw.splitlines(keepends=True)
            lines[110] = lines[110].replace(
                b"3fdf83606ba08263", b"3fde000000000000", 1
            )
            path.write_bytes(b"".join(lines))
            with self.assertRaises(eleventh.EleventhFixtureError):
                eleventh.load(path, require_sha=False)

    def test_fabricated_owner_report_cannot_claim_source_admission(self):
        self.assertEqual(eleventh.REPORT_BYTES, 71499)
        self.assertEqual(eleventh.SHAPE["marker_type"], "CacheOnce")
        self.assertEqual(eleventh.SHAPE["in_op"], "MIN")
        self.assertEqual(eleventh.SHAPE["out_op"], "MAX")
        self.assertIs(eleventh.MARKER_TELEMETRY["source_law_admitted"], False)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "forged-owner.json"
            path.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(
                eleventh.EleventhFixtureError, "owner bytes/SHA"
            ):
                eleventh.validate_original(path)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = eleventh.main(["--capture", str(path)])
            self.assertEqual(rc, 2)
            self.assertIn("ELEVENTH FIXTURE OPEN", err.getvalue())


if __name__ == "__main__":
    unittest.main()
