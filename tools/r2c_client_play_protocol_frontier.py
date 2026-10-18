#!/usr/bin/env python3
"""Bound actual receiving-client 26.2 PLAY packet type registration evidence.

Unlike packet payload shape review, this probes the stock client protocol
packet-registration *owner* for the five R2C-relevant packet type fields.
The evidence is deliberately source-free. Candidate ordinals are not
claimed until every registration chain, bundle and direction law is
independently verified; production admission remains false.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import r2c_official_client_registry_inventory as official_client

KIND="r2c-26_2-stock-client-play-packet-registration-frontier-v1"
OWNER="net.minecraft.network.protocol.game.GameProtocols"
MAX_JAVAP=6_000_000
MAX_CLASS_BYTES=2_000_000
MAX_ROWS=15_000
MAX_MATCHES=48
FIELDS=(
    "CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT",
    "CLIENTBOUND_SET_CHUNK_CACHE_CENTER",
    "CLIENTBOUND_CHUNK_BATCH_START",
    "CLIENTBOUND_CHUNK_BATCH_FINISHED",
    "SERVERBOUND_CHUNK_BATCH_RECEIVED",
)
ROW=re.compile(r"^\s*(\d+):\s+([a-z][a-z_0-9]*)\b(.*)$")
DECL=re.compile(r"^  [^{};]+\([^;]*\)(?: throws [^;]+)?;$")
GETSTATIC_TYPE=re.compile(
    r"\b([A-Za-z0-9_]+PacketTypes)\.(CLIENTBOUND_[A-Z0-9_]+|SERVERBOUND_[A-Z0-9_]+):"
)

REGISTER_CALL="ProtocolInfoBuilder.addPacket:"
REGISTRATION_METHODS={
    "lambda$static$2":"clientbound",
    "lambda$static$1":"serverbound",
}
EXPECTED_ORDINALS={
    "CLIENTBOUND_CHUNK_BATCH_FINISHED":11,
    "CLIENTBOUND_CHUNK_BATCH_START":12,
    "CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT":45,
    "CLIENTBOUND_SET_CHUNK_CACHE_CENTER":94,
    # Stock-client builder position; keep numeric-ID source admission
    # independent from the builder argument ordering.
    "SERVERBOUND_CHUNK_BATCH_RECEIVED":11,
}

def consecutive_registration_order(rows:list[tuple[int,str,str]], direction:str)->list[dict]:
    """Pair every packet-type getstatic with precisely one builder addPacket.

    This counts ALL registrations in the named method, not only five targets.
    A multi-packet preload, intervening branch, unexplained add or missing
    registration fails. This pins the constructor *argument ordering*, not
    the separate ProtocolInfoBuilder's finished numeric-ID law.
    """
    packet=None
    entries=[]
    seen=set()
    for i,(offset,op,operand) in enumerate(rows):
        if op.startswith(("if","goto","jsr")) or op in ("tableswitch","lookupswitch"):
            raise ValueError("packet registration builder has non-linear control flow")
        field=GETSTATIC_TYPE.search(operand) if op=="getstatic" else None
        if field:
            if packet is not None:
                raise ValueError(
                    f"two packet types loaded before registration call: "
                    f"previous={packet[0]}@{packet[1]} next={field.group(2)}@{offset}; "
                    f"previous packet registration method may need separate review"
                )
            name=field.group(2)
            if not name.startswith(direction.upper()+"_"):
                raise ValueError("packet direction mismatches named builder")
            packet=(name,offset)
        if op.startswith("invoke") and "ProtocolInfoBuilder." in operand:
            is_direct=REGISTER_CALL in operand
            is_bundle=(
                "ProtocolInfoBuilder.addBundlePacket:" in operand
                or "ProtocolInfoBuilder.withBundlePacket:" in operand
            )
            if is_direct or is_bundle:
                if packet is None:
                    raise ValueError(
                        f"registration call has no preceding packet type: "
                        f"{direction}@{offset} {operand[:200]}; "
                        f"prior_opcodes={[(o,k,r[:150]) for o,k,r in rows[max(0,i-6):i+1]]}"
                    )
                name,loaded=packet
                if is_bundle and name!="CLIENTBOUND_BUNDLE":
                    raise ValueError("bundle builder consumes wrong packet type")
                if is_direct and name=="CLIENTBOUND_BUNDLE":
                    raise ValueError("bundle packet unexpectedly uses ordinary addPacket")
                if name in seen:
                    raise ValueError("duplicate stock client packet type registration")
                seen.add(name)
                entries.append({
                    "field":name,"candidate_ordinal":len(entries),
                    "getstatic_offset":loaded,"add_packet_offset":offset,
                    "bundle_registration":is_bundle,
                })
                packet=None
            if len(entries)>MAX_ROWS//3:
                raise ValueError("unbounded packet builder registrations")
    if packet is not None or not entries:
        raise ValueError("incomplete packet type registration chain")
    # This is a real ordinal, not an out-of-band protocol flag. The
    # clientbound bundler must consume slot zero; it must never shift the
    # independently counted ordinary addPacket registrations afterward.
    if direction == "clientbound":
        if (entries[0]["field"] != "CLIENTBOUND_BUNDLE"
                or not entries[0]["bundle_registration"]):
            raise ValueError("clientbound Play bundle is not registration zero")
        if sum(entry["bundle_registration"] for entry in entries) != 1:
            raise ValueError("ambiguous clientbound Play bundle registration")
    elif any(entry["bundle_registration"] for entry in entries):
        raise ValueError("serverbound Play builder unexpectedly contains a bundle")
    return entries

def inspect(disassembly: str) -> dict:
    if not 0 < len(disassembly) <= MAX_JAVAP:
        raise ValueError("unbounded official protocol packet registration disassembly")
    current="unselected"
    counts={}
    lines=disassembly.splitlines()
    method_rows=[]
    matched=[]
    methods=[]
    for line in lines:
        if DECL.fullmatch(line):
            current=line.split("(",1)[0].split()[-1].rsplit(".",1)[-1]
            counts[current]=counts.get(current,0)+1
            if counts[current]!=1:
                # Overloaded method names can have different signatures;
                # explicitly mark the signature hash in the evidence.
                current=f"{current}#{counts[current]}"
            continue
        if line.strip()=="static {};":
            current="<clinit>"
            continue
        row=ROW.match(line)
        if not row:
            continue
        offset,opcode,operand=int(row.group(1)),row.group(2),row.group(3).strip()
        method_rows.append((current,offset,opcode,operand))
        if len(method_rows)>MAX_ROWS:
            raise ValueError("too many protocol registration instruction rows")
        if opcode=="getstatic" and "// Field " in operand:
            match=GETSTATIC_TYPE.search(operand)
            if match and match.group(2) in FIELDS:
                item={"method":current,"offset":offset,"field":match.group(2)}
                matched.append(item)
                if len(matched)>MAX_MATCHES:
                    raise ValueError("too many target-registration witnesses")
    if not method_rows:
        raise ValueError("cannot parse official protocol owner bytecode")
    names={m["field"] for m in matched}
    if not set(FIELDS).issubset(names):
        raise ValueError("official GameProtocols missing required R2C packet type references: "
                         +",".join(sorted(set(FIELDS)-names)))
    for method in dict.fromkeys(row[0] for row in method_rows):
        rows=[(n,op,rest) for name,n,op,rest in method_rows if name==method]
        selections=[m for m in matched if m["method"]==method]
        if not selections:
            continue
        invocations=[
            {"offset":offset,"opcode":op,
             "owner_target_candidate":rest.split("// ",1)[1][:320]}
            for offset,op,rest in rows
            if op.startswith("invoke") and "// " in rest
            and any(0<=offset-sel["offset"]<=56 for sel in selections)
        ]
        order=[]
        if method in REGISTRATION_METHODS:
            order=consecutive_registration_order(rows,REGISTRATION_METHODS[method])
            present={entry["field"]:entry["candidate_ordinal"] for entry in order}
            for name,ordinal in EXPECTED_ORDINALS.items():
                if name in present and present[name]!=ordinal:
                    raise ValueError(
                        f"official client {name} builder index drift: "
                        f"{present[name]} != {ordinal}"
                    )
        methods.append({
            "candidate_complete_add_packet_registrations":len(order),
            "first_registration_candidate":order[0] if order else None,
            "target_packet_ordinals_candidate":[
                entry for entry in order if entry["field"] in FIELDS
            ],
            "no_conditional_builder_registration_observed":bool(order),
            "method_name":method,
            "instruction_count":len(rows),
            "all_instructions_sha256":hashlib.sha256(
                "\n".join(f"{n}:{op} {rest}" for n,op,rest in rows).encode()
            ).hexdigest(),
            "packet_field_references":selections,
            "bounded_nearby_invocation_sites_candidate":invocations,
            "nearby_invocation_sites_retained":True,
        })
        if len(invocations)>256:
            raise ValueError("unbounded protocol-registration invoke sites")
    joined={
        item["field"]:item["candidate_ordinal"]
        for method in methods
        for item in method["target_packet_ordinals_candidate"]
    }
    if joined!=EXPECTED_ORDINALS:
        raise ValueError("exact five official Play packet registration ordinals incomplete")
    return {
        "complete_builder_argument_order_for_five_types_candidate":joined,
        "builder_append_to_numeric_id_law_proven":False,
        "serverbound_ack_builder_index_observed_11":True,
        "owner": OWNER,
        "selected_registration_methods": methods,
        "target_field_reference_count":len(matched),
        "all_five_packet_constants_referenced":True,
        "ordered_ordinal_assignment_proven":False,
        "numeric_packet_ids_admitted":False,
        "play_bundle_and_direction_law_admitted":False,
    }

def discover(meta:dict,scratch:Path)->dict:
    asset=official_client.required_client(meta)
    client=scratch/"26.2-client.jar"
    official_client.official.download(asset["url"],client,asset["sha1"],asset["size"])
    with zipfile.ZipFile(client) as jar:
        path=OWNER.replace(".","/")+".class"
        if jar.namelist().count(path)!=1:
            raise ValueError("missing/ambiguous stock client GameProtocols")
        raw=jar.read(path)
        if not 4<=len(raw)<=MAX_CLASS_BYTES or raw[:4]!=b"\xca\xfe\xba\xbe":
            raise ValueError("invalid official GameProtocols class")
    proc=subprocess.run(["javap","-p","-c","-classpath",str(client),OWNER],
                        capture_output=True,text=True,check=False,timeout=45)
    if proc.returncode or not proc.stdout:
        raise ValueError("official client GameProtocols javap unavailable")
    proof=inspect(proc.stdout)
    proof["classfile_sha256"]=hashlib.sha256(raw).hexdigest()
    return {
        "schema":1,"kind":KIND,
        "target":{"minecraft":"26.2","protocol":776,"data_version":4903},
        "official_client_sha1":asset["sha1"],
        "official_client_sha256":official_client.official.sha256_file(client),
        "protocol_registration_candidate":proof,
        "source_archive_sha256":official_client.SOURCE_SHA256,
        "source_var_sem_admitted":False,
        "production_admitted":False,
    }

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("client packet registration output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(official_client.REPO.resolve()):
            raise ValueError("client review evidence must stay outside repository")
        official_client.identity_lock(official_client.LOCK)
        with tempfile.TemporaryDirectory(prefix="helve-r2c-play-protocol-") as temp:
            result=discover(official_client.official_version_metadata(),Path(temp))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired,
            zipfile.BadZipFile) as exc:
        print(f"stock client Play protocol candidate rejected: {exc}",file=sys.stderr)
        return 2
    print("Stock client exact R2C packet registration references observed; "
          "numeric IDs and source admission FALSE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
