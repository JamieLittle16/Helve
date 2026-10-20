# Minecraft Java 26.2 — coherent stock registered-noise density cells

**Status:** independent COLD-only Rust numerical evaluation for the three previously pinned
stock registered noise keys, not a production NoiseRouter, biome, chunk or client authority.
The source-law VAR/SEM admission and truly held-out official JVM seeds/points remain open.

## Existing baseline

PR #449 independently observed and pinned all 15 actual stock key/seed full numeric
states, then demonstrated complete 1,440/1,440 bitwise *observed-state replay*.
PR #450 implemented a truly seed-derived Rust Xoroshiro positional constructor for
the three keys (temperature, continentalness, erosion), reproducing all 15 complete
original JVM states and the same 1,440 original JVM outputs in both debug and release.
This PR does not change either already-qualified scalar sampler or constructor.

## New reusable hot path

- `StockWorldSeededNoiseSet262::new_candidate(seed_bits)` derives **one** root
  Xoroshiro positional factory and creates each of the three named, independent
  NormalNoise samplers from it. The builder owns no chunk, registry, additional
  world cache or communication state. Its output is immutable and safe to share
  across workers, with key dispatch and scale binding outside sample loops.
- `RegisteredPerlinObserved262::sample_axis_grid_16x16` uses the existing
  `ImprovedNoise262::sample_axis_grid_16x16` rather than recomputing all 256
  X/Y lattice-permutation columns for each scalar. Every live octave retains
  the exact scalar coordinate wrap, per-octave weight/volume factor and
  accumulation order. Sparse or nine-slot profiles are not truncated.
- `RegisteredNormalObserved262::sample_axis_grid_16x16` separately scales
  the second Perlin branch's inputs before octave-frequency multiplication,
  preserving nonassociative floating-point behavior and exact signed output
  bits. Fixed-size stack scratch contains both contributions.
- `RegisteredNoiseDensityObserved262::sample_plane_16x16` and
  `sample_cell_16x16x16` take integer block coordinates with the same three
  previously observed density scaling profiles. All X/Z axes are prepared
  only once per cell; 16 Y planes write directly into **caller-owned** output
  in Y/Z/X order. There are **zero heap allocations during sampling**.
- Arithmetic keeps the existing compiler-sensitive operation order:
  do not introduce fast-math, `mul_add`, reassociation, cached floating
  coordinate increments, or heuristic noise shortcuts. The output is still
  a numeric density leaf, *not* a vanilla final terrain-height decision.

## Qualification and failure modes

- The shared-root three-key constructor must be bitwise identical to **each**
  of the 15 stock full-state JVM receipts, not just equal for one key.
- Coherent planes use actual original JVM oracle bits at both ends of the
  signed 2^25 wrap tests; the other 255 positions per plane are independently
  compared against the exact-bit Rust **seed-derived scalar** evaluator.
- Complete 4096-sample Y/Z/X cells at signed seeds/negative Y and two scale
  profiles compare **every** raw `f64::to_bits()` against independently
  evaluated scalar results. Worker concurrency must produce identical bytes.
- All 16 axis integer coordinates are validated with checked `i32`
  arithmetic **before the first output write**. X, Y or Z overflow must
  return the established `DirectNoiseCellError262::BlockCoordinateOverflow`
  without damaging the caller's existing NaN-sentinel buffer.

These tests establish **batched/scalar equivalence** under the previously
qualified numeric kernel; they do not constitute new held-out JVM data for
arbitrary coordinates or seeds. Do not infer production source admission
or generator publishing privileges.

## Next source-facing work

Run an independent *held-out* official 26.2 JVM seed/position profile
(not a recapture of the existing 1,440 rows). Use the pinned stock provider,
source archive, exact key lookup and original executable. Require the held-out
output to be frozen as source-free raw IEEE-754 bits; compare against Rust
seed-derived values in debug and release. Continue the independent
`RandomState` / `Xoroshiro` / positional hashes / Normal-Perlin-Improved
constructor delegate-law review from the existing method inventory.
Only afterwards extend into density-router semantics from additional
source-grounded laws.

**Always closed here:** `world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false`,
`production_worldgen_enabled=false`.
