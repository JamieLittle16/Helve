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

Next: source-qualify exact biome ordinal ordering and the remaining enclosing packet law, add target-owned packet serialization, and only then connect it to the existing `R2bPlaySession` publication cursor and stock-client differential runner.
