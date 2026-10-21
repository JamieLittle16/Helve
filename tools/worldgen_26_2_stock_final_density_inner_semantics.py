#!/usr/bin/env python3
"""Observe *new* inner finalDensity Marker and RangeChoice semantics on stock 26.2.

This is not a repetition of the prior 128 original finalDensity outputs:
the new measurements are the Marker-wrapped density input, the unwrapped
input, the RangeChoice selector and both branches at each previously pinned
coordinate. Previously validated Mapped/Holder words are equality anchors.
The source-free private output is not a source-law review or production gate.
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
import worldgen_26_2_stock_final_density_root_semantics as root
import worldgen_26_2_stock_finaldensity_min_root_fixture as observed
import worldgen_26_2_stock_final_density_singlepoint_capture as final

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityInnerSemantics262.java"
KIND="official_26_2_stock_final_density_inner_marker_rangechoice_unadmitted"
HEAD="HELVE26_2_FINAL_INNER_SHAPE"
VALUE="HELVE26_2_FINAL_INNER_VALUE"
END="HELVE26_2_FINAL_INNER_END"
FAIL="HELVE26_2_FINAL_INNER_FAILURE"
HEX=re.compile(r"[0-9a-f]{16}\Z")
NAME=re.compile(r"[A-Za-z0-9_.$]{1,180}\Z")
# Java's stock Marker$Type constants use normal Java identifiers, including
# UpperCamelCase (for example CacheAllInCell), not necessarily ALL_CAPS.
# Limit the *untrusted stream* to short ASCII identifiers; class identity
# is verified separately against the exact pinned enum declaring class.
ENUM=re.compile(r"[A-Za-z][A-Za-z0-9_]{0,79}\Z")
MARKER_ENUM_CLASS="net.minecraft.world.level.levelgen.DensityFunctions$Marker$Type"
GATES=(
    "mapped_squeeze_source_law_reviewed",
    "mapped_squeeze_rust_jvm_parity_qualified",
    "marker_noisechunk_lifecycle_reviewed",
    "range_choice_source_law_reviewed",
    "range_choice_rust_jvm_parity_qualified",
    "stock_noisechunk_full_lifecycle_qualified",
    "full_router_graph_qualified",
    "router_numeric_parity_qualified",
    "independent_var_sem_admitted",
    "production_worldgen_enabled",
    "source_text_included",
)

class InnerFrontierError(ValueError):
    """Real original stock JVM inner graph frontier has not been admitted."""


def finite_word(word:str)->bool:
    return bool(HEX.fullmatch(word)) and (int(word,16)>>52)&0x7ff!=0x7ff


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>130000:
        raise InnerFrontierError("unbounded original JVM inner evidence")
    rows=[line.split("|") for line in stdout.splitlines()
          if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in rows):
        raise InnerFrontierError("original JVM inner graph rejected review")
    anchor=observed.read_words()
    cursor=0
    shapes=[]
    vectors=[]
    for seed_idx,seed in enumerate(final.SEEDS):
        if cursor>=len(rows):
            raise InnerFrontierError("missing original root seed shape")
        shape=rows[cursor]
        cursor+=1
        if len(shape)!=11 or shape[:3]!=[HEAD,str(seed_idx),seed]:
            raise InnerFrontierError("original inner class/seed metadata changed")
        marker_type,marker_kind,wrapped_type,selector_type,in_type,out_type,low,high=shape[3:]
        if marker_type!=MARKER_ENUM_CLASS:
            raise InnerFrontierError("original Marker enum declaring class changed")
        if not ENUM.fullmatch(marker_kind):
            raise InnerFrontierError("unqualified stock Marker enum identifier")
        for label,name in (
            ("marker_wrapped",wrapped_type),
            ("range_selector",selector_type),
            ("range_when_in",in_type),
            ("range_when_out",out_type),
        ):
            if not NAME.fullmatch(name):
                raise InnerFrontierError("unqualified stock runtime class name: "+label)
        if not finite_word(low) or not finite_word(high):
            raise InnerFrontierError("unqualified stock RangeChoice threshold bits")
        shapes.append({
            "world_seed_bits":seed,"marker_type_class":marker_type,
            "marker_kind":marker_kind,"marker_wrapped_class":wrapped_type,
            "range_selector_class":selector_type,
            "range_in_class":in_type,"range_out_class":out_type,
            "range_min_inclusive_bits":"0x"+low,
            "range_max_exclusive_bits":"0x"+high,
        })
        for point_idx in range(32):
            idx=seed_idx*32+point_idx
            if cursor>=len(rows):
                raise InnerFrontierError("missing real original inner sample")
            row=rows[cursor]
            cursor+=1
            if (len(row)!=9 or row[:2]!=[VALUE,str(idx)] or
                not all(finite_word(value) for value in row[2:])):
                raise InnerFrontierError("invalid or nonfinite stock inner numeric witness")
            marker,wrapped,mapped,selector,in_value,out_value,holder=row[2:]
            if (mapped,holder)!=(anchor[idx][0],anchor[idx][1]):
                raise InnerFrontierError("old original JVM first-level child bit anchor changed")
            branch="both" if holder==in_value==out_value else (
                "in" if holder==in_value else "out" if holder==out_value else None
            )
            if branch is None:
                raise InnerFrontierError("original holder output matches no RangeChoice branch")
            vectors.append({
                **final.input_rows()[idx],
                "marker_bits":"0x"+marker,
                "marker_wrapped_bits":"0x"+wrapped,
                "mapped_bits":"0x"+mapped,
                "range_selector_bits":"0x"+selector,
                "range_in_bits":"0x"+in_value,
                "range_out_bits":"0x"+out_value,
                "holder_bits":"0x"+holder,
                "observed_matching_branch":branch,
            })
        if cursor>=len(rows) or rows[cursor]!=[END,str(seed_idx),"32"]:
            raise InnerFrontierError("missing inner review frame terminator")
        cursor+=1
    if cursor!=len(rows):
        raise InnerFrontierError("unexpected extra stock inner rows")
    # These shape aspects are seed-invariant on the pinned stock Overworld
    # registry; do not mistake runtime type identity for source law.
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!={k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise InnerFrontierError("unexplained seed-variant stock inner graph shape")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise InnerFrontierError("expected bounded source-free JSON report")
    base={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":final.frozen.SOURCE_SHA256,
        "official_server_sha256":final.frozen.SERVER_SHA256,
        "prior_first_level_operand_sha256":observed.FIXTURE_SHA256,
        "prior_original_first_level_report_sha256":observed.ORIGINAL_JSON_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_marker_range_branch_bits_observed":True,
        **{k:False for k in GATES},
    }
    if (set(report)!=set(base)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in base.items())):
        raise InnerFrontierError("unqualified inner evidence identity or gate changed")
    methods=report["source_methods"]
    if not isinstance(methods,dict):
        raise InnerFrontierError("missing pinned source method identities")
    if set(methods)!={"ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise InnerFrontierError("unqualified stock root source methods")
    for k,v in methods.items():
        if not isinstance(v,dict) or v.get("reviewed") is not False:
            raise InnerFrontierError("source method unexpectedly admitted: "+k)
    for name,pin in (
        ("ap2_compute",root.frozen_final.METHODS["ap2_compute"]),
        ("holder_holder_compute",root.frozen_final.METHODS["holder_holder_compute"]),
    ):
        v=methods[name]
        if tuple(v.get(k) for k in ("owner","signature","body_sha256","normalized_sha256"))!=pin:
            raise InnerFrontierError("original source identity changed: "+name)
    if (methods["mapped_delegate_compute"].get("owner")!=root.PURE_TRANSFORMER or
        methods["mapped_delegate_compute"].get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise InnerFrontierError("old PureTransformer source identity changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise InnerFrontierError("expected four original roots and 128 inner samples")
    rows=[]
    for seed_idx,shape in enumerate(shapes):
        if not isinstance(shape,dict) or set(shape)!={
            "world_seed_bits","marker_type_class","marker_kind",
            "marker_wrapped_class","range_selector_class","range_in_class",
            "range_out_class","range_min_inclusive_bits","range_max_exclusive_bits",
        }:
            raise InnerFrontierError("original inner shape keys missing")
        rows.append("|".join((HEAD,str(seed_idx),shape["world_seed_bits"],
            shape["marker_type_class"],shape["marker_kind"],
            shape["marker_wrapped_class"],shape["range_selector_class"],
            shape["range_in_class"],shape["range_out_class"],
            shape["range_min_inclusive_bits"][2:],
            shape["range_max_exclusive_bits"][2:])))
        for point_idx in range(32):
            idx=seed_idx*32+point_idx
            row=vectors[idx]
            context=final.input_rows()[idx]
            if (not isinstance(row,dict) or set(row)!=set(context)|{
                "marker_bits","marker_wrapped_bits","mapped_bits",
                "range_selector_bits","range_in_bits","range_out_bits",
                "holder_bits","observed_matching_branch",
            } or any(row.get(k)!=v for k,v in context.items())):
                raise InnerFrontierError("original ordered seed/XYZ frame changed")
            rows.append("|".join((VALUE,str(idx),
                *(row[k][2:] for k in (
                    "marker_bits","marker_wrapped_bits","mapped_bits",
                    "range_selector_bits","range_in_bits","range_out_bits","holder_bits",
                )))))
        rows.append("|".join((END,str(seed_idx),"32")))
    if parse_output("\n".join(rows))!=(shapes,vectors):
        raise InnerFrontierError("noncanonical inner output document")


def source_provenance(source:Path,db:Path,lock:Path,server:Path)->tuple[str,str,dict]:
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise InnerFrontierError("original source lock not stock Java 26.2")
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        methods=root.source_methods(conn)
    finally:
        conn.close()
    server_sha=official.sha256_file(server)
    if (source_sha!=final.frozen.SOURCE_SHA256 or
        server_sha!=final.frozen.SERVER_SHA256 or
        server_sha!=pin["runtime"]["server_sha256"]):
        raise InnerFrontierError("original source/runtime identity diverged")
    return source_sha,server_sha,methods


def observe(server:Path,*,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-262-final-inner-") as folder:
        work=Path(folder)
        jars=final.official.extract_classpath(server,work/"classpath")
        sources=(
            final.roots.BASE_BRIDGE,final.JAVA_SOURCE,
            root.JAVA_SOURCE,JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise InnerFrontierError("missing source-free reflection bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(x) for x in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise InnerFrontierError("original JVM diagnostic compile failure: "+
                                     build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityInnerSemantics262","--inner-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next((s for s in proc.stdout.splitlines()
                          if s.startswith(FAIL)),"no bounded failure tag")
            raise InnerFrontierError("original Java inner bridge rejected: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=final.improved.external_output(output)
    source_sha,server_sha,methods=source_provenance(source,db,lock,server)
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":source_sha,
        "official_server_sha256":server_sha,
        "prior_first_level_operand_sha256":observed.FIXTURE_SHA256,
        "prior_original_first_level_report_sha256":observed.ORIGINAL_JSON_SHA256,
        "source_methods":methods,
        "world_seeds":list(final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_marker_range_branch_bits_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{k:False for k in GATES},
    }
    validate(report)
    payload=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>90000:
        raise InnerFrontierError("unbounded source-free stock inner report")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as stream:
        stream.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_inner_samples":len(vectors),
        "marker_kind":shapes[0]["marker_kind"],
        "range_min_inclusive_bits":shapes[0]["range_min_inclusive_bits"],
        "range_max_exclusive_bits":shapes[0]["range_max_exclusive_bits"],
        **{k:False for k in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=final.primitive.DB)
    p.add_argument("--lock",type=Path,default=final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=final.primitive.CACHE)
    p.add_argument("--server-jar",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(
            source=args.source,db=args.db,lock=args.lock,server=server,output=args.output),
            sort_keys=True))
    except (InnerFrontierError,ValueError,OSError,KeyError,TypeError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FINAL INNER REVIEW OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
