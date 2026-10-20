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
