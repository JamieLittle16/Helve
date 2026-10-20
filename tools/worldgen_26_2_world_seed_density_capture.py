#!/usr/bin/env python3
"""Real stock-registry 26.2 world-seeded Noise.compute output oracle.

Uses the existing *actual JVM reflected* source-free RandomState shape
manifest, exact pinned local Atlas and official server runtime; then calls
RandomState.create(HolderGetter.Provider, OVERWORLD, seed) with the stock
VanillaRegistries.createLookup() provider, named registered Noises keys,
and the actual DensityFunctions$Noise.compute(FunctionContext) method.

This observes a bounded path. No source/VAR/SEM admission, Rust world-seed
construction, NoiseRouter final density or production publication follows.
If the stock registry cannot be obtained in the pinned official runtime,
the oracle FAILS CLOSED: never fall back to fabricated holders or settings.
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
import worldgen_26_2_density_primitive_capture as primitive
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_random_state_binding_frontier as binding

KIND = "official_26_2_stock_registered_world_seed_noise_density_oracle"
STAGE = "stock_registry_random_state_noise_compute_candidate_not_source_admitted"
FRONTIER_SHA256 = "1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7"
PREFIX = "HELVE26_2_WORLD_SEED_DENSITY|"
FAILURE_TAG = "HELVE26_2_WORLD_SEED_FAILURE|"
JAVA_SOURCE = Path(__file__).resolve().parent / "worldgen_java/HelveWorldSeededDensity262.java"
FRONTIER = Path("/tmp/helve-26_2-random-state-binding-frontier-01.json")
VANILLA_REGISTRIES = "net.minecraft.data.registries.VanillaRegistries"
NOISE_KEYS = ("TEMPERATURE", "CONTINENTALNESS", "EROSION")
PROFILES = {
    "unit": ["0x3ff0000000000000", "0x3ff0000000000000"],
    "quarter_xz": ["0x3fd0000000000000", "0x3ff0000000000000"],
    "quarter_xz_half_y": ["0x3fd0000000000000", "0x3fe0000000000000"],
}
SEEDS = tuple(primitive.SEEDS)
N_COORDS = 32
N_RECORDS = len(PROFILES) * len(SEEDS) * len(NOISE_KEYS) * N_COORDS
BITS = re.compile(r"0x[0-9a-f]{16}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
# Observed method hashes from the source-free, independently acquired
# RandomState frontier. These are identities, NOT source-law admissions.
SOURCE_PINS = {
    "random_state_create_provider": (
        "net.minecraft.world.level.levelgen.RandomState",
        "create", ("HolderGetter", "ResourceKey", "long"),
        "b9595526d577f99d4b569fa845748c75ad9cbf77c205b59027fe651f64bda77d"),
    "random_state_get_noise": (
        "net.minecraft.world.level.levelgen.RandomState",
        "getOrCreateNoise", ("ResourceKey",),
        "056547e13816f7c7dd9a3a82e1acadbbc7e5729da50b3103f28b6d20a115e7ca"),
    "noises_instantiate": (
        "net.minecraft.world.level.levelgen.Noises",
        "instantiate", ("HolderGetter", "PositionalRandomFactory", "ResourceKey"),
        "910d2ef48901972b27273b518c42b3e01bfd8944af650a519b567f64976c90aa"),
    "noise_holder_get_value": (
        "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder",
        "getValue", ("double", "double", "double"),
        "16b3035c3a03b2c0ae5765579640510ad52b92f3e7370b14bf3045b8f53ce782"),
    "density_noise_compute": (
        "net.minecraft.world.level.levelgen.DensityFunctions$Noise",
        "compute", ("FunctionContext",),
        "bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe"),
}


class WorldSeedNoiseError(ValueError):
    """Selected official world-seeded constructor/oracle remains unqualified."""


def input_rows() -> list[dict]:
    points = primitive.inputs()[:N_COORDS]
    return [
        {"profile": profile, "world_seed_bits": seed, "noise_key": key,
         "block_x": point["block_x"], "block_y": point["block_y"],
         "block_z": point["block_z"]}
        for profile in PROFILES for seed in SEEDS
        for key in NOISE_KEYS for point in points
    ]


def reference_frontier(path: Path, pin: dict) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FRONTIER_SHA256 or len(raw) > 100_000:
        raise WorldSeedNoiseError("input RandomState source-free evidence SHA changed")
    try:
        reference = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise WorldSeedNoiseError("invalid pinned shape frontier") from exc
    binding.validate(reference, pin)
    # The proven shape is the actual 26.2 stock registry/seed API input;
    # a rebuilt frontier that swaps one overload must not be accepted.
    runtime = reference["runtime_reflection"]
    random = runtime["net.minecraft.world.level.levelgen.RandomState"]["members"]
    if not any(m["kind"] == "METHOD" and m["name"] == "create"
               and m["linkage"] == "static" and
               m["erased_args"] == (
                   "net.minecraft.core.HolderGetter$Provider,"
                   "net.minecraft.resources.ResourceKey,long")
               for m in random):
        raise WorldSeedNoiseError("official Provider/worldSeed overload absent")
    noise = runtime["net.minecraft.world.level.levelgen.Noises"]["members"]
    for key in NOISE_KEYS:
        if not any(m["kind"] == "FIELD" and m["name"] == key and
                   m["return_or_type"] == "net.minecraft.resources.ResourceKey"
                   for m in noise):
            raise WorldSeedNoiseError("unregistered noise ResourceKey declaration: " + key)
    return reference


def source_methods(reference: dict, conn: sqlite3.Connection) -> dict:
    result = {}
    for label, (owner, method, types, fingerprint) in SOURCE_PINS.items():
        matches = [
            value
            for value in reference["source_atlas"][owner]["methods"]
            if binding.match_args(value["signature"], method, types)
        ]
        if len(matches) != 1 or matches[0]["body_sha256"] != fingerprint:
            raise WorldSeedNoiseError("source-locked seed/Noise.compute fingerprint mismatch: " + label)
        value = matches[0]
        result[label] = {
            "owner": owner, "signature": value["signature"],
            "body_sha256": fingerprint,
            "normalized_sha256": value["normalized_sha256"],
        }
    # The runtime-builtin lookup is the only NEW source root, so pin its
    # exact private Atlas identity at capture time, without assuming its body.
    rows = projection._exact_type_methods(conn, VANILLA_REGISTRIES, 128)
    matches = [row for row in rows if row["name"] == "createLookup"
               and binding.match_args(str(row["signature"]), "createLookup", ())]
    if len(matches) != 1:
        raise WorldSeedNoiseError("26.2 stock VanillaRegistries.createLookup source not unique")
    rec = source_probe.record_template(conn, matches[0],
                                      "INDEX-WORLDGEN-262-STOCK-REGISTRY-LOOKUP")
    evidence = rec["source"]
    if (evidence["type"] != VANILLA_REGISTRIES or
        evidence["signature"] != str(matches[0]["signature"])):
        raise WorldSeedNoiseError("Atlas source owner mismatch for stock lookup")
    for key in ("body_sha256", "normalized_sha256"):
        if not isinstance(evidence[key], str) or SHA.fullmatch(evidence[key]) is None:
            raise WorldSeedNoiseError("incomplete official stock registry source fingerprint")
    result["stock_vanilla_lookup"] = {
        "owner": VANILLA_REGISTRIES, "signature": evidence["signature"],
        "body_sha256": evidence["body_sha256"],
        "normalized_sha256": evidence["normalized_sha256"],
    }
    return result


def parse_bits(stdout: str, expected: int = N_RECORDS) -> list[str]:
    if len(stdout.encode("utf-8")) > 256_000 or len(stdout.splitlines()) > 4096:
        raise WorldSeedNoiseError("unbounded official world-seed JVM output")
    lines = [line for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(lines) != expected:
        raise WorldSeedNoiseError(
            f"actual JVM emitted {len(lines)} world-seed raw-bit rows, expected {expected}")
    values = []
    for index, line in enumerate(lines):
        chunks = line.split("|")
        if len(chunks) != 3 or chunks[0] != PREFIX[:-1] or chunks[1] != str(index) \
            or re.fullmatch("[0-9a-f]{16}", chunks[2]) is None:
            raise WorldSeedNoiseError("world-seed JVM row order or IEEE bits changed: " + str(index))
        values.append("0x" + chunks[2])
    return values


def java_probe_failure(stdout: str) -> str | None:
    """Read a single explicit JVM error through the original stdout FD.

    Minecraft startup can redirect BOTH Java stdout/stderr or install a
    handler which prints only 'Exception in thread "main"'. The original
    Java bridge now catches Throwable and emits this tagged, bounded row
    without trusting Java's default uncaught-exception printer. No success
    or admission can be inferred from a failure tag.
    """
    if not isinstance(stdout, str) or len(stdout.encode("utf-8")) > 256_000:
        raise WorldSeedNoiseError("invalid size for JVM probe output")
    found = [line for line in stdout.splitlines() if line.startswith(FAILURE_TAG)]
    if not found:
        return None
    if len(found) != 1:
        raise WorldSeedNoiseError("duplicate official JVM error records")
    cells = found[0].split("|")
    if len(cells) != 5 or cells[0] != FAILURE_TAG[:-1]:
        raise WorldSeedNoiseError("malformed official JVM error record")
    _, phase, deepest, outer, message = cells
    if (not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", phase)
        or not re.fullmatch(r"[A-Za-z0-9.$_]{1,160}", deepest)
        or not re.fullmatch(r"[A-Za-z0-9.$_]{1,160}", outer)
        or not 1 <= len(message) <= 700
        or any(ord(char) < 32 or ord(char) > 126 for char in message)):
        raise WorldSeedNoiseError("invalid official JVM diagnostic fields")
    return f"JVM PHASE: {phase} | ROOT CAUSE: {deepest}: {message} | OUTER: {outer}"


def java_failure_detail(stderr: str, *, limit: int = 6000) -> str:
    """Put the deepest JVM cause on ONE line; retain bounded stack frames.

    The previous fix removed the JOML Unsafe warning preface, but terminal
    copying may still stop at the first newline after "Exception in thread".
    A stable first-line root cause must survive both JVM warnings and clipped
    multi-line terminal output. This is diagnostics only; it cannot authorise
    the world-seed registry path.
    """
    if not isinstance(stderr, str):
        raise WorldSeedNoiseError("non-text JVM failure output")
    marker = stderr.find('Exception in thread ')
    if marker >= 0:
        detail = stderr[marker:].strip()
    else:
        detail = stderr.strip()[-limit:]
    if not detail:
        return "JVM ROOT CAUSE: non-zero JVM exit without a stderr exception"

    lines = detail.splitlines()
    initial = lines[0].strip()
    causes = [line.strip()[len("Caused by: "):].strip()
              for line in lines if line.strip().startswith("Caused by: ")]
    root = causes[-1] if causes else initial
    # Compact single-line root cause is intentionally emitted FIRST, before
    # any frames. Always reject control characters and unbounded diagnostics.
    short_root = " ".join(root.split())[:700]
    short_initial = " ".join(initial.split())[:700]
    summary = "JVM ROOT CAUSE: " + short_root
    if causes and short_initial != short_root:
        summary += " | TOP EXCEPTION: " + short_initial
    if len(summary) >= limit:
        return summary[:limit]
    available = limit - len(summary) - 1
    if len(detail) > available:
        omitted = "\n... [intermediate JVM frames omitted] ...\n"
        first_size = min(1600, (available - len(omitted)) // 2)
        last_size = available - len(omitted) - first_size
        detail = detail[:first_size] + omitted + detail[-last_size:]
    return summary + "\n" + detail


def oracle(server: Path, points: list[dict], *, timeout: int = 180) -> list[str]:
    if len(points) != N_RECORDS or points != input_rows():
        raise WorldSeedNoiseError("actual world-seed probe request changed shape or order")
    if not JAVA_SOURCE.is_file():
        raise WorldSeedNoiseError("original stock registry JVM bridge unavailable")
    with tempfile.TemporaryDirectory(prefix="helve-worldseed-density-26_2-") as scratch:
        work = Path(scratch)
        cp = official.extract_classpath(server, work / "classpath")
        javac = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(JAVA_SOURCE)],
            text=True, capture_output=True, check=False, timeout=timeout)
        if javac.returncode:
            raise WorldSeedNoiseError("original world-seed probe compilation failed: "
                                      + javac.stderr[:1500])
        rows = "\n".join(
            f"{row['profile']}\t{row['world_seed_bits']}\t{row['noise_key']}\t"
            f"{row['block_x']}\t{row['block_y']}\t{row['block_z']}"
            for row in points
        ) + "\n"
        run = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join([str(work), *(str(part) for part in cp)]),
             "HelveWorldSeededDensity262"],
            input=rows, text=True, capture_output=True, check=False, timeout=timeout)
        failure = java_probe_failure(run.stdout)
        if failure is not None:
            raise WorldSeedNoiseError("real stock-registry 26.2 world-seed JVM path "
                                      "is NOT VERIFIED: " + failure)
        if run.returncode:
            raise WorldSeedNoiseError("real stock-registry 26.2 world-seed JVM path "
                                      "is NOT VERIFIED (no tagged Java error): "
                                      + java_failure_detail(run.stderr))
        return parse_bits(run.stdout)


def validate(manifest: dict, pin: dict, reference: dict) -> None:
    required = {
        "schema", "kind", "stage", "minecraft", "protocol", "data_version",
        "source_archive_sha256", "official_server_sha256", "frontier_sha256",
        "source_methods", "profiles", "world_seeds", "noise_keys", "vectors",
        "world_seed_random_state_observed", "stock_registry_used",
        "world_seed_random_state_bound", "source_text_included",
        "independent_var_sem_admitted", "production_worldgen_enabled",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise WorldSeedNoiseError("worldseed density JSON schema mismatch")
    fixed = {
        "schema": 1, "kind": KIND, "stage": STAGE, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": pin["source"]["archive_sha256"],
        "official_server_sha256": pin["runtime"]["server_sha256"],
        "frontier_sha256": FRONTIER_SHA256, "profiles": PROFILES,
        "world_seeds": list(SEEDS), "noise_keys": list(NOISE_KEYS),
        "world_seed_random_state_observed": True, "stock_registry_used": True,
        "world_seed_random_state_bound": False,
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    for key, expected in fixed.items():
        if type(manifest.get(key)) is not type(expected) or manifest[key] != expected:
            raise WorldSeedNoiseError("wrong pinned worldseed source or status field: " + key)
    methods = manifest["source_methods"]
    if not isinstance(methods, dict) or set(methods) != set(SOURCE_PINS) | {"stock_vanilla_lookup"}:
        raise WorldSeedNoiseError("missing worldseed source method identity")
    for label, (owner, method, types, fingerprint) in SOURCE_PINS.items():
        got = methods[label]
        reference_matches = [
            v for v in reference["source_atlas"][owner]["methods"]
            if binding.match_args(v["signature"], method, types)
        ]
        if len(reference_matches) != 1 or not isinstance(got, dict) \
            or set(got) != {"owner", "signature", "body_sha256", "normalized_sha256"} \
            or got["owner"] != owner or got["signature"] != reference_matches[0]["signature"] \
            or got["body_sha256"] != fingerprint \
            or got["normalized_sha256"] != reference_matches[0]["normalized_sha256"]:
            raise WorldSeedNoiseError("incorrect RandomState Atlas source identity: " + label)
    looked_up = methods["stock_vanilla_lookup"]
    if not isinstance(looked_up, dict) \
        or set(looked_up) != {"owner", "signature", "body_sha256", "normalized_sha256"} \
        or looked_up["owner"] != VANILLA_REGISTRIES \
        or not binding.match_args(looked_up["signature"], "createLookup", ()) \
        or any(not isinstance(looked_up[k], str) or SHA.fullmatch(looked_up[k]) is None
               for k in ("body_sha256", "normalized_sha256")):
        raise WorldSeedNoiseError("unbound stock registry source declaration")
    desired = input_rows()
    vectors = manifest["vectors"]
    if not isinstance(vectors, list) or len(vectors) != len(desired):
        raise WorldSeedNoiseError("incomplete official worldseed numeric vectors")
    for index, (want, actual) in enumerate(zip(desired, vectors, strict=True)):
        if not isinstance(actual, dict) or set(actual) != {*want, "value_bits"} \
            or any(type(actual[k]) is not type(v) or actual[k] != v for k, v in want.items()) \
            or not isinstance(actual["value_bits"], str) or BITS.fullmatch(actual["value_bits"]) is None:
            raise WorldSeedNoiseError("worldseed record shape or order changed: " + str(index))


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as reader:
        pin = tomllib.load(reader)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise WorldSeedNoiseError("wrong locked official Minecraft target")
    reference = reference_frontier(frontier, pin)
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        source_pins = source_methods(reference, conn)
    finally:
        conn.close()
    server_sha = official.sha256_file(server)
    if server_sha != pin["runtime"]["server_sha256"]:
        raise WorldSeedNoiseError("not the pinned official Minecraft server jar")
    requested = input_rows()
    bits = oracle(server, requested)
    report = {
        "schema": 1, "kind": KIND, "stage": STAGE, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha, "frontier_sha256": FRONTIER_SHA256,
        "source_methods": source_pins, "profiles": PROFILES,
        "world_seeds": list(SEEDS), "noise_keys": list(NOISE_KEYS),
        "world_seed_random_state_observed": True, "stock_registry_used": True,
        "world_seed_random_state_bound": False,
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "vectors": [dict(row, value_bits=value)
                    for row, value in zip(requested, bits, strict=True)],
    }
    validate(report, pin, reference)
    data = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as writer:
        writer.write(data)
    return {
        "output": str(destination), "vectors": N_RECORDS,
        "source_free_sha256": hashlib.sha256(data).hexdigest(),
        "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=primitive.DB)
    parser.add_argument("--lock", type=Path, default=primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=primitive.CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--frontier", type=Path, default=FRONTIER)
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args(argv)
    try:
        server = opts.server_jar
        if server is None:
            resolved, _ = official.resolve("26.2", opts.cache)
            server = resolved["server"][0]
        print(json.dumps(capture(source=opts.source, db=opts.db, lock=opts.lock,
            server=server, frontier=opts.frontier, output=opts.output), sort_keys=True))
    except (WorldSeedNoiseError, ValueError, OSError, TypeError, KeyError,
            sqlite3.Error, source_probe.ProbeError, projection.DiscoveryError,
            subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print("OFFICIAL 26.2 STOCK-REGISTRY WORLD-SEED DENSITY NOT QUALIFIED: "
              + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
