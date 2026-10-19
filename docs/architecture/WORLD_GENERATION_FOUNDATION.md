# Helve world generation — deterministic COLD foundation

**Scope:** a deliberately **non-vanilla** testable generation kernel, independent of R2C chunk-publication permission.  
**Version target for later parity:** Minecraft Java 26.2, protocol 776, DataVersion 4903.  
**Implementation:** `crates/world/helve-world-gen`.  
**Status:** first reference-rule implementation and independent correctness tests; not a target-faithful noise engine, not an R2D requirement, and not exposed to live players.

## Architectural boundary

The generator is a **producer**, never a new owner. It creates ordinary `LiveChunkCore` and `ChunkBiomeColumn` objects and moves them into `LiveChunkSemanticState`. Installation goes through **the existing** `SemanticDimensionInstance::admit_chunk` closure, receiving the resident directory's exact `ChunkGeneration` and immutable `DimensionRuntimeProfile`:

```text
seed + world coordinates + pre-resolved dimension profile
    -> statically dispatched sampling kernel (COLD)
    -> 256-column height scratch reused across the whole chunk
    -> uniform-section fast path or reusable 4096-block scratch
    -> GeneratedSectionBuilder (selected storage mechanism)
    -> LiveChunkCore + ChunkBiomeColumn
    -> LiveChunkSemanticState (revision 0, no synthetic saved light)
    -> existing SemanticDimensionInstance::admit_chunk transaction
    -> existing resident handle, generation/revision, HOT access
```

There is **no second resident map**, owned per-chunk target packet, NBT intermediary, parallel revision, duplicate dynamic registry, new networking driver, separate publication queue or runtime scheduler. One chunk has one semantic authority. Generation is independent of import; both produce the same installed semantic chunk type.

## First isolated example: `SteppedSurface`

`SteppedSurface::new(seed, base_y, amplitude)` samples a fixed-width, coordinate-derived, 8×8 stepped surface without global mutable RNG state or floating-point arithmetic. The rule samples exactly 256 horizontal columns **once per chunk**, tracks the minimum and maximum sampled height, and fills entirely air/solid sections with a single array fill. Only intersecting sections need 4096 Y/Z/X comparisons. It reuses one 4096-element block scratch and a 256-element height scratch, passing uniform block and biome sections directly to a statically selected builder to construct the *final* section storage. The baseline biome is one explicit caller-supplied semantic ID; the palette also supplies air and solid IDs. The algorithm never guesses real 26.2 block/biome ordinals.

An exact same-seed/sample-coordinate pair produces the same result regardless of:
- call sequence, chunk creation order, client count or thread placement;
- negative coordinates and crossed chunk boundaries (Euclidean 8-block cells);
- which pre-resolved dimension instance receives the chunk.

`SteppedSurface` is **not vanilla**. It does not implement vanilla 26.2 Perlin/Normal noise, density routing, aquifers, climate/biome selection, surface rules, structures, caves, decorations, fluid state or lighting. The simple height hash is a test of the integration architecture, not a performance or fidelity result. It is **not connected** to the product server or `R2cSourceAdmission`.

### Ownership and failure invariants

- The root resident directory gives the generation; neither the sampler nor the section builder invents a chunk incarnation.
- All sections are built locally. A rejected block or biome section returns an error **without any residency or generation consumption**. The final runtime admission also rejects duplicate, misplaced, stale or wrong-lattice chunks.
- A successful generated chunk is pristine (`ChunkRevision(0)`). It has **no initial-light data**. In particular, "generate solid blocks" never means "invent source-admitted light arrays."
- The section adapter receives a typed uniform-or-dense sample; uniform sections never need a 4096-cell scratch fill or scan. The current tests use `DirectBlockSection` and `DirectBiomeSection` **solely as transparent correctness oracles**. No production section representation is selected by this PR.
- HOT chunk read/mutation remains completely unchanged. Generation has no HOT per-block, actor, scheduler or network cost.

## Reproducible checks

From repository root:

```bash
cargo test --locked -p helve-world-gen
cargo clippy --locked -p helve-world-gen --all-targets --all-features -- -D warnings
cargo fmt --package helve-world-gen -- --check
```

Tests assert: signed chunk-boundary sampling; all 96 block levels and 64 quart biomes across actual sections; stable results for reversed chunk installation orders; distinct-seed sampling; duplicate admission is never built; a failing section builder installs nothing and cannot consume the generation; no generated chunk can claim initial-light provenance.

CI must be green on the exact PR head before merging. These tests are **not** a substitute for the R2C production chunk-source/VAR/SEM gate.

## Strict-parity and whole-cost measurement gate

The first benchmark and official-reference differential infrastructure are now
specified in [Worldgen Bit Parity and Benchmark](WORLDGEN_BIT_PARITY_BENCHMARK.md).
The source-free `SteppedSurface` whole-cost harness measures sampling,
final section construction and genuine resident admission separately, with
host and compiler provenance; it is **not a vanilla noise benchmark**.
The raw IEEE-754 differential checks source-locked `u64` output patterns
rather than accepting epsilon errors. Without an independently verified
official noise sampler and its target 26.2 source fingerprint, **no strict
vanilla noise-parity claim is made** and no speedup is certified.

**First official sampling entry point:** `tools/worldgen_26_2_improved_noise_capture.py`
is a source-pinned, **not yet executed against the official runtime here**,
160-vector raw-IEEE JVM probe for the exact `ImprovedNoise` three-coordinate
overload. The local Atlas/source/runtime lock must pass before it emits
source-free candidate evidence; no official source method, constructor or
RNG delegate is SEM-admitted merely by its output. See
[Worldgen Bit Parity and Benchmark](WORLDGEN_BIT_PARITY_BENCHMARK.md)
for the executable command and exact independent review obligations.

## Exact vanilla 26.2 generator roadmap — future distinct gates

1. **Pinned generation source map and proof contracts.** Identify official 26.2 seed mixing, noise parameter registries, climate/RNG seeding, noise router/density functions, structure and decoration ordering using the existing Atlas/source-lock discipline. Record exact target selections and source-free VAR/SEM with complete error/delegate coverage. Do not infer from an older Java Edition version.
2. **Independent target-faithful sampling oracle.** Extract source-free test vectors for signed coordinates, seed extremes, negative Y, chunk boundaries and major dimensions. Differentially compare *every stage* (RNG/noise, density, aquifers, biomes, surface material) before claiming full terrain fidelity. Keep a slow transparent reference for correctness.
3. **Final-section production builder and candidate optimisations.** Populate compact selected Helve section storage directly rather than creating a Mojang object graph or applying thousands of state mutations. Benchmark total generation + derived state + install cost (allocation, copies, bandwidth, CPU, p50/p95/p99) on representative hardware. SIMD and cache optimisations require parity evidence. Keep M0.3D section-policy decisions independent.
4. **Light, dependencies and lifecycle.** Only derive lighting/heightmap and block-entity/world-feature semantics from admitted sources. Stage neighbor/structure dependencies as revision-bound work; stale generation results must not commit. Avoid global RNG and non-deterministic thread-order effects.
5. **Product integration behind separate gates.** Only once R2C source admission, R2D liveness, stored/generated source selection, and all target-faithful generation contracts qualify, hook on-demand generation into the single resident-world source and chunk-interest lifecycle. Retain the pregenerated import path and forbid raw unadmitted publication.

**R2C/R2D separation remains mandatory.** R2C's test-only 25-column stock-client visual demonstration already works. Its independently source-admitted normal-build publisher, and R2D's persistent full-session liveness/reconnect qualification, are still separate obligations. World generation is useful independent groundwork and must not silently become a prerequisite for either milestone.
