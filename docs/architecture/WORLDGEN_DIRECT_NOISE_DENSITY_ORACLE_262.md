# Official Minecraft Java 26.2 — first noise-backed density oracle

**20 October 2026. Experimental direct-seeded source-free JVM probe. NOT RandomState/world seed or production admission.**

## Why the new boundary

The previous official capture pinned the real 26.2 composition delegates (`Ap2`, `MulOrAdd`, `PureTransformer`) and identified a precise candidate for the next stage:

- `DensityFunctions$Noise.compute(FunctionContext)`: body `bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe`.
- `DensityFunctions.noise(Holder<NoiseParameters>, double, double)`: body `410456eefd7a1364a89705b96c7b31fd0f044c4b017eb521264370d2bdd424f9`.
- `NormalNoise.create(RandomSource,int,double[])`: body `ce4d2746996bf4244a3b79bf86ccdf6c51c36f612047f7843427461e998f7d8e`.
- `NormalNoise.getValue(double,double,double)`: body `578fbb9c36fa89507fbf842effbdadcebb1aeb7369641e972f9e737ef30bd329`.

A direct reference to `NormalNoise262` in our generic eager DAG is not sufficient: this node has Minecraft-specific integer context, scaling, and `NoiseHolder` binding. The actual `RandomState` construction, noise-key registry lookup and router visitation are still source-review gaps.

## Deliberately limited experiment

`tools/worldgen_26_2_noise_density_direct_capture.py` checks exact source lock/Atlas method signatures and hashes plus the official jar identity before invoking a new **original reflection-only** JVM bridge. The bridge bootstraps the real 26.2 server, creates five retained `NormalNoise` instances using **`RandomSource.create(seed)`** and the prior proven `(-3, [1.0, 0.0, 0.5, 1.0])` construction profile, then **directly constructs the official** `NoiseHolder` and `DensityFunctions$Noise` records. It calls their true `compute(SinglePointContext)` at 32 exact integer block contexts under three xz/y scale profiles.

The output request is **480 raw IEEE-754 observations**: 3 profiles × 5 direct RNG seeds × 32 coordinates. The collector verifies every seed, coordinate, scale, profile, row order, method fingerprint, source/runtime lock and exact 16-digit raw result. It writes only a JSON outside the repository with `source_text_included=false`, `independent_var_sem_admitted=false`, `production_worldgen_enabled=false` and **`world_seed_random_state_bound=false`**. A diagnostic JVM transport uses a dedicated tagged output stream on the process stdout descriptor and ignores unrelated startup logging without accepting untagged data.

This is **not** the production `DensityFunctions.noise(...)` factory followed by `RandomState` visitation; it is a controlled, direct construction experiment for the real compute class. Even if the capture succeeds, do not claim parity for `NoiseRouter`, final density, seed-dispatched `Noises.instantiate`, different NoiseParameters or generic noise nodes. Constructor compatibility is runtime-checked against the pinned jar and may fail closed; CI cannot exercise the private official runtime, only an independently authored toy JVM.

The first source-owning run should be:

```bash
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_noise_density_direct_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-density-noise-direct-official-01.json
```

Upload only the generated source-free JSON (or the exact fail-closed diagnostic). **Do not upload source archive, private Atlas database, jar, decompiled method bodies or JVM class files.**

## Next work when official raw-bit capture succeeds

Verify all 480 values and register immutable evidence. Compare candidate Rust computation against the genuine official function, including scaling and signed-zero/arithmetic order; only then implement a typed noise-backed leaf borrowing an immutable retained `NormalNoise262` without new per-sample allocations. Afterwards investigate `RandomState.create`, `RandomState.getOrCreateNoise`, `Noises.instantiate` and `NoiseHolder` visitor substitution using locally source-reviewed laws and another official oracle. Until those bindings pass, the Rust node must remain a **direct-seeded candidate**, not a production router.

The 26.2 source-locked parser and toy Java tests guard the mechanism. Source/VAR/SEM production qualification and `helve-target-26-2` worldgen chunk publication remain closed.


## Official source-owning result — 20 October 2026

The original 26.2 JVM oracle **succeeded**, producing a 97,991-byte source-free JSON with SHA-256
`e2107c7b874aacda195cab980c55cba2e0110f0974b4efebdf2a34fd480c3bd5`.

Independent manifest validation confirms **480/480** requested raw IEEE records in exact order: three scale profiles (1/1, 0.25/1, 0.25/0.5), five direct seeds (`0`, `1`, `u64::MAX`, `i64::MIN`, `0x9e3779b97f4a7c15`), and 32 pinned XYZ contexts. The observed `Noise.compute` body SHA-256 is `bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe`. The previously pinned source archive, server runtime, NormalNoise constructor and `getValue` hashes match unchanged. Seed 0 and the seed with only bit 63 set happen to produce identical 32-value sequences under each profile, consistent with direct legacy RNG seed truncation.

All 480 genuine output raw bits are frozen, without the private source or jar, in
`crates/world/helve-world-gen/tests/data/density_noise_direct_26_2_rawbits.txt`. Each of 15 data lines contains 32 concatenated exact 64-bit hex values; profile and seed order is locked in a Rust regression test. Its source-free header pins the original JSON SHA-256. The Rust type `DirectNoiseDensity262` borrows a retained `NormalNoise262` and selects only those three proven scale profiles. It evaluates integer context to f64, applies horizontal/vertical scale separately and delegates to the existing zero-allocation normal noise kernel. Optimized plane and cell paths precompute per-axis scaled coordinates and use caller-owned output buffers. Overflow in any of the 16-block axes is rejected before output writes.

The Rust golden test will establish the parity of this *direct-seeded* node with all 480 official outputs **only once CI reports success**. No result here proves the full world seed mapping, registry binding, real NoiseRouter or final terrain parity. All source/VAR/SEM, live publication and production gates remain closed.

### Actual next frontier

Source-review the pinned `RandomState.create(NoiseGeneratorSettings, HolderGetter, long)`,
`RandomState.getOrCreateNoise(ResourceKey)`, `Noises.instantiate`, and the relevant
`DensityFunction.NoiseHolder` visitor substitution path. Bind the *correct
registry key and noise parameters* to a genuine world seed, capture another
official raw-bit corpus, and only then enable a qualified `NoiseRouter` path.
