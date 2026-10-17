# R2C — 26.2 serverbound chunk batch ACK numeric ID correction

**Exact target:** Minecraft Java 26.2 / protocol 776 / DataVersion 4903.
**Status:** numeric packet candidate corrected from 12 to **11**;
full source VAR/SEM, biome registry and world packet admission remain blocked.

The dedicated official, SHA-1/size-checked Mojang **client** GameProtocols
bytecode review found its serverbound `SERVERBOUND_CHUNK_BATCH_RECEIVED`
type added to the protocol builder at zero-based position **11** in
`GameProtocols.lambda$static$1` (getstatic bytecode offset 100;
`ProtocolInfoBuilder.addPacket` at 106). The exact 211-instruction
method shape is SHA-256
`e317857a535331f9aa6a6827ed55d67fa2b723103400d45d9ad48dc60b54122a`.

The independent Go protocol-776 reference `github.com/ezchr/go-mcjava/v776`
also lists serverbound Play `chunk_batch_received` as **0x0B** and
`client_command` as **0x0C**. That independently corroborates the
stock-client builder position; the exact stock client remains the
primary identity evidence, not the third-party reference.

The previous Helve ID **12** was the adjacent serverbound command packet;
its use for batch ACK would silently leave the actual client ACK
unclaimed. The correction updates the 26.2 target constant, framed
decoder tests, batch/quota control tests, receipt-to-packet source tests
and the retained R2B/R2C ingress integration tests. A new negative test
ensures former ID 12 stays unclaimed **without consuming the buffer or
mutating the ACK cursor**.

Clientbound ID values (finish 11, start 12, chunk-with-light 45,
cache-centre 94) are **not** modified: packet IDs are directional.

**Important:** The change corrects a numeric candidate, not an independent
VAR/SEM admission. Full packet-type mapping, Play lifecycle, known-pack
numeric biome IDs and source-bound heightmap predicate admission are
still required to construct the uninhabited production R2C publication
capability. No user-facing chunk publication becomes enabled.
