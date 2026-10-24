#!/usr/bin/env python3
"""Twenty-fifth original Java 26.2: two ABS(Mapped(IntervalSelect)) branches.

Keep only the 256 genuinely NEW IntervalSelect child IEEE words.
Anchor 256 OLD ABS parent words to independently frozen 24th Mapped outputs.
No private report in Git, no source-law or production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twenty_fifth_layer as original
import worldgen_26_2_stock_finaldensity_twenty_fourth_layer_fixture as previous

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_twenty_fifth_two_interval_inputs_128_rawbits.tsv"
)
FIXTURE_BYTES = 4352
FIXTURE_SHA256 = "4ac7d5ca7e89bfc4b962651ec829a2a8f39b94dbb38126a9a8d2da05eca40c41"
REPORT_BYTES = 52861
REPORT_SHA256 = "ae0ea421f3d0643f28ba07c8f1e2d5767a1ad5291c313cabbfebd6378447db50"
SHAPE = {
    "first_mapped_enum_class": original.CLASS + "Mapped$Type",
    "first_mapped_kind": "ABS",
    "first_mapped_input_class": original.CLASS + "IntervalSelect",
    "second_mapped_enum_class": original.CLASS + "Mapped$Type",
    "second_mapped_kind": "ABS",
    "second_mapped_input_class": original.CLASS + "IntervalSelect",
}
TELEMETRY = {
    "genuinely_new_sample_ieee_words": 256,
    "old_twenty_fourth_mapped_anchors_matched": 256,
    "original_bounded_points": 128,
    "original_two_mapped_shapes_observed": 4,
    "source_law_admitted": False,
}
WORD_FRAME = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n")
ABS_MASK = 0x7fff_ffff_ffff_ffff


class OriginalTwentyFifthError(ValueError):
    """Genuine source-owned 25th oracle, structure, arithmetic or provenance drift."""


def load(path: Path = FIXTURE, *, check_digest: bool = True) -> tuple[tuple[str, str], ...]:
    data = path.read_bytes()
    if len(data) != FIXTURE_BYTES or (
        check_digest and hashlib.sha256(data).hexdigest() != FIXTURE_SHA256
    ):
        raise OriginalTwentyFifthError("real 25th new-only 256 IEEE words changed")
    old = previous.load()
    frames = data.splitlines(keepends=True)
    if len(frames) != 128 or len(old) != 128:
        raise OriginalTwentyFifthError("original 4x32 child dimensions changed")
    observed = []
    signs = [0, 0]
    for index, (frame, previous_row) in enumerate(zip(frames, old)):
        if not WORD_FRAME.fullmatch(frame):
            raise OriginalTwentyFifthError(f"invalid original IEEE frame {index}")
        words = tuple(part.decode("ascii") for part in frame[:-1].split(b"\t"))
        for side in range(2):
            bits = int(words[side], 16)
            sample = struct.unpack(">d", bits.to_bytes(8, "big"))[0]
            if not (-float("inf") < sample < float("inf")):
                raise OriginalTwentyFifthError(f"nonfinite mapped input {index}/{side}")
            signs[side] += sample < 0
            if f"{bits & ABS_MASK:016x}" != previous_row[side]:
                raise OriginalTwentyFifthError(
                    f"genuine 25th ABS input to old 24th Mapped parent drift {index}/{side}"
                )
        observed.append(words)
    if signs != [65, 66]:
        raise OriginalTwentyFifthError("two source-owned IntervalSelect input sign witnesses drift")
    return tuple(observed)


def validate_original(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) != REPORT_BYTES or hashlib.sha256(data).hexdigest() != REPORT_SHA256:
        raise OriginalTwentyFifthError("private original 25th report byte/SHA drift")
    try:
        report = json.loads(data)
        original.validate(report)
        if (
            len(report["shapes"]) != 4
            or any(s != {**SHAPE, "world_seed_bits": original.FINAL.SEEDS[i]}
                   for i, s in enumerate(report["shapes"]))
            or report["mapped_inputs_candidate_telemetry"] != TELEMETRY
            or len(report["vectors"]) != 128
        ):
            raise OriginalTwentyFifthError("actual two ABS(IntervalSelect) source shapes changed")
        rows = load()
        prior_rows = previous.load()
        for i, record in enumerate(report["vectors"]):
            if tuple(record[k][2:] for k in original.NEW_FIELDS) != rows[i]:
                raise OriginalTwentyFifthError(f"original new-only 25th input drift {i}")
            if tuple(record[k][2:] for k in original.OLD_FIELDS) != prior_rows[i]:
                raise OriginalTwentyFifthError(f"independent 24th original parent drift {i}")
        if any(report[g] is not False for g in original.GATES):
            raise OriginalTwentyFifthError("unqualified real source gate promoted")
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        raise OriginalTwentyFifthError("private original 25th report rejected") from exc
    return {
        "original_report_sha256": REPORT_SHA256,
        "original_new_only_fixture_sha256": FIXTURE_SHA256,
        "original_bounded_points": 128,
        "new_interval_ieee_words": 256,
        "reused_twenty_fourth_mapped_parent_words": 256,
        "first_interval_negative": 65,
        "second_interval_negative": 66,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        **{gate: False for gate in original.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="original PRIVATE JVM layer-25 report")
    args = parser.parse_args(argv)
    try:
        result = validate_original(args.capture) if args.capture else {
            "new_interval_ieee_words": len(load()) * 2,
            "original_report_sha256": REPORT_SHA256,
            "new_only_fixture_sha256": FIXTURE_SHA256,
            "source_law_admitted": False,
            "production_worldgen_enabled": False,
            **{gate: False for gate in original.GATES},
        }
    except (OriginalTwentyFifthError, OSError) as exc:
        print("STOCK 26.2 25TH ORIGINAL ABS RECEIPT OPEN: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
