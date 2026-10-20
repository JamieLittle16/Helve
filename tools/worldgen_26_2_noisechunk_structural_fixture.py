#!/usr/bin/env python3
"""Freeze source-free loop ancestry from pinned original Minecraft 26.2 source.

The original 27255-byte private-source structural JSON is never committed.
This smaller derived receipt certifies lexical loop/call nesting ONLY, not
identifier binding, bounds, cache semantics, canonical fill, or production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_noisechunk_adjacent_fixture as adjacent_fixture
import worldgen_26_2_stock_noisechunk_cell_capture as cell

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"vanilla/reports/worldgen-26_2-noisechunk-source-free-brace-ancestry.json"
FIXTURE_BYTES=6567
FIXTURE_SHA256="7a62758cabb02e7370d7708955c58bdf2010d67551b12059543ae9dd790621a7"
ORIGINAL_JSON_BYTES=27255
ORIGINAL_JSON_SHA256="130070ea39c064d1de37fa0fa3b651b8799e650e066b176a2f419e3e5ff89fab"
KIND="official_26_2_stock_noisechunk_source_free_brace_nesting_summary"
METHOD_LABELS=(
    "generator_do_fill","generator_fill","chunk_initialize",
    "chunk_advance","chunk_select","chunk_update_y","chunk_update_x",
    "chunk_update_z","chunk_swap","chunk_stop","chunk_wrap",
)
GATES=(
    "canonical_control_flow_source_reviewed",
    "stock_noisechunk_canonical_traversal_qualified",
    "stock_noisechunk_full_lifecycle_qualified",
    "full_router_graph_qualified",
    "router_numeric_parity_qualified",
    "world_seed_random_state_bound",
    "independent_var_sem_admitted",
    "production_worldgen_enabled",
    "source_text_included",
)
SHA=re.compile(r"[0-9a-f]{64}\Z")


class FrozenStructuralReviewError(ValueError):
    """Exact original source-owning structural receipt did not validate."""


def load_summary(path:Path=FIXTURE)->dict:
    raw=path.read_bytes()
    if len(raw)!=FIXTURE_BYTES or hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256:
        raise FrozenStructuralReviewError("actual original 26.2 source-free brace receipt changed")
    try:
        summary=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise FrozenStructuralReviewError("invalid source-free structural receipt") from exc
    if (
        summary.get("schema")!=1
        or summary.get("kind")!=KIND
        or summary.get("minecraft")!="26.2"
        or summary.get("source_archive_sha256")!=cell.frozen.SOURCE_SHA256
        or summary.get("original_structural_json_sha256")!=ORIGINAL_JSON_SHA256
        or summary.get("original_structural_json_bytes")!=ORIGINAL_JSON_BYTES
        or any(summary.get(gate) is not False for gate in (
            "source_method_reviewed","canonical_control_flow_source_reviewed",
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "independent_var_sem_admitted","production_worldgen_enabled"
        ))
        or list(summary.get("method_structures",{}))!=list(METHOD_LABELS)
    ):
        raise FrozenStructuralReviewError("invalid source-free structural boundaries")
    do_fill=summary["method_structures"]["generator_do_fill"]
    calls=do_fill["calls"]
    expected_calls=[
        ("initializeForFirstCellX",[]),("advanceCellX",[0]),
        ("selectCellYZ",[0,1,2]),("updateForY",[0,1,2,3]),
        ("updateForX",[0,1,2,3,5]),("updateForZ",[0,1,2,3,5,6]),
        ("swapSlices",[0]),("stopInterpolation",[]),
    ]
    if ([(name,ancestors) for name,_,ancestors in calls]!=expected_calls
        or len(do_fill["controls"])!=10
        or [x[0] for x in do_fill["controls"] if x[0]=="for"]!=["for"]*6
        or [x[3] for x in do_fill["controls"] if x[0]=="for"]!=[
            "increment_hint_only","increment_hint_only",
            "decrement_hint_only","decrement_hint_only",
            "increment_hint_only","increment_hint_only"
        ]
        or summary["method_structures"]["generator_fill"]["calls"]!=[
            ["doFill",17,[1]]
        ]):
        raise FrozenStructuralReviewError("doFill control ancestry differs")
    return summary


def summarize_original(report:dict)->dict:
    if not isinstance(report,dict):
        raise FrozenStructuralReviewError("wrong original report type")
    expected_header={
        "schema":1,
        "kind":"official_26_2_stock_noisechunk_private_structural_nesting_review",
        "minecraft":"26.2","protocol":776,"data_version":4903,
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "analysis_kind":"lexical_brace_and_call_nesting_not_semantic_control_flow",
        "source_text_included":False,
    }
    if (any(type(report.get(k)) is not type(v) or report[k]!=v
            for k,v in expected_header.items())
        or any(report.get(gate) is not False for gate in GATES)
        or set(report)!=set(expected_header)|set(GATES)|{"methods"}):
        raise FrozenStructuralReviewError("original source identity/qualification changed")
    source_methods=adjacent_fixture.source_methods()
    observed_methods=report["methods"]
    if (not isinstance(observed_methods,list) or
        [m.get("label") for m in observed_methods]!=list(METHOD_LABELS)):
        raise FrozenStructuralReviewError("wrong original 11 reviewed method inventory")
    compact={}
    for method in observed_methods:
        label=method["label"]
        frozen=source_methods[label]
        for field in ("owner","signature","body_sha256","normalized_sha256"):
            if method.get(field)!=frozen[field]:
                raise FrozenStructuralReviewError("original source method changed: "+label)
        if method.get("source_method_reviewed") is not False:
            raise FrozenStructuralReviewError("source method reviewed without authority")
        st=method["structure"]
        if (st.get("lexical_control_only") is not True
            or st.get("argument_expressions_source_text_included") is not False
            or st.get("canonical_control_flow_source_reviewed") is not False
            or st.get("unbraced_control_count")!=0):
            raise FrozenStructuralReviewError("missing brace coverage or promoted source review")
        controls=[]
        for i,c in enumerate(st["control_blocks"]):
            if c.get("id")!=i or not SHA.fullmatch(c["header"]["normalized_sha256"]):
                raise FrozenStructuralReviewError("invalid control block")
            controls.append([
                c["kind"],c["relative_line"],c["enclosing_controls"],
                c["loop_direction_hint"],c["header"]["operators"],
            ])
        calls=[]
        for call in st["selected_calls"]:
            if not SHA.fullmatch(call["argument_shape"]["normalized_sha256"]):
                raise FrozenStructuralReviewError("invalid private call expression fingerprint")
            calls.append([call["name"],call["relative_line"],call["enclosing_controls"]])
        compact[label]={"controls":controls,"calls":calls}
    return {
        "schema":1,"kind":KIND,"minecraft":"26.2",
        "source_archive_sha256":cell.frozen.SOURCE_SHA256,
        "original_structural_json_sha256":ORIGINAL_JSON_SHA256,
        "original_structural_json_bytes":ORIGINAL_JSON_BYTES,
        "source_method_reviewed":False,
        "canonical_control_flow_source_reviewed":False,
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
        "method_structures":compact,
    }


def verify_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise FrozenStructuralReviewError("original structural JSON bytes/SHA changed")
    try:
        report=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise FrozenStructuralReviewError("invalid pinned original structural JSON") from exc
    if summarize_original(report)!=load_summary():
        raise FrozenStructuralReviewError("actual original source-owned call nesting disagrees")


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional original exact private-source structural JSON; never commit it")
    args=p.parse_args(argv)
    try:
        summary=load_summary()
        if args.capture is not None:
            verify_original(args.capture)
    except (OSError,KeyError,TypeError,ValueError,
            FrozenStructuralReviewError) as exc:
        print("STOCK 26.2 NOISECHUNK STRUCTURAL RECEIPT UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "source_free_original_brace_nesting_frozen":True,
        "source_methods":len(summary["method_structures"]),
        "do_fill_nested_for_loops":6,
        "original_capture_sha256":ORIGINAL_JSON_SHA256,
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
