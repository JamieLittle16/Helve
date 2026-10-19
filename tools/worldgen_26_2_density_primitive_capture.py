#!/usr/bin/env python3
"""Capture PINNED official Java 26.2 primitive density outputs, source-free.

This is the first *real density-function* reference frontier, NOT a port or a
VAR/SEM approval. Public 26.2 runtime signatures and pinned Atlas body hashes
MUST agree; any missing method, shape, version, context or record fails closed.
The original Java reflection bridge contains no Mojang source or algorithms.
No production world/chunk/publication path is touched.
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
import worldgen_26_2_improved_noise_capture as improved

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vanilla/vanilla.lock.toml"
SOURCE = Path.home() / "Documents/mc-source/mc-src.zip"
DB = ROOT / ".crucible/vanilla/atlas.sqlite"
CACHE = ROOT / ".crucible/vanilla/downloads"
DENSITY = "net.minecraft.world.level.levelgen.DensityFunctions"
CONTEXT = "net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext"
SINGLE = "net.minecraft.world.level.levelgen.DensityFunction$FunctionContext"
CONSTANT = DENSITY + "$Constant"
GRADIENT = DENSITY + "$YClampedGradient"
KIND = "official_26_2_density_primitive_candidate"
HEX = re.compile(r"0x[0-9a-f]{16}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
SEEDS = (
    "0x0000000000000000", "0x0000000000000001",
    "0xffffffffffffffff", "0x8000000000000000",
    "0x9e3779b97f4a7c15",
)
# Parameter bits are exact; no JSON floating numbers or host rounding.
PROFILES = {
    "constant_negative_zero": {
        "factory": "constant",
        "args": ["0x8000000000000000"],
    },
    "constant_fraction": {
        "factory": "constant",
        "args": ["0x3fe0000000000000"],
    },
    "gradient_world_height": {
        "factory": "yClampedGradient",
        "args": [-64, 320, "0xbff0000000000000", "0x3ff0000000000000"],
    },
    "gradient_reverse": {
        "factory": "yClampedGradient",
        "args": [-30, 17, "0x3fe0000000000000", "0xbfe8000000000000"],
    },
}
# Match only the method's symbol and argument type family; its exact body
# SHA is read from the *private verified Atlas* rather than invented here.
METHODS = {
    "constant_factory": (DENSITY, "constant", ("double",)),
    "gradient_factory": (DENSITY, "yClampedGradient", ("int", "int", "double", "double")),
    "constant_compute": (CONSTANT, "compute", ("FunctionContext",)),
    "gradient_compute": (GRADIENT, "compute", ("FunctionContext",)),
}


class DensityCaptureError(ValueError):
    """Wrong source lock, runtime, methods, profile, context or output."""


def inputs() -> list[dict[str, object]]:
    # 32 deterministic integer contexts per seed. Vertical thresholds and
    # clamping boundaries are deliberately present, including negative Y.
    ys = [-4096, -65, -64, -63, -31, -30, -29, -1,
          0, 1, 15, 16, 17, 18, 63, 64,
          127, 128, 255, 256, 318, 319, 320, 321,
          1024, -1024, -384, -320, 319, -64, 17, 320]
    coords = []
    for i, y in enumerate(ys):
        x = (-33_554_432 if i & 1 else 33_554_432) + i * 13
        z = (-(i * 17) if i % 3 else i * 17) - 16
        coords.append((x, y, z))
    return [
        {"profile": name, "seed_bits": seed, "block_x": x,
         "block_y": y, "block_z": z}
        for name in PROFILES for seed in SEEDS for (x, y, z) in coords
    ]


def bound_methods(conn: sqlite3.Connection) -> dict[str, dict[str, str]]:
    result = {}
    owners = {owner for owner, _, _ in METHODS.values()}
    methods_by_owner = {
        owner: projection._exact_type_methods(conn, owner, 128)
        for owner in owners
    }
    for label, (owner, name, arg_types) in METHODS.items():
        matches = []
        for row in methods_by_owner[owner]:
            signature = str(row["signature"])
            if not signature.startswith(name + "(") or not signature.endswith(")"):
                continue
            arguments = signature[len(name) + 1:-1]
            parts = [] if not arguments.strip() else arguments.split(",")
            if len(parts) != len(arg_types):
                continue
            if all(re.search(r"\b" + re.escape(t) + r"\b", part) for t, part in zip(arg_types, parts)):
                matches.append(row)
        if len(matches) != 1:
            raise DensityCaptureError(f"expected exactly one pinned {owner}#{name} declaration; found {len(matches)}")
        row = matches[0]
        record = source_probe.record_template(conn, row, "INDEX-WORLDGEN-26_2-" + label.upper())
        source = record.get("source")
        if not isinstance(source, dict) or source.get("type") != owner or source.get("signature") != row["signature"]:
            raise DensityCaptureError(f"indexed method identity mismatch: {label}")
        digest = source.get("body_sha256")
        normalized = source.get("normalized_sha256")
        if not isinstance(digest, str) or not SHA.fullmatch(digest) or not isinstance(normalized, str) or not SHA.fullmatch(normalized):
            raise DensityCaptureError(f"no exact source body/normalized fingerprints for {label}")
        result[label] = {
            "owner": owner,
            "signature": str(row["signature"]),
            "body_sha256": digest,
            "normalized_sha256": normalized,
        }
    if len({(x["owner"], x["signature"]) for x in result.values()}) != len(METHODS):
        raise DensityCaptureError("duplicate or ambiguous source methods")
    return result


# Small original reflection-only bridge: it delegates all math to the
# UNMODIFIED official JVM; never computes the density formula itself.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public final class HelveDensityPrimitiveBits {
  static double value(String bits) {
    if (!bits.matches("0x[0-9a-f]{16}")) throw new IllegalArgumentException("bad f64 bits");
    return Double.longBitsToDouble(Long.parseUnsignedLong(bits.substring(2), 16));
  }
  public static void main(String[] ignored) throws Exception {
    Class<?> functions = Class.forName("net.minecraft.world.level.levelgen.DensityFunctions");
    Class<?> density = Class.forName("net.minecraft.world.level.levelgen.DensityFunction");
    Class<?> context = Class.forName("net.minecraft.world.level.levelgen.DensityFunction$FunctionContext");
    Class<?> single = Class.forName("net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext");
    Method constant = functions.getMethod("constant", double.class);
    Method gradient = functions.getMethod("yClampedGradient",
        int.class, int.class, double.class, double.class);
    Method compute = density.getMethod("compute", context);
    Constructor<?> point = single.getDeclaredConstructor(int.class, int.class, int.class);
    point.setAccessible(true);
    if (!Modifier.isStatic(constant.getModifiers()) || !Modifier.isStatic(gradient.getModifiers())
        || constant.getReturnType()!=density || gradient.getReturnType()!=density
        || compute.getReturnType()!=double.class || !context.isAssignableFrom(single)) {
      throw new IllegalStateException("26.2 density primitive reflection contract disagrees");
    }
    Map<String,Object> instances = new HashMap<>();
    instances.put("constant_negative_zero", constant.invoke(null, value("0x8000000000000000")));
    instances.put("constant_fraction", constant.invoke(null, value("0x3fe0000000000000")));
    instances.put("gradient_world_height", gradient.invoke(null, -64, 320,
        value("0xbff0000000000000"), value("0x3ff0000000000000")));
    instances.put("gradient_reverse", gradient.invoke(null, -30, 17,
        value("0x3fe0000000000000"), value("0xbfe8000000000000")));
    BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.US_ASCII));
    int count=0;
    for (String line; (line=input.readLine())!=null;) {
      String[] cells=line.split("\t",-1);
      if (cells.length!=5 || ++count>4096 || !cells[1].matches("0x[0-9a-f]{16}"))
        throw new IllegalArgumentException("invalid density input row");
      Object function=instances.get(cells[0]);
      if (function==null) throw new IllegalArgumentException("unknown density profile");
      int x=Integer.parseInt(cells[2]);
      int y=Integer.parseInt(cells[3]);
      int z=Integer.parseInt(cells[4]);
      Object contextValue=point.newInstance(x,y,z);
      double observed=(Double)compute.invoke(function,contextValue);
      System.out.printf(Locale.ROOT,"%016x%n",Double.doubleToRawLongBits(observed));
    }
    if (count!=640) throw new IllegalStateException("incomplete 640-row probe");
  }
}
"""


def runtime_bits(server: Path, records: list[dict[str, object]], *, timeout: int = 120) -> list[str]:
    if len(records) != 640:
        raise DensityCaptureError("density primitive oracle requires exact 640 input contexts")
    with tempfile.TemporaryDirectory(prefix="helve-density-262-") as folder:
        work = Path(folder)
        classpath = official.extract_classpath(server, work / "classpath")
        java = work / "HelveDensityPrimitiveBits.java"
        java.write_text(JAVA_PROBE, encoding="utf-8")
        compiler = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(java)],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if compiler.returncode:
            raise DensityCaptureError("reflection-only JVM probe failed to compile: " + compiler.stderr[:900])
        stdin = "\n".join(
            f"{row['profile']}\t{row['seed_bits']}\t{row['block_x']}\t{row['block_y']}\t{row['block_z']}"
            for row in records
        ) + "\n"
        run = subprocess.run(
            ["java", "-Xmx512m", "-cp", os.pathsep.join([str(work), *(str(p) for p in classpath)]),
             "HelveDensityPrimitiveBits"], input=stdin, text=True,
            capture_output=True, check=False, timeout=timeout,
        )
        if run.returncode:
            raise DensityCaptureError("official density runtime rejected reflection profile: " + run.stderr[:1200])
        values = run.stdout.splitlines()
        if len(values) != len(records) or any(re.fullmatch(r"[0-9a-f]{16}", v) is None for v in values):
            raise DensityCaptureError("missing/extra/invalid official 64-bit density results")
        return ["0x" + value for value in values]


def validate(manifest: dict, lock: dict) -> None:
    required = {
        "schema", "kind", "minecraft", "protocol", "data_version",
        "source_archive_sha256", "official_server_sha256", "stage",
        "source_text_included", "independent_var_sem_admitted", "production_worldgen_enabled",
        "methods", "profiles", "vectors",
    }
    if not isinstance(manifest, dict) or set(manifest) != required or manifest.get("schema") != 1 or manifest.get("kind") != KIND:
        raise DensityCaptureError("missing or unexpected density manifest fields")
    for key, value in [
        ("minecraft", "26.2"), ("protocol", 776), ("data_version", 4903),
        ("stage", "density_primitive"),
        ("source_archive_sha256", lock["source"]["archive_sha256"]),
        ("official_server_sha256", lock["runtime"]["server_sha256"]),
        ("source_text_included", False),
        ("independent_var_sem_admitted", False),
        ("production_worldgen_enabled", False),
    ]:
        if type(manifest.get(key)) is not type(value) or manifest[key] != value:
            raise DensityCaptureError(f"wrong pinned density metadata: {key}")
    if manifest["profiles"] != PROFILES or set(manifest["methods"]) != set(METHODS):
        raise DensityCaptureError("missing or substituted explicit density profiles/source methods")
    for name, (owner, symbol, types) in METHODS.items():
        row = manifest["methods"][name]
        if not isinstance(row, dict) or set(row) != {"owner", "signature", "body_sha256", "normalized_sha256"}:
            raise DensityCaptureError("invalid source method identity")
        if row["owner"] != owner or not row["signature"].startswith(symbol + "("):
            raise DensityCaptureError("changed source method name")
        if any(not isinstance(row[key], str) or SHA.fullmatch(row[key]) is None
               for key in ("body_sha256", "normalized_sha256")):
            raise DensityCaptureError("unbound source method digest")
    rows = manifest["vectors"]
    wanted = inputs()
    if not isinstance(rows, list) or len(rows) != len(wanted):
        raise DensityCaptureError("missing density reference contexts")
    for index, (actual, expected) in enumerate(zip(rows, wanted, strict=True)):
        if not isinstance(actual, dict) or set(actual) != set(expected) | {"value_bits"}:
            raise DensityCaptureError("density vector shape differs")
        if any(type(actual[key]) is not type(value) or actual[key] != value
               for key, value in expected.items()):
            raise DensityCaptureError(f"wrong source-independent density context at row {index}")
        if not isinstance(actual["value_bits"], str) or HEX.fullmatch(actual["value_bits"]) is None:
            raise DensityCaptureError(f"density output must be exact raw bits at row {index}")


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    dest = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if pin.get("minecraft") != "26.2" or pin.get("protocol") != 776 or pin.get("data_version") != 4903:
        raise DensityCaptureError("wrong pinned Minecraft 26.2 lock")
    conn = vanilla_atlas.connect_db(db)
    try:
        source_digest = source_probe.require_pinned_source(conn, source, lock)
        methods = bound_methods(conn)
    finally:
        conn.close()
    runtime_digest = official.sha256_file(server)
    if runtime_digest != pin["runtime"]["server_sha256"]:
        raise DensityCaptureError("official 26.2 runtime mismatch")
    probe = inputs()
    output_bits = runtime_bits(server, probe)
    manifest = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "stage": "density_primitive",
        "source_archive_sha256": source_digest,
        "official_server_sha256": runtime_digest,
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "methods": methods, "profiles": PROFILES,
        "vectors": [dict(p, value_bits=value) for p, value in zip(probe, output_bits, strict=True)],
    }
    validate(manifest, pin)
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(encoded)
    return {
        "output": str(dest), "rows": len(probe),
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
    except (DensityCaptureError, OSError, ValueError, TypeError, KeyError,
            sqlite3.Error, projection.DiscoveryError, source_probe.ProbeError,
            subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(f"OFFICIAL 26.2 DENSITY PRIMITIVES NOT CAPTURED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
