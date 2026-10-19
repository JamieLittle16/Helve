#!/usr/bin/env python3
"""Capture source-locked official Minecraft Java 26.2 composed density candidates.

This only captures exact JVM DensityFunction.compute output bits; it never
reproduces Minecraft math. Exact 26.2 add/mul factory declarations are
CANDIDATES until a private, verified Atlas and official runtime approve them.
No source text, runtime bytecode, production permission or source/SEM approval
may be emitted to the repository.
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

KIND = "official_26_2_density_composition_candidate"
SOURCE = primitive.SOURCE
DB = primitive.DB
LOCK = primitive.LOCK
CACHE = primitive.CACHE
# Name/type candidates based on older public API, NEVER presumed true in 26.2.
COMPOSITION_METHODS = {
    "add_factory": (primitive.DENSITY, "add", ("DensityFunction", "DensityFunction")),
    "mul_factory": (primitive.DENSITY, "mul", ("DensityFunction", "DensityFunction")),
}
# Source-free representation of the *exact graph objects* created by the JVM.
# A shared instance is deliberately used for add_self.
PROFILES = {
    "add_gradients": ["add", "gradient_world_height", "gradient_reverse"],
    "mul_gradients": ["mul", "gradient_world_height", "gradient_reverse"],
    "add_zero_left": ["add", "constant_negative_zero", "gradient_world_height"],
    "add_zero_right": ["add", "gradient_world_height", "constant_negative_zero"],
    "mul_zero_left": ["mul", "constant_negative_zero", "gradient_world_height"],
    "mul_zero_right": ["mul", "gradient_world_height", "constant_negative_zero"],
    "add_self": ["add", "gradient_world_height", "gradient_world_height"],
    "mul_half": ["mul", "gradient_world_height", "constant_fraction"],
}
SAMPLE_COUNT = len(PROFILES) * len(primitive.SEEDS) * 32


class CompositionCaptureError(primitive.DensityCaptureError):
    """Unverified target version or malformed output."""


def inputs() -> list[dict[str, object]]:
    # The primitive's already observed coordinate grid, re-evaluated with
    # explicitly named composed functions; the seed is a LABEL, not RandomState.
    base = primitive.inputs()[:32]
    return [
        {"profile": name, "seed_bits": seed,
         "block_x": row["block_x"], "block_y": row["block_y"], "block_z": row["block_z"]}
        for name in PROFILES for seed in primitive.SEEDS for row in base
    ]


def bound_composition_methods(conn: sqlite3.Connection) -> dict[str, dict[str, str]]:
    rows = projection._exact_type_methods(conn, primitive.DENSITY, 128)
    result = {}
    for label, (owner, method, types) in COMPOSITION_METHODS.items():
        selected = [r for r in rows if primitive.matches_signature(r["signature"], method, types)]
        if len(selected) != 1:
            raise CompositionCaptureError(
                f"expected exactly one pinned 26.2 {owner}#{method}({', '.join(types)}) declaration; found {len(selected)}"
            )
        row = selected[0]
        record = source_probe.record_template(conn, row, "INDEX-WORLDGEN-26_2-" + label.upper())
        source = record.get("source")
        if not isinstance(source, dict) or source.get("type") != owner or source.get("signature") != row["signature"]:
            raise CompositionCaptureError(f"indexed source method identity mismatch: {label}")
        digests = (source.get("body_sha256"), source.get("normalized_sha256"))
        if any(not isinstance(d, str) or primitive.SHA.fullmatch(d) is None for d in digests):
            raise CompositionCaptureError(f"missing exact Atlas body fingerprints for {label}")
        result[label] = {
            "owner": owner, "signature": row["signature"],
            "body_sha256": digests[0], "normalized_sha256": digests[1],
        }
    return result


# Original, reflection-only transport. Minecraft's own factory and
# DensityFunction.compute implement ALL evaluation, optimization and ordering.
# Do not write (or assume) Minecraft's addition/multiplication algorithm here.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public final class HelveDensityCompositionBits {
  static double number(String bits) {
    if (!bits.matches("0x[0-9a-f]{16}")) throw new IllegalArgumentException("invalid 64-bit number");
    return Double.longBitsToDouble(Long.parseUnsignedLong(bits.substring(2), 16));
  }
  static Method exactStatic(Class<?> owner, String name, Class<?> result, Class<?>... args)
      throws Exception {
    Method method = owner.getMethod(name, args);
    if (!Modifier.isStatic(method.getModifiers()) || method.getReturnType() != result)
      throw new IllegalStateException("26.2 density method contract mismatch: " + name);
    return method;
  }
  public static void main(String[] ignored) throws Exception {
    // Same version detection/registry bootstrap used by the prior official
    // 26.2 state/primitive probes: loading DensityFunctions first is invalid.
    Class<?> shared = Class.forName("net.minecraft.SharedConstants");
    exactStatic(shared, "tryDetectVersion", void.class).invoke(null);
    Class<?> bootstrap = Class.forName("net.minecraft.server.Bootstrap");
    exactStatic(bootstrap, "bootStrap", void.class).invoke(null);
    Class<?> density = Class.forName("net.minecraft.world.level.levelgen.DensityFunction");
    Class<?> context = Class.forName("net.minecraft.world.level.levelgen.DensityFunction$FunctionContext");
    Class<?> single = Class.forName("net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext");
    Class<?> funcs = Class.forName("net.minecraft.world.level.levelgen.DensityFunctions");
    Method constant = exactStatic(funcs, "constant", density, double.class);
    Method gradient = exactStatic(funcs, "yClampedGradient", density,
        int.class, int.class, double.class, double.class);
    Method add = exactStatic(funcs, "add", density, density, density);
    Method mul = exactStatic(funcs, "mul", density, density, density);
    Method compute = density.getMethod("compute", context);
    Constructor<?> point = single.getDeclaredConstructor(int.class, int.class, int.class);
    point.setAccessible(true);
    if (compute.getReturnType() != double.class || !context.isAssignableFrom(single))
      throw new IllegalStateException("26.2 composition compute/context contract mismatch");

    Object zero = constant.invoke(null, number("0x8000000000000000"));
    Object half = constant.invoke(null, number("0x3fe0000000000000"));
    Object world = gradient.invoke(null, -64, 320,
        number("0xbff0000000000000"), number("0x3ff0000000000000"));
    Object reverse = gradient.invoke(null, -30, 17,
        number("0x3fe0000000000000"), number("0xbfe8000000000000"));
    Map<String,Object> profiles = new HashMap<>();
    profiles.put("add_gradients", add.invoke(null, world, reverse));
    profiles.put("mul_gradients", mul.invoke(null, world, reverse));
    profiles.put("add_zero_left", add.invoke(null, zero, world));
    profiles.put("add_zero_right", add.invoke(null, world, zero));
    profiles.put("mul_zero_left", mul.invoke(null, zero, world));
    profiles.put("mul_zero_right", mul.invoke(null, world, zero));
    profiles.put("add_self", add.invoke(null, world, world));
    profiles.put("mul_half", mul.invoke(null, world, half));

    BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.US_ASCII));
    int count = 0;
    for (String line; (line = input.readLine()) != null;) {
      String[] items = line.split("\t", -1);
      if (items.length != 5 || ++count > 2048 || !items[1].matches("0x[0-9a-f]{16}"))
        throw new IllegalArgumentException("unexpected official density input row");
      Object function = profiles.get(items[0]);
      if (function == null) throw new IllegalArgumentException("unknown composition profile");
      Object at = point.newInstance(Integer.parseInt(items[2]), Integer.parseInt(items[3]),
          Integer.parseInt(items[4]));
      double observed = (Double) compute.invoke(function, at);
      System.out.printf(Locale.ROOT, "%016x%n", Double.doubleToRawLongBits(observed));
    }
    if (count != 1280) throw new IllegalStateException("incomplete composed density probe");
  }
}
"""


def runtime_bits(server: Path, rows: list[dict[str, object]], *, timeout: int = 120) -> list[str]:
    if len(rows) != SAMPLE_COUNT:
        raise CompositionCaptureError("composition probe requires exactly 1280 requested contexts")
    with tempfile.TemporaryDirectory(prefix="helve-density-composed-262-") as folder:
        work = Path(folder)
        classpath = official.extract_classpath(server, work / "classpath")
        java = work / "HelveDensityCompositionBits.java"
        java.write_text(JAVA_PROBE, encoding="utf-8")
        compiler = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(java)],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if compiler.returncode:
            raise CompositionCaptureError("composed density probe compilation failed: " + compiler.stderr[:900])
        request = "\n".join(
            f"{r['profile']}\t{r['seed_bits']}\t{r['block_x']}\t{r['block_y']}\t{r['block_z']}"
            for r in rows
        ) + "\n"
        run = subprocess.run(
            ["java", "-Xmx512m", "-cp", os.pathsep.join([str(work), *(str(p) for p in classpath)]),
             "HelveDensityCompositionBits"],
            input=request, text=True, capture_output=True, check=False, timeout=timeout,
        )
        if run.returncode:
            raise CompositionCaptureError(
                "official 26.2 composition reflection rejected target candidate: " + run.stderr[:1600]
            )
        out = run.stdout.splitlines()
        if len(out) != SAMPLE_COUNT or any(re.fullmatch(r"[0-9a-f]{16}", s) is None for s in out):
            raise CompositionCaptureError("missing, excess or invalid exact raw-bit composition outputs")
        return ["0x" + s for s in out]


def validate_methods(methods: object, spec: dict[str, tuple[str, str, tuple[str, ...]]]) -> None:
    if not isinstance(methods, dict) or set(methods) != set(spec):
        raise CompositionCaptureError("missing, additional or substituted pinned source methods")
    for label, (owner, method, types) in spec.items():
        row = methods[label]
        if not isinstance(row, dict) or set(row) != {
            "owner", "signature", "body_sha256", "normalized_sha256"
        }:
            raise CompositionCaptureError(f"invalid pinned source identity: {label}")
        if row["owner"] != owner or not primitive.matches_signature(row["signature"], method, types):
            raise CompositionCaptureError(f"changed pinned source declaration: {label}")
        if any(not isinstance(row[k], str) or primitive.SHA.fullmatch(row[k]) is None
               for k in ("body_sha256", "normalized_sha256")):
            raise CompositionCaptureError(f"missing source fingerprint: {label}")
    if len({(r["owner"], r["signature"]) for r in methods.values()}) != len(spec):
        raise CompositionCaptureError("ambiguous pinned method identities")


def validate(manifest: dict, lock: dict) -> None:
    fields = {
        "schema", "kind", "minecraft", "protocol", "data_version", "stage",
        "source_archive_sha256", "official_server_sha256", "source_text_included",
        "runtime_startup_sequence", "independent_var_sem_admitted", "production_worldgen_enabled",
        "primitive_methods", "composition_methods", "profiles", "vectors",
    }
    if not isinstance(manifest, dict) or set(manifest) != fields:
        raise CompositionCaptureError("invalid composition manifest keys")
    required = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "stage": "composed_density",
        "source_archive_sha256": lock["source"]["archive_sha256"],
        "official_server_sha256": lock["runtime"]["server_sha256"],
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "runtime_startup_sequence": primitive.STARTUP_SEQUENCE,
        "profiles": PROFILES,
    }
    for key, want in required.items():
        if type(manifest[key]) is not type(want) or manifest[key] != want:
            raise CompositionCaptureError(f"invalid composition manifest field: {key}")
    validate_methods(manifest["primitive_methods"], primitive.METHODS)
    validate_methods(manifest["composition_methods"], COMPOSITION_METHODS)
    records = manifest["vectors"]
    expected = inputs()
    if not isinstance(records, list) or len(records) != SAMPLE_COUNT:
        raise CompositionCaptureError("wrong number of composed density records")
    for i, (observed, requested) in enumerate(zip(records, expected, strict=True)):
        if not isinstance(observed, dict) or set(observed) != {*requested, "value_bits"}:
            raise CompositionCaptureError(f"invalid density record keys at {i}")
        if any(type(observed[k]) is not type(v) or observed[k] != v for k, v in requested.items()):
            raise CompositionCaptureError(f"altered density input at {i}")
        if not isinstance(observed["value_bits"], str) or primitive.HEX.fullmatch(observed["value_bits"]) is None:
            raise CompositionCaptureError(f"invalid density raw bits at {i}")


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    dest = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise CompositionCaptureError("not pinned Minecraft Java 26.2")
    conn = vanilla_atlas.connect_db(db)
    try:
        source_digest = source_probe.require_pinned_source(conn, source, lock)
        primitive_methods = primitive.bound_methods(conn)
        composition_methods = bound_composition_methods(conn)
    finally:
        conn.close()
    runtime_digest = official.sha256_file(server)
    if runtime_digest != pin["runtime"]["server_sha256"]:
        raise CompositionCaptureError("unrecognized official 26.2 server runtime")
    records = inputs()
    observed = runtime_bits(server, records)
    manifest = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903, "stage": "composed_density",
        "source_archive_sha256": source_digest,
        "official_server_sha256": runtime_digest,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "runtime_startup_sequence": primitive.STARTUP_SEQUENCE,
        "primitive_methods": primitive_methods,
        "composition_methods": composition_methods,
        "profiles": PROFILES,
        "vectors": [dict(r, value_bits=b) for r, b in zip(records, observed, strict=True)],
    }
    validate(manifest, pin)
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(encoded)
    return {
        "output": str(dest), "rows": len(records),
        "file_sha256": hashlib.sha256(encoded).hexdigest(),
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--lock", type=Path, default=LOCK)
    parser.add_argument("--cache", type=Path, default=CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            resolved, _ = official.resolve("26.2", args.cache)
            server = resolved["server"][0]
        print(json.dumps(capture(source=args.source, db=args.db, lock=args.lock,
                                 server=server, output=args.output), sort_keys=True))
    except (CompositionCaptureError, primitive.DensityCaptureError, OSError, ValueError, TypeError, KeyError,
            sqlite3.Error, projection.DiscoveryError, source_probe.ProbeError,
            subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(f"OFFICIAL 26.2 COMPOSED DENSITY NOT CAPTURED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
