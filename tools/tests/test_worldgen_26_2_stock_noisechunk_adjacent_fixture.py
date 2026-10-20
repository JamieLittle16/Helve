"""Exact genuine 26.2 JVM adjacent NoiseChunk bits; candidate lifecycle only."""
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
import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent  # noqa: E402
import worldgen_26_2_stock_noisechunk_adjacent_fixture as fixture  # noqa: E402
import worldgen_26_2_stock_noisechunk_complete_cell_fixture as complete  # noqa: E402


class OriginalAdjacentNoiseChunkFixtureTests(unittest.TestCase):
    @staticmethod
    def manifest():
        bits=fixture.load_bits()
        return {
            "schema":1,"kind":adjacent.KIND,
            "minecraft":"26.2","protocol":776,"data_version":4903,
            "source_archive_sha256":adjacent.cell.frozen.SOURCE_SHA256,
            "official_server_sha256":adjacent.cell.frozen.SERVER_SHA256,
            "previous_original_complete_cell_sha256":complete.ORIGINAL_JSON_SHA256,
            "source_methods":copy.deepcopy(fixture.source_methods()),
            "world_seeds":list(adjacent.SEEDS),
            "chunk_origins":list(adjacent.CHUNK_ORIGINS),
            "sample_context":"NoiseChunk",
            "traversal":"EXPERIMENTAL_xcell_zcell_ycell_desc_yblock_desc_xblock_zblock",
            "stock_registry_used":True,
            "stock_noisechunk_adjacent_cells_observed":True,
            "stock_noisechunk_canonical_traversal_qualified":False,
            "stock_noisechunk_full_lifecycle_qualified":False,
            "world_seed_random_state_bound":False,
            "full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "source_text_included":False,
            "production_worldgen_enabled":False,
            "vectors":[dict(row,value_bits="0x"+bits[i])
                       for i,row in enumerate(adjacent.input_rows())],
        }

    def test_all_768_exact_original_bits_and_32_immutable_complete_cell_overlaps(self):
        bits=fixture.load_bits()
        self.assertEqual(len(bits),768)
        self.assertEqual(len(set(bits)),768)
        self.assertEqual(bits[0],"3fc684d2526f5758")
        self.assertEqual(bits[-1],"bfafc475a9c048c4")
        self.assertEqual(fixture.overlapping_count(bits),32)
        self.assertEqual(len(fixture.source_methods()),12)
        self.assertFalse(any(x["reviewed"] for x in fixture.source_methods().values()))
        fixture.validate_manifest(self.manifest(),bits)

    def test_all_mutations_of_bit_fixture_fail_closed(self):
        raw=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(raw),fixture.FIXTURE_BYTES)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"wrong.txt"
            for mutated in (
                b"0"+raw[1:],
                raw[:-17],
                raw+b"0123456789abcdef\n",
                raw.replace(b"3fc684d2526f5758",b"7ff8000000000000",1),
            ):
                self.assertNotEqual(mutated,raw)
                p.write_bytes(mutated)
                with self.subTest(size=len(mutated)),self.assertRaises(
                    fixture.FrozenAdjacentError
                ):
                    fixture.load_bits(p)

    def test_provenance_order_bits_and_every_production_gate_fail_closed(self):
        original=self.manifest()
        bits=fixture.load_bits()
        gates=(
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified","independent_var_sem_admitted",
            "source_text_included","production_worldgen_enabled",
        )
        for gate in gates:
            mutated=copy.deepcopy(original);mutated[gate]=True
            with self.subTest(gate=gate),self.assertRaises(fixture.FrozenAdjacentError):
                fixture.validate_manifest(mutated,bits)
        mutations=(
            lambda d:d["vectors"].reverse(),
            lambda d:d["vectors"][101].__setitem__("block_z",9),
            lambda d:d["vectors"][101].__setitem__("value_bits","0x0000000000000000"),
            lambda d:d["vectors"].pop(),
            lambda d:d["source_methods"]["chunk_swap"].__setitem__("reviewed",True),
            lambda d:d["source_methods"]["generator_do_fill"].__setitem__("body_sha256","0"*64),
            lambda d:d.__setitem__("previous_original_complete_cell_sha256","0"*64),
            lambda d:d.__setitem__("traversal","canonical"),
            lambda d:d.__setitem__("chunk_origins",[0,16]),
            lambda d:d.__setitem__("sample_context","SinglePointContext"),
        )
        for i,mutate in enumerate(mutations):
            m=copy.deepcopy(original);mutate(m)
            with self.subTest(case=i),self.assertRaises(fixture.FrozenAdjacentError):
                fixture.validate_manifest(m,bits)

    def test_original_capture_receipt_cannot_be_forged_as_reconstruction(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fake.json"
            p.write_text(json.dumps(self.manifest()))
            with self.assertRaisesRegex(fixture.FrozenAdjacentError,"bytes/SHA"):
                fixture.validate_original_capture(p)

    def test_standalone_cli_reports_frozen_candidate_without_opening_gates(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(fixture.main([]),0)
        info=json.loads(out.getvalue())
        self.assertEqual(info["vectors"],768)
        self.assertEqual(info["genuine_complete_cell_overlap_bitwise_matches"],32)
        self.assertTrue(info["candidate_adjacent_reference_frozen"])
        self.assertFalse(info["stock_noisechunk_canonical_traversal_qualified"])
        self.assertFalse(info["stock_noisechunk_full_lifecycle_qualified"])
        self.assertFalse(info["rust_router_numeric_parity_qualified"])
        self.assertFalse(info["independent_var_sem_admitted"])
        self.assertFalse(info["production_worldgen_enabled"])


if __name__=="__main__":
    unittest.main()
