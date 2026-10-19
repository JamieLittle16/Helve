#!/usr/bin/env python3
"""Compare source-free 64-bit noise/density vector captures without float conversion.

This tool compares an independently obtained official 26.2 *candidate* oracle
to a Helve candidate. Matching vectors are useful evidence, NOT proof that
the official archive, methods, seed pipeline or production path are admitted.
No official Java source, runtime bytes or extracted code are ever stored here.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vanilla/vanilla.lock.toml"
HEX64 = re.compile(r"0x[0-9a-f]{16}\Z")
STAGES = frozenset({
    "rng_seed", "improved_noise", "perlin_noise", "normal_noise",
    "density_router", "aquifer", "climate", "surface_rule"
})
VECTOR_FIELDS = ("seed_bits", "x_bits", "y_bits", "z_bits", "value_bits")
INPUT_FIELDS = VECTOR_FIELDS[:-1]


class OracleError(ValueError):
    """The provided evidence is incomplete, invalid or inconsistent."""


def _fixed_hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise OracleError(f"{name}: expected 0x and exactly sixteen lowercase hex digits")
    return value


def validate(manifest: object, lock: dict, kind: str) -> dict[tuple[str, ...], str]:
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise OracleError("unsupported noise oracle manifest schema")
    expected_keys = {
        "schema", "kind", "minecraft", "protocol", "data_version",
        "source_archive_sha256", "official_server_sha256", "stage",
        "method_body_sha256", "source_text_included",
        "independent_var_sem_admitted", "production_worldgen_enabled", "vectors",
    }
    if set(manifest) != expected_keys:
        raise OracleError("unexpected manifest metadata or source-rich payload")
    if manifest.get("kind") != kind:
        raise OracleError("candidate/oracle role mismatch")
    for field, expected in (
        ("minecraft", lock["minecraft"]),
        ("protocol", lock["protocol"]),
        ("data_version", lock["data_version"]),
        ("source_archive_sha256", lock["source"]["archive_sha256"]),
        ("official_server_sha256", lock["runtime"]["server_sha256"]),
    ):
        if manifest.get(field) != expected:
            raise OracleError(f"wrong target/source lock field: {field}")
    stage = manifest.get("stage")
    if stage not in STAGES:
        raise OracleError(f"invalid or unreviewed noise stage: {stage!r}")
    method = manifest.get("method_body_sha256")
    if not isinstance(method, str) or re.fullmatch(r"[0-9a-f]{64}", method) is None:
        raise OracleError("missing exact source method fingerprint")
    if manifest.get("source_text_included") is not False:
        raise OracleError("source-rich material may not appear in vectors")
    if manifest.get("independent_var_sem_admitted") is not False:
        raise OracleError("independent_var_sem_admitted: vector evidence cannot assert admission")
    if manifest.get("production_worldgen_enabled") is not False:
        raise OracleError("production_worldgen_enabled: vector evidence cannot enable generation")
    vectors = manifest.get("vectors")
    if not isinstance(vectors, list) or not (16 <= len(vectors) <= 100_000):
        raise OracleError("expected between 16 and 100000 independent vector probes")
    result: dict[tuple[str, ...], str] = {}
    for index, item in enumerate(vectors):
        if not isinstance(item, dict) or set(item) != set(VECTOR_FIELDS):
            raise OracleError(f"vector {index} has missing or unexpected fields")
        fields = {
            key: _fixed_hex64(item[key], f"vector {index} {key}")
            for key in VECTOR_FIELDS
        }
        key = tuple(fields[name] for name in INPUT_FIELDS)
        if key in result:
            raise OracleError(f"duplicate input probe at vector {index}")
        result[key] = fields["value_bits"]
    seeds = {key[0] for key in result}
    if len(seeds) < 3:
        raise OracleError("insufficient seed diversity (at least 3)")
    # Include both signs and a fractional coordinate: exact raw IEEE-754
    # bits preserve -0.0 and NaN payloads; no Python float ever touches output.
    coordinates = [int(v, 16) for key in result for v in key[1:]]
    if not any(v == 0 for v in coordinates):
        raise OracleError("missing +0.0 coordinate")
    if not any(v == 0x8000000000000000 for v in coordinates):
        raise OracleError("missing -0.0 coordinate")
    if not any((v >> 63) != 0 and v != 0x8000000000000000 for v in coordinates):
        raise OracleError("missing negative coordinate")
    return result


def compare(reference: dict, candidate: dict, lock: dict) -> dict:
    old = validate(reference, lock, "official_26_2_noise_oracle_candidate")
    new = validate(candidate, lock, "helve_noise_candidate")
    for name in ("stage", "method_body_sha256"):
        if reference[name] != candidate[name]:
            raise OracleError(f"stage/method mismatch: {name}")
    if old.keys() != new.keys():
        raise OracleError(
            f"input coverage mismatch: reference={len(old)}, candidate={len(new)}"
        )
    mismatches = [(key, expected, new[key]) for key, expected in old.items() if new[key] != expected]
    if mismatches:
        key, expected, actual = mismatches[0]
        raise OracleError(
            f"{len(mismatches)} bit-pattern mismatches: first input={key}, "
            f"reference={expected}, helve={actual}"
        )
    return {
        "schema": 1,
        "stage": reference["stage"],
        "method_body_sha256": reference["method_body_sha256"],
        "matched_raw_bit_patterns": len(old),
        "bit_pattern_match": True,
        "official_source_review_admitted": False,
        "production_worldgen_enabled": False,
        "notice": "Source-free differential candidate only; not independent source/VAR/SEM proof",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=LOCK)
    args = parser.parse_args(argv)
    try:
        with args.lock.open("rb") as src:
            lock = tomllib.load(src)
        reference = json.loads(args.reference.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        print(json.dumps(compare(reference, candidate, lock), sort_keys=True))
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, OracleError) as exc:
        print(f"Worldgen raw-bit differential NOT QUALIFIED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
