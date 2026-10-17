# R2C — stock-client Play packet numeric-ID registration frontier

**Java 26.2, protocol 776, DataVersion 4903. Status: source-free registration discovery; numeric IDs remain unadmitted.**

The existing client chunk/light wire codec review proves field serialization
call order and the exact chunk-with-light packet type constant reference.
It does **not** prove the numeric Play packet ID. This probe therefore
inspects the stock-client `net.minecraft.network.protocol.game.GameProtocols`
registration owner, rather than inventing a server-source proof.

The SHA/size checked official Mojang client JAR is downloaded into ephemeral
CI scratch with Java 25. Exactly the GameProtocols class is inspected;
method-local bytecode identities and references to five relevant packet
type fields are retained: chunk-with-light, cache centre, batch start,
batch finish, and serverbound batch received. For each selected method
the probe fingerprints all instruction rows and records only bounded
nearby registration calls. The parser rejects missing, oversized or
ambiguous evidence. No JAR, classfiles or disassembly are committed.

A `getstatic GamePacketTypes.CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT` reference
does **not** prove packet ID 45. The independent source review must
establish that it is used in the correct clientbound PLAY protocol builder,
enumerate every registration including bundling and zero-based indexing,
and independently bind this to the pinned server-source packet mapping.
The serverbound ACK belongs to a different direction and numeric table.

## Exact official-client candidate results

The Java 25 job has now scanned **all** game, cookie and other packet-type
registrations in the selected `GameProtocols` methods. It verified that
the clientbound bundle is registered specially, before ordinary packets.
Official class method bodies were fingerprinted and registered packet
types were matched to each `ProtocolInfoBuilder.addPacket` call in
a nonbranching method-local sequence. The independent CI gate freezes
the complete method-code identities:

- Clientbound `lambda$static$2`: 429 JVM instructions,
  SHA-256 `83b3c511b46a3575a4fbf0779ee145b01519404f5516ac83cb2aefdd13a81b21`.
- Serverbound `lambda$static$1`: 211 JVM instructions,
  SHA-256 `e317857a535331f9aa6a6827ed55d67fa2b723103400d45d9ad48dc60b54122a`.

| Packet | Client builder ordinal candidate |
| --- | ---: |
| Chunk-with-light | 45 |
| Set chunk cache centre | 94 |
| Chunk batch start | 12 |
| Chunk batch finish | 11 |
| Serverbound batch received | **11** |

**Important mismatch:** Helve's existing serverbound ACK *wire ID*
candidate is **12**, whereas the client's observed `addPacket` builder
position is **11**. Do **not** silently change the runtime ID or
silently treat this as a source admission. Independent review of the
`ProtocolInfoBuilder` output table, bundle/delimiter/reserved slots and
target PLAY direction is needed to determine the exact numeric ID.

The other four builder positions coincide with Helve's current
clientbound numeric candidates. They remain *structural evidence*
until the builder append-to-numeric-table semantics and server-side
source review are independently admitted.

The CI explicitly asserts ordered_ordinal_assignment_proven=false,
numeric_packet_ids_admitted=false, play_bundle_and_direction_law_admitted=false,
source_var_sem_admitted=false and production_admitted=false.

This discovery cannot unlock the uninhabited runtime `R2cSourceAdmission`
capability, publish a packet, or claim a stock-client visible-world demo.
