"""Fail-closed 26.2 real HolderHolder binding inventory contracts."""
from __future__ import annotations

import copy
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_router_holder_capture as holder  # noqa: E402


class StockHolderEvidenceTests(unittest.TestCase):
    def setup_fakes(self):
        original={"bound_router_roots":[]}
        previous={"graphs":[]}
        lines=["stock server bootstrap stdout ignored"]
        for seed_i,seed in enumerate(holder.roots.SEEDS):
            fields=[]
            nodes=[]
            roots=[]
            for i in range(15):
                label="root%02d"%i
                kind="HolderHolder" if i==6 else "Constant"
                cls="net.minecraft.world.level.levelgen.DensityFunctions$"+kind
                fields.append({
                    "field":label,"implementation_class":cls,
                    "compute_declaring_class":cls,
                    "first_level_density_children":[],
                })
                roots.append({"field":label,"node_id":i})
                nodes.append({
                    "node_id":i,"depth":0,"implementation_class":cls,
                    "compute_declaring_class":cls,
                    "record_components_inspected":True,
                    "density_children":[],
                    "opaque_components":([{
                        "slot_index":0,"slot":"function",
                        "declared_class":"net.minecraft.core.Holder",
                    }] if i==6 else []),
                })
            original["bound_router_roots"].append({"fields":fields,"world_seed_bits":seed})
            previous["graphs"].append({
                "world_seed_bits":seed,"roots":roots,"nodes":nodes,
                "density_edges":0,"opaque_record_slots":1,
            })
            lines.append(holder.graph.JAVA_HEAD+
                         f"|{seed_i}|15|{holder.roots.ROUTER}")
            for i in range(15):
                lines.append(holder.graph.JAVA_ROOT+f"|{seed_i}|{i}|root{i:02d}|{i}")
            for i,node in enumerate(nodes):
                lines.append(holder.graph.JAVA_NODE+
                             f"|{seed_i}|{i}|0|{node['implementation_class']}|"
                             f"{node['compute_declaring_class']}|1|0|{1 if i==6 else 0}")
                if i==6:
                    lines.append(holder.graph.JAVA_OPAQUE+
                                 f"|{seed_i}|6|0|function|net.minecraft.core.Holder")
                    lines.append(holder.TAG+f"|{seed_i}|6|0|"
                                 "net.minecraft.core.Holder$Reference|"
                                 "net.minecraft.world.level.levelgen.DensityFunctions$Noise|"
                                 "net.minecraft.world.level.levelgen.DensityFunctions$Noise")
            lines.append(holder.graph.JAVA_END+f"|{seed_i}|15|0|1")
            lines.append(holder.END+f"|{seed_i}|1|15")
        return original,previous,lines

    def methods(self):
        return {
            "router_map_all":{
                "owner":holder.roots.ROUTER,"signature":"mapAll(Visitor)",
                "body_sha256":holder.roots.ROUTER_MAP_ALL_SHA256,
                "normalized_sha256":"a"*64,"reviewed":False,
            },
            "random_state_router":{
                "owner":holder.roots.STATE,"signature":"router()",
                "body_sha256":"b"*64,"normalized_sha256":"c"*64,
                "reviewed":False,
            },
            "holder_holder_compute":{
                "owner":holder.OWNER,"signature":"compute(FunctionContext)",
                "body_sha256":"d"*64,"normalized_sha256":"e"*64,
                "reviewed":False,
            },
        }

    def manifest(self,bindings):
        return {
            "schema":1,"kind":holder.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":holder.frozen.SOURCE_SHA256,
            "official_server_sha256":holder.frozen.SERVER_SHA256,
            "original_router_roots_sha256":holder.graph.ORIGINAL_ROOT_SHA256,
            "original_router_graph_sha256":holder.ORIGINAL_GRAPH_SHA256,
            "source_methods":self.methods(),"world_seeds":list(holder.roots.SEEDS),
            "world_seed_random_state_observed":True,
            "world_seed_random_state_bound":False,
            "source_text_included":False,
            "independent_var_sem_admitted":False,
            "router_numeric_parity_qualified":False,
            "full_router_graph_qualified":False,
            "production_worldgen_enabled":False,
            "holder_bindings":bindings,
        }

    def test_original_graph_is_preserved_and_only_holder_value_binding_reported(self):
        original,previous,lines=self.setup_fakes()
        actual=holder.parse_output("\n".join(lines),previous,original)
        self.assertEqual(len(actual),4)
        self.assertEqual([len(g["observed_bound_holders"]) for g in actual],[1]*4)
        self.assertTrue(all(group["observed_bound_holders"][0]["node_id"]==6
                            for group in actual))
        holder.validate(self.manifest(actual),previous,self.methods())

    def test_malformed_duplicate_missing_unbound_and_changed_graph_rejected(self):
        original,previous,lines=self.setup_fakes()
        h=next(i for i,l in enumerate(lines) if l.startswith(holder.TAG+"|0|"))
        failures=(
            lines[:h]+lines[h+1:],
            lines[:h]+[lines[h]]+lines[h:],
            [x.replace("|0|6|0|net.minecraft.core.Holder$Reference",
                       "|0|7|0|net.minecraft.core.Holder$Reference")
             if x.startswith(holder.TAG) else x for x in lines],
            lines[:-1],
            lines+[lines[-1]],
            [x.replace("DensityFunctions$Constant","DensityFunctions$Noise")
             if x.startswith(holder.graph.JAVA_NODE+"|0|2|") else x
             for x in lines],
            [x.replace("DensityFunctions$Noise|","java.lang.Object|")
             if x.startswith(holder.TAG+"|0|") else x for x in lines],
        )
        for changed in failures:
            with self.subTest(lines=len(changed)):
                with self.assertRaises((holder.HolderEvidenceError,
                                        holder.graph.RouterGraphError)):
                    holder.parse_output("\n".join(changed),previous,original)

    def test_closed_gates_and_source_receipt_never_promoted(self):
        original,previous,lines=self.setup_fakes()
        evidence=holder.parse_output("\n".join(lines),previous,original)
        template=self.manifest(evidence)
        for flag in ("world_seed_random_state_bound","source_text_included",
                     "independent_var_sem_admitted","router_numeric_parity_qualified",
                     "full_router_graph_qualified","production_worldgen_enabled"):
            mutated=copy.deepcopy(template);mutated[flag]=True
            with self.subTest(flag=flag),self.assertRaises(holder.HolderEvidenceError):
                holder.validate(mutated,previous,self.methods())
        changed=copy.deepcopy(template)
        changed["holder_bindings"][0]["observed_bound_holders"][0]["source_reviewed"]=True
        with self.assertRaises(holder.HolderEvidenceError):
            holder.validate(changed,previous,self.methods())
        changed=copy.deepcopy(template)
        changed["holder_bindings"][0]["observed_bound_holders"][0]["node_id"]=7
        with self.assertRaises(holder.HolderEvidenceError):
            holder.validate(changed,previous,self.methods())

    def test_original_graph_must_have_byte_identical_pinned_receipt(self):
        with tempfile.TemporaryDirectory() as work:
            f=Path(work)/"not-original.json"
            f.write_text(json.dumps(self.setup_fakes()[1]))
            with self.assertRaisesRegex(holder.HolderEvidenceError,"SHA"):
                holder.load_graph(f,self.setup_fakes()[0])

    def test_indexed_holder_compute_is_not_claimed_as_source_reviewed(self):
        conn=sqlite3.connect(":memory:")
        conn.row_factory=sqlite3.Row
        conn.executescript("""
        CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
        CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,
            name TEXT,signature TEXT,param_count INTEGER,
            body_sha256 TEXT,normalized_sha256 TEXT);
        INSERT INTO types VALUES(1,'net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder');
        INSERT INTO methods VALUES(1,1,'compute','compute(FunctionContext)',1,
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb');
        """)
        result=holder.source_holder_compute(conn)
        self.assertEqual(result["body_sha256"],"a"*64)
        self.assertFalse(result["reviewed"])
        conn.execute("DELETE FROM methods")
        with self.assertRaises(holder.HolderEvidenceError):
            holder.source_holder_compute(conn)
        conn.close()


if __name__=="__main__":
    unittest.main()
