# R2C — receiving-client packet builder-to-wire ID closure

**Version:** Minecraft Java 26.2, protocol 776, DataVersion 4903.  
**Status:** exact stock-client JVM *call-site evidence*, **not yet** a verified
numeric-ID/source-SEM admission certificate.

## What is already established

PRs #348–349 resolved the client `GameProtocols` packet-type builder
argument order, including the important distinction between clientbound
and serverbound direction: candidate indices are 11 / 12 / 45 / 94 for
the relevant clientbound batch-finish, batch-start, chunk-with-light and
cache-centre packets, and **11** for serverbound chunk-batch receipt.
That corrected the earlier serverbound ACK candidate of 12.

This review picks up *after* those exact packet registration argument
positions; it does not rescan the 429- and 211-instruction
`GameProtocols.lambda$static$N` bodies.

## Official client implementation observed

`tools/r2c_client_packet_builder_frontier.py` downloads only Mojang's
official size/SHA-1 checked 26.2 unobfuscated **client**, validates the
repository's exact target/source lock and inspects the actual
`net.minecraft.network.protocol.ProtocolInfoBuilder` plus its five
nested classes. Class bytecode is never copied into the repo, CI output,
or artifacts.

The root class SHA-256 is pinned to
`7af68e5a84feaa5c7b4f2c6bff09e8ee2b8f679256624419428c774cf88e8bde`.
Its exact source-free method-shape witnesses include:

| Method | Code SHA-256 | Direct observed call sites |
| --- | --- | --- |
| First `addPacket` overload | `f1a20e916c0dcd8c3f321e42e2aab8fd6a56300f1cb1177fb3a53a9271017a27` | read `codecs` at bci 1; allocate `CodecEntry` bci 4; initialize entry bci 11; `List.add` bci 14 |
| Second `addPacket` overload | `1cd95818ae419881c72f65e3a9d584aec38a8a10cf804a8d22423a866c7dbaa8` | same four offsets and receiver/entry names |
| `withBundlePacket` | `01a8b43ca46c5e92a17c40aaff795558fe63820bbf55750a862723d52caf41fe` | bundle entry reaches `List.add` bci 28; `BundlerInfo.createForPacket` bci 38; `bundlerInfo` field store bci 41 |

All six actual classfile SHA-256s, method-shape hashes and ordered
instruction call sites are independently pinned by the dedicated
Java-25 CI workflow. The tests reject truncated classes, malformed
bytecode offsets, unsymbolized references and missing/duplicate roots.
Full class names, code-shape digests, and bounded target references
are the only retained evidence.

This is stronger than seeing a `GameProtocols.addPacket` call and
guessing at the result: the actual receiving-client builder *does*
have ordered mutable `codecs` list insertion sites. Importantly,
a bundle delimiter is itself inserted into the builder. Thus packet
ordinal evaluation must count its position rather than silently
subtracting a bundle entry.

## Downstream numeric dispatch law directly observed

The same official-client-only CI now follows actual call-site targets
further, without guessing new packet classes:

1. `ProtocolInfoBuilder.buildUnbound` copies the ordered `codecs`
   list with `List.copyOf` at bytecode offset 4. Both nested `bind`
   implementations feed that list into `buildPacketCodec`.
2. `buildPacketCodec` iterates the list and invokes
   `CodecEntry.addToBuilder` at bytecode offset 49.
   `CodecEntry.addToBuilder` invokes `ProtocolCodecBuilder.add` at
   offset 49, preserving the packet type alongside its stream codec.
3. `ProtocolCodecBuilder.add` delegates to
   `IdDispatchCodec$Builder.add` at offset 41, and `build` delegates
   to `IdDispatchCodec$Builder.build` at offset 4.
4. The *actual* `IdDispatchCodec$Builder.add` appends an entry to
   its `entries` list at offset 13. The 49-instruction
   `IdDispatchCodec$Builder.build` iterates that list
   (offsets 18, 25 and 34), obtains the current
   `Object2IntOpenHashMap.size` at offset 44, and calls
   `putIfAbsent` with the packet type at offset 56. Its distinct
   error branch creates an `IllegalStateException` for duplicate
   packet types; it snapshots `entries` with `List.copyOf`
   at offset 103 into the finished `IdDispatchCodec`.
5. The exact `IdDispatchCodec.decode` reads a network VarInt at
   bytecode offset 1, indexes `byId` with `List.get` at offset 41,
   and invokes the chosen entry's decoder at offset 55. The matching
   `encode` resolves the packet type through `toId.getOrDefault`
   at offset 17, emits it with `VarInt.write` at offset 50 and
   indexes the same `byId` table at offset 60 before encoding the
   packet body.

The relevant exact source-free method SHA-256 identities include:

| Method | Instruction SHA-256 |
| --- | --- |
| `ProtocolInfoBuilder.buildPacketCodec` | `39caa1a45b1bb0212ef922b1700fad0a92661e5cb130baf8fdd59f56e50bfeb4` |
| `ProtocolInfoBuilder$CodecEntry.addToBuilder` | `69488d19803f37955aac584fbbfd236631b05a10b17b9188efb375ca0d982593` |
| `ProtocolCodecBuilder.add` | `ede86bfae070b2bac3b2ac53a8885648d44a995cd3c2c68fcec91afb1e3014ff` |
| `ProtocolCodecBuilder.build` | `95dfd6fceb0869f43bfcaa92c13c5bae7dc48762eb77fcdd74ac09233cb66afc` |
| `IdDispatchCodec$Builder.add` | `ee260d95f5e0bbe233fa4875ef4c40c8d91a20dfa007474a08e0158237308c83` |
| `IdDispatchCodec$Builder.build` | `e20ada392294df45f305e29cef91f8a4f143cee33f7f05631f92817df0852fbc` |
| `IdDispatchCodec.decode` | `8749bdfc2418e725da921046cda9b5a50bf8486a9621bcd934e05882e9986938` |
| `IdDispatchCodec.encode` | `efe32a2a267cf7eb1cd25737f35534f4ae9cc2026a121e35d0a243ef88f4a8ea` |

The dedicated workflow pins the `ProtocolInfoBuilder`,
`ProtocolCodecBuilder`, `IdDispatchCodec` and builder classfile
hashes plus these precise offsets and opcode relationships, checking
the exact SHA/size verified Mojang client every run. This is
particularly strong *candidate evidence* that list ordinal equals
wire numeric ID for successful, nonduplicate registration.

## Remaining source-law proof

The bounded official client bytecode inspection now reaches the
finished `IdDispatchCodec` and both its VarInt read/write paths.
These necessary JVM witnesses do **not** substitute for independent
source/VAR/SEM evidence, a proof of all branch/exception/default-map
behaviour, or a stock-client network trial. The remaining independent
source review must certify:

1. Exactly how the `ProtocolInfoBuilder` list is bound/finalized,
   including the observed method/delegate and bundle delimiter.
2. Whether the selected bound dispatch encoder/decoder maps entries to
   numeric IDs directly from ordered list indexes, including duplicate
   rejection, cross-direction identity and exceptions.
3. Exact receiving-client Configuration known-pack/biome registration
   identity, source-fingerprinted complete heightmap predicates, and
   the separate first-Play ordering conditions.
4. Complete source-free VAR/SEM evidence through the independent
   admission gate before constructing the production
   `R2cSourceAdmission` capability and emitting chunk packets.

No client JAR, source excerpt, method disassembly or proprietary
binary is added. A green result here leaves `builder_append_to_numeric_id_law_proven`,
`independent_source_var_sem_admitted`, and `production_admitted`
**false**. Do not convert this necessary source witness into an
authorization for the live R2C product path.
