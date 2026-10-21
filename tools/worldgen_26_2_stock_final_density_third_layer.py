#!/usr/bin/env python3
"""Third NEW original 26.2 finalDensity graph frontier: four source-rooted children.

Old 128-root/inner/second, 512-cell and 768-NoiseChunk evidence is never
re-captured as a new proof. Previous second-layer inputs are strict independent
bit anchors. Capture only marker-wrapped, nested RangeChoice and outside
MulOrAdd upstream inputs. No Java source, registry or executable bytes emitted.
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
import worldgen_26_2_stock_final_density_second_layer as second
import worldgen_26_2_stock_finaldensity_second_layer_fixture as prior

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityThirdLayer262.java"
KIND="original_26_2_finaldensity_third_layer_four_actual_children_unadmitted"
HEAD="HELVE26_2_THIRD_SHAPE"
VALUE="HELVE26_2_THIRD_VALUE"
END="HELVE26_2_THIRD_END"
FAIL="HELVE26_2_THIRD_FAILURE"
DENSITY=second.DENSITY
NEW_FIELDS=(
    "left_marker_wrapped_bits",
    "nested_selector_bits","nested_in_bits","nested_out_bits",
    "outside_marker_wrapped_bits","outside_mul_wrapped_bits",
)
WORDS=(
    "left_marker_wrapped_bits","left_marker_output_bits",
    "nested_selector_bits","nested_in_bits","nested_out_bits",
    "nested_output_bits",
    "outside_marker_wrapped_bits","outside_marker_output_bits",
    "outside_mul_wrapped_bits","outside_mul_output_bits",
)
SHAPE_FIELDS=(
    "left_marker_enum_class","left_marker_kind","left_marker_wrapped_class",
    "nested_selector_class","nested_in_class","nested_out_class",
    "nested_min_inclusive_bits","nested_max_exclusive_bits",
    "outside_marker_enum_class","outside_marker_kind",
    "outside_marker_wrapped_class",
    "outside_mul_enum_class","outside_mul_op",
    "outside_mul_argument_bits","outside_mul_wrapped_class",
)
PARAM_FIELDS=(
    "nested_min_inclusive_bits","nested_max_exclusive_bits",
    "outside_mul_argument_bits",
)
GATES=tuple(second.GATES)+(
    "third_layer_four_child_shapes_qualified",
    "third_layer_nested_rangechoice_qualified",
    "third_layer_rust_jvm_numeric_parity_qualified",
)


class ThirdLayerError(ValueError):
    """The original 26.2 third-layer evidence is not qualified."""


def float_word(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word[2:]))[0]


def bits(value:float)->str:
    return "0x"+struct.pack(">d",value).hex()


def validate_shape(shape:dict)->None:
    if set(shape)!=set(SHAPE_FIELDS)|{"world_seed_bits"}:
        raise ThirdLayerError("original third-layer shape fields changed")
    for key in SHAPE_FIELDS:
        value=shape[key]
        if key.endswith("_class"):
            second.require_class(value)
    for prefix in ("left_marker","outside_marker"):
        if shape[prefix+"_enum_class"]!=DENSITY+"Marker$Type":
            raise ThirdLayerError("unknown Marker enum declaring type")
        second.require_enum(shape[prefix+"_kind"],shape[prefix+"_enum_class"])
    if shape["outside_mul_enum_class"]!=DENSITY+"MulOrAdd$Type":
        raise ThirdLayerError("unknown second MulOrAdd enum declaring type")
    second.require_enum(shape["outside_mul_op"],shape["outside_mul_enum_class"])
    if shape["outside_mul_op"] not in ("ADD","MUL"):
        raise ThirdLayerError("unsupported second MulOrAdd operation")
    for key in ("nested_min_inclusive_bits","nested_max_exclusive_bits",
                "outside_mul_argument_bits"):
        if not isinstance(shape[key],str) or not shape[key].startswith("0x") or (
                not second.inner.finite_word(shape[key][2:])):
            raise ThirdLayerError("nonfinite/unqualified third-layer parameter")
    if float_word(shape["nested_min_inclusive_bits"])>=float_word(
            shape["nested_max_exclusive_bits"]):
        raise ThirdLayerError("invalid actual nested RangeChoice thresholds")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>160000:
        raise ThirdLayerError("unbounded JVM third-layer frames")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise ThirdLayerError("original JVM rejected third-layer reflection")
    old=prior.load()
    cursor=0
    shapes=[]
    vectors=[]
    for seed_index,seed in enumerate(second.final.SEEDS):
        if cursor>=len(frames):
            raise ThirdLayerError("missing third-layer original shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=18 or row[:3]!=[HEAD,str(seed_index),seed]:
            raise ThirdLayerError("original third-layer shape frame changed")
        shape=dict(zip(SHAPE_FIELDS,row[3:],strict=True))
        # JVM frames carry plain 16-digit IEEE words. The validated
        # JSON report, like every earlier layer, uses "0x"-prefixed
        # words. Never conflate the two transport representations.
        for key in PARAM_FIELDS:
            if not second.inner.finite_word(shape[key]):
                raise ThirdLayerError("invalid third-layer IEEE shape parameter")
            shape[key]="0x"+shape[key]
        shape["world_seed_bits"]=seed
        validate_shape(shape)
        shapes.append(shape)
        for point_index in range(32):
            index=seed_index*32+point_index
            if cursor>=len(frames):
                raise ThirdLayerError("missing new third-layer original sample")
            v=frames[cursor]
            cursor+=1
            if (len(v)!=12 or v[:2]!=[VALUE,str(index)] or
                not all(second.inner.finite_word(x) for x in v[2:])):
                raise ThirdLayerError("invalid third-layer bounded IEEE frame")
            words=dict(zip(WORDS,("0x"+x for x in v[2:]),strict=True))
            previous=old[index]
            if (
                words["left_marker_output_bits"][2:]!=previous[0] or
                words["nested_output_bits"][2:]!=previous[1] or
                words["outside_marker_output_bits"][2:]!=previous[2] or
                words["outside_mul_output_bits"][2:]!=previous[3]
            ):
                raise ThirdLayerError("previous second-layer JVM output anchor moved")
            if words["left_marker_wrapped_bits"]!=words["left_marker_output_bits"]:
                raise ThirdLayerError("original left Marker SinglePoint delegation differed")
            if words["outside_marker_wrapped_bits"]!=words["outside_marker_output_bits"]:
                raise ThirdLayerError("original outside Marker SinglePoint delegation differed")
            min_value=float_word(shape["nested_min_inclusive_bits"])
            max_value=float_word(shape["nested_max_exclusive_bits"])
            selection=float_word(words["nested_selector_bits"])
            branch=("nested_in_bits" if min_value<=selection<max_value
                    else "nested_out_bits")
            if words[branch]!=words["nested_output_bits"]:
                raise ThirdLayerError("actual nested RangeChoice branch bits differ")
            mul_input=float_word(words["outside_mul_wrapped_bits"])
            argument=float_word(shape["outside_mul_argument_bits"])
            result=(mul_input+argument if shape["outside_mul_op"]=="ADD"
                    else mul_input*argument)
            if bits(result)!=words["outside_mul_output_bits"]:
                raise ThirdLayerError("actual nested MulOrAdd output IEEE bits differ")
            vectors.append({**second.final.input_rows()[index],**words})
        if cursor>=len(frames) or frames[cursor]!=[END,str(seed_index),"32"]:
            raise ThirdLayerError("missing third-layer terminator")
        cursor+=1
    if cursor!=len(frames):
        raise ThirdLayerError("extra original third-layer JVM frames")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise ThirdLayerError("third-layer original graph changes with seed")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise ThirdLayerError("expected source-free original third-layer report")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":second.final.frozen.SOURCE_SHA256,
        "official_server_sha256":second.final.frozen.SERVER_SHA256,
        "prior_second_fixture_sha256":prior.SHA256,
        "prior_second_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(second.final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_third_layer_inputs_observed":True,
        **{key:False for key in GATES},
    }
    if (set(report)!=set(pins)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in pins.items())):
        raise ThirdLayerError("original third-layer source pin or gate changed")
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
            "ap2_compute","mapped_delegate_compute","holder_holder_compute"}:
        raise ThirdLayerError("original source compute method identity missing")
    for key,pin in (
        ("ap2_compute",second.root.frozen_final.METHODS["ap2_compute"]),
        ("holder_holder_compute",second.root.frozen_final.METHODS["holder_holder_compute"]),
    ):
        m=methods[key]
        if (not isinstance(m,dict) or m.get("reviewed") is not False or
            tuple(m.get(field) for field in (
                "owner","signature","body_sha256","normalized_sha256"))!=pin):
            raise ThirdLayerError("original third-layer stock source method changed: "+key)
    mapped=methods["mapped_delegate_compute"]
    if (not isinstance(mapped,dict) or mapped.get("reviewed") is not False or
        mapped.get("owner")!=second.root.PURE_TRANSFORMER or
        mapped.get("body_sha256")!=second.root.PURE_COMPUTE_SHA256):
        raise ThirdLayerError("original stock mapped source delegate changed")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise ThirdLayerError("expected four shapes and 128 original new third-layer samples")
    rows=[]
    for seed_index,shape in enumerate(shapes):
        validate_shape(shape)
        rows.append("|".join((
            HEAD,str(seed_index),shape["world_seed_bits"],
            *(shape[field][2:] if field in PARAM_FIELDS else shape[field]
              for field in SHAPE_FIELDS),
        )))
        for j in range(32):
            index=seed_index*32+j
            v=vectors[index]
            context=second.final.input_rows()[index]
            if (not isinstance(v,dict) or set(v)!=set(context)|set(WORDS) or
                any(v.get(key)!=value for key,value in context.items())):
                raise ThirdLayerError("original third-layer XYZ/source context changed")
            rows.append("|".join((
                VALUE,str(index),*(v[field][2:] for field in WORDS),
            )))
        rows.append("|".join((END,str(seed_index),"32")))
    if parse_output("\n".join(rows))!=(shapes,vectors):
        raise ThirdLayerError("reassembled original third-layer JVM witness differs")


def source_observation(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-third-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        sources=(
            second.final.roots.BASE_BRIDGE,second.final.JAVA_SOURCE,
            second.root.JAVA_SOURCE,second.inner.JAVA_SOURCE,
            second.JAVA_SOURCE,JAVA_SOURCE,
        )
        if any(not source.is_file() for source in sources):
            raise ThirdLayerError("missing source-free original JVM reflection bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),
             *(str(source) for source in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise ThirdLayerError("stock third-layer javac failed: "+build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityThirdLayer262","--third-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in second.final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next(
                (line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                "no bounded original failure tag",
            )
            raise ThirdLayerError("original 26.2 JVM third-layer rejected: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=second.final.improved.external_output(output)
    source_sha,server_sha,methods=second.inner.source_provenance(source,db,lock,server)
    shapes,vectors=source_observation(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":source_sha,"official_server_sha256":server_sha,
        "prior_second_fixture_sha256":prior.SHA256,
        "prior_second_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":methods,
        "world_seeds":list(second.final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_third_layer_inputs_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{key:False for key in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>125000:
        raise ThirdLayerError("unbounded third-layer source-free output")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as f:
        f.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "new_third_layer_samples":len(vectors),
        "left_marker_kind":shapes[0]["left_marker_kind"],
        "outside_marker_kind":shapes[0]["outside_marker_kind"],
        "nested_range_selector_class":shapes[0]["nested_selector_class"],
        "outside_muloradd_operation":shapes[0]["outside_mul_op"],
        **{key:False for key in GATES},
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=second.final.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=second.final.primitive.DB)
    p.add_argument("--lock",type=Path,default=second.final.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=second.final.primitive.CACHE)
    p.add_argument("--server-jar",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            metadata,_=official.resolve("26.2",args.cache)
            server=metadata["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
                                 server=server,output=args.output),sort_keys=True))
    except (ThirdLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 THIRD LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
