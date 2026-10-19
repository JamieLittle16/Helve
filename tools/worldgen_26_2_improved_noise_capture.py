#!/usr/bin/env python3
"""Capture exact 26.2 ImprovedNoise 3D output bits from the pinned official JVM.

This uses the independent official Minecraft server runtime and the pinned
local source/Atlas fingerprint. It never evaluates a Python approximation,
copies Mojang Java source into the repository or admits VAR/SEM. No private
runtime or generated Java probe is committed. Only source-free raw-bit output
is emitted, exclusively to a fresh path outside the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import struct
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
from pathlib import Path
from typing import Sequence

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_noise_oracle as differential

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vanilla/vanilla.lock.toml"
SOURCE = Path.home() / "Documents/mc-source/mc-src.zip"
DB = ROOT / ".crucible/vanilla/atlas.sqlite"
CACHE = ROOT / ".crucible/vanilla/downloads"
OWNER = "net.minecraft.world.level.levelgen.synth.ImprovedNoise"
RANDOM_SOURCE = "net.minecraft.util.RandomSource"
METHOD = "noise"
MAX_METHODS = 32
MAX_PROBES = 1024
KIND = "official_26_2_noise_oracle_candidate"
HEX64 = re.compile(r"[0-9a-f]{16}\Z")
HASH256 = re.compile(r"[0-9a-f]{64}\Z")


class CaptureError(ValueError):
    """Pinned source, runtime, method or output contract was not satisfied."""


def external_output(path: Path) -> Path:
    if path.exists() or path.is_symlink():
        raise CaptureError("oracle output already exists (will not overwrite)")
    dest = path.expanduser().resolve(strict=False)
    try:
        dest.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        return dest
    raise CaptureError("official runtime vectors must be written outside the repository")


def select_source_method(rows: Sequence[sqlite3.Row]) -> sqlite3.Row:
    """Bind only the three-double overload; fail on missing or ambiguous signatures."""
    matches = []
    for row in rows:
        if row["name"] != METHOD:
            continue
        signature = str(row["signature"])
        pattern = r"\bnoise\s*\(([^()]*)\)"
        matches_in_sig = re.findall(pattern, signature)
        if len(matches_in_sig) != 1:
            continue
        parameters = [part.strip() for part in matches_in_sig[0].split(",")]
        if len(parameters) != 3:
            continue
        if all(re.match(r"^(?:final\s+)?double(?:\s+[A-Za-z_$][\w$]*)?$", p) for p in parameters):
            matches.append(row)
    if len(matches) != 1:
        raise CaptureError(f"expected one exact 3-double ImprovedNoise noise method, got {len(matches)}")
    return matches[0]


def source_fingerprint(conn: sqlite3.Connection) -> str:
    rows = projection._exact_type_methods(conn, OWNER, MAX_METHODS)
    row = select_source_method(rows)
    template = source_probe.record_template(conn, row, "INDEX-WORLDGEN-26_2-IMPROVED-NOISE-001")
    source = template.get("source")
    if not isinstance(source, dict) or source.get("type") != OWNER:
        raise CaptureError("Atlas returned a different owner")
    body = source.get("body_sha256")
    normalized = source.get("normalized_sha256")
    if (not isinstance(body, str) or HASH256.fullmatch(body) is None
        or body == hashlib.sha256(b"").hexdigest()
        or not isinstance(normalized, str) or HASH256.fullmatch(normalized) is None):
        raise CaptureError("exact executable source method fingerprint is unavailable")
    return body


def u64(value: int) -> str:
    return f"0x{value & ((1 << 64) - 1):016x}"


def float_bits(value: float) -> str:
    return "0x" + struct.pack(">d", value).hex()


def probes() -> list[dict[str, str]]:
    """Seed-/coordinate-diverse, order-preserving fixed candidate probe corpus.

    Coordinates are frozen raw bits. This is NOT a full test of all runtime
    noise branches, nor does it guarantee target-source method correctness.
    """
    seeds = (0, 1, 0xffff_ffff_ffff_ffff, 0x8000_0000_0000_0000, 0x9e37_79b9_7f4a_7c15)
    triples = (
        (0.0, 0.0, 0.0), (-0.0, 0.0, 0.0), (0.0, -0.0, 0.0),
        (0.0, 0.0, -0.0), (-0.0, -0.0, -0.0),
        (0.5, 0.5, 0.5), (-0.5, -0.5, -0.5),
        (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0),
        (-8.0, 40.0, -8.0), (-16.0, -64.0, 16.0),
        (16.0, -64.0, -16.0), (15.999, 319.0, 16.001),
        (31.125, -63.875, -31.125), (-31.125, 319.875, 31.125),
        (0.0000000000000002, -0.0000000000000002, 7.0),
        (1.0000000000000002, -1.0000000000000002, -7.0),
        (-128.5, -64.5, 256.75), (1024.125, 2048.25, -4096.375),
        (-65536.0, -2.0, 65536.0), (4095.999999, -63.0, 0.25),
        (-4096.000001, 318.0, -0.25), (0.125, 0.25, 0.375),
        (0.75, 0.875, 0.9375), (-0.25, -0.75, 0.25),
        (2.0**20, 256.0, -(2.0**20)), (-(2.0**20), 0.0, 2.0**20),
        (2.0**30, -64.0, -(2.0**30)), (-(2.0**30), 319.0, 2.0**30),
        (2.0**-30, -(2.0**-30), 2.0**-20),
        (1.5, -1.25, 2.125), (-1.5, 1.25, -2.125),
    )
    result = [
        {"seed_bits": u64(seed), "x_bits": float_bits(x),
         "y_bits": float_bits(y), "z_bits": float_bits(z)}
        for seed in seeds for (x, y, z) in triples
    ]
    if len(result) > MAX_PROBES:
        raise CaptureError("more than bounded maximum official probes")
    keys = [tuple(item.values()) for item in result]
    if len(keys) != len(set(keys)):
        raise CaptureError("duplicate fixed probe coordinate/seed pair")
    return result


# This source is authored by Helve and purely reflective. No Mojang source
# or class implementation is embedded or copied.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.util.*;
public final class HelveImprovedNoiseBits {
  private static long decode(String raw) {
    if (!raw.matches("[0-9a-f]{16}")) throw new IllegalArgumentException("not raw 64 bits");
    return Long.parseUnsignedLong(raw, 16);
  }

  public static void main(String[] args) throws Exception {
    Class<?> randomType = Class.forName("net.minecraft.util.RandomSource");
    Class<?> noiseType = Class.forName("net.minecraft.world.level.levelgen.synth.ImprovedNoise");
    Method randomCreate = randomType.getMethod("create", long.class);
    Constructor<?> constructor = noiseType.getConstructor(randomType);
    Method noise = noiseType.getMethod("noise", double.class, double.class, double.class);
    if (!Modifier.isStatic(randomCreate.getModifiers())
        || !Modifier.isPublic(noise.getModifiers())
        || noise.getReturnType() != double.class) {
      throw new IllegalStateException("unexpected official 26.2 noise shape");
    }

    Map<Long,Object> bySeed = new HashMap<>();
    BufferedReader input = new BufferedReader(new InputStreamReader(System.in, java.nio.charset.StandardCharsets.US_ASCII));
    String line;
    int count = 0;
    while ((line = input.readLine()) != null) {
      String[] cells = line.split("\\t", -1);
      if (cells.length != 4 || ++count > 1024) {
        throw new IllegalArgumentException("invalid input row or probe count");
      }
      long seed = decode(cells[0]);
      Object sampler = bySeed.get(seed);
      if (sampler == null) {
        sampler = constructor.newInstance(randomCreate.invoke(null, seed));
        bySeed.put(seed, sampler);
      }
      double x = Double.longBitsToDouble(decode(cells[1]));
      double y = Double.longBitsToDouble(decode(cells[2]));
      double z = Double.longBitsToDouble(decode(cells[3]));
      double sample = (Double) noise.invoke(sampler, x, y, z);
      long bits = Double.doubleToRawLongBits(sample);
      System.out.printf(java.util.Locale.ROOT, "%016x%n", bits);
    }
  }
}
"""


def read_runtime_bits(
    server: Path, records: Sequence[dict[str, str]], *,
    timeout: int = 120,
) -> list[str]:
    """Run only a fixed reflective stub against an official, verified server jar."""
    with tempfile.TemporaryDirectory(prefix="helve-noise-bits-") as folder:
        work = Path(folder)
        entries = official.extract_classpath(server, work / "classpath")
        src = work / "HelveImprovedNoiseBits.java"
        src.write_text(JAVA_PROBE, encoding="utf-8")
        comp = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(src)],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if comp.returncode:
            raise CaptureError(f"official noise probe compiler rejected stub: {comp.stderr[:1200]}")
        classpath = os.pathsep.join([str(work), *(str(p) for p in entries)])
        inputs = "\n".join(
            "\t".join(record[field][2:] for field in differential.INPUT_FIELDS)
            for record in records
        ) + "\n"
        proc = subprocess.run(
            ["java", "-Xmx512m", "-cp", classpath, "HelveImprovedNoiseBits"],
            input=inputs, text=True, capture_output=True, check=False, timeout=timeout,
        )
        if proc.returncode:
            raise CaptureError(f"official JVM noise probe failed: {proc.stderr[:1400]}")
        answers = proc.stdout.splitlines()
        if len(answers) != len(records) or any(HEX64.fullmatch(v) is None for v in answers):
            raise CaptureError("official JVM returned incomplete/non-bit-preserving probe rows")
        return ["0x" + value for value in answers]


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    destination = external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin["minecraft"] != "26.2" or pin["protocol"] != 776
        or pin["data_version"] != 4903):
        raise CaptureError("requested server profile is not the 26.2 pinned target")
    conn = vanilla_atlas.connect_db(db)
    try:
        actual_source_sha = source_probe.require_pinned_source(conn, source, lock)
        body_sha = source_fingerprint(conn)
    finally:
        conn.close()
    actual_runtime = official.sha256_file(server)
    if actual_runtime != pin["runtime"]["server_sha256"]:
        raise CaptureError("official runtime archive does not match locked 26.2 server")
    records = probes()
    outputs = read_runtime_bits(server, records)
    vectors = [dict(record, value_bits=answer) for record, answer in zip(records, outputs, strict=True)]
    manifest = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "source_archive_sha256": actual_source_sha,
        "official_server_sha256": actual_runtime, "stage": "improved_noise",
        "method_body_sha256": body_sha, "source_text_included": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
        "vectors": vectors,
    }
    differential.validate(manifest, pin, KIND)
    data = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    return {
        "output": str(destination), "vectors": len(vectors),
        "source_method_body_sha256": body_sha, "oracle_file_sha256": hashlib.sha256(data).hexdigest(),
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
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
        result = capture(
            source=args.source, db=args.db, lock=args.lock, server=server,
            output=args.output,
        )
    except (CaptureError, ValueError, OSError, KeyError, IndexError, TypeError,
            sqlite3.Error, source_probe.ProbeError, projection.DiscoveryError,
            subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print(f"Official ImprovedNoise vector capture REJECTED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
