#!/usr/bin/env python3
"""Source-free constructed-state probe for pinned official Java 26.2 noise.

Consumes an independently captured Perlin/Normal *output* oracle and invokes
the identical pinned official JVM factory to inspect private, typed numeric
state. No Java source, decompiled code, production enablement or semantic
review is copied/claimed. Field names are preserved as OBSERVED metadata,
not guessed semantic roles. Caller must upload the JSON separately.
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
import worldgen_26_2_perlin_normal_capture as family

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"0x[0-9a-f]{16}\Z")
HEX512 = re.compile(r"[0-9a-f]{512}\Z")
SEEDS = tuple(f"0x{seed:016x}" for seed in improved.SEEDS)
KINDS = frozenset({"D", "I", "A", "P", "Z", "L"})
MAX_RECORDS_PER_SEED = 150


class StateCaptureError(ValueError):
    """Observed Java state is missing, ambiguous, malformed or unpinned."""


# New authored reflective diagnostics, not excerpts of any game source.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.util.*;
public final class HelveFamilyStateBits {
  static Class<?> randomType, perlinType, normalType, improvedType, doubleListType;
  static Method randomCreate, perlinCreate, normalCreate;
  static String seed;

  static String raw(double value) {
    return String.format(Locale.ROOT, "%016x", Double.doubleToRawLongBits(value));
  }
  static String hex256(Object array) {
    int len=Array.getLength(array);
    if (len!=256) throw new IllegalStateException("expected 256 permutation entries");
    StringBuilder result=new StringBuilder(512);
    for (int index=0; index<len; index++) {
      int value=((Number) Array.get(array,index)).intValue();
      if (value<0) value &= 255;
      if (value<0 || value>255) throw new IllegalStateException("invalid permutation byte");
      result.append(String.format(Locale.ROOT,"%02x",value));
    }
    return result.toString();
  }
  static void emit(String kind, String path, String name, String value) {
    if (!path.matches("[A-Za-z0-9_./\\[\\]-]{1,128}")
        || !name.matches("[A-Za-z0-9_]{1,96}")) {
      throw new IllegalStateException("invalid reflected numeric state label");
    }
    System.out.println(kind+"\t"+seed+"\t"+path+"\t"+name+"\t"+value);
  }
  static Field[] sortedFields(Class<?> owner) {
    Field[] fields=owner.getDeclaredFields();
    Arrays.sort(fields, Comparator.comparing(Field::getName));
    return fields;
  }
  static Object sampleFactory(boolean perlin, Object random) throws Exception {
    if (perlin) {
      return perlinCreate.invoke(null, random, -3, 1.0,
                                 new double[]{0.0,0.5,1.0});
    }
    return normalCreate.invoke(null, random, -3,
                               new double[]{1.0,0.0,0.5,1.0});
  }
  static void improved(Object sampler, String path) throws Exception {
    int offsets=0, perms=0;
    for (Field field:sortedFields(improvedType)) {
      if (Modifier.isStatic(field.getModifiers())) continue;
      field.setAccessible(true);
      Class<?> type=field.getType();
      if (type==double.class) {
        emit("D",path,field.getName(),raw(field.getDouble(sampler))); offsets++;
      } else if (type.isArray()
                 && (type.getComponentType()==byte.class
                     || type.getComponentType()==int.class)) {
        emit("P",path,field.getName(),hex256(field.get(sampler))); perms++;
      }
    }
    if (offsets!=3 || perms!=1) {
      throw new IllegalStateException("unexpected private ImprovedNoise numeric state");
    }
  }
  static void perlin(Object sampler, String path) throws Exception {
    int arrays=0, lists=0;
    for (Field field:sortedFields(perlinType)) {
      if (Modifier.isStatic(field.getModifiers())) continue;
      field.setAccessible(true);
      Class<?> type=field.getType();
      Object value=field.get(sampler);
      if (type==double.class) {
        emit("D",path,field.getName(),raw(field.getDouble(sampler)));
      } else if (type==int.class) {
        emit("I",path,field.getName(),Integer.toString(field.getInt(sampler)));
      } else if (type.isArray() && type.getComponentType()==improvedType) {
        arrays++;
        int length=Array.getLength(value);
        if (length<1 || length>64) throw new IllegalStateException("invalid octave slot count");
        emit("L",path,field.getName(),Integer.toString(length));
        for (int i=0;i<length;i++) {
          Object octave=Array.get(value,i);
          String member=path+"/"+field.getName()+"["+i+"]";
          if (octave==null) emit("Z",member,"null","0");
          else improved(octave,member);
        }
      } else if (doubleListType.isAssignableFrom(type)) {
        lists++;
        int length=((Number)doubleListType.getMethod("size").invoke(value)).intValue();
        if (length<1 || length>64) throw new IllegalStateException("invalid amplitude count");
        emit("L",path,field.getName(),Integer.toString(length));
        Method get=doubleListType.getMethod("getDouble",int.class);
        for (int i=0;i<length;i++) {
          emit("A",path,field.getName()+"_"+i,
               raw(((Number)get.invoke(value,i)).doubleValue()));
        }
      }
    }
    if (arrays!=1 || lists!=1) {
      throw new IllegalStateException("unexpected private PerlinNoise state structure");
    }
  }
  static void normal(Object sampler, String path) throws Exception {
    int children=0;
    for (Field field:sortedFields(normalType)) {
      if (Modifier.isStatic(field.getModifiers())) continue;
      field.setAccessible(true);
      Class<?> type=field.getType();
      if (type==double.class) {
        emit("D",path,field.getName(),raw(field.getDouble(sampler)));
      } else if (type==perlinType) {
        children++;
        perlin(field.get(sampler),path+"/"+field.getName());
      }
    }
    if (children!=2) throw new IllegalStateException("expected exactly 2 PerlinNoise branches");
  }
  public static void main(String[] args) throws Exception {
    if(args.length!=1 || !(args[0].equals("perlin_noise")||args[0].equals("normal_noise"))) {
      throw new IllegalArgumentException("invalid noise family stage");
    }
    randomType=Class.forName("net.minecraft.util.RandomSource");
    perlinType=Class.forName("net.minecraft.world.level.levelgen.synth.PerlinNoise");
    normalType=Class.forName("net.minecraft.world.level.levelgen.synth.NormalNoise");
    improvedType=Class.forName("net.minecraft.world.level.levelgen.synth.ImprovedNoise");
    doubleListType=Class.forName("it.unimi.dsi.fastutil.doubles.DoubleList");
    randomCreate=randomType.getMethod("create",long.class);
    perlinCreate=perlinType.getMethod("create",randomType,int.class,double.class,double[].class);
    normalCreate=normalType.getMethod("create",randomType,int.class,double[].class);
    BufferedReader in=new BufferedReader(new InputStreamReader(
      System.in,java.nio.charset.StandardCharsets.US_ASCII));
    String line;
    int count=0;
    while((line=in.readLine())!=null) {
      if (!line.matches("[0-9a-f]{16}") || ++count>5) {
        throw new IllegalArgumentException("invalid or excessive seed rows");
      }
      seed=line;
      Object random=randomCreate.invoke(null,Long.parseUnsignedLong(line,16));
      Object sampler=sampleFactory(args[0].equals("perlin_noise"),random);
      if(args[0].equals("perlin_noise")) perlin(sampler,"root");
      else normal(sampler,"root");
    }
    if(count!=5) throw new IllegalStateException("expected five independent constructed states");
  }
}
"""


def parse_records(raw: str, expected_seeds: tuple[str, ...]) -> list[dict]:
    """Strict bounded record parser, retaining observable names but no code."""
    if len(raw) > 600_000:
        raise StateCaptureError("excessive state output bytes")
    records_by_seed: dict[str, list[dict[str, str]]] = {seed: [] for seed in expected_seeds}
    for index, line in enumerate(raw.splitlines()):
        parts = line.split("\t")
        if len(parts) != 5:
            raise StateCaptureError(f"wrong state record shape at line {index}")
        kind, seed, path, field, value = parts
        if kind not in KINDS or seed not in records_by_seed:
            raise StateCaptureError("unexpected record kind or seed")
        if not re.fullmatch(r"[A-Za-z0-9_./\[\]-]{1,128}", path) \
           or not re.fullmatch(r"[A-Za-z0-9_]{1,96}", field):
            raise StateCaptureError("unbounded reflection state identifiers")
        if kind in {"D", "A"} and HEX64.fullmatch("0x" + value) is None:
            raise StateCaptureError("floating-point state lost 64-bit encoding")
        if kind == "P":
            if HEX512.fullmatch(value) is None:
                raise StateCaptureError("permutation not exactly 256 raw bytes")
            values = bytes.fromhex(value)
            if len(set(values)) != 256:
                raise StateCaptureError("permutation is not a 256-value bijection")
        if kind in {"I", "L"} and (not re.fullmatch(r"-?[0-9]{1,10}", value)):
            raise StateCaptureError("invalid numeric state integer")
        if kind == "L" and not 1 <= int(value) <= 64:
            raise StateCaptureError("invalid state length")
        if kind == "Z" and value != "0":
            raise StateCaptureError("invalid absent octave marker")
        rows = records_by_seed[seed]
        if len(rows) >= MAX_RECORDS_PER_SEED:
            raise StateCaptureError("excessive state records per seed")
        rows.append({"kind": kind, "path": path, "field": field, "value": value})
    if not all(records_by_seed.values()):
        raise StateCaptureError("incomplete five-seed constructed-state coverage")
    # Required typed scaffolding is independent of reflected field names.
    for seed, rows in records_by_seed.items():
        permutations = sum(row["kind"] == "P" for row in rows)
        if permutations < 2:
            raise StateCaptureError(f"missing constructed octave permutation for {seed}")
        if not any(row["kind"] == "A" for row in rows):
            raise StateCaptureError("constructed octave amplitudes missing")
    return [{"seed_bits": seed, "records": records_by_seed[seed]} for seed in expected_seeds]


def run_official_state(server: Path, stage: str,
                       seeds: tuple[str, ...] = SEEDS, timeout: int = 120) -> list[dict]:
    if stage not in family.STAGES or len(seeds) != 5 or len(set(seeds)) != 5:
        raise StateCaptureError("unexpected stage or five-seed sampling profile")
    with tempfile.TemporaryDirectory(prefix="helve-family-state-") as directory:
        work = Path(directory)
        jars = official.extract_classpath(server, work / "classpath")
        source = work / "HelveFamilyStateBits.java"
        source.write_text(JAVA_PROBE, encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(source)],
            text=True, capture_output=True, timeout=timeout, check=False,
        )
        if compiled.returncode:
            raise StateCaptureError(f"official state helper compile failure: {compiled.stderr[:1000]}")
        result = subprocess.run(
            ["java", "-Xmx512m", "-cp",
             os.pathsep.join([str(work), *(str(j) for j in jars)]),
             "HelveFamilyStateBits", stage],
            input="\n".join(seed[2:] for seed in seeds) + "\n",
            text=True, capture_output=True, timeout=timeout, check=False,
        )
        if result.returncode:
            raise StateCaptureError(f"official state reflection rejected: {result.stderr[:1200]}")
        return parse_records(result.stdout, seeds)


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            reference: Path, output: Path) -> dict:
    dest = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    reference_bytes = reference.read_bytes()
    try:
        oracle = json.loads(reference_bytes)
    except json.JSONDecodeError as exc:
        raise StateCaptureError("reference family manifest is malformed") from exc
    if not isinstance(oracle, dict) or oracle.get("stage") not in family.STAGES:
        raise StateCaptureError("expected an official Perlin or Normal oracle")
    family.validate_family(oracle, pin)
    stage = oracle["stage"]
    if pin.get("minecraft") != "26.2" or pin.get("protocol") != 776 or pin.get("data_version") != 4903:
        raise StateCaptureError("not the exact 26.2 worldgen target")
    discovered_seeds = tuple(dict.fromkeys(v["seed_bits"] for v in oracle["vectors"]))
    if discovered_seeds != SEEDS:
        raise StateCaptureError("reference seed set/order is not the official fixed five-seed profile")
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        method_binding = family.bound_methods(conn, stage)
    finally:
        conn.close()
    if source_sha != oracle["source_archive_sha256"] \
       or method_binding != oracle["source_methods"]:
        raise StateCaptureError("reference differs from local pinned Atlas method binding")
    runtime_sha = official.sha256_file(server)
    if runtime_sha != pin["runtime"]["server_sha256"] or runtime_sha != oracle["official_server_sha256"]:
        raise StateCaptureError("reference/runtime SHA-256 disagreement")
    samples = run_official_state(server, stage, SEEDS)
    result = {
        "schema": 1,
        "kind": "official_26_2_noise_constructor_state_candidate",
        "minecraft": "26.2", "protocol": 776, "data_version": 4903,
        "stage": stage, "profile": family.PROFILE,
        "source_archive_sha256": source_sha,
        "official_server_sha256": runtime_sha,
        "source_methods": method_binding,
        "reference_oracle_sha256": hashlib.sha256(reference_bytes).hexdigest(),
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "note": "Read-only JVM state observation; numeric layouts are not VAR/SEM admission",
        "samples": samples,
    }
    payload = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
    return {"output": str(dest), "stage": stage, "seeds": len(samples),
            "records": sum(len(s["records"]) for s in samples),
            "file_sha256": hashlib.sha256(payload).hexdigest(),
            "production_worldgen_enabled": False,
            "independent_var_sem_admitted": False}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=family.SOURCE)
    p.add_argument("--db", type=Path, default=family.DB)
    p.add_argument("--lock", type=Path, default=family.LOCK)
    p.add_argument("--cache", type=Path, default=family.CACHE)
    p.add_argument("--server-jar", type=Path)
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            resolved, _ = official.resolve("26.2", args.cache)
            server = resolved["server"][0]
        result = capture(
            source=args.source, db=args.db, lock=args.lock, server=server,
            reference=args.reference, output=args.output,
        )
    except (OSError, StateCaptureError, ValueError, KeyError, TypeError, sqlite3.Error,
            source_probe.ProbeError, projection.DiscoveryError,
            subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print(f"Official noise-family constructor state NOT CAPTURED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
