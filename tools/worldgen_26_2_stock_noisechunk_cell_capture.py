#!/usr/bin/env python3
"""Source-pinned actual 26.2 NoiseChunk wrapped finalDensity cell numerical frontier.

Four real stock Overworld seeds, one 4x8x4 cell, four interpolated block
positions each. Authentic NoiseChunk constructor, wrap, initialize/advance,
selectCellYZ, updateY/X/Z, compute, stop sequence. This is first bounded
*chunk-context* evidence, NOT production terrain/chunk parity or Rust parity.
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
import worldgen_26_2_stock_final_density_singlepoint_capture as scalar
import worldgen_26_2_stock_final_density_singlepoint_fixture as scalar_fixture
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

ROOT=Path(__file__).resolve().parents[1]
JAVA_SOURCE=ROOT/"tools/worldgen_java/HelveStockNoiseChunkCell262.java"
KIND="official_26_2_stock_noisechunk_wrapped_final_density_single_cell_16"
SEEDS=tuple(scalar.SEEDS)
POINTS=((0,64,0),(1,65,1),(2,66,2),(3,67,3))
TAG_HEAD="HELVE26_2_NOISECHUNK_CELL_HEAD"
TAG_BITS="HELVE26_2_NOISECHUNK_CELL_BITS"
TAG_END="HELVE26_2_NOISECHUNK_CELL_END"
TAG_FAILURE="HELVE26_2_NOISECHUNK_CELL_FAILURE"
HEX=re.compile(r"[0-9a-f]{16}\Z")
SHA=re.compile(r"[0-9a-f]{64}\Z")
CLASS=re.compile(r"net\.minecraft\.world\.level\.levelgen\.[A-Za-z_$][\w$]*\Z")
GEOMETRY=(4,8,-64,384)
# Source-indexed only; a SHA identifies code but does NOT certify a law.
METHODS=(
 ("chunk_wrap","net.minecraft.world.level.levelgen.NoiseChunk","wrap",1),
 ("chunk_initialize","net.minecraft.world.level.levelgen.NoiseChunk","initializeForFirstCellX",0),
 ("chunk_advance","net.minecraft.world.level.levelgen.NoiseChunk","advanceCellX",1),
 ("chunk_select","net.minecraft.world.level.levelgen.NoiseChunk","selectCellYZ",2),
 ("chunk_update_y","net.minecraft.world.level.levelgen.NoiseChunk","updateForY",2),
 ("chunk_update_x","net.minecraft.world.level.levelgen.NoiseChunk","updateForX",2),
 ("chunk_update_z","net.minecraft.world.level.levelgen.NoiseChunk","updateForZ",2),
 ("chunk_stop","net.minecraft.world.level.levelgen.NoiseChunk","stopInterpolation",0),
 ("global_fluid_picker","net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator","createFluidPicker",1),
)


class NoiseChunkCellError(ValueError):
    """Genuine chunk-scoped 26.2 density interpolation was not admitted."""


def input_rows() -> list[dict]:
    return [
        {"world_seed_bits":seed,"block_x":x,"block_y":y,"block_z":z,
         "cell_x":0,"cell_y":16,"cell_z":0}
        for seed in SEEDS for (x,y,z) in POINTS
    ]


def source_methods(conn:sqlite3.Connection) -> dict:
    report={}
    for label,owner,name,arity in METHODS:
        rows=conn.execute(
            "SELECT m.id,m.signature,m.body_sha256,m.normalized_sha256 "
            "FROM methods m JOIN types t ON m.type_id=t.id "
            "WHERE t.qualified_name=? AND m.name=? AND m.param_count=?",
            (owner,name,arity),
        ).fetchall()
        if len(rows)!=1:
            raise NoiseChunkCellError("missing/ambiguous 26.2 NoiseChunk source method: "+label)
        row=rows[0]
        if not all(isinstance(row[k],str) and SHA.fullmatch(row[k])
                   for k in ("body_sha256","normalized_sha256")):
            raise NoiseChunkCellError("incomplete 26.2 source fingerprint: "+label)
        report[label]={
            "owner":owner,"signature":row["signature"],
            "body_sha256":row["body_sha256"],
            "normalized_sha256":row["normalized_sha256"],
            "reviewed":False,
        }
    return report


def parse_output(stdout:str) -> tuple[list[str],list[str]]:
    if not isinstance(stdout,str) or len(stdout)>30_000:
        raise NoiseChunkCellError("unbounded NoiseChunk original JVM stdout")
    tagged=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in
            {TAG_HEAD,TAG_BITS,TAG_END,TAG_FAILURE}]
    failures=[row for row in tagged if row[0]==TAG_FAILURE]
    if failures:
        if len(failures)!=1 or len(failures[0])!=5:
            raise NoiseChunkCellError("malformed original NoiseChunk JVM error")
        row=failures[0]
        raise NoiseChunkCellError("JVM PHASE: "+row[1]+"; ROOT: "+row[2]+
                                   "; CAUSE: "+row[4])
    cursor=0
    values=[]
    wrappers=[]
    for seed_index,seed in enumerate(SEEDS):
        if cursor>=len(tagged):
            raise NoiseChunkCellError("missing 26.2 cell HEAD")
        row=tagged[cursor];cursor+=1
        if len(row)!=9 or row[:7]!=[
                TAG_HEAD,str(seed_index),seed,
                *(str(v) for v in GEOMETRY)] or row[8]!="4" or \
            not CLASS.fullmatch(row[7]):
            raise NoiseChunkCellError("wrong 26.2 NoiseChunk constructor, wrapper or cell shape")
        wrappers.append(row[7])
        for point_index in range(len(POINTS)):
            if cursor>=len(tagged):
                raise NoiseChunkCellError("missing original NoiseChunk density value")
            row=tagged[cursor];cursor+=1
            if len(row)!=3 or row[:2]!=[TAG_BITS,str(len(values))] or \
               not HEX.fullmatch(row[2]) or (int(row[2],16)>>52)&0x7ff==0x7ff:
                raise NoiseChunkCellError("malformed/reordered/nonfinite official chunk density")
            values.append("0x"+row[2])
        if cursor>=len(tagged) or tagged[cursor]!=[
                TAG_END,str(seed_index),str(len(POINTS))]:
            raise NoiseChunkCellError("missing or incorrect stock cell END")
        cursor+=1
    if cursor!=len(tagged) or len(values)!=16 or len(wrappers)!=4:
        raise NoiseChunkCellError("missing or surplus authentic NoiseChunk samples")
    return values,wrappers


def observe(server:Path,*,timeout:int=240)->tuple[list[str],list[str]]:
    with tempfile.TemporaryDirectory(prefix="helve-262-real-noisechunk-") as scratch:
        work=Path(scratch)
        cp=official.extract_classpath(server,work/"classpath")
        built=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             str(scalar.roots.BASE_BRIDGE),str(JAVA_SOURCE)],
            capture_output=True,text=True,check=False,timeout=timeout,
        )
        if built.returncode:
            raise NoiseChunkCellError("original 26.2 NoiseChunk JVM probe compile failed: "+
                                       built.stderr[:2000])
        run=subprocess.run(
            ["java","-Xmx1024m","-cp",
             os.pathsep.join([str(work),*(str(j) for j in cp)]),
             "HelveStockNoiseChunkCell262","--stock-noisechunk-cell-16"],
            input="\n".join(SEEDS)+"\n",capture_output=True,text=True,
            check=False,timeout=timeout,
        )
        if run.returncode:
            try:
                parse_output(run.stdout)
            except NoiseChunkCellError as exc:
                raise NoiseChunkCellError(str(exc)) from exc
            raise NoiseChunkCellError("actual 26.2 NoiseChunk JVM failed: "+
                                       stock.java_failure_detail(run.stderr))
        return parse_output(run.stdout)


def validate(manifest:dict,method_inventory:dict)->None:
    constants={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":frozen.SOURCE_SHA256,
        "official_server_sha256":frozen.SERVER_SHA256,
        "original_singlepoint_oracle_sha256":scalar_fixture.ORIGINAL_JSON_SHA256,
        "source_methods":method_inventory,"world_seeds":list(SEEDS),
        "points":[list(p) for p in POINTS],
        "cell_geometry":{"width":4,"height":8,"min_y":-64,"world_height":384,
                         "cell_x":0,"cell_y":16,"cell_z":0},
        "sample_context":"NoiseChunk",
        "stock_registry_used":True,
        "stock_noisechunk_cell_observed":True,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "world_seed_random_state_bound":False,
        "full_router_graph_qualified":False,
        "router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "source_text_included":False,
        "production_worldgen_enabled":False,
    }
    if not isinstance(manifest,dict) or set(manifest)!=set(constants)|{"vectors","wrapped_classes"}:
        raise NoiseChunkCellError("unqualified actual NoiseChunk cell result schema")
    for k,v in constants.items():
        if type(manifest.get(k)) is not type(v) or manifest[k]!=v:
            raise NoiseChunkCellError("unqualified stock cell evidence/gate: "+k)
    classes=manifest["wrapped_classes"]
    if not isinstance(classes,list) or len(classes)!=4 or \
       any(not isinstance(c,str) or not CLASS.fullmatch(c) for c in classes):
        raise NoiseChunkCellError("wrong wrapped original NoiseChunk classes")
    rows=manifest["vectors"]
    if not isinstance(rows,list) or len(rows)!=16:
        raise NoiseChunkCellError("actual NoiseChunk density 16-vector count changed")
    for i,(actual,expected) in enumerate(zip(rows,input_rows(),strict=True)):
        if not isinstance(actual,dict) or set(actual)!=set(expected)|{"value_bits"} or \
           any(type(actual.get(k)) is not type(v) or actual[k]!=v
               for k,v in expected.items()) or \
           not isinstance(actual.get("value_bits"),str) or \
           not re.fullmatch(r"0x[0-9a-f]{16}",actual["value_bits"]) or \
           (int(actual["value_bits"][2:],16)>>52)&0x7ff==0x7ff:
            raise NoiseChunkCellError("unqualified stock cell density value: "+str(i))


def capture(*,source:Path,db:Path,lock:Path,server:Path,
            previous_singlepoint:Path,output:Path)->dict:
    destination=improved.external_output(output)
    scalar_fixture.validate_original_capture(previous_singlepoint)
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise NoiseChunkCellError("not exact pinned original Minecraft 26.2")
    connection=vanilla_atlas.connect_db(db)
    try:
        src=source_probe.require_pinned_source(connection,source,lock)
        methods=source_methods(connection)
    finally:
        connection.close()
    jvm=official.sha256_file(server)
    if src!=frozen.SOURCE_SHA256 or jvm!=frozen.SERVER_SHA256 or \
       jvm!=pin["runtime"]["server_sha256"]:
        raise NoiseChunkCellError("source/official server JAR identity differs")
    values,wrapped_classes=observe(server)
    manifest={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":src,
        "official_server_sha256":jvm,
        "original_singlepoint_oracle_sha256":scalar_fixture.ORIGINAL_JSON_SHA256,
        "source_methods":methods,"world_seeds":list(SEEDS),
        "points":[list(p) for p in POINTS],
        "cell_geometry":{"width":4,"height":8,"min_y":-64,"world_height":384,
                         "cell_x":0,"cell_y":16,"cell_z":0},
        "sample_context":"NoiseChunk","stock_registry_used":True,
        "stock_noisechunk_cell_observed":True,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "world_seed_random_state_bound":False,
        "full_router_graph_qualified":False,
        "router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "source_text_included":False,
        "production_worldgen_enabled":False,
        "wrapped_classes":wrapped_classes,
        "vectors":[dict(row,value_bits=value)
                   for row,value in zip(input_rows(),values,strict=True)],
    }
    validate(manifest,methods)
    payload=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>40_000:
        raise NoiseChunkCellError("unbounded source-free stock NoiseChunk cell JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_CREAT|os.O_WRONLY|os.O_EXCL,0o600),"wb") as out:
        out.write(payload)
    return {"output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
            "genuine_noisechunk_cell_samples":len(values),
            "stock_noisechunk_full_lifecycle_qualified":False,
            "production_worldgen_enabled":False}


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=primitive.SOURCE)
    parser.add_argument("--db",type=Path,default=primitive.DB)
    parser.add_argument("--lock",type=Path,default=primitive.LOCK)
    parser.add_argument("--cache",type=Path,default=primitive.CACHE)
    parser.add_argument("--server-jar",type=Path)
    parser.add_argument("--previous-singlepoint",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        outcome=capture(
            source=args.source,db=args.db,lock=args.lock,server=server,
            previous_singlepoint=args.previous_singlepoint,output=args.output)
        print(json.dumps(outcome,sort_keys=True))
        return 0
    except (NoiseChunkCellError,scalar_fixture.FrozenFinalDensityError,
            scalar.FinalDensityError,improved.CaptureError,
            sqlite3.Error,TypeError,KeyError,ValueError,OSError,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 NOISECHUNK CELL UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
