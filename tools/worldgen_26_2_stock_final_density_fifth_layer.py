#!/usr/bin/env python3
"""Original stock 26.2 fifth-layer next NEW leaves, never old oracle recapture.

Reads the four actual previously observed 26.2 graph branches and a
YClampedGradient record from the owner's original JVM. Only six new
child samples per fixed XYZ; five fourth-layer words are equality anchors.
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
import worldgen_26_2_stock_final_density_fourth_layer as fourth
import worldgen_26_2_stock_finaldensity_fourth_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityFifthLayer262.java"
KIND="original_26_2_finaldensity_fifth_layer_source_owned_children_unadmitted"
HEAD="HELVE26_2_FIFTH_SHAPE"
VALUE="HELVE26_2_FIFTH_VALUE"
END="HELVE26_2_FIFTH_END"
FAIL="HELVE26_2_FIFTH_FAILURE"
CLASS=fourth.DENSITY
SHAPE_FIELDS=(
    "left_ap2_enum_class","left_ap2_op",
    "left_ap2_left_class","left_ap2_right_class",
    "gradient_from_y","gradient_to_y",
    "gradient_from_value_bits","gradient_to_value_bits",
    "outside_holder_target_class",
    "outside_in_enum_class","outside_in_op","outside_in_argument_bits",
    "outside_in_child_class",
    "max_left_mapped_enum_class","max_left_mapped_kind","max_left_mapped_child_class",
    "max_right_mapped_enum_class","max_right_mapped_kind","max_right_mapped_child_class",
)
NUMBER_FIELDS=("gradient_from_y","gradient_to_y")
PARAM_FIELDS=("gradient_from_value_bits","gradient_to_value_bits","outside_in_argument_bits")
WORDS=(
    "left_ap2_left_bits","left_ap2_right_bits","left_ap2_output_bits",
    "outside_holder_target_bits","outside_holder_output_bits",
    "outside_in_child_bits","outside_in_output_bits",
    "max_left_mapped_child_bits","max_left_mapped_output_bits",
    "max_right_mapped_child_bits","max_right_mapped_output_bits",
)
NEW_FIELDS=(
    "left_ap2_left_bits","left_ap2_right_bits",
    "outside_holder_target_bits","outside_in_child_bits",
    "max_left_mapped_child_bits","max_right_mapped_child_bits",
)
GATES=tuple(fourth.GATES)+(
    "fifth_layer_actual_child_shapes_qualified",
    "fifth_layer_rust_jvm_numeric_parity_qualified",
)


class FifthLayerError(ValueError):
    """Fail-closed original 26.2 fifth-layer evidence."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def bits(number:float)->str:
    return "0x"+struct.pack(">d",number).hex()


def validate_shape(shape:dict)->None:
    if not isinstance(shape,dict) or set(shape)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise FifthLayerError("fifth-layer original JVM declared unexpected graph schema")
    for name in SHAPE_FIELDS:
        if name.endswith("_class"):
            fourth.third.second.require_class(shape[name])
    for field in PARAM_FIELDS:
        word=shape.get(field)
        if not isinstance(word,str) or not word.startswith("0x") or (
                not fourth.third.second.inner.finite_word(word[2:])):
            raise FifthLayerError("invalid fifth-layer finite original-JVM gradient/constant")
    for field in NUMBER_FIELDS:
        if not isinstance(shape[field],int) or isinstance(shape[field],bool) or (
                shape[field]<-(2**31) or shape[field]>=2**31):
            raise FifthLayerError("invalid fifth-layer integer Y bound")
    if shape["gradient_from_y"]>=shape["gradient_to_y"]:
        raise FifthLayerError("reversed original Y-gradient")
    enums=(
        ("left_ap2_op","left_ap2_enum_class",CLASS+"TwoArgumentSimpleFunction$Type"),
        ("outside_in_op","outside_in_enum_class",CLASS+"MulOrAdd$Type"),
        ("max_left_mapped_kind","max_left_mapped_enum_class",CLASS+"Mapped$Type"),
        ("max_right_mapped_kind","max_right_mapped_enum_class",CLASS+"Mapped$Type"),
    )
    for name,typename,expected in enums:
        if shape[typename]!=expected:
            raise FifthLayerError("unexpected fifth-layer original enum class")
        fourth.third.second.require_enum(shape[name],shape[typename])
    if shape["outside_in_op"] not in ("ADD","MUL"):
        raise FifthLayerError("unsupported original outside-in MulOrAdd operator")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>155000:
        raise FifthLayerError("unbounded original fifth-layer source-free stream")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise FifthLayerError("original JVM fifth-layer reflection failed")
    old=prior.load()
    cursor=0
    shapes=[]
    vectors=[]
    points=fourth.third.second.final.input_rows()
    for seed_index,seed in enumerate(fourth.third.second.final.SEEDS):
        if cursor>=len(frames):
            raise FifthLayerError("missing actual original fifth-layer shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=3+len(SHAPE_FIELDS) or row[:3]!=[HEAD,str(seed_index),seed]:
            raise FifthLayerError("unqualified fifth-layer shape transport")
        shape=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        for k in PARAM_FIELDS:
            if not fourth.third.second.inner.finite_word(shape[k]):
                raise FifthLayerError("invalid original fifth-layer shape word")
            shape[k]="0x"+shape[k]
        for k in NUMBER_FIELDS:
            if not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,9})",shape[k]):
                raise FifthLayerError("invalid bounded original gradient int")
            shape[k]=int(shape[k])
        shape["world_seed_bits"]=seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index=seed_index*32+j
            if cursor>=len(frames):
                raise FifthLayerError("missing original fifth-layer value")
            row=frames[cursor]
            cursor+=1
            if (len(row)!=13 or row[:2]!=[VALUE,str(index)] or
                    not all(fourth.third.second.inner.finite_word(x) for x in row[2:])):
                raise FifthLayerError("invalid bounded fifth-layer point words")
            words=dict(zip(WORDS,("0x"+x for x in row[2:]),strict=True))
            oldwords=old[index]
            anchors=(
                ("left_ap2_output_bits",oldwords[0]),
                ("outside_holder_output_bits",oldwords[2]),
                ("outside_in_output_bits",oldwords[3]),
                ("max_left_mapped_output_bits",oldwords[5]),
                ("max_right_mapped_output_bits",oldwords[6]),
            )
            if any(words[k][2:]!=v for k,v in anchors):
                raise FifthLayerError("previous original fourth-layer anchor changed")
            if words["outside_holder_target_bits"]!=words["outside_holder_output_bits"]:
                raise FifthLayerError("fifth-layer HolderHolder did not forward its target")
            operand=value(words["outside_in_child_bits"])
            argument=value(shape["outside_in_argument_bits"])
            calculation=operand+argument if shape["outside_in_op"]=="ADD" else operand*argument
            if bits(calculation)!=words["outside_in_output_bits"]:
                raise FifthLayerError("actual fifth-layer MulOrAdd arithmetic mismatch")
            vectors.append({**points[index],**words})
        if cursor>=len(frames) or frames[cursor]!=[END,str(seed_index),"32"]:
            raise FifthLayerError("missing original fifth-layer group terminator")
        cursor+=1
    if cursor!=len(frames):
        raise FifthLayerError("unexpected additional original fifth-layer frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise FifthLayerError("fifth-layer stock graph shape depends on seed")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise FifthLayerError("expected original fifth-layer source-free report")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":fourth.third.second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":fourth.third.second.final.frozen.SERVER_SHA256,
        "prior_fourth_fixture_sha256":prior.SHA256,
        "prior_fourth_report_sha256":prior.REPORT_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,"sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_fifth_layer_inputs_observed":True,
        **{gate:False for gate in GATES},
    }
    if (set(report)!=set(pins)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in pins.items())):
        raise FifthLayerError("fifth-layer source provenance, schema or gate mismatch")
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise FifthLayerError("fifth-layer pinned source methods changed")
    root=fourth.third.second.root
    for name in ("ap2_compute","holder_holder_compute"):
        v=methods[name]
        if not isinstance(v,dict) or v.get("reviewed") is not False or (
                tuple(v.get(k) for k in (
                    "owner","signature","body_sha256","normalized_sha256"))
                !=root.frozen_final.METHODS[name]):
            raise FifthLayerError("fifth-layer method source pin moved")
    v=methods["mapped_delegate_compute"]
    if not isinstance(v,dict) or v.get("reviewed") is not False or (
            v.get("owner")!=root.PURE_TRANSFORMER or
            v.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise FifthLayerError("fifth-layer mapped source fingerprint changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise FifthLayerError("fifth-layer requires four seeds times 32 contexts")
    frames=[]
    points=fourth.third.second.final.input_rows()
    for seed_index,shape in enumerate(shapes):
        validate_shape(shape)
        frames.append("|".join((HEAD,str(seed_index),shape["world_seed_bits"],
                       *(shape[k][2:] if k in PARAM_FIELDS else str(shape[k])
                         for k in SHAPE_FIELDS))))
        for j in range(32):
            index=seed_index*32+j
            v=vectors[index]
            if not isinstance(v,dict) or set(v)!=set(points[index])|set(WORDS) or (
                    any(v.get(k)!=x for k,x in points[index].items())):
                raise FifthLayerError("original fifth-layer seed/XYZ frame drifted")
            frames.append("|".join((VALUE,str(index),*(v[k][2:] for k in WORDS))))
        frames.append("|".join((END,str(seed_index),"32")))
    if parse_output("\n".join(frames))!=(shapes,vectors):
        raise FifthLayerError("fifth-layer original source-free transport not canonical")


def source_observation(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-fifth-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        sources=(
            fourth.third.second.final.roots.BASE_BRIDGE,
            fourth.third.second.final.JAVA_SOURCE,
            fourth.third.second.root.JAVA_SOURCE,
            fourth.third.second.inner.JAVA_SOURCE,
            fourth.third.second.JAVA_SOURCE,
            fourth.third.JAVA_SOURCE,
            fourth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not p.is_file() for p in sources):
            raise FifthLayerError("missing original source-owning fifth-layer bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise FifthLayerError("original fifth-layer javac rejected: "+build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityFifthLayer262","--fifth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in fourth.third.second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next((line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                         "no bounded original-JVM failure tag")
            raise FifthLayerError("original fifth-layer source-owning reflection failed: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=fourth.third.second.final.improved.external_output(output)
    source_sha,server_sha,methods=fourth.third.second.inner.source_provenance(
        source,db,lock,server)
    shapes,vectors=source_observation(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_fourth_fixture_sha256":prior.SHA256,
        "prior_fourth_report_sha256":prior.REPORT_SHA256,
        "source_methods":methods,
        "world_seeds":list(fourth.third.second.final.SEEDS),
        "point_count_per_seed":32,"sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,"new_fifth_layer_inputs_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{gate:False for gate in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>155000:
        raise FifthLayerError("unbounded original fifth-layer output JSON")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as file:
        file.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_fifth_layer_rows":len(vectors),
        "left_ap2_operation":shapes[0]["left_ap2_op"],
        "outside_in_operation":shapes[0]["outside_in_op"],
        "left_mapped_operation":shapes[0]["max_left_mapped_kind"],
        "right_mapped_operation":shapes[0]["max_right_mapped_kind"],
        **{gate:False for gate in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=fourth.third.second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=fourth.third.second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=fourth.third.second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=fourth.third.second.final.primitive.CACHE)
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
    except (FifthLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FIFTH LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
