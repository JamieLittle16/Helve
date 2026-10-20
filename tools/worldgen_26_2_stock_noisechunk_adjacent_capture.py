#!/usr/bin/env python3
"""Bounded candidate cross-cell stock 26.2 NoiseChunk numerical frontier.

Extends the existing original-JVM bridge without touching its 16/512 modes.
Two chunk origins, two adjacent X and Z cells, three Y cells and explicit
swapSlices per X column. This is NOT independently source-reviewed as the
canonical vanilla loop, not a Rust parity or production-worldgen gate.
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

import worldgen_26_2_stock_noisechunk_cell_capture as cell
import worldgen_26_2_stock_noisechunk_cell_fixture as previous
import worldgen_26_2_stock_noisechunk_complete_cell_fixture as complete

KIND="official_26_2_stock_noisechunk_candidate_adjacent_cells"
MODE="--stock-noisechunk-adjacent-cells"
HEAD="HELVE26_2_NOISECHUNK_ADJACENT_HEAD"
BIT="HELVE26_2_NOISECHUNK_ADJACENT_BITS"
END="HELVE26_2_NOISECHUNK_ADJACENT_END"
HEX=re.compile(r"[0-9a-f]{16}\Z")
SHA=re.compile(r"[0-9a-f]{64}\Z")
WRAPPED=cell.ROOT if hasattr(cell,"ROOT") else None
# Stock finalDensity is the observed Ap2 root, NOT a compiled Rust router.
AP2="net.minecraft.world.level.levelgen.DensityFunctions$Ap2"
SEEDS=cell.SEEDS
CHUNK_ORIGINS=(0,-16)
EXTRA_METHODS=(
    ("chunk_swap","net.minecraft.world.level.levelgen.NoiseChunk","swapSlices"),
    ("generator_fill","net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator","fillFromNoise"),
    ("generator_do_fill","net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator","doFill"),
)


class AdjacentError(ValueError):
    """The original cross-cell numerical frontier was not admitted."""


def points(chunk_index:int)->tuple[tuple[int,int,int],...]:
    if type(chunk_index) is not int or chunk_index not in (0,1):
        raise AdjacentError("wrong bounded chunk index")
    origin=CHUNK_ORIGINS[chunk_index]
    return tuple(
        (origin+cx*4+lx,cy*8+ly,origin+cz*4+lz)
        for cx in range(2)
        for cz in range(2)
        for cy in range(17,14,-1)
        for ly in (7,0)
        for lx in (0,3)
        for lz in (0,3)
    )


assert all(len(points(i))==96 and len(set(points(i)))==96 for i in (0,1))


def input_rows()->list[dict]:
    return [
        {"world_seed_bits":seed,"chunk_index":chunk_index,
         "block_x":x,"block_y":y,"block_z":z}
        for seed in SEEDS for chunk_index in range(2)
        for x,y,z in points(chunk_index)
    ]


def source_methods(conn:sqlite3.Connection)->dict:
    # The existing nine immutable source identities MUST continue matching.
    existing=cell.source_methods(conn)
    if existing!=previous.source_methods():
        raise AdjacentError("existing nine 26.2 NoiseChunk method identities drifted")
    report=dict(existing)
    for label,owner,name in EXTRA_METHODS:
        rows=conn.execute(
            "SELECT m.signature,m.param_count,m.body_sha256,m.normalized_sha256 "
            "FROM methods m JOIN types t ON t.id=m.type_id "
            "WHERE t.qualified_name=? AND m.name=?",
            (owner,name),
        ).fetchall()
        if len(rows)!=1:
            raise AdjacentError("missing/ambiguous original 26.2 method: "+label)
        r=rows[0]
        if not all(isinstance(r[k],str) and SHA.fullmatch(r[k])
                   for k in ("body_sha256","normalized_sha256")):
            raise AdjacentError("missing original method body fingerprint: "+label)
        if label=="chunk_swap" and r["param_count"]!=0:
            raise AdjacentError("original swapSlices arity changed")
        report[label]={
            "owner":owner,"signature":r["signature"],
            "body_sha256":r["body_sha256"],
            "normalized_sha256":r["normalized_sha256"],
            "reviewed":False,
        }
    return report


def parse_output(stdout:str)->list[str]:
    if not isinstance(stdout,str) or len(stdout)>130_000:
        raise AdjacentError("unbounded adjacent original-JVM stdout")
    tags={HEAD,BIT,END,cell.TAG_FAILURE}
    rows=[line.split("|") for line in stdout.splitlines()
          if line.split("|",1)[0] in tags]
    failures=[r for r in rows if r[0]==cell.TAG_FAILURE]
    if failures:
        if len(failures)!=1 or len(failures[0])!=5:
            raise AdjacentError("malformed original JVM failure")
        raise AdjacentError("JVM PHASE: "+failures[0][1]+"; ROOT: "+
                            failures[0][2]+"; CAUSE: "+failures[0][4])
    cursor=0
    values=[]
    for si,seed in enumerate(SEEDS):
        for chunk_index,origin in enumerate(CHUNK_ORIGINS):
            expected=[HEAD,str(si),seed,str(chunk_index),str(origin),
                      str(origin),"4","8","-64","384",AP2,"96"]
            if cursor>=len(rows) or rows[cursor]!=expected:
                raise AdjacentError("wrong original adjacent header/chunk origin")
            cursor+=1
            for point in points(chunk_index):
                if cursor>=len(rows):
                    raise AdjacentError("missing original adjacent numeric bits")
                r=rows[cursor]
                cursor+=1
                if (len(r)!=6 or r[:5]!=[
                    BIT,str(len(values)),*(str(x) for x in point)
                ] or not HEX.fullmatch(r[5]) or
                    (int(r[5],16)>>52)&0x7ff==0x7ff):
                    raise AdjacentError("reordered/nonfinite/wrong coordinate adjacent bits")
                values.append("0x"+r[5])
            if cursor>=len(rows) or rows[cursor]!=[
                END,str(si),str(chunk_index),"96"
            ]:
                raise AdjacentError("missing original adjacent END")
            cursor+=1
    if cursor!=len(rows) or len(values)!=768:
        raise AdjacentError("not exactly 768 bounded stock adjacent samples")
    return values


def observe(server:Path,*,timeout:int=240)->list[str]:
    with tempfile.TemporaryDirectory(prefix="helve-262-stock-adjacent-") as td:
        work=Path(td)
        jars=cell.official.extract_classpath(server,work/"classpath")
        built=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(cell.scalar.roots.BASE_BRIDGE),str(cell.JAVA_SOURCE)],
            capture_output=True,text=True,check=False,timeout=timeout,
        )
        if built.returncode:
            raise AdjacentError("original adjacent JVM compile failed: "+built.stderr[:1800])
        proc=subprocess.run(
            ["java","-Xmx1024m","-cp",
             os.pathsep.join([str(work),*(str(x) for x in jars)]),
             "HelveStockNoiseChunkCell262",MODE],
            input="\n".join(SEEDS)+"\n",capture_output=True,text=True,
            check=False,timeout=timeout,
        )
        if proc.returncode:
            try:
                parse_output(proc.stdout)
            except AdjacentError as exc:
                raise AdjacentError(str(exc)) from exc
            raise AdjacentError("original JVM failed: "+
                                cell.stock.java_failure_detail(proc.stderr))
        return parse_output(proc.stdout)


def validate(manifest:dict,methods:dict)->None:
    constants={
        "schema":1,"kind":KIND,"minecraft":"26.2",
        "protocol":776,"data_version":4903,
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "official_server_sha256":cell.frozen.SERVER_SHA256,
        "previous_original_complete_cell_sha256":complete.ORIGINAL_JSON_SHA256,
        "source_methods":methods,
        "world_seeds":list(SEEDS),
        "chunk_origins":list(CHUNK_ORIGINS),
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
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(constants)|{"vectors"}:
        raise AdjacentError("wrong original adjacent evidence schema")
    for k,v in constants.items():
        if type(manifest.get(k)) is not type(v) or manifest[k]!=v:
            raise AdjacentError("adjacent source identity or qualification changed: "+k)
    rows=manifest["vectors"]
    if not isinstance(rows,list) or len(rows)!=768:
        raise AdjacentError("not 768 original adjacent numerical rows")
    for idx,(got,expected) in enumerate(zip(rows,input_rows(),strict=True)):
        if (not isinstance(got,dict) or
            set(got)!=set(expected)|{"value_bits"} or
            any(type(got.get(k)) is not type(v) or got[k]!=v
                for k,v in expected.items()) or
            not isinstance(got.get("value_bits"),str) or
            not re.fullmatch(r"0x[0-9a-f]{16}",got["value_bits"]) or
            ((int(got["value_bits"][2:],16)>>52)&0x7ff)==0x7ff):
            raise AdjacentError("bad original adjacent row: "+str(idx))


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    target=cell.improved.external_output(output)
    # Reuse, authenticate, and do not rerun the earlier 512/16/128 captures.
    complete.load_bits()
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise AdjacentError("not pinned exact Minecraft 26.2 source")
    conn=cell.vanilla_atlas.connect_db(db)
    try:
        source_sha=cell.source_probe.require_pinned_source(conn,source,lock)
        methods=source_methods(conn)
    finally:
        conn.close()
    jar_sha=cell.official.sha256_file(server)
    if (source_sha!=cell.frozen.SOURCE_SHA256 or
        jar_sha!=cell.frozen.SERVER_SHA256 or
        jar_sha!=pin["runtime"]["server_sha256"]):
        raise AdjacentError("original source/JAR signature drift")
    values=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2",
        "protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,
        "official_server_sha256":jar_sha,
        "previous_original_complete_cell_sha256":complete.ORIGINAL_JSON_SHA256,
        "source_methods":methods,"world_seeds":list(SEEDS),
        "chunk_origins":list(CHUNK_ORIGINS),
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
        "vectors":[dict(row,value_bits=value)
                   for row,value in zip(input_rows(),values,strict=True)],
    }
    validate(report,methods)
    payload=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>240_000:
        raise AdjacentError("oversized bounded adjacent original JSON")
    target.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),
                   "wb") as stream:
        stream.write(payload)
    return {
        "output":str(target),"sha256":hashlib.sha256(payload).hexdigest(),
        "candidate_stock_adjacent_samples":len(values),
        "stock_noisechunk_canonical_traversal_qualified":False,
        "production_worldgen_enabled":False,
    }


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=cell.primitive.SOURCE)
    parser.add_argument("--db",type=Path,default=cell.primitive.DB)
    parser.add_argument("--lock",type=Path,default=cell.primitive.LOCK)
    parser.add_argument("--cache",type=Path,default=cell.primitive.CACHE)
    parser.add_argument("--server-jar",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=cell.official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(
            source=args.source,db=args.db,lock=args.lock,
            server=server,output=args.output,
        ),sort_keys=True))
    except (AdjacentError,cell.NoiseChunkCellError,
            complete.FrozenCompleteCellError,
            sqlite3.Error,KeyError,ValueError,TypeError,OSError,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 ADJACENT NOISECHUNK UNQUALIFIED: "+str(exc),
              file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
