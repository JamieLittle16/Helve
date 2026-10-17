"""Fail-closed candidate collection for exact client 26.2 Play packet registrations."""
from __future__ import annotations
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import r2c_client_play_protocol_frontier as probe

BYTECODE=b"\xca\xfe\xba\xbesynthetic-client-game-protocol"

def fixture(fields:tuple[str,...]=probe.FIELDS)->str:
    rows=[]
    offset=0
    for name in fields:
        rows.append(f"      {offset}: getstatic #11 // Field net/minecraft/network/protocol/game/GamePacketTypes.{name}:Lnet/minecraft/network/protocol/PacketType;")
        offset+=3
        rows.append(f"      {offset}: invokevirtual #14 // Method net/minecraft/network/ProtocolInfoBuilder.addPacket:(Lnet/minecraft/network/protocol/PacketType;)Lnet/minecraft/network/ProtocolInfoBuilder;")
        offset+=3
    rows.append(f"      {offset}: return")
    return "\n".join(["public class net.minecraft.network.protocol.game.GameProtocols {",
        "  static {};","    Code:",*rows,"}"])

def jar_bytes(with_class:bool=True)->bytes:
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as jar:
        if with_class:
            jar.writestr(probe.OWNER.replace(".","/")+".class",BYTECODE)
    return out.getvalue()

def mock_javap(args:list[str],**kwargs:object)->subprocess.CompletedProcess:
    del kwargs
    return subprocess.CompletedProcess(args,0,fixture(),"")

class ClientPlayProtocolFrontierTests(unittest.TestCase):
    def test_exact_five_method_local_packet_fields_and_non_admission(self)->None:
        entry=probe.inspect(fixture())
        self.assertEqual(entry["target_field_reference_count"],5)
        self.assertTrue(entry["all_five_packet_constants_referenced"])
        self.assertFalse(entry["ordered_ordinal_assignment_proven"])
        self.assertFalse(entry["numeric_packet_ids_admitted"])
        self.assertFalse(entry["play_bundle_and_direction_law_admitted"])
        self.assertEqual(len(entry["selected_registration_methods"]),1)
        method=entry["selected_registration_methods"][0]
        self.assertEqual([m["field"] for m in method["packet_field_references"]],
                         list(probe.FIELDS))
        self.assertEqual(len(method["bounded_nearby_invocation_sites_candidate"]),5)
        self.assertNotIn("synthetic-client-game-protocol",json.dumps(entry))

    def test_missing_duplicate_and_oversized_clients_fail_closed(self)->None:
        with self.assertRaisesRegex(ValueError,"missing required"):
            probe.inspect(fixture(probe.FIELDS[:-1]))
        with self.assertRaisesRegex(ValueError,"unbounded"):
            probe.inspect("x"*(probe.MAX_JAVAP+1))
        with self.assertRaisesRegex(ValueError,"too many target-registration"):
            probe.inspect(fixture(probe.FIELDS*12))
        with self.assertRaisesRegex(ValueError,"cannot parse"):
            probe.inspect("nothing here")

    def test_full_pipeline_has_no_authority(self)->None:
        raw=jar_bytes()
        meta={"downloads":{"client":{"url":"https://example.invalid/minecraft-client.jar",
                                     "sha1":"b"*40,"size":len(raw)}}}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"client.jar"
            path.write_bytes(jar_bytes(False))
            with self.assertRaisesRegex(ValueError,"missing/ambiguous"):
                probe.inspect if False else None
                with patch.object(probe.subprocess,"run",side_effect=mock_javap):
                    # Test the actual missing-class check without hitting network.
                    with patch.object(probe.official_client.official,"download",
                                      side_effect=lambda url,dst,sha1,size:dst.write_bytes(jar_bytes(False))):
                        probe.discover(meta,Path(temp))
            def download(url:str,dest:Path,sha1:str,size:int)->None:
                del url,sha1,size
                dest.write_bytes(raw)
            with patch.object(probe.official_client.official,"download",side_effect=download),\
                patch.object(probe.subprocess,"run",side_effect=mock_javap):
                report=probe.discover(meta,Path(temp))
        self.assertEqual(report["official_client_sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(report["protocol_registration_candidate"]["target_field_reference_count"],5)
        self.assertFalse(report["source_var_sem_admitted"])
        self.assertFalse(report["production_admitted"])
        self.assertFalse(report["protocol_registration_candidate"]["numeric_packet_ids_admitted"])

if __name__=="__main__":
    unittest.main()
