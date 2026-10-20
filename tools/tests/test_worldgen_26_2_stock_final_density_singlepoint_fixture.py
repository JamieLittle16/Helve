"""Immutable actual 26.2 Overworld bound finalDensity SinglePointContext oracle."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_singlepoint_fixture as frozen  # noqa: E402
import worldgen_26_2_stock_final_density_singlepoint_capture as stock  # noqa: E402


class RealFinalDensityFrozenFixtureTests(unittest.TestCase):
    def manifest(self):
        methods={
            name:{
                "owner":owner,"signature":signature,
                "body_sha256":body,"normalized_sha256":normalized,
                "reviewed":False,
            }
            for name,(owner,signature,body,normalized) in frozen.METHODS.items()
        }
        rows=stock.input_rows()
        bits=frozen.load_bits()
        return {
            "schema":1,"kind":stock.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":stock.frozen.SOURCE_SHA256,
            "official_server_sha256":stock.frozen.SERVER_SHA256,
            "original_router_roots_sha256":stock.graph.ORIGINAL_ROOT_SHA256,
            "original_router_graph_sha256":stock.holder.ORIGINAL_GRAPH_SHA256,
            "original_holder_bindings_sha256":stock.ORIGINAL_HOLDER_SHA256,
            "source_methods":methods,"world_seeds":list(stock.SEEDS),
            "points":[list(point) for point in stock.POINTS],
            "sample_context":"DensityFunction$SinglePointContext",
            "stock_registry_used":True,
            "stock_bound_final_density_singlepoint_observed":True,
            "stock_noisechunk_interpolation_observed":False,
            "world_seed_random_state_bound":False,
            "router_numeric_parity_qualified":False,
            "full_router_graph_qualified":False,
            "source_text_included":False,
            "independent_var_sem_admitted":False,
            "production_worldgen_enabled":False,
            "vectors":[dict(row,value_bits="0x"+bits[i])
                       for i,row in enumerate(rows)],
        }

    def test_all_exact_original_128_rawbits_frozen_no_nan_and_distinct_seeds(self):
        bits=frozen.load_bits()
        self.assertEqual(len(bits),128)
        self.assertEqual(bits[0],"3fa330e560418937")
        self.assertEqual(bits[31],"3fa330e560418937")
        self.assertEqual(bits[127],"3fa330e560418937")
        self.assertEqual(len(set(bits)),97)
        self.assertEqual(bits.count("bfdd555555555555"),18)
        self.assertEqual(len(stock.input_rows()),128)
        self.assertEqual([bits[i*32] for i in range(4)],
                         ["3fa330e560418937"]*4)
        self.assertEqual([bits[i*32+8] for i in range(4)],
                         ["bf99983c131d5acc"]*4)
        self.assertGreater(len({bits[i*32+3] for i in range(4)}),1)

    def test_mutated_truncated_or_appended_bit_fixture_fails_closed(self):
        original=frozen.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"wrong_fixture.txt"
            for corrupted in (
                b"0"+original[1:],
                original[:-17],
                original+b"0000000000000000\n",
                original.replace(b"3fa330e560418937",b"7ff8000000000000",1),
            ):
                with self.subTest(length=len(corrupted)):
                    self.assertNotEqual(corrupted,original)
                    path.write_bytes(corrupted)
                    with self.assertRaises(frozen.FrozenFinalDensityError):
                        frozen.load_bits(path)

    def test_reference_manifest_pins_every_byte_and_gate(self):
        manifest=self.manifest()
        bits=frozen.load_bits()
        frozen.validate_manifest(manifest,bits)
        for flag in (
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified",
            "stock_noisechunk_interpolation_observed",
            "source_text_included","independent_var_sem_admitted",
            "production_worldgen_enabled",
        ):
            changed=copy.deepcopy(manifest)
            changed[flag]=True
            with self.subTest(flag=flag),self.assertRaises(
                frozen.FrozenFinalDensityError
            ):
                frozen.validate_manifest(changed,bits)
        for corrupt in (
            lambda m:m["vectors"][17].__setitem__("value_bits","0x0000000000000000"),
            lambda m:m["vectors"][17].__setitem__("block_x",999),
            lambda m:m["vectors"].reverse(),
            lambda m:m["source_methods"]["ap2_compute"].__setitem__(
                "body_sha256","f"*64),
            lambda m:m["source_methods"]["holder_holder_compute"].__setitem__(
                "reviewed",True),
            lambda m:m.__setitem__("original_holder_bindings_sha256","0"*64),
            lambda m:m.__setitem__("sample_context","NoiseChunk"),
        ):
            changed=copy.deepcopy(manifest)
            corrupt(changed)
            with self.assertRaises(frozen.FrozenFinalDensityError):
                frozen.validate_manifest(changed,bits)

    def test_exact_original_capture_is_required_for_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"synthetic-128.json"
            path.write_text(json.dumps(self.manifest()))
            with self.assertRaisesRegex(frozen.FrozenFinalDensityError,"SHA"):
                frozen.validate_original_capture(path)

    def test_fixture_works_standalone_without_private_minecraft_jvm(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(frozen.main([]),0)
        parsed=json.loads(out.getvalue())
        self.assertEqual(parsed["vectors"],128)
        self.assertTrue(parsed["stock_singlepoint_reference_verified"])
        self.assertFalse(parsed["rust_final_density_parity_verified"])
        self.assertFalse(parsed["stock_noisechunk_interpolation_observed"])
        self.assertFalse(parsed["production_worldgen_enabled"])


if __name__=="__main__":
    unittest.main()
