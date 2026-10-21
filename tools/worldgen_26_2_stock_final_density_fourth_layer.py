#!/usr/bin/env python3
"""Original 26.2 finalDensity fourth layer: seven NEW child inputs, four old anchors.

The four actual third-layer branches are source-owning JVM inspected, not
assumed from a historical formula. Zero previously frozen root/inner/second/
third/NoiseChunk datasets are recaptured. No Java source or binary is exported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

import official_state_data as official
import worldgen_26_2_stock_final_density_third_layer as third
import worldgen_26_2_stock_finaldensity_third_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityFourthLayer262.java"
KIND="original_26_2_finaldensity_fourth_layer_four_actual_children_unadmitted"
HEAD="HELVE26_2_FOURTH_SHAPE"
VALUE="HELVE26_2_FOURTH_VALUE"
END="HELVE26_2_FOURTH_END"
FAIL="HELVE26_2_FOURTH_FAILURE"
DENSITY=third.DENSITY
SHAPE_FIELDS=(
    "left_mul_enum_class","left_mul_op","left_mul_argument_bits",
    "left_mul_input_class","nested_holder_target_class",
    "outside_range_selector_class","outside_range_in_class","outside_range_out_class",
    "outside_range_min_bits","outside_range_max_bits",
    "right_ap2_enum_class","right_ap2_op","right_ap2_left_class","right_ap2_right_class",
)
PARAM_FIELDS=("left_mul_argument_bits","outside_range_min_bits","outside_range_max_bits")
WORDS=(
    "left_mul_input_bits","left_mul_output_bits",
    "nested_holder_target_bits","nested_holder_output_bits",
    "outside_selector_bits","outside_in_bits","outside_out_bits",
    "outside_range_output_bits",
    "right_ap2_left_bits","right_ap2_right_bits","right_ap2_output_bits",
)
NEW_FIELDS=(
    "left_mul_input_bits","nested_holder_target_bits",
    "outside_selector_bits","outside_in_bits","outside_out_bits",
    "right_ap2_left_bits","right_ap2_right_bits",
)
GATES=tuple(third.GATES)+(
    "fourth_layer_four_child_shapes_qualified",
    "fourth_layer_rust_jvm_numeric_parity_qualified",
)


class FourthLayerError(ValueError):
    """Original 26.2 fourth-layer child evidence is not yet admitted."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def bits(number:float)->str:
    return "0x"+struct.pack(">d",number).hex()


def validate_shape(shape:dict)->None:
    if set(shape)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise FourthLayerError("unexpected original fourth-layer graph shape")
    for k in SHAPE_FIELDS:
        if k.endswith("_class"):
            third.second.require_class(shape[k])
    if shape["left_mul_enum_class"]!=DENSITY+"MulOrAdd$Type":
        raise FourthLayerError("real fourth-layer MulOrAdd declaring type changed")
    if shape["right_ap2_enum_class"]!=DENSITY+"TwoArgumentSimpleFunction$Type":
        raise FourthLayerError("real fourth-layer Ap2 declaring type changed")
    for kind,prefix in (("left_mul_op","left_mul"),("right_ap2_op","right_ap2")):
        third.second.require_enum(shape[kind],shape[prefix+"_enum_class"])
    if shape["left_mul_op"] not in ("MUL","ADD"):
        raise FourthLayerError("unqualified fourth-layer MulOrAdd operation")
    for name in PARAM_FIELDS:
        v=shape.get(name)
        if not isinstance(v,str) or not v.startswith("0x") or (
                not third.second.inner.finite_word(v[2:])):
            raise FourthLayerError("nonfinite fourth-layer original parameter")
    if value(shape["outside_range_min_bits"])>=value(shape["outside_range_max_bits"]):
        raise FourthLayerError("original fourth-layer RangeChoice bounds invalid")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>160000:
        raise FourthLayerError("unbounded original fourth-layer JVM frame")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise FourthLayerError("source-owning JVM rejected fourth-layer reflection")
    old=prior.load()
    cursor=0
    shapes=[]
    vectors=[]
    for seed_index,seed in enumerate(third.second.final.SEEDS):
        if cursor>=len(frames):
            raise FourthLayerError("missing fourth-layer shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=17 or row[:3]!=[HEAD,str(seed_index),seed]:
            raise FourthLayerError("unqualified fourth-layer shape transport")
        shape=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for k in PARAM_FIELDS:
            if not third.second.inner.finite_word(shape[k]):
                raise FourthLayerError("invalid original fourth-layer parameter word")
            shape[k]="0x"+shape[k]
        shape["world_seed_bits"]=seed
        validate_shape(shape)
        shapes.append(shape)
        for point_index in range(32):
            index=seed_index*32+point_index
            if cursor>=len(frames):
                raise FourthLayerError("missing fourth-layer point")
            row=frames[cursor]
            cursor+=1
            if (len(row)!=13 or row[:2]!=[VALUE,str(index)] or
                    not all(third.second.inner.finite_word(x) for x in row[2:])):
                raise FourthLayerError("invalid bounded fourth-layer input")
            fields=dict(zip(WORDS,("0x"+x for x in row[2:]),strict=True))
            expected=old[index]
            anchors=(
                ("left_mul_output_bits",expected[0]),
                ("nested_holder_output_bits",expected[1]),
                ("outside_range_output_bits",expected[4]),
                ("right_ap2_output_bits",expected[5]),
            )
            if any(fields[k][2:]!=v for k,v in anchors):
                raise FourthLayerError("previous original third-layer output anchor changed")
            op=shape["left_mul_op"]
            lhs=value(fields["left_mul_input_bits"])
            arg=value(shape["left_mul_argument_bits"])
            actual=(lhs*arg if op=="MUL" else lhs+arg)
            if bits(actual)!=fields["left_mul_output_bits"]:
                raise FourthLayerError("fourth-layer MulOrAdd bit arithmetic differed")
            if fields["nested_holder_target_bits"]!=fields["nested_holder_output_bits"]:
                raise FourthLayerError("HolderHolder single-point forwarding differed")
            selector=value(fields["outside_selector_bits"])
            low=value(shape["outside_range_min_bits"])
            high=value(shape["outside_range_max_bits"])
            branch=("outside_in_bits" if low<=selector<high else "outside_out_bits")
            if fields[branch]!=fields["outside_range_output_bits"]:
                raise FourthLayerError("actual outside RangeChoice branch bit mismatch")
            # Deliberately do not guess Ap2 operation semantics from enum name.
            # Its genuinely new input words and its previously frozen output
            # are retained separately until its exact source law is reviewed.
            vectors.append({**third.second.final.input_rows()[index],**fields})
        if cursor>=len(frames) or frames[cursor]!=[END,str(seed_index),"32"]:
            raise FourthLayerError("missing fourth-layer terminator")
        cursor+=1
    if cursor!=len(frames):
        raise FourthLayerError("extra original fourth-layer frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise FourthLayerError("actual fourth-layer graph seed-dependent")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise FourthLayerError("missing original fourth-layer source-free report")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":third.second.final.frozen.SERVER_SHA256,
        "prior_third_fixture_sha256":prior.SHA256,
        "prior_third_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(third.second.final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_fourth_layer_inputs_observed":True,
        **{gate:False for gate in GATES},
    }
    if (set(report)!=set(pins)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in pins.items())):
        raise FourthLayerError("original fourth-layer source pin or gate changed")
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise FourthLayerError("original fourth-layer source methods differ")
    for name in ("ap2_compute","holder_holder_compute"):
        m=methods[name]
        pin=third.second.root.frozen_final.METHODS[name]
        if (not isinstance(m,dict) or m.get("reviewed") is not False or
            tuple(m.get(k) for k in (
                "owner","signature","body_sha256","normalized_sha256"))!=pin):
            raise FourthLayerError("fourth-layer source method pin moved")
    m=methods["mapped_delegate_compute"]
    if (not isinstance(m,dict) or m.get("reviewed") is not False or
            m.get("owner")!=third.second.root.PURE_TRANSFORMER or
            m.get("body_sha256")!=third.second.root.PURE_COMPUTE_SHA256):
        raise FourthLayerError("fourth-layer stock mapped delegate changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise FourthLayerError("expect four runtime shapes and 128 new point samples")
    rows=[]
    for seed_index,shape in enumerate(shapes):
        validate_shape(shape)
        rows.append("|".join((HEAD,str(seed_index),shape["world_seed_bits"],
                 *(shape[k][2:] if k in PARAM_FIELDS else shape[k] for k in SHAPE_FIELDS))))
        for j in range(32):
            index=seed_index*32+j
            v=vectors[index]
            context=third.second.final.input_rows()[index]
            if (not isinstance(v,dict) or set(v)!=set(context)|set(WORDS) or
                    any(v.get(k)!=x for k,x in context.items())):
                raise FourthLayerError("fourth-layer original XYZ context differs")
            rows.append("|".join((VALUE,str(index),*(v[k][2:] for k in WORDS))))
        rows.append("|".join((END,str(seed_index),"32")))
    if parse_output("\n".join(rows))!=(shapes,vectors):
        raise FourthLayerError("fourth-layer source-free frame not canonical")


def source_observation(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-fourth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        sources=(
            third.second.final.roots.BASE_BRIDGE,
            third.second.final.JAVA_SOURCE,
            third.second.root.JAVA_SOURCE,
            third.second.inner.JAVA_SOURCE,
            third.second.JAVA_SOURCE,
            third.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise FourthLayerError("missing source-free fourth-layer reflection bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise FourthLayerError("fourth-layer javac rejected: "+build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityFourthLayer262","--fourth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next((s for s in proc.stdout.splitlines() if s.startswith(FAIL)),
                         "no bounded original JVM failure tag")
            raise FourthLayerError("original 26.2 fourth-layer reflection failed: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=source_observation(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_third_fixture_sha256":prior.SHA256,
        "prior_third_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":methods,
        "world_seeds":list(third.second.final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_fourth_layer_inputs_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{gate:False for gate in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>150000:
        raise FourthLayerError("unbounded original fourth-layer source-free JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_fourth_layer_rows":len(vectors),
        "left_mul_operation":shapes[0]["left_mul_op"],
        "nested_holder_target_class":shapes[0]["nested_holder_target_class"],
        "right_ap2_operation":shapes[0]["right_ap2_op"],
        **{gate:False for gate in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=third.second.final.primitive.CACHE)
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
    except (FourthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FOURTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
