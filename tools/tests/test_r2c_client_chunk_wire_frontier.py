"""Fail-closed official chunk packet client signature and field/method edge fixtures."""
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
import r2c_client_chunk_wire_frontier as probe

BYTECODE=b"\xca\xfe\xba\xbesynthetic-codec-class"

def synthetic(class_name: str) -> str:
    return f"""public final class {class_name} {{
  public void write(net.minecraft.network.FriendlyByteBuf);
    Code:
       0: aload_1
       1: getfield #10 // Field chunkX:I
       4: invokevirtual #11 // Method net/minecraft/network/FriendlyByteBuf.writeInt:(I)Lnet/minecraft/network/FriendlyByteBuf;
       7: aload_1
       8: invokevirtual #12 // Method net/minecraft/network/FriendlyByteBuf.writeVarInt:(I)Lnet/minecraft/network/FriendlyByteBuf;
      11: return
  public net.minecraft.network.protocol.PacketType type();
    Code:
       0: getstatic #14 // Field net/minecraft/network/protocol/game/GamePacketTypes.CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT:Lnet/minecraft/network/protocol/PacketType;
       3: areturn
  public void unrelated();
    Code:
       0: invokevirtual #17 // Method misleading/wire.fake:()V
       3: return
}}
"""

def mock_javap(args: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    del kwargs
    return subprocess.CompletedProcess(args,0,synthetic(args[-1]),"")

def jar_bytes(missing: str | None = None) -> bytes:
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as jar:
        for cls in probe.ROOTS:
            if cls != missing:
                jar.writestr(cls.replace(".","/")+".class", BYTECODE)
    return out.getvalue()


class ChunkClientWireTests(unittest.TestCase):
    def test_exact_method_signatures_bound_symbols_and_no_admission(self) -> None:
        for name in probe.ROOTS:
            with self.subTest(name=name):
                item=probe.inspect_class(synthetic(name),name)
                self.assertEqual([m["name"] for m in item["candidate_methods"]],
                                 ["write","type"])
                self.assertFalse(item["outer_packet_wire_semantics_source_admitted"])
                [write,packet_type]=item["candidate_methods"]
                self.assertEqual(len(write["symbols"]),3)
                self.assertEqual(write["symbols"][0]["offset"],1)
                self.assertEqual(packet_type["symbols"][0]["opcode"],"getstatic")
                self.assertIn("GamePacketTypes.CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT",
                              packet_type["symbols"][0]["symbol_candidate"])
                self.assertNotIn("misleading/wire.fake",json.dumps(item))
                self.assertEqual(len(write["instruction_shape_sha256"]),64)

    def test_missing_malformed_and_ambiguous_method_fail_closed(self) -> None:
        cls=probe.ROOTS[0]
        original=synthetic(cls)
        with self.assertRaisesRegex(ValueError,"write method not inspectable"):
            probe.inspect_class(original.replace(" void write("," void other("),cls)
        with self.assertRaisesRegex(ValueError,"offsets not increasing"):
            probe.inspect_class(original.replace("8: invokevirtual","1: invokevirtual"),cls)
        with self.assertRaisesRegex(ValueError,"missing symbolic"):
            probe.inspect_class(original.replace("// Method","; Method"),cls)
        with self.assertRaisesRegex(ValueError,"oversized"):
            probe.inspect_class("x"*(probe.MAX_CLASS_JAVAP+1),cls)

    def test_artifact_lookup_and_source_free_nonadmission(self) -> None:
        original=jar_bytes()
        meta={"downloads":{"client":{"url":"https://example.invalid/client.jar",
                                     "sha1":"a"*40,"size":len(original)}}}
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"client.jar"
            target.write_bytes(original)
            with patch.object(probe.subprocess,"run",side_effect=mock_javap):
                items=probe.inspect_client(target)
                self.assertEqual(len(items),3)
            target.write_bytes(jar_bytes(probe.ROOTS[-1]))
            with patch.object(probe.subprocess,"run",side_effect=mock_javap):
                with self.assertRaisesRegex(ValueError,"missing or ambiguous"):
                    probe.inspect_client(target)
            def fake_download(url:str,path:Path,sha1:str,size:int) -> None:
                del url,sha1,size
                path.write_bytes(original)
            with patch.object(probe.receiver.official,"download",
                              side_effect=fake_download),patch.object(
                                  probe.subprocess,"run",side_effect=mock_javap):
                result=probe.discover(meta,Path(temp))
            self.assertEqual(result["official_client_sha256_candidate"],
                             hashlib.sha256(original).hexdigest())
            for key in ("packet_type_identity_admitted",
                        "serialized_field_order_admitted",
                        "source_var_sem_admitted","production_admitted"):
                self.assertFalse(result[key])
            self.assertNotIn("synthetic-codec-class",json.dumps(result))

if __name__=="__main__":
    unittest.main()
