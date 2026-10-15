# R2C — Chunk-with-light wire-source closure frontier

**Current status: discovery only. No packet, block-entity, pacing, or biome-ID
production admission.** This is independent of already-admitted R2C world-state
palette, heightmap, and light semantics.

Helve now has a dormant COLD candidate for the complete explicitly-empty
block-entity chunk-with-light body. The remaining correctness requirement is
not another storage system or packet encoder: it is an exact pinned 26.2 source
proof that the candidate's outer identity, fields and publication order agree
with vanilla.

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
5. **Qualify stock-client joining and a visible pregenerated world**,
   using bounded scratch, generation/revision-bound source receipt,
   exact packet IDs and unmodified target 26.2 client.

There is **no production path** from the discovery inventory to a
wire encoder. \`source_inspected\`, \`packet_wire_law_proven\`,
\`block_entity_semantics_proven\`, \`chunk_publication_order_proven\`
and \`production_admitted\` are always false. The operator must not
edit them to claim proof.

No official Java source is committed, and existing resident-world
ownership, COLD projection, and HOT-path performance constraints are
unchanged.
