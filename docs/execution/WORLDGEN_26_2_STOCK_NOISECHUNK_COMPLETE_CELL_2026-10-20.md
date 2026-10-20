# Helve — bounded complete 4×8×4 stock NoiseChunk cell numeric frontier

**20 October 2026 · Minecraft Java 26.2 · Protocol 776 · DataVersion 4903.**

## Grounded starting point

The original stock JVM captured a real 16-point `NoiseChunk` cell
numerical oracle for four independent world seeds (merged PR #465).
The original 8,485-byte source-free JSON SHA is
`3ea20f5ed1b1236f5e166a847e5405ca54169d39f98810e0c8bf7029e3e74169`.
The first sample per seed at `(0,64,0)` exactly matches stock
`SinglePointContext` for that coordinate. **No global context
equivalence or full lifecycle is claimed**. Those 16 bits are frozen.

## Next experiment: all 128 voxel positions of that ONE cell

The previous Java stock bridge
`tools/worldgen_java/HelveStockNoiseChunkCell262.java`
has a **new, separate optional mode**
`--stock-noisechunk-complete-cell-512`. The old
`--stock-noisechunk-cell-16` must remain entirely unchanged in output
and in the existing frozen oracle.

Using the same actual 26.2 stock runtime,
`VanillaRegistries` provider, `NoiseGeneratorSettings.OVERWORLD`,
`RandomState.router().finalDensity`,
`NoiseBasedChunkGenerator.createFluidPicker`,
`DensityFunctions.BeardifierMarker.INSTANCE`,
`Blender.empty`, exact constructor, `NoiseChunk.wrap`,
and the old proven four-seed sampling boundary, the added mode
enumerates exactly:

- **4** independently pinned 64-bit world seeds;
- **128** explicitly ordered block coordinates within one
  `x=0..3, y=64..71, z=0..3` cell;
- **512** original JVM `DensityFunction.compute(NoiseChunk)` raw
  IEEE-754 f64 words, framed and checked;
- the 128 positions are ordered **Y ascending → X ascending →
  Z ascending**; values use the same explicit stock
  `updateForY`, `updateForX`, `updateForZ` calls before compute;
- the same `initializeForFirstCellX`, `advanceCellX(0)`,
  `selectCellYZ(16,0)`, `stopInterpolation` boundary.

The new source-owning wrapper
`tools/worldgen_26_2_stock_noisechunk_complete_cell_capture.py`
**requires exact original 8,485-byte receipt SHA** via the frozen
fixture, plus locked 26.2 source archive/JAR, the *same nine* actual
`NoiseChunk`+fluid-picker indexed source method body hashes
(`reviewed:false`), and strict 512 ordered finite raw-bit words.
Only the source-free JSON is written with permissions 0600 and an
exclusive-create policy outside the repository. No source, private
JAR, Atlas DB or giant original graph is checked in.

Important distinction: this is the probe's **experimental traversal
order**, not a manually admitted proof that this order matches the
actual `NoiseBasedChunkGenerator.fillFromNoise` block emplacement
order. Every source/VAR/SEM, canonical traversal, complete
interpolation lifecycle, Rust final-router bit parity, and
production-worldgen gate stays **false**. The bridge uses real stock
functions rather than implementing or duplicating their math.

## Run only after PR merges with green checks

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --previous-cell /tmp/helve-26_2-stock-noisechunk-cell-16.json \
  --output /tmp/helve-26_2-stock-noisechunk-complete-cell-512.json
```

Upload this new source-free JSON (or the exact `JVM PHASE` error).
The output must not exist beforehand.

## Next engineering milestone beyond ONE cell

Review actual original 26.2 chunk generation loop and its source
method fingerprint: distinguish when to call `advanceCellX`,
`selectCellYZ`, `updateForY/X/Z`, `swapSlices`,
`stopInterpolation`, and any cache/interpolator initialization,
including Y/Z and next-X boundaries. Capture **adjacent X/Z/Y cells
and slice transitions** after source-pinning these lifetimes. Only
then consider broad generated-chunk numerical and block-choice parity.

A successful original 512 probe is a **reference for the original
JVM's explicitly requested traversal**, not a generated-chunk result.
When designing the eventual compiled Rust evaluator, retain Helve's
existing server-lifetime world owner, seeded noise kernels, typed
density operations, and caller-owned contiguous scratch. No duplicate
ownership, per-voxel virtual registry access, source math copying,
or false performance/production qualification.
\n## 20 October 2026 update — actual complete-cell capture SUCCEEDED; do not repeat

The source-owning Minecraft 26.2 JVM successfully emitted all **512**
real `NoiseChunk`-context raw-bit values. The original JSON is
**122,792 bytes**, exact SHA-256
`1ce45d95a09eae9d5f95754e4ef582244fa707ca08598223eeb52930d7c65fb9`.
One 4×8×4 interpolation cell, four world seeds, 128 ordered coordinates
per seed, 512/512 finite distinct raw IEEE-754 words. The stock
`NoiseRouter.finalDensity` wrapper is the observed
`DensityFunctions$Ap2` in every seed.

**All 16 earlier original stock values** (four coordinates × four seeds)
are reproduced **bit-for-bit** at the matching cell coordinates in the
512-observation JSON, independent of their ordering in the full-cell
file. This corroborates the earlier original 16-vector receipt
(SHA `3ea20f5ed1b1236f5e166a847e5405ca54169d39f98810e0c8bf7029e3e74169`),
which is already frozen by PR #465.

New immutable compact numeric reference:
`vanilla/reports/worldgen-26_2-stock-noisechunk-complete-cell-512-bits.txt`
(8,704 bytes, 512 source-free hex bitwords), SHA
`71da8201d571fbd2856848066a18b5f844a83533742937e2b0dcefcae55049eb`.
Use `tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py`
to verify the fixture and all 16 overlaps; pass `--capture` to
additionally authenticate the exact private original 122,792-byte
receipt. CI exercises the same fail-closed verifier and refuses
altered source identities, positions, values, or production gates.
No private original full JSON, source archive or JVM binaries are
checked into GitHub.

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py

# Optional exact source-owning original JSON proof:
python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py \
  --capture /tmp/helve-26_2-stock-noisechunk-complete-cell-512.json
```

**Important: the capture's traversal is experimentally
Y-ascending / X-ascending / Z-ascending** and is NOT yet source-reviewed
as Mojang's production block emplacement order. A notable outlier
for seed `0x0123456789abcdef` at (0,70,3) is about 0.335 whereas
nearby values are about 0.08; it is an actual captured raw bit
(`0x3fd56bd4106a5f4d`), *not proof* of a Minecraft
terrain discontinuity. Exact caching/interpolation lifecycle and
order-dependence require separate review and differential experiments.
Do not smooth the outlier or silently pass these 512 values off as
canonical generated terrain.

**Next action is no new capture of the same cell.** Source-review
`NoiseBasedChunkGenerator.fillFromNoise` and
`doFill`/helpers in the exact original 26.2 archive,
the `NoiseChunk` slice/column interpolation and cache transitions
(`initializeForFirstCellX`, `advanceCellX`,
`selectCellYZ`, `updateForY/X/Z`, `swapSlices`,
`stopInterpolation`). After identifying the exact canonical ordering,
capture adjacent cells across X, Z, and Y plus slice transitions with
new original JVM bounded oracles. Reuse the existing registry and
`NoiseChunk` bridge and the Rust worldgen primitives; do not
invent another owner or duplicate the noise kernel.

**Gates still CLOSED:** `stock_noisechunk_canonical_traversal_qualified`,
`stock_noisechunk_full_lifecycle_qualified`,
`router_numeric_parity_qualified`,
`world_seed_random_state_bound`,
`full_router_graph_qualified`,
`independent_var_sem_admitted`,
`production_worldgen_enabled`.

For complete instructions continue from
`docs/execution/HANDOFF_2026-10-20_HELVE_WORLDGEN_AFTER_512.md`.
