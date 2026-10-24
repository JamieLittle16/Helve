#!/usr/bin/env python3
"""Authenticate the 23rd original 26.2 spaghetti registry parameter receipt.

The private source-owned JSON is optional input, not a committed oracle.
The one numerical noise leaf remains in the previously frozen 21st fixture.
No redundant output TSV, source-law promotion or production authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twenty_third_layer as owner
import worldgen_26_2_stock_finaldensity_twenty_second_structure_receipt as prior

REPORT_BYTES = 33486
REPORT_SHA256 = "e3dde9db3a83e7cd16c126536475943728e73c11a4ddd44820a2cad4f35ffc05"
FIRST_OCTAVE = "-8"
AMPLITUDES = "3ff0000000000000"
PARAMETERS = {
    **prior.STRUCTURE,
    "noise_first_octave": FIRST_OCTAVE,
    "noise_amplitudes_rawbits": AMPLITUDES,
}
TELEMETRY = {
    "genuinely_new_sample_ieee_words": 0,
    "old_twenty_first_noise_anchors_matched": 128,
    "original_bounded_points": 128,
    "original_parameter_shapes_observed": 4,
    "source_law_admitted": False,
}


class TwentyThirdReceiptError(ValueError):
    """Original source-owned parameter identity, numeric anchor or gate drift."""


def validate_original(path: Path) -> dict:
    content = path.read_bytes()
    if len(content) != REPORT_BYTES or hashlib.sha256(content).hexdigest() != REPORT_SHA256:
        raise TwentyThirdReceiptError("original 23rd report bytes/SHA drift")
    try:
        report = json.loads(content)
        owner.validate(report)
        if report["parameter_candidate_telemetry"] != TELEMETRY:
            raise TwentyThirdReceiptError("original four-seed parameter telemetry drift")
        for index, shape in enumerate(report["shapes"]):
            if shape != {**PARAMETERS, "world_seed_bits": owner.FINAL.SEEDS[index]}:
                raise TwentyThirdReceiptError(
                    f"original spaghetti NoiseParameters record drift at seed {index}"
                )
        old = owner.prior_leaf.load()
        if len(report["vectors"]) != 128 or len(old) != 128:
            raise TwentyThirdReceiptError("source-owned 128 old Noise points missing")
        for index, row in enumerate(report["vectors"]):
            if row["old_twenty_first_noise_bits"] != "0x" + old[index]:
                raise TwentyThirdReceiptError(
                    f"genuine twenty-first source Noise output altered at {index}"
                )
        if any(report[gate] is not False for gate in owner.GATES):
            raise TwentyThirdReceiptError("source/production admission gate promoted")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise TwentyThirdReceiptError("source-owned 23rd parameter receipt rejected") from exc
    return {
        "kind": "original_26_2_finaldensity_23rd_spaghetti_parameters_only_unadmitted",
        "original_report_sha256": REPORT_SHA256,
        "original_report_bytes": REPORT_BYTES,
        "noise_key": PARAMETERS["noise_parameters_key"],
        "first_octave": int(FIRST_OCTAVE),
        "amplitudes_rawbits": AMPLITUDES,
        "old_noise_values_anchored": 128,
        "new_density_sample_words": 0,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        **{gate: False for gate in owner.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = validate_original(args.capture)
    except (TwentyThirdReceiptError, OSError) as exc:
        print("STOCK 26.2 TWENTY-THIRD PARAMETER RECEIPT OPEN: " + str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
