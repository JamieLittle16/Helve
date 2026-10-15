"""Independent saved 26.2 quart-biome oracle regression tests."""

from __future__ import annotations

import unittest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import r2c_genuine_save_biome_differential as diff  # noqa: E402
import vanilla_section_extractor as nbt  # noqa: E402


def packed_section(size: int) -> tuple[dict[str, object], tuple[str, ...]]:
    palette = tuple(f"minecraft:biome_{i}" for i in range(size))
    bits = (size - 1).bit_length()
    per_word = 64 // bits
    words = [0] * ((64 + per_word - 1) // per_word)
    expected: list[str] = []
    for i in range(64):
        index = (i * 17 + 3) % size
        words[i // per_word] |= index << ((i % per_word) * bits)
        expected.append(palette[index])
    return (
        {"palette": nbt.NbtListValue(8, palette), "data": nbt.NbtLongArray(tuple(words))},
        tuple(expected),
    )


class SavedBiomeOracleTests(unittest.TestCase):
    def test_uniform_and_packed_biome_cell_laws(self) -> None:
        uniform = {"palette": nbt.NbtListValue(8, ("minecraft:plains",))}
        self.assertEqual(diff.decode_biome_cells(uniform), ("minecraft:plains",) * 64)
        self.assertEqual(
            diff.decode_biome_cells({**uniform, "data": nbt.NbtLongArray(())}),
            ("minecraft:plains",) * 64,
        )
        for size in (2, 3, 5, 9, 17, 33, 64):
            with self.subTest(palette=size):
                source, expected = packed_section(size)
                self.assertEqual(diff.decode_biome_cells(source), expected)

    def test_unknown_padding_and_invalid_palette_fail_closed(self) -> None:
        source, _ = packed_section(3)
        with self.assertRaises(diff.BiomeDifferentialError):
            diff.decode_biome_cells({**source, "data": nbt.NbtLongArray((0,))})
        with self.assertRaises(diff.BiomeDifferentialError):
            diff.decode_biome_cells(
                {"palette": nbt.NbtListValue(8, ()), "data": nbt.NbtLongArray(())}
            )
        with self.assertRaises(diff.BiomeDifferentialError):
            diff.decode_biome_cells(
                {"palette": nbt.NbtListValue(8, ("minecraft:plains",)),
                 "data": nbt.NbtLongArray((0,))}
            )
        with self.assertRaises(diff.BiomeDifferentialError):
            diff.decode_biome_cells(
                {"palette": nbt.NbtListValue(
                    8, ("minecraft:plains", "minecraft:forest", "minecraft:desert")
                ),
                 "data": nbt.NbtLongArray((3, 0))}
            )

    def test_nonspanning_padding_and_quart_yzx_order(self) -> None:
        source, expected = packed_section(5)
        self.assertEqual(diff.decode_biome_cells(source), expected)
        self.assertEqual(expected[0], "minecraft:biome_3")
        self.assertEqual(expected[1], "minecraft:biome_0")
        self.assertEqual(expected[16], "minecraft:biome_0")


if __name__ == "__main__":
    unittest.main()
