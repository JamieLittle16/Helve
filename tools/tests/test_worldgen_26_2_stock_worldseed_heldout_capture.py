"""Fail-closed tests for one new source-free, real-stock 26.2 held-out corpus."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_worldseed_heldout_capture as target  # noqa: E402
import worldgen_26_2_stock_worldseed_fixture as frozen  # noqa: E402
import worldgen_26_2_world_seed_density_capture as stock  # noqa: E402


class StockHeldoutWorldSeedTests(unittest.TestCase):
    @staticmethod
    def methods() -> dict:
        return {"stock_vanilla_lookup": {
            "body_sha256": frozen.VANILLA_STOCK_LOOKUP_SHA256,
            "owner": stock.VANILLA_REGISTRIES,
            "signature": "createLookup()",
            "normalized_sha256": "c" * 64,
        }}

    def manifest(self) -> dict:
        return {
            "schema": 1, "kind": target.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": frozen.SOURCE_SHA256,
            "official_server_sha256": frozen.SERVER_SHA256,
            "frontier_sha256": stock.FRONTIER_SHA256,
            "reference_fixture_sha256": frozen.FIXTURE_SHA256,
            "source_methods": self.methods(),
            "profiles": stock.PROFILES,
            "world_seeds": list(target.SEEDS),
            "noise_keys": list(stock.NOISE_KEYS),
            "points": [list(row) for row in target.POINTS],
            "stock_registry_used": True,
            "world_seed_random_state_observed": True,
            "world_seed_random_state_bound": False,
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "vectors": [dict(row, value_bits="0x8000000000000000")
                        for row in target.input_rows()],
        }

    def verify(self, data: dict) -> None:
        target.validate(
            data, source_sha=frozen.SOURCE_SHA256, server_sha=frozen.SERVER_SHA256,
            methods=self.methods())

    def test_exactly_576_new_seeds_keys_profiles_coordinates_and_no_duplicates(self):
        rows = target.input_rows()
        self.assertEqual(len(rows), 576)
        self.assertEqual(len({tuple(sorted(row.items())) for row in rows}), 576)
        self.assertFalse(set(target.SEEDS).intersection(stock.SEEDS))
        self.assertEqual(set(stock.NOISE_KEYS), {row["noise_key"] for row in rows})
        self.assertEqual(set(stock.PROFILES), {row["profile"] for row in rows})
        self.assertEqual({row["world_seed_bits"] for row in rows}, set(target.SEEDS))
        for row in rows:
            for coordinate in ("block_x", "block_y", "block_z"):
                self.assertGreaterEqual(row[coordinate], -(1 << 31))
                self.assertLess(row[coordinate], 1 << 31)
        self.verify(self.manifest())

    def test_mutations_reject_bad_frame_bad_count_bad_provenance_and_open_gates(self):
        edits = [
            lambda m: m["vectors"].pop(),
            lambda m: m["vectors"].reverse(),
            lambda m: m["vectors"][0].__setitem__("value_bits", "invalid"),
            lambda m: m["vectors"][0].__setitem__("block_x", 12345),
            lambda m: m["vectors"][0].__setitem__("world_seed_bits", "0x0000000000000000"),
            lambda m: m["points"].reverse(),
            lambda m: m["world_seeds"].reverse(),
            lambda m: m["noise_keys"].reverse(),
            lambda m: m.__setitem__("source_archive_sha256", "bad"),
            lambda m: m.__setitem__("reference_fixture_sha256", "bad"),
            lambda m: m.__setitem__("source_methods", {}),
            lambda m: m.__setitem__("stock_registry_used", False),
            lambda m: m.__setitem__("world_seed_random_state_bound", True),
            lambda m: m.__setitem__("independent_var_sem_admitted", True),
            lambda m: m.__setitem__("production_worldgen_enabled", True),
            lambda m: m.__setitem__("source_text_included", True),
        ]
        for mutate in edits:
            with self.subTest(edit=str(mutate)):
                data = self.manifest()
                mutate(data)
                with self.assertRaises(target.HeldoutNoiseError):
                    self.verify(data)

    def test_tagged_jvm_parser_maintains_ieee_negative_zero_and_strict_count(self):
        lines = [f"{stock.PREFIX}{i}|{i:016x}" for i in range(576)]
        values = stock.parse_bits("\n".join(lines), expected=576)
        self.assertEqual(values[0], "0x0000000000000000")
        self.assertEqual(values[-1], "0x000000000000023f")
        self.assertEqual(
            stock.parse_bits(
                "\n".join([f"{stock.PREFIX}{i}|8000000000000000"
                           for i in range(576)]), expected=576)[0],
            "0x8000000000000000",
        )
        for corrupt in (
            lines[:-1],
            lines + lines[:1],
            lines[1:2] + lines[0:1] + lines[2:],
            [lines[0]] * 576,
        ):
            with self.assertRaises(stock.WorldSeedNoiseError):
                stock.parse_bits("\n".join(corrupt), expected=576)

    def test_heldout_mode_is_explicit_and_does_not_allow_original_1440_mode_substitution(self):
        events = []
        def fake_run(args, **kwargs):
            events.append(args)
            if args[0] == "javac":
                return subprocess.CompletedProcess(args, 0, "", "")
            return subprocess.CompletedProcess(
                args, 0,
                "\n".join(f"{stock.PREFIX}{i}|3ff0000000000000"
                          for i in range(576)), "")
        with mock.patch.object(target.official, "extract_classpath", return_value=[]), \
             mock.patch.object(target.subprocess, "run", side_effect=fake_run):
            output = target.observe(Path("/tmp/stock-runtime.jar"), target.input_rows())
        self.assertEqual(len(output), 576)
        self.assertIn("--heldout-576", events[1])
        self.assertNotIn("source.java", str(events))
        invalid = target.input_rows()
        invalid[0] = dict(invalid[0], world_seed_bits=stock.SEEDS[0])
        with self.assertRaises(target.HeldoutNoiseError):
            target.observe(Path("/tmp/stock-runtime.jar"), invalid)

    def test_local_capture_writes_once_with_both_source_and_production_gates_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / "pin.toml"
            lock.write_text(
                'minecraft="26.2"\nprotocol=776\ndata_version=4903\n'
                '[runtime]\nserver_sha256="' + frozen.SERVER_SHA256 + '"\n'
            )
            output = root / "new-heldout.json"
            with mock.patch.object(target.stock, "reference_frontier", return_value={}), \
                 mock.patch.object(target.vanilla_atlas, "connect_db") as db, \
                 mock.patch.object(target.source_probe, "require_pinned_source",
                                   return_value=frozen.SOURCE_SHA256), \
                 mock.patch.object(target.stock, "source_methods",
                                   return_value=self.methods()), \
                 mock.patch.object(target.official, "sha256_file",
                                   return_value=frozen.SERVER_SHA256), \
                 mock.patch.object(target, "observe",
                                   return_value=["0x0000000000000000"] * 576):
                result = target.capture(
                    source=root/"source.zip", db=root/"atlas.sqlite",
                    lock=lock, server=root/"server.jar", frontier=root/"frontier.json",
                    output=output)
                self.assertEqual(result["vectors"], 576)
                self.assertFalse(result["rust_heldout_parity_verified"])
                self.assertTrue(db.return_value.close.called)
                data = json.loads(output.read_text())
                self.verify(data)
                with self.assertRaises(ValueError):
                    target.capture(
                        source=root/"source.zip", db=root/"atlas.sqlite",
                        lock=lock, server=root/"server.jar", frontier=root/"frontier.json",
                        output=output)


if __name__ == "__main__":
    unittest.main()
