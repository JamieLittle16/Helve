#!/usr/bin/env python3
"""Pinned 26.2 real finalDensity root operation and first-child numeric diagnostic.

Uses the *existing* 128 SinglePointContext coordinate frames and SHA-frozen
official finalDensity outputs; unlike a recapture this reveals the original
Ap2 type, Mapped transform, HolderHolder concrete target and both child words.
A JVM enum name or root child word is NOT an independent source-law proof,
a mapped/spline/cache implementation or production worldgen authorization.
No original Minecraft sources, bytecode, registries or JAR are exported.
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
import worldgen_26_2_stock_final_density_singlepoint_capture as final
import worldgen_26_2_stock_final_density_singlepoint_fixture as frozen_final

JAVA_SOURCE=Path(__file__).resolve().parent/"worldgen_java/HelveStockFinalDensityRootSemantics262.java"
# The genuine pinned 26.2 delegate inventory already identified this inherited
# compute body (used also by stock MulOrAdd). Mapped is a PureTransformer
# record; it does not declare its own compute(FunctionContext) implementation.
# Strictly require the source SHA AND its runtime declaring class below.
PURE_TRANSFORMER=final.FINAL.rsplit("$",1)[0]+"$PureTransformer"
PURE_COMPUTE_SHA256="80087cd337e4ac54a98884a9c47579f4573740fc983f033ed2243e579515a6dd"
KIND="official_26_2_stock_final_density_root_child_semantics_unadmitted"
HEAD="HELVE26_2_FINAL_ROOT_SHAPE"
VALUE="HELVE26_2_FINAL_ROOT_VALUE"
END="HELVE26_2_FINAL_ROOT_END"
FAIL="HELVE26_2_FINAL_ROOT_FAILURE"
NAME=re.compile(r"[A-Za-z0-9_.$]{1,180}\Z")
ENUM=re.compile(r"[A-Z][A-Z0-9_]*\Z")
BITS=re.compile(r"[0-9a-f]{16}\Z")
GATES=("stock_final_density_root_operator_source_reviewed",
       "stock_mapped_transform_source_reviewed",
       "stock_holder_target_source_reviewed",
       "stock_noisechunk_canonical_traversal_qualified",
       "stock_noisechunk_full_lifecycle_qualified",
       "world_seed_random_state_bound","full_router_graph_qualified",
       "router_numeric_parity_qualified","independent_var_sem_admitted",
       "production_worldgen_enabled","source_text_included")


class RootSemanticError(ValueError):
    """Original pinned stock 26.2 root diagnostic not independently admitted."""


def parse_output(stdout:str)->tuple[list[dict],list[dict]]:
    if not isinstance(stdout,str) or len(stdout)>70000:
        raise RootSemanticError("unbounded original Java diagnostic stream")
    rows=[line.split("|") for line in stdout.splitlines()
          if line.split("|",1)[0] in {HEAD,VALUE,END,FAIL}]
    if any(row[0]==FAIL for row in rows):
        raise RootSemanticError("actual official JVM root diagnostic failed")
    shapes=[]
    vectors=[]
    cursor=0
    original=frozen_final.load_bits()
    for seed_index,seed in enumerate(final.SEEDS):
        if cursor>=len(rows):
            raise RootSemanticError("missing original stock root metadata")
        row=rows[cursor]
        cursor+=1
        if len(row)!=11 or row[:3]!=[HEAD,str(seed_index),seed]:
            raise RootSemanticError("altered stock root identity / seed ordering")
        operator_class,operator,mapped_class,mapped,mapped_input,holder_target,low,high=row[3:]
        if (not all(NAME.fullmatch(v) for v in (
            operator_class,mapped_class,mapped_input,holder_target))
            or not ENUM.fullmatch(operator) or not ENUM.fullmatch(mapped)
            or not operator_class.startswith(final.FINAL.rsplit("$",1)[0]+"$")
            or not mapped_class.startswith(final.MAPPED.rsplit("$",1)[0]+"$")
            or not all(BITS.fullmatch(v) for v in (low,high))):
            raise RootSemanticError("unqualified stock operator, transform or holder identity")
        shapes.append({
            "world_seed_bits":seed,
            "ap2_operator_class":operator_class,"ap2_operator":operator,
            "mapped_transform_class":mapped_class,"mapped_transform":mapped,
            "mapped_input_class":mapped_input,"holder_target_class":holder_target,
            "ap2_min_bits":"0x"+low,"ap2_max_bits":"0x"+high,
        })
        for point in range(32):
            if cursor>=len(rows):
                raise RootSemanticError("missing stock child numeric witness")
            numeric=rows[cursor]
            cursor+=1
            index=seed_index*32+point
            if len(numeric)!=5 or numeric[:2]!=[VALUE,str(index)] or \
               any(not BITS.fullmatch(v) for v in numeric[2:]) or \
               any((int(v,16)>>52)&0x7ff==0x7ff for v in numeric[2:]) or \
               numeric[4]!=original[index]:
                raise RootSemanticError("root/left/right values differ from frozen authentic JVM")
            vectors.append({
                **final.input_rows()[index],
                "mapped_bits":"0x"+numeric[2],
                "holder_bits":"0x"+numeric[3],
                "final_density_bits":"0x"+numeric[4],
            })
        if cursor>=len(rows) or rows[cursor]!=[END,str(seed_index),"32"]:
            raise RootSemanticError("missing stock diagnostic seed end")
        cursor+=1
    if cursor!=len(rows):
        raise RootSemanticError("unexpected stock diagnostic rows")
    if any(shape["ap2_operator"]!=shapes[0]["ap2_operator"] or
           shape["mapped_transform"]!=shapes[0]["mapped_transform"] or
           shape["mapped_input_class"]!=shapes[0]["mapped_input_class"] or
           shape["holder_target_class"]!=shapes[0]["holder_target_class"]
           for shape in shapes[1:]):
        raise RootSemanticError("stock root shape changed across original four seeds")
    return shapes,vectors


def validate(report:dict)->None:
    expected={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":final.frozen.SOURCE_SHA256,
        "official_server_sha256":final.frozen.SERVER_SHA256,
        "original_final_density_fixture_sha256":frozen_final.FIXTURE_SHA256,
        "original_final_density_json_sha256":frozen_final.ORIGINAL_JSON_SHA256,
        "source_methods":report.get("source_methods"),
        "world_seeds":list(final.SEEDS),"point_count_per_seed":32,
        "sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "operator_class_identity_observed":True,
        "first_child_values_observed":True,
        **{name:False for name in GATES},
    }
    if (not isinstance(report,dict) or
        set(report)!=set(expected)|{"shapes","vectors"} or
        any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in expected.items())):
        raise RootSemanticError("root semantic report identity / gates changed")
    methods=report["source_methods"]
    if not isinstance(methods,dict) or set(methods)!={"ap2_compute","mapped_delegate_compute",
                                                      "holder_holder_compute"}:
        raise RootSemanticError("bounded stock source method identity inventory missing")
    for name,method in methods.items():
        if not isinstance(method,dict) or set(method)!={
            "owner","signature","body_sha256","normalized_sha256","reviewed"
        } or method["reviewed"] is not False or not all(
            isinstance(method[k],str) and re.fullmatch(r"[0-9a-f]{64}",method[k])
            for k in ("body_sha256","normalized_sha256")
        ):
            raise RootSemanticError("source method not exact or improperly reviewed: "+name)
    fixed=frozen_final.METHODS
    for name,pin in (("ap2_compute",fixed["ap2_compute"]),
                     ("holder_holder_compute",fixed["holder_holder_compute"])):
        method=methods[name]
        if (method["owner"],method["signature"],method["body_sha256"],
            method["normalized_sha256"])!=pin:
            raise RootSemanticError("prior pinned source identity changed: "+name)
    delegate=methods["mapped_delegate_compute"]
    if (delegate["owner"]!=PURE_TRANSFORMER or
        delegate["body_sha256"]!=PURE_COMPUTE_SHA256):
        raise RootSemanticError("Mapped inherited PureTransformer.compute source identity changed")
    shapes=report["shapes"]
    vectors=report["vectors"]
    if not isinstance(shapes,list) or not isinstance(vectors,list) or len(shapes)!=4 \
       or len(vectors)!=128:
        raise RootSemanticError("not four roots or 128 independently anchored child witnesses")
    # Regenerate original JVM frame to validate the entire schema, order and bits.
    rows=[]
    for seed_index,shape in enumerate(shapes):
        if not isinstance(shape,dict) or set(shape)!={
            "world_seed_bits","ap2_operator_class","ap2_operator",
            "mapped_transform_class","mapped_transform","mapped_input_class",
            "holder_target_class","ap2_min_bits","ap2_max_bits"
        }:
            raise RootSemanticError("wrong original shape keys")
        rows.append("|".join((HEAD,str(seed_index),shape["world_seed_bits"],
            shape["ap2_operator_class"],shape["ap2_operator"],
            shape["mapped_transform_class"],shape["mapped_transform"],
            shape["mapped_input_class"],shape["holder_target_class"],
            shape["ap2_min_bits"][2:],shape["ap2_max_bits"][2:])))
        for point in range(32):
            idx=seed_index*32+point
            if (not isinstance(vectors[idx],dict) or
                set(vectors[idx])!=set(final.input_rows()[idx])|{
                    "mapped_bits","holder_bits","final_density_bits"
                } or
                any(vectors[idx].get(k)!=v for k,v in final.input_rows()[idx].items())):
                raise RootSemanticError("original world-seed XYZ point altered")
            rows.append("|".join((VALUE,str(idx),
                vectors[idx]["mapped_bits"][2:],
                vectors[idx]["holder_bits"][2:],
                vectors[idx]["final_density_bits"][2:])))
        rows.append("|".join((END,str(seed_index),"32")))
    parse_output("\n".join(rows))


def source_methods(conn:sqlite3.Connection)->dict:
    # Fail closed if the original Mapped record has acquired a declared
    # compute method: the inherited-dispatch explanation would be invalid.
    declared=conn.execute(
        "SELECT m.id FROM methods m JOIN types t ON m.type_id=t.id "
        "WHERE t.qualified_name=? AND m.name='compute'",
        (final.MAPPED,),
    ).fetchall()
    if declared:
        raise RootSemanticError("Mapped unexpectedly declares a direct compute method")
    methods={}
    for label,owner in (("ap2_compute",final.FINAL),
                        ("mapped_delegate_compute",PURE_TRANSFORMER),
                        ("holder_holder_compute",final.HOLDER)):
        found=conn.execute(
            "SELECT m.signature,m.body_sha256,m.normalized_sha256 "
            "FROM methods m JOIN types t ON m.type_id=t.id "
            "WHERE t.qualified_name=? AND m.name='compute' AND m.param_count=1",
            (owner,),
        ).fetchall()
        if len(found)!=1:
            raise RootSemanticError("missing or ambiguous pinned 26.2 compute: "+label)
        row=found[0]
        if (label=="mapped_delegate_compute" and
            row["body_sha256"]!=PURE_COMPUTE_SHA256):
            raise RootSemanticError("pinned PureTransformer.compute body SHA changed")
        methods[label]={
            "owner":owner,"signature":row["signature"],
            "body_sha256":row["body_sha256"],
            "normalized_sha256":row["normalized_sha256"],
            "reviewed":False,
        }
    return methods


def observe(server:Path,*,timeout:int=240)->tuple[list[dict],list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-262-root-semantics-") as folder:
        work=Path(folder)
        jars=final.official.extract_classpath(server,work/"classpath")
        sources=(final.roots.BASE_BRIDGE,final.JAVA_SOURCE,JAVA_SOURCE)
        if any(not path.is_file() for path in sources):
            raise RootSemanticError("missing exact 26.2 source-free bridge")
        build=subprocess.run(
            ["javac","-encoding","UTF-8","-d",str(work),*(str(p) for p in sources)],
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if build.returncode:
            raise RootSemanticError("stock root bridge compilation rejected: "+
                                    build.stderr[:650])
        result=subprocess.run(
            ["java","-Xmx768m","-cp",
             os.pathsep.join((str(work),*(str(jar) for jar in jars))),
             "HelveStockFinalDensityRootSemantics262","--final-root-children-128"],
            input="\n".join(
                f"{x['world_seed_bits']}\t{x['block_x']}\t{x['block_y']}\t{x['block_z']}"
                for x in final.input_rows()
            )+"\n",
            capture_output=True,text=True,timeout=timeout,check=False,
        )
        if result.returncode:
            # Do not print private logs or Minecraft exceptions.
            raise RootSemanticError("original 26.2 JVM child diagnostic rejected: "+
                                    (result.stdout.splitlines()[-1][:180]
                                     if result.stdout else "no result"))
        return parse_output(result.stdout)


def capture(*,source:Path,db:Path,lock:Path,server:Path,output:Path)->dict:
    destination=final.improved.external_output(output)
    with lock.open("rb") as fp:
        pin=tomllib.load(fp)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise RootSemanticError("not exact Minecraft Java 26.2 pinned version")
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        methods=source_methods(conn)
    finally:
        conn.close()
    server_sha=official.sha256_file(server)
    if (source_sha!=final.frozen.SOURCE_SHA256 or
        server_sha!=final.frozen.SERVER_SHA256 or
        server_sha!=pin["runtime"]["server_sha256"]):
        raise RootSemanticError("stock JVM/source identity diverged from 128 original oracle")
    shapes,vectors=observe(server)
    report={
        "schema":1,"kind":KIND,"minecraft":"26.2","protocol":776,
        "data_version":4903,"source_archive_sha256":source_sha,
        "official_server_sha256":server_sha,
        "original_final_density_fixture_sha256":frozen_final.FIXTURE_SHA256,
        "original_final_density_json_sha256":frozen_final.ORIGINAL_JSON_SHA256,
        "source_methods":methods,"world_seeds":list(final.SEEDS),
        "point_count_per_seed":32,"sample_context":"DensityFunction$SinglePointContext",
        "original_stock_registry_used":True,
        "operator_class_identity_observed":True,
        "first_child_values_observed":True,
        "shapes":shapes,"vectors":vectors,
        **{name:False for name in GATES},
    }
    validate(report)
    payload=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>75000:
        raise RootSemanticError("unbounded source-free stock root packet")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as stream:
        stream.write(payload)
    return {
        "output":str(destination),"sha256":hashlib.sha256(payload).hexdigest(),
        "root_shapes":len(shapes),"original_child_sample_pairs":len(vectors),
        "root_operator":shapes[0]["ap2_operator"],
        "mapped_transform":shapes[0]["mapped_transform"],
        "holder_target_class":shapes[0]["holder_target_class"],
        **{name:False for name in GATES},
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
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
                                 server=server,output=args.output),sort_keys=True))
    except (RootSemanticError,OSError,ValueError,TypeError,KeyError,sqlite3.Error,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print("STOCK 26.2 FINAL ROOT SEMANTIC REVIEW OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
