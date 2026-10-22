#!/usr/bin/env python3
"""Genuine fourteenth Marker target receipt; NO duplicate numerical fixture.

Only source-owning new evidence is Holder$Direct -> Marker class identity.
Original target IEEE values all duplicate the independently immutable
thirteenth RIGHT operand (128/128) and must never be committed again.
The private original 26.2 report is pinned by its exact length and SHA.
All source laws and production gates remain unadmitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_fourteenth_layer as owner
import worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture as prior

REPORT_BYTES = 36371
REPORT_SHA256 = "8d258327bb24a5b8f6d6a3a64ad6ab751fd5dea7706b80ca88e42ca6a2b43492"
SHAPE = {
    "holder_class": owner.CLASS + "HolderHolder",
    "holder_container_class": "net.minecraft.core.Holder$Direct",
    "target_class": owner.CLASS + "Marker",
}
TELEMETRY = {
    "direct_target_forward_candidate_mismatches": 0,
    "direct_target_forward_first_mismatch_index": -1,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}


class FourteenthReceiptError(ValueError):
    """Original JVM report/real Marker target identity failed a pinned gate."""


def validate_original(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise FourteenthReceiptError("fourteenth genuine original JVM report length/SHA changed")
    try:
        report = json.loads(raw)
        owner.validate(report)
        shapes = report["shapes"]
        vectors = report["vectors"]
        old = prior.load()
        if len(shapes) != 4 or len(vectors) != 128 or len(old) != 128:
            raise FourteenthReceiptError("genuine 4x32 source evidence size drift")
        for j, shape in enumerate(shapes):
            if (set(shape) != set(SHAPE) | {"world_seed_bits"}
                    or {key: shape[key] for key in SHAPE} != SHAPE
                    or shape["world_seed_bits"] != owner.FINAL.SEEDS[j]):
                raise FourteenthReceiptError("original Holder$Direct -> Marker shape drift")
        if report["holder_forward_candidate_telemetry"] != TELEMETRY:
            raise FourteenthReceiptError("fourteenth all-false candidate telemetry drift")
        for i, (v, old_pair) in enumerate(zip(vectors, old, strict=True)):
            original_right = "0x" + old_pair[1]
            if (v["holder_target_bits"] != original_right
                    or v["old_thirteenth_right_holder_bits"] != original_right):
                raise FourteenthReceiptError(f"original target/Holder/old thirteenth mismatch {i}")
        if any(report.get(k) is not False for k in owner.GATES):
            raise FourteenthReceiptError("unadmitted source/production gate was changed")
    except (TypeError, ValueError, KeyError, IndexError) as exc:
        raise FourteenthReceiptError("original fourteenth source/parent/shape receipt rejected") from exc
    return {
        "kind": "original_26_2_fourteenth_direct_holder_to_marker_equality_only",
        "original_private_report_bytes": REPORT_BYTES,
        "original_private_report_sha256": REPORT_SHA256,
        "real_original_world_seeds": 4,
        "bounded_original_points": 128,
        "delegate_vs_old_holder_bit_exact_matches": 128,
        "independent_thirteenth_right_fixture_bit_exact_matches": 128,
        "unique_new_original_ieee_words_to_freeze": 0,
        "new_only_tsv_created": False,
        "original_holder_class": SHAPE["holder_class"],
        "original_holder_container_class": SHAPE["holder_container_class"],
        "original_holder_delegate_class": SHAPE["target_class"],
        "original_thirteenth_fixture_sha256": prior.SHA256,
        "source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True,
                        help="private existing original JVM JSON (NEVER recapture)")
    args = parser.parse_args(argv)
    try:
        receipt = validate_original(args.capture)
    except (OSError, FourteenthReceiptError) as exc:
        print("STOCK 26.2 FOURTEENTH RECEIPT OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
