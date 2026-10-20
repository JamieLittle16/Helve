#!/usr/bin/env python3
"""Bounded, source-free 26.2 stock registered-noise numeric-state receipt.

This is deliberately NOT another 1,440-vector capture. It observes the
NoiseParameters and two complete prepared Perlin branches for five world seeds
and three real stock keys, with the same source/JAR/stock-provider preflight
as the successful official DensityFunctions.Noise oracle. Source-method
fingerprints identify code but do not independently establish RNG laws.
No VAR/SEM/production/world-seed constructor admission follows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

PROBE = Path(__file__).resolve().parent / "worldgen_java/HelveWorldSeededState262.java"
PREFIX = "HELVE26_2_REGISTERED_STATE|"
FAILURE = "HELVE26_2_REGISTERED_STATE_FAILURE|"
TYPES = {"I", "D", "A", "P", "L", "Z", "E"}
HEX64 = re.compile(r"[0-9a-f]{16}\Z")
HEX256 = re.compile(r"[0-9a-f]{512}\Z")
IDENT = re.compile(r"[A-Za-z0-9_]{1,80}\Z")
PATH = re.compile(r"[A-Za-z0-9_/\[\].-]{1,120}\Z")
INTEGER = re.compile(r"-?[0-9]{1,10}\Z")
MAX_RECORDS = 15_000


class RegisteredStateError(ValueError):
    """Stock constructor-state evidence incomplete, malformed or unpinned."""


def _numeric(row: dict) -> None:
    kind, value = row["kind"], row["value"]
    if kind in {"D", "A"}:
        if HEX64.fullmatch(value) is None:
            raise RegisteredStateError("raw floating-point bits malformed")
        number = struct.unpack(">d", bytes.fromhex(value))[0]
        if not math.isfinite(number):
            raise RegisteredStateError("nonfinite noise parameter/state")
    elif kind == "P":
        if HEX256.fullmatch(value) is None or len(set(bytes.fromhex(value))) != 256:
            raise RegisteredStateError("not a 256-byte permutation bijection")
    elif kind in {"I", "L"}:
        if INTEGER.fullmatch(value) is None or (kind == "L" and not 1 <= int(value) <= 64):
            raise RegisteredStateError("invalid octave count or signed int")
        if kind == "I" and not -(1 << 31) <= int(value) < (1 << 31):
            raise RegisteredStateError("out-of-range Java signed i32")
    elif kind == "Z" and value != "0":
        raise RegisteredStateError("absent octave has nonzero marker")
    elif kind == "E" and (row["path"], row["name"], value) != ("sample", "complete", "1"):
        raise RegisteredStateError("invalid sample terminator")


def _validate_group(rows: list[dict]) -> None:
    if not rows or rows[-1] != {"kind":"E", "path":"sample","name":"complete","value":"1"}:
        raise RegisteredStateError("missing stock seed/key sample terminator")
    records = rows[:-1]
    def selected(kind: str, path: str) -> list[dict]:
        return [r for r in records if r["kind"] == kind and r["path"] == path]

    if len(selected("I", "parameters")) != 1 or len(selected("L", "parameters")) != 1:
        raise RegisteredStateError("missing registered first octave/amplitude count")
    params_len = int(selected("L","parameters")[0]["value"])
    if len(selected("A","parameters")) != params_len:
        raise RegisteredStateError("registered amplitude vector incomplete")
    if not selected("D","normal"):
        raise RegisteredStateError("normal output factors absent")

    branches = {r["path"] for r in records if r["path"].startswith("normal/")
                and r["path"].count("/") == 1}
    if len(branches) != 2:
        raise RegisteredStateError("not exactly two independent Perlin states")
    for branch in branches:
        if len(selected("I",branch)) != 1 or len(selected("L",branch)) != 2:
            raise RegisteredStateError("missing Perlin octave/scale shape")
        lengths = [int(v["value"]) for v in selected("L",branch)]
        if lengths[0] != lengths[1] or len(selected("A",branch)) != lengths[0]:
            raise RegisteredStateError("Perlin amplitude/slot span differs")
        if len(selected("D",branch)) < 2:
            raise RegisteredStateError("Perlin frequency/value factors absent")
        slots = sorted({r["path"] for r in records if r["path"].startswith(branch+"/")})
        if len(slots) != lengths[0]:
            raise RegisteredStateError("missing Perlin octave slot")
        parent_names = [
            r["name"] for r in selected("L",branch)
            if all(s.startswith(branch+"/"+r["name"]+"[") for s in slots)
        ]
        if len(parent_names) != 1:
            raise RegisteredStateError("ambiguous or unbound octave-array field")
        expected_base = branch + "/" + parent_names[0]
        if slots != sorted(expected_base + "[" + str(i) + "]" for i in range(lengths[0])):
            raise RegisteredStateError("noncontiguous or reordered octave slots")
        for slot in slots:
            nulls = selected("Z",slot)
            if nulls:
                if len(nulls) != 1 or any(r["path"] == slot and r["kind"] != "Z" for r in records):
                    raise RegisteredStateError("mixed absent/live octave state")
            elif len(selected("D",slot)) != 3 or len(selected("P",slot)) != 1:
                raise RegisteredStateError("incomplete live ImprovedNoise state")


def parse(stdout: str) -> list[dict]:
    """Accept exactly 15 ordered seed/key groups; preserve all raw bits."""
    if len(stdout.encode("utf-8")) > 1_500_000 or len(stdout.splitlines()) > MAX_RECORDS + 1000:
        raise RegisteredStateError("excessive JVM numeric state output")
    if FAILURE in stdout:
        failures = [s for s in stdout.splitlines() if s.startswith(FAILURE)]
        if len(failures) != 1 or len(failures[0]) > 800 or failures[0].count("|") != 3:
            raise RegisteredStateError("corrupted/duplicated JVM error record")
        raise RegisteredStateError("stock JVM phase/exception: " + failures[0][len(FAILURE):])
    records: list[dict] = []
    groups = []
    current: list[dict] = []
    seen = set()
    for line in stdout.splitlines():
        if not line.startswith(PREFIX):
            continue  # Minecraft redirects its own logging streams.
        chunks = line.split("|")
        if len(chunks) != 7:
            raise RegisteredStateError("invalid JVM state row framing")
        _, seed, key, kind, path, name, value = chunks
        index = len(groups)
        if index >= len(stock.SEEDS) * len(stock.NOISE_KEYS) or            seed != str(index // len(stock.NOISE_KEYS)) or            key != str(index % len(stock.NOISE_KEYS)):
            raise RegisteredStateError("wrong signed seed/stock key order")
        if kind not in TYPES or IDENT.fullmatch(name) is None or PATH.fullmatch(path) is None:
            raise RegisteredStateError("unexpected JVM state path/type")
        row = {"kind":kind, "path":path, "name":name, "value":value}
        _numeric(row)
        marker = (kind,path,name)
        if marker in seen:
            raise RegisteredStateError("duplicate numeric field receipt")
        seen.add(marker)
        current.append(row)
        if len(records) + len(current) > MAX_RECORDS:
            raise RegisteredStateError("excessive octave-state records")
        if kind == "E":
            _validate_group(current)
            groups.append({"world_seed_bits": stock.SEEDS[index // len(stock.NOISE_KEYS)],
                           "noise_key": stock.NOISE_KEYS[index % len(stock.NOISE_KEYS)],
                           "records":current})
            records.extend(current)
            current=[]
            seen=set()
    if current or len(groups) != 15:
        raise RegisteredStateError("incomplete official five-seed/three-key state")
    # Registry parameters are stock definitions, never seed-specific guesses.
    # Reject drift in octave number, slot count, amplitude bits or field identity.
    for key_index in range(len(stock.NOISE_KEYS)):
        reference = [r for r in groups[key_index]["records"]
                     if r["path"] == "parameters"]
        for seed_index in range(1,len(stock.SEEDS)):
            other = [r for r in groups[seed_index*len(stock.NOISE_KEYS)+key_index]["records"]
                     if r["path"] == "parameters"]
            if other != reference:
                raise RegisteredStateError("registered key parameters drift by worldseed")
    return groups


def observe(server: Path, *, timeout: int = 180) -> list[dict]:
    """One already-qualified stock setup, 15 sampler introspections; no density recapture."""
    if not PROBE.is_file() or not stock.JAVA_SOURCE.is_file():
        raise RegisteredStateError("missing original reflection-only Java helpers")
    with tempfile.TemporaryDirectory(prefix="helve-262-registered-state-") as scratch:
        work = Path(scratch)
        cp = official.extract_classpath(server, work / "classpath")
        built = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             str(stock.JAVA_SOURCE), str(PROBE)],
            capture_output=True, text=True, check=False, timeout=timeout)
        if built.returncode:
            raise RegisteredStateError("original state bridge javac failed: " + built.stderr[:1600])
        seeds = "\n".join(stock.SEEDS) + "\n"
        run = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join([str(work), *(str(jar) for jar in cp)]),
             "HelveWorldSeededState262"],
            input=seeds, text=True, capture_output=True, check=False, timeout=timeout)
        # Parse tagged failures even on nonzero exit; never convert partial output to a receipt.
        if run.returncode:
            parse(run.stdout)
            raise RegisteredStateError("stock JVM rejected probe: "+stock.java_failure_detail(run.stderr))
        return parse(run.stdout)


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version")) != ("26.2",776,4903):
        raise RegisteredStateError("not the pinned 26.2 target")
    reference = stock.reference_frontier(frontier,pin)
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn,source,lock)
        methods = stock.source_methods(reference,conn)
    finally:
        conn.close()
    if source_sha != frozen.SOURCE_SHA256 or        methods["stock_vanilla_lookup"]["body_sha256"] != frozen.VANILLA_STOCK_LOOKUP_SHA256:
        raise RegisteredStateError("official source/stock registry pin changed")
    server_sha = official.sha256_file(server)
    if server_sha != frozen.SERVER_SHA256 or server_sha != pin["runtime"]["server_sha256"]:
        raise RegisteredStateError("not the pinned official runtime")
    samples = observe(server)
    result = {
        "schema":1, "kind":"official_26_2_stock_registered_noise_numeric_state_receipt",
        "minecraft":"26.2", "protocol":776, "data_version":4903,
        "source_archive_sha256":source_sha, "official_server_sha256":server_sha,
        "frontier_sha256":stock.FRONTIER_SHA256, "source_methods":methods,
        "reference_fixture_sha256":frozen.FIXTURE_SHA256,
        "stock_registry_used":True, "world_seed_random_state_observed":True,
        "world_seed_random_state_bound":False, "source_text_included":False,
        "independent_var_sem_admitted":False, "production_worldgen_enabled":False,
        "samples":samples,
    }
    payload=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with os.fdopen(os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"wb") as stream:
        stream.write(payload)
    return {"output":str(destination), "samples":len(samples),
            "sha256":hashlib.sha256(payload).hexdigest(),
            "world_seed_random_state_bound":False, "production_worldgen_enabled":False}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=stock.primitive.SOURCE)
    p.add_argument("--db",type=Path,default=stock.primitive.DB)
    p.add_argument("--lock",type=Path,default=stock.primitive.LOCK)
    p.add_argument("--cache",type=Path,default=stock.primitive.CACHE)
    p.add_argument("--server-jar",type=Path)
    p.add_argument("--frontier",type=Path,default=stock.FRONTIER)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            found,_=official.resolve("26.2",args.cache)
            server=found["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
             server=server,frontier=args.frontier,output=args.output),sort_keys=True))
    except (RegisteredStateError,stock.WorldSeedNoiseError,ValueError,OSError,KeyError,
            TypeError,sqlite3.Error,source_probe.ProbeError,projection.DiscoveryError,
            subprocess.TimeoutExpired,urllib.error.URLError) as err:
        print("26.2 STOCK REGISTERED NUMERIC STATE NOT QUALIFIED: "+str(err),file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
