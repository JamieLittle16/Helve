#!/usr/bin/env python3
"""Four-seed source-pinned stock 26.2 bounded density-record graph inventory.

Actual JVM builds the authentic registry/RandomState/Overworld router; this
tool records identity-aware typed DensityFunction record links to depth 4.
Everything else remains OPAQUE, including holders, splines, cache contexts,
parameters and unknown nonrecord nodes. No density value is computed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
from pathlib import Path

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import vanilla_atlas
import worldgen_26_2_density_primitive_capture as primitive
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_stock_router_roots_capture as roots
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_ROOT_SHA256 = "81cc1fb15388998f9b812803ee96a30c792ef68df8120490b05f38acd3338736"
ROOT_FIXTURE = ROOT / "vanilla/reports/worldgen-26_2-stock-router-roots-15-observed.tsv"
ROOT_FIXTURE_SHA256 = "27187403bfcccea13370f3d1d218a58d243a98c194684f71bc6f1c5fbe824dd1"
KIND = "official_26_2_stock_bound_density_record_graph_depth4"
GRAPH_DEPTH = 4
MAX_NODES = 384
MAX_ROWS = 18_000
JAVA_HEAD = "HELVE26_2_ROUTER_GRAPH_HEAD"
JAVA_ROOT = "HELVE26_2_ROUTER_GRAPH_ROOT"
JAVA_NODE = "HELVE26_2_ROUTER_GRAPH_NODE"
JAVA_EDGE = "HELVE26_2_ROUTER_GRAPH_EDGE"
JAVA_OPAQUE = "HELVE26_2_ROUTER_GRAPH_OPAQUE"
JAVA_END = "HELVE26_2_ROUTER_GRAPH_END"
TAGS = frozenset((JAVA_HEAD,JAVA_ROOT,JAVA_NODE,JAVA_EDGE,JAVA_OPAQUE,JAVA_END))
DENSITY_CLASS = re.compile(r"net\.minecraft\.world\.level\.levelgen\.DensityFunctions\$[A-Za-z_$][\w$]*\Z")
OPAQUE_CLASS = re.compile(r"[A-Za-z_$][A-Za-z0-9_.$]*(?:\[\])*\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")


class RouterGraphError(ValueError):
    """Original 26.2 router source/shape/bounds/oracle remains unqualified."""


def root_signature(group: list[dict]) -> bytes:
    lines = []
    for field in group:
        children = field["first_level_density_children"]
        row = "\t".join((
            field["field"],field["implementation_class"],
            field["compute_declaring_class"],
            ";".join(child["slot"]+":"+child["implementation_class"]
                     for child in children),
        ))
        lines.append(row)
    return ("\n".join(lines)+"\n").encode("ascii")


def load_original_roots(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw)!=28439 or hashlib.sha256(raw).hexdigest()!=ORIGINAL_ROOT_SHA256:
        raise RouterGraphError("original official four-seed root JSON length/SHA changed")
    try:
        original=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise RouterGraphError("invalid source-free original root JSON") from exc
    if not isinstance(original,dict):
        raise RouterGraphError("invalid root evidence object")
    fixture = ROOT_FIXTURE.read_bytes()
    if hashlib.sha256(fixture).hexdigest()!=ROOT_FIXTURE_SHA256:
        raise RouterGraphError("15-root observed frozen signature changed")
    methods=original.get("source_methods")
    if not isinstance(methods,dict):
        raise RouterGraphError("original source method pin inventory missing")
    try:
        roots.validate(original,methods=methods)
    except (roots.RouterRootsError,TypeError,KeyError) as exc:
        raise RouterGraphError("original four-seed router roots rejected") from exc
    for group in original["bound_router_roots"]:
        if root_signature(group["fields"])!=fixture:
            raise RouterGraphError("stock root signature differs from fixed actual JVM snapshot")
    return original


def index(raw: str) -> int:
    if not raw.isascii() or not raw.isdecimal() or str(int(raw))!=raw:
        raise RouterGraphError("noncanonical graph index")
    value=int(raw)
    if value>100_000:
        raise RouterGraphError("out-of-range graph index")
    return value


def parse_output(stdout: str, original: dict) -> list[dict]:
    if not isinstance(stdout,str) or len(stdout)>2_000_000:
        raise RouterGraphError("unbounded stock JVM graph stdout")
    lines=stdout.splitlines()
    for line in lines:
        if line.startswith(roots.TAG_FAILURE):
            parts=line.split("|")
            if len(parts)!=5 or any(len(x)>520 for x in parts):
                raise RouterGraphError("invalid official JVM graph failure frame")
            raise RouterGraphError("JVM PHASE: "+parts[1]+"; ROOT: "+parts[2]+
                                   "; CAUSE: "+parts[4])
    rows=[line.split("|") for line in lines if line.split("|",1)[0] in TAGS]
    if len(rows)>MAX_ROWS:
        raise RouterGraphError("unbounded stock density-record graph rows")
    cursor=0
    result=[]
    for seed_index,expected_seed in enumerate(original["bound_router_roots"]):
        if cursor>=len(rows) or rows[cursor] != [
            JAVA_HEAD,str(seed_index),str(roots.N_FIELDS),roots.ROUTER,
        ]:
            raise RouterGraphError("missing or reordered stock graph header")
        cursor+=1
        observed_roots=[]
        for root_i,field in enumerate(expected_seed["fields"]):
            if cursor>=len(rows):
                raise RouterGraphError("missing stock graph root")
            row=rows[cursor];cursor+=1
            if len(row)!=5 or row[:3] != [JAVA_ROOT,str(seed_index),str(root_i)] \
               or row[3]!=field["field"]:
                raise RouterGraphError("incorrect or reordered stock bound graph root")
            observed_roots.append({"field":row[3],"node_id":index(row[4])})
        nodes=[]
        total_edges=0
        total_opaque=0
        while cursor<len(rows) and rows[cursor][0]==JAVA_NODE:
            row=rows[cursor];cursor+=1
            if len(row)!=9 or row[1]!=str(seed_index) or index(row[2])!=len(nodes):
                raise RouterGraphError("noncanonical sequential stock graph node")
            node_id=len(nodes)
            depth=index(row[3])
            if depth>GRAPH_DEPTH or not DENSITY_CLASS.fullmatch(row[4]) \
               or not DENSITY_CLASS.fullmatch(row[5]) \
               or row[6] not in ("0","1") or (row[6]=="1")!=(depth<GRAPH_DEPTH):
                raise RouterGraphError("unapproved graph depth, delegate or traversal status")
            child_count=index(row[7]); opaque_count=index(row[8])
            if child_count+opaque_count>32 or child_count>32 or opaque_count>32:
                raise RouterGraphError("unbounded stock node record fields")
            slots=set()
            children=[]
            opaques=[]
            for n in range(child_count):
                if cursor>=len(rows):
                    raise RouterGraphError("missing graph edge")
                edge=rows[cursor];cursor+=1
                if len(edge)!=6 or edge[:3]!=[JAVA_EDGE,str(seed_index),str(node_id)]:
                    raise RouterGraphError("malformed/reordered graph density edge")
                slot=index(edge[3])
                if slot>=32 or slot in slots or not roots.FIELD_NAME.fullmatch(edge[4]):
                    raise RouterGraphError("invalid or repeated typed density child slot")
                slots.add(slot)
                children.append({"slot_index":slot,"slot":edge[4],
                                 "child_id":index(edge[5])})
            for n in range(opaque_count):
                if cursor>=len(rows):
                    raise RouterGraphError("missing graph opaque boundary")
                opaque=rows[cursor];cursor+=1
                if len(opaque)!=6 or opaque[:3]!=[JAVA_OPAQUE,str(seed_index),str(node_id)]:
                    raise RouterGraphError("malformed/reordered graph opaque component")
                slot=index(opaque[3])
                if slot>=32 or slot in slots or not roots.FIELD_NAME.fullmatch(opaque[4]) \
                   or not OPAQUE_CLASS.fullmatch(opaque[5]):
                    raise RouterGraphError("invalid/repeated opaque record component")
                slots.add(slot)
                opaques.append({"slot_index":slot,"slot":opaque[4],
                                "declared_class":opaque[5]})
            if sorted(slots)!=list(range(child_count+opaque_count)):
                raise RouterGraphError("missing, repeated or invalid record component ordering")
            if not (depth<GRAPH_DEPTH) and slots:
                raise RouterGraphError("cut-off node falsely reports inspected components")
            nodes.append({
                "node_id":node_id,"depth":depth,"implementation_class":row[4],
                "compute_declaring_class":row[5],
                "record_components_inspected":depth<GRAPH_DEPTH,
                "density_children":children,"opaque_components":opaques,
            })
            total_edges+=child_count
            total_opaque+=opaque_count
            if len(nodes)>MAX_NODES or total_edges>4096 or total_opaque>4096:
                raise RouterGraphError("bound graph exceeds maximum node/edge counts")
        if cursor>=len(rows):
            raise RouterGraphError("missing stock graph END frame")
        end=rows[cursor];cursor+=1
        if len(end)!=5 or end[:2]!=[JAVA_END,str(seed_index)] or \
           [index(x) for x in end[2:]] != [len(nodes),total_edges,total_opaque]:
            raise RouterGraphError("incorrect bounded graph checksum or END frame")
        for bound,expected in zip(observed_roots,expected_seed["fields"],strict=True):
            if bound["node_id"]>=len(nodes):
                raise RouterGraphError("unresolved stock graph root id")
            node=nodes[bound["node_id"]]
            if node["depth"]!=0 or node["implementation_class"]!=expected["implementation_class"] \
               or node["compute_declaring_class"]!=expected["compute_declaring_class"]:
                raise RouterGraphError("genuine root disagrees with prior real JVM class")
            actual_children=[(ch["slot"],nodes[ch["child_id"]]["implementation_class"])
                             for ch in node["density_children"]
                             if ch["child_id"]<len(nodes)]
            anticipated=[(ch["slot"],ch["implementation_class"])
                         for ch in expected["first_level_density_children"]]
            if actual_children!=anticipated:
                raise RouterGraphError("first-level bound child differs from official frozen roots")
        for node in nodes:
            for edge in node["density_children"]:
                child_id=edge["child_id"]
                if child_id>=len(nodes) or nodes[child_id]["depth"]>node["depth"]+1:
                    raise RouterGraphError("unresolved or depth-impossible graph edge")
        result.append({
            "world_seed_bits":expected_seed["world_seed_bits"],
            "roots":observed_roots,"nodes":nodes,
            "density_edges":total_edges,"opaque_record_slots":total_opaque,
        })
    if cursor!=len(rows):
        raise RouterGraphError("extra/duplicate stock graph records after four seeds")
    return result


def observe(server: Path, original: dict, *, timeout: int=240) -> list[dict]:
    if not roots.JAVA_SOURCE.is_file() or not roots.BASE_BRIDGE.is_file():
        raise RouterGraphError("source-free stock router reflection bridge missing")
    with tempfile.TemporaryDirectory(prefix="helve-262-router-graph-") as folder:
        work=Path(folder)
        jars=official.extract_classpath(server,work/"classpath")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(roots.BASE_BRIDGE),str(roots.JAVA_SOURCE)],
            text=True,capture_output=True,check=False,timeout=timeout,
        )
        if build.returncode:
            raise RouterGraphError("stock router graph Java bridge compilation failed: "+
                                   build.stderr[:1500])
        result=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join([str(work),*(str(jar) for jar in jars)]),
             "HelveStockNoiseRouterRoots262","--router-graph-4"],
            input="\n".join(roots.SEEDS)+"\n",text=True,capture_output=True,
            check=False,timeout=timeout,
        )
        if result.returncode:
            try:
                parse_output(result.stdout,original)
            except RouterGraphError as exc:
                raise RouterGraphError(str(exc)) from exc
            raise RouterGraphError("official stock graph JVM failed: "+
                                   stock.java_failure_detail(result.stderr))
        return parse_output(result.stdout,original)


def validate(manifest: dict, original: dict, methods: dict) -> None:
    expected={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":frozen.SOURCE_SHA256,
        "official_server_sha256":frozen.SERVER_SHA256,
        "original_router_roots_sha256":ORIGINAL_ROOT_SHA256,
        "root_signature_fixture_sha256":ROOT_FIXTURE_SHA256,
        "original_stock_noise_fixture_sha256":frozen.FIXTURE_SHA256,
        "source_methods":methods,
        "world_seeds":list(roots.SEEDS),
        "maximum_graph_depth":GRAPH_DEPTH,
        "maximum_bound_nodes_per_seed":MAX_NODES,
        "stock_registry_used":True,
        "world_seed_random_state_observed":True,
        "world_seed_random_state_bound":False,
        "source_text_included":False,
        "full_router_graph_qualified":False,
        "router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(expected)|{"graphs"}:
        raise RouterGraphError("changed bounded graph manifest schema")
    for name,value in expected.items():
        if type(manifest.get(name)) is not type(value) or manifest[name]!=value:
            raise RouterGraphError("changed graph manifest source identity or CLOSED gate: "+name)
    graphs=manifest["graphs"]
    if not isinstance(graphs,list) or len(graphs)!=4:
        raise RouterGraphError("missing four seed-specific graph results")
    for seed_index,group in enumerate(graphs):
        if not isinstance(group,dict) or set(group)!={
            "world_seed_bits","roots","nodes","density_edges","opaque_record_slots"
        } or group["world_seed_bits"]!=roots.SEEDS[seed_index]:
            raise RouterGraphError("missing or reordered stock graph seed")
        if not isinstance(group["nodes"],list) or len(group["nodes"])>MAX_NODES:
            raise RouterGraphError("incorrect graph node count")
        if not isinstance(group["roots"],list) or len(group["roots"])!=15:
            raise RouterGraphError("incorrect original fifteen root count")
        if group["density_edges"]!=sum(len(n["density_children"]) for n in group["nodes"]) \
           or group["opaque_record_slots"]!=sum(
               len(n["opaque_components"]) for n in group["nodes"]):
            raise RouterGraphError("graph edge/opaque totals changed")
        for root_i,root in enumerate(group["roots"]):
            if not isinstance(root,dict) or set(root)!={"field","node_id"} \
               or root["field"]!=original["bound_router_roots"][seed_index]["fields"][root_i]["field"] \
               or type(root["node_id"]) is not int or not (0<=root["node_id"]<len(group["nodes"])):
                raise RouterGraphError("incorrect root index or field name")
        for node_i,node in enumerate(group["nodes"]):
            if not isinstance(node,dict) or set(node)!={
                "node_id","depth","implementation_class","compute_declaring_class",
                "record_components_inspected","density_children","opaque_components"
            } or type(node["node_id"]) is not int or node["node_id"]!=node_i \
               or type(node["depth"]) is not int or not (0<=node["depth"]<=GRAPH_DEPTH) \
               or type(node["record_components_inspected"]) is not bool \
               or node["record_components_inspected"]!=(node["depth"]<GRAPH_DEPTH) \
               or not isinstance(node["implementation_class"],str) \
               or not DENSITY_CLASS.fullmatch(node["implementation_class"]) \
               or not isinstance(node["compute_declaring_class"],str) \
               or not DENSITY_CLASS.fullmatch(node["compute_declaring_class"]) \
               or not isinstance(node["density_children"],list) \
               or not isinstance(node["opaque_components"],list):
                raise RouterGraphError("unqualified bounded graph node")
            combined=[]
            for child in node["density_children"]:
                if not isinstance(child,dict) or set(child)!={"slot_index","slot","child_id"} \
                   or type(child["slot_index"]) is not int or type(child["child_id"]) is not int \
                   or not isinstance(child["slot"],str) or not roots.FIELD_NAME.fullmatch(child["slot"]) \
                   or not (0<=child["child_id"]<len(group["nodes"])) \
                   or group["nodes"][child["child_id"]]["depth"]>node["depth"]+1:
                    raise RouterGraphError("bad bounded graph density link")
                combined.append((child["slot_index"],child["slot"]))
            for opaque in node["opaque_components"]:
                if not isinstance(opaque,dict) or set(opaque)!={"slot_index","slot","declared_class"} \
                   or type(opaque["slot_index"]) is not int or not isinstance(opaque["slot"],str) \
                   or not roots.FIELD_NAME.fullmatch(opaque["slot"]) \
                   or not isinstance(opaque["declared_class"],str) \
                   or not OPAQUE_CLASS.fullmatch(opaque["declared_class"]):
                    raise RouterGraphError("bad bounded graph opaque declaration")
                combined.append((opaque["slot_index"],opaque["slot"]))
            if len(combined)>32 or len(set(combined))!=len(combined) \
               or len({slot for slot,_ in combined})!=len(combined) \
               or sorted(slot for slot,_ in combined)!=list(range(len(combined))) \
               or (node["depth"]==GRAPH_DEPTH and combined):
                raise RouterGraphError("noncanonical bounded graph record components")
        for root,expected_field in zip(group["roots"],
                                       original["bound_router_roots"][seed_index]["fields"],
                                       strict=True):
            node=group["nodes"][root["node_id"]]
            if node["depth"]!=0 or node["implementation_class"]!=expected_field["implementation_class"] \
               or node["compute_declaring_class"]!=expected_field["compute_declaring_class"]:
                raise RouterGraphError("stock graph changed original root identity")
            actual=[(c["slot"],group["nodes"][c["child_id"]]["implementation_class"])
                    for c in node["density_children"]]
            anticipated=[(c["slot"],c["implementation_class"])
                         for c in expected_field["first_level_density_children"]]
            if actual!=anticipated:
                raise RouterGraphError("stock graph changed frozen first-level density edges")


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, old_roots: Path, output: Path) -> dict:
    destination=improved.external_output(output)
    original=load_original_roots(old_roots)
    with lock.open("rb") as file:
        pin=tomllib.load(file)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=("26.2",776,4903):
        raise RouterGraphError("not the official locked 26.2 source")
    stock.reference_frontier(frontier,pin)
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        methods=roots.source_methods(conn)
    finally:
        conn.close()
    server_sha=official.sha256_file(server)
    if source_sha!=frozen.SOURCE_SHA256 or server_sha!=frozen.SERVER_SHA256 \
       or server_sha!=pin["runtime"]["server_sha256"] \
       or methods!=original["source_methods"]:
        raise RouterGraphError("bound router source/JVM or original indexed methods changed")
    graphs=observe(server,original)
    manifest={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "original_router_roots_sha256":ORIGINAL_ROOT_SHA256,
        "root_signature_fixture_sha256":ROOT_FIXTURE_SHA256,
        "original_stock_noise_fixture_sha256":frozen.FIXTURE_SHA256,
        "source_methods":methods,"world_seeds":list(roots.SEEDS),
        "maximum_graph_depth":GRAPH_DEPTH,"maximum_bound_nodes_per_seed":MAX_NODES,
        "stock_registry_used":True,"world_seed_random_state_observed":True,
        "world_seed_random_state_bound":False,
        "source_text_included":False,"full_router_graph_qualified":False,
        "router_numeric_parity_qualified":False,"independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
        "graphs":graphs,
    }
    validate(manifest,original,methods)
    payload=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>2_000_000:
        raise RouterGraphError("unbounded source-free graph manifest size")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as file:
        file.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "observed_bound_nodes":sum(len(g["nodes"]) for g in graphs),
        "observed_bound_density_edges":sum(g["density_edges"] for g in graphs),
        "opaque_record_components":sum(g["opaque_record_slots"] for g in graphs),
        "router_numeric_parity_qualified":False,
        "production_worldgen_enabled":False,
    }


def main(argv: list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=primitive.SOURCE)
    parser.add_argument("--db",type=Path,default=primitive.DB)
    parser.add_argument("--lock",type=Path,default=primitive.LOCK)
    parser.add_argument("--cache",type=Path,default=primitive.CACHE)
    parser.add_argument("--server-jar",type=Path)
    parser.add_argument("--frontier",type=Path,default=stock.FRONTIER)
    parser.add_argument("--roots",type=Path,required=True,
                        help="the exact prior official four-seed router root JSON")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,server=server,
                                 frontier=args.frontier,old_roots=args.roots,
                                 output=args.output),sort_keys=True))
    except (RouterGraphError,roots.RouterRootsError,improved.CaptureError,
            OSError,ValueError,KeyError,TypeError,sqlite3.Error,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 BOUND ROUTER GRAPH UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
