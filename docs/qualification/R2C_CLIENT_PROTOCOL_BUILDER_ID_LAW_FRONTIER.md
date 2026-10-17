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

## Remaining source-law proof

This still does **not** establish that the ultimately bound Play
`IdDispatchCodec` or other concrete dispatch code uses the list
index unchanged as the numeric network packet ID. The independent
source review must trace:

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
