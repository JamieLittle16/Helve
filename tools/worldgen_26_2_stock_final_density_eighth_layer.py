#!/usr/bin/env python3
"""Bounded original JVM 26.2 eighth left Ap2 and selector target observation.

Only two genuinely NEW child IEEE words per point; existing seventh values
are fixed prior anchors, not re-exported or committed as new oracle values.
No Java source or private registries, no stock NoiseChunk or production gate.
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
import worldgen_26_2_stock_final_density_seventh_layer as seventh
import worldgen_26_2_stock_finaldensity_seventh_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityEighthLayer262.java"
KIND="original_26_2_finaldensity_eighth_layer_ap2_and_holder_targets_unadmitted"
HEAD="HELVE26_2_EIGHTH_SHAPE"
VALUE="HELVE26_2_EIGHTH_VALUE"
END="HELVE26_2_EIGHTH_END"
FAIL="HELVE26_2_EIGHTH_FAILURE"
CLASS=seventh.CLASS
SHAPE_FIELDS=(
    "deep_ap2_enum_class","deep_ap2_op","deep_ap2_left_class","deep_ap2_right_class",
    "left_target_class","left_from_y","left_to_y",
    "left_from_value_bits","left_to_value_bits",
    "right_target_class","right_from_y","right_to_y",
    "right_from_value_bits","right_to_value_bits",
)
INT_FIELDS=("left_from_y","left_to_y","right_from_y","right_to_y")
PARAM_FIELDS=("left_from_value_bits","left_to_value_bits",
              "right_from_value_bits","right_to_value_bits")
WORDS=(
    "ap2_left_bits","ap2_right_bits","ap2_old_bits",
    "left_target_bits","left_selector_old_bits",
    "right_target_bits","right_selector_old_bits",
)
NEW_FIELDS=("ap2_left_bits","ap2_right_bits")
GATES=tuple(seventh.GATES)+(
    "eighth_layer_real_ap2_shapes_qualified",
    "eighth_layer_selector_target_law_qualified",
)


class EighthLayerError(ValueError):
    """Fail-closed stock original eighth-layer evidence qualification."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def pack(number:float)->str:
    return "0x"+struct.pack(">d",number).hex()


def validate_shape(s:dict)->None:
    if not isinstance(s,dict) or set(s)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise EighthLayerError("original eighth-layer shape schema changed")
    for key in SHAPE_FIELDS:
        if key.endswith("_class"):
            seventh.sixth.fifth.fourth.third.second.require_class(s[key])
    if s["deep_ap2_enum_class"]!=CLASS+"TwoArgumentSimpleFunction$Type" or (
            s["deep_ap2_op"] not in ("ADD","MUL","MIN","MAX")):
        raise EighthLayerError("genuine source Ap2 enum moved")
    if any(s[k]!="YClampedGradient" and s[k]!=CLASS+"YClampedGradient"
           for k in ("left_target_class","right_target_class")):
        raise EighthLayerError("actual selector target not reflected Y-gradient")
    for k in INT_FIELDS:
        n=s[k]
        if type(n) is not int or not -(2**31)<=n<2**31:
            raise EighthLayerError("invalid original gradient endpoint")
    if s["left_from_y"]>=s["left_to_y"] or s["right_from_y"]>=s["right_to_y"]:
        raise EighthLayerError("invalid eighth gradient bound order")
    for k in PARAM_FIELDS:
        w=s[k]
        if not isinstance(w,str) or not w.startswith("0x") or (
                not seventh.sixth.fifth.fourth.third.second.inner.finite_word(w[2:])):
            raise EighthLayerError("invalid gradient real parameter")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>120000:
        raise EighthLayerError("unbounded eighth original JVM output")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(frame[0]==FAIL for frame in frames):
        raise EighthLayerError("original eighth reflection failure")
    old=prior.load()
    points=seventh.sixth.fifth.fourth.third.second.final.input_rows()
    shapes=[]
    vectors=[]
    cursor=0
    for i,seed in enumerate(seventh.sixth.fifth.fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise EighthLayerError("original eighth source shape missing")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(i),seed]:
            raise EighthLayerError("bounded eighth Java shape row changed")
        s=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for k in INT_FIELDS:
            if not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,9})",s[k]):
                raise EighthLayerError("actual eighth gradient integer syntax changed")
            s[k]=int(s[k])
        for k in PARAM_FIELDS:
            if not seventh.sixth.fifth.fourth.third.second.inner.finite_word(s[k]):
                raise EighthLayerError("eighth gradient IEEE parameter invalid")
            s[k]="0x"+s[k]
        s["world_seed_bits"]=seed
        validate_shape(s)
        shapes.append(s)
        for j in range(32):
            idx=i*32+j
            if cursor>=len(frames):
                raise EighthLayerError("original eighth source-owned point missing")
            row=frames[cursor]
            cursor+=1
            if len(row)!=2+len(WORDS) or row[:2]!=[VALUE,str(idx)] or (
                    not all(seventh.sixth.fifth.fourth.third.second.inner.finite_word(w)
                            for w in row[2:])):
                raise EighthLayerError("eighth bounded finite IEEE frame invalid")
            entry=dict(zip(WORDS,("0x"+w for w in row[2:]),strict=True))
            parent=old[idx]
            if (entry["ap2_old_bits"][2:]!=parent[0] or
                entry["left_selector_old_bits"][2:]!=parent[1] or
                entry["right_selector_old_bits"][2:]!=parent[4]):
                raise EighthLayerError("immutable seventh independent parent moved")
            if entry["left_target_bits"]!=entry["left_selector_old_bits"] or (
                    entry["right_target_bits"]!=entry["right_selector_old_bits"]):
                raise EighthLayerError("actual original Holder target forwarding changed")
            a=value(entry["ap2_left_bits"])
            b=value(entry["ap2_right_bits"])
            if s["deep_ap2_op"] in ("ADD","MUL"):
                result=a+b if s["deep_ap2_op"]=="ADD" else a*b
                if pack(result)!=entry["ap2_old_bits"]:
                    raise EighthLayerError("original eighth Ap2 real arithmetic changed")
            # MIN/MAX source law is not presumed from the enum alone.
            vectors.append({**points[idx],**entry})
        if cursor>=len(frames) or frames[cursor]!=[END,str(i),"32"]:
            raise EighthLayerError("original eighth seed-end marker missing")
        cursor+=1
    if cursor!=len(frames):
        raise EighthLayerError("extra eighth source-free frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise EighthLayerError("original eighth graph changed between seeds")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise EighthLayerError("actual eighth source-owned JSON required")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_seventh_fixture_sha256":prior.SHA256,
        "prior_seventh_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_eighth_layer_inputs_observed":True,
        "source_text_included":False,
        **{g:False for g in GATES},
    }
    if set(report)!=set(pins)|{"shapes","vectors"} or any(
            type(report.get(k)) is not type(v) or report[k]!=v for k,v in pins.items()):
        raise EighthLayerError("original eighth source/provenance/gate changed")
    root=seventh.sixth.fifth.fourth.third.second.root
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise EighthLayerError("original eighth source method set changed")
    for name in ("ap2_compute","holder_holder_compute"):
        m=methods[name]
        if not isinstance(m,dict) or m.get("reviewed") is not False or tuple(
                m.get(k) for k in ("owner","signature","body_sha256","normalized_sha256")
                )!=root.frozen_final.METHODS[name]:
            raise EighthLayerError("actual eighth source method SHA moved")
    m=methods["mapped_delegate_compute"]
    if not isinstance(m,dict) or m.get("reviewed") is not False or (
            m.get("owner")!=root.PURE_TRANSFORMER or
            m.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise EighthLayerError("original eighth mapped delegate source SHA moved")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or (
            not isinstance(vectors,list) or len(vectors)!=128):
        raise EighthLayerError("exact original eighth 4x32 points required")
    points=seventh.sixth.fifth.fourth.third.second.final.input_rows()
    lines=[]
    for i,s in enumerate(shapes):
        validate_shape(s)
        lines.append("|".join((HEAD,str(i),s["world_seed_bits"],
            *(s[k][2:] if k in PARAM_FIELDS else str(s[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            idx=i*32+j
            v=vectors[idx]
            if not isinstance(v,dict) or set(v)!=set(points[idx])|set(WORDS) or (
                    any(v.get(k)!=p for k,p in points[idx].items())):
                raise EighthLayerError("original eighth XYZ/seed changed")
            lines.append("|".join((VALUE,str(idx),*(v[k][2:] for k in WORDS))))
        lines.append("|".join((END,str(i),"32")))
    if parse_output("\n".join(lines))!=(shapes,vectors):
        raise EighthLayerError("eighth source-owner receipt cannot round-trip")


def observe(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-eighth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        f=seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            seventh.sixth.JAVA_SOURCE,
            seventh.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise EighthLayerError("missing eighth original Java source-free bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise EighthLayerError("bounded eighth-layer javac failed: "+build.stderr[:600])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityEighthLayer262","--eighth-layer-128"],
            input="\n".join(
                f"{v['world_seed_bits']}\t{v['block_x']}\t{v['block_y']}\t{v['block_z']}"
                for v in seventh.sixth.fifth.fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            phase=next((line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                       "no bounded original eighth-layer failure tag")
            raise EighthLayerError("original 26.2 eighth failed: "+phase[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=seventh.sixth.fifth.fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=seventh.sixth.fifth.fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_seventh_fixture_sha256":prior.SHA256,
        "prior_seventh_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_eighth_layer_inputs_observed":True,
        "source_text_included":False,
        "shapes":shapes,"vectors":vectors,
        **{gate:False for gate in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>110000:
        raise EighthLayerError("unbounded eighth source-free JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_eighth_original_child_rows":len(vectors),
        "real_deeper_ap2_type":shapes[0]["deep_ap2_op"],
        "left_selector_target_type":shapes[0]["left_target_class"],
        "right_selector_target_type":shapes[0]["right_target_class"],
        **{gate:False for gate in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=seventh.sixth.fifth.fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=seventh.sixth.fifth.fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=seventh.sixth.fifth.fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=seventh.sixth.fifth.fourth.third.second.final.primitive.CACHE)
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
    except (EighthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 EIGHTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
