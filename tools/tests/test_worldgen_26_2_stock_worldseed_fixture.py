"""Frozen, unadmitted official 26.2 stock world-seed numeric evidence tests."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_worldseed_fixture as stock  # noqa: E402
import worldgen_26_2_world_seed_density_capture as source  # noqa: E402


class OfficialStockWorldSeedFixtureTests(unittest.TestCase):
    def make_shape_only_manifest(self):
        """SYNTHETIC in-memory shape test; it is never accepted as an authentic capture."""
        methods = {
            name: {
                "owner": owner,
                "signature": method + "(test)",
                "body_sha256": sha,
                "normalized_sha256": "0" * 64,
            }
            for name, (owner, method, _, sha) in source.SOURCE_PINS.items()
        }
        methods["stock_vanilla_lookup"] = {
            "owner": source.VANILLA_REGISTRIES,
            "signature": "createLookup()",
            "body_sha256": stock.VANILLA_STOCK_LOOKUP_SHA256,
            "normalized_sha256": "0" * 64,
        }
        rows = source.input_rows()
        bits = stock.load_bits()
        return {
            "schema": 1,
            "kind": source.KIND,
            "stage": source.STAGE,
            "minecraft": "26.2",
            "protocol": 776,
            "data_version": 4903,
            "source_archive_sha256": stock.SOURCE_SHA256,
            "official_server_sha256": stock.SERVER_SHA256,
            "frontier_sha256": source.FRONTIER_SHA256,
            "profiles": source.PROFILES,
            "world_seeds": list(source.SEEDS),
            "noise_keys": list(source.NOISE_KEYS),
            "stock_registry_used": True,
            "world_seed_random_state_observed": True,
            "world_seed_random_state_bound": False,
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "source_methods": methods,
            "vectors": [dict(row, value_bits="0x" + value)
                        for row, value in zip(rows, bits, strict=True)],
        }

    def test_pinned_official_bits_are_1440_ordered_finite_64_bit_values(self):
        bits = stock.load_bits()
        self.assertEqual(len(bits), 3 * 5 * 3 * 32)
        self.assertEqual(bits[0], "3fe642a30a35f266")
        self.assertEqual(bits[480], "bfb1cb44d1eacac0")
        self.assertEqual(bits[-1], "3fc3cbbb372a1759")
        self.assertGreater(len(set(bits)), 1400)
        inputs = source.input_rows()
        self.assertEqual(len(inputs), len(bits))
        self.assertEqual(
            [(row["profile"], row["world_seed_bits"], row["noise_key"])
             for row in (inputs[0], inputs[480], inputs[1439])],
            [("unit", source.SEEDS[0], "TEMPERATURE"),
             ("quarter_xz", source.SEEDS[0], "TEMPERATURE"),
             ("quarter_xz_half_y", source.SEEDS[-1], "EROSION")],
        )
        self.assertEqual(len({(r["block_x"], r["block_y"], r["block_z"])
                              for r in inputs[:32]}), 32)

    def test_modifying_truncating_or_appending_fixture_never_passes(self):
        original = stock.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "copy.txt"
            for changed in (b"0" + original[1:], original[:-17],
                            original + b"0000000000000000\n"):
                path.write_bytes(changed)
                with self.assertRaises(stock.FixtureError):
                    stock.load_bits(path)

    def test_source_free_row_shapes_are_exact_and_promotion_is_rejected(self):
        bits = stock.load_bits()
        manifest = self.make_shape_only_manifest()
        stock.validate_manifest(manifest, bits)
        for flag in ("world_seed_random_state_bound",
                     "independent_var_sem_admitted", "production_worldgen_enabled",
                     "source_text_included"):
            changed = dict(manifest, **{flag: True})
            with self.subTest(flag=flag), self.assertRaises(stock.FixtureError):
                stock.validate_manifest(changed, bits)
        changed = dict(manifest, source_methods={
            **manifest["source_methods"],
            "stock_vanilla_lookup": {
                **manifest["source_methods"]["stock_vanilla_lookup"],
                "body_sha256": "f" * 64,
            },
        })
        with self.assertRaises(stock.FixtureError):
            stock.validate_manifest(changed, bits)
        changed = dict(manifest, vectors=list(manifest["vectors"]))
        changed["vectors"][41] = dict(changed["vectors"][41], block_y=999)
        with self.assertRaisesRegex(stock.FixtureError, "at 41"):
            stock.validate_manifest(changed, bits)
        changed = dict(manifest, vectors=list(manifest["vectors"]))
        changed["vectors"][701] = dict(changed["vectors"][701], value_bits="0x" + "f" * 16)
        with self.assertRaisesRegex(stock.FixtureError, "at 701"):
            stock.validate_manifest(changed, bits)

    def test_nonoriginal_manifest_json_is_never_accepted_as_official(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "fake.json"
            fake.write_text(json.dumps(self.make_shape_only_manifest()))
            with self.assertRaisesRegex(stock.FixtureError, "SHA-256 changed"):
                stock.validate_original_capture(fake)

    def test_cli_exposes_reference_evidence_without_false_rust_parity(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(stock.main([]), 0)
        got = json.loads(out.getvalue())
        self.assertEqual(got["vectors"], 1440)
        self.assertEqual(got["fixture_sha256"], stock.FIXTURE_SHA256)
        self.assertTrue(got["stock_world_seed_observed"])
        self.assertFalse(got["rust_world_seed_parity_verified"])
        self.assertFalse(got["production_worldgen_enabled"])


if __name__ == "__main__":
    unittest.main()
