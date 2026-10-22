#!/usr/bin/env python3
"""Original 26.2 ninth source-owner: one new true MulOrAdd child per point.

Also inspect the actual left-deep YClampedGradient record. Old eighth
left/right raw-bit outputs are independent immutable SHA-pinned anchors.
No previous original-JVM oracle is regenerated or copied into a new fixture.
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
import worldgen_26_2_stock_final_density_eighth_layer as eighth
import worldgen_26_2_stock_finaldensity_eighth_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityNinthLayer262.java"
KIND="original_26_2_finaldensity_ninth_layer_actual_muloradd_child_unadmitted"
HEAD="HELVE26_2_NINTH_SHAPE"
VALUE="HELVE26_2_NINTH_VALUE"
END="HELVE26_2_NINTH_END"
FAIL="HELVE26_2_NINTH_FAILURE"
CLASS=eighth.CLASS
SHAPE_FIELDS=(
    "left_from_y","left_to_y","left_from_value_bits","left_to_value_bits",
    "right_enum_class","right_op","right_arg_bits","right_child_class",
)
INT_FIELDS=("left_from_y","left_to_y")
BIT_FIELDS=("left_from_value_bits","left_to_value_bits","right_arg_bits")
WORDS=("new_right_child_bits","old_right_muloradd_bits","old_left_gradient_bits")
GATES=tuple(eighth.GATES)+(
    "ninth_layer_actual_right_child_shapes_qualified",
    "ninth_layer_unbounded_native_parity_admitted",
)


class NinthLayerError(ValueError):
    """Original stock ninth-layer numeric and source provenance unqualified."""


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def bits(value:float)->str:
    return "0x"+struct.pack(">d",value).hex()


def validate_shape(shape:dict)->None:
    if not isinstance(shape,dict) or set(shape)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise NinthLayerError("original ninth graph shape changed")
    for k in INT_FIELDS:
        v=shape[k]
        if type(v) is not int or not -(2**31)<=v<2**31:
            raise NinthLayerError("ninth actual gradient endpoint out of range")
    if shape["left_from_y"]>=shape["left_to_y"]:
        raise NinthLayerError("ninth original gradient record endpoints reversed")
    for k in BIT_FIELDS:
        w=shape[k]
        if not isinstance(w,str) or not w.startswith("0x") or (
                not eighth.seventh.sixth.fifth.fourth.third.second.inner.finite_word(w[2:])):
            raise NinthLayerError("actual ninth gradient/constant parameter not finite")
    for k in ("right_enum_class","right_child_class"):
        eighth.seventh.sixth.fifth.fourth.third.second.require_class(shape[k])
    if shape["right_enum_class"]!=CLASS+"MulOrAdd$Type" or (
            shape["right_op"] not in ("ADD","MUL")):
        raise NinthLayerError("actual ninth original right MulOrAdd record moved")
    eighth.seventh.sixth.fifth.fourth.third.second.require_enum(
        shape["right_op"],shape["right_enum_class"])


def candidate_telemetry(shapes:list[dict],vectors:list[dict])->dict:
    """Only diagnostic; no all-input MulOrAdd/gradient source-law assertion."""
    mismatch=[]
    for i,v in enumerate(vectors):
        s=shapes[i//32]
        x=number(v["new_right_child_bits"])
        arg=number(s["right_arg_bits"])
        guess=x+arg if s["right_op"]=="ADD" else x*arg
        if bits(guess)!=v["old_right_muloradd_bits"]:
            mismatch.append(i)
    return {
        "old_parent_anchored_points":len(vectors),
        "naive_muloradd_mismatch_count":len(mismatch),
        "naive_muloradd_first_mismatch_index":mismatch[0] if mismatch else -1,
        "source_law_admitted":False,
    }


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>125000:
        raise NinthLayerError("unbounded ninth original JVM stdout")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(line[0]==FAIL for line in frames):
        raise NinthLayerError("original ninth Java reflection failed")
    old=prior.load()
    points=eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    shapes=[]
    vectors=[]
    cursor=0
    for group,seed in enumerate(eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise NinthLayerError("missing bounded real ninth shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(group),seed]:
            raise NinthLayerError("source-owned ninth class shape/seed changed")
        s=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for k in INT_FIELDS:
            if not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,9})",s[k]):
                raise NinthLayerError("invalid original ninth gradient Y syntax")
            s[k]=int(s[k])
        for k in BIT_FIELDS:
            if not eighth.seventh.sixth.fifth.fourth.third.second.inner.finite_word(s[k]):
                raise NinthLayerError("invalid ninth original record IEEE bits")
            s[k]="0x"+s[k]
        s["world_seed_bits"]=seed
        validate_shape(s)
        shapes.append(s)
        for j in range(32):
            idx=group*32+j
            if cursor>=len(frames):
                raise NinthLayerError("missing stock ninth numeric point")
            row=frames[cursor]
            cursor+=1
            if len(row)!=2+len(WORDS) or row[:2]!=[VALUE,str(idx)] or (
                    not all(eighth.seventh.sixth.fifth.fourth.third.second.inner.finite_word(x)
                            for x in row[2:])):
                raise NinthLayerError("invalid bounded real ninth IEEE point")
            v=dict(zip(WORDS,("0x"+x for x in row[2:]),strict=True))
            if v["old_left_gradient_bits"][2:]!=old[idx][0] or (
                    v["old_right_muloradd_bits"][2:]!=old[idx][1]):
                raise NinthLayerError("independent immutable eighth parent changed")
            vectors.append({**points[idx],**v})
        if cursor>=len(frames) or frames[cursor]!=[END,str(group),"32"]:
            raise NinthLayerError("ninth original source-owner seed terminator missing")
        cursor+=1
    if cursor!=len(frames):
        raise NinthLayerError("extra ninth original source frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise NinthLayerError("ninth source class/record changed between seeds")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise NinthLayerError("original ninth owner report expected")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_eighth_fixture_sha256":prior.SHA256,
        "prior_eighth_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_ninth_layer_child_observed":True,
        "source_text_included":False,
        "muloradd_candidate_telemetry":report.get("muloradd_candidate_telemetry"),
        **{g:False for g in GATES},
    }
    if set(report)!=set(pins)|{"shapes","vectors"} or any(
            type(report.get(k)) is not type(v) or report[k]!=v for k,v in pins.items()):
        raise NinthLayerError("ninth source/provenance/admission changed")
    root=eighth.seventh.sixth.fifth.fourth.third.second.root
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise NinthLayerError("ninth actual source method set changed")
    for k in ("ap2_compute","holder_holder_compute"):
        m=methods[k]
        if not isinstance(m,dict) or m.get("reviewed") is not False or tuple(
                m.get(name) for name in ("owner","signature","body_sha256","normalized_sha256")
                )!=root.frozen_final.METHODS[k]:
            raise NinthLayerError("ninth original method provenance SHA changed")
    m=methods["mapped_delegate_compute"]
    if not isinstance(m,dict) or m.get("reviewed") is not False or (
            m.get("owner")!=root.PURE_TRANSFORMER or
            m.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise NinthLayerError("ninth source-mapped method changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or (
            not isinstance(vectors,list) or len(vectors)!=128):
        raise NinthLayerError("ninth original 4x32 finite context count changed")
    points=eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    rows=[]
    for i,s in enumerate(shapes):
        validate_shape(s)
        rows.append("|".join((HEAD,str(i),s["world_seed_bits"],
            *(s[k][2:] if k in BIT_FIELDS else str(s[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            idx=i*32+j
            v=vectors[idx]
            if not isinstance(v,dict) or set(v)!=set(points[idx])|set(WORDS) or (
                    any(v.get(k)!=z for k,z in points[idx].items())):
                raise NinthLayerError("ninth pinned XYZ/seed changed")
            rows.append("|".join((VALUE,str(idx),*(v[k][2:] for k in WORDS))))
        rows.append("|".join((END,str(i),"32")))
    if type(report["muloradd_candidate_telemetry"]) is not dict or (
            report["muloradd_candidate_telemetry"]!=candidate_telemetry(shapes,vectors)):
        raise NinthLayerError("ninth unadmitted MulOrAdd telemetry inconsistent")
    if parse_output("\n".join(rows))!=(shapes,vectors):
        raise NinthLayerError("ninth original source-owner report cannot round-trip")


def observe(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-ninth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        f=eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            eighth.seventh.sixth.JAVA_SOURCE,
            eighth.seventh.JAVA_SOURCE,
            eighth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise NinthLayerError("missing bounded source-free ninth Java bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise NinthLayerError("bounded ninth javac failed: "+build.stderr[:550])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityNinthLayer262","--ninth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            reason=next((s for s in proc.stdout.splitlines() if s.startswith(FAIL)),
                        "no bounded original ninth-layer failure tag")
            raise NinthLayerError("original 26.2 ninth failed: "+reason[:160])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=eighth.seventh.sixth.fifth.fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=eighth.seventh.sixth.fifth.fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_eighth_fixture_sha256":prior.SHA256,
        "prior_eighth_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_ninth_layer_child_observed":True,
        "source_text_included":False,
        "shapes":shapes,"vectors":vectors,
        "muloradd_candidate_telemetry":candidate_telemetry(shapes,vectors),
        **{g:False for g in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>105000:
        raise NinthLayerError("unbounded ninth original source-free JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_ninth_original_input_rows":len(vectors),
        "right_operation":shapes[0]["right_op"],
        "right_child_class":shapes[0]["right_child_class"],
        "muloradd_candidate_telemetry":candidate_telemetry(shapes,vectors),
        **{g:False for g in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.CACHE)
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
    except (NinthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 NINTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
