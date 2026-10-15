"""Hermetic tests for R2C's *non-admitted* official heightmap fact oracle."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import official_r2c_heightmap_facts as oracle


def make_rows(count: int = oracle.EXPECTED_STATE_COUNT) -> str:
    return "\n".join(
        f"{i}\t{int(i != 0)}\t{int(i in (1, 3))}\t{int(i == 2)}\t{int(i == 3)}"
        for i in range(count)
    )


class OfficialR2cHeightmapFactsTests(unittest.TestCase):
    def test_exact_java_symbols_and_selected_predicate_names(self) -> None:
        source = oracle.java_probe(None)
        self.assertIn("Blocks", source)
        self.assertIn("blocksMotion", source)
        self.assertIn("getFluidState", source)
        self.assertIn("LeavesBlock", source)
        self.assertIn("getBlock", source)
        self.assertIn("getId", source)
        self.assertIn("BLOCK_STATE_REGISTRY", source)

    def test_all_32366_dense_state_ids_keep_global_id_and_packed_predicates(self) -> None:
        parsed = oracle.parse_probe_output(make_rows())
        self.assertEqual(len(parsed), 32_366)
        self.assertEqual(parsed[0], 0)
        self.assertEqual(parsed[1], 0b0011)
        self.assertEqual(parsed[2], 0b0101)
        self.assertEqual(parsed[3], 0b1011)
        self.assertEqual(parsed[4], 1)

        reversed_rows = "\n".join(reversed(make_rows().splitlines()))
        self.assertEqual(parsed, oracle.parse_probe_output(reversed_rows))

    def test_truncation_duplicate_and_outside_universe_are_rejected(self) -> None:
        rows = make_rows().splitlines()
        with self.assertRaisesRegex(ValueError, "not dense"):
            oracle.parse_probe_output("\n".join(rows[:-1]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            oracle.parse_probe_output("\n".join(rows + [rows[10]]))
        rows[-1] = f"{oracle.EXPECTED_STATE_COUNT}\t1\t0\t0\t0"
        with self.assertRaisesRegex(ValueError, "not dense"):
            oracle.parse_probe_output("\n".join(rows))

    def test_malformed_row_and_impossible_air_facts_fail_closed(self) -> None:
        base = make_rows().splitlines()
        invalid = base.copy()
        invalid[4] = "4\t1\t1\t2\t0"
        with self.assertRaisesRegex(ValueError, "invalid ID/boolean"):
            oracle.parse_probe_output("\n".join(invalid))
        invalid[4] = "4\t0\t1\t0\t0"
        with self.assertRaisesRegex(ValueError, "contradicts air"):
            oracle.parse_probe_output("\n".join(invalid))
        invalid[4] = "garbage"
        with self.assertRaisesRegex(ValueError, "5 fields"):
            oracle.parse_probe_output("\n".join(invalid))


if __name__ == "__main__":
    unittest.main()
