#!/usr/bin/env python3
"""Bounded actual stock 26.2 HolderHolder.value() identity inspection.

Follows only exactly-typed HolderHolder.function -> public Holder.value()
in the four already-validated stock Overworld bound density graphs. This is
READ-ONLY reflective evidence, not permission to compile or evaluate holders.
The original graph and all first-level node edges must remain identical.
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
import worldgen_26_2_stock_router_graph_capture as graph
import worldgen_26_2_stock_router_roots_capture as roots
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

KIND="official_26_2_stock_density_holder_value_binding_frontier"
ORIGINAL_GRAPH_BYTES=141287
ORIGINAL_GRAPH_SHA256="5911470e36725da99e7b82b5b8b4eef03a1d150662aa44c71b6c64340e4a46fb"
HOLDER="net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder"
OWNER="net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder"
TAG="HELVE26_2_ROUTER_HOLDER"
END="HELVE26_2_ROUTER_HOLDER_END"
MAX_HOLDERS=64
CLASS=re.compile(r"net\.minecraft(?:\.[a-zA-Z_$][\w$]*)+\Z")
SHA=re.compile(r"[0-9a-f]{64}\Z")


class HolderEvidenceError(ValueError):
    """Actual 26.2 holder binding evidence is not qualified."""


def load_graph(path: Path, original_roots: dict) -> dict:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_GRAPH_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_GRAPH_SHA256:
        raise HolderEvidenceError("exact previous official graph bytes/SHA required")
    try:
        previous=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise HolderEvidenceError("invalid previous source-free graph") from exc
    if not isinstance(previous,dict) or not isinstance(previous.get("source_methods"),dict):
        raise HolderEvidenceError("missing prior source method inventory")
    graph.validate(previous,original_roots,previous["source_methods"])
    return previous


def source_holder_compute(conn: sqlite3.Connection) -> dict:
    rows=conn.execute(
        "SELECT m.id,m.signature FROM methods m JOIN types t ON m.type_id=t.id "
        "WHERE t.qualified_name=? AND m.name=? AND m.param_count=?",
        (OWNER,"compute",1),
    ).fetchall()
    if len(rows)!=1:
        raise HolderEvidenceError("missing/ambiguous original HolderHolder.compute source method")
    row=rows[0]
    digests=conn.execute(
        "SELECT body_sha256,normalized_sha256 FROM methods WHERE id=?",
        (row["id"],),
    ).fetchone()
    if digests is None or not all(isinstance(v,str) and SHA.fullmatch(v)
                                   for v in digests):
        raise HolderEvidenceError("missing HolderHolder.compute body fingerprint")
    return {
        "owner":OWNER,"signature":row["signature"],
        "body_sha256":digests[0],"normalized_sha256":digests[1],
        "reviewed":False,
    }


def expected_holders(previous: dict, seed_index: int) -> list[dict]:
    nodes=previous["graphs"][seed_index]["nodes"]
    holders=[node for node in nodes if node["implementation_class"]==HOLDER]
    if not holders or len(holders)>MAX_HOLDERS:
        raise HolderEvidenceError("missing or unbounded real stock HolderHolder nodes")
    for node in holders:
        if node["depth"]==graph.GRAPH_DEPTH or node["density_children"] or \
           node["opaque_components"]!=[{
               "slot_index":0,"slot":"function","declared_class":"net.minecraft.core.Holder"
           }]:
            raise HolderEvidenceError("unqualified original HolderHolder field contract")
    return holders


def parse_output(stdout: str, previous: dict, original_roots: dict) -> list[dict]:
    if not isinstance(stdout,str) or len(stdout)>2_000_000:
        raise HolderEvidenceError("unbounded original stock JVM holder output")
    for line in stdout.splitlines():
        if line.startswith(roots.TAG_FAILURE):
            parts=line.split("|")
            if len(parts)!=5:
                raise HolderEvidenceError("malformed original JVM failure frame")
            raise HolderEvidenceError("JVM PHASE: "+parts[1]+
                                      "; ROOT: "+parts[2]+"; CAUSE: "+parts[4])
    # Verify the Java holder mode did not change any previously observed
    # node, sharing edge, cut-off or opaque component declaration.
    observed_graph=graph.parse_output(stdout,original_roots)
    if observed_graph!=previous["graphs"]:
        raise HolderEvidenceError("Holder binding mode altered real graph structure")
    rows=[line.split("|") for line in stdout.splitlines()
          if line.split("|",1)[0] in (TAG,END)]
    result=[]
    cursor=0
    for i in range(4):
        expected=expected_holders(previous,i)
        bound=[]
        for node in expected:
            if cursor>=len(rows):
                raise HolderEvidenceError("missing real HolderHolder binding")
            line=rows[cursor];cursor+=1
            if len(line)!=7 or line[0]!=TAG or line[1]!=str(i) \
               or line[2]!=str(node["node_id"]) or line[3]!=str(node["depth"]) \
               or not CLASS.fullmatch(line[4]) \
               or not graph.DENSITY_CLASS.fullmatch(line[5]) \
               or not graph.DENSITY_CLASS.fullmatch(line[6]):
                raise HolderEvidenceError("wrong order, context or class in bound holder")
            bound.append({
                "node_id":node["node_id"],"depth":node["depth"],
                "holder_implementation_class":line[4],
                "bound_density_implementation_class":line[5],
                "bound_compute_declaring_class":line[6],
                "source_reviewed":False,
            })
        if cursor>=len(rows) or rows[cursor] != [
            END,str(i),str(len(bound)),str(len(previous["graphs"][i]["nodes"])),
        ]:
            raise HolderEvidenceError("missing/wrong bounded Holder END")
        cursor+=1
        result.append({
            "world_seed_bits":roots.SEEDS[i],
            "observed_bound_holders":bound,
        })
    if cursor!=len(rows):
        raise HolderEvidenceError("duplicate or unexpected stock Holder records")
    return result


def observe(server:Path, previous:dict, original_roots:dict, *,
            timeout:int=240) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="helve-262-actual-holder-") as folder:
        work=Path(folder)
        jars=official.extract_classpath(server,work/"classpath")
        compiled=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(roots.BASE_BRIDGE),str(roots.JAVA_SOURCE)],
            text=True,capture_output=True,check=False,timeout=timeout,
        )
        if compiled.returncode:
            raise HolderEvidenceError("original Holder JVM bridge did not compile: "+
                                      compiled.stderr[:1200])
        run=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join([str(work),*(str(jar) for jar in jars)]),
             "HelveStockNoiseRouterRoots262","--router-holder-4"],
            input="\n".join(roots.SEEDS)+"\n",text=True,capture_output=True,
            check=False,timeout=timeout,
        )
        if run.returncode:
            try:
                parse_output(run.stdout,previous,original_roots)
            except HolderEvidenceError as exc:
                raise HolderEvidenceError(str(exc)) from exc
            raise HolderEvidenceError("stock JVM holder probe failed: "+
                                      stock.java_failure_detail(run.stderr))
        return parse_output(run.stdout,previous,original_roots)


def validate(manifest:dict, previous:dict, source_methods:dict) -> None:
    expected={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":frozen.SOURCE_SHA256,
        "official_server_sha256":frozen.SERVER_SHA256,
        "original_router_roots_sha256":graph.ORIGINAL_ROOT_SHA256,
        "original_router_graph_sha256":ORIGINAL_GRAPH_SHA256,
        "source_methods":source_methods,
        "world_seeds":list(roots.SEEDS),
        "world_seed_random_state_observed":True,
        "world_seed_random_state_bound":False,
        "source_text_included":False,
        "independent_var_sem_admitted":False,
        "router_numeric_parity_qualified":False,
        "full_router_graph_qualified":False,
        "production_worldgen_enabled":False,
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(expected)|{"holder_bindings"}:
        raise HolderEvidenceError("invalid source-free holder manifest schema")
    for k,v in expected.items():
        if type(manifest.get(k)) is not type(v) or manifest[k]!=v:
            raise HolderEvidenceError("changed bound holder evidence / CLOSED gate: "+k)
    groups=manifest["holder_bindings"]
    if not isinstance(groups,list) or len(groups)!=4:
        raise HolderEvidenceError("expected precisely four bound-holder groups")
    for i,group in enumerate(groups):
        expected_nodes=expected_holders(previous,i)
        if not isinstance(group,dict) or set(group)!={"world_seed_bits","observed_bound_holders"} \
           or group["world_seed_bits"]!=roots.SEEDS[i] \
           or not isinstance(group["observed_bound_holders"],list) \
           or len(group["observed_bound_holders"])!=len(expected_nodes):
            raise HolderEvidenceError("missing, reordered or extra bound holders")
        for actual,node in zip(group["observed_bound_holders"],expected_nodes,strict=True):
            if not isinstance(actual,dict) or set(actual)!={
                "node_id","depth","holder_implementation_class",
                "bound_density_implementation_class","bound_compute_declaring_class",
                "source_reviewed",
            } or type(actual["node_id"]) is not int \
               or actual["node_id"]!=node["node_id"] \
               or type(actual["depth"]) is not int or actual["depth"]!=node["depth"] \
               or actual["source_reviewed"] is not False \
               or not isinstance(actual["holder_implementation_class"],str) \
               or not CLASS.fullmatch(actual["holder_implementation_class"]) \
               or not isinstance(actual["bound_density_implementation_class"],str) \
               or not graph.DENSITY_CLASS.fullmatch(actual["bound_density_implementation_class"]) \
               or not isinstance(actual["bound_compute_declaring_class"],str) \
               or not graph.DENSITY_CLASS.fullmatch(actual["bound_compute_declaring_class"]):
                raise HolderEvidenceError("invalid real HolderHolder.function.value identity")


def capture(*,source:Path,db:Path,lock:Path,server:Path,frontier:Path,
            roots_path:Path,graph_path:Path,output:Path) -> dict:
    destination=improved.external_output(output)
    original=graph.load_original_roots(roots_path)
    previous=load_graph(graph_path,original)
    with lock.open("rb") as file:
        pinned=tomllib.load(file)
    if (pinned.get("minecraft"),pinned.get("protocol"),pinned.get("data_version"))!=(
        "26.2",776,4903,
    ):
        raise HolderEvidenceError("not the pinned official 26.2 target")
    stock.reference_frontier(frontier,pinned)
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        prior_methods=roots.source_methods(conn)
        new_method=source_holder_compute(conn)
    finally:
        conn.close()
    server_sha=official.sha256_file(server)
    if source_sha!=frozen.SOURCE_SHA256 or server_sha!=frozen.SERVER_SHA256 \
       or server_sha!=pinned["runtime"]["server_sha256"] \
       or prior_methods!=previous["source_methods"]:
        raise HolderEvidenceError("original source/JAR or prior router methods changed")
    methods=dict(prior_methods,holder_holder_compute=new_method)
    bindings=observe(server,previous,original)
    manifest={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "original_router_roots_sha256":graph.ORIGINAL_ROOT_SHA256,
        "original_router_graph_sha256":ORIGINAL_GRAPH_SHA256,
        "source_methods":methods,"world_seeds":list(roots.SEEDS),
        "world_seed_random_state_observed":True,
        "world_seed_random_state_bound":False,
        "source_text_included":False,
        "independent_var_sem_admitted":False,
        "router_numeric_parity_qualified":False,
        "full_router_graph_qualified":False,
        "production_worldgen_enabled":False,
        "holder_bindings":bindings,
    }
    validate(manifest,previous,methods)
    raw=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(raw)>200_000:
        raise HolderEvidenceError("unbounded stock holder output")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as file:
        file.write(raw)
    return {
        "output":str(destination),"sha256":hashlib.sha256(raw).hexdigest(),
        "holder_bindings":sum(len(g["observed_bound_holders"]) for g in bindings),
        "source_reviewed":False,"production_worldgen_enabled":False,
    }


def main(argv:list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=primitive.SOURCE)
    parser.add_argument("--db",type=Path,default=primitive.DB)
    parser.add_argument("--lock",type=Path,default=primitive.LOCK)
    parser.add_argument("--cache",type=Path,default=primitive.CACHE)
    parser.add_argument("--server-jar",type=Path)
    parser.add_argument("--frontier",type=Path,default=stock.FRONTIER)
    parser.add_argument("--roots",type=Path,required=True)
    parser.add_argument("--graph",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
                                 server=server,frontier=args.frontier,
                                 roots_path=args.roots,graph_path=args.graph,
                                 output=args.output),sort_keys=True))
    except (HolderEvidenceError,graph.RouterGraphError,roots.RouterRootsError,
            improved.CaptureError,OSError,ValueError,KeyError,TypeError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 HOLDER BOUNDARY UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
