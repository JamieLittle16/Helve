#!/usr/bin/env python3
"""Single 1,920-vector source-pinned stock 26.2 mixed density JVM capture.

Stock VanillaRegistries -> RandomState -> getOrCreateNoise produces a real
registered Noise density leaf, then original DensityFunctions.add/mul combines
it with real YClampedGradient or Constant. Actual compute and delegate classes
are observed by reflection; no Mojang math is copied, interpreted or inferred.
This is output evidence ONLY; VAR/SEM and production admission remain CLOSED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
from pathlib import Path

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_26_2_density_composition_capture as composed
import worldgen_26_2_density_primitive_capture as primitive
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_stock_worldseed_heldout_capture as heldout
import worldgen_26_2_stock_worldseed_heldout_fixture as heldout_fixture
import worldgen_26_2_world_seed_density_capture as stock

KIND = "official_26_2_stock_worldseed_mixed_density_1920"
COUNT = 1920
PROFILES = (
    "add_noise_gradient", "add_gradient_noise",
    "mul_noise_gradient", "mul_gradient_noise",
    "add_noise_negative_zero", "add_negative_zero_noise",
    "mul_noise_negative_zero", "mul_negative_zero_noise",
    "mul_noise_half", "mul_half_noise",
)
SEEDS = heldout.SEEDS
KEYS = stock.NOISE_KEYS
# New Y=128 is crucial: primitive world-height gradient is precisely positive
# zero there, which distinguished official Ap2 from eager IEEE in PR #433.
POINTS = (
    (0, 128, 0), (1, 127, -1), (-1, 129, 1),
    (33_554_431, -63, -33_554_432),
    (-33_554_431, 320, 33_554_431),
    (2_147_483_600, 255, -2_147_483_600),
    (-2_147_483_600, -4096, 2_147_483_600),
    (105, -65, -417), (-1_000_000, 2048, 1_000_000),
    (123_456, -128, -654_321), (-16, 0, 16), (15, 256, -15),
    (33_554_433, 321, -33_554_433),
    (-33_554_433, -31, 33_554_433),
    (2048, 63, -2048), (-2049, 64, 2049),
)
assert len(PROFILES) * len(SEEDS) * len(KEYS) * len(POINTS) == COUNT
ROOT = Path(__file__).resolve().parents[1]
JAVA_SOURCE = ROOT / "tools/worldgen_java/HelveStockMixedDensity262.java"
ORIGINAL_BRIDGE = stock.JAVA_SOURCE
BIT_PREFIX = "HELVE26_2_STOCK_MIXED_BITS|"
DELEGATE_PREFIX = "HELVE26_2_STOCK_MIXED_DELEGATE|"
FAILURE_PREFIX = "HELVE26_2_STOCK_MIXED_FAILURE|"
JAVA_CLASS = re.compile(r"(?:net\.minecraft|java\.lang)(?:\.[A-Za-z_$][\w$]*)+\Z")
BIT_WORD = re.compile(r"[0-9a-f]{16}\Z")
METHOD_BODY_PINS = {
    "add_factory": "aff60df9dc11f0e52d061660cf39684dfd671e214ab185174a293ce96ddebe58",
    "mul_factory": "c5d5aaa53f8650d9068362c193487625eeeb057633eaafb0142651a4cc29d7f1",
}


class MixedDensityCaptureError(ValueError):
    """A bounded official mixed composition capture could not be qualified."""


def inputs() -> list[dict]:
    return [
        {"profile": profile, "world_seed_bits": seed, "noise_key": key,
         "block_x": x, "block_y": y, "block_z": z}
        for profile in PROFILES for seed in SEEDS for key in KEYS
        for x, y, z in POINTS
    ]


def source_method_inventory(reference: dict, conn: sqlite3.Connection) -> dict:
    stock_methods = stock.source_methods(reference, conn)
    primitive_methods = primitive.bound_methods(conn)
    composition_methods = composed.bound_composition_methods(conn)
    for label, expected_sha in METHOD_BODY_PINS.items():
        if composition_methods[label]["body_sha256"] != expected_sha:
            raise MixedDensityCaptureError("original 26.2 composed factory source changed: " + label)
    return {
        "worldseed_noise": stock_methods,
        "density_primitives": primitive_methods,
        "composition_factories": composition_methods,
    }


def parse_output(output: str) -> tuple[list[str], dict]:
    if not isinstance(output, str) or len(output) > 600_000:
        raise MixedDensityCaptureError("unbounded mixed stock JVM stdout")
    results = []
    delegates = {}
    failures = []
    for raw in output.splitlines():
        if raw.startswith(FAILURE_PREFIX):
            failures.append(raw)
        elif raw.startswith(BIT_PREFIX):
            result = raw.split("|")
            if len(result) != 3 or result[1] != str(len(results)) \
               or BIT_WORD.fullmatch(result[2]) is None:
                raise MixedDensityCaptureError("malformed, duplicate or reordered raw JVM output at " + str(len(results)))
            results.append("0x" + result[2])
            if len(results) > COUNT:
                raise MixedDensityCaptureError("unexpected extra official mixed density output")
        elif raw.startswith(DELEGATE_PREFIX):
            record = raw.split("|")
            if len(record) != 5 or record[1] not in PROFILES or record[1] in delegates:
                raise MixedDensityCaptureError("duplicate or unapproved mixed compute delegate")
            implementation, compute, parent = record[2:]
            if not JAVA_CLASS.fullmatch(implementation) or not JAVA_CLASS.fullmatch(compute) \
               or (parent != "-" and not JAVA_CLASS.fullmatch(parent)):
                raise MixedDensityCaptureError("mixed delegate class/package is not source-grounded")
            delegates[record[1]] = {
                "implementation_class": implementation,
                "compute_declaring_class": compute,
                "superclass": parent,
            }
    if failures:
        if len(failures) != 1:
            raise MixedDensityCaptureError("multiple official JVM failures")
        parts = failures[0].split("|")
        if len(parts) != 5 or any(not part or len(part) > 510 or
                                 re.search(r"[^\x20-\x7e]", part) for part in parts):
            raise MixedDensityCaptureError("malformed tagged official JVM failure")
        raise MixedDensityCaptureError(
            "JVM PHASE: " + parts[1] + "; ROOT CAUSE: " + parts[2] + ": " + parts[4]
        )
    if len(results) != COUNT or list(delegates) != list(PROFILES):
        raise MixedDensityCaptureError(
            f"incomplete official JVM observations: {len(results)}/{COUNT} values, "
            f"{len(delegates)}/{len(PROFILES)} ordered delegates"
        )
    return results, delegates


def observe(server: Path, rows: list[dict], *, timeout: int = 240) -> tuple[list[str], dict]:
    if rows != inputs() or len(rows) != COUNT:
        raise MixedDensityCaptureError("mixed stock JVM request set changed")
    if not JAVA_SOURCE.is_file() or not ORIGINAL_BRIDGE.is_file():
        raise MixedDensityCaptureError("pinned original source-free reflection bridges missing")
    with tempfile.TemporaryDirectory(prefix="helve-262-stock-mixed-") as folder:
        work = Path(folder)
        jars = official.extract_classpath(server, work / "classpath")
        compile_result = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             str(ORIGINAL_BRIDGE), str(JAVA_SOURCE)],
            capture_output=True, text=True, check=False, timeout=timeout,
        )
        if compile_result.returncode:
            raise MixedDensityCaptureError("reflection-only Java mixed bridge did not compile: " +
                                           compile_result.stderr[:1500])
        text_rows = "\n".join(
            f"{r['profile']}\t{r['world_seed_bits']}\t{r['noise_key']}\t"
            f"{r['block_x']}\t{r['block_y']}\t{r['block_z']}" for r in rows
        ) + "\n"
        sample = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join([str(work), *(str(j) for j in jars)]),
             "HelveStockMixedDensity262", "--mixed-1920"],
            input=text_rows, capture_output=True, text=True, check=False, timeout=timeout,
        )
        if sample.returncode:
            try:
                parse_output(sample.stdout)
            except MixedDensityCaptureError as problem:
                raise MixedDensityCaptureError(str(problem)) from problem
            raise MixedDensityCaptureError(
                "official mixed stock JVM terminated unsuccessfully: " +
                stock.java_failure_detail(sample.stderr)
            )
        return parse_output(sample.stdout)


def validate(manifest: dict, *, source_sha: str, server_sha: str, methods: dict,
             delegates: dict) -> None:
    expected = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "original_stock_fixture_sha256": frozen.FIXTURE_SHA256,
        "heldout_stock_fixture_sha256": heldout_fixture.FIXTURE_SHA256,
        "source_methods": methods,
        "delegates": delegates,
        "profiles": list(PROFILES),
        "world_seeds": list(SEEDS),
        "noise_keys": list(KEYS),
        "points": [list(point) for point in POINTS],
        "xz_scale_bits": "0x3fd0000000000000",
        "y_scale_bits": "0x3fe0000000000000",
        "stock_registry_used": True,
        "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    if not isinstance(manifest, dict) or set(manifest) != set(expected) | {"vectors"}:
        raise MixedDensityCaptureError("unsupported mixed density manifest schema")
    for label, value in expected.items():
        if type(manifest.get(label)) is not type(value) or manifest[label] != value:
            raise MixedDensityCaptureError("wrong pinned mixed density target / gate: " + label)
    entries = manifest["vectors"]
    rows = inputs()
    if not isinstance(entries, list) or len(entries) != COUNT:
        raise MixedDensityCaptureError("exactly 1,920 mixed raw-bit records required")
    for index, (row, recorded) in enumerate(zip(rows, entries, strict=True)):
        if type(recorded) is not dict or set(recorded) != set(row) | {"value_bits"} \
           or any(type(recorded.get(k)) is not type(v) or recorded[k] != v for k, v in row.items()) \
           or not isinstance(recorded.get("value_bits"), str) \
           or not re.fullmatch(r"0x[0-9a-f]{16}", recorded["value_bits"]):
            raise MixedDensityCaptureError("invalid or reordered original JVM vector " + str(index))


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as file:
        pin = tomllib.load(file)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise MixedDensityCaptureError("not the locked Minecraft 26.2")
    reference = stock.reference_frontier(frontier, pin)
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        methods = source_method_inventory(reference, conn)
    finally:
        conn.close()
    server_sha = official.sha256_file(server)
    if source_sha != frozen.SOURCE_SHA256 or server_sha != frozen.SERVER_SHA256 \
       or server_sha != pin["runtime"]["server_sha256"]:
        raise MixedDensityCaptureError("official 26.2 runtime/source changed")
    values, delegates = observe(server, inputs())
    result = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha, "official_server_sha256": server_sha,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "original_stock_fixture_sha256": frozen.FIXTURE_SHA256,
        "heldout_stock_fixture_sha256": heldout_fixture.FIXTURE_SHA256,
        "source_methods": methods, "delegates": delegates,
        "profiles": list(PROFILES), "world_seeds": list(SEEDS),
        "noise_keys": list(KEYS), "points": [list(point) for point in POINTS],
        "xz_scale_bits": "0x3fd0000000000000",
        "y_scale_bits": "0x3fe0000000000000",
        "stock_registry_used": True, "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False, "source_text_included": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
        "vectors": [dict(row, value_bits=bits) for row, bits in zip(inputs(), values, strict=True)],
    }
    validate(result, source_sha=source_sha, server_sha=server_sha,
             methods=methods, delegates=delegates)
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as file:
        file.write(payload)
    return {
        "output": str(destination), "vectors": COUNT,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "independent_official_jvm_mixed_composition_observed": True,
        "rust_mixed_semantics_qualified": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=primitive.DB)
    parser.add_argument("--lock", type=Path, default=primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=primitive.CACHE)
    parser.add_argument("--server-jar", type=Path, default=None)
    parser.add_argument("--frontier", type=Path, default=stock.FRONTIER)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            metadata, _ = official.resolve("26.2", args.cache)
            server = metadata["server"][0]
        print(json.dumps(capture(source=args.source, db=args.db, lock=args.lock,
                                 server=server, frontier=args.frontier, output=args.output),
                         sort_keys=True))
    except (MixedDensityCaptureError, OSError, ValueError, KeyError, TypeError,
            sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print("OFFICIAL STOCK MIXED DENSITY UNQUALIFIED: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
