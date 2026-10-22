#!/usr/bin/env python3
"""Genuine stock 26.2 17th right Ap2(ADD) operands, source-only immutable oracle.

Freeze precisely TWO new original-JVM IEEE words per 4x32 original point;
the old right-Ap2 output belongs ONLY to sixteenth immutable TSV RIGHT.
Finite arithmetic agreement does NOT admit general Java/cache/NoiseChunk law.
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

import worldgen_26_2_stock_final_density_seventeenth_layer as owner
import worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_seventeenth_minright_add_children_128_rawbits.tsv"
)
SHA256 = "ef9a7e19fc793ce4d33592756faa73a80d86ad59941ae171820b3ed8eb4263a5"
REPORT_BYTES = 43284
REPORT_SHA256 = "1c9fd95824aef71b68aaeb9c9528cb1adca174d6a258bc002989c3eb2fcac3c1"
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
SHAPE = {
    "ap2_enum_class": owner.CLASS + "TwoArgumentSimpleFunction$Type",
    "ap2_op": "ADD",
    "ap2_left_class": owner.CLASS + "HolderHolder",
    "ap2_right_class": owner.CLASS + "Clamp",
}
TELEMETRY = {
    "arithmetic_candidate_first_mismatch_index": -1,
    "arithmetic_candidate_mismatches": 0,
    "observed_equal_operands": 0,
    "observed_left_strictly_less": 124,
    "observed_right_strictly_less": 4,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}


class SeventeenthFixtureError(ValueError):
    """Stock 26.2 seventeenth exact-original evidence changed."""


def number(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def add_bits(left: str, right: str) -> str:
    a, b = number(left), number(right)
    if not (math.isfinite(a) and math.isfinite(b)):
        raise SeventeenthFixtureError("nonfinite seventeenth source operand")
    result = a + b
    if not math.isfinite(result):
        raise SeventeenthFixtureError("nonfinite seventeenth source sum")
    return struct.pack(">d", result).hex()


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != 4352 or (require_sha and hashlib.sha256(raw).hexdigest() != SHA256):
        raise SeventeenthFixtureError("seventeenth genuine 2-new-only fixture bytes/SHA drift")
    prior_rows = prior.load()
    lines = raw.splitlines(keepends=True)
    if len(lines) != 128 or len(prior_rows) != 128:
        raise SeventeenthFixtureError("original seventeenth 4x32 dimensions moved")
    result = []
    left_less = right_less = equal = 0
    for i, line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise SeventeenthFixtureError(f"seventeenth original IEEE TSV frame malformed {i}")
        left, right = (x.decode("ascii") for x in line[:-1].split(b"\t"))
        if add_bits(left, right) != prior_rows[i][1]:
            raise SeventeenthFixtureError(
                f"independent immutable sixteenth RIGHT ADD parent mismatch row {i}"
            )
        a, b = number(left), number(right)
        left_less += a < b
        right_less += a > b
        equal += a == b
        result.append((left, right))
    if (left_less, right_less, equal) != (124, 4, 0):
        raise SeventeenthFixtureError("original seventeenth finite comparison coverage moved")
    return tuple(result)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise SeventeenthFixtureError("original seventeenth JVM report bytes/SHA drift")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if len(report["shapes"]) != 4 or any(
            set(shape) != set(SHAPE) | {"world_seed_bits"}
            or {k: shape[k] for k in SHAPE} != SHAPE
            or shape["world_seed_bits"] != owner.FINAL.SEEDS[j]
            for j, shape in enumerate(report["shapes"])
        ):
            raise SeventeenthFixtureError("genuine original ADD HolderHolder/Clamp topology moved")
        if report["ap2_arithmetic_candidate_telemetry"] != TELEMETRY:
            raise SeventeenthFixtureError("genuine original ADD finite candidate telemetry changed")
        rows = load()
        old = prior.load()
        for i, (vector, pair) in enumerate(zip(report["vectors"], rows, strict=True)):
            if any(vector[key] != "0x" + word
                   for key, word in zip(owner.NEW_FIELDS, pair, strict=True)):
                raise SeventeenthFixtureError(f"original new ADD child word changed at {i}")
            if vector["old_sixteenth_right_bits"] != "0x" + old[i][1]:
                raise SeventeenthFixtureError(f"original sixteenth RIGHT parent moved at {i}")
        if any(report.get(gate) is not False for gate in owner.GATES):
            raise SeventeenthFixtureError("source-law or production gate promoted")
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise SeventeenthFixtureError("source-owned seventeenth report rejected") from exc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capture", type=Path, help="existing private original JVM JSON; NEVER recapture")
    args = ap.parse_args(argv)
    try:
        rows = load()
        if args.capture:
            validate_original(args.capture)
    except (OSError, SeventeenthFixtureError) as exc:
        print("STOCK 26.2 SEVENTEENTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_seventeenth_right_ap2_add_two_new_children_finite_only",
        "new_only_rows": len(rows),
        "genuine_original_child_ieee_words": 2 * len(rows),
        "independent_old_sixteenth_right_parent_words": len(rows),
        "original_report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": SHA256,
        "bit_exact_original_add_parent_matches": len(rows),
        "observed_left_less": 124,
        "observed_right_less": 4,
        "source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
