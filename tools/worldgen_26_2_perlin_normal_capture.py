#!/usr/bin/env python3
"""Pin and capture official Minecraft Java 26.2 PerlinNoise / NormalNoise output bits.

The exact, source-free method fingerprints below came from a separate,
user-supplied local Atlas inventory of the pinned official 26.2 source ZIP.
They establish method identity and a review *frontier*, not VAR/SEM admission.
The reference JVM alone supplies all output bits; no algorithm is inferred.

Both stages deliberately use ONE fixed, explicit profile:
  RandomSource.create(seed), firstOctave=-3, amplitudes=[1,0,0.5,1].
No world-seed mixing, parameter registry or density router is claimed.
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
from typing import Mapping, Sequence

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_26_2_improved_noise_capture as improved
import worldgen_noise_oracle as raw_oracle

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "vanilla/vanilla.lock.toml"
SOURCE = Path.home() / "Documents/mc-source/mc-src.zip"
DB = ROOT / ".crucible/vanilla/atlas.sqlite"
CACHE = ROOT / ".crucible/vanilla/downloads"
KIND = "official_26_2_noise_oracle_candidate"
PERLIN = "net.minecraft.world.level.levelgen.synth.PerlinNoise"
NORMAL = "net.minecraft.world.level.levelgen.synth.NormalNoise"
HEX64 = re.compile(r"[0-9a-f]{16}\Z")
STAGES = {"perlin_noise": PERLIN, "normal_noise": NORMAL}
PROFILE = {
    "random_factory": "RandomSource.create(long)",
    "first_octave": -3,
    "amplitudes_bits": [
        "0x3ff0000000000000", "0x0000000000000000",
        "0x3fe0000000000000", "0x3ff0000000000000",
    ],
}
# Exact source-free identities from the user's 26.2 method inventory.
# Constructor/create and reached critical delegates are independently bound,
# but their semantic rules have NOT been source-reviewed/admitted.
EXPECTED: dict[str, dict[str, tuple[str, str, str]]] = {
    "perlin_noise": {
        "create": (
            PERLIN,
            "create(final RandomSource random , final int firstOctave , final double firstAmplitude , final double ... amplitudes)",
            "75af76ad1ae2e6d40d935b7b7e6189885a5a86ca94d358220357f142796906c6",
        ),
        "constructor": (
            PERLIN,
            "PerlinNoise(final RandomSource random , final Pair < Integer , DoubleList > pair , final boolean useNewInitialization)",
            "284f244706e539438c714b5c6fbbbf5d3e030dac309865d28de8722bad7311a3",
        ),
        "get_value_3": (
            PERLIN,
            "getValue(final double x , final double y , final double z)",
            "d26c57b409a8113b0e1cccbe4f2158e158e2078cd1be6e8617588af4201e71d5",
        ),
        "get_value_5": (
            PERLIN,
            "getValue(final double x , final double y , final double z , final double yScale , final double yFudge)",
            "6fac8c41416a2d5ec966baab1e3c4cf231408c40932bac469a871c664b7ca838",
        ),
        "wrap": (
            PERLIN,
            "wrap(final double x)",
            "64bd4c4c429d67919314fbb39b360a4ef6a7c6252abd6f3267b7e78d078b85ac",
        ),
        "skip_octave": (
            PERLIN,
            "skipOctave(final RandomSource random)",
            "d9935d2d05d184965e7d7623fbd5593bd180a06c3800415c675ec2eb8d639e71",
        ),
    },
    "normal_noise": {
        "create": (
            NORMAL,
            "create(final RandomSource random , final int firstOctave , final double ... amplitudes)",
            "ce4d2746996bf4244a3b79bf86ccdf6c51c36f612047f7843427461e998f7d8e",
        ),
        "create_parameters": (
            NORMAL,
            "create(final RandomSource random , final NormalNoise . NoiseParameters parameters)",
            "5387d64a511913ac0f013cfbd374a997e61fd80be3e458a406e2ebfb12a5302a",
        ),
        "constructor": (
            NORMAL,
            "NormalNoise(final RandomSource random , final NormalNoise . NoiseParameters parameters , final boolean useNewInitialization)",
            "52d398b9f46301b0bd5d6e6c675fe5b88760e7dba1cdb5f1ad5596d855255eff",
        ),
        "get_value_3": (
            NORMAL,
            "getValue(final double x , final double y , final double z)",
            "578fbb9c36fa89507fbf842effbdadcebb1aeb7369641e972f9e737ef30bd329",
        ),
        "noise_parameters": (
            NORMAL,
            "NoiseParameters(int firstOctave , DoubleList amplitudes)",
            "ce58234fdbd4896e39fbdacebc79ae0bc452148d5739a616a76d9875c59eeaaa",
        ),
        "deviation": (
            NORMAL,
            "expectedDeviation(final int octaveSpan)",
            "2aa56548edebbe567587083d861a73a609068eb4e68c54c7aa0dac7fdefbe3c4",
        ),
        "perlin_create": (
            PERLIN,
            "create(final RandomSource random , final int firstOctave , final DoubleList amplitudes)",
            "92c230c5a209826c90ecad53a0c231a237839a8cbee9a73074e1d6d64b6f8156",
        ),
        "perlin_get_value_3": (
            PERLIN,
            "getValue(final double x , final double y , final double z)",
            "d26c57b409a8113b0e1cccbe4f2158e158e2078cd1be6e8617588af4201e71d5",
        ),
    },
}


class CaptureError(ValueError):
    """Exact 26.2 noise family, archive, JVM or output evidence is invalid."""


def bound_methods(conn: sqlite3.Connection, stage: str) -> dict[str, dict[str, str]]:
    if stage not in STAGES:
        raise CaptureError("noise family stage must be perlin_noise or normal_noise")
    rows_by_owner: dict[str, dict[str, sqlite3.Row]] = {}
    for owner in {record[0] for record in EXPECTED[stage].values()}:
        rows = projection._exact_type_methods(conn, owner, 64)
        signatures = [str(row["signature"]) for row in rows]
        if len(signatures) != len(set(signatures)):
            raise CaptureError(f"ambiguous Atlas method declarations for {owner}")
        rows_by_owner[owner] = {str(row["signature"]): row for row in rows}
    result = {}
    for name, (owner, signature, expected_hash) in EXPECTED[stage].items():
        row = rows_by_owner[owner].get(signature)
        if row is None:
            raise CaptureError(f"missing exact source method for {name}: {owner}#{signature}")
        indexed = source_probe.record_template(conn, row, f"INDEX-WORLDGEN-26_2-{stage.upper()}-{name.upper()}")
        source = indexed.get("source")
        if not isinstance(source, dict) or source.get("type") != owner or source.get("signature") != signature:
            raise CaptureError(f"Atlas method identity disagrees with {name}")
        if source.get("body_sha256") != expected_hash:
            raise CaptureError(f"source body fingerprint differs from owner-reviewed inventory: {name}")
        normalized = source.get("normalized_sha256")
        if not isinstance(normalized, str) or not re.fullmatch(r"[0-9a-f]{64}", normalized):
            raise CaptureError(f"normalized source hash missing for {name}")
        result[name] = {"owner": owner, "signature": signature, "body_sha256": expected_hash}
    return result


# Helve-authored original reflective bridge. The target Java implementation
# and its parameter algorithms are never copied or inferred in this source.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.util.*;
public final class HelveNoiseFamilyBits {
  private static long bits(String s) {
    if (!s.matches("[0-9a-f]{16}")) throw new IllegalArgumentException("bad raw bits");
    return Long.parseUnsignedLong(s, 16);
  }
  public static void main(String[] args) throws Exception {
    if (args.length != 1 || !(args[0].equals("perlin_noise") || args[0].equals("normal_noise"))) {
      throw new IllegalArgumentException("unsupported stage");
    }
    boolean perlin = args[0].equals("perlin_noise");
    Class<?> randomType = Class.forName("net.minecraft.util.RandomSource");
    Class<?> family = Class.forName(
      perlin ? "net.minecraft.world.level.levelgen.synth.PerlinNoise"
             : "net.minecraft.world.level.levelgen.synth.NormalNoise");
    Method randomCreate = randomType.getMethod("create", long.class);
    Method factory = perlin
      ? family.getMethod("create", randomType, int.class, double.class, double[].class)
      : family.getMethod("create", randomType, int.class, double[].class);
    Method sample = family.getMethod("getValue", double.class, double.class, double.class);
    if (!Modifier.isStatic(randomCreate.getModifiers())
        || !Modifier.isStatic(factory.getModifiers())
        || !family.isAssignableFrom(factory.getReturnType())
        || sample.getReturnType() != double.class) {
      throw new IllegalStateException("official runtime signature disagrees with source Atlas");
    }
    Map<Long,Object> perSeed = new HashMap<>();
    BufferedReader in = new BufferedReader(
      new InputStreamReader(System.in, java.nio.charset.StandardCharsets.US_ASCII));
    String line;
    int count = 0;
    while ((line = in.readLine()) != null) {
      String[] cells = line.split("\\t", -1);
      if (cells.length != 4 || ++count > 1024) {
        throw new IllegalArgumentException("incorrect raw probe row count or shape");
      }
      long seed = bits(cells[0]);
      Object instance = perSeed.get(seed);
      if (instance == null) {
        Object random = randomCreate.invoke(null, seed);
        double[] amplitudes = new double[] {1.0, 0.0, 0.5, 1.0};
        instance = perlin
          ? factory.invoke(null, random, -3, amplitudes[0],
                           new double[] {amplitudes[1], amplitudes[2], amplitudes[3]})
          : factory.invoke(null, random, -3, amplitudes);
        perSeed.put(seed, instance);
      }
      double x = Double.longBitsToDouble(bits(cells[1]));
      double y = Double.longBitsToDouble(bits(cells[2]));
      double z = Double.longBitsToDouble(bits(cells[3]));
      double value = (Double) sample.invoke(instance, x, y, z);
      System.out.printf(Locale.ROOT, "%016x%n", Double.doubleToRawLongBits(value));
    }
  }
}
"""


def capture_runtime_bits(
    server: Path, stage: str, records: Sequence[Mapping[str, str]],
    *, timeout: int = 120,
) -> list[str]:
    if stage not in STAGES or len(records) > 1024:
        raise CaptureError("unknown family or excessive JVM probe count")
    with tempfile.TemporaryDirectory(prefix="helve-noise-family-") as directory:
        work = Path(directory)
        classpath = official.extract_classpath(server, work / "classpath")
        source = work / "HelveNoiseFamilyBits.java"
        source.write_text(JAVA_PROBE, encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(source)],
            check=False, text=True, capture_output=True, timeout=timeout,
        )
        if compiled.returncode != 0:
            raise CaptureError(f"family reflection compiler rejected probe: {compiled.stderr[:1000]}")
        raw = "\n".join(
            "\t".join(item[field][2:] for field in raw_oracle.INPUT_FIELDS)
            for item in records
        ) + "\n"
        run = subprocess.run(
            ["java", "-Xmx512m", "-cp", os.pathsep.join([str(work), *(str(p) for p in classpath)]),
             "HelveNoiseFamilyBits", stage],
            input=raw, check=False, text=True, capture_output=True, timeout=timeout,
        )
        if run.returncode != 0:
            raise CaptureError(f"official family JVM probe rejected profile: {run.stderr[:1200]}")
        outputs = run.stdout.splitlines()
        if len(outputs) != len(records) or any(HEX64.fullmatch(x) is None for x in outputs):
            raise CaptureError("missing, extra or non-raw-bit official family probe outputs")
        return ["0x" + x for x in outputs]


def validate_family(manifest: dict, lock: dict) -> dict[tuple[str, ...], str]:
    base_fields = {
        "schema", "kind", "minecraft", "protocol", "data_version",
        "source_archive_sha256", "official_server_sha256", "stage",
        "method_body_sha256", "source_text_included",
        "independent_var_sem_admitted", "production_worldgen_enabled", "vectors",
    }
    if not isinstance(manifest, dict) or set(manifest) != base_fields | {"profile", "source_methods"}:
        raise CaptureError("family manifest has missing, extra or source-rich fields")
    stage = manifest["stage"]
    if stage not in STAGES or manifest["profile"] != PROFILE:
        raise CaptureError("unexpected or substituted 26.2 family construction profile")
    methods = manifest["source_methods"]
    if not isinstance(methods, dict) or set(methods) != set(EXPECTED[stage]):
        raise CaptureError("family manifest has incomplete source-method binding")
    for name, (owner, signature, fingerprint) in EXPECTED[stage].items():
        if methods[name] != {"owner": owner, "signature": signature, "body_sha256": fingerprint}:
            raise CaptureError(f"incorrect source method identity for {name}")
    if manifest["method_body_sha256"] != EXPECTED[stage]["get_value_3"][2]:
        raise CaptureError("family primary method hash differs from JVM target")
    return raw_oracle.validate({key: manifest[key] for key in base_fields}, lock, KIND)


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            stage: str, output: Path) -> dict:
    if stage not in STAGES:
        raise CaptureError("requested family stage is not supported")
    dest = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin.get("minecraft") != "26.2" or pin.get("protocol") != 776
        or pin.get("data_version") != 4903):
        raise CaptureError("not the pinned official 26.2 worldgen profile")
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        methods = bound_methods(conn, stage)
    finally:
        conn.close()
    runtime_sha = official.sha256_file(server)
    if runtime_sha != pin["runtime"]["server_sha256"]:
        raise CaptureError("official 26.2 runtime SHA-256 differs from source lock")
    probe_inputs = improved.probes()
    output_bits = capture_runtime_bits(server, stage, probe_inputs)
    vectors = [dict(record, value_bits=bits)
               for record, bits in zip(probe_inputs, output_bits, strict=True)]
    manifest = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "source_archive_sha256": source_sha,
        "official_server_sha256": runtime_sha, "stage": stage,
        "method_body_sha256": methods["get_value_3"]["body_sha256"],
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False, "profile": PROFILE,
        "source_methods": methods, "vectors": vectors,
    }
    validate_family(manifest, pin)
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as writer:
        writer.write(encoded)
    return {
        "output": str(dest), "stage": stage, "vectors": len(vectors),
        "file_sha256": hashlib.sha256(encoded).hexdigest(),
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--lock", type=Path, default=LOCK)
    parser.add_argument("--cache", type=Path, default=CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--stage", choices=sorted(STAGES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            resolved, _ = official.resolve("26.2", args.cache)
            server = resolved["server"][0]
        result = capture(
            source=args.source, db=args.db, lock=args.lock,
            server=server, stage=args.stage, output=args.output,
        )
    except (CaptureError, OSError, ValueError, TypeError, KeyError,
            sqlite3.Error, projection.DiscoveryError, source_probe.ProbeError,
            subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print(f"Official 26.2 {args.stage} bits NOT CAPTURED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
