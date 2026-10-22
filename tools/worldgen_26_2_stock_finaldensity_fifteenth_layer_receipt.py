#!/usr/bin/env python3
"""Pin genuine original 26.2 fifteenth CacheOnce->Ap2 topology, NO new TSV.

Original fourteenth Holder and fifteenth Marker/wrapped values coincide with
the independently immutable thirteenth RIGHT operand at 128/128 points. The
fifteenth source receipt adds class identity and observed numeric equality,
not a distinct original numerical oracle and not an all-input cache law.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_fifteenth_layer as owner
import worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture as prior

REPORT_BYTES = 43502
REPORT_SHA256 = "bc1df68c3245c55735df84c4c2e36bc35b4d349d4a5c9623db24ac9630cbe0f0"
SHAPE = {
    "marker_enum_class": owner.CLASS + "Marker$Type",
    "marker_type": "CacheOnce",
    "marker_wrapped_class": owner.CLASS + "Ap2",
}
TELEMETRY = {
    "marker_wrapped_candidate_mismatches": 0,
    "marker_wrapped_first_mismatch_index": -1,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}


class FifteenthReceiptError(ValueError):
    """The original fifteenth private source-owned receipt is not qualified."""


def validate_original(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise FifteenthReceiptError("genuine fifteenth original report length/SHA changed")
    try:
        report = json.loads(raw)
        owner.validate(report)
        prior_pairs = prior.load()
        if (len(report["shapes"]) != 4 or len(report["vectors"]) != 128
                or len(prior_pairs) != 128):
            raise FifteenthReceiptError("original 4x32 sample dimensions changed")
        for i, shape in enumerate(report["shapes"]):
            if (set(shape) != set(SHAPE) | {"world_seed_bits"}
                    or any(shape[k] != val for k, val in SHAPE.items())
                    or shape["world_seed_bits"] != owner.FINAL.SEEDS[i]):
                raise FifteenthReceiptError("actual fifteenth Marker/CacheOnce/Ap2 shape drift")
        if report["marker_wrapped_candidate_telemetry"] != TELEMETRY:
            raise FifteenthReceiptError("fifteenth observed finite equality telemetry drift")
        for i, (v, (left, right)) in enumerate(
            zip(report["vectors"], prior_pairs, strict=True)
        ):
            old = "0x" + right
            if (v["marker_wrapped_bits"] != old
                    or v["old_marker_target_bits"] != old
                    or v["old_thirteenth_right_holder_bits"] != old):
                raise FifteenthReceiptError(
                    f"fifteenth original child/Marker/Holder vs independent thirteenth row {i}"
                )
        if any(report[k] is not False for k in owner.GATES):
            raise FifteenthReceiptError("original qualification gate promoted")
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise FifteenthReceiptError("genuine fifteenth original fixture/source receipt rejected") from exc
    return {
        "kind": "original_26_2_fifteenth_cacheonce_ap2_equality_only",
        "original_report_sha256": REPORT_SHA256,
        "original_report_bytes": REPORT_BYTES,
        "original_four_seeds": 4,
        "original_singlepointcontext_samples": 128,
        "original_marker_type": SHAPE["marker_type"],
        "original_wrapped_density_class": SHAPE["marker_wrapped_class"],
        "original_wrapped_to_marker_ieee_equalities": 128,
        "original_wrapped_to_old_thirteenth_right_ieee_equalities": 128,
        "new_distinct_ieee_words_to_freeze": 0,
        "new_tsv_created": False,
        "prior_original_fourteenth_report_sha256": owner.previous.REPORT_SHA256,
        "prior_thirteenth_fixture_sha256": prior.SHA256,
        "source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True,
                        help="existing PRIVATE original JVM report; never repeat original capture")
    args = parser.parse_args(argv)
    try:
        receipt = validate_original(args.capture)
    except (OSError, FifteenthReceiptError) as exc:
        print("STOCK 26.2 FIFTEENTH RECEIPT OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
