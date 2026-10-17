#!/usr/bin/env python3
"""Official Minecraft 26.2 client ProtocolInfoBuilder numeric-ID law frontier.

This is a bounded, exact-client, *source-free* method-shape inspection.
The GameProtocols builder argument ordering has already been witnessed;
we must independently prove that addPacket/build preserve that order and
assign wire IDs without a bundle/direction adjustment. Until then every
numeric-ID and production-admission flag is FALSE.
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

import r2c_official_client_registry_inventory as official_client

KIND = "r2c-26_2-stock-client-protocol-id-builder-frontier-v1"
OWNER = "net.minecraft.network.protocol.ProtocolInfoBuilder"
ROOT = OWNER.replace(".", "/")
CODEC_BUILDER = "net.minecraft.network.protocol.ProtocolCodecBuilder"
CODEC_ROOT = CODEC_BUILDER.replace(".", "/")
DISPATCH_CODEC = "net.minecraft.network.codec.IdDispatchCodec"
DISPATCH_ROOT = DISPATCH_CODEC.replace(".", "/")
MAX_JAR_ENTRIES = 60_000
MAX_BUILDER_CLASSES = 24
MAX_CLASS_BYTES = 786_432
MAX_JAVAP_BYTES = 3_000_000
MAX_METHODS = 180
MAX_METHOD_INSTRUCTIONS = 2_500
MAX_SYMBOLS = 256
DECL = re.compile(r"^  (?P<declaration>[^;{}]+\([^;]*\)(?: throws [^;]+)?);$")
INSTRUCTION = re.compile(r"^\s*(\d+):\s+([a-z][a-z_0-9]*)\b(.*)$")
FOCUS = (
    "addPacket", "withBundlePacket", "addBundlePacket", "build",
    "buildCodec", "createProtocolInfo", "finish",
    # Exact real method names discovered on SHA-pinned 26.2 builder classes:
    "buildDetails", "buildPacketCodec", "buildUnbound",
    "addToBuilder", "listPackets", "bind", "codec", "id", "add",
)


def inspect(disassembly: str, class_name: str) -> dict:
    if not 0 < len(disassembly) <= MAX_JAVAP_BYTES:
        raise ValueError("unbounded official client builder disassembly")
    lines = disassembly.splitlines()
    headers = []
    for i, line in enumerate(lines):
        match = DECL.fullmatch(line)
        if match is None:
            continue
        name = match.group("declaration").split("(", 1)[0].split()[-1].rsplit(".", 1)[-1]
        headers.append((i, name, line.strip()))
    if not headers or len(headers) > MAX_METHODS:
        raise ValueError(f"missing or excessive official builder declarations: {class_name}")
    records = []
    for ordinal, (start, name, declaration) in enumerate(headers):
        if name not in FOCUS:
            continue
        stop = headers[ordinal + 1][0] if ordinal + 1 < len(headers) else len(lines)
        rows = []
        edges = []
        seen_code = False
        for line in lines[start + 1:stop]:
            if line == "  static {};" or line == "}":
                break
            if line.strip() == "Code:":
                if seen_code:
                    raise ValueError("multiple code blocks inside one builder method")
                seen_code = True
                continue
            match = INSTRUCTION.match(line)
            if match is None:
                continue
            if not seen_code:
                raise ValueError("instruction outside builder method code")
            offset, opcode = int(match.group(1)), match.group(2)
            operand = match.group(3).strip()
            if rows and offset <= rows[-1][0]:
                raise ValueError("nonincreasing builder instruction offsets")
            rows.append((offset, opcode, operand))
            if len(rows) > MAX_METHOD_INSTRUCTIONS:
                raise ValueError("unbounded official builder method")
            if opcode.startswith("invoke") or opcode in (
                "getstatic", "getfield", "putstatic", "putfield", "new"
            ):
                if "// " not in operand:
                    raise ValueError("unsymbolized builder invoke or data edge")
                value = operand.split("// ", 1)[1]
                if not 0 < len(value) <= 4_096:
                    raise ValueError("unbounded official builder symbolic operand")
                edges.append({
                    "bytecode_offset": offset,
                    "opcode": opcode,
                    "symbol_candidate": value[:300],
                    "symbol_sha256": hashlib.sha256(value.encode()).hexdigest(),
                    "symbol_truncated": len(value) > 300,
                })
                if len(edges) > MAX_SYMBOLS:
                    raise ValueError("unbounded symbolic builder edges")
        records.append({
            "method_name": name,
            "declaration_sha256": hashlib.sha256(declaration.encode()).hexdigest(),
            "instruction_count": len(rows),
            "instruction_shape_sha256": hashlib.sha256(
                "\n".join(f"{n}:{op} {arg}" for n, op, arg in rows).encode()
            ).hexdigest(),
            "abstract_or_native_no_bytecode": not seen_code,
            "symbolic_edges_candidate": edges,
        })
    return {
        "class_name": class_name,
        "all_declared_method_names_candidate": sorted({name for _, name, _ in headers}),
        "selected_methods": records,
        "builder_numeric_id_assignment_proven": False,
    }


def builder_roots(jar: zipfile.ZipFile) -> list[tuple[str, str]]:
    names = jar.namelist()
    if len(names) > MAX_JAR_ENTRIES:
        raise ValueError("unbounded official client JAR entries")
    if names.count(ROOT + ".class") != 1:
        raise ValueError("missing or duplicate official ProtocolInfoBuilder root")
    candidates = sorted({
        name for name in names
        if (name.startswith(ROOT + "$") or name.startswith(CODEC_ROOT + "$")
            or name == DISPATCH_ROOT + "$Builder.class")
        and name.endswith(".class")
    })
    # The downstream target codec builder is a separate class; it is
    # reached by the pinned CodecEntry.addToBuilder bytecode, not guessed.
    if CODEC_ROOT + ".class" in names:
        candidates.append(CODEC_ROOT + ".class")
    if DISPATCH_ROOT + ".class" in names:
        candidates.append(DISPATCH_ROOT + ".class")
    if len(candidates) > MAX_BUILDER_CLASSES - 1:
        raise ValueError("unbounded official builder nested class inventory")
    return [(name, name.removesuffix(".class").replace("/", "."))
            for name in [ROOT + ".class", *candidates]]


def inspect_client(client: Path) -> list[dict]:
    output = []
    with zipfile.ZipFile(client) as jar:
        for source, name in builder_roots(jar):
            if jar.namelist().count(source) != 1:
                raise ValueError("duplicate official nested builder class")
            raw = jar.read(source)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError("corrupt official builder classfile")
            proc = subprocess.run(
                ["javap", "-p", "-c", "-classpath", str(client), name],
                capture_output=True, text=True, check=False, timeout=40,
            )
            if proc.returncode or len(proc.stdout) > MAX_JAVAP_BYTES:
                raise ValueError("cannot inspect complete actual client builder method")
            result = inspect(proc.stdout, name)
            result["classfile_sha256"] = hashlib.sha256(raw).hexdigest()
            output.append(result)
    if not any(record["method_name"] == "addPacket"
               for item in output for record in item["selected_methods"]):
        raise ValueError("exact stock client builder lacks addPacket declaration")
    return output


def discover(meta: dict, work: Path) -> dict:
    asset = official_client.required_client(meta)
    path = work / "26.2-client.jar"
    official_client.official.download(
        asset["url"], path, asset["sha1"], asset["size"]
    )
    return {
        "schema": 1, "kind": KIND,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "official_client_sha1": asset["sha1"],
        "official_client_sha256": official_client.official.sha256_file(path),
        "pinned_source_archive_sha256": official_client.SOURCE_SHA256,
        "builder_class_candidates": inspect_client(path),
        "builder_append_to_numeric_id_law_proven": False,
        "bundle_numeric_id_effect_proven": False,
        "serverbound_clientbound_direction_law_proven": False,
        "independent_source_var_sem_admitted": False,
        "production_admitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("official builder output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(
            official_client.REPO.resolve()
        ):
            raise ValueError("source-free builder evidence must stay outside repository")
        official_client.identity_lock(official_client.LOCK)
        with tempfile.TemporaryDirectory(prefix="helve-26-2-client-builder-") as tmp:
            result = discover(official_client.official_version_metadata(), Path(tmp))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as exc:
        print(f"exact stock-client builder source frontier rejected: {exc}",
              file=sys.stderr)
        return 2
    print("Stock 26.2 client ProtocolInfoBuilder identities captured; all "
          "numeric-ID/VAR/SEM/production admission flags remain FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
