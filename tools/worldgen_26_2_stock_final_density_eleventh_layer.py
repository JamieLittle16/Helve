#!/usr/bin/env python3
"""Bounded original JVM 26.2 tenth: one genuine deep-right RangeChoice only.

The real ninth RangeChoice result is already frozen as ONE old child word.
New tenth source owns three distinct children and original range bounds;
no source-law/NoiseChunk/production admission and no previous recapture.
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
import worldgen_26_2_stock_final_density_ninth_layer as ninth
import worldgen_26_2_stock_finaldensity_ninth_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityTenthLayer262.java"
KIND="original_26_2_finaldensity_tenth_right_rangechoice_children_unadmitted"
HEAD="HELVE26_2_TENTH_SHAPE"
VALUE="HELVE26_2_TENTH_VALUE"
END="HELVE26_2_TENTH_END"
FAIL="HELVE26_2_TENTH_FAILURE"
SHAPE_FIELDS=("min_bits","max_bits","selector_class","when_in_class","when_out_class")
BIT_FIELDS=("min_bits","max_bits")
WORDS=("selector_bits","when_in_bits","when_out_bits","old_rangechoice_bits")
NEW_FIELDS=("selector_bits","when_in_bits","when_out_bits")
GATES=tuple(ninth.GATES)+(
    "tenth_layer_real_rangechoice_shapes_qualified",
    "tenth_layer_full_source_law_admitted",
)


class TenthLayerError(ValueError):
    """Original tenth fixed-depth JVM source owner is unqualified."""


def finite_bits(word:str)->bool:
    return ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner.finite_word(word)


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def choice_telemetry(shapes:list[dict],vectors:list[dict])->dict:
    bad=[]
    for i,v in enumerate(vectors):
        shape=shapes[i//32]
        selector=value(v["selector_bits"])
        lower=value(shape["min_bits"])
        upper=value(shape["max_bits"])
        expected=v["when_in_bits"] if lower<=selector<upper else v["when_out_bits"]
        if expected!=v["old_rangechoice_bits"]:
            bad.append(i)
    return {
        "original_bounded_choice_samples":len(vectors),
        "naive_candidate_mismatches":len(bad),
        "naive_candidate_first_mismatch_index":bad[0] if bad else -1,
        "source_law_admitted":False,
    }


def validate_shape(s:dict)->None:
    if not isinstance(s,dict) or set(s)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise TenthLayerError("tenth genuine original RangeChoice shape changed")
    for name in BIT_FIELDS:
        w=s[name]
        if not isinstance(w,str) or not w.startswith("0x") or not finite_bits(w[2:]):
            raise TenthLayerError("real tenth RangeChoice finite bound missing")
    if value(s["min_bits"])>=value(s["max_bits"]):
        raise TenthLayerError("real tenth RangeChoice bounds reversed")
    for name in ("selector_class","when_in_class","when_out_class"):
        ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(s[name])


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>130000:
        raise TenthLayerError("unbounded tenth original JVM output")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise TenthLayerError("tenth original JVM source reflection failed")
    old=prior.load()
    points=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    shapes=[]
    vectors=[]
    cursor=0
    for group,seed in enumerate(ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise TenthLayerError("missing original tenth seed shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(group),seed]:
            raise TenthLayerError("tenth real source shape header drift")
        s=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for key in BIT_FIELDS:
            if not finite_bits(s[key]):
                raise TenthLayerError("invalid source-owned tenth IEEE bound")
            s[key]="0x"+s[key]
        s["world_seed_bits"]=seed
        validate_shape(s)
        shapes.append(s)
        for j in range(32):
            idx=group*32+j
            if cursor>=len(frames):
                raise TenthLayerError("missing tenth original point")
            row=frames[cursor]
            cursor+=1
            if len(row)!=2+len(WORDS) or row[:2]!=[VALUE,str(idx)] or (
                    not all(finite_bits(word) for word in row[2:])):
                raise TenthLayerError("tenth exact finite word frame invalid")
            v=dict(zip(WORDS,("0x"+word for word in row[2:]),strict=True))
            if v["old_rangechoice_bits"][2:]!=old[idx]:
                raise TenthLayerError("immutable real ninth original RangeChoice parent moved")
            vectors.append({**points[idx],**v})
        if cursor>=len(frames) or frames[cursor]!=[END,str(group),"32"]:
            raise TenthLayerError("tenth seed terminator mismatch")
        cursor+=1
    if cursor!=len(frames):
        raise TenthLayerError("extra tenth Java source-owner frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise TenthLayerError("real RangeChoice shape changed across seeds")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise TenthLayerError("tenth original JVM JSON object expected")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_ninth_fixture_sha256":prior.SHA256,
        "prior_ninth_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_tenth_layer_children_observed":True,
        "source_text_included":False,
        "rangechoice_candidate_telemetry":report.get("rangechoice_candidate_telemetry"),
        **{gate:False for gate in GATES},
    }
    if set(report)!=set(pins)|{"shapes","vectors"} or any(
            type(report.get(k)) is not type(v) or report[k]!=v for k,v in pins.items()):
        raise TenthLayerError("tenth original source or admission drift")
    root=ninth.eighth.seventh.sixth.fifth.fourth.third.second.root
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise TenthLayerError("tenth source method inventory drift")
    for name in ("ap2_compute","holder_holder_compute"):
        m=methods[name]
        if not isinstance(m,dict) or m.get("reviewed") is not False or tuple(
                m.get(k) for k in ("owner","signature","body_sha256","normalized_sha256")
                )!=root.frozen_final.METHODS[name]:
            raise TenthLayerError("tenth original indexed method SHA drift")
    m=methods["mapped_delegate_compute"]
    if not isinstance(m,dict) or m.get("reviewed") is not False or (
            m.get("owner")!=root.PURE_TRANSFORMER or
            m.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise TenthLayerError("tenth original mapped source method changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or (
            not isinstance(vectors,list) or len(vectors)!=128):
        raise TenthLayerError("tenth fixed 4x32 bounded sample count changed")
    points=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    raw=[]
    for group,shape in enumerate(shapes):
        validate_shape(shape)
        raw.append("|".join((HEAD,str(group),shape["world_seed_bits"],
            *(shape[k][2:] if k in BIT_FIELDS else str(shape[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            idx=group*32+j
            v=vectors[idx]
            if not isinstance(v,dict) or set(v)!=set(points[idx])|set(WORDS) or (
                    any(v.get(k)!=p for k,p in points[idx].items())):
                raise TenthLayerError("tenth source-owned pinned XYZ/seed drift")
            raw.append("|".join((VALUE,str(idx),*(v[k][2:] for k in WORDS))))
        raw.append("|".join((END,str(group),"32")))
    if type(report["rangechoice_candidate_telemetry"]) is not dict or (
            report["rangechoice_candidate_telemetry"]!=choice_telemetry(shapes,vectors)):
        raise TenthLayerError("tenth candidate telemetry cannot be silently admitted")
    if parse_output("\n".join(raw))!=(shapes,vectors):
        raise TenthLayerError("tenth source-owning frames could not round-trip")


def observe(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-tenth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        f=ninth.eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            ninth.eighth.seventh.sixth.JAVA_SOURCE,
            ninth.eighth.seventh.JAVA_SOURCE,
            ninth.eighth.JAVA_SOURCE,
            ninth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TenthLayerError("missing source-free tenth original bridge files")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise TenthLayerError("tenth bounded javac failed: "+build.stderr[:480])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityTenthLayer262","--tenth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            reason=next((v for v in proc.stdout.splitlines() if v.startswith(FAIL)),
                        "no bounded original tenth failure tag")
            raise TenthLayerError("real tenth original JVM failure: "+reason[:160])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    dest=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_ninth_fixture_sha256":prior.SHA256,
        "prior_ninth_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_tenth_layer_children_observed":True,
        "source_text_included":False,
        "shapes":shapes,"vectors":vectors,
        "rangechoice_candidate_telemetry":choice_telemetry(shapes,vectors),
        **{gate:False for gate in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>125000:
        raise TenthLayerError("bounded tenth source-free report too large")
    dest.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(dest),"sha256":hashlib.sha256(payload).hexdigest(),
        "genuinely_new_tenth_child_points":len(vectors),
        "selector_class":shapes[0]["selector_class"],
        "when_in_class":shapes[0]["when_in_class"],
        "when_out_class":shapes[0]["when_out_class"],
        "rangechoice_candidate_telemetry":choice_telemetry(shapes,vectors),
        **{gate:False for gate in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.primitive.CACHE)
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
    except (TenthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 TENTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
