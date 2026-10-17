"""Cross-oracle selected Configuration vs direct runtime 66-biome ID preflight."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import r2c_selected_biome_profile as profile

ROOT = Path(__file__).resolve().parents[2]


def _packet(registry: str, names: list[str] | None = None) -> bytes:
    # All synthetic fixture identifier lengths are single-byte VarInts.
    registry_bytes = registry.encode("utf-8")
    assert 0 < len(registry_bytes) < 128
    body = bytearray([7, len(registry_bytes)]) + registry_bytes
    if names is None:
        body.append(0)  # empty unrelated registry
    else:
        body.append(len(names))
        for name in names:
            encoded = name.encode("utf-8")
            assert 0 < len(encoded) < 128
            body.extend((len(encoded),))
            body.extend(encoded)
            body.append(0)  # selected minecraft:core known pack omits inline NBT
    return bytes(body)


def _selected(names: list[str]) -> list[bytes]:
    registry_bodies = [_packet(f"minecraft:other_{i}") for i in range(28)]
    registry_bodies.insert(11, _packet(profile.EXPECTED_REGISTRY, names))
    result = [b"\x01", b"\x0c", b"\x0e", *registry_bodies, b"\x0d", b"\x03"]
    assert len(result) == 34
    return result


class SelectedBiomeProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = json.loads(profile.FROZEN.read_text(encoding="utf-8"))
        cls.names = cls.candidate["names_by_verified_runtime_id_candidate"]

    def test_independent_66_runtime_id_order_matches_selected_wire_without_sorting(self) -> None:
        self.assertEqual(len(self.names), 66)
        self.assertEqual(self.names[40], "minecraft:plains")
        self.assertIsNone(profile.verify_selected_biome_profile(_selected(self.names)))

    def test_transposed_middle_and_near_end_ordinals_are_rejected(self) -> None:
        for index in (0, 27, 63):
            with self.subTest(index=index):
                changed = list(self.names)
                changed[index], changed[index + 1] = changed[index + 1], changed[index]
                with self.assertRaisesRegex(profile.ProfileMismatch, f"ordinal {index}"):
                    profile.verify_selected_biome_profile(_selected(changed))

    def test_missing_duplicate_and_data_bearing_registry_profiles_rejected(self) -> None:
        base = _selected(self.names)
        missing = base[:]
        missing[3 + 11] = _packet("minecraft:replaced")
        duplicated = base[:]
        duplicated[3 + 12] = base[3 + 11]
        wrong_id = base[:]
        wrong_id[4] = b"\x08" + wrong_id[4][1:]
        changed_bool = base[:]
        matching = bytearray(changed_bool[3 + 11])
        first = self.names[0].encode("utf-8")
        index = matching.index(first) + len(first)
        self.assertEqual(matching[index], 0)
        matching[index] = 1
        changed_bool[3 + 11] = bytes(matching)
        duplicate_entry = list(self.names)
        duplicate_entry[1] = duplicate_entry[0]
        for candidate in (missing, duplicated, wrong_id, changed_bool, _selected(duplicate_entry)):
            with self.subTest(candidate=candidate[4][:5]):
                with self.assertRaises(profile.ProfileMismatch):
                    profile.verify_selected_biome_profile(candidate)

    def test_wrong_known_pack_source_identity_or_digest_rejected(self) -> None:
        base = _selected(self.names)
        with tempfile.TemporaryDirectory(prefix="helve-biome-profile-") as temp:
            path = Path(temp) / "candidate.json"
            for key, value in (
                ("known_packs", ["minecraft:alternate@26.2"]),
                ("numeric_id_authority", "SOURCE_ADMITTED"),
                ("source_archive_sha256", "0" * 64),
                ("independent_numeric_id_order_sha256", "0" * 64),
            ):
                with self.subTest(key=key):
                    candidate = dict(self.candidate)
                    candidate[key] = value
                    path.write_text(json.dumps(candidate), encoding="utf-8")
                    with self.assertRaises(profile.ProfileMismatch):
                        profile.verify_selected_biome_profile(base, fixture=path)

            modified = dict(self.candidate)
            order = self.names.copy()
            order[0], order[1] = order[1], order[0]
            modified["names_by_verified_runtime_id_candidate"] = order
            path.write_text(json.dumps(modified), encoding="utf-8")
            with self.assertRaisesRegex(profile.ProfileMismatch, "SHA-256"):
                profile.verify_selected_biome_profile(base, fixture=path)


if __name__ == "__main__":
    unittest.main()
