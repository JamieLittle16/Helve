"""Fail-closed synthetic qualification for R2C Configuration biome-order extraction."""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import r2c_biome_registry_capture as probe  # noqa: E402
import r1b_join_capture_image as witness  # noqa: E402


def vi(value: int) -> bytes:
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def ident(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return vi(len(encoded)) + encoded


def packet(registry: str, entries: tuple[str, ...], flags: tuple[int, ...] | None = None) -> bytes:
    if flags is None:
        flags = (0,) * len(entries)
    return b"".join(
        (vi(7), ident(registry), vi(len(entries))),
    ) + b"".join(ident(name) + bytes([flag]) for name, flag in zip(entries, flags))


class BiomeRegistryCaptureTests(unittest.TestCase):
    def test_preserves_first_occurrence_wire_order_not_alphabetical(self) -> None:
        names = ("minecraft:plains", "minecraft:desert", "minecraft:forest")
        encoded = packet(probe.BIOME_REGISTRY, names)
        self.assertEqual(probe.registry_packet_name(encoded)[0], probe.BIOME_REGISTRY)
        self.assertEqual(probe.decode_biome_packet(encoded), names)
        self.assertNotEqual(names, tuple(sorted(names)))

    def test_varints_are_canonical_and_finite(self) -> None:
        for value in (0, 1, 127, 128, 255, 16384, 2**32 - 1):
            raw = vi(value)
            self.assertEqual(probe._varint(raw, 0), (value, len(raw)))
        for raw in (b"", b"\x80", b"\x80\x00", b"\xff\xff\xff\xff\x7f",
                    b"\x80\x80\x80\x80\x80\x00"):
            with self.subTest(raw=raw):
                with self.assertRaises(probe.BiomeCaptureError):
                    probe._varint(raw, 0)

    def test_rejects_invalid_names_duplicates_and_wrong_packet(self) -> None:
        good = ("minecraft:forest", "minecraft:plains")
        for raw in (
            packet(probe.BIOME_REGISTRY, ("minecraft:forest", "minecraft:forest")),
            packet(probe.BIOME_REGISTRY, ("Forest",)),
            packet(probe.BIOME_REGISTRY, ("minecraft:bad name",)),
            packet(probe.BIOME_REGISTRY, good) + b"\x00",
            packet(probe.BIOME_REGISTRY, good)[:-1],
            packet(probe.BIOME_REGISTRY, good, (0, 1)),
            packet("minecraft:dimension_type", good),
            b"\x08" + packet(probe.BIOME_REGISTRY, good)[1:],
            vi(7) + ident(probe.BIOME_REGISTRY) + vi(0),
            vi(7) + ident(probe.BIOME_REGISTRY) + vi(probe.MAX_ENTRIES + 1),
        ):
            with self.subTest(raw=raw[:40]):
                with self.assertRaises(probe.BiomeCaptureError):
                    probe.decode_biome_packet(raw)

    def test_pinned_identity_does_not_accept_arbitrary_capture_images(self) -> None:
        for image in (
            {},
            {"kind": witness.KIND, "schema": 1,
             "target": {"minecraft": "26.3", "protocol": 776}},
            {"kind": witness.KIND, "schema": 1, "target": {
                "minecraft": "26.2", "protocol": 776,
                "source_archive_sha256": witness.EXPECTED_SOURCE_SHA256,
                "capture_sha256": witness.EXPECTED_CAPTURE_SHA256,
            }, "configuration": {"server_bodies": []}},
        ):
            with self.assertRaises(probe.BiomeCaptureError):
                probe._verified_bodies(image)

    def test_candidate_artifact_never_claims_admitted_numeric_ids(self) -> None:
        names = ("minecraft:forest", "minecraft:plains", "minecraft:desert")
        packets = [packet(f"minecraft:synthetic/registry_{i}", ("minecraft:test",))
                   for i in range(28)]
        packets.insert(11, packet(probe.BIOME_REGISTRY, names))
        lock = {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": witness.EXPECTED_SOURCE_SHA256},
            "runtime": {"server_sha256": "a" * 64},
        }
        with patch.object(probe, "_verified_bodies", return_value=packets):
            result = probe.extract({}, names, lock)
            self.assertEqual(result["candidate_names_by_network_ordinal"], list(names))
            self.assertEqual(result["numeric_id_authority"], "UNQUALIFIED_CAPTURE_CANDIDATE")
            self.assertNotIn("names_by_protocol_id", result)
            self.assertEqual(
                result["candidate_order_sha256"],
                hashlib.sha256(("\n".join(names) + "\n").encode()).hexdigest(),
            )
            with self.assertRaises(probe.BiomeCaptureError):
                probe.extract({}, tuple(reversed(names[:-1])) + ("minecraft:extra",), lock)
            packets[-1] = packets[0]
            with self.assertRaises(probe.BiomeCaptureError):
                probe.extract({}, names, lock)

    def test_frozen_official_inventory_has_exact_digest(self) -> None:
        root = Path(__file__).resolve().parents[2]
        path = root / "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt"
        names = probe._inventory(path)
        self.assertEqual(len(names), 66)
        self.assertIn("minecraft:plains", names)
        self.assertIn("minecraft:sulfur_caves", names)

    def test_empty_or_unsourced_lock_rejected(self) -> None:
        with self.assertRaises(probe.BiomeCaptureError):
            probe.extract({}, ("minecraft:plains",), {})


if __name__ == "__main__":
    unittest.main()
