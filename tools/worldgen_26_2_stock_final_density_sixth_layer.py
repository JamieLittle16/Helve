#!/usr/bin/env python3
"""Original stock 26.2 sixth-layer four NEW child inputs; fifth-layer anchors.

Observe *only* true newly unresolved MulOrAdd and ABS Marker operands, plus
two independent YClampedGradient record shapes. This source-owning diagnostic
does not repeat previous root/inner/second/third/fourth/fifth or NoiseChunk
oracles, claim all-input source semantics, or enable production worldgen.
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
import worldgen_26_2_stock_final_density_fifth_layer as fifth
import worldgen_26_2_stock_finaldensity_fifth_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensitySixthLayer262.java"
KIND="original_26_2_finaldensity_sixth_layer_actual_children_unadmitted"
HEAD="HELVE26_2_SIXTH_SHAPE"
VALUE="HELVE26_2_SIXTH_VALUE"
END="HELVE26_2_SIXTH_END"
FAIL="HELVE26_2_SIXTH_FAILURE"
CLASS=fifth.CLASS
SHAPE_FIELDS=(
    "left_gradient_from_y","left_gradient_to_y",
    "left_gradient_from_value_bits","left_gradient_to_value_bits",
    "outside_gradient_from_y","outside_gradient_to_y",
    "outside_gradient_from_value_bits","outside_gradient_to_value_bits",
    "left_mul_enum_class","left_mul_op","left_mul_arg_bits","left_mul_child_class",
    "outside_mul_enum_class","outside_mul_op",
    "outside_mul_arg_bits","outside_mul_child_class",
    "left_marker_enum_class","left_marker_kind","left_marker_child_class",
    "right_marker_enum_class","right_marker_kind","right_marker_child_class",
)
INT_FIELDS=(
    "left_gradient_from_y","left_gradient_to_y",
    "outside_gradient_from_y","outside_gradient_to_y",
)
PARAM_FIELDS=(
    "left_gradient_from_value_bits","left_gradient_to_value_bits",
    "outside_gradient_from_value_bits","outside_gradient_to_value_bits",
    "left_mul_arg_bits","outside_mul_arg_bits",
)
WORDS=(
    "left_gradient_old_bits","left_mul_child_bits","left_mul_old_bits",
    "outside_gradient_old_bits","outside_mul_child_bits","outside_mul_old_bits",
    "left_marker_child_bits","left_marker_old_bits",
    "right_marker_child_bits","right_marker_old_bits",
)
NEW_FIELDS=(
    "left_mul_child_bits","outside_mul_child_bits",
    "left_marker_child_bits","right_marker_child_bits",
)
GATES=tuple(fifth.GATES)+(
    "sixth_layer_actual_child_shapes_qualified",
    "sixth_layer_rust_jvm_numeric_parity_qualified",
)


class SixthLayerError(ValueError):
    """Original source-backed sixth-layer shape or parent words are unqualified."""


def value(bits:str)->float:
    return struct.unpack(">d",bytes.fromhex(bits[2:]))[0]


def pack(number:float)->str:
    return "0x"+struct.pack(">d",number).hex()


def validate_shape(shape:dict)->None:
    if not isinstance(shape,dict) or set(shape)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise SixthLayerError("original sixth-layer record schema differs")
    for k in SHAPE_FIELDS:
        if k.endswith("_class"):
            fifth.fourth.third.second.require_class(shape[k])
    for k in INT_FIELDS:
        v=shape[k]
        if type(v) is not int or not -(2**31)<=v<2**31:
            raise SixthLayerError("sixth-layer gradient height out of range")
    for p in ("left","outside"):
        if shape[p+"_gradient_from_y"]>=shape[p+"_gradient_to_y"]:
            raise SixthLayerError("actual source gradient Y bounds reversed")
    for k in PARAM_FIELDS:
        v=shape[k]
        if not isinstance(v,str) or not v.startswith("0x") or (
                not fifth.fourth.third.second.inner.finite_word(v[2:])):
            raise SixthLayerError("sixth-layer gradient or constant word nonfinite")
    enums=(
        ("left_mul_op","left_mul_enum_class",CLASS+"MulOrAdd$Type"),
        ("outside_mul_op","outside_mul_enum_class",CLASS+"MulOrAdd$Type"),
        ("left_marker_kind","left_marker_enum_class",CLASS+"Marker$Type"),
        ("right_marker_kind","right_marker_enum_class",CLASS+"Marker$Type"),
    )
    for op,klass,exact in enums:
        if shape[klass]!=exact:
            raise SixthLayerError("unqualified actual sixth-layer enum declaring class")
        fifth.fourth.third.second.require_enum(shape[op],shape[klass])
    if shape["left_mul_op"] not in ("ADD","MUL") or (
            shape["outside_mul_op"] not in ("ADD","MUL")):
        raise SixthLayerError("unknown actual original MulOrAdd operation")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>170000:
        raise SixthLayerError("unbounded stock sixth-layer original JVM output")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise SixthLayerError("original sixth-layer Java reflection failed")
    previous=prior.load()
    points=fifth.fourth.third.second.final.input_rows()
    shapes=[]
    vectors=[]
    cursor=0
    for seed_idx,seed in enumerate(fifth.fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise SixthLayerError("original sixth-layer expected shape missing")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(seed_idx),seed]:
            raise SixthLayerError("sixth-layer bounded shape frame moved")
        shape=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for k in INT_FIELDS:
            if not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,9})",shape[k]):
                raise SixthLayerError("invalid original gradient height syntax")
            shape[k]=int(shape[k])
        for k in PARAM_FIELDS:
            if not fifth.fourth.third.second.inner.finite_word(shape[k]):
                raise SixthLayerError("invalid original sixth-layer parameter bits")
            shape[k]="0x"+shape[k]
        shape["world_seed_bits"]=seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index=seed_idx*32+j
            if cursor>=len(frames):
                raise SixthLayerError("missing source-owned sixth-layer original point")
            row=frames[cursor]
            cursor+=1
            if len(row)!=2+len(WORDS) or row[:2]!=[VALUE,str(index)] or (
                    not all(fifth.fourth.third.second.inner.finite_word(w) for w in row[2:])):
                raise SixthLayerError("invalid actual sixth-layer finite IEEE words")
            measured=dict(zip(WORDS,("0x"+x for x in row[2:]),strict=True))
            old=previous[index]
            anchors=(
                ("left_gradient_old_bits",old[0]),
                ("left_mul_old_bits",old[1]),
                ("outside_gradient_old_bits",old[2]),
                ("outside_mul_old_bits",old[3]),
                ("left_marker_old_bits",old[4]),
                ("right_marker_old_bits",old[5]),
            )
            if any(measured[k][2:]!=w for k,w in anchors):
                raise SixthLayerError("original fifth-layer independent parent anchor changed")
            for prefix in ("left","outside"):
                child=value(measured[prefix+"_mul_child_bits"])
                arg=value(shape[prefix+"_mul_arg_bits"])
                actual=child+arg if shape[prefix+"_mul_op"]=="ADD" else child*arg
                if pack(actual)!=measured[prefix+"_mul_old_bits"]:
                    raise SixthLayerError("actual sixth-layer constant operator not bit-exact")
            for prefix in ("left","right"):
                if measured[prefix+"_marker_child_bits"]!=measured[prefix+"_marker_old_bits"]:
                    raise SixthLayerError("sixth-layer Marker single-point forwarding changed")
            vectors.append({**points[index],**measured})
        if cursor>=len(frames) or frames[cursor]!=[END,str(seed_idx),"32"]:
            raise SixthLayerError("missing sixth-layer source-owning terminator")
        cursor+=1
    if cursor!=len(frames):
        raise SixthLayerError("extra source-free original sixth-layer records")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise SixthLayerError("real sixth-layer structural record differs by seed")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise SixthLayerError("original sixth-layer source-free JSON expected")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":fifth.fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_fifth_fixture_sha256":prior.SHA256,
        "prior_fifth_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_sixth_layer_inputs_observed":True,
        "source_text_included":False,
        **{gate:False for gate in GATES},
    }
    if set(report)!=set(pins)|{"shapes","vectors"} or any(
            type(report.get(k)) is not type(v) or report[k]!=v for k,v in pins.items()):
        raise SixthLayerError("original sixth-layer provenance/source/gate pin changed")
    root=fifth.fourth.third.second.root
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise SixthLayerError("sixth-layer stock source method owner mismatch")
    for name in ("ap2_compute","holder_holder_compute"):
        m=methods[name]
        if not isinstance(m,dict) or m.get("reviewed") is not False or tuple(
                m.get(k) for k in (
                    "owner","signature","body_sha256","normalized_sha256")
                )!=root.frozen_final.METHODS[name]:
            raise SixthLayerError("sixth-layer original source-method pin changed")
    m=methods["mapped_delegate_compute"]
    if not isinstance(m,dict) or m.get("reviewed") is not False or (
            m.get("owner")!=root.PURE_TRANSFORMER or
            m.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise SixthLayerError("sixth-layer mapped source-method pin changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise SixthLayerError("sixth-layer must have 4x32 source-owned contexts")
    points=fifth.fourth.third.second.final.input_rows()
    lines=[]
    for i,shape in enumerate(shapes):
        validate_shape(shape)
        lines.append("|".join((HEAD,str(i),shape["world_seed_bits"],
            *(shape[k][2:] if k in PARAM_FIELDS else str(shape[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            n=i*32+j
            v=vectors[n]
            if not isinstance(v,dict) or set(v)!=set(points[n])|set(WORDS) or (
                    any(v.get(k)!=a for k,a in points[n].items())):
                raise SixthLayerError("actual sixth-layer XYZ/seed changed")
            lines.append("|".join((VALUE,str(n),*(v[k][2:] for k in WORDS))))
        lines.append("|".join((END,str(i),"32")))
    if parse_output("\n".join(lines))!=(shapes,vectors):
        raise SixthLayerError("source-owning sixth-layer original report cannot round-trip")


def source_observation(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-sixth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        sources=(
            fifth.fourth.third.second.final.roots.BASE_BRIDGE,
            fifth.fourth.third.second.final.JAVA_SOURCE,
            fifth.fourth.third.second.root.JAVA_SOURCE,
            fifth.fourth.third.second.inner.JAVA_SOURCE,
            fifth.fourth.third.second.JAVA_SOURCE,
            fifth.fourth.third.JAVA_SOURCE,
            fifth.fourth.JAVA_SOURCE,
            fifth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise SixthLayerError("missing original source-free sixth-layer Java bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise SixthLayerError("sixth-layer source-free javac failed: "+build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensitySixthLayer262","--sixth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in fifth.fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next((s for s in proc.stdout.splitlines() if s.startswith(FAIL)),
                         "no bounded source-free JVM failure tag")
            raise SixthLayerError("original stock 26.2 sixth-layer failed: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=fifth.fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=fifth.fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=source_observation(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_fifth_fixture_sha256":prior.SHA256,
        "prior_fifth_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_sixth_layer_inputs_observed":True,
        "source_text_included":False,
        "shapes":shapes,"vectors":vectors,
        **{gate:False for gate in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>160000:
        raise SixthLayerError("unbounded sixth-layer source-free output")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as stream:
        stream.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_sixth_layer_input_rows":len(vectors),
        "left_mul_operation":shapes[0]["left_mul_op"],
        "outside_mul_operation":shapes[0]["outside_mul_op"],
        "left_abs_marker_kind":shapes[0]["left_marker_kind"],
        "right_abs_marker_kind":shapes[0]["right_marker_kind"],
        **{gate:False for gate in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=fifth.fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=fifth.fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=fifth.fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=fifth.fourth.third.second.final.primitive.CACHE)
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
    except (SixthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 SIXTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
