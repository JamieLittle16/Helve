#!/usr/bin/env python3
"""New bounded original JVM review of finalDensity's real MulOrAdd and Ap2 children.

This does NOT repeat the previously pinned root/inner bit captures. It
observes the *upstream* MulOrAdd input, selector Marker's child and both
out-of-range Ap2 operands, and reads their actual factory/record types and
constant parameter. All old MulOrAdd/selector/out values are strict frozen
bit anchors. Neither Java source text nor stock binary bytes are exported.
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
import urllib.error
from pathlib import Path

import official_state_data as official
import worldgen_26_2_stock_final_density_inner_semantics as inner
import worldgen_26_2_stock_final_density_root_semantics as root
import worldgen_26_2_stock_finaldensity_inner_fixture as prior
import worldgen_26_2_stock_final_density_singlepoint_capture as final

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensitySecondLayer262.java"
KIND="original_26_2_finaldensity_second_layer_muloradd_selector_ap2_unadmitted"
HEAD="HELVE26_2_SECOND_SHAPE"
VALUE="HELVE26_2_SECOND_VALUE"
END="HELVE26_2_SECOND_END"
FAIL="HELVE26_2_SECOND_FAILURE"
FQN=re.compile(r"net\.minecraft(?:\.[A-Za-z_$][A-Za-z0-9_$]*)+\Z")
IDENT=re.compile(r"[A-Za-z][A-Za-z0-9_]{0,79}\Z")
HEX=re.compile(r"[0-9a-f]{16}\Z")
DENSITY="net.minecraft.world.level.levelgen.DensityFunctions$"
WORDS=(
    "mul_input_bits","mul_output_bits",
    "selector_input_bits","selector_output_bits",
    "outer_left_bits","outer_right_bits","outer_output_bits",
)
GATES=tuple(inner.GATES)+(
    "muloradd_actual_subgraph_qualified",
    "selector_marker_actual_subgraph_qualified",
    "outside_ap2_actual_subgraph_qualified",
    "second_layer_rust_jvm_numeric_parity_qualified",
)

class SecondLayerError(ValueError):
    """Original stock second-layer graph cannot yet be admitted."""


def require_class(name:str)->None:
    if not isinstance(name,str) or not FQN.fullmatch(name) or len(name)>180:
        raise SecondLayerError("unqualified second-layer original class name")


def require_enum(name:str,declaring:str)->None:
    require_class(declaring)
    if not declaring.startswith(DENSITY) or not isinstance(name,str) or not IDENT.fullmatch(name):
        raise SecondLayerError("unqualified second-layer enum identity")


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>115000:
        raise SecondLayerError("unbounded JVM second-layer output")
    frames=[line.split("|") for line in stdout.splitlines()
            if line.split("|",1)[0] in (HEAD,VALUE,END,FAIL)]
    if any(row[0]==FAIL for row in frames):
        raise SecondLayerError("original JVM rejected second-layer reflection")
    pinned=prior.load()
    cursor=0
    shapes=[]
    vectors=[]
    for seed_index,seed in enumerate(final.SEEDS):
        if cursor>=len(frames):
            raise SecondLayerError("missing original second-layer shape")
        row=frames[cursor]
        cursor+=1
        if len(row)!=14 or row[:3]!=[HEAD,str(seed_index),seed]:
            raise SecondLayerError("original second-layer shape frame changed")
        (mul_enum,mul_op,mul_arg,mul_input,
         selector_enum,selector_kind,selector_input,
         ap2_enum,ap2_op,ap2_left,ap2_right)=row[3:]
        require_enum(mul_op,mul_enum)
        require_enum(selector_kind,selector_enum)
        require_enum(ap2_op,ap2_enum)
        for cls in (mul_input,selector_input,ap2_left,ap2_right):
            require_class(cls)
        if not inner.finite_word(mul_arg):
            raise SecondLayerError("unqualified stock MulOrAdd argument IEEE bits")
        shapes.append({
            "world_seed_bits":seed,
            "mul_op_enum_class":mul_enum,"mul_op":mul_op,
            "mul_argument_bits":"0x"+mul_arg,"mul_input_class":mul_input,
            "selector_marker_enum_class":selector_enum,
            "selector_marker_kind":selector_kind,"selector_input_class":selector_input,
            "outside_ap2_enum_class":ap2_enum,"outside_ap2_op":ap2_op,
            "outside_left_class":ap2_left,"outside_right_class":ap2_right,
        })
        for j in range(32):
            index=seed_index*32+j
            if cursor>=len(frames):
                raise SecondLayerError("missing original second-layer sample")
            v=frames[cursor]
            cursor+=1
            if len(v)!=9 or v[:2]!=[VALUE,str(index)] or not all(
                inner.finite_word(x) for x in v[2:]
            ):
                raise SecondLayerError("invalid nonfinite second-layer IEEE frame")
            new=dict(zip(WORDS,("0x"+x for x in v[2:]),strict=True))
            earlier=pinned[index]
            if (new["mul_output_bits"][2:]!=earlier[1] or
                new["selector_output_bits"][2:]!=earlier[3] or
                new["outer_output_bits"][2:]!=earlier[5]):
                raise SecondLayerError("original previous JVM inner output bit anchor moved")
            vectors.append({**final.input_rows()[index],**new})
        if cursor>=len(frames) or frames[cursor]!=[END,str(seed_index),"32"]:
            raise SecondLayerError("missing second-layer terminator")
        cursor+=1
    if cursor!=len(frames):
        raise SecondLayerError("unexpected second-layer JVM output rows")
    # The canonical Overworld graph structure is registry-owned, not
    # seeded dynamically. If type/argument evidence varies, fail closed.
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=
           {k:v for k,v in shapes[0].items() if k!="world_seed_bits"}
           for s in shapes[1:]):
        raise SecondLayerError("actual second-layer graph changes across world seeds")
    return shapes,vectors


def validate(report:dict)->None:
    if not isinstance(report,dict):
        raise SecondLayerError("expected source-free original report object")
    pins={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":final.frozen.SOURCE_SHA256,
        "official_server_sha256":final.frozen.SERVER_SHA256,
        "prior_inner_fixture_sha256":prior.SHA256,
        "prior_inner_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_second_layer_inputs_observed":True,
        **{k:False for k in GATES},
    }
    if (set(report)!=set(pins)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(value) or report[k]!=value
            for k,value in pins.items())):
        raise SecondLayerError("original source pin or unadmitted gate changed")
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={
        "ap2_compute","mapped_delegate_compute","holder_holder_compute",
    }:
        raise SecondLayerError("original stock compute source identity missing")
    for key,pin in (("ap2_compute",root.frozen_final.METHODS["ap2_compute"]),
                    ("holder_holder_compute",root.frozen_final.METHODS["holder_holder_compute"])):
        method=methods[key]
        if (not isinstance(method,dict) or method.get("reviewed") is not False or
            tuple(method.get(k) for k in (
                "owner","signature","body_sha256","normalized_sha256",
            ))!=pin):
            raise SecondLayerError("source method previously pinned differs: "+key)
    delegate=methods["mapped_delegate_compute"]
    if (not isinstance(delegate,dict) or delegate.get("reviewed") is not False or
        delegate.get("owner")!=root.PURE_TRANSFORMER or
        delegate.get("body_sha256")!=root.PURE_COMPUTE_SHA256):
        raise SecondLayerError("PureTransformer source delegate differs")
    shapes=report.get("shapes")
    vectors=report.get("vectors")
    if not isinstance(shapes,list) or len(shapes)!=4 or not isinstance(vectors,list) or len(vectors)!=128:
        raise SecondLayerError("expected four seeded shapes and 128 second-layer samples")
    lines=[]
    keys={
        "world_seed_bits","mul_op_enum_class","mul_op",
        "mul_argument_bits","mul_input_class","selector_marker_enum_class",
        "selector_marker_kind","selector_input_class","outside_ap2_enum_class",
        "outside_ap2_op","outside_left_class","outside_right_class",
    }
    for seed_index,shape in enumerate(shapes):
        if not isinstance(shape,dict) or set(shape)!=keys:
            raise SecondLayerError("malformed second-layer original shape")
        lines.append("|".join((
            HEAD,str(seed_index),shape["world_seed_bits"],
            shape["mul_op_enum_class"],shape["mul_op"],
            shape["mul_argument_bits"][2:],shape["mul_input_class"],
            shape["selector_marker_enum_class"],shape["selector_marker_kind"],
            shape["selector_input_class"],shape["outside_ap2_enum_class"],
            shape["outside_ap2_op"],shape["outside_left_class"],shape["outside_right_class"],
        )))
        for j in range(32):
            index=seed_index*32+j
            v=vectors[index]
            context=final.input_rows()[index]
            if (not isinstance(v,dict) or set(v)!=set(context)|set(WORDS) or
                any(v.get(key)!=value for key,value in context.items())):
                raise SecondLayerError("original seed/XYZ second-layer context changed")
            lines.append("|".join((
                VALUE,str(index),*(v[key][2:] for key in WORDS),
            )))
        lines.append("|".join((END,str(seed_index),"32")))
    if parse_output("\n".join(lines))!=(shapes,vectors):
        raise SecondLayerError("reassembled second-layer source witness not canonical")


def source_observation(server:Path,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-second-layer-") as td:
        work=Path(td)
        jars=official.extract_classpath(server,work/"classpath")
        sources=(
            final.roots.BASE_BRIDGE,final.JAVA_SOURCE,root.JAVA_SOURCE,
            inner.JAVA_SOURCE,JAVA_SOURCE,
        )
        if any(not x.is_file() for x in sources):
            raise SecondLayerError("missing source-free stock reflection bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(x) for x in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise SecondLayerError("original JVM second-layer Java compile rejected: "+
                                   build.stderr[:650])
        proc=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(x) for x in jars))),
             "HelveStockFinalDensitySecondLayer262","--second-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if proc.returncode:
            failure=next((line for line in proc.stdout.splitlines()
                          if line.startswith(FAIL)),"no bounded failure tag")
            raise SecondLayerError("original 26.2 JVM second-layer rejected: "+failure[:200])
        return parse_output(proc.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=final.improved.external_output(output)
    source_sha,server_sha,methods=inner.source_provenance(source,db,lock,server)
    shapes,vectors=source_observation(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":source_sha,
        "official_server_sha256":server_sha,
        "prior_inner_fixture_sha256":prior.SHA256,
        "prior_inner_report_sha256":prior.ORIGINAL_JSON_SHA256,
        "source_methods":methods,
        "world_seeds":list(final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "new_second_layer_inputs_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{k:False for k in GATES},
    }
    validate(report)
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>90000:
        raise SecondLayerError("unbounded original second-layer output")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as out:
        out.write(payload)
    return {
        "output":str(destination),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "new_second_layer_samples":len(vectors),
        "mul_or_add_operation":shapes[0]["mul_op"],
        "outside_ap2_operation":shapes[0]["outside_ap2_op"],
        "selector_marker_kind":shapes[0]["selector_marker_kind"],
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
            source=args.source,db=args.db,lock=args.lock,server=server,output=args.output,
        ),sort_keys=True))
    except (SecondLayerError,ValueError,TypeError,KeyError,IndexError,OSError,
            sqlite3.Error,subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FINAL SECOND LAYER OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
