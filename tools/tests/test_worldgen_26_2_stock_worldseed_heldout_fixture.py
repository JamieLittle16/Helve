"""The independent 576-row Minecraft 26.2 held-out raw-bit oracle is pinned."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_worldseed_heldout_fixture as target  # noqa: E402


class HeldoutStockFixtureTests(unittest.TestCase):
    def test_exact_full_576_word_sha_and_raw_float_format(self):
        bits = target.read_fixture()
        self.assertEqual(len(bits), 576)
        self.assertEqual(bits[0], "bfded41016e4261a")
        self.assertEqual(bits[287], "bfa078eb58200b97")
        self.assertEqual(bits[-1], "3fbe82b27db6a527")
        self.assertNotIn("NaN", bits)

    def test_mutated_truncated_trailing_garbage_and_changed_words_fail_closed(self):
        original = target.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "heldout.txt"
            for altered in (
                original[:-1],
                original + b"\n",
                b"g" + original[1:],
                b"0" + original[1:],
                original.replace(b"bfded41016e4261a", b"bfded41016e4261b", 1),
                original.replace(b"3fbe82b27db6a527", b"3fbe82b27db6a526", 1),
            ):
                with self.subTest(length=len(altered), front=altered[:20]):
                    path.write_bytes(altered)
                    with self.assertRaises(target.HeldoutFixtureError):
                        target.read_fixture(path)

    def test_unrelated_json_cannot_impersonate_original_stock_jvm_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jvm.json"
            path.write_text('{"vectors": []}\n')
            with self.assertRaises(target.HeldoutFixtureError):
                target.validate_original_capture(path)


if __name__ == "__main__":
    unittest.main()
