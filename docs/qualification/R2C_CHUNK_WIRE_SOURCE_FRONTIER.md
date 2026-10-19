# R2C — Chunk-with-light wire-source closure frontier

**Current status: original discovery, first-pass source observations
and scoped direct-method second-pass now recorded; complete packet,
block-entity, pacing, and biome-ID source admission is still blocked.** This is independent of already-admitted R2C world-state
palette, heightmap, and light semantics.

Helve now has a dormant COLD candidate for the complete explicitly-empty
block-entity chunk-with-light body. The remaining correctness requirement is
not another storage system or packet encoder: it is an exact pinned 26.2 source
proof that the candidate's outer identity, fields and publication order agree
with vanilla.

## 18 October 2026: first stock-client palette fault and correction

A real Minecraft Java 26.2 client connected to the opt-in *test-only*
R2C nine-chunk sender, consumed the chunk batch and sent its batch ACK,
then failed while **applying** one `ClientboundLevelChunkWithLightPacket`:

```text
ArrayIndexOutOfBoundsException: Index 2 out of bounds for length 2
  at LinearPalette.read
  at PalettedContainer.read
  at LevelChunkSection.read
  at LevelChunk.replaceWithPacketData
```

The immediately actionable mismatch is the **extra VarInt packed-word
array length** in Helve's block and quart-biome containers. The
already-recorded selected 26.2
`SEM-NET-R2C-WORLD-BIOME-CONTAINER-WIRE` source law in
`vanilla/semantics/network/R2C_WORLD_STATE_SEMANTICS.md` specifies
a **fixed-size** long array, not a length-prefixed array. Both
`PackedBlockContainer` and `PackedBiomeSectionReference`
previously emitted `VarInt(words.len())` immediately before raw
longs; that shifts the client's packed bit values and can drive a
2-value local palette to invalid index 2. Both encoders now append the
words *directly* after the width byte and palette representation.
The raw word count is still internally exactly
`ceil(entries / floor(64 / bits))`; width zero writes no words.
The 26.2 `LevelChunkSection` field order **does** include the
non-air and fluid shorts and those are left intact.

This is a correction to an **existing dormant source candidate**, not
a declaration that all outer chunk/light/registry/known-pack source
review, visual-client qualification, or production admission has
closed. After landing, rerun the exact same clean-source live
diagnostic; record both the new console result and the original
client `latest.log`. Only observed rendered terrain with a
successful maintained connection qualifies as the first visual pass.

## Narrow, finite official-source review

The 4-class plan at
\`vanilla/reviews/network/r2c-chunk-wire-source-frontier.json\` freezes:

1. **ClientboundLevelChunkWithLightPacket**: registered Play packet ID,
   constructor, signed coordinates, target body ordering and codec.
2. **ClientboundLevelChunkPacketData**: section payload framing,
   heightmap-map encoding and block-entity inclusion, including exact
   absent/empty NBT semantics and VarInt list count.
3. **ClientboundLightUpdatePacketData**: four mask fields, sky/block
   array counts, layer widths and position.
4. **PlayerChunkSender**: first chunk send trigger, batching, client
   acknowledgement and ordering relative to the R2B world-entry handoff.

The *already admitted* R2C world-state source group should be **reused**
for the inner block/biome/height/light encoding laws. Do not repeat its
50+ source reviews. Biome runtime numeric assignment and client
registry synchronization remain separately blocked under issue #285,
even though the 66 loaded official runtime IDs match Configuration.

Run on the machine holding the pinned 26.2 official source ZIP:

\`\`\`sh
python3 tools/vanilla_atlas.py --db .crucible/vanilla/atlas.sqlite \
  verify-source "$HOME/Documents/mc-source/mc-src.zip" \
  --lock vanilla/vanilla.lock.toml

python3 tools/r2c_chunk_wire_source_frontier.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-r2c-chunk-wire-source-inventory.json
\`\`\`

The script refuses an unpinned source archive/Atlas, missing or
ambiguous class, excessive class methods, existing output, or output
under the repository. It produces only declaration fingerprints,
source-free hazard leads and explicit unresolved review questions. An
abstract declaration is flagged as declaration-only.

## 19 October 2026: exact outer-envelope direct-method second pass

The second-pass source-free evidence at
`vanilla/reviews/network/r2c-outer-envelope-second-pass-source-findings.json`
re-reads the already pinned 26.2 excerpt identities, *not* another broad
source tree or speculative packet. The five explicit method roots are the
chunk-with-light packet codec initializer (first-pass index 11),
constructor (12), `write(RegistryFriendlyByteBuf)` (13),
`ClientboundLevelChunkPacketData` receiving constructor (14), and
`ClientboundLightUpdatePacketData` receiving constructor (16).
The manifest keeps exact full body/excerpt SHA-256 pairs and source archive
identity. It retains the original first-pass parent and local private bundle
hash, without committing any official Java text.

**Directly observed, still unadmitted candidate laws:**

- The outer packet's send constructor obtains signed X/Z from
  `LevelChunk.getPos` and builds chunk and light data. Its writer
  emits X, Z, chunk data then light data, never light before chunk.
- The inner chunk receiving constructor consumes heightmaps,
  VarInt-length-prefixed section bytes (explicit upper rejection at
  2,097,152), then block-entity entries. Negative/invalid length handling
  resides in reached buffer delegates and is not proved here.
- The initial light receiving constructor reads four bitsets in
  sky-present, block-present, sky-empty, block-empty order followed by
  sky and block update collections.

The existing candidate body test now independently asserts the exact
8-byte negative-X/positive-Z big-endian prefix and that chunk fields,
the single explicit empty block-entity count, and light fields are
contiguous. `tools/tests/test_r2c_outer_envelope_second_pass.py` checks
full pinned method fingerprints and makes any silent claim of
independent VAR/SEM, full delegate closure or production admission fail.

**Specific remaining source steps:** independently review the concrete
`RegistryFriendlyByteBuf/FriendlyByteBuf` signed `writeInt/readInt`
delegates and receiving packet constructor; bind exact fingerprints
of the previously admitted inner chunk/light writers to the parent,
then close packet registration ID, section-size decode failures,
zero block-entity list law, `collectChunksToSend` and client ACK/receive.
Client known-pack/biome numerical IDs and the dense heightmap input
facts are distinct source gates. Until their independent Atlas VAR/SEM
decisions succeed, this record is a *source-reading candidate*,
not a source-admitted production packet.

## Mandatory closure after inventory

1. **Inspect the exact official method bodies and their delegates**, not
   merely the class inventory or captured packets. Select exact
   overloads/signatures, close implementation hazards and save the
   appropriate source-free VAR/SEM evidence records under Helve's
   independent gate.
2. **Compare the candidate serialization against the admitted facts**:
   packet type registration, chunk coordinates, heightmap and section
   framing, the zero block-entity list encoding, and light field order.
   Promote only after those *specific* wire claims are proved.
3. **Review loaded registry allocation and client numeric-ID assignment
   separately** under #285; matching default 66 runtime names is
   independently useful confirmation, not semantic source authority.
4. **Check publication**: selected first-spawn clientbound packet
   ordering, chunk send window, batch delimiters/acknowledgement and
   pacing on the R2B -> R2C cursor. No captured replay allowed.
5. **Repeat the stock-client visible-world qualification against the
   ordinary, non-test server after source admission**, using bounded
   scratch, generation/revision-bound source receipts, exact packet
   IDs and unmodified target 26.2 client. The 25-source / central-3x3
   test-only visual checkpoint was achieved on 18 October; it is not
   equivalent to a production publication pass.

There is **no production path** from the discovery inventory to a
wire encoder. \`source_inspected\`, \`packet_wire_law_proven\`,
\`block_entity_semantics_proven\`, \`chunk_publication_order_proven\`
and \`production_admitted\` are always false. The operator must not
edit them to claim proof.

No official Java source is committed, and existing resident-world
ownership, COLD projection, and HOT-path performance constraints are
unchanged.
