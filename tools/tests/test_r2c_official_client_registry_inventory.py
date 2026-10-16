"""Official *client* artifacts remain candidates until independently reviewed."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_official_client_registry_inventory as probe

MAPPINGS = """net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl -> z.a:
    1:1:void handleRegistryData(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket) -> a
    2:2:void handleUpdateTags(net.minecraft.network.protocol.configuration.ClientboundUpdateTagsPacket) -> b
    3:3:void close() -> c
net.minecraft.client.multiplayer.OtherClient -> z.b:
    1:1:void ignore() -> a
"""


def meta() -> dict:
    return {
        "id": "26.2",
        "downloads": {
            "client": {"url": "https://example.invalid/client.jar",
                       "sha1": "a" * 40, "size": 123},
            "client_mappings": {"url": "https://example.invalid/mappings.txt",
                                "sha1": "b" * 40, "size": 234},
        },
    }


class OfficialClientSourceFrontierTests(unittest.TestCase):
    def test_bounded_mapped_receiver_is_not_client_invocation_proof(self) -> None:
        [candidate] = probe.receiver_candidates(MAPPINGS)
        self.assertEqual(
            candidate["mapped_class"],
            "net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl",
        )
        self.assertEqual(candidate["official_obfuscated_class"], "z.a")
        self.assertEqual(candidate["registry_related_method_names"],
                         ["handleRegistryData", "handleUpdateTags"])
        with self.assertRaisesRegex(ValueError, "no unique bounded"):
            probe.receiver_candidates(
                "net.minecraft.server.ServerConfigurationListener -> z.a:\n"
                "    void handleRegistryData() -> x\n"
            )
        with self.assertRaisesRegex(ValueError, "no registry method"):
            probe.receiver_candidates(
                "net.minecraft.client.multiplayer.ClientConfigurationListener -> z.a:\n"
                "    void handleTags() -> x\n"
            )

    def test_metadata_must_have_official_identity_fields(self) -> None:
        self.assertEqual(probe.required_asset(meta(), "client")["size"], 123)
        for invalid in [
            {"url": "http://example.invalid/x", "sha1": "a" * 40, "size": 12},
            {"url": "https://example.invalid/x", "sha1": "short", "size": 12},
            {"url": "https://example.invalid/x", "sha1": "a" * 40, "size": 0},
            {"url": "https://example.invalid/x", "sha1": "a" * 40, "size": True},
            {"url": "https://example.invalid/x", "sha1": "a" * 40},
        ]:
            data = meta()
            data["downloads"]["client"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                probe.required_asset(data, "client")
        with self.assertRaises(ValueError):
            probe.required_asset(meta(), "server")

    def test_lock_rejects_version_and_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lock.toml"
            lock.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                '[source]\narchive_sha256 = "' + probe.SOURCE_SHA256 + '"\n'
            )
            probe.identity_lock(lock)
            lock.write_text(lock.read_text().replace("776", "777"))
            with self.assertRaises(ValueError):
                probe.identity_lock(lock)

    def test_discovery_is_ephemeral_and_never_self_admits(self) -> None:
        def fake_download(url: str, output: Path, sha1: str, size: int) -> None:
            del sha1, size
            output.write_bytes(MAPPINGS.encode() if "mappings" in url else b"client-jvm-bytes")

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(probe.official, "download", side_effect=fake_download):
                result = probe.discover(meta(), Path(tmp))
        self.assertEqual(result["target"]["protocol"], 776)
        self.assertEqual(result["artifacts"]["client"]["observed_sha256_candidate"],
                         hashlib.sha256(b"client-jvm-bytes").hexdigest())
        self.assertFalse(result["source_inspected"])
        self.assertFalse(result["client_handler_invocation_proven"])
        self.assertFalse(result["client_numeric_id_assignment_proven"])
        self.assertFalse(result["production_admitted"])
        self.assertEqual(len(result["client_configuration_listener_candidates"]), 1)
        self.assertNotIn("client-jvm-bytes", json.dumps(result))
        self.assertNotIn("net.minecraft.server.ServerConfigurationListener",
                         json.dumps(result))


if __name__ == "__main__":
    unittest.main()
