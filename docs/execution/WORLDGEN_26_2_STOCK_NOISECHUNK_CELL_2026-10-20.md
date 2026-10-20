# Helve — first real Minecraft Java 26.2 stock NoiseChunk cell numerical frontier

**20 October 2026 · protocol 776 · DataVersion 4903**

The four-seed source-owning stock `finalDensity.compute(SinglePointContext)`
oracle is complete, permanently frozen, and CI green. The **second
upload is byte-for-byte the same verified original JSON** (25,704
bytes, SHA-256
`0c294020fb2ad882f6ed88e5759e032c6955d48be3cfef1a19a089f561bb059d`).
Do not repeat those same 128 scalar samples.

## First authentically chunk-scoped measurement

The new narrow official-JVM bridge
`tools/worldgen_java/HelveStockNoiseChunkCell262.java` constructs an
**original stock** `NoiseChunk` with real
`VanillaRegistries.createLookup`, registry-returned Overworld
`NoiseGeneratorSettings`, `RandomState.create`, original stock
`NoiseBasedChunkGenerator.createFluidPicker`, stock
`DensityFunctions.BeardifierMarker.INSTANCE`, and stock
`Blender.empty()`. It does not make a synthetic registry, invent a
density function, call a Rust implementation, or use SinglePointContext.

It explicitly checks the exact legacy 26.2 constructor (9 typed
parameters), public accessor contracts and 26.2 cell dimensions
`(4,8,-64,384)`. The **new 26.3 NoiseChunk constructor/context
changes are not imported**. A missing or incompatible API is a hard
failure with a tagged `JVM PHASE` so the original source can be
reviewed before patching.

Per authentic Overworld seed, it uses the real
`NoiseChunk.wrap(RandomState.router().finalDensity())` result and the
real Minecraft sampling lifecycle:

1. `initializeForFirstCellX()`
2. `advanceCellX(0)`
3. `selectCellYZ(16,0)` for 4×8×4 cell
   `x∈[0,3], y∈[64,71], z∈[0,3]`
4. for each fixed point `(0,64,0), (1,65,1), (2,66,2),
   (3,67,3)`, execute `updateForY(y,fY)`,
   `updateForX(x,fX)`, `updateForZ(z,fZ)` and the
   **actual wrapped** `DensityFunction.compute(NoiseChunk)`.
5. `stopInterpolation()` and validate exactly four outputs.

Four independent held-out stock seeds × four samples yield **16 raw
IEEE-754 bit observations** when the user's local official JVM run
succeeds. This is intentionally a single **cell** first-contact probe,
**not** the 16×16×384 full chunk generation lifecycle; it does not
prove every cache mode, noise lattice, aquifer, block palette, biome,
surface or feature stage. It also does not establish Rust parity.

The companion strict collector
`tools/worldgen_26_2_stock_noisechunk_cell_capture.py` refuses
any unsanctioned output path, does not copy source/JAR, requires
the pinned source+runtime JAR and the exact original SHA of the 128
prior scalar vectors, and queries the actual local official 26.2
Atlas for **nine source-owning methods**: chunk `wrap`,
`initializeForFirstCellX`, `advanceCellX`, `selectCellYZ`,
`updateForY/X/Z`, `stopInterpolation`, and
`NoiseBasedChunkGenerator.createFluidPicker`. The source-method
hashes are recorded **reviewed:false**: indexing is not an independent
VAR/SEM proof. All previously false production, compiled-router and
full-chunk qualification gates remain false. Output is source-free,
outside Git, with mode 0600.

CI tests ordered 16 raw-bit frames, geometry, values, malformed,
missing, nonfinite and reordered rows, source index, all closed gates
and **a separately compiled Java synthetic stub** exercising the same
reflective constructor + chunk methods. The synthetic fixture is
transport evidence only, never called stock Minecraft evidence.

## Source-owning command

The previous original JVM capture must remain at its original, exact
25,704-byte path and the destination must not already exist.

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_noisechunk_cell_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --previous-singlepoint /tmp/helve-26_2-stock-final-density-singlepoint-128.json \
  --output /tmp/helve-26_2-stock-noisechunk-cell-16.json
```

Upload only the resulting source-free JSON, or paste the exact
`STOCK 26.2 NOISECHUNK CELL UNQUALIFIED` / `JVM PHASE`
error including the actual exception. Do not weaken typed guards
or infer a replacement constructor from a different Minecraft
release. When successful, compare observed chunk and scalar bits
at matched XYZ coordinates where useful, but **do not demand
identity**: the stock functions may depend legitimately on
cache/interpolated context, especially wrapped markers.

## Exact state boundaries

Open evidence: actual stock original scalar oracle for four seeds;
constructor/lifecycle **proposed** until original 26.2 probe succeeds.
CLOSED:
`world_seed_random_state_bound`,
`full_router_graph_qualified`,
`router_numeric_parity_qualified`,
`stock_noisechunk_full_lifecycle_qualified`,
`independent_var_sem_admitted`,
`production_worldgen_enabled`.

After real NoiseChunk cell bits succeed, source-review the actual
wrapped delegate and cell-state/cache lifetimes; then extend
contiguously to neighbouring cells and complete X/Y/Z + slice swap
before claiming a real 16×16×384-chunk generator. The eventual Rust
path reuses Helve's existing world owner, qualified density primitives,
seeded noise implementation and scratch buffers; there is no new
owner or per-block dynamic registry/reflection.
