#!/usr/bin/env python3
"""Genuine 26.2 eighteenth Clamp source receipt: ONLY 2 distinct new words.

Four stock-RandomState seed groups yield original Clamp[-1,1] wrapping Ap2.
At 126/128 original SinglePointContext samples the inner word equals old
seventeenth Clamp output, already independently immutable. The OTHER 2
inner values are truly new and held in the two-row override TSV. No full
128-row numerical copy; no all-input Clamp/cache/NoiseChunk source law.
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

import worldgen_26_2_stock_final_density_eighteenth_layer as owner
import worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_eighteenth_clamp_true_new_two_overrides_128.tsv"
)
FIXTURE_BYTES = 40
SHA256 = "e1b4da2ef965a0e92ad2bb56931de16dce95318f3aadabd4e78be2721a5b2811"
REPORT_BYTES = 36555
REPORT_SHA256 = "4e8279f53b06a6de9154f18df073b742ad091acfe6b156611bc916dbbf8781ae"
SHAPE = {
    "clamp_class": owner.CLASS + "Clamp",
    "clamp_input_class": owner.CLASS + "Ap2",
    "clamp_min_bits": "bff0000000000000",
    "clamp_max_bits": "3ff0000000000000",
}
OVERRIDES = {
    18: "3ff5c1c9c20d14a4",
    28: "3ff219c5d9c551b1",
}
TELEMETRY = {
    "original_bounded_points": 128,
    "clamp_candidate_mismatches": 0,
    "clamp_candidate_first_mismatch_index": -1,
    "observed_below_min": 0,
    "observed_within_inclusive_bounds": 126,
    "observed_above_max": 2,
    "source_law_admitted": False,
}
LINE = re.compile(rb"(?:0|[1-9][0-9]*)\t[0-9a-f]{16}\n\Z")


class EighteenthReceiptError(ValueError):
    """Original bounded eighteenth rawbits, ancestry or source pin changed."""


def value(bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(bits))[0]


def minmax(bits: str) -> str:
    x = value(bits)
    if not math.isfinite(x):
        raise EighteenthReceiptError("eighteenth original Clamp candidate nonfinite")
    result = max(-1.0, min(1.0, x))
    return struct.pack(">d", result).hex()


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != FIXTURE_BYTES or (require_sha and hashlib.sha256(raw).hexdigest() != SHA256):
        raise EighteenthReceiptError("two actual original eighteenth override fixture SHA/bytes moved")
    records = raw.splitlines(keepends=True)
    if len(records) != 2:
        raise EighteenthReceiptError("only two real out-of-bound original eighteenth samples")
    overrides = {}
    for record in records:
        if not LINE.fullmatch(record):
            raise EighteenthReceiptError("strict two-row eighteenth override syntax drift")
        idx_raw, bits = record[:-1].split(b"\t")
        index = int(idx_raw)
        if index in overrides:
            raise EighteenthReceiptError("duplicate eighteenth original frame")
        overrides[index] = bits.decode("ascii")
    if overrides != OVERRIDES:
        raise EighteenthReceiptError("source-owner eighteenth observed indices/IEEE words changed")
    old = prior.load()
    if len(old) != 128:
        raise EighteenthReceiptError("older seventeenth genuine source fixture changed dimensions")
    result = tuple(overrides.get(i, words[1]) for i, words in enumerate(old))
    above = below = inside = 0
    for i, (inner, (_, old_clamp)) in enumerate(zip(result, old, strict=True)):
        v = value(inner)
        if v > 1.0:
            above += 1
        elif v < -1.0:
            below += 1
        else:
            inside += 1
        if minmax(inner) != old_clamp:
            raise EighteenthReceiptError(f"true original seventeenth immutable Clamp parent drift at {i}")
        if (i in OVERRIDES) != (inner != old_clamp):
            raise EighteenthReceiptError(f"source-only equality vs true clipped override moved at {i}")
    if (below, inside, above) != (0, 126, 2):
        raise EighteenthReceiptError("original eighteenth true Clamp branch coverage changed")
    return result


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise EighteenthReceiptError("genuine full original eighteenth report SHA/bytes moved")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if len(report["shapes"]) != 4 or any(
            set(s) != set(SHAPE) | {"world_seed_bits"}
            or {k: s[k] for k in SHAPE} != SHAPE
            or s["world_seed_bits"] != owner.FINAL.SEEDS[i]
            for i, s in enumerate(report["shapes"])
        ):
            raise EighteenthReceiptError("original eighteenth Clamp[-1,+1] actual Ap2 source shape changed")
        if report["clamp_candidate_telemetry"] != TELEMETRY:
            raise EighteenthReceiptError("original finite Clamp original 2/126/0 coverage changed")
        expected = load()
        old = prior.load()
        if len(report["vectors"]) != 128:
            raise EighteenthReceiptError("eighteenth actual original finite sample count moved")
        for i, (frame, raw_new) in enumerate(zip(report["vectors"], expected, strict=True)):
            if frame["clamp_inner_bits"] != "0x" + raw_new:
                raise EighteenthReceiptError(f"original eighteenth true wrapped input moved at {i}")
            if frame["old_seventeenth_clamp_bits"] != "0x" + old[i][1]:
                raise EighteenthReceiptError(f"original seventeenth parent old anchor changed at {i}")
        if any(report.get(gate) is not False for gate in owner.GATES):
            raise EighteenthReceiptError("original source/production law gate improperly admitted")
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        raise EighteenthReceiptError("original eighteenth complete source report rejected") from exc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capture", type=Path, help="existing PRIVATE 18th original JSON, NEVER recapture")
    args = ap.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (OSError, EighteenthReceiptError) as exc:
        print("STOCK 26.2 EIGHTEENTH RECEIPT OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_eighteenth_real_clamp_ap2_two_distinct_new_only_words",
        "report_sha256": REPORT_SHA256,
        "new_only_override_fixture_sha256": SHA256,
        "genuine_original_4x32_points": len(rows),
        "truly_new_original_ieee_words": 2,
        "values_identical_to_previous_17th_right_ieee": 126,
        "original_clamp_overflow_indices": sorted(OVERRIDES),
        "candidate_original_clamp_parent_matches": 128,
        "all_input_clamp_source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
