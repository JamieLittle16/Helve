"""Fail-closed tests for the direct loaded-vanilla biome order observation."""

from __future__ import annotations

import socket
import sys
import threading
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import r2c_live_biome_registry as probe


def registry_packet(name: str, entries: tuple[str, ...]) -> bytes:
    return (
        probe.varint(7) + probe.write_string(name) + probe.varint(len(entries))
        + b"".join(probe.write_string(key) + b"\x00" for key in entries)
    )


class LiveBiomeRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = tuple(
            (TOOLS.parent / "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt")
            .read_text(encoding="utf-8").splitlines()
        )
        assert len(cls.inventory) == 66

    def test_canonical_length_and_known_pack_guards(self) -> None:
        self.assertEqual(probe.varint(776), b"\x88\x06")
        packs = (
            probe.varint(14) + probe.varint(1) +
            probe.write_string("minecraft") +
            probe.write_string("core") +
            probe.write_string("26.2")
        )
        self.assertEqual(probe.known_packs(packs), probe.EXPECTED_PACKS)
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.known_packs(packs + b"\x00")
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.known_packs(packs.replace(b"26.2", b"26.1"))
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.frame(b"")
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.varint(-1)

    def test_complete_configuration_handshake_yields_runtime_order(self) -> None:
        # This fixture tests packet parsing and exact negotiation, NOT loaded
        # numeric ID authority or any vanilla wire-law admission.
        client, server = socket.socketpair()
        client.settimeout(5)
        server.settimeout(5)
        failures: list[Exception] = []
        observed: list[tuple[str, ...]] = []
        packs = (
            probe.varint(1) +
            probe.write_string("minecraft") +
            probe.write_string("core") +
            probe.write_string("26.2")
        )

        def official_emulator() -> None:
            try:
                self.assertEqual(probe.read_packet(server)[0], 0)  # Handshake.
                self.assertEqual(probe.read_packet(server)[0], 0)  # Login Hello.
                probe.send_packet(server, 2, b"\x00" * 36)  # Login finished.
                self.assertEqual(probe.read_packet(server)[0], 3)  # Login Ack.
                probe.send_packet(server, 1, b"\x00")
                probe.send_packet(server, 12, b"\x00")
                probe.send_packet(server, 14, packs)
                selected, body = probe.read_packet(server)
                self.assertEqual(selected, 7)
                self.assertEqual(body[1:], packs)
                for index in range(28):
                    server.sendall(probe.frame(registry_packet(
                        f"minecraft:test_{index}", (),
                    )))
                server.sendall(probe.frame(registry_packet(
                    "minecraft:worldgen/biome", self.inventory,
                )))
                probe.send_packet(server, 13, b"\x00")
            except Exception as error:  # Propagate thread assertions to test.
                failures.append(error)
            finally:
                server.close()

        worker = threading.Thread(target=official_emulator, daemon=True)
        worker.start()
        try:
            observed.append(probe.observe_configuration(client))
        finally:
            client.close()
            worker.join(timeout=6)
        if failures:
            raise failures[0]
        self.assertFalse(worker.is_alive())
        self.assertEqual(observed, [self.inventory])

    def test_resource_inventory_is_not_numeric_id_authority(self) -> None:
        import tomllib

        lock = tomllib.loads(
            (TOOLS.parent / "vanilla/vanilla.lock.toml").read_text(encoding="utf-8")
        )
        digest = lock["runtime"]["server_sha256"]
        result = probe.evidence(self.inventory, self.inventory, digest, lock)
        self.assertEqual(
            result["numeric_id_authority"],
            "RUNTIME_OBSERVED_SOURCE_ADMISSION_PENDING",
        )
        self.assertEqual(result["network_entry_count"], 66)
        self.assertEqual(result["names_by_observed_network_ordinal"], list(self.inventory))
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.evidence(self.inventory[:-1], self.inventory, digest, lock)
        with self.assertRaises(probe.LiveBiomeProbeError):
            probe.evidence(self.inventory, self.inventory, "0" * 64, lock)


if __name__ == "__main__":
    unittest.main()
