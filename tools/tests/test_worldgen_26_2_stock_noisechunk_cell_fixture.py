"""Frozen authenticated original 26.2 stock NoiseChunk numerical evidence."""
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
import worldgen_26_2_stock_noisechunk_cell_fixture as frozen  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_capture as cell  # noqa: E402


class StockNoiseChunkFrozenNumericTests(unittest.TestCase):
    def manifest(self):
        bits=frozen.load_bits()
        return {
            "schema":1,"kind":cell.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":cell.frozen.SOURCE_SHA256,
            "official_server_sha256":cell.frozen.SERVER_SHA256,
            "original_singlepoint_oracle_sha256":
                cell.scalar_fixture.ORIGINAL_JSON_SHA256,
            "source_methods":frozen.source_methods(),
            "world_seeds":list(cell.SEEDS),
            "points":[list(p) for p in cell.POINTS],
            "cell_geometry":{
                "width":4,"height":8,"min_y":-64,"world_height":384,
                "cell_x":0,"cell_y":16,"cell_z":0,
            },
            "sample_context":"NoiseChunk",
            "stock_registry_used":True,
            "stock_noisechunk_cell_observed":True,
            "stock_noisechunk_full_lifecycle_qualified":False,
            "world_seed_random_state_bound":False,
            "full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "source_text_included":False,
            "production_worldgen_enabled":False,
            "wrapped_classes":[frozen.WRAPPED]*4,
            "vectors":[dict(row,value_bits="0x"+bit)
                       for row,bit in zip(cell.input_rows(),bits,strict=True)],
        }

    def test_actual_16_unique_finite_ieee_bits_match_exact_shape_and_overlap(self):
        words=frozen.load_bits()
        self.assertEqual(len(words),16)
        self.assertEqual(len(set(words)),16)
        self.assertEqual(words[0],"3fb5d28da46fdcc5")
        self.assertEqual(words[-1],"bfc816a4ba539b11")
        self.assertEqual([words[i*4] for i in range(4)],[
            "3fb5d28da46fdcc5","3fb5fc0185d59b19",
            "3fa7a959223e7ff2","bfc1916e25c2ce6c",
        ])
        frozen.validate_manifest(self.manifest(),words)

    def test_no_modification_truncation_or_nonfinite_fixture_can_pass(self):
        actual=frozen.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            modified=Path(td)/"corrupt-oracle.txt"
            for payload in (
                b"0"+actual[1:],
                actual[:-17],
                actual+b"0000000000000000\n",
                actual.replace(b"3fb5d28da46fdcc5",b"7ff0000000000000",1),
            ):
                with self.subTest(modified_size=len(payload)):
                    modified.write_bytes(payload)
                    with self.assertRaises(frozen.FrozenNoiseChunkError):
                        frozen.load_bits(modified)

    def test_source_method_and_closed_gate_and_geometry_mutations_fail(self):
        words=frozen.load_bits()
        correct=self.manifest()
        frozen.validate_manifest(correct,words)
        for gate in (
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "independent_var_sem_admitted","source_text_included",
            "production_worldgen_enabled",
        ):
            changed=copy.deepcopy(correct)
            changed[gate]=True
            with self.subTest(gate=gate),self.assertRaises(frozen.FrozenNoiseChunkError):
                frozen.validate_manifest(changed,words)
        attacks=(
            lambda m:m["source_methods"]["chunk_wrap"].__setitem__("body_sha256","f"*64),
            lambda m:m["source_methods"]["chunk_select"].__setitem__("reviewed",True),
            lambda m:m["vectors"][2].__setitem__("block_z",3),
            lambda m:m["vectors"][2].__setitem__("value_bits","0x0000000000000000"),
            lambda m:m["vectors"].reverse(),
            lambda m:m["wrapped_classes"].__setitem__(0,"java.lang.Object"),
            lambda m:m["cell_geometry"].__setitem__("height",16),
            lambda m:m.__setitem__("sample_context","DensityFunction$SinglePointContext"),
        )
        for i,attack in enumerate(attacks):
            changed=copy.deepcopy(correct);attack(changed)
            with self.subTest(attack=i),self.assertRaises(frozen.FrozenNoiseChunkError):
                frozen.validate_manifest(changed,words)

    def test_source_free_mock_json_does_not_masquerade_as_original_jvm(self):
        with tempfile.TemporaryDirectory() as td:
            forged=Path(td)/"made-up.json"
            forged.write_text(json.dumps(self.manifest()))
            with self.assertRaisesRegex(frozen.FrozenNoiseChunkError,"bytes/SHA"):
                frozen.validate_original_capture(forged)

    def test_independent_standalone_validation_does_not_promote_rust_parity(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(frozen.main([]),0)
        data=json.loads(output.getvalue())
        self.assertEqual(data["vectors"],16)
        self.assertEqual(data["overlapping_singlepoint_exact_match"],4)
        self.assertTrue(data["stock_noisechunk_cell_reference_frozen"])
        self.assertFalse(data["stock_noisechunk_full_lifecycle_qualified"])
        self.assertFalse(data["rust_router_numeric_parity_qualified"])
        self.assertFalse(data["production_worldgen_enabled"])


if __name__=="__main__":
    unittest.main()
