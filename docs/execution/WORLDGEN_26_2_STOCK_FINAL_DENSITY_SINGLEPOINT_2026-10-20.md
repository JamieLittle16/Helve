# Helve — first genuine stock 26.2 bound final-density numeric oracle

**20 October 2026.** Minecraft Java 26.2 · protocol 776 · DataVersion
4903. Source-free real original JVM observations, **not** compiled vanilla
graph equivalence, full chunk interpolation or production worldgen authority.

## New original stock evidence: all HolderHolder binding targets known

The user ran the real source-owning four-seed `HolderHolder.function ->
Holder.value()` collector from PR #460. The actual
`helve-26_2-stock-router-bound-holders-4.json` is **15,260 bytes**,
SHA-256:
`1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64`.

For each of the four previously independent world seeds, all **eight**
bound `HolderHolder` positions have exactly the same class and type
signature, and use the real `net.minecraft.core.Holder$Direct`:

| Original graph node | Connected root/path | Bound `DensityFunctions$` class |
| --- | --- | --- |
| 6 | `continents` | `Marker` |
| 7 | `erosion` | `Marker` |
| 8 | `depth` | `Ap2` |
| 9 | `ridges` | `Marker` |
| 15 | `temperature/vegetation.shiftX` | `Marker` |
| 17 | `temperature/vegetation.shiftZ` | `Marker` |
| 21 | `finalDensity.argument2` | `RangeChoice` |
| 27 | `veinToggle.RangeChoice.input` | `YClampedGradient` |

**These are runtime class observations only**. `HolderHolder.compute`
was only indexed, not independently source-reviewed; no actual density
value has been qualified by the prior holder probe. The four seed
inventories were structurally identical; their numerical values and
underlying sampled noise are not thereby seed-independent.

## Actual finalDensity scalar sampling instead of a guessed graph

The new `tools/worldgen_java/HelveStockFinalDensitySinglePoint262.java`
builds the original stock `VanillaRegistries.createLookup()` provider,
requires the genuine `HolderGetter.Provider` subtype relationship,
creates `RandomState.create(provider, OVERWORLD, worldSeed)` using
each one of the four previously held-out signed seeds, and gets the
actual bound `NoiseRouter.finalDensity` record field (index 11).
For every seed, the probe checks the already independently observed:

- actual root concrete type `DensityFunctions$Ap2`;
- `argument1` concrete type `DensityFunctions$Mapped`;
- `argument2` concrete type `DensityFunctions$HolderHolder`.

It then invokes the actual public `DensityFunction.compute` interface
on the *real bound stock final-density node* with a new original
`DensityFunction.SinglePointContext(x,y,z)` for each of 32 explicit
coordinates. The resulting 128 **raw IEEE-754 64-bit outputs** are
serialized as 16 lowercase hexadecimal digits, retaining negative
zero. Java failure phases are tagged and fail-closed; nonfinite results
are refused.

These points include the Overworld vertical limits, neighbouring
Y-values, positive and negative coordinates, 16-block chunk edges,
and larger stress coordinates. Input order, seed count, and every
point are source-free and fixed in the collector.

### What this proves and what it does not

This is the first prospective **actual bound finalDensity numerical
oracle**; its numerical values still require a successful source-owning
JVM capture. A passed synthetic CI fixture proves our transport and
schema contract, **not** Mojang's final-density numbers.

An authentic `SinglePointContext` point computation is **not** the
same as the `NoiseChunk` evaluation used during actual terrain
generation. We have NOT certified cache/interpolation markers, aquifer
path, surface/noise settings, terrain block choice, biome sampling,
actual density-grid or stock chunk parity. We do not assert that the
early standalone numerical results are equal to the chunk-context
results. All VAR/SEM and production gates remain **false**.

The collector requires exact byte SHA-256 checks on the three real,
independent, user-owned receipts:

1. Fifteen root fields × four seeds: **28,439 bytes**, SHA
   `81cc1fb15388998f9b812803ee96a30c792ef68df8120490b05f38acd3338736`.
2. Depth-four graph × four seeds: **141,287 bytes**, SHA
   `5911470e36725da99e7b82b5b8b4eef03a1d150662aa44c71b6c64340e4a46fb`.
3. Holder bindings × four seeds: **15,260 bytes**, SHA
   `1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64`.

It also reruns pinned original 26.2 source/JAR and private Atlas source
identity checks, including indexed `DensityFunctions$Ap2.compute`
method body SHA (`reviewed: false`). No original source or JAR,
registry payloads, Atlas DB or JVM objects are exposed in the output.
The JSON file is exclusively created with permissions 0600 outside the
repository. CI uses an **independently compiled toy Java registry and
record types**, including a package-private `HolderHolder`, to verify
reflection/transport. It is not substituted for an official capture.

## Source-owning command, after CI-green merge

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_final_density_singlepoint_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --roots /tmp/helve-26_2-stock-router-roots-4.json \
  --graph /tmp/helve-26_2-stock-router-graph-depth4.json \
  --holders /tmp/helve-26_2-stock-router-bound-holders-4.json \
  --output /tmp/helve-26_2-stock-final-density-singlepoint-128.json
```

The output path must **not** exist. Upload only the final source-free
JSON, or paste the full tagged `JVM PHASE` error so the exact official
runtime constraint can be addressed without guessing a Minecraft
implementation.

## Next steps after authentic values

1. Freeze numerical raw-bit observations only after source-owning
   capture; discriminate negative zero, NaNs and boundary positions.
2. Independently source-review the exact `Ap2`, `Mapped`,
   `RangeChoice`, `Marker`, holder and noise delegates actually
   encountered; do not call a source hash a proof of evaluation law.
3. Build a **separate** stock `NoiseChunk`-correct reference capture
   for interpolated grid samples with the real `NoiseChunk` scope,
   cache lifecycle and settings. Compare it to standalone points, but
   do not silently treat them as interchangeable.
4. Compile and cache only the independently qualified shape/laws in
   Rust, reusing Helve's existing server-lifetime world and SIMD/plane/
   16³ scratch as appropriate, without a second sampler or ownership
   model. Benchmark once correctness is qualified.

CLOSED: `world_seed_random_state_bound`,
`router_numeric_parity_qualified`, `full_router_graph_qualified`,
`stock_noisechunk_interpolation_observed`,
`independent_var_sem_admitted`, `production_worldgen_enabled`.
