#!/usr/bin/env python3
"""Immutable 26.2 twelfth original out-left Ap2 children, sample-only evidence.

Only two NEW genuine original JVM child IEEE words per 4x32 fixed sample;
the old out-left parent is loaded independently from the eleventh fixture.
No stock source text, old fixture duplication or production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twelfth_layer as twelfth
import worldgen_26_2_stock_finaldensity_eleventh_layer_fixture as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_twelfth_outleft_ap2_children_128_rawbits.tsv"
)
SHA256 = "c51d0c1686a5a7160abb2f03c6db5e377b6a2f6fee23cc18bca7a493439b552f"
REPORT_SHA256 = "041eadc4a4174b4bace6eed2270c129cad6c65fe06cdbd7396268216bf26ab26"
REPORT_BYTES = 39658
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
CLASS = twelfth.CLASS
SHAPE = {
    "ap2_enum_class": CLASS + "TwoArgumentSimpleFunction$Type",
    "ap2_op": "MIN",
    "ap2_left_class": CLASS + "Ap2",
    "ap2_right_class": CLASS + "Ap2",
}
TELEMETRY = {
    "direct_arithmetic_candidate_mismatches": 0,
    "direct_arithmetic_first_mismatch_index": -1,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}
RIGHT_WIN_INDICES = (21, 97, 106)


class TwelfthFixtureError(ValueError):
    """Genuine source-owned twelfth finite fixture drift or missing admission."""


def number(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def selected_min(left: str, right: str) -> str:
    """Finite MIN candidate with unqualified ties handled fail-closed."""
    a, b = number(left), number(right)
    if not math.isfinite(a) or not math.isfinite(b):
        raise TwelfthFixtureError("nonfinite original twelfth operand")
    if a == b:
        raise TwelfthFixtureError("unreviewed original twelfth MIN tie / signed-zero")
    return left if a < b else right


def load(
    path: Path = FIXTURE, *, require_sha: bool = True
) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != 128 * 34 or (
        require_sha and hashlib.sha256(raw).hexdigest() != SHA256
    ):
        raise TwelfthFixtureError("genuine twelfth 128x2-only bytes/SHA drift")
    old = prior.load()
    rows = raw.splitlines(keepends=True)
    if len(rows) != 128 or len(old) != 128:
        raise TwelfthFixtureError("bounded original 4x32 sample count changed")
    result = []
    left_wins = right_wins = 0
    right_witnesses = []
    for i, row in enumerate(rows):
        if not LINE.fullmatch(row):
            raise TwelfthFixtureError(f"original twelfth IEEE row malformed: {i}")
        left, right = (w.decode("ascii") for w in row[:-1].split(b"\t"))
        picked = selected_min(left, right)
        if picked != old[i][3]:
            raise TwelfthFixtureError(f"twelfth genuine old eleventh out-left parent drift: {i}")
        if picked == left:
            left_wins += 1
        else:
            right_wins += 1
            right_witnesses.append(i)
        result.append((left, right))
    if (left_wins, right_wins) != (125, 3) or tuple(right_witnesses) != RIGHT_WIN_INDICES:
        raise TwelfthFixtureError("actual source-owned MIN branch coverage changed")
    return tuple(result)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise TwelfthFixtureError("original twelfth JVM report bytes/SHA drift")
    try:
        report = json.loads(raw)
        twelfth.validate(report)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise TwelfthFixtureError("original twelfth report provenance rejected") from exc
    if any(
        {key: value for key, value in shape.items() if key != "world_seed_bits"} != SHAPE
        for shape in report["shapes"]
    ):
        raise TwelfthFixtureError("genuine twelfth Ap2(MIN) child class/operation moved")
    if report["arithmetic_candidate_telemetry"] != TELEMETRY:
        raise TwelfthFixtureError("unadmitted original twelfth arithmetic telemetry changed")
    new, old = load(), prior.load()
    for i, (v, row) in enumerate(zip(report["vectors"], new, strict=True)):
        if any(
            v[key] != "0x" + word
            for key, word in zip(twelfth.NEW_FIELDS, row, strict=True)
        ):
            raise TwelfthFixtureError(f"original twelfth new-only operand moved: {i}")
        if v["old_out_left_bits"] != "0x" + old[i][3]:
            raise TwelfthFixtureError(f"original eleventh parent evidence moved: {i}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", type=Path, help="EXISTING genuine twelfth JVM JSON; do not recapture")
    args = p.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (TwelfthFixtureError, OSError) as exc:
        print("STOCK 26.2 TWELFTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_twelfth_outleft_ap2_min_finite_only",
        "new_only_operand_rows": len(rows),
        "new_only_ieee_words": len(rows) * 2,
        "old_eleventh_parent_ieee_words_anchored": len(rows),
        "bounded_min_parent_candidate_matches": len(rows),
        "min_left_wins": 125,
        "min_right_wins": 3,
        "actual_min_right_witness_indices": list(RIGHT_WIN_INDICES),
        "new_only_fixture_sha256": SHA256,
        "original_twelfth_report_sha256": REPORT_SHA256,
        **{gate: False for gate in twelfth.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
