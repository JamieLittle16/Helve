# Helve — Minecraft 26.2 NoiseChunk adjacent-cell/slice frontier

**20 October 2026 · original Mojang JVM · Minecraft 26.2 · protocol 776.**

## Immutable baseline

PR #467 merged the **512** genuine stock Java `NoiseChunk` numbers
from one 4×8×4 cell (four seeds), and permanently froze their exact
IEEE-754 words. The earlier **16** and **128** source-owning captures
remain frozen. **Do not rerun them.** In this workspace the uploaded
original 512-source-free JSON independently matched its frozen SHA-256
`1ce45d95a09eae9d5f95754e4ef582244fa707ca08598223eeb52930d7c65fb9`.

## New bounded transport (EXPERIMENTAL, NOT canonical source review)

The separate `--stock-noisechunk-adjacent-cells` JVM mode in the
**existing** `HelveStockNoiseChunkCell262.java` reuses the same original
Overworld registry, settings, `RandomState`, actual wrapped
`finalDensity`, `NoiseChunk` constructor and interpolation functions.
Existing `--stock-noisechunk-cell-16` and
`--stock-noisechunk-complete-cell-512` remain separate modes.

For each of the same four original seeds, construct a `NoiseChunk`
at (0,0) and one at (-16,-16). For each origin, execute a candidate
bounded traversal of two consecutive X cells and two Z cells, at Y
cell indices 17, 16 and 15 (descending, world Y=72..79, 64..71,
56..63 respectively, using world minY=-64); the per-cell voxel loop
visits every X/Z value 0..3 and Y 7..0. Sampling `compute` at *every*
visited block helps reveal marker/cache lifetime effects. Emit only
each selected boundary offset (X=0 or 3; Y=0 or 7; Z=0 or 3):
**96 values per chunk**, **192 per seed**, **768 total**.
After each X column call the original `swapSlices` reflectively,
then advance the next X cell. Negative origins exercise floor-division
and negative block positions without relying on an invented noise model.

This is **a hypothesis about traversal to be reviewed**, not the stock
chunk-emplacement algorithm. Only the *actual* private original
26.2 source may determine whether loop nesting, descending Y order,
slice swaps, cache lifetimes and full vertical sweeps are faithful.
The probe explicitly does **not** require equality with old 512 values
because their traversal/context differs. The new collector rejects
wrong ordering, missing/doubled rows, nonfinite f64, wrong source/JAR
fingerprints, and any promoted production/VAR/SEM gates.

### Source review that must precede calling it canonical

On the owner's exact original archive
`$HOME/Documents/mc-source/mc-src.zip` (SHA-256
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`),
review method bodies for:

- `NoiseBasedChunkGenerator.fillFromNoise` and `doFill`:
  determine **actual** X/Z/Y cell-loop nesting, vertical traversal
  extent, block order, Y/X/Z update order and `swapSlices` placement;
- `NoiseChunk.initializeForFirstCellX`,
  `advanceCellX`, `selectCellYZ`, `swapSlices`,
  `updateForY/X/Z`, `stopInterpolation`:
  confirm buffering, cache state, interpolation axes and lifecycle;
- `NoiseChunk.wrap` and marker/cache wrappers:
  confirm whether state persists across loops and whether a partial
  2×2×3 cell window can be interpreted canonically.

The collector indexes `fillFromNoise`, `doFill` and `swapSlices`
as **identity-only / reviewed:false**, on top of the nine already-frozen
NoiseChunk source methods. A SHA is not independent semantics review.
If an original method is absent/overloaded, the collector intentionally
fails; inspect source and adapt it instead of guessing from a different
Minecraft release.

## First source-free lifecycle review packet — received

The user ran the source-owning lifecycle packet tool against the exact pinned
private Minecraft 26.2 source and Atlas on **20 October 2026**. The resulting
**8,827-byte**, source-free JSON had SHA-256
`ff46d300be0e7a683e8f301c6bc476b7babc892207540074f167b698ce4fa1b2`.
Do **not** rerun this unchanged packet just to rediscover the same calls.

It resolves **12 bounded method identities**, including actual
`NoiseBasedChunkGenerator.fillFromNoise` and `doFill`, and
`NoiseChunk.swapSlices`. Within `doFill`, the Atlas's syntactic callsite
order is `initializeForFirstCellX`, `advanceCellX`, `selectCellYZ`,
`updateForY`, `updateForX`, `updateForZ`, `swapSlices`, then
`stopInterpolation`. The former method has a same-type `doFill`
callsite. All 12 methods are still `reviewed:false`.

**Limit of this receipt:** Callsite text order alone establishes neither loop
nesting nor call arguments, absolute-versus-relative cell indices, chunk
constructor-coordinate semantics, vertical coverage, marker/cache behaviour,
nor production traversal. The source-free packet declares
`canonical_control_flow_source_reviewed:false`; all worldgen qualification
and production gates remain **false**. The existing adjacent JVM probe is an
**experimental hypothesis** until those semantics are verified and genuine
new JVM values are captured. Do not silently promote it to a canonical oracle.

## First real adjacent-cell invocation — negative-origin failure and correction

The first **actual** pinned source/JAR run, from merged PR #468 at
`a6462d1904a011c8a7a40c5b0be78e45756c7352`, stopped fail-closed:

```text
JVM PHASE: adjacent-select-0-1-0-0-17
ROOT: java.lang.ArrayIndexOutOfBoundsException
CAUSE: Index -4 out of bounds for length 5
```

This failure occurred at world-seed index zero, **second chunk origin
(-16,-16)**, first X/Z cell, Y cell 17. The experimental Java mode had
called `advanceCellX(firstCell+cellXOffset)` and
`selectCellYZ(cellY,firstCell+cellZOffset)`, with `firstCell=-4`.
The select call demonstrably supplied a negative index to a stock
5-element array; no 768-value file was produced, and the partial
stdout is **not** a valid oracle.

This repair uses **local** X/Z cell indices `cellXOffset` and
`cellZOffset` (0 or 1) for these two lifecycle calls, while keeping
the original `NoiseChunk` constructor's absolute block-space origin
and keeping `updateForX`/`updateForZ` in absolute world block
coordinates. It updates only the **experimental adjacent mode**;
previous immutable 16/128/512 captures and their vectors are untouched.
A regression test pins this separation.

**Admission boundary:** The failure makes the original index misuse
concrete; the repair's complete fidelity to vanilla's `doFill` loop
still requires independent source-body review and a successful new JVM
run. In particular, no conclusion is yet established about cache
freshness, later `swapSlices` calls, or canonical chunk traversal.
All production/VAR/SEM and canonical gates remain **false**.

## One new original JVM run — only after source inspection

```bash
cd ~/Crucible
git switch main && git pull --ff-only
# Or check out this branch's merged revision.
python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py
python3 -m unittest tools.tests.test_worldgen_26_2_stock_noisechunk_adjacent_capture
python3 -m unittest tools.tests.test_worldgen_26_2_noisechunk_lifecycle_review_packet

# Source-free syntactic call-order aid; does NOT certify production control flow.
python3 tools/worldgen_26_2_noisechunk_lifecycle_review_packet.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-noisechunk-lifecycle-review.json

# Inspect exact original source traversal against this packet BEFORE labelling
# the next experiment canonical. The mode remains explicitly experimental.
python3 tools/worldgen_26_2_stock_noisechunk_adjacent_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-stock-noisechunk-adjacent-768.json
```

Output is exclusive-created (no overwrites), `0600`, source-free
and capped. Share only that JSON or the exact failure phase and
source-free review findings. **Do not commit** source, Atlas, original
JAR, or full original capture. Do **not** freeze these 768 values as
canonical until verifying the real 26.2 production traversal and
investigating any JVM state failure. The existing source-free 512
fixture is the only complete-cell baseline, not a canonical generated
chunk.

## Engineering boundary

All seven gates stay **false**:
`stock_noisechunk_canonical_traversal_qualified`,
`stock_noisechunk_full_lifecycle_qualified`,
`world_seed_random_state_bound`, `full_router_graph_qualified`,
`router_numeric_parity_qualified`,
`independent_var_sem_admitted`, and
`production_worldgen_enabled`.

Next: source-review the exact control flow and adjust this candidate
until it matches production; establish immutable source-owned
inter-cell bitwords, then implement a compiled, seed-initialized Rust
finalDensity evaluator leveraging the existing optimized kernels.
Do not create a second world owner or publish procedural chunks yet.
