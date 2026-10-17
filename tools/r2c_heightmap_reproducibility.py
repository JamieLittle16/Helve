#!/usr/bin/env python3
"""Reproducibility audit for source-unadmitted Minecraft 26.2 state facts.

Two independently executed official-server runtime probe outputs must bind to
one exact official server/source identity and produce bit-identical dense
32,366-state heightmap candidates. This is a deterministic artifact check,
NOT a second source predicate oracle and NOT VAR/SEM admission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

import r2c_heightmap_candidate_bytes as candidate

STATE_COUNT = 32366


def compare(original: dict, repeated: dict, lock: dict) -> dict:
    a=candidate.validate_candidate(original,lock)
    b=candidate.validate_candidate(repeated,lock)
    if len(a)!=STATE_COUNT or len(b)!=STATE_COUNT:
        raise ValueError("official state fact universe incomplete")
    if original["server_sha256"] != repeated["server_sha256"]:
        raise ValueError("runtime identity changed between independent probes")
    if original["source_file_sha256"] != repeated["source_file_sha256"]:
        raise ValueError("source-review surface changed between probes")
    if a != b:
        mismatch=next(i for i,(left,right) in enumerate(zip(a,b)) if left!=right)
        raise ValueError(f"official heightmap facts not reproducible at ID {mismatch}")
    # Counts make a future review detect suspicious 'all solid' or 'all
    # non-air' outputs without checking in the full 32,366-byte artifact.
    histogram=[0]*16
    for entry in a:
        histogram[entry]+=1
    if sum(histogram)!=STATE_COUNT:
        raise ValueError("heightmap histogram is not a complete global ID census")
    counts={
        "world_surface":sum((flag&1)!=0 for flag in a),
        "motion_blocking":sum((flag&6)!=0 for flag in a),
        "motion_blocking_no_leaves":sum((flag&6)!=0 and not (flag&8) for flag in a),
        "leaves":sum((flag&8)!=0 for flag in a),
        "fluid_non_empty":sum((flag&4)!=0 for flag in a),
    }
    if not all(0<count<STATE_COUNT for count in counts.values()):
        raise ValueError("official heightmap census lacks expected predicate diversity")
    return {
        "schema":1,
        "target":candidate.EXPECTED_TARGET,
        "state_count":STATE_COUNT,
        "official_server_sha256":original["server_sha256"],
        "official_source_sha256":original["source_archive_sha256"],
        "reproduced_dense_state_fact_sha256":hashlib.sha256(a).hexdigest(),
        "four_bit_histogram":histogram,
        "client_heightmap_state_predicate_counts":counts,
        "official_independent_probe_runs":2,
        "runtime_id_indexed_byte_equality":True,
        "independent_semantic_source_review":False,
        "source_var_sem_admitted":False,
        "production_admitted":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first",type=Path,required=True)
    parser.add_argument("--repeat",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--lock",type=Path,default=Path("vanilla/vanilla.lock.toml"))
    args=parser.parse_args()
    try:
        if args.first.resolve()==args.repeat.resolve():
            raise ValueError("repeat probe must be separately executed, not same input")
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("candidate audit output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(Path(__file__).resolve().parents[1]):
            raise ValueError("candidate audit must not be recorded inside repository")
        with args.lock.open("rb") as f:
            lock=tomllib.load(f)
        output=compare(
            json.loads(args.first.read_text()),json.loads(args.repeat.read_text()),lock
        )
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    except (OSError,KeyError,TypeError,ValueError,json.JSONDecodeError) as e:
        print(f"official R2C heightmap reproducibility FAILED: {e}",file=sys.stderr)
        return 2
    print("Official R2C state facts bit-identical across two independent executions; "
          "source admission FALSE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
