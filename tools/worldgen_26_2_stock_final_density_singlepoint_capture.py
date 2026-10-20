#!/usr/bin/env python3
"""Stock 26.2 Overworld finalDensity.compute(SinglePointContext) bit oracle.

Authentic VanillaRegistries, NoiseGeneratorSettings.OVERWORLD,
RandomState.create and actual bound NoiseRouter.finalDensity own all math.
128 raw IEEE-754 outputs, four independent seeds × 32 explicit XYZ points.
NOT a NoiseChunk, interpolation, full-router or terrain generation oracle.
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
import worldgen_26_2_stock_router_holder_capture as holder
import worldgen_26_2_stock_router_graph_capture as graph
import worldgen_26_2_stock_router_roots_capture as roots
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

ROOT=Path(__file__).resolve().parents[1]
JAVA_SOURCE=ROOT/"tools/worldgen_java/HelveStockFinalDensitySinglePoint262.java"
KIND="official_26_2_stock_bound_final_density_singlepoint_128"
ORIGINAL_HOLDER_BYTES=15260
ORIGINAL_HOLDER_SHA256="1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64"
SEEDS=tuple(roots.SEEDS)
POINTS=(
    (0,-64,0),(0,0,0),(0,63,0),(0,64,0),
    (0,65,0),(0,128,0),(0,192,0),(0,255,0),
    (0,320,0),(1,-63,-1),(-1,-1,1),(15,64,15),
    (16,64,16),(-16,63,-16),(-17,65,-17),(31,127,-31),
    (32,128,-32),(128,64,128),(128,128,128),(-128,128,-128),
    (256,255,-256),(-256,0,256),(1024,64,-1024),(-1025,65,1025),
    (123456,73,-654321),(1000000,96,1000000),(-1000000,96,-1000000),
    (33554431,128,-33554432),(-33554431,-63,33554431),
    (2147483600,255,-2147483600),(-2147483600,-4096,2147483600),
    (0,-65,0),
)
assert len(SEEDS)==4 and len(POINTS)==32 and len(SEEDS)*len(POINTS)==128
HEAD="HELVE26_2_FINAL_SINGLE_HEAD"
BITS="HELVE26_2_FINAL_SINGLE_BITS"
END="HELVE26_2_FINAL_SINGLE_END"
FAIL="HELVE26_2_FINAL_SINGLE_FAILURE"
FINAL="net.minecraft.world.level.levelgen.DensityFunctions$Ap2"
MAPPED="net.minecraft.world.level.levelgen.DensityFunctions$Mapped"
HOLDER="net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder"
HEX=re.compile(r"[0-9a-f]{16}\Z")
SHA=re.compile(r"[0-9a-f]{64}\Z")


class FinalDensityError(ValueError):
    """Original official stock finalDensity SinglePointContext not qualified."""


def input_rows() -> list[dict]:
    return [
        {"world_seed_bits":seed,"block_x":x,"block_y":y,"block_z":z}
        for seed in SEEDS for (x,y,z) in POINTS
    ]


def source_ap2_compute(conn:sqlite3.Connection) -> dict:
    rows=conn.execute(
        "SELECT m.id,m.signature FROM methods m JOIN types t ON m.type_id=t.id "
        "WHERE t.qualified_name=? AND m.name='compute' AND m.param_count=1",
        (FINAL,),
    ).fetchall()
    if len(rows)!=1:
        raise FinalDensityError("missing or ambiguous actual 26.2 Ap2.compute source method")
    fingerprint=conn.execute(
        "SELECT body_sha256,normalized_sha256 FROM methods WHERE id=?",
        (rows[0]["id"],),
    ).fetchone()
    if fingerprint is None or not all(isinstance(v,str) and SHA.fullmatch(v)
                                      for v in fingerprint):
        raise FinalDensityError("missing source indexed Ap2.compute body SHA")
    return {
        "owner":FINAL,"signature":rows[0]["signature"],
        "body_sha256":fingerprint[0],
        "normalized_sha256":fingerprint[1],
        "reviewed":False,
    }


def load_holder_evidence(path:Path, previous:dict) -> dict:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_HOLDER_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_HOLDER_SHA256:
        raise FinalDensityError("exact previous official Holder evidence bytes/SHA required")
    try:
        receipt=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise FinalDensityError("invalid original Holder evidence JSON") from exc
    if not isinstance(receipt,dict) or not isinstance(receipt.get("source_methods"),dict):
        raise FinalDensityError("original holder source fingerprint inventory absent")
    holder.validate(receipt,previous,receipt["source_methods"])
    expected=((6,"Marker"),(7,"Marker"),(8,"Ap2"),(9,"Marker"),
              (15,"Marker"),(17,"Marker"),(21,"RangeChoice"),
              (27,"YClampedGradient"))
    for i,group in enumerate(receipt["holder_bindings"]):
        if group["world_seed_bits"]!=SEEDS[i]:
            raise FinalDensityError("bound stock holder seed changed")
        seen=group["observed_bound_holders"]
        if len(seen)!=len(expected):
            raise FinalDensityError("unexpected HolderHolder target count")
        for actual,(id_,class_name) in zip(seen,expected,strict=True):
            if actual["node_id"]!=id_ or \
               actual["holder_implementation_class"]!="net.minecraft.core.Holder$Direct" or \
               actual["bound_density_implementation_class"]!=(
                   "net.minecraft.world.level.levelgen.DensityFunctions$"+class_name
               ):
                raise FinalDensityError("prior real holder target differs from independently observed")
    return receipt


def parse_output(stdout:str) -> list[str]:
    if not isinstance(stdout,str) or len(stdout)>80_000:
        raise FinalDensityError("unbounded stock finalDensity JVM output")
    lines=stdout.splitlines()
    failures=[line for line in lines if line.startswith(FAIL+"|")]
    if failures:
        if len(failures)!=1 or len(failures[0].split("|"))!=5:
            raise FinalDensityError("malformed finalDensity JVM failure")
        parts=failures[0].split("|")
        raise FinalDensityError("JVM PHASE: "+parts[1]+
                                "; ROOT: "+parts[2]+"; CAUSE: "+parts[4])
    # Ignore Minecraft bootstrap diagnostics but require exact ordered tags.
    records=[line.split("|") for line in lines
             if line.split("|",1)[0] in (HEAD,BITS,END)]
    cursor=0
    bits=[]
    for seed_index,seed in enumerate(SEEDS):
        if cursor>=len(records) or records[cursor]!=[
            HEAD,str(seed_index),seed,FINAL,MAPPED,HOLDER,str(len(POINTS))
        ]:
            raise FinalDensityError("wrong stock finalDensity bound class or seed")
        cursor+=1
        for point_index in range(len(POINTS)):
            if cursor>=len(records):
                raise FinalDensityError("missing exact finalDensity bit row")
            row=records[cursor];cursor+=1
            if len(row)!=3 or row[:2]!=[BITS,str(len(bits))] or \
               not HEX.fullmatch(row[2]) or (int(row[2],16)>>52)&0x7ff==0x7ff:
                raise FinalDensityError("malformed/reordered or nonfinite official finalDensity bits")
            bits.append("0x"+row[2])
        if cursor>=len(records) or records[cursor]!=[END,str(seed_index),str(len(POINTS))]:
            raise FinalDensityError("missing/changed official finalDensity seed END")
        cursor+=1
    if cursor!=len(records) or len(bits)!=128:
        raise FinalDensityError("unexpected official finalDensity extra or omitted records")
    return bits


def observe(server:Path,*,timeout:int=240) -> list[str]:
    if not JAVA_SOURCE.is_file() or not roots.BASE_BRIDGE.is_file():
        raise FinalDensityError("actual original JVM reflection bridges missing")
    with tempfile.TemporaryDirectory(prefix="helve-262-real-final-density-") as folder:
        work=Path(folder)
        jars=official.extract_classpath(server,work/"classpath")
        built=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(roots.BASE_BRIDGE),str(JAVA_SOURCE)],
            capture_output=True,text=True,check=False,timeout=timeout,
        )
        if built.returncode:
            raise FinalDensityError("original final density JVM reflection bridge compile failed: "+
                                    built.stderr[:1400])
        run=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join([str(work),*(str(jar) for jar in jars)]),
             "HelveStockFinalDensitySinglePoint262","--final-singlepoint-128"],
            input="\n".join(
                f"{r['world_seed_bits']}\t{r['block_x']}\t{r['block_y']}\t{r['block_z']}"
                for r in input_rows()
            )+"\n",capture_output=True,text=True,check=False,timeout=timeout,
        )
        if run.returncode:
            try:
                parse_output(run.stdout)
            except FinalDensityError as exc:
                raise FinalDensityError(str(exc)) from exc
            raise FinalDensityError("official stock finalDensity JVM returned failure: "+
                                    stock.java_failure_detail(run.stderr))
        return parse_output(run.stdout)


def validate(manifest:dict,source_methods:dict) -> None:
    expected={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":frozen.SOURCE_SHA256,
        "official_server_sha256":frozen.SERVER_SHA256,
        "original_router_roots_sha256":graph.ORIGINAL_ROOT_SHA256,
        "original_router_graph_sha256":holder.ORIGINAL_GRAPH_SHA256,
        "original_holder_bindings_sha256":ORIGINAL_HOLDER_SHA256,
        "source_methods":source_methods,
        "world_seeds":list(SEEDS),
        "points":[list(point) for point in POINTS],
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
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(expected)|{"vectors"}:
        raise FinalDensityError("invalid bound SinglePointContext oracle schema")
    for k,v in expected.items():
        if type(manifest.get(k)) is not type(v) or manifest[k]!=v:
            raise FinalDensityError("changed stock SinglePointContext oracle source or gate: "+k)
    rows=manifest["vectors"]
    if not isinstance(rows,list) or len(rows)!=128:
        raise FinalDensityError("expected exactly 128 ordered stock finalDensity outputs")
    for idx,(row,want) in enumerate(zip(rows,input_rows(),strict=True)):
        if not isinstance(row,dict) or set(row)!=set(want)|{"value_bits"} or \
           any(type(row.get(k)) is not type(v) or row[k]!=v for k,v in want.items()) or \
           not isinstance(row.get("value_bits"),str) or \
           not re.fullmatch(r"0x[0-9a-f]{16}",row["value_bits"]) or \
           (int(row["value_bits"][2:],16)>>52)&0x7ff==0x7ff:
            raise FinalDensityError("unqualified stock finalDensity vector at index "+str(idx))


def capture(*,source:Path,db:Path,lock:Path,server:Path,frontier:Path,
            roots_path:Path,graph_path:Path,holders_path:Path,output:Path) -> dict:
    destination=improved.external_output(output)
    first=graph.load_original_roots(roots_path)
    previous=holder.load_graph(graph_path,first)
    held=load_holder_evidence(holders_path,previous)
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903
    ):
        raise FinalDensityError("not the locked 26.2 official JVM")
    stock.reference_frontier(frontier,pin)
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        prior=roots.source_methods(conn)
        bound=holder.source_holder_compute(conn)
        ap2=source_ap2_compute(conn)
    finally:
        conn.close()
    server_sha=official.sha256_file(server)
    if source_sha!=frozen.SOURCE_SHA256 or \
       server_sha!=frozen.SERVER_SHA256 or \
       server_sha!=pin["runtime"]["server_sha256"] or \
       dict(prior,holder_holder_compute=bound)!=held["source_methods"]:
        raise FinalDensityError("real router binding or original source/JVM identities changed")
    methods=dict(held["source_methods"],ap2_compute=ap2)
    values=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":source_sha,
        "official_server_sha256":server_sha,
        "original_router_roots_sha256":graph.ORIGINAL_ROOT_SHA256,
        "original_router_graph_sha256":holder.ORIGINAL_GRAPH_SHA256,
        "original_holder_bindings_sha256":ORIGINAL_HOLDER_SHA256,
        "source_methods":methods,"world_seeds":list(SEEDS),
        "points":[list(point) for point in POINTS],
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
        "vectors":[dict(row,value_bits=value)
                   for row,value in zip(input_rows(),values,strict=True)],
    }
    validate(report,methods)
    payload=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>100_000:
        raise FinalDensityError("unbounded source-free stock final density report")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "singlepoint_final_density_values":len(values),
        "stock_noisechunk_interpolation_observed":False,
        "router_numeric_parity_qualified":False,
        "production_worldgen_enabled":False,
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
    parser.add_argument("--holders",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        result=capture(source=args.source,db=args.db,lock=args.lock,
                       server=server,frontier=args.frontier,roots_path=args.roots,
                       graph_path=args.graph,holders_path=args.holders,output=args.output)
        print(json.dumps(result,sort_keys=True))
    except (FinalDensityError,holder.HolderEvidenceError,graph.RouterGraphError,
            roots.RouterRootsError,improved.CaptureError,
            OSError,ValueError,KeyError,TypeError,sqlite3.Error,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FINAL DENSITY SINGLEPOINT UNQUALIFIED: "+str(exc),
              file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
