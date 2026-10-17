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

The CI explicitly asserts ordered_ordinal_assignment_proven=false,
numeric_packet_ids_admitted=false, play_bundle_and_direction_law_admitted=false,
source_var_sem_admitted=false and production_admitted=false.

This discovery cannot unlock the uninhabited runtime `R2cSourceAdmission`
capability, publish a packet, or claim a stock-client visible-world demo.
