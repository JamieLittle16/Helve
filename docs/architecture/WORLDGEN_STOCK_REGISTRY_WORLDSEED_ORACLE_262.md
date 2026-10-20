# Minecraft 26.2 — stock-registry world-seeded density oracle

**20 October 2026 · candidate numeric evidence path only · no VAR/SEM or production admission**

## Why this is a genuinely different oracle

The source-free exact **RandomState shape** observation (uploaded after #439)
has SHA-256 `1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7`
and confirms the pinned Minecraft 26.2 source/server SHA-256. It records
the actual public methods:
- `RandomState.create(HolderGetter.Provider, ResourceKey<NoiseGeneratorSettings>, long)`.
- `RandomState.getOrCreateNoise(ResourceKey<NoiseParameters>)`.
- `Noises.instantiate(HolderGetter<NoiseParameters>, PositionalRandomFactory, ResourceKey)`.
- `DensityFunction$NoiseHolder(Holder<NoiseParameters>, NormalNoise)` and
  `DensityFunctions$Noise(NoiseHolder, double, double)`.
- The three real `Noises` resource-key fields `TEMPERATURE`, `CONTINENTALNESS`, `EROSION`.
- The Overworld settings key and `Registries.NOISE` field.

We already have **480/480** raw-bit matches for the direct
`RandomSource.create(seed)` path. That does *not* mean the world seed is
converted using the same RNG factory. The new probe instead asks the
**official JVM** to run the actual world-seed-aware `RandomState` constructor
against a **real stock built-in `HolderGetter.Provider`**, and only then
samples the official `DensityFunctions$Noise.compute`.

## Construction and provenance

The original bridge at
`tools/worldgen_java/HelveWorldSeededDensity262.java` uses reflection
against the **pinned official 26.2 server runtime**; it contains no copied
Mojang implementation or decompiled bodies. The exact flow is:

1. `SharedConstants.tryDetectVersion()` and `Bootstrap.bootStrap()`.
2. Official `VanillaRegistries.createLookup()`, requiring a real
   `HolderLookup.Provider`; then `asGetterLookup()`.
3. Resolve the **real** `Registries.NOISE` via the official
   `HolderGetter.Provider` accessor and obtain a keyed `Holder.Reference`
   using `getOrThrow`. No `Holder.direct` substitute or fabricated
   `NoiseParameters` is accepted.
4. Call the **real** `RandomState.create(provider, NoiseGeneratorSettings.OVERWORLD,
   worldSeed)` and `getOrCreateNoise` for one of the three registered noise
   keys. Reuse each created state per world seed.
5. Create `NoiseHolder(holder, noise)` and `DensityFunctions$Noise`, and
   invoke the actual `compute(SinglePointContext)` method; retain raw
   IEEE-754 bits, including signed zeros.

Three XZ/Y scale profiles × five exact signed seed bit patterns × three real
noise keys × 32 integer XYZ contexts = **1,440 output records**. The collector
validates the prior source-free frontier SHA, exact five source-method
fingerprints including `Noises.instantiate`, plus the **new local
`VanillaRegistries.createLookup` Atlas body hash**, source archive SHA,
runtime jar SHA, transport ordering, vector values and strict admission flags.

The bridge fails closed if the official jar cannot load the built-in
registries, if `VanillaRegistries.createLookup` has changed shape, if the
provider is not a real stock registry holder, or if any key/constructor path
fails. Do **not** change to a fake `HolderGetter` to make the output pass.

A fake **independent test JVM** exists only in CI for reflection/signature,
manifest, stdout redirection and request framing validation. Hosted CI does
**not** contain private Minecraft runtime/source and does **not** prove the
numeric 1,440 official results.

## Local official run

The previous source-free frontier JSON must remain available at its
original `/tmp` path, or be supplied with `--frontier`:

```bash
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_world_seed_density_capture.py \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-world-seed-stock-registry-density-01.json
```

Upload **only** the generated source-free JSON, or the precise failure
diagnostic. Do not upload original Minecraft source, Atlas databases,
server jars, extracted Java class files or decompiled source bodies.

## Proof boundary and next implementation

A successful manifest sets `world_seed_random_state_observed:true` and
`stock_registry_used:true` (a **specific bounded JVM observation**), but
keeps `world_seed_random_state_bound:false`,
`independent_var_sem_admitted:false` and
`production_worldgen_enabled:false`. Official output parity does not
independently review all relevant source laws or prove the entire router.

After success, freeze all 1,440 genuine output bits, compare with Rust
and local source-review the exact `RandomState` seed factory and
`Noises.instantiate` parameter/registry binding. Build an immutable
registry-keyed per-world sampler owner with construction outside the
sampling loop; reuse existing exact-bit noise kernels and caller-owned
buffers. Extend later to `NoiseRouter.mapAll` caching and broad vanilla
surface/cave/biome/chunk parity. Keep the normal executable's worldgen
publication gate closed until separately qualified.
