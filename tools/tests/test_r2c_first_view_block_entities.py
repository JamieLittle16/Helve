"""Hermetic read-only initial-view block-entity source-audit regressions."""
from __future__ import annotations

import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import r2c_first_view_block_entities as audit


def _named(tag: int, name: str, payload: bytes) -> bytes:
    encoded = name.encode("utf-8")
    return bytes([tag]) + struct.pack(">H", len(encoded)) + encoded + payload


def _entity(kind: str, x: int, y: int, z: int) -> bytes:
    return (
        _named(8, "id", struct.pack(">H", len(kind)) + kind.encode("ascii"))
        + _named(3, "x", struct.pack(">i", x))
        + _named(3, "y", struct.pack(">i", y))
        + _named(3, "z", struct.pack(">i", z))
        + b"\x00"
    )


def _chunk(x: int, z: int, *, entities: tuple[bytes, ...] | None = ()) -> bytes:
    nbt = (
        b"\x0a\x00\x00"
        + _named(3, "DataVersion", struct.pack(">i", 4903))
        + _named(3, "xPos", struct.pack(">i", x))
        + _named(3, "zPos", struct.pack(">i", z))
    )
    if entities is not None:
        nbt += _named(9, "block_entities", b"\x0a" + struct.pack(">i", len(entities)) + b"".join(entities))
    return nbt + b"\x00"


def _regions(world: Path, definitions: dict[tuple[int, int], bytes]) -> None:
    directory = world / "dimensions/minecraft/overworld/region"
    directory.mkdir(parents=True, exist_ok=True)
    (world / "level.dat").write_bytes(b"preserved source metadata")
    grouped: dict[tuple[int, int], list[tuple[int, int, bytes]]] = {}
    for (x, z), raw_nbt in definitions.items():
        grouped.setdefault((x // 32, z // 32), []).append((x, z, raw_nbt))
    for (rx, rz), chunks in grouped.items():
        header = bytearray(8192)
        content = bytearray()
        for x, z, nbt in chunks:
            compressed = zlib.compress(nbt)
            record = struct.pack(">I", len(compressed) + 1) + b"\x02" + compressed
            sectors = (len(record) + 4095) // 4096
            offset = 2 + len(content) // 4096
            slot = (x % 32) + (z % 32) * 32
            header[slot * 4: slot * 4 + 4] = (offset << 8 | sectors).to_bytes(4, "big")
            content.extend(record + b"\x00" * (sectors * 4096 - len(record)))
        (directory / f"r.{rx}.{rz}.mca").write_bytes(header + content)


class FirstViewBlockEntityAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.world = Path(self.temp.name) / "source-world"
        self.positions = audit.first_view_positions()

    def make_world(
        self, *, override: dict[tuple[int, int], bytes] | None = None,
        count: int = audit.INITIAL_CHUNKS,
    ) -> None:
        sources = {
            (x, z): _chunk(x, z) for x, z in audit.first_view_positions(count)
        }
        sources.update(override or {})
        _regions(self.world, sources)

    def test_exact_pinned_first_view_spans_four_signed_regions(self) -> None:
        self.assertEqual(self.positions, (
            (0, -1), (-1, -1), (0, -2), (0, 0), (1, -1),
            (-1, -2), (-1, 0), (1, -2), (1, 0),
        ))
        self.assertEqual({
            (x // 32, z // 32) for x, z in self.positions
        }, {(-1, -1), (-1, 0), (0, -1), (0, 0)})

    def test_25_halo_is_exact_5x5_and_extends_original_nine(self) -> None:
        positions = audit.first_view_positions(audit.RENDER_HALO_CHUNKS)
        self.assertEqual(positions[:9], self.positions)
        self.assertEqual(len(positions), 25)
        self.assertEqual(len(set(positions)), 25)
        self.assertEqual(
            set(positions),
            {(dx, -1 + dz) for dx in range(-2, 3) for dz in range(-2, 3)},
        )
        with self.assertRaisesRegex(audit.SourceAuditError, "unsupported"):
            audit.first_view_positions(24)

    def test_new_halo_border_entities_fail_without_source_mutation(self) -> None:
        outside = (-2, -3)
        self.assertNotIn(outside, self.positions)
        self.make_world(
            count=audit.RENDER_HALO_CHUNKS,
            override={
                outside: _chunk(
                    *outside, entities=(
                        _entity("minecraft:beehive", -24, 71, -48),
                        _entity("minecraft:beehive", -23, 72, -47),
                    ),
                ),
            },
        )
        region = self.world / "dimensions/minecraft/overworld/region/r.-1.-1.mca"
        before = region.read_bytes()
        first = audit.audit_world(self.world)
        self.assertTrue(audit.print_report(first))
        extended = audit.audit_world(self.world, audit.RENDER_HALO_CHUNKS)
        self.assertEqual(len(extended), 25)
        evidence = [record for record in extended if record.entries]
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].entries, (
            ("minecraft:beehive", -24, 71, -48),
            ("minecraft:beehive", -23, 72, -47),
        ))
        self.assertFalse(audit.print_report(extended))
        self.assertEqual(region.read_bytes(), before)

    def test_all_25_explicitly_empty_halo_lists_are_eligible(self) -> None:
        self.make_world(count=audit.RENDER_HALO_CHUNKS)
        reports = audit.audit_world(self.world, audit.RENDER_HALO_CHUNKS)
        self.assertEqual(len(reports), 25)
        self.assertTrue(audit.print_report(reports))

    def test_all_explicit_empty_lists_are_only_cold_eligible(self) -> None:
        self.make_world()
        reports = audit.audit_world(self.world)
        self.assertEqual(len(reports), 9)
        self.assertTrue(all(r.evidence == "EXPLICITLY_EMPTY" for r in reports))
        self.assertTrue(audit.print_report(reports))

    def test_nonempty_entry_is_located_without_changing_source(self) -> None:
        kind = "minecraft:chest"
        self.make_world(override={
            (-1, -1): _chunk(-1, -1, entities=(_entity(kind, -12, 72, -9),)),
        })
        region_path = self.world / "dimensions/minecraft/overworld/region/r.-1.-1.mca"
        original = region_path.read_bytes()
        reports = audit.audit_world(self.world)
        self.assertEqual(region_path.read_bytes(), original)
        self.assertEqual(reports[1].evidence, "NONEMPTY (unsupported)")
        self.assertEqual(reports[1].entries, ((kind, -12, 72, -9),))
        self.assertFalse(audit.print_report(reports))
        self.assertTrue(all(r.evidence == "EXPLICITLY_EMPTY" for r in reports[2:]))

    def test_missing_list_is_never_treated_as_empty(self) -> None:
        self.make_world(override={(0, -1): _chunk(0, -1, entities=None)})
        reports = audit.audit_world(self.world)
        self.assertEqual(reports[0].evidence, "ABSENT (not admitted as empty)")
        self.assertFalse(audit.print_report(reports))

    def test_wrong_saved_version_and_missing_region_fail_closed(self) -> None:
        self.make_world()
        original_path = self.world / "dimensions/minecraft/overworld/region/r.0.-1.mca"
        original_path.unlink()
        with self.assertRaisesRegex(audit.SourceAuditError, "required regular"):
            audit.audit_world(self.world)

    def test_missing_selected_slot_is_a_source_failure(self) -> None:
        self.make_world()
        region_path = self.world / "dimensions/minecraft/overworld/region/r.0.-1.mca"
        data = bytearray(region_path.read_bytes())
        slot = (0 % 32) + 32 * (-1 % 32)
        data[slot * 4:slot * 4 + 4] = b"\x00" * 4
        region_path.write_bytes(data)
        with self.assertRaisesRegex(audit.SourceAuditError, "absent"):
            audit.audit_world(self.world)


if __name__ == "__main__":
    unittest.main()
