#!/usr/bin/env python3
"""Resolve official 26.2 density factory *runtime delegate classes* and router Atlas roots.

This is a one-shot, source-free next-implementation frontier, NOT automatic
VAR/SEM review or code generation. The official 26.2 JVM identifies actual
implementation/compute-owner types; the pinned, private Atlas supplies their
structural source identities and call inventories. No official source snippets,
bytecode, raw archive, world chunk or production permissions are exported.
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

KIND = "official_26_2_density_delegate_router_frontier"
ROOT_TYPES = (
    # Existing, confirmed factory/compute roots.
    "net.minecraft.world.level.levelgen.DensityFunction",
    "net.minecraft.world.level.levelgen.DensityFunctions",
    # Plausible 26.2 router pipeline types; optional because their names
    # are not yet pinned by the actual 26.2 Atlas in this frontier.
    "net.minecraft.world.level.levelgen.NoiseRouter",
    "net.minecraft.world.level.levelgen.NoiseRouterData",
    "net.minecraft.world.level.levelgen.NoiseChunk",
    "net.minecraft.world.level.levelgen.NoiseSettings",
    "net.minecraft.world.level.levelgen.RandomState",
    "net.minecraft.data.worldgen.NoiseRouterData",
)
REQUIRED_ROOTS = frozenset(ROOT_TYPES[:2])
DENSITY_NESTED_PREFIX = primitive.DENSITY + "$"
PROFILES = tuple(composed.PROFILES)
MAX_METHODS_PER_TYPE = 512
MAX_NESTED_TYPES = 192
MAX_REVIEW_METHODS = 2048
CANDIDATE_METHODS = frozenset({
    "compute", "fillArray", "mapAll", "minValue", "maxValue", "add", "mul",
    "noise", "shift", "shiftA", "shiftB", "shiftedNoise", "create",
    "instantiate", "getOrCreateNoise", "getNoise", "getOrCreateRandom",
    "router", "finalDensity", "initialDensityWithoutJaggedness",
    "createNoiseRouter", "getAquifer", "createNoiseChunk",
})
# Already *observed* and frozen; refuse to capture against a different
# factory source even if the method name/signature still matches.
COMPOSITION_BODY_PINS = {
    "add_factory": "aff60df9dc11f0e52d061660cf39684dfd671e214ab185174a293ce96ddebe58",
    "mul_factory": "c5d5aaa53f8650d9068362c193487625eeeb057633eaafb0142651a4cc29d7f1",
}
JAVA_CLASS = re.compile(r"net\.minecraft(?:\.[A-Za-z_$][\w$]*)+\Z")
METHOD_HASH = re.compile(r"[0-9a-f]{64}\Z")


class DelegateFrontierError(ValueError):
    """Source, runtime, selected class, or bounded index did not verify."""


# Only factory *objects* and actual compute declaring owners are observed.
# No Minecraft math or original methods are copied or implemented in Java.
JAVA_PROBE = r"""import java.lang.reflect.*;
import java.util.*;
public final class HelveDensityDelegateTypes {
  static double number(String bits) {
    return Double.longBitsToDouble(Long.parseUnsignedLong(bits.substring(2), 16));
  }
  static Method exactStatic(Class<?> owner, String name, Class<?> result, Class<?>... args)
      throws Exception {
    Method m = owner.getMethod(name, args);
    if (!Modifier.isStatic(m.getModifiers()) || m.getReturnType() != result)
      throw new IllegalStateException("26.2 factory signature mismatch: " + name);
    return m;
  }
  static void emit(String label, Object instance, Class<?> context) throws Exception {
    Class<?> concrete = instance.getClass();
    Method compute = concrete.getMethod("compute", context);
    String superName = concrete.getSuperclass() == null
        ? "-" : concrete.getSuperclass().getName();
    System.out.println(label + "\t" + concrete.getName() + "\t" +
        compute.getDeclaringClass().getName() + "\t" + superName);
  }
  public static void main(String[] unused) throws Exception {
    Class<?> shared = Class.forName("net.minecraft.SharedConstants");
    Method detect = shared.getMethod("tryDetectVersion");
    if (!Modifier.isStatic(detect.getModifiers()) || detect.getParameterCount() != 0)
      throw new IllegalStateException("invalid version detection");
    detect.invoke(null);
    Class<?> bootstrap = Class.forName("net.minecraft.server.Bootstrap");
    Method boot = bootstrap.getMethod("bootStrap");
    if (!Modifier.isStatic(boot.getModifiers()) || boot.getParameterCount() != 0)
      throw new IllegalStateException("invalid bootstrap");
    boot.invoke(null);

    Class<?> density = Class.forName("net.minecraft.world.level.levelgen.DensityFunction");
    Class<?> context = Class.forName("net.minecraft.world.level.levelgen.DensityFunction$FunctionContext");
    Class<?> funcs = Class.forName("net.minecraft.world.level.levelgen.DensityFunctions");
    Method constant = exactStatic(funcs, "constant", density, double.class);
    Method gradient = exactStatic(funcs, "yClampedGradient", density,
        int.class, int.class, double.class, double.class);
    Method add = exactStatic(funcs, "add", density, density, density);
    Method mul = exactStatic(funcs, "mul", density, density, density);

    Object zero = constant.invoke(null, number("0x8000000000000000"));
    Object half = constant.invoke(null, number("0x3fe0000000000000"));
    Object world = gradient.invoke(null, -64, 320,
        number("0xbff0000000000000"), number("0x3ff0000000000000"));
    Object reverse = gradient.invoke(null, -30, 17,
        number("0x3fe0000000000000"), number("0xbfe8000000000000"));
    emit("add_gradients", add.invoke(null, world, reverse), context);
    emit("mul_gradients", mul.invoke(null, world, reverse), context);
    emit("add_zero_left", add.invoke(null, zero, world), context);
    emit("add_zero_right", add.invoke(null, world, zero), context);
    emit("mul_zero_left", mul.invoke(null, zero, world), context);
    emit("mul_zero_right", mul.invoke(null, world, zero), context);
    emit("add_self", add.invoke(null, world, world), context);
    emit("mul_half", mul.invoke(null, world, half), context);
  }
}
"""


def parse_runtime_output(output: str) -> dict[str, dict[str, str]]:
    """Require eight exact profile identities, nonempty exact JVM class names."""
    rows = output.splitlines()
    if len(rows) != len(PROFILES):
        raise DelegateFrontierError(f"official reflection produced {len(rows)} classes, expected 8")
    result = {}
    for profile, line in zip(PROFILES, rows, strict=True):
        cells = line.split("\t")
        if len(cells) != 4 or cells[0] != profile:
            raise DelegateFrontierError(f"incorrect runtime profile order or shape: {profile}")
        concrete, compute, parent = cells[1:]
        if not JAVA_CLASS.fullmatch(concrete) or not JAVA_CLASS.fullmatch(compute):
            raise DelegateFrontierError(f"invalid 26.2 delegate class identity: {profile}")
        if parent != "-" and not JAVA_CLASS.fullmatch(parent):
            raise DelegateFrontierError(f"invalid 26.2 delegate superclass identity: {profile}")
        if concrete != compute and parent == "-":
            raise DelegateFrontierError(f"unexplained inherited compute owner: {profile}")
        result[profile] = {
            "implementation_class": concrete,
            "compute_declaring_class": compute,
            "superclass": parent,
        }
    return result


def runtime_classes(server: Path, *, timeout: int = 120) -> dict[str, dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix="helve-density-delegates-262-") as folder:
        work = Path(folder)
        classpath = official.extract_classpath(server, work / "classpath")
        java = work / "HelveDensityDelegateTypes.java"
        java.write_text(JAVA_PROBE, encoding="utf-8")
        compiler = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(java)],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if compiler.returncode:
            raise DelegateFrontierError("original reflection bridge failed to compile: " + compiler.stderr[:1200])
        process = subprocess.run(
            ["java", "-Xmx512m", "-cp", os.pathsep.join([str(work), *(str(p) for p in classpath)]),
             "HelveDensityDelegateTypes"],
            text=True, capture_output=True, check=False, timeout=timeout,
        )
        if process.returncode:
            raise DelegateFrontierError("26.2 official delegate inspection failed: " + process.stderr[:1600])
        return parse_runtime_output(process.stdout)


def atlas_types(conn: sqlite3.Connection) -> set[str]:
    """Exact core roots plus bounded literal DensityFunctions nested family."""
    rows = conn.execute(
        "SELECT qualified_name FROM types WHERE qualified_name LIKE ? ORDER BY qualified_name",
        (DENSITY_NESTED_PREFIX + "%",),
    ).fetchall()
    nested = [str(row[0]) for row in rows]
    if len(nested) > MAX_NESTED_TYPES:
        raise DelegateFrontierError("26.2 DensityFunctions nested type inventory exceeds bounded frontier")
    return set(nested)


def method_record(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    template = source_probe.record_template(conn, row, "INDEX-WORLDGEN-26_2-DELEGATE")
    src = template["source"]
    if src["type"] != row["qualified_name"] or src["signature"] != row["signature"]:
        raise DelegateFrontierError("Atlas method identity changed during bound inventory")
    for key in ("body_sha256", "normalized_sha256"):
        if src[key] is not None and (not isinstance(src[key], str) or not METHOD_HASH.fullmatch(src[key])):
            raise DelegateFrontierError(f"invalid Atlas {key} for {src['type']}")
    return {
        "owner": str(src["type"]),
        "signature": str(src["signature"]),
        "body_sha256": src["body_sha256"],
        "normalized_sha256": src["normalized_sha256"],
        "atlas_observed_hazards": template["atlas_observed_hazards"],
        "atlas_classifications": template["classifications"],
        "calls": projection._call_inventory(conn, int(row["id"])),
        "reviewed": False,
    }


def inventory(conn: sqlite3.Connection, runtime: dict[str, dict[str, str]]) -> dict:
    nested = atlas_types(conn)
    known = nested | set(ROOT_TYPES)
    used = {v["implementation_class"] for v in runtime.values()} | {
        v["compute_declaring_class"] for v in runtime.values()
    }
    if not used <= known:
        raise DelegateFrontierError("runtime classes outside pinned density family/root targets: " +
                                    ", ".join(sorted(used - known)))
    # Distinguish guessed optional root names from actual source type matches.
    requested = sorted(set(ROOT_TYPES) | used | nested)
    results = []
    count = 0
    observed_methods = set()
    for name in requested:
        types = conn.execute(projection._TYPE_SELECT, (name,)).fetchall()
        if len(types) > 1:
            raise DelegateFrontierError(f"ambiguous Atlas root type {name}: {len(types)}")
        if not types:
            if name in REQUIRED_ROOTS or name in used:
                raise DelegateFrontierError(f"missing mandatory official runtime/Atlas root {name}")
            results.append({"type": name, "status": "not_present_in_pinned_atlas", "methods": []})
            continue
        methods = projection._exact_type_methods(conn, name, MAX_METHODS_PER_TYPE)
        # Preserve all methods on real runtime compute owners, specifically
        # their compute declaration and reached targets. Else collect the
        # small explicit density/router API family, not arbitrary source.
        selected = [
            row for row in methods
            if name in used or row["name"] in CANDIDATE_METHODS
        ]
        count += len(selected)
        if count > MAX_REVIEW_METHODS:
            raise DelegateFrontierError("26.2 density method frontier exceeds bounded index budget")
        source_methods = [method_record(conn, row) for row in selected]
        if name in {v["compute_declaring_class"] for v in runtime.values()}:
            qualified = [m for m in source_methods
                         if m["signature"].startswith("compute(")
                         and "FunctionContext" in m["signature"]
                         and m["body_sha256"] is not None]
            if len(qualified) != 1:
                raise DelegateFrontierError(f"official runtime compute source method ambiguous: {name}")
            observed_methods.add(name)
        results.append({"type": name, "status": "indexed_not_reviewed",
                        "method_count": len(methods), "methods": source_methods})
    if observed_methods != {v["compute_declaring_class"] for v in runtime.values()}:
        raise DelegateFrontierError("incomplete 26.2 compute delegate inventory")
    return {"types": results, "nested_density_type_count": len(nested),
            "selected_method_count": count}


def validate(manifest: dict, lock: dict) -> None:
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema", "kind", "minecraft", "protocol", "data_version", "stage",
        "source_archive_sha256", "official_server_sha256", "runtime_startup_sequence",
        "composition_factories", "runtime_profiles", "atlas_frontier",
        "source_text_included", "independent_var_sem_admitted", "production_worldgen_enabled",
    }:
        raise DelegateFrontierError("wrong source-free frontier fields")
    required = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "stage": "density_router_delegate_discovery",
        "source_archive_sha256": lock["source"]["archive_sha256"],
        "official_server_sha256": lock["runtime"]["server_sha256"],
        "runtime_startup_sequence": primitive.STARTUP_SEQUENCE,
        "source_text_included": False, "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    for name, want in required.items():
        if type(manifest.get(name)) is not type(want) or manifest[name] != want:
            raise DelegateFrontierError(f"wrong target/provenance/admission field: {name}")
    if manifest["composition_factories"] != COMPOSITION_BODY_PINS:
        raise DelegateFrontierError("unverified add/mul factory source identities")
    profiles = manifest["runtime_profiles"]
    if not isinstance(profiles, dict) or set(profiles) != set(PROFILES):
        raise DelegateFrontierError("missing or substituted runtime profile classes")
    # Validates shape, order and class names without trusting runtime metadata.
    lines = "\n".join(
        "\t".join((p, profiles[p]["implementation_class"], profiles[p]["compute_declaring_class"],
                  profiles[p]["superclass"])) for p in PROFILES
    )
    if parse_runtime_output(lines) != profiles:
        raise DelegateFrontierError("runtime profile identities changed")
    indexed = manifest["atlas_frontier"]
    if not isinstance(indexed, dict) or set(indexed) != {
        "types", "nested_density_type_count", "selected_method_count",
    }:
        raise DelegateFrontierError("malformed source index")
    if not isinstance(indexed["types"], list) or not 2 <= len(indexed["types"]) <= MAX_NESTED_TYPES + len(ROOT_TYPES):
        raise DelegateFrontierError("unbounded source index")
    if not isinstance(indexed["nested_density_type_count"], int) or not 0 <= indexed["nested_density_type_count"] <= MAX_NESTED_TYPES:
        raise DelegateFrontierError("invalid nested density inventory size")
    if not isinstance(indexed["selected_method_count"], int) or not 0 <= indexed["selected_method_count"] <= MAX_REVIEW_METHODS:
        raise DelegateFrontierError("invalid selected method count")
    indexed_names = set()
    visited = 0
    for item in indexed["types"]:
        if not isinstance(item, dict) or not isinstance(item.get("type"), str) or item["type"] in indexed_names:
            raise DelegateFrontierError("duplicate/invalid source type identity")
        indexed_names.add(item["type"])
        if item.get("status") not in {"not_present_in_pinned_atlas", "indexed_not_reviewed"}:
            raise DelegateFrontierError("unreviewed type promoted without source admission")
        if not isinstance(item.get("methods"), list):
            raise DelegateFrontierError("malformed method inventory")
        if item["status"] == "not_present_in_pinned_atlas":
            if item["type"] in REQUIRED_ROOTS or item["type"] in {
                value[k] for value in profiles.values()
                for k in ("implementation_class", "compute_declaring_class")
            } or item["methods"]:
                raise DelegateFrontierError("mandatory compute source treated as optional")
        for method in item["methods"]:
            if not isinstance(method, dict) or method.get("owner") != item["type"] or method.get("reviewed") is not False:
                raise DelegateFrontierError("unsupported method or admission status")
            if not isinstance(method.get("signature"), str) or not method["signature"]:
                raise DelegateFrontierError("missing source method signature")
            for digest in ("body_sha256", "normalized_sha256"):
                value = method.get(digest)
                if value is not None and (not isinstance(value, str) or not METHOD_HASH.fullmatch(value)):
                    raise DelegateFrontierError("invalid source body/hash")
            visited += 1
    if visited != indexed["selected_method_count"]:
        raise DelegateFrontierError("incomplete method inventory")
    if not REQUIRED_ROOTS <= indexed_names:
        raise DelegateFrontierError("missing official core density roots")
    if not {v["compute_declaring_class"] for v in profiles.values()} <= indexed_names:
        raise DelegateFrontierError("unindexed official compute delegate")


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise DelegateFrontierError("wrong pinned Minecraft version/protocol/data version")
    conn = vanilla_atlas.connect_db(db)
    try:
        sha = source_probe.require_pinned_source(conn, source, lock)
        factories = composed.bound_composition_methods(conn)
        for name, expected in COMPOSITION_BODY_PINS.items():
            if factories[name]["body_sha256"] != expected:
                raise DelegateFrontierError(f"changed official 26.2 composition factory source: {name}")
        runtime_sha = official.sha256_file(server)
        if runtime_sha != pin["runtime"]["server_sha256"]:
            raise DelegateFrontierError("unknown official server runtime")
        classes = runtime_classes(server)
        selected = inventory(conn, classes)
    finally:
        conn.close()
    manifest = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "stage": "density_router_delegate_discovery",
        "source_archive_sha256": sha,
        "official_server_sha256": runtime_sha,
        "runtime_startup_sequence": primitive.STARTUP_SEQUENCE,
        "composition_factories": COMPOSITION_BODY_PINS,
        "runtime_profiles": classes,
        "atlas_frontier": selected,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    validate(manifest, pin)
    data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    return {
        "output": str(destination), "types": len(selected["types"]),
        "selected_methods": selected["selected_method_count"],
        "source_free_sha256": hashlib.sha256(data).hexdigest(),
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=primitive.DB)
    parser.add_argument("--lock", type=Path, default=primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=primitive.CACHE)
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
    except (DelegateFrontierError, composed.CompositionCaptureError, primitive.DensityCaptureError,
            OSError, ValueError, TypeError, KeyError, sqlite3.Error,
            projection.DiscoveryError, source_probe.ProbeError,
            subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(f"OFFICIAL 26.2 DENSITY DELEGATES NOT RESOLVED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
