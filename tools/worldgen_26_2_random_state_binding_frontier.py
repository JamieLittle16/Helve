#!/usr/bin/env python3
"""Pin 26.2 RandomState/registry/NoiseRouter *binding shapes* without private source.

This is the precise next boundary after the 480 official direct-seeded
Noise.compute observations. Record which actual official JVM method/field/
constructor shapes exist, and reconcile the exact RandomState entry points
with a private Atlas method/call inventory. No RNG/world-seed simulation,
registry instantiation, worldgen authority or VAR/SEM admission is inferred.

Do not distribute a source archive, jar, Atlas database, body text or bytecode.
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

KIND = "official_26_2_random_state_noise_binding_shape_frontier"
STAGE = "random_state_registry_shape_not_world_seed_admitted"
TAG = "HELVE26_2_SEED_ROUTER_SHAPE"
ROOT = "net.minecraft.world.level.levelgen."
TYPES = (
    ROOT + "RandomState",
    ROOT + "NoiseGeneratorSettings",
    ROOT + "Noises",
    ROOT + "NoiseRouter",
    ROOT + "NoiseRouterData",
    ROOT + "DensityFunction$NoiseHolder",
    ROOT + "DensityFunctions$Noise",
    ROOT + "synth.NormalNoise$NoiseParameters",
    "net.minecraft.core.HolderGetter",
    "net.minecraft.core.Holder",
    "net.minecraft.resources.ResourceKey",
    "net.minecraft.core.registries.Registries",
)
REQUIRED = frozenset((TYPES[0], TYPES[1], TYPES[2], TYPES[3], TYPES[5], TYPES[8]))
# Only selected method names are inspected. The JVM probe does NOT call any
# of these implementations; its method names/erasure signatures are evidence,
# not an independently validated algorithm.
NAMES = frozenset((
    "create", "getOrCreateNoise", "instantiate", "mapAll", "compute",
    "getValue", "noise", "get", "getOrThrow", "lookup", "lookupOrThrow",
    "value", "unwrapKey", "isBound", "direct", "register", "bootstrap",
    "getOrCreateRandom", "noiseRouter", "noiseSettings", "router",
))
FIELD_PREFIXES = ("OVERWORLD", "NOISE", "SHIFT", "TEMPERATURE",
                  "CONTINENTALNESS", "EROSION", "RIDGE", "DEFAULT")
BODY_PINS = {
    "state_create": (TYPES[0], "create", ("NoiseGeneratorSettings", "HolderGetter", "long"),
        "cf52d92bbb7a73f32a72e7480ed98c2d08efdd48f5815b4342e37f8191eaf64f"),
    "state_get_noise": (TYPES[0], "getOrCreateNoise", ("ResourceKey",),
        "056547e13816f7c7dd9a3a82e1acadbbc7e5729da50b3103f28b6d20a115e7ca"),
    "router_map": (TYPES[3], "mapAll", ("Visitor",),
        "61ea5c6e319640ee561342ceeb9833aaf9c832ce3aa296e27a2bc1f965a9897c"),
}
METHOD_LIMIT = 384
MAX_JVM_LINES = 1024
MAX_STDOUT_BYTES = 262144
SHA = re.compile(r"[0-9a-f]{64}\Z")
JAVA_SYMBOL = re.compile(r"[A-Za-z_$][\w$]*\Z")
JAVA_ERASURE = re.compile(r"[\w.$\[\];,/\-]+\Z")
METHOD_KINDS = frozenset(("METHOD", "CTOR", "FIELD"))


class BindingFrontierError(ValueError):
    """An official source, runtime, reflection or admission boundary failed."""


def match_args(signature: str, name: str, types: tuple[str, ...]) -> bool:
    if not signature.startswith(name + "(") or not signature.endswith(")"):
        return False
    body = signature[len(name) + 1:-1].strip()
    args = [] if not body else body.split(",")
    return len(args) == len(types) and all(
        re.search(r"\b" + re.escape(word) + r"\b", part) is not None
        for word, part in zip(types, args)
    )


def atlas_binding(conn: sqlite3.Connection) -> dict:
    """Pin three already observed method bodies, then bound adjacent methods.

    A call inventory gives source-review *targets*, not authority to translate
    an unresolved call, nor a proof of runtime dispatch or seeded output.
    """
    items = {}
    for owner in TYPES:
        rows = projection._exact_type_methods(conn, owner, METHOD_LIMIT)
        if not rows:
            if owner in REQUIRED:
                raise BindingFrontierError("mandatory source type/methods absent: " + owner)
            items[owner] = {"status": "not_indexed", "methods": []}
            continue
        candidates = [row for row in rows if row["name"] in NAMES]
        if len(candidates) > 96:
            raise BindingFrontierError("unbounded selected source methods: " + owner)
        records = []
        signatures = set()
        for row in candidates:
            signature = str(row["signature"])
            if signature in signatures:
                raise BindingFrontierError("duplicate exact source declaration: " + owner)
            signatures.add(signature)
            template = source_probe.record_template(
                conn, row, "INDEX-WORLDGEN-262-RANDOMSTATE")
            source = template["source"]
            if source["type"] != owner or source["signature"] != signature:
                raise BindingFrontierError("Atlas source identity mismatch: " + owner)
            body = source["body_sha256"]
            normalized = source["normalized_sha256"]
            if any(x is not None and (not isinstance(x, str) or not SHA.fullmatch(x))
                   for x in (body, normalized)):
                raise BindingFrontierError("malformed Atlas SHA-256: " + owner)
            calls = projection._call_inventory(conn, int(row["id"]))
            records.append({
                "name": str(row["name"]),
                "signature": signature,
                "body_sha256": body,
                "normalized_sha256": normalized,
                "call_sites": calls["call_sites"],
                "unresolved_call_sites": calls["unresolved_call_sites"],
                "reviewed": False,
            })
        items[owner] = {"status": "indexed_not_reviewed", "methods": records}
    for label, (owner, name, arg_types, expected) in BODY_PINS.items():
        matches = [row for row in items[owner]["methods"]
                   if match_args(row["signature"], name, arg_types)]
        if len(matches) != 1 or matches[0]["body_sha256"] != expected:
            raise BindingFrontierError("source body or exact method signature changed: " + label)
    return items


# Intentionally original Java reflection only: no copied Mojang source,
# bytecode, registry values or method invocations beyond bootstrap.
JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.*;
public final class HelveRandomStateBindingShape {
  private static final PrintStream RESULT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);
  private static final String ROOT = "net.minecraft.world.level.levelgen.";
  private static final String[] TYPES = {
      ROOT+"RandomState", ROOT+"NoiseGeneratorSettings", ROOT+"Noises",
      ROOT+"NoiseRouter", ROOT+"NoiseRouterData",
      ROOT+"DensityFunction$NoiseHolder", ROOT+"DensityFunctions$Noise",
      ROOT+"synth.NormalNoise$NoiseParameters",
      "net.minecraft.core.HolderGetter", "net.minecraft.core.Holder",
      "net.minecraft.resources.ResourceKey", "net.minecraft.core.registries.Registries"
  };
  private static final Set<String> NAMES = Set.of(
      "create","getOrCreateNoise","instantiate","mapAll","compute",
      "getValue","noise","get","getOrThrow","lookup","lookupOrThrow",
      "value","unwrapKey","isBound","direct","register","bootstrap",
      "getOrCreateRandom","noiseRouter","noiseSettings","router");
  private static final String[] FIELD_PREFIXES = {
      "OVERWORLD","NOISE","SHIFT","TEMPERATURE",
      "CONTINENTALNESS","EROSION","RIDGE","DEFAULT"
  };
  private static String args(Class<?>[] types) {
    if (types.length==0) return "-";
    return Arrays.stream(types).map(Class::getName).collect(Collectors.joining(","));
  }
  private static String staticKind(int mod) {
    return Modifier.isStatic(mod) ? "static" : "instance";
  }
  private static void result(int index, String... cells) {
    RESULT.println("HELVE26_2_SEED_ROUTER_SHAPE|"+index+"|"+
        String.join("|",cells));
  }
  public static void main(String[] ignored) throws Exception {
    Class<?> constants=Class.forName("net.minecraft.SharedConstants");
    Method detect=constants.getMethod("tryDetectVersion");
    if (!Modifier.isStatic(detect.getModifiers()) || detect.getParameterCount()!=0)
      throw new IllegalStateException("unexpected version startup");
    detect.invoke(null);
    Class<?> bootstrap=Class.forName("net.minecraft.server.Bootstrap");
    Method boot=bootstrap.getMethod("bootStrap");
    if (!Modifier.isStatic(boot.getModifiers()) || boot.getParameterCount()!=0)
      throw new IllegalStateException("unexpected bootstrap startup");
    boot.invoke(null);

    ClassLoader loader=HelveRandomStateBindingShape.class.getClassLoader();
    for (int i=0;i<TYPES.length;i++) {
      Class<?> type;
      try { type=Class.forName(TYPES[i],false,loader); }
      catch (ClassNotFoundException absent) {
        result(i,"TYPE",TYPES[i],"absent");
        continue;
      }
      result(i,"TYPE",TYPES[i],"present");
      SortedSet<String> observed=new TreeSet<>();
      for (Method method:type.getDeclaredMethods()) {
        if (!NAMES.contains(method.getName()) || method.isSynthetic()) continue;
        observed.add(String.join("|","METHOD",method.getName(),
            method.getReturnType().getName(),
            staticKind(method.getModifiers()),args(method.getParameterTypes())));
      }
      for (Constructor<?> ctor:type.getDeclaredConstructors()) {
        if (ctor.isSynthetic()) continue;
        observed.add("CTOR|init|-|instance|"+args(ctor.getParameterTypes()));
      }
      for (Field field:type.getDeclaredFields()) {
        if (field.isSynthetic()) continue;
        boolean relevant=false;
        for (String prefix:FIELD_PREFIXES)
          if (field.getName().startsWith(prefix)) relevant=true;
        if (!relevant) continue;
        observed.add(String.join("|","FIELD",field.getName(),
            field.getType().getName(),staticKind(field.getModifiers()),"-"));
      }
      if (observed.size()>96)
        throw new IllegalStateException("unbounded selected reflection member inventory");
      for (String entry:observed) RESULT.println(
          "HELVE26_2_SEED_ROUTER_SHAPE|"+i+"|"+entry);
    }
  }
}
"""


def parse_runtime(output: str) -> dict:
    if len(output.encode("utf-8")) > MAX_STDOUT_BYTES:
        raise BindingFrontierError("official runtime output exceeds bound")
    lines = output.splitlines()
    if len(lines) > MAX_JVM_LINES:
        raise BindingFrontierError("official runtime output has too many lines")
    tagged = [line for line in lines if line.startswith(TAG + "|")]
    if not tagged:
        raise BindingFrontierError("official reflection emitted no tagged records")
    found: dict[str, dict] = {}
    ordered: dict[int, list[str]] = {i: [] for i in range(len(TYPES))}
    last = -1
    for line in tagged:
        cells = line.split("|")
        if len(cells) not in (5, 7) or cells[0] != TAG or not cells[1].isdigit():
            raise BindingFrontierError("invalid tagged 26.2 runtime reflection row")
        index = int(cells[1])
        if index >= len(TYPES) or index < last:
            raise BindingFrontierError("wrong official reflection type ordering")
        last = index
        if len(cells) == 5:
            if cells[2] != "TYPE" or cells[3] != TYPES[index] or cells[4] not in ("present", "absent"):
                raise BindingFrontierError("unexpected runtime class identity")
            if TYPES[index] in found or ordered[index]:
                raise BindingFrontierError("duplicate/out-of-order runtime class declaration")
            found[TYPES[index]] = {"status": cells[4], "members": []}
        else:
            if cells[2] not in METHOD_KINDS or TYPES[index] not in found or found[TYPES[index]]["status"] != "present":
                raise BindingFrontierError("unexpected member from unobserved JVM class")
            kind, name, result_type, linkage, args = cells[2:]
            if not JAVA_SYMBOL.fullmatch(name) or not JAVA_ERASURE.fullmatch(result_type) \
                or linkage not in ("static", "instance") or not JAVA_ERASURE.fullmatch(args):
                raise BindingFrontierError("malformed JVM member identity")
            if kind == "CTOR" and (name, result_type, linkage) != ("init", "-", "instance"):
                raise BindingFrontierError("malformed JVM constructor")
            if kind == "FIELD" and args != "-":
                raise BindingFrontierError("JVM field unexpectedly has parameters")
            member = "|".join(cells[2:])
            if member in ordered[index] or (ordered[index] and member <= ordered[index][-1]):
                raise BindingFrontierError("duplicate/unsorted JVM reflection member")
            ordered[index].append(member)
            if len(ordered[index]) > 96:
                raise BindingFrontierError("unbounded JVM member inventory")
            found[TYPES[index]]["members"].append({
                "kind": kind, "name": name, "return_or_type": result_type,
                "linkage": linkage, "erased_args": args,
            })
    if set(found) != set(TYPES) or any(found[t]["status"] != "present" for t in REQUIRED):
        raise BindingFrontierError("official registry or RandomState class missing")
    for name, method_name, type_words in (
        (TYPES[0], "create", ("NoiseGeneratorSettings", "HolderGetter", "long")),
        (TYPES[0], "getOrCreateNoise", ("ResourceKey",)),
        (TYPES[3], "mapAll", ("Visitor",)),
    ):
        matches = [
            member for member in found[name]["members"]
            if member["kind"] == "METHOD" and member["name"] == method_name
            and all(word in member["erased_args"] for word in type_words)
        ]
        if len(matches) != 1:
            raise BindingFrontierError("official runtime signature not independently identified: " + method_name)
    return found


def runtime_shape(server: Path, *, timeout: int = 120) -> dict:
    with tempfile.TemporaryDirectory(prefix="helve-world-seed-shapes-262-") as folder:
        home = Path(folder)
        classpath = official.extract_classpath(server, home / "classpath")
        source = home / "HelveRandomStateBindingShape.java"
        source.write_text(JAVA_PROBE, encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(home), str(source)],
            text=True, capture_output=True, check=False, timeout=timeout)
        if compiled.returncode:
            raise BindingFrontierError("original Java reflection did not compile: " + compiled.stderr[:1400])
        run = subprocess.run(
            ["java", "-Xmx512m", "-cp", os.pathsep.join([str(home), *(str(p) for p in classpath)]),
             "HelveRandomStateBindingShape"],
            text=True, capture_output=True, check=False, timeout=timeout)
        if run.returncode:
            raise BindingFrontierError("pinned JVM RandomState shape NOT resolved: " + run.stderr[:1600])
        return parse_runtime(run.stdout)


def validate(manifest: dict, lock: dict) -> None:
    keys = {
        "schema", "kind", "stage", "minecraft", "protocol", "data_version",
        "source_archive_sha256", "official_server_sha256", "startup",
        "source_atlas", "runtime_reflection", "source_text_included",
        "world_seed_random_state_bound", "independent_var_sem_admitted",
        "production_worldgen_enabled",
    }
    if not isinstance(manifest, dict) or set(manifest) != keys:
        raise BindingFrontierError("wrong RandomState frontier manifest schema")
    fixed = {
        "schema": 1, "kind": KIND, "stage": STAGE,
        "minecraft": "26.2", "protocol": 776, "data_version": 4903,
        "source_archive_sha256": lock["source"]["archive_sha256"],
        "official_server_sha256": lock["runtime"]["server_sha256"],
        "startup": primitive.STARTUP_SEQUENCE,
        "source_text_included": False,
        "world_seed_random_state_bound": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }
    for field, value in fixed.items():
        if type(manifest.get(field)) is not type(value) or manifest[field] != value:
            raise BindingFrontierError("wrong source/protocol or admission field: " + field)
    atlas = manifest["source_atlas"]
    if not isinstance(atlas, dict) or set(atlas) != set(TYPES):
        raise BindingFrontierError("incomplete Atlas registry frontier")
    total = 0
    for owner, group in atlas.items():
        if not isinstance(group, dict) or set(group) != {"status", "methods"}:
            raise BindingFrontierError("wrong Atlas source entry shape")
        if group["status"] not in ("indexed_not_reviewed", "not_indexed"):
            raise BindingFrontierError("source method promoted without VAR/SEM")
        methods = group["methods"]
        if not isinstance(methods, list) or len(methods) > 96 or (
            group["status"] == "not_indexed" and (owner in REQUIRED or methods)
        ):
            raise BindingFrontierError("incomplete or overly broad source inventory")
        known = set()
        for rec in methods:
            if not isinstance(rec, dict) or set(rec) != {
                "name", "signature", "body_sha256", "normalized_sha256",
                "call_sites", "unresolved_call_sites", "reviewed",
            } or rec["reviewed"] is not False:
                raise BindingFrontierError("invalid or independently-admitted source method")
            if not isinstance(rec["name"], str) or rec["name"] not in NAMES \
                or not isinstance(rec["signature"], str) or rec["signature"] in known:
                raise BindingFrontierError("ambiguous Atlas method signature")
            known.add(rec["signature"])
            for key in ("body_sha256", "normalized_sha256"):
                value = rec[key]
                if value is not None and (not isinstance(value, str) or not SHA.fullmatch(value)):
                    raise BindingFrontierError("invalid method body hash")
            if not (type(rec["call_sites"]) is int and type(rec["unresolved_call_sites"]) is int
                    and 0 <= rec["unresolved_call_sites"] <= rec["call_sites"] <= 4096):
                raise BindingFrontierError("invalid source callsite counts")
        total += len(methods)
    if total > len(TYPES) * 96:
        raise BindingFrontierError("unbounded RandomState source inventory")
    for label, (owner, name, args, digest) in BODY_PINS.items():
        matches = [rec for rec in atlas[owner]["methods"]
                   if match_args(rec["signature"], name, args)]
        if len(matches) != 1 or matches[0]["body_sha256"] != digest:
            raise BindingFrontierError("invalid pinned seed/router source method " + label)
    runtime = manifest["runtime_reflection"]
    if not isinstance(runtime, dict) or set(runtime) != set(TYPES):
        raise BindingFrontierError("wrong JVM classes")
    serialized = []
    for index, owner in enumerate(TYPES):
        item = runtime[owner]
        if not isinstance(item, dict) or set(item) != {"status", "members"} \
            or item["status"] not in ("absent", "present") or not isinstance(item["members"], list):
            raise BindingFrontierError("invalid JVM reflection type")
        serialized.append("|".join((TAG, str(index), "TYPE", owner, item["status"])))
        for entry in item["members"]:
            if not isinstance(entry, dict) or set(entry) != {
                "kind", "name", "return_or_type", "linkage", "erased_args",
            }:
                raise BindingFrontierError("malformed reflected JVM member")
            serialized.append("|".join((TAG, str(index), entry["kind"], entry["name"],
                entry["return_or_type"], entry["linkage"], entry["erased_args"])))
    if parse_runtime("\n".join(serialized)) != runtime:
        raise BindingFrontierError("JVM method erasure, order or ownership disagreement")


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise BindingFrontierError("not source-locked Minecraft 26.2")
    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source, lock)
        atlas = atlas_binding(conn)
    finally:
        conn.close()
    server_sha = official.sha256_file(server)
    if server_sha != pin["runtime"]["server_sha256"]:
        raise BindingFrontierError("official server jar fingerprint changed")
    runtime = runtime_shape(server)
    manifest = {
        "schema": 1, "kind": KIND, "stage": STAGE, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "startup": primitive.STARTUP_SEQUENCE,
        "source_atlas": atlas, "runtime_reflection": runtime,
        "source_text_included": False, "world_seed_random_state_bound": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }
    validate(manifest, pin)
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as target:
        target.write(encoded)
    return {
        "output": str(destination), "source_free_sha256": hashlib.sha256(encoded).hexdigest(),
        "jvm_types": len(TYPES), "atlas_selected_methods":
            sum(len(row["methods"]) for row in atlas.values()),
        "world_seed_random_state_bound": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--source", type=Path, default=primitive.SOURCE)
    args.add_argument("--db", type=Path, default=primitive.DB)
    args.add_argument("--lock", type=Path, default=primitive.LOCK)
    args.add_argument("--cache", type=Path, default=primitive.CACHE)
    args.add_argument("--server-jar", type=Path)
    args.add_argument("--output", type=Path, required=True)
    options = args.parse_args(argv)
    try:
        server = options.server_jar
        if server is None:
            resolved, _ = official.resolve("26.2", options.cache)
            server = resolved["server"][0]
        print(json.dumps(capture(source=options.source, db=options.db,
            lock=options.lock, server=server, output=options.output), sort_keys=True))
    except (BindingFrontierError, OSError, ValueError, TypeError, KeyError,
            sqlite3.Error, source_probe.ProbeError, projection.DiscoveryError,
            subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(f"OFFICIAL 26.2 RANDOMSTATE/REGISTRY SHAPE NOT RESOLVED: {error}",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
