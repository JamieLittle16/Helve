#!/usr/bin/env python3
"""Collect bounded source-free *control-flow* evidence for official 26.2 biome IDs.

The stock client is SHA-1/size checked from Mojang's official metadata. This
does NOT decompile, commit bytecode, admit semantics or enable runtime biome
IDs. It checks exact instruction-level operation order and preserves source-
free method-code hashes + conditional branch targets for manual VAR/SEM review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import r2c_official_client_registry_inventory as receiver

KIND = "r2c-26_2-official-client-biome-order-branch-frontier-v1"
MAX_CLASS_BYTES = 1_048_576
MAX_DISASSEMBLY_CHARS = 4_000_000
MAX_INSTRUCTIONS = 512
MAX_BRANCHES = 96
# Fixed receiver-reached methods. Never discover random classes by name.
METHODS = (
    ("net.minecraft.client.multiplayer.RegistryDataCollector$ContentsCollector", "append"),
    ("net.minecraft.resources.NetworkRegistryLoadTask", "load"),
    ("net.minecraft.resources.NetworkRegistryLoadTask", "lambda$load$2"),
    ("net.minecraft.util.Util", "sequence"),
    ("net.minecraft.util.Util", "lambda$sequence$0"),
    ("net.minecraft.resources.RegistryLoadTask", "registerElements"),
    ("net.minecraft.core.MappedRegistry", "register"),
)
DECLARATION = re.compile(
    r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;"
)
INSTRUCTION = re.compile(r"^\s*(\d+):\s+([a-z][a-z_0-9]*)\b(.*)$")
BRANCH_TARGET = re.compile(r"^\s*(-?\d+)(?:\s|$)")
TARGET_LIMIT = 512
# Each subsequence is a *necessary structural witness*, never a complete
# semantic proof. The exact JVM instruction fingerprint disambiguates other
# branches and calls, which independent source review must still close.
REQUIRED_CALLS = {
    ("net.minecraft.client.multiplayer.RegistryDataCollector$ContentsCollector", "append"): (
        "Map.computeIfAbsent:", "List.addAll:",
    ),
    ("net.minecraft.resources.NetworkRegistryLoadTask", "load"): (
        "NetworkedRegistryData.elements:", "List.iterator:",
        "List.add:", "Util.sequence:", "CompletableFuture.thenAcceptAsync:",
    ),
    ("net.minecraft.resources.NetworkRegistryLoadTask", "lambda$load$2"): (
        "List.stream:", "registerElements:", "registerTags:",
    ),
    ("net.minecraft.util.Util", "sequence"): (
        "List.isEmpty:", "List.size:", "CompletableFuture.allOf:",
        "CompletableFuture.thenApply:",
    ),
    ("net.minecraft.util.Util", "lambda$sequence$0"): (
        "List.stream:", "Stream.map:", "Stream.toList:",
    ),
    ("net.minecraft.resources.RegistryLoadTask", "registerElements"): (
        "Stream.forEach:",
    ),
    ("net.minecraft.core.MappedRegistry", "register"): (
        "ObjectList.size:", "ObjectList.add:", "Reference2IntMap.put:",
    ),
}


def _target(line: str) -> str:
    return line.split("// ", 1)[1].strip() if "// " in line else ""


def _ordered_subsequence(actual: list[str], required: tuple[str, ...]) -> list[dict]:
    """Each required operation must occur in the prescribed *relative* order."""
    selected: list[dict] = []
    cursor = 0
    for wanted in required:
        indices = [i for i in range(cursor, len(actual)) if wanted in actual[i]]
        if not indices:
            raise ValueError(f"missing or reordered required receiver call: {wanted}")
        idx = indices[0]
        selected.append({"call_index": idx, "symbol": wanted})
        cursor = idx + 1
    return selected


def bounded_method_shape(disassembly: str, class_name: str, method: str) -> dict:
    """Extract one declared method, never include a neighbor's instructions."""
    if len(disassembly) > MAX_DISASSEMBLY_CHARS:
        raise ValueError("oversized official client disassembly")
    lines = disassembly.splitlines()
    headers: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        decl = DECLARATION.fullmatch(line)
        if decl:
            headers.append((i, decl.group(1), line))
    matches = [(i, signature) for i, name, signature in headers if name == method]
    if len(matches) != 1:
        raise ValueError(f"absent/ambiguous exact method: {class_name}#{method}")
    start, signature = matches[0]
    end = next((i for i, _, _ in headers if i > start), len(lines))
    section = lines[start:end]
    if not any(line.strip() == "Code:" for line in section):
        raise ValueError("selected client method has no executable Code")
    instructions: list[tuple[int, str, str]] = []
    for line in section:
        found = INSTRUCTION.match(line)
        if not found:
            continue
        offset = int(found.group(1))
        opcode = found.group(2)
        remainder = found.group(3).strip()
        if instructions and offset <= instructions[-1][0]:
            raise ValueError("client method offsets not strictly increasing")
        instructions.append((offset, opcode, remainder))
        if len(instructions) > MAX_INSTRUCTIONS:
            raise ValueError("client method instruction budget exceeded")
    if not instructions:
        raise ValueError("selected client method has no parseable instructions")
    branch_edges: list[dict] = []
    invocations: list[tuple[int, str, str]] = []
    offsets = {offset for offset, _, _ in instructions}
    for offset, opcode, remainder in instructions:
        if opcode.startswith(("if", "goto", "jsr")):
            found = BRANCH_TARGET.match(remainder)
            if found is None:
                raise ValueError(f"conditional branch missing explicit JVM target at {offset}")
            target = int(found.group(1))
            if target not in offsets:
                raise ValueError(f"conditional branch jumps outside parsed method at {offset}")
            branch_edges.append({"from": offset, "to": target, "opcode": opcode})
            if len(branch_edges) > MAX_BRANCHES:
                raise ValueError("too many client conditional branches")
        if opcode.startswith("invoke"):
            symbol = _target(remainder)
            if not symbol or len(symbol) > 8192:
                raise ValueError(f"missing/oversized symbolic invoke at {offset}")
            invocations.append((offset, opcode, symbol))
    required = REQUIRED_CALLS.get((class_name, method))
    if required is None:
        raise ValueError("method outside exact receiving-client review roots")
    matched = _ordered_subsequence([target for _, _, target in invocations], required)
    checkpoints = [
        {
            "offset": invocations[item["call_index"]][0],
            "opcode": invocations[item["call_index"]][1],
            "expected_symbol": item["symbol"],
            "exact_target_sha256": hashlib.sha256(
                invocations[item["call_index"]][2].encode("utf-8")
            ).hexdigest(),
        }
        for item in matched
    ]
    # Do not ship full disassembly/instruction lists. Hash the selected raw
    # opcode/operand rows to pin human review of *all* instructions, including
    # branch and exceptional paths that a call-only witness cannot inspect.
    fingerprint = hashlib.sha256(
        "\n".join(f"{i}:{op} {rest}" for i, op, rest in instructions).encode()
    ).hexdigest()
    return {
        "class_name": class_name,
        "method_name": method,
        "declaration_sha256": hashlib.sha256(signature.encode()).hexdigest(),
        "instruction_shape_sha256": fingerprint,
        "instruction_count": len(instructions),
        "conditional_branch_edges": branch_edges,
        "return_instruction_offsets": [
            i for i, op, _ in instructions if op.endswith("return") or op == "athrow"
        ],
        "required_ordered_invoke_checkpoints": checkpoints,
        "ordered_callsite_witness_matches": True,
        "all_control_flow_paths_reviewed": False,
        "exception_and_duplicate_semantics_proven": False,
    }


def inspect_client(client: Path) -> list[dict]:
    class_output: dict[str, str] = {}
    with zipfile.ZipFile(client) as jar:
        names = jar.namelist()
        for class_name, _ in METHODS:
            if class_name in class_output:
                continue
            path = class_name.replace(".", "/") + ".class"
            if names.count(path) != 1:
                raise ValueError(f"missing/duplicate official client class: {class_name}")
            raw = jar.read(path)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError(f"malformed official client class: {class_name}")
            proc = subprocess.run(
                ["javap", "-c", "-p", "-classpath", str(client), class_name],
                capture_output=True, text=True, check=False, timeout=35,
            )
            if proc.returncode or len(proc.stdout) > MAX_DISASSEMBLY_CHARS:
                raise ValueError(f"client JVM method review unavailable: {class_name}")
            class_output[class_name] = proc.stdout
    return [
        bounded_method_shape(class_output[class_name], class_name, method)
        for class_name, method in METHODS
    ]


def discover(metadata: dict, scratch: Path) -> dict:
    asset = receiver.required_client(metadata)
    jar = scratch / "26.2-client.jar"
    receiver.official.download(asset["url"], jar, asset["sha1"], asset["size"])
    return {
        "schema": 1,
        "kind": KIND,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "source_archive_sha256": receiver.SOURCE_SHA256,
        "official_client_sha1": asset["sha1"],
        "official_client_sha256_candidate": receiver.official.sha256_file(jar),
        "review_method_shapes": inspect_client(jar),
        "complete_semantic_review": False,
        "client_numeric_id_assignment_proven": False,
        "source_var_sem_admitted": False,
        "production_admitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("client ordering output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(receiver.REPO.resolve()):
            raise ValueError("review evidence must not be written to repository")
        receiver.identity_lock(receiver.LOCK)
        with tempfile.TemporaryDirectory(prefix="helve-r2c-ordering-") as temp:
            output = discover(receiver.official_version_metadata(), Path(temp))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as error:
        print(f"Official 26.2 client ordering review failed closed: {error}",
              file=sys.stderr)
        return 2
    print("Official client ordering method shapes and branches captured; "
          "numeric-ID semantic admission remains FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
