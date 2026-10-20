#!/usr/bin/env python3
"""Source-owning, SOURCE-FREE callsite packet for exact stock 26.2 traversal review.

Reads only the user's pinned private Vanilla Atlas and source archive. Emits
bounded method IDs and relevant *syntactic* invocation order; this is a review
aid, NOT control-flow proof, canonical-loop admission or published source text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tomllib
from pathlib import Path

import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent
import worldgen_26_2_stock_noisechunk_cell_capture as cell

KEY_CALLS=frozenset({
    "initializeForFirstCellX","advanceCellX","selectCellYZ","updateForY",
    "updateForX","updateForZ","swapSlices","stopInterpolation","wrap",
    "compute","fillFromNoise","doFill","getOrComputeBlendingOutput",
    "getCellWidth","getCellHeight","blockX","blockY","blockZ",
})
MAX_METHODS=16
MAX_CALLS_PER_METHOD=128


class ReviewPacketError(ValueError):
    """Exact source-owned traversal evidence is not qualified."""


def extract(conn:sqlite3.Connection)->dict:
    methods=adjacent.source_methods(conn)
    if len(methods)!=len(cell.METHODS)+len(adjacent.EXTRA_METHODS):
        raise ReviewPacketError("wrong bounded source review method inventory")
    packet=[]
    for label,item in sorted(methods.items()):
        rows=conn.execute(
            "SELECT m.id,m.start_line,m.end_line,m.param_count FROM methods m "
            "JOIN types t ON t.id=m.type_id WHERE t.qualified_name=? "
            "AND m.signature=?",
            (item["owner"],item["signature"]),
        ).fetchall()
        if len(rows)!=1:
            raise ReviewPacketError("source signature no longer uniquely resolvable: "+label)
        r=rows[0]
        if (not isinstance(r["start_line"],int) or
            not isinstance(r["end_line"],int) or
            r["start_line"]<1 or r["end_line"]<r["start_line"]):
            raise ReviewPacketError("invalid original source line span: "+label)
        calls=conn.execute(
            "SELECT callee_name,arg_count,line,resolution FROM method_calls "
            "WHERE caller_method_id=? ORDER BY line,id",
            (r["id"],),
        ).fetchall()
        if len(calls)>1000:
            raise ReviewPacketError("unbounded original method callsite inventory")
        selected=[]
        for call in calls:
            if call["callee_name"] not in KEY_CALLS:
                continue
            line=call["line"]
            if (not isinstance(line,int) or
                line<r["start_line"] or line>r["end_line"] or
                type(call["arg_count"]) is not int or call["arg_count"]<0):
                raise ReviewPacketError("invalid original callsite bounds: "+label)
            selected.append({
                "name":call["callee_name"],
                "argument_count":call["arg_count"],
                "relative_source_line":line-r["start_line"],
                "resolution":call["resolution"],
            })
        if len(selected)>MAX_CALLS_PER_METHOD:
            raise ReviewPacketError("unbounded selected original invocation list")
        packet.append({
            "label":label,"owner":item["owner"],
            "signature":item["signature"],
            "body_sha256":item["body_sha256"],
            "normalized_sha256":item["normalized_sha256"],
            "reviewed":False,
            "source_lines":r["end_line"]-r["start_line"]+1,
            "selected_syntactic_calls":selected,
        })
    if len(packet)>MAX_METHODS:
        raise ReviewPacketError("unbounded method count")
    return {
        "schema":1,
        "kind":"official_26_2_noisechunk_source_free_lifecycle_review_packet",
        "minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "method_inventory":packet,
        "call_resolution_is_syntactic":True,
        "canonical_control_flow_source_reviewed":False,
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
        "source_text_included":False,
    }


def collect(source:Path,db:Path,lock:Path,output:Path)->dict:
    path=cell.improved.external_output(output)
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=(
        "26.2",776,4903):
        raise ReviewPacketError("wrong pinned source version")
    conn=cell.vanilla_atlas.connect_db(db)
    try:
        sha=cell.source_probe.require_pinned_source(conn,source,lock)
        packet=extract(conn)
    finally:
        conn.close()
    if sha!=cell.frozen.SOURCE_SHA256:
        raise ReviewPacketError("original Java source archive changed")
    payload=(json.dumps(packet,sort_keys=True,indent=2)+"\n").encode("ascii")
    if len(payload)>50_000:
        raise ReviewPacketError("source-free review packet too large")
    path.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),
                   "wb") as stream:
        stream.write(payload)
    return {
        "output":str(path),"sha256":hashlib.sha256(payload).hexdigest(),
        "methods":len(packet["method_inventory"]),
        "canonical_control_flow_source_reviewed":False,
        "production_worldgen_enabled":False,
    }


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=cell.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=cell.primitive.DB)
    p.add_argument("--lock",type=Path,default=cell.primitive.LOCK)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        print(json.dumps(collect(args.source,args.db,args.lock,args.output),
                         sort_keys=True))
    except (OSError,sqlite3.Error,ReviewPacketError,adjacent.AdjacentError,
            cell.NoiseChunkCellError,KeyError,TypeError,ValueError) as exc:
        print("STOCK 26.2 LIFECYCLE SOURCE REVIEW OPEN: "+str(exc),
              file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
