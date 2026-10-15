# R2C — Target-owned block-state container reference

**Status:** COLD reference candidate only, not admitted for live Play packet publication. Target: Java 26.2 (protocol 776), parent R2C plan.

This narrowly scoped target module is deliberately isolated in `helve-target-26-2`, not `helve-world-chunk`. The existing generated state-id universe establishes compact vanilla-identity `u16` values with exact cardinality 32,366. The reference receives a **caller-supplied validated cardinality** and a callback returning one already-resolved global identity for each of the 4,096 section cells in YZX order. No section copy is mandated and the callback is invoked exactly once per cell.

Reference representation: single value (0-bit storage), first-use local palette (minimum 4 bits, maximum 8 bits), or global registry IDs when 257 distinct states have appeared. Packed words use the non-spanning `floor(64 / width)` convention. The reference has immutable container-level bytes, a direct append-to-existing-buffer API and an exact-size calculation, and no connection or world authority. It introduces no HOT-path tracking, locks or network-shaped live section representation.

The M0 section semantics and reviewed PalettedContainer/section source establish the selected strategy, linearization and summary boundaries. **R2C block-section source admission, exact enclosing packet/section placement and the 26.2 client wire proof remain separate gates.** In particular, the byte encoder here is a source-informed candidate, **not** an assertion of complete 26.2 packet-law admission. Do not use this module to send world data until the required source/SEM check, independent vanilla comparison and section-prefix + biome integration have passed.

The unit tests deliberately decode the emitted bytes through a separate straightforward oracle and exercise uniform, 4–8-bit local width boundaries, global widths 15/16, multi-byte VarInts, bad cardinalities, invalid global IDs, and allocation-free reuse of pre-reserved output bytes. Tests do not claim black-box client parity or production efficiency.

Next integration: expose one **immutable** section borrow through the resident core, then statically bind a target adapter using the generated `to_vanilla_state_id` mapping; verify exact section summary counts and combine block/biome containers in admitted order. No registry/hash lookups or per-cell world-position resolution should be introduced in that adapter.
