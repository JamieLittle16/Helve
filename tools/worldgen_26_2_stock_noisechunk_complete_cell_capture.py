#!/usr/bin/env python3
"""Actual stock Minecraft Java 26.2 full 4×8×4 single-NoiseChunk-cell probe.

512 raw IEEE-754 finalDensity outputs: four pinned world seeds × all 128
positions of ONE original NoiseChunk interpolation cell, same original
holder/settings/constructor. Different traversal from the four-point probe;
NOT a certified vanilla chunk production order, cache/slice lifecycle,
neighbouring-cell seam, or Rust numerical parity.
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
import worldgen_26_2_stock_noisechunk_cell_fixture as frozen_cell

ROOT=Path(__file__).resolve().parents[1]
KIND="official_26_2_stock_noisechunk_complete_single_cell_512"
POINTS=tuple((x,y,z) for y in range(64,72)
             for x in range(4) for z in range(4))
SEEDS=cell.SEEDS
assert len(POINTS)==128 and len(SEEDS)==4
WRAPPED=frozen_cell.WRAPPED
HEX=re.compile(r"[0-9a-f]{16}\Z")


class CompleteCellError(ValueError):
    """Original 26.2 NoiseChunk full bounded cell data remain unqualified."""


def input_rows()->list[dict]:
    return [
        {
            "world_seed_bits":seed,"block_x":x,"block_y":y,"block_z":z,
            "cell_x":0,"cell_y":16,"cell_z":0,
        }
        for seed in SEEDS for x,y,z in POINTS
    ]


def parse_output(stdout:str)->list[str]:
    if not isinstance(stdout,str) or len(stdout)>100_000:
        raise CompleteCellError("unbounded full-cell original JVM output")
    tokens={cell.TAG_HEAD,cell.TAG_BITS,cell.TAG_END,cell.TAG_FAILURE}
    rows=[line.split("|") for line in stdout.splitlines()
          if line.split("|",1)[0] in tokens]
    failures=[r for r in rows if r[0]==cell.TAG_FAILURE]
    if failures:
        if len(failures)!=1 or len(failures[0])!=5:
            raise CompleteCellError("malformed actual NoiseChunk JVM failure")
        bad=failures[0]
        raise CompleteCellError("JVM PHASE: "+bad[1]+"; ROOT: "+bad[2]+
                                "; CAUSE: "+bad[4])
    cursor=0
    values=[]
    for i,seed in enumerate(SEEDS):
        header=[cell.TAG_HEAD,str(i),seed,"4","8","-64","384",WRAPPED,"128"]
        if cursor>=len(rows) or rows[cursor]!=header:
            raise CompleteCellError("nonoriginal 26.2 NoiseChunk cell header or wrong wrapped graph")
        cursor+=1
        for point in POINTS:
            if cursor>=len(rows):
                raise CompleteCellError("missing full-cell official stock bit frame")
            row=rows[cursor];cursor+=1
            if len(row)!=3 or row[:2]!=[cell.TAG_BITS,str(len(values))] or \
               not HEX.fullmatch(row[2]) or ((int(row[2],16)>>52)&0x7ff)==0x7ff:
                raise CompleteCellError("nonfinite/reordered/malformed actual NoiseChunk bits")
            values.append("0x"+row[2])
        if cursor>=len(rows) or rows[cursor]!=[
            cell.TAG_END,str(i),str(len(POINTS))
        ]:
            raise CompleteCellError("missing original full-cell END frame")
        cursor+=1
    if len(values)!=512 or cursor!=len(rows):
        raise CompleteCellError("not exactly four complete 128-position stock cells")
    return values


def observe(server:Path,*,timeout:int=240)->list[str]:
    with tempfile.TemporaryDirectory(prefix="helve-262-complete-stock-cell-") as td:
        work=Path(td)
        jars=cell.official.extract_classpath(server,work/"classpath")
        compiled=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(cell.scalar.roots.BASE_BRIDGE),str(cell.JAVA_SOURCE)],
            capture_output=True,text=True,check=False,timeout=timeout,
        )
        if compiled.returncode:
            raise CompleteCellError("original stock full-cell JVM probe compile failed: "+
                                    compiled.stderr[:1800])
        run=subprocess.run(
            ["java","-Xmx1024m","-cp",
             os.pathsep.join([str(work),*(str(p) for p in jars)]),
             "HelveStockNoiseChunkCell262","--stock-noisechunk-complete-cell-512"],
            input="\n".join(SEEDS)+"\n",capture_output=True,text=True,
            check=False,timeout=timeout,
        )
        if run.returncode:
            try:
                parse_output(run.stdout)
            except CompleteCellError as exc:
                raise CompleteCellError(str(exc)) from exc
            raise CompleteCellError("actual original full-cell JVM failed: "+
                                    cell.stock.java_failure_detail(run.stderr))
        return parse_output(run.stdout)


def validate(manifest:dict,source_methods:dict)->None:
    constants={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "official_server_sha256":cell.frozen.SERVER_SHA256,
        "previous_original_cell_sha256":frozen_cell.ORIGINAL_JSON_SHA256,
        "previous_original_singlepoint_sha256":cell.scalar_fixture.ORIGINAL_JSON_SHA256,
        "source_methods":source_methods,
        "world_seeds":list(SEEDS),
        "points":[list(p) for p in POINTS],
        "sample_context":"NoiseChunk",
        "traversal":"single_cell_y_ascending_x_ascending_z_ascending",
        "cell_geometry":{
            "width":4,"height":8,"min_y":-64,"world_height":384,
            "cell_x":0,"cell_y":16,"cell_z":0,
        },
        "wrapped_classes":[WRAPPED]*4,
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
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(constants)|{"vectors"}:
        raise CompleteCellError("wrong bounded 26.2 complete-cell schema")
    for k,v in constants.items():
        if type(manifest.get(k)) is not type(v) or manifest[k]!=v:
            raise CompleteCellError("unqualified original 26.2 full cell source/gate: "+k)
    vectors=manifest["vectors"]
    if not isinstance(vectors,list) or len(vectors)!=512:
        raise CompleteCellError("not exactly 512 original stock NoiseChunk rows")
    for idx,(row,expected) in enumerate(zip(vectors,input_rows(),strict=True)):
        if not isinstance(row,dict) or set(row)!=set(expected)|{"value_bits"} or \
           any(type(row.get(k)) is not type(v) or row[k]!=v for k,v in expected.items()) or \
           not isinstance(row.get("value_bits"),str) or \
           not re.fullmatch(r"0x[0-9a-f]{16}",row["value_bits"]) or \
           ((int(row["value_bits"][2:],16)>>52)&0x7ff)==0x7ff:
            raise CompleteCellError("wrong row/coordinate or nonfinite rawbit at "+str(idx))


def capture(*,source:Path,db:Path,lock:Path,server:Path,
            previous_cell:Path,output:Path)->dict:
    destination=cell.improved.external_output(output)
    # Prior real 16-cell evidence and scalar exact overlaps MUST be authentic;
    # this is not an inference from a test fixture or source body SHA alone.
    frozen_cell.validate_original_capture(previous_cell)
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise CompleteCellError("wrong pinned stock Minecraft version")
    conn=cell.vanilla_atlas.connect_db(db)
    try:
        source_sha=cell.source_probe.require_pinned_source(conn,source,lock)
        methods=cell.source_methods(conn)
    finally:
        conn.close()
    if methods!=frozen_cell.source_methods():
        raise CompleteCellError("genuine previous NoiseChunk method bodies changed")
    jvm_sha=cell.official.sha256_file(server)
    if source_sha!=cell.frozen.SOURCE_SHA256 or \
       jvm_sha!=cell.frozen.SERVER_SHA256 or \
       jvm_sha!=pin["runtime"]["server_sha256"]:
        raise CompleteCellError("pinned original stock source/JAR identity changed")
    values=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":source_sha,
        "official_server_sha256":jvm_sha,
        "previous_original_cell_sha256":frozen_cell.ORIGINAL_JSON_SHA256,
        "previous_original_singlepoint_sha256":cell.scalar_fixture.ORIGINAL_JSON_SHA256,
        "source_methods":methods,"world_seeds":list(SEEDS),
        "points":[list(p) for p in POINTS],
        "sample_context":"NoiseChunk",
        "traversal":"single_cell_y_ascending_x_ascending_z_ascending",
        "cell_geometry":{
            "width":4,"height":8,"min_y":-64,"world_height":384,
            "cell_x":0,"cell_y":16,"cell_z":0,
        },
        "wrapped_classes":[WRAPPED]*4,
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
        "vectors":[dict(row,value_bits=bit)
                   for row,bit in zip(input_rows(),values,strict=True)],
    }
    validate(report,methods)
    payload=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>250_000:
        raise CompleteCellError("unbounded original stock complete-cell JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),"wb") as out:
        out.write(payload)
    return {
        "output":str(destination),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "authentic_stock_single_cell_values":len(values),
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "production_worldgen_enabled":False,
    }


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=cell.primitive.SOURCE)
    parser.add_argument("--db",type=Path,default=cell.primitive.DB)
    parser.add_argument("--lock",type=Path,default=cell.primitive.LOCK)
    parser.add_argument("--cache",type=Path,default=cell.primitive.CACHE)
    parser.add_argument("--server-jar",type=Path)
    parser.add_argument("--previous-cell",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=cell.official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(
            source=args.source,db=args.db,lock=args.lock,server=server,
            previous_cell=args.previous_cell,output=args.output
        ),sort_keys=True))
    except (
        CompleteCellError,cell.NoiseChunkCellError,
        frozen_cell.FrozenNoiseChunkError,
        cell.scalar_fixture.FrozenFinalDensityError,
        cell.improved.CaptureError,
        sqlite3.Error,KeyError,TypeError,ValueError,OSError,
        subprocess.TimeoutExpired,urllib.error.URLError,
    ) as exc:
        print("STOCK 26.2 NOISECHUNK COMPLETE CELL UNQUALIFIED: "+str(exc),
              file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
