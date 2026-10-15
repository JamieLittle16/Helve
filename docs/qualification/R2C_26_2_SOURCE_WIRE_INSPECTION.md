# R2C 26.2 — pinned-source chunk packet and registry inspection

**Status:** exact server-source inspection and COLD wire-scalar implementation.
**Not:** independent VAR/SEM admission of production world publication, biome IDs,
complete first-spawn profile, batching lifecycle or a stock-client visual demo.

## Input and provenance

Locally inspected the user-provided official Java 26.2 server source ZIP,
without checking any Mojang source into Helve.

- Pinned whole archive SHA-256:
  `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`
- `GameProtocols.java` file SHA-256:
  `bd883b1b79580ac6c9e95b1228e69123e7af99b0e80021725bb0df0bfd5d8339`
- `ProtocolInfoBuilder.java` file SHA-256:
  `b24fca6b3141d0d1296281991f83fd2f5e91101f427eec1cea1c5a6966d07cee`
- `ClientboundLevelChunkWithLightPacket.java` file SHA-256:
  `853a2e7f16f2291337301ef702dbcdb0ed8dec0b37e186dac035aa1f421237c0`
- `ClientboundLevelChunkPacketData.java` file SHA-256:
  `4af49cb792cc859074e145222388f4915d2f33c5edc2032fb9eb29dbaad38cc2`
- `ClientboundLightUpdatePacketData.java` file SHA-256:
  `682b2195dd4234abd8ce603b8bcf09007e9461d2e235faf05dbac7dd83489669`
- `PlayerChunkSender.java` file SHA-256:
  `eac549258221448bfbd27a0c562dc270221545101d3e2410cf8734b74066b290`
- `MappedRegistry.java` file SHA-256:
  `d5351583e7fe0eadb7587ec1ccbb1b0340662dc62cada04a37d6303239d3e86f`
- `ResourceManagerRegistryLoadTask.java` file SHA-256:
  `055690f1a5842beafe9875f0f6381635563c1dfc3ec7d4fb4d8b0b1524ee2f8e`
- `NetworkRegistryLoadTask.java` file SHA-256:
  `dc9d281b179da141bb2faaa3707a58e3a213ce8a837703ee7e6557a6c1b49404`
- `RegistrySynchronization.java` file SHA-256:
  `818347d9b07276f831367e5cb43d1f633a384f2c3da139198063b24b6ed37c32`
- `SynchronizeRegistriesTask.java` file SHA-256:
  `189dcf096ec102ca010d6f84b53025fbf4aa60640380491504c9cdab4c8226d7`
- `PalettedContainerFactory.java` file SHA-256:
  `db3cfdd5d731f08083d3e57529f5bcd256e3de5066b98500d8d1248c9bc32679`
- `ClientboundChunkBatchFinishedPacket.java` file SHA-256:
  `cbfd70c33e1b51bc96a648c528937be3fcee4f2045f0b803c05df3d0bd61ea13`
- `ServerboundChunkBatchReceivedPacket.java` file SHA-256:
  `16cafff7a016c1203310e0c511c47d629c5cba73174473125cc197e11d41a61a`
- `ClientboundSetChunkCacheCenterPacket.java` file SHA-256:
  `02f1d994ad9380df652015881785f9aa6fb846ecaf1a58d08ce71b96de10ce49`

All filenames above are relative to `src/net/minecraft/`. These are **raw
source-file SHA-256 hashes**, not Atlas-normalized declaration fingerprints.
The Atlas fingerprint-bound independent review pipeline must still run before
source gate promotion.

## Exact findings from the pinned source

1. **Packet IDs.** `ProtocolInfoBuilder.withBundlePacket` installs the
   clientbound Play bundle delimiter as codec entry zero. `GameProtocols`
   then registers packet codecs in list order. This yields clientbound
   `chunk_batch_finished = 11`, `chunk_batch_start = 12`,
   `level_chunk_with_light = 45`, `set_chunk_cache_center = 94`;
   serverbound `chunk_batch_received = 12`. Clientbound keepalive is 44,
   independently matching Helve's previously admitted R2A generated ID.

2. **Chunk payload.** `ClientboundLevelChunkWithLightPacket` writes signed
   big-endian i32 X and Z, then `ClientboundLevelChunkPacketData`, then
   `ClientboundLightUpdatePacketData`. Chunk data writes the client
   heightmap-map codec, a VarInt section byte count and sections, then the
   block-entity list codec. A verified source-resident *empty* list has
   zero-count VarInt encoding. Actual block-entity presence/exclusion in the
   selected saved world remains a receipt/import obligation.

3. **Light.** Four `BitSet` long-array fields appear in exact order:
   sky data, block data, sky empty, block empty. Next appear a VarInt list
   of sky 2,048-byte layers and then a VarInt list of block layers. The
   bitsets are serialized via the standard long-array codec, not raw
   fixed-width masks. The existing R2C candidate matches this field order.

4. **Heightmaps.** The client heightmaps are the enum types with numeric
   IDs 1, 4, 5. This matches the existing three-map candidate. The enum
   map codec does not entitle Helve to manufacture missing world state.

5. **Batching.** `PlayerChunkSender` sends a start packet, each selected
   chunk-with-light packet, and a finish packet containing VarInt count.
   For a remote (non-memory) connection the desired chunk rate is initially
   9, with a 0.01–64 clamp; one batch is initially allowed outstanding,
   rising to a limit of 10 after acknowledgement. Acknowledgement carries
   a big-endian IEEE-754 float. NaN selects 0.01, infinities clamp to the
   endpoints. Sending a complete world requires **stateful** pacing and
   an outstanding-batch acknowledgement lifetime; simply emitting two
   scalars around every chunk is not automatically equivalent.

6. **Cache center.** `ClientboundSetChunkCacheCenterPacket` encodes both
   chunk coordinates as signed (two's-complement) VarInts.
   `ChunkMap` publishes the center as view tracking changes. Initial
   chunk selection must still respect the actual bootstrap lifecycle.

7. **Loaded biome IDs.** `ResourceManagerRegistryLoadTask` sorts keys before
   registration; `MappedRegistry.register` appends to its dense by-ID
   table, and `RegistrySynchronization.packRegistry` publishes
   `listElements()` in that order. Accepted known packs affect whether
   entry contents are transmitted, not the identity/order of the entries.
   `NetworkRegistryLoadTask` preserves the ordered network list through
   `Util.sequence` then `registerElements`. The source's
   `PalettedContainerFactory` binds biome holder IDs directly to the
   active loaded registry. Together these server/source-shared laws explain
   the independent 66-ID byId/network candidate, **without** approving
   arbitrary pack profiles or inferring numeric IDs from sorted save names.

## Concrete implementation from this inspection

`helve-target-26-2::r2c_play_wire` now provides COLD scalar encoders for the
five exact ID-bound selected packet types, exact signed centre VarInts,
remote-batch start/finish/count bounds, serverbound acknowledgement decoding
and acknowledgement float normalization. Tests prove the packet scalars and
malformed-input behaviour. This does not add a second packet queue, runtime
protocol registry, resident copy, or HOT-path dependency.

## Phase-boundary packet capacity (R2C retained-driver widening)

R2B originally accepts packet bodies up to 65,536 bytes on the *same*
continuing driver. The pinned `ClientboundLevelChunkPacketData` constructor
checks its **section-byte** count against 2,097,152, independently of the
outer chunk position/heightmaps/block-entity/light fields. The actual outer
remote frame remains constrained by Minecraft's three-byte `VarInt21`
limit of 2,097,151 **total body** bytes. A packet body exceeding that
external limit is invalid; the inner section cap does not override it.

R2C may now raise the existing driver limits monotonically at the
`WorldProjection` handoff: 2,097,151 frame-body bytes, 3 MiB ingress,
4 MiB egress. The operation updates scalar limits **in place**, retaining
both original `Vec` allocations, unread fragmented ingress and pending
egress, and does not reserve 3/4 MiB on every join. All reductions fail
without mutating active data. No second driver, queue, socket or read-scratch
owner is introduced. The widening hook is dormant until the actual R2C
product route is source-admitted. The chosen 3/4 MiB budgets are explicit
Helve policy, **not** asserted as vanilla quotas.

## Selected known-pack Configuration biome order binding

Source-checked additional declarations from the identical pinned server archive:

- `ConfigurationProtocols.java` raw-file SHA-256
  `d718e44bba997b84ccc756c352ead42c7652e5fe396a65371becc2671b452655`
- `ClientboundRegistryDataPacket.java` raw-file SHA-256
  `5fcce02e360a61fefdb057f39067185876030e311804210c23dad3bec7d37409`

The 26.2 Configuration clientbound registry-data packet is ID **7**.
Its fields are a registry identifier then a `VarInt`-length list of
`RegistrySynchronization.PackedRegistryEntry`: each entry contains a
resource identifier and an optional NBT value. Under the selected
`minecraft:core@26.2` known-pack route, the frozen official runtime
cross-check observed 66 ordered biome keys with absent entry payloads.
Absent optional values use a zero boolean byte, which permits exact
bounded parsing without a generic NBT/registry runtime.

`helve-target-26-2::r2c_biome_config::borrow_core_biome_order` now
borrows those 66 keys in **actual sent order** from the immutable
Configuration packet bodies (ID 7, `minecraft:worldgen/biome`). It
rejects wrong cardinality, inline entry NBT, malformed bodies, duplicate
biome registry packets and trailing bytes. It copies no names, creates
only one 66-pointer COLD vector, and never sorts to assign IDs. The
validated `Target26_2R1xContext` exposes this through the narrow
`candidate_sent_biome_order` method.

This is a **configuration-image consistency observation**, not proof of
the client's numeric assignment or client content resolution. It does
not link into live publication and must not turn the 66-entry fixture
into independently admitted production authority. The client-side
VAR/SEM proof and complete selected profile remain open as described in
issue #285.

## Configuration-bound COLD import composition

The server's `r2c_configured_biomes` candidate ties the exact 66
ordered names borrowed from a validated immutable `Target26_2R1xContext`
to the existing `OrderedBiomeRegistry`. It keeps both the byte-owning
Configuration image and a small derived pointer array alive only for a
closure-scoped COLD import operation; no self-referential registry object
or copied name table becomes another owner.

The existing `ExactBiomeDecoder` can resolve each saved 4×4×4 biome
palette name directly to this transmitted-order `u16` identity, not
an alphabetic ranking. Tests compose synthetic Configuration registry
wire fields and actual schema-decoded biome-section NBT, deliberately
reversing names to prove that sorting cannot change IDs. Unknown saved
names and duplicate Configuration entries fail before world installation.

The bridge is deliberately not called in the live R2B playtest. It
does not bypass independent client numeric-ID assignment admission or
grant authority to its synthetic tests. The source-matching selected
Configuration branch and `R2C-BIOMES` gate must still be verified
before it can be used to publish native Play chunks.

## What still blocks production R2C

- The pinned source archive is a **server-source corpus**. The precise
  receiving client registry installation/lifecycle and full selected
  Configuration pack-profile parity still require independent closure and
  a recorded `R2C-BIOMES` VAR/SEM admission. Do not mark issue #285 done
  solely from this inspection.
- Commit source-free independent VAR/SEM records for the exact outer packet,
  empty block entities, initial light/heightmap code path and the observed
  publication lifecycle; run the pinned Atlas gate. The raw-file hashes here
  are review anchors, not independently approved VAR/SEM records.
- Integrate an acknowledgement-aware batch cursor on the retained
  `R2bPlaySession`, size its packet/egress buffers for actual selected
  chunks, and join a stock 26.2 client with a pinned pregenerated world.
- R2D world generation is **not** a dependency of the first R2C demo.

**No official Java source bytes or packet captures are stored here.**
