#!/usr/bin/env python3
"""Source-owned, bounded structural review of actual Minecraft 26.2 NoiseChunk control flow.

Unlike the earlier flat Atlas callsite receipt, this tool reopens the *pinned*
private source archive, identifies the exact hashed methods, and produces a
source-free lexical nesting map of controls and selected calls. Neither this
lexical analysis nor apparent loop direction is a source-law/semantic review,
a certified canonical stock traversal, or production worldgen admission.
Never persist source bodies or the original ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tomllib
import zipfile
from pathlib import Path

import vanilla_atlas
import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent
import worldgen_26_2_stock_noisechunk_cell_capture as cell

REVIEW_LABELS=(
    "generator_do_fill","generator_fill",
    "chunk_initialize","chunk_advance","chunk_select",
    "chunk_update_y","chunk_update_x","chunk_update_z",
    "chunk_swap","chunk_stop","chunk_wrap",
)
KEY_CALLS=frozenset({
    "initializeForFirstCellX","advanceCellX","selectCellYZ",
    "updateForY","updateForX","updateForZ","swapSlices",
    "stopInterpolation","wrap","compute","doFill",
})
CONTROL_HEADS=frozenset({"for","while","if","switch","catch","synchronized"})
DIRECT_BLOCKS=frozenset({"else","try","finally","do"})
HEADER_OPERATORS=frozenset({"++","--","<",">","<=",">=","==","!=","+=","-=","&&","||",";"})
MAX_CONTROLS=160
MAX_SELECTED_CALLS=160
MAX_METHOD_TOKENS=45000
MAX_SOURCE_BYTES=2_000_000


class StructureReviewError(ValueError):
    """Pinned 26.2 source-owned structural evidence was not established."""


def _digest(tokens)->str:
    return vanilla_atlas.normalized_fingerprint(tokens)


def _shape(tokens)->dict:
    operators=tuple(t.text for t in tokens if t.text in HEADER_OPERATORS)
    if len(operators)>64:
        raise StructureReviewError("unbounded private expression operators")
    return {
        "normalized_sha256":_digest(tokens),
        "token_count":len(tokens),
        "operators":list(operators),
        "numeric_literal_count":sum(t.kind=="number" for t in tokens),
    }


def _direction(tokens)->str:
    ops=[t.text for t in tokens]
    if "--" in ops and "++" not in ops:
        return "decrement_hint_only"
    if "++" in ops and "--" not in ops:
        return "increment_hint_only"
    return "unknown"


def _find_method(source_text:str,owner:str,signature:str):
    tokens=vanilla_atlas.tokenize_java(source_text)
    braces=vanilla_atlas.matching_pairs(tokens,"{","}")
    parens=vanilla_atlas.matching_pairs(tokens,"(",")")
    package,_=vanilla_atlas.package_and_imports(tokens)
    types=[t for t in vanilla_atlas.extract_types(tokens,package,braces)
           if t.qualified_name==owner]
    if len(types)!=1:
        raise StructureReviewError("private source owner missing or ambiguous")
    methods,_=vanilla_atlas.extract_members(tokens,types[0],parens,braces)
    matching=[m for m in methods if m.signature==signature
              and m.body_open is not None and m.body_close is not None]
    if len(matching)!=1:
        raise StructureReviewError("private source method ambiguous or lacks body")
    return tokens,matching[0],braces,parens


def structural_profile(tokens,method,braces,parens)->dict:
    """Return sanitized brace-nesting and call-argument fingerprints only.

    This deliberately does NOT interpret Java variable bindings, loop bounds,
    branches, lambdas, cache state or the semantics of a density computation.
    Unbraced or unowned blocks appear as explicit open questions.
    """
    lo=method.body_open
    hi=method.body_close
    assert lo is not None and hi is not None
    if hi-lo<1 or hi-lo>MAX_METHOD_TOKENS:
        raise StructureReviewError("unexpected original method token extent")
    controls=[]
    unbraced=0
    for i in range(lo+1,hi):
        name=tokens[i].text
        if name in CONTROL_HEADS:
            if i+1>=hi or tokens[i+1].text!="(" or i+1 not in parens:
                # E.g. 'if' inside malformed source, reject rather than guess.
                raise StructureReviewError("unpaired private control header")
            close=parens[i+1]
            body=close+1
            if body>=hi or tokens[body].text!="{" or body not in braces:
                unbraced+=1
                continue
            body_close=braces[body]
            header=tokens[i+2:close]
        elif name in DIRECT_BLOCKS:
            body=i+1
            if body>=hi or tokens[body].text!="{" or body not in braces:
                unbraced+=1
                continue
            body_close=braces[body]
            header=[]
        else:
            continue
        if body_close>hi or body_close<body:
            raise StructureReviewError("private control block escaped method")
        if len(controls)>=MAX_CONTROLS:
            raise StructureReviewError("unbounded method control blocks")
        controls.append({
            "id":len(controls),
            "kind":name,
            "relative_line":tokens[i].line-tokens[lo].line,
            "body_first_relative_line":tokens[body].line-tokens[lo].line,
            "body_last_relative_line":tokens[body_close].line-tokens[lo].line,
            "header":_shape(header),
            "loop_direction_hint":_direction(header) if name=="for" else "not_a_for_loop",
            "_start":body,
            "_end":body_close,
        })
    # Compute every ancestry relation BEFORE deleting transient token offsets.
    # Deleting one control's offsets inside the first pass corrupts the next
    # control's lookup and must never escape the source-free result.
    for control in controls:
        ancestors=[other["id"] for other in controls
                   if other["_start"]<control["_start"] and
                      control["_end"]<=other["_end"]]
        control["enclosing_controls"]=ancestors
    for control in controls:
        del control["_start"],control["_end"]
    # Regenerate lexical intervals in exactly the same discovery order for call ancestry.
    # This is based only on the braces in the tokenized private method.
    intervals=[]
    for i in range(lo+1,hi):
        name=tokens[i].text
        if name in CONTROL_HEADS and i+1<hi and tokens[i+1].text=="(" and i+1 in parens:
            body=parens[i+1]+1
            if body<hi and tokens[body].text=="{" and body in braces:
                intervals.append((body,braces[body]))
        elif name in DIRECT_BLOCKS and i+1<hi and tokens[i+1].text=="{" and i+1 in braces:
            intervals.append((i+1,braces[i+1]))
    if len(intervals)!=len(controls):
        raise StructureReviewError("private structural control remapping inconsistent")
    calls=[]
    for i in range(lo+1,hi-1):
        name=tokens[i].text
        if name not in KEY_CALLS or tokens[i+1].text!="(" or i+1 not in parens:
            continue
        close=parens[i+1]
        if close>=hi:
            raise StructureReviewError("selected call escapes private method")
        args=tokens[i+2:close]
        if len(calls)>=MAX_SELECTED_CALLS:
            raise StructureReviewError("unbounded selected private method calls")
        calls.append({
            "name":name,
            "relative_line":tokens[i].line-tokens[lo].line,
            "argument_count":vanilla_atlas.count_top_level_items(args),
            "argument_shape":_shape(args),
            "enclosing_controls":[j for j,(start,end) in enumerate(intervals)
                                  if start<i<end],
        })
    return {
        "control_blocks":controls,
        "selected_calls":calls,
        "unbraced_control_count":unbraced,
        "lexical_control_only":True,
        "argument_expressions_source_text_included":False,
        "canonical_control_flow_source_reviewed":False,
    }


def extract(conn:sqlite3.Connection,source:Path)->dict:
    method_identities=adjacent.source_methods(conn)
    selected={}
    for label in REVIEW_LABELS:
        ident=method_identities[label]
        rows=conn.execute(
            "SELECT f.path,m.start_line,m.end_line FROM methods m "
            "JOIN types t ON m.type_id=t.id "
            "JOIN source_files f ON t.file_id=f.id "
            "WHERE t.qualified_name=? AND m.signature=?",
            (ident["owner"],ident["signature"]),
        ).fetchall()
        if len(rows)!=1:
            raise StructureReviewError("missing exact private method in Atlas: "+label)
        selected[label]=(ident,dict(rows[0]))
    reports=[]
    with zipfile.ZipFile(source) as zf:
        file_cache={}
        for label,(ident,where) in selected.items():
            path=where["path"]
            if path not in file_cache:
                info=zf.getinfo(path)
                if info.file_size>MAX_SOURCE_BYTES:
                    raise StructureReviewError("private source file exceeds bounded review size")
                file_cache[path]=zf.read(info).decode("utf-8",errors="replace")
            source_text=file_cache[path]
            tokens,method,braces,parens=_find_method(
                source_text,ident["owner"],ident["signature"])
            if (method.start_line!=where["start_line"] or
                method.end_line!=where["end_line"]):
                raise StructureReviewError("Atlas/private source line mismatch: "+label)
            body=tokens[method.body_open+1:method.body_close]
            raw=source_text[tokens[method.body_open].end:tokens[method.body_close].start]
            if (_digest(body)!=ident["normalized_sha256"] or
                hashlib.sha256(raw.encode()).hexdigest()!=ident["body_sha256"]):
                raise StructureReviewError("Atlas/private source body differs: "+label)
            reports.append({
                "label":label,
                "owner":ident["owner"],
                "signature":ident["signature"],
                "body_sha256":ident["body_sha256"],
                "normalized_sha256":ident["normalized_sha256"],
                "source_method_reviewed":False,
                "structure":structural_profile(tokens,method,braces,parens),
            })
    return {
        "schema":1,
        "kind":"official_26_2_stock_noisechunk_private_structural_nesting_review",
        "minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "methods":reports,
        "analysis_kind":"lexical_brace_and_call_nesting_not_semantic_control_flow",
        "canonical_control_flow_source_reviewed":False,
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "world_seed_random_state_bound":False,
        "full_router_graph_qualified":False,
        "router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
        "source_text_included":False,
    }


def collect(*,source:Path,db:Path,lock:Path,output:Path)->dict:
    target=cell.improved.external_output(output)
    with lock.open("rb") as fp:
        pinned=tomllib.load(fp)
    if (pinned.get("minecraft"),pinned.get("protocol"),pinned.get("data_version"))!=(
        "26.2",776,4903):
        raise StructureReviewError("wrong version lock")
    conn=cell.vanilla_atlas.connect_db(db)
    try:
        source_sha=cell.source_probe.require_pinned_source(conn,source,lock)
        if source_sha!=cell.frozen.SOURCE_SHA256:
            raise StructureReviewError("original source hash changed")
        report=extract(conn,source)
    finally:
        conn.close()
    payload=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode("ascii")
    if len(payload)>240_000:
        raise StructureReviewError("oversized sanitized structural packet")
    target.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as stream:
        stream.write(payload)
    return {
        "output":str(target),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "method_count":len(report["methods"]),
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
        print(json.dumps(collect(
            source=args.source,db=args.db,lock=args.lock,output=args.output
        ),sort_keys=True))
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error,
            zipfile.BadZipFile,adjacent.AdjacentError,
            cell.NoiseChunkCellError) as exc:
        print("STOCK 26.2 NOISECHUNK STRUCTURAL REVIEW OPEN: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
