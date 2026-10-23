#!/usr/bin/env python3
"""Stock 26.2 original nineteenth Clamp-wrapped Ap2(ADD) child-only receipt.

Freeze exactly two new original JVM IEEE words per 4x32 fixed point.
The old eighteenth Clamp-inner parent is independently reconstructed from the
previous immutable TWO-OVERRIDE receipt, never copied into this fixture.
Finite arithmetic agreement admits no all-input Ap2/cache/NoiseChunk law.
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

import worldgen_26_2_stock_final_density_nineteenth_layer as owner
import worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_nineteenth_clamp_ap2_add_children_128_rawbits.tsv"
)
FIXTURE_BYTES = 4352
SHA256 = "77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4"
REPORT_BYTES = 43278
REPORT_SHA256 = "a79b4d191a42f3f264d5e44757aa75c56cdf5077258d36c967207b058695e1f1"
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
SHAPE = {
    "ap2_enum_class": owner.CLASS + "TwoArgumentSimpleFunction$Type",
    "ap2_op": "ADD",
    "ap2_left_class": owner.CLASS + "Ap2",
    "ap2_right_class": owner.CLASS + "MulOrAdd",
}
TELEMETRY = {
    "original_bounded_points": 128,
    "arithmetic_candidate_mismatches": 0,
    "arithmetic_candidate_first_mismatch_index": -1,
    "observed_left_strictly_less": 0,
    "observed_right_strictly_less": 128,
    "observed_equal_operands": 0,
    "source_law_admitted": False,
}


class NineteenthFixtureError(ValueError):
    """Immutable original nineteenth child word, provenance or gate mismatch."""


def add_bits(left: str, right: str) -> str:
    a, b = (struct.unpack(">d", bytes.fromhex(word))[0] for word in (left, right))
    if not (math.isfinite(a) and math.isfinite(b)):
        raise NineteenthFixtureError("nonfinite original nineteenth Ap2 operand")
    result = a + b
    if not math.isfinite(result):
        raise NineteenthFixtureError("nonfinite original nineteenth Ap2 sum")
    return struct.pack(">d", result).hex()


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != FIXTURE_BYTES or (require_sha and hashlib.sha256(raw).hexdigest() != SHA256):
        raise NineteenthFixtureError("original nineteenth two-child fixture bytes/SHA moved")
    records = raw.splitlines(keepends=True)
    old = prior.load()
    if len(records) != 128 or len(old) != 128:
        raise NineteenthFixtureError("original nineteenth 4x32 dimensions moved")
    rows: list[tuple[str, str]] = []
    left_less = right_less = ties = 0
    for i, record in enumerate(records):
        if not LINE.fullmatch(record):
            raise NineteenthFixtureError(f"strict nineteenth rawbits frame malformed at {i}")
        left, right = (item.decode("ascii") for item in record[:-1].split(b"\t"))
        if add_bits(left, right) != old[i]:
            raise NineteenthFixtureError(f"independently pinned eighteenth raw Ap2 parent drift at {i}")
        a = struct.unpack(">d", bytes.fromhex(left))[0]
        b = struct.unpack(">d", bytes.fromhex(right))[0]
        left_less += a < b
        right_less += a > b
        ties += a == b
        rows.append((left, right))
    if (left_less, right_less, ties) != (0, 128, 0):
        raise NineteenthFixtureError("original nineteenth finite comparison coverage drift")
    return tuple(rows)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise NineteenthFixtureError("nineteenth original JVM report bytes/SHA mismatch")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if len(report["shapes"]) != 4 or any(
            set(s) != set(SHAPE) | {"world_seed_bits"}
            or {k: s[k] for k in SHAPE} != SHAPE
            or s["world_seed_bits"] != owner.FINAL.SEEDS[i]
            for i, s in enumerate(report["shapes"])
        ):
            raise NineteenthFixtureError("real nineteenth ADD(Ap2,MulOrAdd) classes changed")
        if report["ap2_arithmetic_candidate_telemetry"] != TELEMETRY:
            raise NineteenthFixtureError("original bounded nineteenth candidate telemetry drift")
        rows, old = load(), prior.load()
        for i, (v, row) in enumerate(zip(report["vectors"], rows, strict=True)):
            if any(v[k] != "0x" + word for k, word in zip(owner.NEW_FIELDS, row, strict=True)):
                raise NineteenthFixtureError(f"new nineteenth original child IEEE altered at {i}")
            if v["old_eighteenth_clamp_inner_bits"] != "0x" + old[i]:
                raise NineteenthFixtureError(f"old eighteenth original raw parent altered at {i}")
        if any(report.get(gate) is not False for gate in owner.GATES):
            raise NineteenthFixtureError("all-input or production source gate promoted")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise NineteenthFixtureError("nineteenth source-authentic original report rejected") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="existing PRIVATE original JVM JSON; do not recapture")
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (NineteenthFixtureError, OSError) as exc:
        print("STOCK 26.2 NINETEENTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_nineteenth_clamp_ap2_add_two_new_children_unadmitted",
        "report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": SHA256,
        "genuine_original_4x32_points": len(rows),
        "truly_new_original_ieee_words": 2 * len(rows),
        "old_eighteenth_raw_parent_words_reused": len(rows),
        "original_bounded_add_parent_matches": len(rows),
        "observed_right_strictly_less": 128,
        "source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
