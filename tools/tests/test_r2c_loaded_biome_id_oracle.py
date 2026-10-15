"""Qualification of direct loaded biome IDs, distinct from network decoding."""

from __future__ import annotations

import sys
import tomllib
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import r2c_loaded_biome_id_oracle as oracle


class DirectLoadedBiomeIdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = tuple(
            (TOOLS.parent / "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt")
            .read_text(encoding="utf-8").splitlines()
        )
        cls.lock = tomllib.loads(
            (TOOLS.parent / "vanilla/vanilla.lock.toml")
            .read_text(encoding="utf-8")
        )

    def report(self, names: tuple[str, ...] | None = None) -> bytes:
        return "".join(
            f"{index}\t{name}\n"
            for index, name in enumerate(names or self.inventory)
        ).encode("utf-8")

    def test_exact_direct_dense_numeric_id_report(self) -> None:
        parsed = oracle.parse_direct_id_report(self.report())
        self.assertEqual(parsed, self.inventory)
        for altered in (
            self.report().replace(b"0\t", b"1\t", 1),
            self.report().replace(b"1\t", b"01\t", 1),
            self.report()[:-1],
            self.report().replace(b"\n", b"\r\n"),
            self.report() + b"66\tminecraft:extra\n",
            self.report().replace(b"minecraft:plains", b"minecraft:forest"),
            self.report() + b"\xff",
        ):
            with self.subTest(altered=altered[:15]), self.assertRaises(
                oracle.LoadedIdOracleError
            ):
                oracle.parse_direct_id_report(altered)

    def test_crosscheck_fails_if_id_order_differs_from_configuration(self) -> None:
        server_sha = self.lock["runtime"]["server_sha256"]
        expected = oracle.compare_authorities(
            self.inventory, self.inventory, self.inventory, server_sha, self.lock
        )
        self.assertEqual(expected["count"], 66)
        self.assertEqual(
            expected["numeric_id_authority"],
            "RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING",
        )
        self.assertEqual(expected["names_by_verified_runtime_id_candidate"], list(self.inventory))
        inverted = list(self.inventory)
        inverted[1], inverted[2] = inverted[2], inverted[1]
        with self.assertRaises(oracle.LoadedIdOracleError):
            oracle.compare_authorities(
                tuple(inverted), self.inventory, self.inventory, server_sha, self.lock
            )
        with self.assertRaises(oracle.LoadedIdOracleError):
            oracle.compare_authorities(
                self.inventory, self.inventory, self.inventory, "a"*64, self.lock
            )

    def test_official_symbol_resolution_requires_explicit_unique_mappings(self) -> None:
        mapping = "\n".join([
            "net.minecraft.server.MinecraftServer -> a.b:",
            "    public net.minecraft.core.RegistryAccess registryAccess() -> c",
            "net.minecraft.core.registries.Registries -> x.y:",
            "    public static net.minecraft.resources.ResourceKey BIOME -> z",
            "net.minecraft.core.Registry -> r.s:",
            "    public net.minecraft.resources.ResourceLocation getKey(java.lang.Object) -> k",
            "net.minecraft.core.IdMap -> q.t:",
            "    public java.lang.Object byId(int) -> f",
            "    public int getId(java.lang.Object) -> g",
            "",
        ])
        symbols = oracle.symbols(mapping)
        self.assertEqual(symbols["SERVER_CLASS"], "a.b")
        self.assertEqual(symbols["BIOME_FIELD"], "z")
        self.assertEqual(symbols["BY_ID"], "f")
        self.assertEqual(symbols["GET_KEY"], "k")
        with self.assertRaises(oracle.LoadedIdOracleError):
            oracle.symbols(mapping.replace("registryAccess() -> c", "other() -> c"))


if __name__ == "__main__":
    unittest.main()
