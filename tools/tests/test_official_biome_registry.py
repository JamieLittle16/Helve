"""Source-identity boundary tests for ordered 26.2 biome registry extraction."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import official_biome_registry as probe  # noqa: E402


def synthetic(names: tuple[str, ...]) -> dict[str, object]:
    """Intentionally non-alphabetic report insertion order."""
    return {
        probe.REGISTRY: {
            "entries": {
                name: {"protocol_id": i}
                for i, name in enumerate(names)
            },
        },
    }


class OfficialBiomeRegistryTests(unittest.TestCase):
    def test_ids_are_report_protocol_values_not_key_sort_order(self) -> None:
        data = synthetic(
            ("minecraft:forest", "minecraft:desert", "minecraft:plains")
        )
        self.assertEqual(
            probe.canonical_keys(data),
            ("minecraft:forest", "minecraft:desert", "minecraft:plains"),
        )
        entries = data[probe.REGISTRY]["entries"]
        self.assertEqual(entries["minecraft:plains"]["protocol_id"], 2)
        result = probe.payload(probe.TARGET_VERSION, "a" * 64, data)
        self.assertEqual(result["registry_count"], 3)
        self.assertEqual(result["names_by_protocol_id"][0], "minecraft:forest")

    def test_sparse_duplicate_and_noninteger_ids_fail_closed(self) -> None:
        bad = synthetic(("minecraft:forest", "minecraft:desert"))
        bad[probe.REGISTRY]["entries"]["minecraft:desert"]["protocol_id"] = 0
        with self.assertRaises(probe.RegistryExtractionError):
            probe.canonical_keys(bad)

        bad = synthetic(("minecraft:forest", "minecraft:desert"))
        bad[probe.REGISTRY]["entries"]["minecraft:desert"]["protocol_id"] = 2
        with self.assertRaises(probe.RegistryExtractionError):
            probe.canonical_keys(bad)

        bad = synthetic(("minecraft:forest", "minecraft:desert"))
        bad[probe.REGISTRY]["entries"]["minecraft:forest"]["protocol_id"] = True
        with self.assertRaises(probe.RegistryExtractionError):
            probe.canonical_keys(bad)

    def test_missing_biome_registry_and_wrong_release_rejected(self) -> None:
        with self.assertRaises(probe.RegistryExtractionError):
            probe.canonical_keys({})
        with self.assertRaises(probe.RegistryExtractionError):
            probe.canonical_keys({probe.REGISTRY: {"entries": {}}})
        with self.assertRaises(probe.RegistryExtractionError):
            probe.payload("26.3", "a" * 64, synthetic(("minecraft:forest",)))


    def test_resource_inventory_is_not_protocol_id_evidence(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            biome_dir = root / "data/minecraft/worldgen/biome"
            biome_dir.mkdir(parents=True)
            (biome_dir / "plains.json").write_text(
                json.dumps({"temperature": 0.8}), encoding="utf-8"
            )
            (biome_dir / "forest.json").write_text(
                json.dumps({"temperature": 0.7}), encoding="utf-8"
            )
            names = probe.source_biome_inventory(root)
            self.assertEqual(
                names, ("minecraft:forest", "minecraft:plains"),
            )
            evidence = probe.candidate_payload(
                probe.TARGET_VERSION, "a" * 64, names
            )
            self.assertEqual(evidence["protocol_id_authority"], "NOT_QUALIFIED")
            self.assertEqual(evidence["biome_resource_count"], 2)
            self.assertNotIn("names_by_protocol_id", evidence)
            (biome_dir / "forest.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(probe.RegistryExtractionError):
                probe.source_biome_inventory(root)

    def test_missing_dynamic_biome_resource_inventory_fails_closed(self) -> None:
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as dirname:
            with self.assertRaises(probe.RegistryExtractionError):
                probe.source_biome_inventory(Path(dirname))


if __name__ == "__main__":
    unittest.main()
