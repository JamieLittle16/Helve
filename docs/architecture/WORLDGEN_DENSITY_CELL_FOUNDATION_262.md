# Minecraft Java 26.2 worldgen — non-admitted density-cell foundation

**Date:** 19 October 2026 · **State:** implemented source-free COLD mechanism, NOT a target-faithful `DensityFunctions` / `NoiseRouter` implementation.

## Architecture and admission boundary

The existing exact-bit `ImprovedNoise262`, `PerlinNoise262` and `NormalNoise262` evaluators (PRs #417–#427) are **reused**, not rebuilt. The next stage is `crates/world/helve-world-gen/src/density_kernel_262.rs`, an immutable and statically sized *explicit* expression graph:

```text
world/dimension seed-compiled samplers (retained, immutable, borrowed)
         |
explicit density nodes, each assigned exactly one stable topological slot
         |
per-worker fixed array scratch, rewritten once for each XYZ coordinate
         |
bit-preserving 16x16 horizontal plane or 16x16x16 Y/Z/X density cell
         |
[not yet connected] aquifer / biome / surface rules / semantic chunk build
```

The owner of the samplers is external. The graph does not own a random source, registry, dimension, chunk map, network connection, derived light, or a second packet representation. It never publishes; all R2C source/VAR/SEM, R2D readiness, density-router and production chunk-publication gates remain **closed**. No new worldgen production setting is enabled.

## Qualified scope of this mechanism

- **Operations:** caller-selected constants, X/Y/Z coordinates, Perlin or Normal noise leaf, ordered `Add` and `Multiply`. They are generic eager arithmetic operations, **not an asserted vanilla 26.2 class mapping**.
- **Preflight:** compile-time-sized `[DensityNode262; N]` constructor rejects empty output, forward/cyclic/invalid references and unreachable work without allocating. Root is the last node. A prior node may be reused by two or more later dependents, making a DAG rather than a recursively duplicated expression tree.
- **Runtime:** the graph contains borrowed immutable sampler refs, not copied permutation tables. Each coordinate is evaluated with `&mut [f64; N]` scratch belonging to that worker or a small stack wrapper. Node results are computed in declared order, no arithmetic reassociation, `mul_add`, or fast math. The compiler can statically dispatch each known operation type; this is a small tagged switch, not an allocation-heavy hierarchy.
- **Coherence:** single-node Normal or Perlin delegates directly into the existing source-free JVM-bit-qualified `sample_plane_16x16` implementation, including the exact coordinate-addition arithmetic; constants and Y-only values fill planes. Complex graphs use the same point-wise order as `sample_with_scratch`. All paths write Z-major planes and Y/Z/X 4096-value cells to caller-owned buffers; no intermediate volume is retained.
- **Missing source laws:** exact default noise router composition, sampling context coordinates, noise settings/parameters/registries, `DensityFunctions` class identities, lazy branching, caching policies, interpolation, splines, `RandomState` world seed mapping, aquifers, terrain blocks, biome identities, surfaces, features, and lighting are **not** implemented or inferred.

The tests consume the already-pinned official reference fixture `tests/data/perlin_normal_26_2_rawbits.tsv`. A program with a single Perlin/Normal leaf must return all **320/320** independently observed official noise *output* bits, across the five direct random-factory seeds. These are strictly noise-leaf assertions, **not official density outputs**. Separate tests check full 4096-cell Y/Z/X order, scalar/plane parity at negative and wrapping boundaries, ordered operations, signed zero, invalid/cyclic/unused-node rejection and thread-isolated scratch.

## Next vanilla source-evidence milestones

1. Review the pinned 26.2 official `DensityFunctions` / `NoiseRouter` families and delegates **on the source-owning machine**. Select the smallest genuine node set and exact coordinate/evaluation semantics; classify every API overload, shortcut and reached method as reviewed or open. A method hash or interface name alone is not enough.
2. Record **source-free official JVM raw output bits** for those exact nodes and contexts, with method-body fingerprints, seeds/settings, signed/negative-Y/extreme coordinates, and effective random-source/parameter bindings. Do not commit proprietary source or class bytes.
3. Implement separately named *source-qualified* typed nodes and parameter resolutions only after this evidence. Refuse to use the generic straight-line operations as a guessed substitute for vanilla min/max, interpolation or caches. Keep arithmetic-order, signed-zero and missing-input tests.
4. Extend from sampled density cells to complete native semantic chunks through existing `GeneratedSectionBuilder` and `SemanticDimensionInstance::admit_chunk`, with exact palette/biome/aquifer/surface/light provenance; do **not** insert a second world owner or route generation through NBT.
5. Benchmark a target-faithful scalar reference against batched COLD graph, section build and full resident installation on controlled hardware. Record work counts, whole-cost p50/p95/p99, allocations, bytes and visible-latency changes. The previous benchmarks measure isolated or non-vanilla candidates and are **not** proof the current kernel is optimal.

**Guardrail:** this is implementation progress toward a real density engine, not a declaration of source/VAR/SEM admission, vanilla terrain parity, or production readiness.
