#!/usr/bin/env python3
"""Fail-closed 1,920-vector real JVM stock mixed-density reference qualification.

This validates the exact source-free official capture, numeric fixture and
twelve source method body fingerprints; never generates test answers from Rust.
A frozen oracle plus a matching Rust test still does not independently source
admit arbitrary vanilla router delegates or enable production worldgen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_mixed_density_capture as source
import worldgen_26_2_stock_worldseed_fixture as frozen

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "crates/world/helve-world-gen/tests/data/stock_mixed_density_1920_rawbits.txt"
FIXTURE_SHA256 = "13d279c3ad4d1d79e991846deedd532d096fa2eb20df2d428ff1640b9fce8062"
ORIGINAL_JSON_SHA256 = "4e998fc577236b50fa8b9b31188eef19e56aa35210fe889498016bac038ed305"
HEX16 = re.compile(r"[0-9a-f]{16}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
LEVEL = "net.minecraft.world.level.levelgen."
METHODS = {
    "composition_factories": {
        "add_factory": (LEVEL + "DensityFunctions",
                        "aff60df9dc11f0e52d061660cf39684dfd671e214ab185174a293ce96ddebe58"),
        "mul_factory": (LEVEL + "DensityFunctions",
                        "c5d5aaa53f8650d9068362c193487625eeeb057633eaafb0142651a4cc29d7f1"),
    },
    "density_primitives": {
        "constant_compute": (LEVEL + "DensityFunctions$Constant",
                             "2d4dca61b23e524980e837ac3183e3edd2a497f42abcb88620ddad83b5b30b79"),
        "constant_factory": (LEVEL + "DensityFunctions",
                             "1a3c5fd8ef141a6cd9bf8fe2b1475e267bb8f426e074f3636cb544a8e9d9aa37"),
        "gradient_compute": (LEVEL + "DensityFunctions$YClampedGradient",
                             "e4ec69f8b92efb95bb0948e7fefa5ffc3d01ee9c360f94fdc3ff9693f4f52174"),
        "gradient_factory": (LEVEL + "DensityFunctions",
                             "35213bdd109633d9be131dbe43fa5a5a20dd07ba35ab21291d6a51ebd36e8635"),
    },
    "worldseed_noise": {
        "density_noise_compute": (LEVEL + "DensityFunctions$Noise",
                                  "bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe"),
        "noise_holder_get_value": (LEVEL + "DensityFunction$NoiseHolder",
                                   "16b3035c3a03b2c0ae5765579640510ad52b92f3e7370b14bf3045b8f53ce782"),
        "noises_instantiate": (LEVEL + "Noises",
                               "910d2ef48901972b27273b518c42b3e01bfd8944af650a519b567f64976c90aa"),
        "random_state_create_provider": (LEVEL + "RandomState",
                                         "b9595526d577f99d4b569fa845748c75ad9cbf77c205b59027fe651f64bda77d"),
        "random_state_get_noise": (LEVEL + "RandomState",
                                   "056547e13816f7c7dd9a3a82e1acadbbc7e5729da50b3103f28b6d20a115e7ca"),
        "stock_vanilla_lookup": ("net.minecraft.data.registries.VanillaRegistries",
                                 frozen.VANILLA_STOCK_LOOKUP_SHA256),
    },
}
DELEGATES = {
    profile: {
        "implementation_class": LEVEL + (
            "DensityFunctions$Ap2" if index < 4 else "DensityFunctions$MulOrAdd"),
        "compute_declaring_class": LEVEL + (
            "DensityFunctions$Ap2" if index < 4 else "DensityFunctions$PureTransformer"),
        "superclass": "java.lang.Record",
    }
    for index, profile in enumerate(source.PROFILES)
}


class StockMixedFixtureError(ValueError):
    """An independently acquired Minecraft 26.2 source-free oracle changed."""


def read_bits(path: Path = FIXTURE) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != 1920 * 17 or hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise StockMixedFixtureError("mixed stock oracle length/SHA-256 changed")
    try:
        records = raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise StockMixedFixtureError("mixed stock oracle contains non-ASCII bytes") from exc
    if len(records) != 1920:
        raise StockMixedFixtureError("mixed stock oracle row count changed")
    bits = []
    for index, line in enumerate(records):
        if len(line) != 17 or not line.endswith("\n") or not HEX16.fullmatch(line[:-1]):
            raise StockMixedFixtureError("noncanonical JVM word at row " + str(index))
        word = int(line[:-1], 16)
        if ((word >> 52) & 0x7ff) == 0x7ff:
            raise StockMixedFixtureError("nonfinite JVM word at row " + str(index))
        bits.append(line[:-1])
    if (bits[0], bits[384], bits[576], bits[-1]) != (
        "bfda6cdb9e1f1c66", "8000000000000000",
        "0000000000000000", "3fae82b27db6a527"
    ):
        raise StockMixedFixtureError("official JVM raw-bit anchor changed")
    return tuple(bits)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != 483143 or hashlib.sha256(raw).hexdigest() != ORIGINAL_JSON_SHA256:
        raise StockMixedFixtureError("original official 1,920-capture SHA/size changed")
    try:
        manifest = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise StockMixedFixtureError("malformed official mixed JSON") from exc
    methods = manifest.get("source_methods")
    if not isinstance(methods, dict) or set(methods) != set(METHODS):
        raise StockMixedFixtureError("wrong exact source method inventory")
    for category, known in METHODS.items():
        items = methods.get(category)
        if not isinstance(items, dict) or set(items) != set(known):
            raise StockMixedFixtureError("changed official source-method family: " + category)
        for name, (owner, digest) in known.items():
            record = items[name]
            if not isinstance(record, dict) or set(record) != {
                "owner", "signature", "body_sha256", "normalized_sha256"
            } or record.get("owner") != owner or record.get("body_sha256") != digest \
               or not isinstance(record.get("signature"), str) \
               or not record["signature"] or not isinstance(record.get("normalized_sha256"), str) \
               or SHA.fullmatch(record["normalized_sha256"]) is None:
                raise StockMixedFixtureError("unverified official source method: " + name)
    if manifest.get("delegates") != DELEGATES:
        raise StockMixedFixtureError("official 26.2 mixed compute delegate identity changed")
    try:
        source.validate(
            manifest, source_sha=frozen.SOURCE_SHA256,
            server_sha=frozen.SERVER_SHA256,
            methods=methods, delegates=DELEGATES,
        )
    except source.MixedDensityCaptureError as exc:
        raise StockMixedFixtureError("original stock mixed capture rejected: " + str(exc)) from exc
    for index, (line, actual) in enumerate(zip(read_bits(), manifest["vectors"], strict=True)):
        if actual["value_bits"] != "0x" + line:
            raise StockMixedFixtureError("official JVM capture/fixture differ at row " + str(index))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-json", type=Path,
                        help="optional exact original source-free JVM receipt")
    opts = parser.parse_args(argv)
    try:
        records = read_bits()
        if opts.original_json is not None:
            validate_original(opts.original_json)
    except (StockMixedFixtureError, OSError, KeyError, TypeError) as exc:
        print("UNQUALIFIED 26.2 STOCK MIXED JVM FIXTURE: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "official_jvm_mixed_output_rows": len(records),
        "fixture_sha256": FIXTURE_SHA256,
        "original_json_sha256": ORIGINAL_JSON_SHA256,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
