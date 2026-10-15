#!/usr/bin/env python3
"""Source-reviewed but not source-admitted 26.2 runtime heightmap state oracle.

The official server owns all 32,366 canonical global state IDs. Resolve
per-state predicates by invoking the official runtime, never guessing
blocksMotion from section counters, collision flags or block names.

This is a *candidate* evidence producer only. The independent Atlas
VAR/SEM source-admission and generation decision remain separately gated.
No Java source, JAR or runtime state table is checked into the repository.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import urllib.error

import official_state_data as official

VERSION = "26.2"
EXPECTED_STATE_COUNT = 32_366
SOURCE_ARCHIVE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
SOURCE_FILE_SHA256 = {
    "Heightmap.java": "399cd25b1d00b9537a96486d01ef90f4095dfb5f01a5b007925a8893fac95801",
    "BlockBehaviour.java": "598050c5e9c9064b8fc95f91c84d925695b573830eca129b81a964e1f171e572",
    "FluidState.java": "f861b76280724832b3fe348895f6d33f125b15c146eea51bfbfc9fe30f2a0b7f",
    "LeavesBlock.java": "327c0f09e58c457c4cd02d6bdbfb03242eedcba13263ba55727cc900d073ba39",
}

def java_probe(mapping_text: str | None) -> str:
    cls = {
        **official.CLASS_NAMES,
        "leaves": "net.minecraft.world.level.block.LeavesBlock",
    }
    if mapping_text is None:
        classes = cls
        field = "BLOCK_STATE_REGISTRY"
        methods = {
            "detect_version": "tryDetectVersion",
            "bootstrap": "bootStrap",
            "get_id": "getId",
            "is_air": "isAir",
            "blocks_motion": "blocksMotion",
            "get_fluid": "getFluidState",
            "fluid_empty": "isEmpty",
            "get_block": "getBlock",
        }
    else:
        c, f, m = official.parse_mappings(mapping_text)
        classes = {key: c[value] for key, value in cls.items()}
        field = f[(cls["block"], "BLOCK_STATE_REGISTRY")]
        method_owners = {
            "detect_version": (cls["shared_constants"], "tryDetectVersion"),
            "bootstrap": (cls["bootstrap"], "bootStrap"),
            "get_id": (cls["block"], "getId"),
            "is_air": (cls["state_base"], "isAir"),
            "blocks_motion": (cls["state_base"], "blocksMotion"),
            "get_fluid": (cls["state_base"], "getFluidState"),
            "fluid_empty": (cls["fluid_state"], "isEmpty"),
            "get_block": (cls["state_base"], "getBlock"),
        }
        methods = {
            key: official.unique_method(m, owner, name)
            for key, (owner, name) in method_owners.items()
        }

    # Class names and members come solely from the pinned official
    # declarations/mappings, not user-controlled network strings.
    return f'''import java.lang.reflect.*;
public final class HelveHeightmapProbe {{
  private static Method method(Class<?> owner, String name) throws Exception {{
    Method method = owner.getMethod(name);
    method.setAccessible(true);
    return method;
  }}
  private static Method stateId(Class<?> owner, String name) throws Exception {{
    for (Method method : owner.getMethods()) {{
      if (method.getName().equals(name) &&
          Modifier.isStatic(method.getModifiers()) &&
          method.getParameterCount() == 1) {{
        method.setAccessible(true);
        return method;
      }}
    }}
    throw new NoSuchMethodException(name);
  }}
  public static void main(String[] args) throws Exception {{
    java.io.PrintStream output = System.out;
    method(Class.forName("{classes['shared_constants']}"), "{methods['detect_version']}").invoke(null);
    method(Class.forName("{classes['bootstrap']}"), "{methods['bootstrap']}").invoke(null);
    Class.forName("{classes['blocks']}", true, HelveHeightmapProbe.class.getClassLoader());
    Class<?> block = Class.forName("{classes['block']}");
    Field registryField = block.getField("{field}");
    registryField.setAccessible(true);
    Object registry = registryField.get(null);
    Method idOf = stateId(block, "{methods['get_id']}");
    Class<?> stateBase = Class.forName("{classes['state_base']}");
    Method isAir = method(stateBase, "{methods['is_air']}");
    Method blocksMotion = method(stateBase, "{methods['blocks_motion']}");
    Method getFluid = method(stateBase, "{methods['get_fluid']}");
    Method getBlock = method(stateBase, "{methods['get_block']}");
    Method isFluidEmpty = method(Class.forName("{classes['fluid_state']}"), "{methods['fluid_empty']}");
    Class<?> leavesClass = Class.forName("{classes['leaves']}");
    for (Object state : (Iterable<?>)registry) {{
      int id = ((Number)idOf.invoke(null, state)).intValue();
      boolean nonAir = !(Boolean)isAir.invoke(state);
      boolean motion = (Boolean)blocksMotion.invoke(state);
      boolean fluid = !(Boolean)isFluidEmpty.invoke(getFluid.invoke(state));
      boolean leaves = leavesClass.isInstance(getBlock.invoke(state));
      output.println(id + "\\t" + (nonAir ? 1 : 0) + "\\t" +
        (motion ? 1 : 0) + "\\t" + (fluid ? 1 : 0) + "\\t" +
        (leaves ? 1 : 0));
    }}
  }}
}}
'''

def parse_probe_output(output: str) -> list[int]:
    """Compact packed flags in vanilla-global-ID order.

    bit0 non-air, bit1 blocksMotion, bit2 fluidNonEmpty, bit3 leaves.
    This is the minimal separate SoA table a future COLD heightmap
    projector could use after independent source/SEM admission.
    """
    seen: dict[int, int] = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) != 5:
            raise ValueError("official heightmap probe line does not have 5 fields")
        raw_id, *raw_flags = fields
        if not raw_id.isdecimal() or any(flag not in ("0", "1") for flag in raw_flags):
            raise ValueError("official heightmap probe row has invalid ID/boolean")
        state_id = int(raw_id)
        if state_id in seen:
            raise ValueError(f"duplicate official state ID {state_id}")
        non_air, motion, fluid, leaves = map(int, raw_flags)
        if (motion or leaves) and not non_air:
            raise ValueError(f"official state {state_id} contradicts air predicate")
        seen[state_id] = non_air | (motion << 1) | (fluid << 2) | (leaves << 3)
    if sorted(seen) != list(range(EXPECTED_STATE_COUNT)):
        raise ValueError(f"official heightmap state ID set is not dense 0..{EXPECTED_STATE_COUNT - 1}")
    return [seen[state_id] for state_id in range(EXPECTED_STATE_COUNT)]

def official_runtime_facts(server: Path, mappings: Path | None) -> list[int]:
    with tempfile.TemporaryDirectory(prefix="helve-heightmap-probe-") as temp:
        work = Path(temp)
        entries = official.extract_classpath(server, work / "classpath")
        mapped_text = mappings.read_text(encoding="utf-8") if mappings else None
        source = work / "HelveHeightmapProbe.java"
        source.write_text(java_probe(mapped_text), encoding="utf-8")
        compile_cmd = ["javac", "-encoding", "UTF-8", "-d", str(work), str(source)]
        compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, check=False)
        if compile_result.returncode:
            raise ValueError(f"official probe compilation failed: {compile_result.stderr}")
        cp = os.pathsep.join((str(work), *(str(entry) for entry in entries)))
        result = subprocess.run(
            ["java", "-cp", cp, "HelveHeightmapProbe"],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise ValueError(f"official probe runtime failed: {result.stderr}")
        return parse_probe_output(result.stdout)

def extract(output: Path, cache: Path, server: Path | None, mappings: Path | None, lock: Path) -> None:
    with lock.open("rb") as stream:
        pin = tomllib.load(stream)
    if server is None:
        resolved, _ = official.resolve(VERSION, cache)
        server = resolved["server"][0]
        if mappings is None and "server_mappings" in resolved:
            mappings = resolved["server_mappings"][0]
    actual_hash = official.sha256_file(server)
    expected_hash = pin["runtime"]["server_sha256"]
    if actual_hash != expected_hash:
        raise ValueError(f"official runtime SHA-256 mismatch: {actual_hash} != {expected_hash}")
    states = official_runtime_facts(server, mappings)
    report = {
        "schema": 1,
        "target": {"minecraft": VERSION, "protocol": 776, "data_version": 4903},
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "source_file_sha256": SOURCE_FILE_SHA256,
        "server_sha256": actual_hash,
        "state_count": len(states),
        "flags_by_vanilla_state_id": states,
        "bit_layout": {
            "non_air": 0, "blocks_motion": 1, "fluid_non_empty": 2, "leaves": 3,
        },
        "heightmap_laws": {
            "WORLD_SURFACE": "non_air",
            "MOTION_BLOCKING": "blocks_motion || fluid_non_empty",
            "MOTION_BLOCKING_NO_LEAVES":
                "(blocks_motion || fluid_non_empty) && !leaves",
        },
        "source_admitted": False,
        "production_admitted": False,
        "gate": "R2C-HEIGHTMAP-STATE-PREDICATES source fingerprint and independent SEM admission",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"source-reviewed COLD candidate: {len(states)} official state facts -> {output}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path(".crucible/vanilla/downloads"))
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--server-mappings", type=Path)
    parser.add_argument("--lock", type=Path, default=Path("vanilla/vanilla.lock.toml"))
    args = parser.parse_args()
    try:
        extract(args.output, args.cache, args.server_jar, args.server_mappings, args.lock)
    except (ValueError, KeyError, OSError, urllib.error.URLError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
