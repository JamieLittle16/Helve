"""Real original Minecraft Java 26.2 NoiseChunk full 512-point cell fixture."""
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
import worldgen_26_2_stock_noisechunk_complete_cell_capture as complete  # noqa: E402
import worldgen_26_2_stock_noisechunk_complete_cell_fixture as fixture  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_fixture as first16  # noqa: E402


class GenuineCompleteNoiseChunkCellTests(unittest.TestCase):
    def manifest(self):
        words=fixture.load_bits()
        return {
            "schema":1,"kind":complete.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":complete.cell.frozen.SOURCE_SHA256,
            "official_server_sha256":complete.cell.frozen.SERVER_SHA256,
            "previous_original_cell_sha256":first16.ORIGINAL_JSON_SHA256,
            "previous_original_singlepoint_sha256":
                complete.cell.scalar_fixture.ORIGINAL_JSON_SHA256,
            "source_methods":first16.source_methods(),
            "world_seeds":list(complete.SEEDS),
            "points":[list(x) for x in complete.POINTS],
            "sample_context":"NoiseChunk",
            "traversal":"single_cell_y_ascending_x_ascending_z_ascending",
            "cell_geometry":{"width":4,"height":8,"min_y":-64,
                             "world_height":384,"cell_x":0,"cell_y":16,"cell_z":0},
            "wrapped_classes":[complete.WRAPPED]*4,
            "stock_registry_used":True,
            "stock_noisechunk_complete_cell_observed":True,
            "stock_noisechunk_canonical_traversal_qualified":False,
            "stock_noisechunk_full_lifecycle_qualified":False,
            "world_seed_random_state_bound":False,
            "full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "source_text_included":False,
            "production_worldgen_enabled":False,
            "vectors":[dict(row,value_bits="0x"+words[i])
                       for i,row in enumerate(complete.input_rows())],
        }

    def test_original_all_512_exact_stock_bits_and_all_16_first_pass_overlaps(self):
        words=fixture.load_bits()
        self.assertEqual(len(words),512)
        self.assertEqual(len(set(words)),512)
        self.assertEqual(words[0],"3fb5d28da46fdcc5")
        self.assertEqual(words[-1],"bfcc0c61ee4dc371")
        first=first16.load_bits()
        matched=0
        for seed in range(4):
            for old_index,xyz in enumerate(complete.cell.POINTS):
                index=seed*128+fixture.POINT_INDEX[xyz]
                self.assertEqual(words[index],first[seed*4+old_index])
                matched+=1
        self.assertEqual(matched,16)
        fixture.validate_manifest(self.manifest(),words)

    def test_mutated_fixture_or_length_fails(self):
        original=fixture.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"corrupted.txt"
            for trial in (
                b"0"+original[1:],
                original[:-17],
                original+b"0123456789abcdef\n",
                original.replace(b"3fb5d28da46fdcc5",b"7ff8000000000000",1),
            ):
                with self.subTest(length=len(trial)):
                    self.assertNotEqual(trial,original)
                    path.write_bytes(trial)
                    with self.assertRaises(fixture.FrozenCompleteCellError):
                        fixture.load_bits(path)

    def test_manifest_fail_closed_for_all_flags_source_coordinates_and_bits(self):
        original=self.manifest()
        words=fixture.load_bits()
        fixture.validate_manifest(original,words)
        for flag in (
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified","independent_var_sem_admitted",
            "source_text_included","production_worldgen_enabled",
        ):
            changed=copy.deepcopy(original);changed[flag]=True
            with self.subTest(flag=flag),self.assertRaises(
                fixture.FrozenCompleteCellError
            ):
                fixture.validate_manifest(changed,words)
        changes=(
            lambda d:d["vectors"].reverse(),
            lambda d:d["vectors"][31].__setitem__("block_y",78),
            lambda d:d["vectors"][31].__setitem__("value_bits","0x0000000000000000"),
            lambda d:d["vectors"].pop(),
            lambda d:d["source_methods"]["chunk_wrap"].__setitem__("reviewed",True),
            lambda d:d["source_methods"]["chunk_select"].__setitem__("body_sha256","0"*64),
            lambda d:d.__setitem__("previous_original_cell_sha256","0"*64),
            lambda d:d.__setitem__("traversal","production_canonical"),
            lambda d:d.__setitem__("sample_context","SinglePointContext"),
        )
        for i,change in enumerate(changes):
            data=copy.deepcopy(original);change(data)
            with self.subTest(case=i),self.assertRaises(
                fixture.FrozenCompleteCellError
            ):
                fixture.validate_manifest(data,words)

    def test_byte_pinned_original_512_capture_cannot_be_replaced_by_reconstruction(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"synthetic.json"
            p.write_text(json.dumps(self.manifest()))
            with self.assertRaisesRegex(fixture.FrozenCompleteCellError,"bytes/SHA"):
                fixture.validate_original_capture(p)

    def test_source_free_standalone_cli_does_not_open_gates(self):
        stdout=io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(fixture.main([]),0)
        data=json.loads(stdout.getvalue())
        self.assertEqual(data["vectors"],512)
        self.assertEqual(data["original_overlap_bitwise_matches"],16)
        self.assertTrue(data["stock_noisechunk_complete_cell_reference_frozen"])
        self.assertFalse(data["stock_noisechunk_full_lifecycle_qualified"])
        self.assertFalse(data["stock_noisechunk_canonical_traversal_qualified"])
        self.assertFalse(data["rust_router_numeric_parity_qualified"])
        self.assertFalse(data["production_worldgen_enabled"])


if __name__=="__main__":
    unittest.main()
