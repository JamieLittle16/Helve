"""Source-free 26.2 stock NoiseRouter graph depth-4 identity/closure contract."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_router_graph_capture as graph  # noqa: E402


class StockRouterGraphContractTests(unittest.TestCase):
    def original(self):
        evidence=[]
        raw=graph.ROOT_FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         graph.ROOT_FIXTURE_SHA256)
        for row in raw.decode("ascii").splitlines():
            name,implementation,compute,children=row.split("\t")
            evidence.append({
                "field":name,"implementation_class":implementation,
                "compute_declaring_class":compute,
                "first_level_density_children":[
                    {"slot":a,"implementation_class":b}
                    for a,b in (piece.split(":",1) for piece in children.split(";")
                                if piece)
                ],
            })
        self.assertEqual(len(evidence),15)
        return {"bound_router_roots":[
            {"world_seed_bits":seed,"fields":copy.deepcopy(evidence)}
            for seed in graph.roots.SEEDS
        ]}

    def records(self):
        original=self.original()
        lines=["official minecraft boot diagnostics"]
        for seed_index,group in enumerate(original["bound_router_roots"]):
            lines.append(graph.JAVA_HEAD+
                         f"|{seed_index}|15|{graph.roots.ROUTER}")
            for i,field in enumerate(group["fields"]):
                lines.append(graph.JAVA_ROOT+
                             f"|{seed_index}|{i}|{field['field']}|{i}")
            nodes=[(
                0,field["implementation_class"],field["compute_declaring_class"],
                [(item["slot"],item["implementation_class"])
                 for item in field["first_level_density_children"]]
            ) for field in group["fields"]]
            for root in list(nodes):
                for _,cls in root[3]:
                    nodes.append((1,cls,cls,[]))
            nxt=15
            for id,(depth,cls,compute,children) in enumerate(nodes):
                lines.append(graph.JAVA_NODE+
                             f"|{seed_index}|{id}|{depth}|{cls}|{compute}|1|"
                             f"{len(children)}|{1 if depth==1 else 0}")
                for k,(name,_type) in enumerate(children):
                    lines.append(graph.JAVA_EDGE+
                                 f"|{seed_index}|{id}|{k}|{name}|{nxt}")
                    nxt+=1
                if depth==1:
                    lines.append(graph.JAVA_OPAQUE+
                                 f"|{seed_index}|{id}|0|value|double")
            self.assertEqual(nxt,len(nodes))
            lines.append(graph.JAVA_END+
                         f"|{seed_index}|{len(nodes)}|{len(nodes)-15}|"
                         f"{len(nodes)-15}")
        return "\n".join(lines)

    def test_real_frozen_15_roots_and_all_four_bounded_seed_graphs(self):
        original=self.original()
        result=graph.parse_output(self.records(),original)
        self.assertEqual(len(result),4)
        self.assertEqual([len(g["roots"]) for g in result],[15]*4)
        self.assertEqual([len(g["nodes"]) for g in result],[27]*4)
        self.assertEqual([g["density_edges"] for g in result],[12]*4)
        self.assertEqual([g["opaque_record_slots"] for g in result],[12]*4)
        for group in result:
            self.assertEqual(group["roots"][11]["field"],"finalDensity")
            final=group["nodes"][group["roots"][11]["node_id"]]
            self.assertEqual([c["slot"] for c in final["density_children"]],
                             ["argument1","argument2"])
            self.assertEqual(group["nodes"][group["roots"][10]["node_id"]]
                             ["implementation_class"].split("$")[-1],
                             "FindTopSurface")

    def test_transport_detects_missing_duplicate_reordered_edge_and_bad_depth(self):
        original=self.original()
        transcript=self.records()
        rows=transcript.splitlines()
        header=next(i for i,v in enumerate(rows)
                    if v.startswith(graph.JAVA_HEAD+"|1|"))
        first_edge=next(i for i,v in enumerate(rows)
                        if v.startswith(graph.JAVA_EDGE+"|0|4|"))
        for changed in (
            "\n".join(rows[:header]+rows[header+1:]),
            transcript+"\n"+rows[-1],
            "\n".join(rows[:first_edge]+rows[first_edge+1:]),
            "\n".join(rows[:first_edge]+[rows[first_edge]]+
                      rows[first_edge:]),
            transcript.replace("|0|15|1|","|0|15|4|",1),
            transcript.replace("|0|11|finalDensity|11",
                               "|0|11|wrongRoot|11",1),
            transcript.replace("|0|11|0|net.minecraft.world.level.levelgen."
                               "DensityFunctions$Ap2",
                               "|0|11|0|net.minecraft.world.level.levelgen."
                               "DensityFunctions$Noise",1),
        ):
            with self.subTest(length=len(changed)):
                with self.assertRaises(graph.RouterGraphError):
                    graph.parse_output(changed,original)

    def test_real_frozen_fixture_rejects_modified_original_and_malformed_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            fake=Path(folder)/"roots.json"
            fake.write_text(json.dumps(self.original()))
            with self.assertRaisesRegex(graph.RouterGraphError,"SHA"):
                graph.load_original_roots(fake)

    def test_no_copyrighted_source_or_production_authority_in_manifest(self):
        original=self.original()
        methods={
            "router_map_all":{"owner":graph.roots.ROUTER,"signature":"mapAll(Visitor)",
                              "body_sha256":graph.roots.ROUTER_MAP_ALL_SHA256,
                              "normalized_sha256":"a"*64,"reviewed":False},
            "random_state_router":{"owner":graph.roots.STATE,"signature":"router()",
                                   "body_sha256":"b"*64,
                                   "normalized_sha256":"c"*64,"reviewed":False},
        }
        manifest={
            "schema":1,"kind":graph.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":graph.frozen.SOURCE_SHA256,
            "official_server_sha256":graph.frozen.SERVER_SHA256,
            "original_router_roots_sha256":graph.ORIGINAL_ROOT_SHA256,
            "root_signature_fixture_sha256":graph.ROOT_FIXTURE_SHA256,
            "original_stock_noise_fixture_sha256":graph.frozen.FIXTURE_SHA256,
            "source_methods":methods,"world_seeds":list(graph.roots.SEEDS),
            "maximum_graph_depth":graph.GRAPH_DEPTH,
            "maximum_bound_nodes_per_seed":graph.MAX_NODES,
            "stock_registry_used":True,"world_seed_random_state_observed":True,
            "world_seed_random_state_bound":False,
            "source_text_included":False,"full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "production_worldgen_enabled":False,
            "graphs":graph.parse_output(self.records(),original),
        }
        graph.validate(manifest,original,methods)
        for key in ("world_seed_random_state_bound","source_text_included",
                    "full_router_graph_qualified","router_numeric_parity_qualified",
                    "independent_var_sem_admitted","production_worldgen_enabled"):
            changed=copy.deepcopy(manifest)
            changed[key]=True
            with self.subTest(key=key),self.assertRaises(graph.RouterGraphError):
                graph.validate(changed,original,methods)
        mutated=copy.deepcopy(manifest)
        mutated["graphs"][0]["nodes"][11]["density_children"][0]["slot"]="wrong"
        with self.assertRaises(graph.RouterGraphError):
            graph.validate(mutated,original,methods)


if __name__=="__main__":
    unittest.main()
