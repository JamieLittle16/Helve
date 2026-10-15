#!/usr/bin/env python3
"""Observe loaded 26.2 biome entry ordinals from a fresh pinned vanilla server.

Unlike datagen's 66 *resource keys*, this probe reads the server's ordered
Configuration registry_data packet after answering the exact known-packs
challenge. It does not run a Minecraft client, ship replay frames or infer
registry IDs by sorting names. The source/wire admission and an independent
loaded-registry oracle remain separate requirements under issue #285.

All server state and wire evidence are ephemeral. Only a source-free ordered
candidate with explicit UNQUALIFIED status is written to the requested path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import queue
import socket
import subprocess
import sys
import threading
import time
import tomllib
from pathlib import Path

import official_state_data
import r2c_biome_registry_capture as capture

TARGET_VERSION = "26.2"
TARGET_PROTOCOL = 776
PORT = 25565
MAX_FRAME_BYTES = 2_097_152
MAX_PACKETS = 96
MAX_REGISTRY_PACKETS = 29
EXPECTED_PACKS = (("minecraft", "core", TARGET_VERSION),)


class LiveBiomeProbeError(ValueError):
    """The official runtime or selected Configuration protocol violated our bounds."""


def varint(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF_FFFF:
        raise LiveBiomeProbeError("invalid VarInt value")
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def read_exact(conn: socket.socket, size: int) -> bytes:
    if size < 0 or size > MAX_FRAME_BYTES:
        raise LiveBiomeProbeError("frame length exceeds bound")
    output = bytearray()
    while len(output) < size:
        part = conn.recv(size - len(output))
        if not part:
            raise LiveBiomeProbeError("server disconnected during Configuration observation")
        output.extend(part)
    return bytes(output)


def read_varint(conn: socket.socket) -> int:
    raw = bytearray()
    for _ in range(5):
        byte = read_exact(conn, 1)[0]
        raw.append(byte)
        if byte & 128 == 0:
            value, offset = capture._varint(bytes(raw), 0)
            if offset != len(raw):
                raise LiveBiomeProbeError("invalid frame-length encoding")
            return value
    raise LiveBiomeProbeError("overlong frame-length VarInt")


def frame(body: bytes) -> bytes:
    if not body or len(body) > MAX_FRAME_BYTES:
        raise LiveBiomeProbeError("invalid packet body length")
    return varint(len(body)) + body


def send_packet(conn: socket.socket, packet_id: int, payload: bytes = b"") -> None:
    conn.sendall(frame(varint(packet_id) + payload))


def read_packet(conn: socket.socket) -> tuple[int, bytes]:
    length = read_varint(conn)
    if not 1 <= length <= MAX_FRAME_BYTES:
        raise LiveBiomeProbeError("invalid server frame length")
    body = read_exact(conn, length)
    packet_id, _ = capture._varint(body, 0)
    return packet_id, body


def write_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) > 32_767:
        raise LiveBiomeProbeError("UTF-8 field exceeds bound")
    return varint(len(encoded)) + encoded


def read_string(data: bytes, offset: int) -> tuple[str, int]:
    length, offset = capture._varint(data, offset)
    if length > 32_767 or length > len(data) - offset:
        raise LiveBiomeProbeError("string exceeds packet bounds")
    raw = data[offset:offset + length]
    try:
        return raw.decode("utf-8"), offset + length
    except UnicodeDecodeError as error:
        raise LiveBiomeProbeError("invalid UTF-8 in known-pack descriptor") from error


def known_packs(body: bytes) -> tuple[tuple[str, str, str], ...]:
    packet_id, offset = capture._varint(body, 0)
    if packet_id != 14:
        raise LiveBiomeProbeError("not a selected known-packs challenge")
    count, offset = capture._varint(body, offset)
    if not 1 <= count <= 64:
        raise LiveBiomeProbeError("selected known-pack count outside admitted profile")
    result: list[tuple[str, str, str]] = []
    for _ in range(count):
        namespace, offset = read_string(body, offset)
        pack_id, offset = read_string(body, offset)
        version, offset = read_string(body, offset)
        result.append((namespace, pack_id, version))
    if offset != len(body) or tuple(result) != EXPECTED_PACKS:
        raise LiveBiomeProbeError("unexpected vanilla 26.2 known-pack profile")
    return tuple(result)


def observe_configuration(conn: socket.socket) -> tuple[str, ...]:
    """Perform selected offline Login and observe exactly one ordered registry sync."""
    conn.settimeout(120)
    handshake = (varint(TARGET_PROTOCOL) + write_string("localhost")
                 + PORT.to_bytes(2, "big") + varint(2))
    send_packet(conn, 0, handshake)
    send_packet(conn, 0, write_string("HelveProbe") + bytes(16))

    packet_id, login_finished = read_packet(conn)
    if packet_id != 2 or len(login_finished) < 20:
        raise LiveBiomeProbeError(
            f"expected uncompressed offline LoginFinished id 2, got {packet_id}"
        )
    send_packet(conn, 3)  # Serverbound LoginAcknowledged: unit, terminal.

    selected = False
    seen_registries: set[str] = set()
    biome_names: tuple[str, ...] | None = None
    for _ in range(MAX_PACKETS):
        packet_id, body = read_packet(conn)
        if packet_id == 14:  # ClientboundSelectKnownPacks
            if selected or seen_registries:
                raise LiveBiomeProbeError("known-pack negotiation repeated or arrived late")
            known_packs(body)
            # Same ordered known-pack descriptor bytes in serverbound packet ID 7.
            send_packet(conn, 7, body[1:])
            selected = True
        elif packet_id == 7:  # ClientboundRegistryData
            if not selected or len(seen_registries) >= MAX_REGISTRY_PACKETS:
                raise LiveBiomeProbeError("registry publication outside bounded sync")
            registry, _ = capture.registry_packet_name(body)
            if registry in seen_registries:
                raise LiveBiomeProbeError(f"duplicate Configuration registry: {registry}")
            seen_registries.add(registry)
            if registry == capture.BIOME_REGISTRY:
                biome_names = capture.decode_biome_packet(body)
        elif packet_id == 13:  # ClientboundUpdateTags closes selected registry sync
            if not selected or len(seen_registries) != MAX_REGISTRY_PACKETS:
                raise LiveBiomeProbeError("tags arrived before full Configuration registry sync")
            if biome_names is None:
                raise LiveBiomeProbeError("vanilla did not publish the loaded biome registry")
            return biome_names
        elif packet_id in (1, 12):  # Brand payload / enabled features.
            if selected:
                raise LiveBiomeProbeError("initial Configuration prefix arrived after registry sync")
        elif packet_id == 4:  # Configuration KeepAlive, echo its 8-byte payload.
            if len(body) != 9:
                raise LiveBiomeProbeError("invalid Configuration keepalive")
            send_packet(conn, 4, body[1:])
        elif packet_id == 5:  # Configuration Ping -> Pong, four-byte payload.
            if len(body) != 5:
                raise LiveBiomeProbeError("invalid Configuration ping")
            send_packet(conn, 5, body[1:])
        else:
            raise LiveBiomeProbeError(
                f"unexpected Configuration packet id {packet_id} on pinned selected profile"
            )
    raise LiveBiomeProbeError("exceeded bounded Configuration packet count")


def server_properties() -> str:
    return "\n".join([
        "allow-nether=false",
        "difficulty=peaceful",
        "enable-query=false",
        "enable-rcon=false",
        "gamemode=survival",
        "level-name=world",
        "level-seed=0",
        "max-players=1",
        "max-tick-time=-1",
        "motd=Helve pinned biome ordinal oracle",
        "network-compression-threshold=-1",
        "online-mode=false",
        "server-ip=127.0.0.1",
        f"server-port={PORT}",
        "simulation-distance=2",
        "spawn-protection=0",
        "view-distance=2",
        "white-list=false",
    ]) + "\n"


def observe_official_server(server: Path, work_dir: Path) -> tuple[str, ...]:
    if work_dir.exists() or work_dir.is_symlink():
        raise LiveBiomeProbeError("runtime world work directory must be fresh")
    work_dir.mkdir(parents=True)
    (work_dir / "eula.txt").write_text("eula=true\n", encoding="ascii")
    (work_dir / "server.properties").write_text(server_properties(), encoding="ascii")
    proc = subprocess.Popen(
        ["java", "-Xms256M", "-Xmx1536M", "-jar", str(server.resolve()), "nogui"],
        cwd=work_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    lines: queue.Queue[str] = queue.Queue(maxsize=512)
    tail: list[str] = []

    def pump() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            try:
                lines.put_nowait(line)
            except queue.Full:
                pass

    reader = threading.Thread(target=pump, daemon=True)
    reader.start()
    try:
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise LiveBiomeProbeError(
                    f"official server exited before startup: {proc.returncode}\n"
                    + "".join(tail[-16:])
                )
            try:
                line = lines.get(timeout=0.5)
            except queue.Empty:
                continue
            tail.append(line)
            tail = tail[-32:]
            if "Done (" in line and 'For help, type "help"' in line:
                break
        else:
            raise LiveBiomeProbeError(
                "official 26.2 server startup timeout\n" + "".join(tail[-16:])
            )
        with socket.create_connection(("127.0.0.1", PORT), timeout=10) as conn:
            return observe_configuration(conn)
    finally:
        if proc.poll() is None:
            try:
                assert proc.stdin is not None
                proc.stdin.write("stop\n")
                proc.stdin.flush()
                proc.wait(timeout=30)
            except (OSError, subprocess.TimeoutExpired):
                proc.kill()
                proc.wait(timeout=15)


def evidence(
    biome_names: tuple[str, ...], inventory: tuple[str, ...],
    server_sha256: str, lock: dict[str, object],
) -> dict[str, object]:
    if len(biome_names) != 66 or len(set(biome_names)) != 66:
        raise LiveBiomeProbeError("loaded runtime biome registry is not 66 unique entries")
    if set(biome_names) != set(inventory):
        raise LiveBiomeProbeError("runtime registry differs from pinned official biome keys")
    if server_sha256 != lock.get("runtime", {}).get("server_sha256"):
        raise LiveBiomeProbeError("official server SHA differs from lock")
    canonical = ("\n".join(biome_names) + "\n").encode("utf-8")
    return {
        "schema": 1,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "registry": capture.BIOME_REGISTRY,
        "source": "pinned-official-server-live-configuration-observation-v1",
        "server_sha256": server_sha256,
        "source_archive_sha256": lock["source"]["archive_sha256"],
        "known_packs": ["minecraft:core@26.2"],
        "network_entry_count": len(biome_names),
        "runtime_order_sha256": hashlib.sha256(canonical).hexdigest(),
        "names_by_observed_network_ordinal": list(biome_names),
        "numeric_id_authority": "RUNTIME_OBSERVED_SOURCE_ADMISSION_PENDING",
        "required_independent_check": (
            "pinned 26.2 loaded-registry ID oracle and R2C source/SEM packet assignment"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/helve-vanilla-downloads"))
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=Path("vanilla/vanilla.lock.toml"))
    parser.add_argument("--inventory", type=Path, default=Path(
        "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt"
    ))
    args = parser.parse_args()
    try:
        with args.lock.open("rb") as handle:
            lock = tomllib.load(handle)
        if (lock.get("minecraft") != TARGET_VERSION
            or lock.get("protocol") != TARGET_PROTOCOL
            or lock.get("data_version") != 4903):
            raise LiveBiomeProbeError("unexpected pinned version/protocol/data version")
        resolved, _ = official_state_data.resolve(TARGET_VERSION, args.cache)
        server, _ = resolved["server"]
        digest = official_state_data.sha256_file(server)
        if digest != lock.get("runtime", {}).get("server_sha256"):
            raise LiveBiomeProbeError("downloaded official server SHA mismatch")
        names = observe_official_server(server, args.work_dir)
        result = evidence(names, capture._inventory(args.inventory), digest, lock)
        if args.output.exists() or args.output.is_symlink():
            raise LiveBiomeProbeError("output must be a fresh non-symlink path")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    except (LiveBiomeProbeError, capture.BiomeCaptureError,
            OSError, ValueError, KeyError, subprocess.SubprocessError,
            socket.timeout) as error:
        print(f"live biome registry probe failed: {error}", file=sys.stderr)
        return 2
    print(
        f"Official live 26.2 Configuration published {result['network_entry_count']} "
        f"biomes; observed ordinal digest {result['runtime_order_sha256']}. "
        "SOURCE/SEM AND INDEPENDENT LOADED-REGISTRY ID CHECK STILL PENDING."
    )
    for ordinal, name in enumerate(result["names_by_observed_network_ordinal"]):
        print(f"BIOME_NETWORK_ORDINAL|{ordinal}|{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
