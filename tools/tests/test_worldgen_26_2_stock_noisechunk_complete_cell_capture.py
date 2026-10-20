"""Fail-closed 512-value original 26.2 NoiseChunk single-cell numeric transport."""
from __future__ import annotations

import copy
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_noisechunk_complete_cell_capture as grid  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_fixture as frozen  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_capture as cell  # noqa: E402


class CompleteStockNoiseChunkCellTests(unittest.TestCase):
    def valid_output(self):
        lines=["stock bootstrap logs"]
        for si,seed in enumerate(grid.SEEDS):
            lines.append(cell.TAG_HEAD+f"|{si}|{seed}|4|8|-64|384|{grid.WRAPPED}|128")
            for pi,(x,y,z) in enumerate(grid.POINTS):
                value=struct.pack(">d",float(x+y+z)).hex()
                lines.append(cell.TAG_BITS+f"|{si*128+pi}|{value}")
            lines.append(cell.TAG_END+f"|{si}|128")
        return lines

    def manifest(self,bits):
        return {
            "schema":1,"kind":grid.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":cell.frozen.SOURCE_SHA256,
            "official_server_sha256":cell.frozen.SERVER_SHA256,
            "previous_original_cell_sha256":frozen.ORIGINAL_JSON_SHA256,
            "previous_original_singlepoint_sha256":
                cell.scalar_fixture.ORIGINAL_JSON_SHA256,
            "source_methods":frozen.source_methods(),
            "world_seeds":list(grid.SEEDS),
            "points":[list(p) for p in grid.POINTS],
            "sample_context":"NoiseChunk",
            "traversal":"single_cell_y_ascending_x_ascending_z_ascending",
            "cell_geometry":{
                "width":4,"height":8,"min_y":-64,"world_height":384,
                "cell_x":0,"cell_y":16,"cell_z":0,
            },
            "wrapped_classes":[grid.WRAPPED]*4,
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
            "vectors":[dict(row,value_bits=b)
                       for row,b in zip(grid.input_rows(),bits,strict=True)],
        }

    def test_complete_cell_has_128_coordinates_in_strict_y_x_z_order(self):
        self.assertEqual(len(grid.POINTS),128)
        self.assertEqual(len(set(grid.POINTS)),128)
        self.assertEqual(grid.POINTS[0],(0,64,0))
        self.assertEqual(grid.POINTS[1],(0,64,1))
        self.assertEqual(grid.POINTS[15],(3,64,3))
        self.assertEqual(grid.POINTS[16],(0,65,0))
        self.assertEqual(grid.POINTS[-1],(3,71,3))
        self.assertEqual(len(grid.input_rows()),512)
        bits=grid.parse_output("\n".join(self.valid_output()))
        self.assertEqual(len(bits),512)
        self.assertEqual(bits[0],"0x4050000000000000")
        self.assertEqual(bits[127],struct.pack(">d",77.0).hex().join(["0x",""]))
        grid.validate(self.manifest(bits),frozen.source_methods())

    def test_corrupted_missing_reordered_or_nonfinite_outputs_fail_closed(self):
        original=self.valid_output()
        i=next(i for i,v in enumerate(original)
               if v.startswith(cell.TAG_BITS+"|2|"))
        for bad in (
            original[:i]+original[i+1:],
            original[:i]+[original[i]]+original[i:],
            original[:-1],
            original+[original[-1]],
            [v.replace("|2|","|99|",1) if j==i else v
             for j,v in enumerate(original)],
            [cell.TAG_BITS+"|2|7ff8000000000000" if j==i else v
             for j,v in enumerate(original)],
            [v.replace("|128","|4") if v.startswith(cell.TAG_HEAD) else v
             for v in original],
            [v.replace(grid.WRAPPED,"java.lang.Object")
             if v.startswith(cell.TAG_HEAD) else v for v in original],
        ):
            with self.assertRaises(grid.CompleteCellError):
                grid.parse_output("\n".join(bad))
        with self.assertRaisesRegex(grid.CompleteCellError,"JVM PHASE"):
            grid.parse_output(cell.TAG_FAILURE+
                "|original-NoiseChunk-interpolate-0-7|"
                "java.lang.IllegalStateException|"
                "java.lang.reflect.InvocationTargetException|wrong original cell")

    def test_fixed_source_identity_and_every_qualification_gate_stay_closed(self):
        bits=grid.parse_output("\n".join(self.valid_output()))
        manifest=self.manifest(bits)
        grid.validate(manifest,frozen.source_methods())
        for gate in (
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified","source_text_included",
            "independent_var_sem_admitted","production_worldgen_enabled",
        ):
            modified=copy.deepcopy(manifest);modified[gate]=True
            with self.subTest(gate=gate),self.assertRaises(grid.CompleteCellError):
                grid.validate(modified,frozen.source_methods())
        attacks=(
            lambda d:d["vectors"].pop(),
            lambda d:d["vectors"].reverse(),
            lambda d:d["vectors"][63].__setitem__("block_y",68),
            lambda d:d["vectors"][63].__setitem__("value_bits","0x7ff0000000000000"),
            lambda d:d["cell_geometry"].__setitem__("height",16),
            lambda d:d["source_methods"]["chunk_wrap"].__setitem__("reviewed",True),
            lambda d:d.__setitem__("previous_original_cell_sha256","0"*64),
            lambda d:d.__setitem__("traversal","canonical"),
            lambda d:d["wrapped_classes"].__setitem__(2,"java.lang.Object"),
        )
        for i,attack in enumerate(attacks):
            modified=copy.deepcopy(manifest);attack(modified)
            with self.subTest(attack=i),self.assertRaises(grid.CompleteCellError):
                grid.validate(modified,frozen.source_methods())

    def test_requires_authentic_previous_original_cell_not_fake_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fake-original.json"
            p.write_text("{}\n")
            with self.assertRaisesRegex(frozen.FrozenNoiseChunkError,"bytes/SHA"):
                frozen.validate_original_capture(p)


if __name__=="__main__":
    unittest.main()
