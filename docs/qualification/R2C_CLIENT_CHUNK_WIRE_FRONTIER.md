# R2C — exact client 26.2 chunk-with-light codec counterpart

**Status: stock-client, source-free bytecode evidence; not source/VAR/SEM
admission.** This is independent evidence about the *unmodified receiving
client's* packet class bodies, separate from the pinned official server-source
VAR/SEM plan at `R2C_CHUNK_WIRE_SOURCE_FRONTIER.md`.

## Exact artifact and review scope

The Java 25 workflow obtains Mojang's official unobfuscated **26.2 client
JAR**, validates official SHA-1/size and fingerprints full client SHA-256.
`tools/r2c_client_chunk_wire_frontier.py` inspects exactly three packet
implementation classes, with bounded method bodies and method-local
symbolic field/method references:

| Official stock-client class | Exact class SHA-256 |
| --- | --- |
| `ClientboundLevelChunkWithLightPacket` | `19dc8da92e1fce46d65e84e227b910950d71a3fc2b7c8bcc007360df1c2134ad` |
| `ClientboundLevelChunkPacketData` | `7bbd72318995b2206bd25a7ee137cb1b892d5c40d1e829132af91757f1db5654` |
| `ClientboundLightUpdatePacketData` | `2f00e4382a7a61ef29b6dc79196aeccbcbc9ce3e97d5b9ef89b8d5a44991cda7` |

These class hashes, exact `write`-method code-shape hashes, symbolic
references and bytecode offsets are **frozen in the workflow**; a
changed official class or call site fails closed. The parser treats
fully qualified Java constructors and the class static initializer as
independent bytecode boundaries, avoiding false cross-method evidence.

## Source-free official client's exact `write` path

The stock-client `ClientboundLevelChunkWithLightPacket.write` places:

- X coordinate at bytecode `getfield` offset 2, followed by
  `RegistryFriendlyByteBuf.writeInt` offset 5;
- Z coordinate at 11, followed by `writeInt` at 14;
- `chunkData.write(RegistryFriendlyByteBuf)` at 23;
- `lightData.write(FriendlyByteBuf)` at 31.

Its `type()` reads
`GamePacketTypes.CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT` from a
`getstatic` instruction at offset 0. This confirms the *class's
packet-type constant reference*, not the numeric packet-table ID.

The stock client's `ClientboundLevelChunkPacketData.write` executes:

1. `HEIGHTMAPS_STREAM_CODEC.encode(heightmaps)` at offset 8;
2. `RegistryFriendlyByteBuf.writeVarInt(buffer.length)` at 19
   and `writeBytes(buffer)` at 28;
3. `BlockEntityInfo.LIST_STREAM_CODEC.encode(blockEntitiesData)`
   at 40.

The stock client's `ClientboundLightUpdatePacketData.write` performs
`writeBitSet` for `skyYMask` at 5, `blockYMask` at 13,
`emptySkyYMask` at 21 and `emptyBlockYMask` at 29,
then `writeCollection` for `skyUpdates` at 40 and
`blockUpdates` at 51, both using the same
`DATA_LAYER_STREAM_CODEC` field.

The CI asserts exactly those call sites, owners and sequence, including
frozen source-free whole-method SHA-256 identities. This gives us an
independently observed client-side serialization counterpart for the
candidate assembled chunk body without inventing packet fields.

## Remaining finite proof boundary

This is **not** yet a production admitted packet encoder. The
independent official **server** source review must still prove the
numeric protocol-776 packet registration identity, signed coordinates,
heightmap stream codec body, section-palette framing, empty/nonempty
block-entity list encoding, light bitset and data layer framing,
and packet publication/batch ACK lifecycle. Separate issue #285 must
admit the 66 client biome numeric IDs; the 32,366-state heightmap
runtime table has its own independent VAR/SEM gate.

The official JAR, binary classfiles, Java source and disassembly
are never committed or preserved as workflow artifacts. Only concise
source-free identity fingerprints and bytecode-symbol offsets are
retained for seven days.

**Do not enable Play chunk publication or promote the
`source_var_sem_admitted`, `packet_type_identity_admitted`,
`serialized_field_order_admitted` or `production_admitted` flags
on the strength of this client-side witness.**
