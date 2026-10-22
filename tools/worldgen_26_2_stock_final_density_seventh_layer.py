#!/usr/bin/env python3
"""Original stock 26.2 seventh-layer NEW RangeChoice and MulOrAdd children.

Only seven newly exposed input words per XYZ; three sixth-layer words are
independent equality anchors, not a repeat of any frozen oracle. This is
source-owner-only, bounded, fail-closed and never production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import struct
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

import official_state_data as official
import worldgen_26_2_stock_final_density_sixth_layer as sixth
import worldgen_26_2_stock_finaldensity_sixth_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensitySeventhLayer262.java"
KIND="original_26_2_finaldensity_seventh_layer_actual_rangechoice_children_unadmitted"
HEAD="HELVE26_2_SEVENTH_SHAPE"
VALUE="HELVE26_2_SEVENTH_VALUE"
END="HELVE26_2_SEVENTH_END"
FAIL="HELVE26_2_SEVENTH_FAILURE"
CLASS=sixth.CLASS
SHAPE_FIELDS=(
    "left_deep_enum_class","left_deep_op","left_deep_arg_bits","left_deep_child_class",
    "left_choice_min_bits","left_choice_max_bits",
    "left_choice_selector_class","left_choice_in_class","left_choice_out_class",
    "right_choice_min_bits","right_choice_max_bits",
    "right_choice_selector_class","right_choice_in_class","right_choice_out_class",
)
PARAM_FIELDS=(
    "left_deep_arg_bits",
    "left_choice_min_bits","left_choice_max_bits",
    "right_choice_min_bits","right_choice_max_bits",
)
WORDS=(
    "left_deep_child_bits","left_deep_output_bits",
    "left_selector_bits","left_in_bits","left_out_bits","left_choice_output_bits",
    "right_selector_bits","right_in_bits","right_out_bits","right_choice_output_bits",
)
NEW_FIELDS=(
    "left_deep_child_bits","left_selector_bits","left_in_bits","left_out_bits",
    "right_selector_bits","right_in_bits","right_out_bits",
)
GATES=tuple(sixth.GATES)+(
    "seventh_layer_actual_choice_shapes_qualified",
    "seventh_layer_rust_jvm_numeric_parity_qualified",
)


class SeventhLayerError(ValueError):
    """Actual source-owned seventh-layer graph evidence unqualified."""


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def pack(value:float)->str:
    return "0x"+struct.pack(">d",value).hex()


def validate_shape(s:dict)->None:
    if not isinstance(s,dict) or set(s)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise SeventhLayerError("original seventh-layer runtime schema changed")
    for key in SHAPE_FIELDS:
        if key.endswith("_class"):
            sixth.fifth.fourth.third.second.require_class(s[key])
    for key in PARAM_FIELDS:
        v=s[key]
        if not isinstance(v,str) or not v.startswith("0x") or (
                not sixth.fifth.fourth.third.second.inner.finite_word(v[2:])):
            raise SeventhLayerError("nonfinite seventh-layer source-owned scalar")
    if s["left_deep_enum_class"]!=CLASS+"MulOrAdd$Type" or (
            s["left_deep_op"] not in ("ADD","MUL")):
        raise SeventhLayerError("unsupported original nested MulOrAdd enum")
    sixth.fifth.fourth.third.second.require_enum(
        s["left_deep_op"],s["left_deep_enum_class"])
    for name in ("left_choice","right_choice"):
        if number(s[name+"_min_bits"])>=number(s[name+"_max_bits"]):
            raise SeventhLayerError("actual seventh-layer RangeChoice bounds reversed")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>205000:
        raise SeventhLayerError("unbounded original seventh-layer stdout")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise SeventhLayerError("original seventh-layer Java reflection failed")
    old=prior.load()
    points=sixth.fifth.fourth.third.second.final.input_rows()
    shapes=[]
    vectors=[]
    cursor=0
    for group,seed in enumerate(sixth.fifth.fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise SeventhLayerError("missing seed graph shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(group),seed]:
            raise SeventhLayerError("seventh-layer bounded source shape differs")
        shape=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for field in PARAM_FIELDS:
            if not sixth.fifth.fourth.third.second.inner.finite_word(shape[field]):
                raise SeventhLayerError("actual seventh-layer parameter bits invalid")
            shape[field]="0x"+shape[field]
        shape["world_seed_bits"]=seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            idx=32*group+j
            if cursor>=len(frames):
                raise SeventhLayerError("missing seventh-layer original point")
            row=frames[cursor]
            cursor+=1
            if len(row)!=2+len(WORDS) or row[:2]!=[VALUE,str(idx)] or (
                    not all(sixth.fifth.fourth.third.second.inner.finite_word(w) for w in row[2:])):
                raise SeventhLayerError("invalid actual seventh-layer finite IEEE frame")
            entry=dict(zip(WORDS,("0x"+w for w in row[2:]),strict=True))
            expected={
                "left_deep_output_bits":old[idx][0],
                "left_choice_output_bits":old[idx][2],
                "right_choice_output_bits":old[idx][3],
            }
            if any(entry[k][2:]!=v for k,v in expected.items()):
                raise SeventhLayerError("sixth-layer original parent equality failed")
            child=number(entry["left_deep_child_bits"])
            arg=number(shape["left_deep_arg_bits"])
            result=child+arg if shape["left_deep_op"]=="ADD" else child*arg
            if pack(result)!=entry["left_deep_output_bits"]:
                raise SeventhLayerError("nested source MulOrAdd actual operation mismatch")
            for name in ("left","right"):
                sel=number(entry[name+"_selector_bits"])
                minimum=number(shape[name+"_choice_min_bits"])
                maximum=number(shape[name+"_choice_max_bits"])
                selected=entry[name+"_in_bits"] if minimum<=sel<maximum else entry[name+"_out_bits"]
                if selected!=entry[name+"_choice_output_bits"]:
                    raise SeventhLayerError("seventh-layer actual RangeChoice branch mismatch")
            vectors.append({**points[idx],**entry})
        if cursor>=len(frames) or frames[cursor]!=[END,str(group),"32"]:
            raise SeventhLayerError("seventh-layer source-owned terminator missing")
        cursor+=1
    if cursor!=len(frames):
        raise SeventhLayerError("extra stock seventh-layer data")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise SeventhLayerError("source graph changed across seeds")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise SeventhLayerError("seventh-layer source-owned report required")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_sixth_fixture_sha256":prior.SHA256,
        "prior_sixth_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_seventh_layer_inputs_observed":True,
        "source_text_included":False,
        **{g:False for g in GATES},
    }
    if set(report)!=set(pins)|{"shapes","vectors"} or any(
            type(report.get(k)) is not type(v) or report[k]!=v for k,v in pins.items()):
        raise SeventhLayerError("original seventh-layer source/registry/gates changed")
    root=sixth.fifth.fourth.third.second.root
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise SeventhLayerError("original seventh-layer source-method set changed")
    for name in ("ap2_compute","holder_holder_compute"):
        m=methods[name]
        if not isinstance(m,dict) or m.get("reviewed") is not False or tuple(
                m.get(k) for k in ("owner","signature","body_sha256","normalized_sha256")
                )!=root.frozen_final.METHODS[name]:
            raise SeventhLayerError("actual seventh-layer source-method pin changed")
    m=methods["mapped_delegate_compute"]
    if not isinstance(m,dict) or m.get("reviewed") is not False or (
            m.get("owner")!=root.PURE_TRANSFORMER or
            m.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise SeventhLayerError("seventh-layer mapped source method pin changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or (
            not isinstance(vectors,list) or len(vectors)!=128):
        raise SeventhLayerError("expected exactly 4x32 original points")
    points=sixth.fifth.fourth.third.second.final.input_rows()
    lines=[]
    for group,s in enumerate(shapes):
        validate_shape(s)
        lines.append("|".join((HEAD,str(group),s["world_seed_bits"],
            *(s[k][2:] if k in PARAM_FIELDS else str(s[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            idx=group*32+j
            row=vectors[idx]
            if not isinstance(row,dict) or set(row)!=set(points[idx])|set(WORDS) or (
                    any(row.get(k)!=v for k,v in points[idx].items())):
                raise SeventhLayerError("source-owned seventh-layer XYZ mismatch")
            lines.append("|".join((VALUE,str(idx),*(row[k][2:] for k in WORDS))))
        lines.append("|".join((END,str(group),"32")))
    if parse_output("\n".join(lines))!=(shapes,vectors):
        raise SeventhLayerError("seventh-layer report did not round-trip")


def observe(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-seventh-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        f=sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            sixth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise SeventhLayerError("missing seventh-layer source-free Java bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise SeventhLayerError("bounded seventh-layer javac failed: "+build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensitySeventhLayer262","--seventh-layer-128"],
            input="\n".join(
                f"{v['world_seed_bits']}\t{v['block_x']}\t{v['block_y']}\t{v['block_z']}"
                for v in sixth.fifth.fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            phase=next((s for s in proc.stdout.splitlines() if s.startswith(FAIL)),
                       "no bounded original seventh-layer failure tag")
            raise SeventhLayerError("original 26.2 seventh failed: "+phase[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=sixth.fifth.fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=sixth.fifth.fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_sixth_fixture_sha256":prior.SHA256,
        "prior_sixth_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_seventh_layer_inputs_observed":True,
        "source_text_included":False,
        "shapes":shapes,"vectors":vectors,
        **{g:False for g in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>182000:
        raise SeventhLayerError("unbounded original seventh-layer JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_original_seventh_input_rows":len(vectors),
        "left_deep_operator":shapes[0]["left_deep_op"],
        "left_choice_bounds_bits":(shapes[0]["left_choice_min_bits"],
                                   shapes[0]["left_choice_max_bits"]),
        "right_choice_bounds_bits":(shapes[0]["right_choice_min_bits"],
                                    shapes[0]["right_choice_max_bits"]),
        **{g:False for g in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=sixth.fifth.fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=sixth.fifth.fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=sixth.fifth.fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=sixth.fifth.fourth.third.second.final.primitive.CACHE)
    p.add_argument("--server-jar",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            meta,_=official.resolve("26.2",args.cache)
            server=meta["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
                                 server=server,output=args.output),sort_keys=True))
    except (SeventhLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 SEVENTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
