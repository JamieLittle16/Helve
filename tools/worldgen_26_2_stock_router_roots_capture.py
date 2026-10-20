#!/usr/bin/env python3
"""Inspect the REAL bound stock Minecraft 26.2 NoiseRouter's 15 root nodes.

Reuses the original stock-registry/RandomState reflection bridge. Only the
runtime class names and first-level public record density children are
recorded. No density values, graph-equivalence, cache interpolation,
VAR/SEM source-law admission, terrain or production permission is inferred.
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
import vanilla_atlas
import worldgen_26_2_density_primitive_capture as primitive
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_stock_mixed_density_fixture as mixed
import worldgen_26_2_stock_worldseed_heldout_capture as heldout
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

ROOT = Path(__file__).resolve().parents[1]
JAVA_SOURCE = ROOT / "tools/worldgen_java/HelveStockNoiseRouterRoots262.java"
BASE_BRIDGE = stock.JAVA_SOURCE
KIND = "official_26_2_stock_randomstate_router_15_root_frontier"
SEEDS = heldout.SEEDS
N_FIELDS = 15
TAG_HEADER = "HELVE26_2_ROUTER_HEADER|"
TAG_FIELD = "HELVE26_2_ROUTER_FIELD|"
TAG_CHILD = "HELVE26_2_ROUTER_CHILD|"
TAG_FAILURE = "HELVE26_2_ROUTER_FAILURE|"
JAVA_NAME = re.compile(r"net\.minecraft(?:\.[A-Za-z_$][\w$]*)+\Z")
FIELD_NAME = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]{0,100}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
# This is an indexed method identity, not a review of its implementation.
ROUTER_MAP_ALL_SHA256 = "61ea5c6e319640ee561342ceeb9833aaf9c832ce3aa296e27a2bc1f965a9897c"
ROUTER = "net.minecraft.world.level.levelgen.NoiseRouter"
STATE = "net.minecraft.world.level.levelgen.RandomState"


class RouterRootsError(ValueError):
    """The stock 26.2 router root-binding frontier is unqualified."""


def source_methods(conn: sqlite3.Connection) -> dict:
    expected = {
        "router_map_all": (ROUTER, "mapAll", 1),
        "random_state_router": (STATE, "router", 0),
    }
    methods: dict[str, dict] = {}
    for label, (owner, name, count) in expected.items():
        rows = conn.execute(
            "SELECT m.id,m.signature,m.param_count,m.name,t.qualified_name "
            "FROM methods m JOIN types t ON m.type_id=t.id "
            "WHERE t.qualified_name=? AND m.name=? AND m.param_count=?",
            (owner, name, count),
        ).fetchall()
        if len(rows) != 1:
            raise RouterRootsError(f"exact stock 26.2 source method absent/ambiguous: {label}")
        row = rows[0]
        hashes = conn.execute(
            "SELECT body_sha256,normalized_sha256 FROM methods WHERE id=?", (row["id"],)
        ).fetchone()
        if hashes is None or not isinstance(hashes[0], str) or not HASH.fullmatch(hashes[0]) \
           or not isinstance(hashes[1], str) or not HASH.fullmatch(hashes[1]):
            raise RouterRootsError("incomplete source body fingerprint: " + label)
        if label == "router_map_all" and hashes[0] != ROUTER_MAP_ALL_SHA256:
            raise RouterRootsError("original 26.2 NoiseRouter.mapAll source changed")
        methods[label] = {
            "owner": row["qualified_name"], "signature": row["signature"],
            "body_sha256": hashes[0], "normalized_sha256": hashes[1],
            "reviewed": False,
        }
    return methods


def parse_output(stdout: str) -> list[dict]:
    if not isinstance(stdout, str) or len(stdout) > 400_000:
        raise RouterRootsError("unbounded official router JVM stdout")
    lines = stdout.splitlines()
    failures = [v for v in lines if v.startswith(TAG_FAILURE)]
    if failures:
        if len(failures) != 1 or len(failures[0].split("|")) != 5:
            raise RouterRootsError("malformed router tagged JVM failure")
        parts = failures[0].split("|")
        raise RouterRootsError("JVM PHASE: " + parts[1] + "; ROOT: " + parts[2] +
                               "; CAUSE: " + parts[4])
    records = [v for v in lines if v.startswith((
        TAG_HEADER, TAG_FIELD, TAG_CHILD))]
    index = 0
    roots = []
    observed_names = None
    for seed_index, seed in enumerate(SEEDS):
        if index >= len(records):
            raise RouterRootsError("missing stock router seed header")
        fields = records[index].split("|")
        index += 1
        if fields != ["HELVE26_2_ROUTER_HEADER", str(seed_index),
                      str(N_FIELDS), ROUTER]:
            raise RouterRootsError("wrong stock router header / record shape")
        group = []
        for root_index in range(N_FIELDS):
            if index >= len(records):
                raise RouterRootsError("missing bound stock router root")
            items = records[index].split("|")
            index += 1
            if len(items) != 7 or items[:3] != [
                "HELVE26_2_ROUTER_FIELD", str(seed_index), str(root_index)]:
                raise RouterRootsError("wrong/reordered stock NoiseRouter field")
            _, _, _, name, implementation, declared, child_count_raw = items
            if not FIELD_NAME.fullmatch(name) or not JAVA_NAME.fullmatch(implementation) \
               or not JAVA_NAME.fullmatch(declared) or not child_count_raw.isascii() \
               or not child_count_raw.isdecimal() or str(int(child_count_raw)) != child_count_raw \
               or int(child_count_raw) > 32:
                raise RouterRootsError("unqualified class name or first-level child bound")
            children = []
            for child_index in range(int(child_count_raw)):
                if index >= len(records):
                    raise RouterRootsError("missing first-level density child")
                child = records[index].split("|")
                index += 1
                if len(child) != 6 or child[:4] != [
                    "HELVE26_2_ROUTER_CHILD", str(seed_index),
                    str(root_index), str(child_index)] or not FIELD_NAME.fullmatch(child[4]) \
                   or not JAVA_NAME.fullmatch(child[5]):
                    raise RouterRootsError("malformed, missing or reordered density child")
                children.append({"slot": child[4], "implementation_class": child[5]})
            if len({v["slot"] for v in children}) != len(children):
                raise RouterRootsError("duplicate density child record component")
            group.append({
                "field": name, "implementation_class": implementation,
                "compute_declaring_class": declared, "first_level_density_children": children,
            })
        names = tuple(v["field"] for v in group)
        if len(set(names)) != N_FIELDS or (observed_names is not None and names != observed_names):
            raise RouterRootsError("inconsistent named router record roots across seeds")
        observed_names = names
        roots.append({"world_seed_bits": seed, "fields": group})
    if index != len(records):
        raise RouterRootsError("unexpected extra/duplicated tagged router records")
    return roots


def observe(server: Path, *, timeout: int = 240) -> list[dict]:
    if not JAVA_SOURCE.is_file() or not BASE_BRIDGE.is_file():
        raise RouterRootsError("required original reflection bridge absent")
    with tempfile.TemporaryDirectory(prefix="helve-262-router-roots-") as folder:
        work = Path(folder)
        jars = official.extract_classpath(server, work / "classpath")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             str(BASE_BRIDGE), str(JAVA_SOURCE)],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if build.returncode:
            raise RouterRootsError("router reflection bridge did not compile: " +
                                   build.stderr[:1500])
        result = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join([str(work), *(str(j) for j in jars)]),
             "HelveStockNoiseRouterRoots262", "--router-roots-4"],
            input="\n".join(SEEDS)+"\n", text=True, capture_output=True,
            check=False, timeout=timeout,
        )
        if result.returncode:
            try:
                parse_output(result.stdout)
            except RouterRootsError as exc:
                raise RouterRootsError(str(exc)) from exc
            raise RouterRootsError("official router JVM failed: " +
                                   stock.java_failure_detail(result.stderr))
        return parse_output(result.stdout)


def validate(manifest: dict, *, methods: dict) -> None:
    expected = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": frozen.SOURCE_SHA256,
        "official_server_sha256": frozen.SERVER_SHA256,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "original_stock_noise_fixture_sha256": frozen.FIXTURE_SHA256,
        "original_mixed_density_fixture_sha256": mixed.FIXTURE_SHA256,
        "source_methods": methods,
        "world_seeds": list(SEEDS),
        "noise_router_field_count": N_FIELDS,
        "stock_registry_used": True,
        "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False,
        "router_numeric_parity_qualified": False,
        "router_full_graph_qualified": False,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    if not isinstance(manifest, dict) or set(manifest) != set(expected) | {"bound_router_roots"}:
        raise RouterRootsError("wrong router evidence schema")
    for key, value in expected.items():
        if type(manifest.get(key)) is not type(value) or manifest[key] != value:
            raise RouterRootsError("changed router source target / closed gate: " + key)
    roots = manifest["bound_router_roots"]
    if not isinstance(roots, list) or len(roots) != len(SEEDS):
        raise RouterRootsError("incorrect world-seed router count")
    names = None
    for index, item in enumerate(roots):
        if not isinstance(item, dict) or set(item) != {"world_seed_bits", "fields"} \
           or item["world_seed_bits"] != SEEDS[index]:
            raise RouterRootsError("incorrect bound router world-seed order")
        fields = item["fields"]
        if not isinstance(fields, list) or len(fields) != N_FIELDS:
            raise RouterRootsError("incorrect number of bound router fields")
        present = []
        for field in fields:
            if not isinstance(field, dict) or set(field) != {
                "field", "implementation_class", "compute_declaring_class",
                "first_level_density_children",
            } or not all(isinstance(field[k], str) and
                         (FIELD_NAME if k == "field" else JAVA_NAME).fullmatch(field[k])
                         for k in ("field", "implementation_class", "compute_declaring_class")):
                raise RouterRootsError("invalid source-free router field identity")
            children = field["first_level_density_children"]
            if not isinstance(children, list) or len(children) > 32:
                raise RouterRootsError("unbounded router first-level children")
            child_names = []
            for child in children:
                if not isinstance(child, dict) or set(child) != {"slot", "implementation_class"} \
                   or not isinstance(child["slot"], str) or not FIELD_NAME.fullmatch(child["slot"]) \
                   or not isinstance(child["implementation_class"], str) \
                   or not JAVA_NAME.fullmatch(child["implementation_class"]):
                    raise RouterRootsError("invalid stock router first-level child")
                child_names.append(child["slot"])
            if len(set(child_names)) != len(children):
                raise RouterRootsError("repeated density child slot")
            present.append(field["field"])
        if len(set(present)) != N_FIELDS or (names is not None and present != names):
            raise RouterRootsError("stock router field order changed between seeds")
        names = present


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as file:
        pin = tomllib.load(file)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise RouterRootsError("not the locked 26.2 target")
    stock.reference_frontier(frontier, pin)
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        selected = source_methods(conn)
    finally:
        conn.close()
    server_sha = official.sha256_file(server)
    if source_sha != frozen.SOURCE_SHA256 or server_sha != frozen.SERVER_SHA256 \
       or server_sha != pin["runtime"]["server_sha256"]:
        raise RouterRootsError("wrong original official 26.2 archive/runtime")
    result = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "original_stock_noise_fixture_sha256": frozen.FIXTURE_SHA256,
        "original_mixed_density_fixture_sha256": mixed.FIXTURE_SHA256,
        "source_methods": selected,
        "world_seeds": list(SEEDS),
        "noise_router_field_count": N_FIELDS,
        "stock_registry_used": True,
        "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False,
        "router_numeric_parity_qualified": False,
        "router_full_graph_qualified": False,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "bound_router_roots": observe(server),
    }
    validate(result, methods=selected)
    payload = (json.dumps(result, sort_keys=True, indent=2)+"\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as file:
        file.write(payload)
    return {
        "output": str(destination),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "world_seeds": len(SEEDS),
        "bound_density_roots": len(SEEDS)*N_FIELDS,
        "complete_router_qualified": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=primitive.DB)
    parser.add_argument("--lock", type=Path, default=primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=primitive.CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--frontier", type=Path, default=stock.FRONTIER)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            metadata, _ = official.resolve("26.2", args.cache)
            server = metadata["server"][0]
        print(json.dumps(capture(source=args.source, db=args.db, lock=args.lock,
                                 server=server, frontier=args.frontier,
                                 output=args.output), sort_keys=True))
    except (RouterRootsError, OSError, ValueError, KeyError, TypeError,
            sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError) as exc:
        print("STOCK 26.2 ROUTER ROOTS UNQUALIFIED: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
