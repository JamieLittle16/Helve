# R2C — Coherent block/biome section candidate

**Status:** deliberately dormant COLD integration; no Play packet authority granted.

The 26.2 target reference encoder (#290) and read-only coherent chunk section borrow (#291) are now joined at the **server composition** boundary. A caller with an already-verified `InitialChunkReference` supplies one section Y and the cardinality of a separately validated biome registry. The candidate:

1. Takes the existing immutable `BlockSection` borrow by local section Y (no world-coordinate resolution per cell).
2. Reuses the source section's existing exact non-air/fluid counters, rejecting impossible summaries.
3. Traverses 4,096 local YZX block cells once, statically dispatches `BlockSection::get`, converts dense generated `BlockStateId` to official vanilla-identity numeric IDs, and builds the target-owned reference block palette.
4. Derives the matching 64-cell biome palette from the **same** coherent image and revision; unknown ordinals, invalid cardinalities and missing sections fail before any byte is appended.
5. Delegates the four counter bytes and complete block/biome order to the target-owned **candidate** section-byte assembler. Output is appended into one caller-owned `Vec<u8>` with a pre-reserve, no intermediate encoded block or biome byte buffers.

This does not add a cache, worker, clock, chunk owner, packet queue or HOT-path check. It **does** build COLD per-section palette metadata; reference-mechanism performance optimization remains a future qualification exercise.

**No live publication**: The source-verified 26.2 biome numeric ID ordering (issue #285), exact generated heightmap state predicates, enclosing chunk/packet wire source admission, block-entity and world-entry gates remain outstanding. Nothing from this candidate is sent to the stock client. Test biome IDs and test heightmap facts are synthetic and must not be represented as official authority.

Tests cover direct coherent-source integration (two adjacent sections of unequal palette shape), source revision persistence, correct section order and count prefix, output reuse without reallocating pre-reserved scratch, and transactional rejection on invalid section and biome identity. The target palette's own independent decoding oracle remains in #290.

## Atomic complete-section-column candidate

The optional COLD server composition routine `append_coherent_section_column_candidate`
walks the resident vertical lattice in exact bottom-to-top section-Y order, using the
same immutable `InitialChunkReference`. Each section is projected directly into the
existing destination. It remembers only the caller's previous byte length, and
truncates the candidate suffix if any later section fails validation. This avoids
a second whole-column `Vec`, palette replay, second world owner, or extra checks
on HOT state mutation.

The output is **not** a full 26.2 chunk packet and carries no registry-ID or
world-entry authority. A suffix rollback is an output-buffer operation only,
not a transaction on the world owner or socket. Tests establish the byte order
against independent per-section concatenation, preserved allocation on a
pre-reserved destination, and all-or-nothing rollback when an upper-section
biome ordinal is out of the selected registry range.

Next: source-qualify exact biome ordinal ordering and the remaining enclosing packet law, add target-owned packet serialization, and only then connect it to the existing `R2bPlaySession` publication cursor and stock-client differential runner.

## Heightmaps + bounded section-byte prefix (R2C next candidate)

The target-owned COLD `r2c_chunk_data` adapter now validates and appends
three source-selected heightmap type IDs 1, 4 and 5, each followed by its
canonical packed long array, with a three-entry map prefix. It validates
the exact dimension-relative height bound, required non-spanning word
counts and unused storage padding before appending anything.

The complete section sequence is built directly into the same caller-owned
`Vec<u8>`, and then receives its canonical length `VarInt` using one
in-place byte movement. There is no second serialized chunk buffer. The
source section validation and a caller-specified uncompressed section byte
limit remain fail-closed. If any section fails after heightmaps were written,
the server candidate truncates **all** fields back to the caller's old length.

`append_coherent_chunk_data_fields_candidate` consumes the same immutable
`InitialChunkReference` (generation/revision, blocks, biomes, verified
light and already packed heightmaps), never retains a packet-shaped
resident image and introduces no HOT-path branches.

**This is not a complete chunk packet.** The prefix omits the block-entity
field, chunk position/packet identity, light payload and the source-backed
publication order. The existing biome runtime candidate is not yet an
admitted numeric-ID table; issue #285 remains open. The implementation
must not be connected to actual Play output until all those independent
gates are satisfied.

The target adapter's unit tests verify canonical big-endian packed words,
VarInt boundaries, invalid padding/count and source failures. The server
composition tests verify byte equality with separately assembled fields,
retention of allocation with pre-reserved scratch, and atomic rollback even
when the **second** section fails.

## Target-owned initial light payload candidate

The selected 26.2 light source group already admits four masks in order:
sky data, block data, empty sky, empty block. The new COLD target
`r2c_light` module writes their **minimal BitSet long arrays** (including
the 64-bit boundary at light section index 64), and VarInt-counted sky
then block updates. Each update has exact VarInt(2048) length and 2048
raw packed bytes, copied straight from the borrowed source
`LightDataLayer` into the existing caller output allocation.

The server candidate `append_coherent_light_payload_candidate`
retains the same `InitialChunkReference` as the section/heightmap
candidate, classifies masks only from its already verified initial light,
and visits source updates in ascending light-section order. It confirms
each mask's set-bit count agrees with its source update iterator.
Contradictory/out-of-span masks are rejected before output; a later
source inconsistency truncates the complete candidate suffix.
Missing light remains missing and packed zero data remains **present
data**, not an empty layer.

No intermediate 2048-byte layer buffer, new light engine, second
publication queue or resident packet image is introduced. There is
still **no enclosing Play chunk-with-light packet**, as the packet
identity, coordinates, block entities, publication ordering and
source-verified biome numeric IDs must be admitted separately.
