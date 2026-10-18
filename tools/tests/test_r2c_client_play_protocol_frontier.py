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
    present=set(fields)|{"CLIENTBOUND_BUNDLE"}
    client_targets={11:"CLIENTBOUND_CHUNK_BATCH_FINISHED",
                    12:"CLIENTBOUND_CHUNK_BATCH_START",
                    45:"CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT",
                    94:"CLIENTBOUND_SET_CHUNK_CACHE_CENTER"}
    server_targets={11:"SERVERBOUND_CHUNK_BATCH_RECEIVED"}
    def method(name:str,values:dict[int,str],size:int,direction:str)->list[str]:
        rows=[f"  private static void {name}();","    Code:"]
        offset=0
        for i in range(size):
            token=("CLIENTBOUND_BUNDLE" if direction=="CLIENTBOUND" and i==0
                   else values.get(i,f"{direction}_TEST_{i}"))
            if token not in present:
                token=f"{direction}_TEST_{i}"
            rows.append(
                f"      {offset}: getstatic #11 // Field net/minecraft/network/protocol/game/GamePacketTypes.{token}:Lnet/minecraft/network/protocol/PacketType;"
            )
            offset+=3
            registrar=("withBundlePacket" if token=="CLIENTBOUND_BUNDLE" else "addPacket")
            rows.append(
                f"      {offset}: invokevirtual #14 // Method net/minecraft/network/protocol/ProtocolInfoBuilder.{registrar}:(Lnet/minecraft/network/protocol/PacketType;)Lnet/minecraft/network/protocol/ProtocolInfoBuilder;"
            )
            offset+=3
        rows.append(f"      {offset}: return")
        return rows
    return "\n".join([
        "public class net.minecraft.network.protocol.game.GameProtocols {",
        *method("lambda$static$2",client_targets,95,"CLIENTBOUND"),
        *method("lambda$static$1",server_targets,13,"SERVERBOUND"),
        "}",
    ])

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
        self.assertEqual(len(entry["selected_registration_methods"]),2)
        self.assertEqual(entry["complete_builder_argument_order_for_five_types_candidate"],
                         probe.EXPECTED_ORDINALS)
        methods=entry["selected_registration_methods"]
        self.assertEqual(methods[0]["first_registration_candidate"], {
            "field": "CLIENTBOUND_BUNDLE",
            "candidate_ordinal": 0,
            "getstatic_offset": 0,
            "add_packet_offset": 3,
            "bundle_registration": True,
        })
        self.assertFalse(methods[1]["first_registration_candidate"]["bundle_registration"])
        self.assertEqual(methods[0]["candidate_complete_add_packet_registrations"],95)
        self.assertEqual(methods[1]["candidate_complete_add_packet_registrations"],13)
        self.assertEqual([m["field"] for method in methods
                          for m in method["packet_field_references"]],
                         [
                             "CLIENTBOUND_CHUNK_BATCH_FINISHED",
                             "CLIENTBOUND_CHUNK_BATCH_START",
                             "CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT",
                             "CLIENTBOUND_SET_CHUNK_CACHE_CENTER",
                             "SERVERBOUND_CHUNK_BATCH_RECEIVED",
                         ])
        self.assertTrue(all(m["no_conditional_builder_registration_observed"] for m in methods))
        self.assertFalse(entry["builder_append_to_numeric_id_law_proven"])
        self.assertTrue(entry["serverbound_ack_builder_index_observed_11"])
        self.assertNotIn("synthetic-client-game-protocol",json.dumps(entry))

    def test_missing_duplicate_and_oversized_clients_fail_closed(self)->None:
        with self.assertRaisesRegex(ValueError,"missing required"):
            probe.inspect(fixture(probe.FIELDS[:-1]))
        with self.assertRaisesRegex(ValueError,"unbounded"):
            probe.inspect("x"*(probe.MAX_JAVAP+1))
        many=fixture().replace(
            "GamePacketTypes.CLIENTBOUND_TEST_1:",
            "GamePacketTypes.CLIENTBOUND_CHUNK_BATCH_START:"
        )
        with self.assertRaisesRegex(ValueError,"duplicate"):
            probe.inspect(many)
        invalid=fixture().replace(
            "ProtocolInfoBuilder.addPacket:", "ProtocolInfoBuilder.unrelated:",1
        )
        with self.assertRaisesRegex(ValueError,"two packet types"):
            probe.inspect(invalid)
        branched=fixture().replace(
            "      6: getstatic", "      6: ifnull 99"
        )
        with self.assertRaisesRegex(ValueError,"non-linear"):
            probe.inspect(branched)
        # The bundle is an actual first entry in the clientbound list,
        # not a meta-packet that may be added later or subtracted from IDs.
        without_bundle=fixture().replace(
            "GamePacketTypes.CLIENTBOUND_BUNDLE:",
            "GamePacketTypes.CLIENTBOUND_TEST_0:"
        )
        with self.assertRaisesRegex(ValueError,"bundle builder consumes wrong packet type"):
            probe.inspect(without_bundle)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            probe.inspect(fixture().replace(
                "GamePacketTypes.CLIENTBOUND_TEST_1:",
                "GamePacketTypes.CLIENTBOUND_BUNDLE:"
            ).replace(
                "ProtocolInfoBuilder.addPacket:",
                "ProtocolInfoBuilder.withBundlePacket:",1
            ))
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
        self.assertEqual(
            report["protocol_registration_candidate"]["complete_builder_argument_order_for_five_types_candidate"],
            probe.EXPECTED_ORDINALS,
        )
        self.assertFalse(report["source_var_sem_admitted"])
        self.assertFalse(report["production_admitted"])
        self.assertFalse(report["protocol_registration_candidate"]["numeric_packet_ids_admitted"])

if __name__=="__main__":
    unittest.main()
