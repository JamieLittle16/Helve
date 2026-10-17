#!/usr/bin/env python3
"""Inspect exact stock Minecraft 26.2 client chunk-with-light wire codec roots.

This is a source-free, SHA-1/size-verified *client* artifact witness. It is
not server-source review, not outer Play packet-ID admission, and does not
enable Helve Play publication. No client JAR, javap disassembly or source is
retained or uploaded.
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

KIND = "r2c-26_2-client-chunk-wire-method-frontier-candidate-v1"
ROOTS = (
    "net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket",
    "net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData",
    "net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData",
)
MAX_CLASS_BYTES = 1_048_576
MAX_CLASS_JAVAP = 3_000_000
MAX_DECLARATIONS = 96
MAX_INSTRUCTIONS = 900
MAX_SYMBOLS = 160
HEADER = re.compile(r"^  [^{};]+\([^;]*\)(?: throws [^;]+)?;$")
INSTRUCTION = re.compile(r"^\s*(\d+):\s+([a-z][a-z_0-9]*)\b(.*)$")
REVIEW_NAMES = ("write", "type", "handle", "read", "getReadBuffer")


def inspect_class(disassembly: str, class_name: str) -> dict:
    if not 0 < len(disassembly) <= MAX_CLASS_JAVAP:
        raise ValueError("unbounded official chunk packet inspection")
    lines = disassembly.splitlines()
    heads = []
    for index, line in enumerate(lines):
        m = HEADER.fullmatch(line)
        if m:
            # Include fully-qualified Java constructors as method boundaries:
            # their names contain dots, unlike javap's simple method names.
            # Otherwise the previous write/type body can accidentally absorb
            # the following constructor's restarted bytecode offsets.
            head = line.split("(", 1)[0].split()[-1].rsplit(".", 1)[-1]
            heads.append((index, head, line))
    if not heads or len(heads) > MAX_DECLARATIONS:
        raise ValueError("missing or excessive chunk codec declarations")
    methods = []
    for start, name, declaration in heads:
        if name not in REVIEW_NAMES:
            continue
        end = next((i for i, _, _ in heads if i > start), len(lines))
        rows = []
        symbols = []
        for line in lines[start:end]:
            match = INSTRUCTION.match(line)
            if not match:
                continue
            offset, op, rest = int(match.group(1)), match.group(2), match.group(3).strip()
            if rows and offset <= rows[-1][0]:
                raise ValueError("chunk codec instruction offsets not increasing")
            rows.append((offset, op, rest))
            if len(rows) > MAX_INSTRUCTIONS:
                raise ValueError("unbounded chunk codec method body")
            if op.startswith("invoke") or op in ("getstatic", "getfield", "putstatic", "putfield"):
                if "// " not in rest:
                    raise ValueError("missing symbolic client packet field/method reference")
                symbol = rest.split("// ", 1)[1]
                if not 0 < len(symbol) <= 8192:
                    raise ValueError("oversized official packet symbol")
                symbols.append({
                    "offset": offset, "opcode": op,
                    "symbol_candidate": symbol[:384],
                    "symbol_sha256": hashlib.sha256(symbol.encode()).hexdigest(),
                    "symbol_truncated": len(symbol) > 384,
                })
                if len(symbols) > MAX_SYMBOLS:
                    raise ValueError("unbounded chunk codec symbolic edges")
        if not rows:
            raise ValueError("selected exact chunk packet method has no code")
        methods.append({
            "name": name,
            "declaration_sha256": hashlib.sha256(declaration.encode()).hexdigest(),
            "instruction_shape_sha256": hashlib.sha256(
                "\n".join(f"{offset}:{op} {rest}" for offset, op, rest in rows).encode()
            ).hexdigest(),
            "instruction_count": len(rows),
            "symbols": symbols,
        })
    if not any(m["name"] == "write" for m in methods):
        raise ValueError(f"stock client packet write method not inspectable: {class_name}")
    return {"class_name": class_name, "candidate_methods": methods,
            "outer_packet_wire_semantics_source_admitted": False}


def inspect_client(client: Path) -> list[dict]:
    output = []
    with zipfile.ZipFile(client) as jar:
        names = jar.namelist()
        for class_name in ROOTS:
            name = class_name.replace(".", "/") + ".class"
            if names.count(name) != 1:
                raise ValueError(f"missing or ambiguous official packet class {class_name}")
            raw = jar.read(name)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError("malformed official chunk packet class")
            p = subprocess.run(
                ["javap", "-p", "-c", "-classpath", str(client), class_name],
                check=False, capture_output=True, text=True, timeout=35,
            )
            if p.returncode or len(p.stdout) > MAX_CLASS_JAVAP:
                raise ValueError(f"cannot inspect exact client chunk codec: {class_name}")
            record = inspect_class(p.stdout, class_name)
            record["classfile_sha256_candidate"] = hashlib.sha256(raw).hexdigest()
            output.append(record)
    return output


def discover(meta: dict, work: Path) -> dict:
    asset = receiver.required_client(meta)
    client = work / "26.2-client.jar"
    receiver.official.download(asset["url"], client, asset["sha1"], asset["size"])
    return {
        "schema": 1, "kind": KIND,
        "target": {"minecraft":"26.2","protocol":776,"data_version":4903},
        "official_client_sha1": asset["sha1"],
        "official_client_sha256_candidate": receiver.official.sha256_file(client),
        "source_archive_sha256": receiver.SOURCE_SHA256,
        "wire_codec_candidates": inspect_client(client),
        "packet_type_identity_admitted": False,
        "serialized_field_order_admitted": False,
        "source_var_sem_admitted": False,
        "production_admitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("client wire output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(receiver.REPO.resolve()):
            raise ValueError("client wire evidence must be outside repository")
        receiver.identity_lock(receiver.LOCK)
        with tempfile.TemporaryDirectory(prefix="helve-r2c-chunk-client-") as temp:
            report = discover(receiver.official_version_metadata(), Path(temp))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n")
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as err:
        print(f"official client chunk wire candidate rejected: {err}", file=sys.stderr)
        return 2
    print("Exact client chunk wire method signatures and symbolic instructions inspected; NO admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
