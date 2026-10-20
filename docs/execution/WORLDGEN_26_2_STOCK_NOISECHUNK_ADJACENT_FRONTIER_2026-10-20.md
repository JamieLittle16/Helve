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
**experimental hypothesis** even though genuine adjacent-cell values have
now been captured; its production-equivalent semantics remain unreviewed. Do not silently promote it to a canonical oracle.

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
still requires independent source-body review. A later corrected JVM
run did succeed; it does not independently certify the source control flow. In particular, no conclusion is yet established about cache
freshness, later `swapSlices` calls, or canonical chunk traversal.
All production/VAR/SEM and canonical gates remain **false**.

## Successful 768-value genuine stock capture — immutable experimental fixture

The corrected PR #469 (`66590d26e91054d2289422dab1fcdf007b006de7`)
ran successfully on the user's pinned 26.2 source archive and official
server JAR. Its bounded original-JVM numeric observations were uploaded
and independently checked on **20 October 2026**:

- **768 exactly** finite binary64 words; four seeds, two chunk origins
  `(0,0)` and `(-16,-16)`; each 96 sampled boundary positions.
- **All 12 source method fingerprints** coincide with the previously
  recorded exact source-free lifecycle review packet.
- **32/32 exact raw IEEE-754 bitwise matches** at positions overlapping
  the frozen original 512 same-cell values, covering all four seeds.
  This is a genuine cross-capture consistency check, not a declaration
  that either traversal is the stock production traversal.
- **Original source-free JSON:** exactly **150,067 bytes**, SHA-256
  `86f33de3a4fe19a6bcc202badaaeb23bdef83bab29405e01534bd12c226bbcc1`.
- **Checked-in raw word fixture:** 768 lines of 16 lowercase hex
  digits, **13,056 bytes**, SHA-256
  `906ef4684d025d633e7d04f8c963b62b41c725b800739ce37e3256d8f484c95f`.
  Path:
  `vanilla/reports/worldgen-26_2-stock-noisechunk-adjacent-768-bits.txt`.

The original 150,067-byte JSON stays **private/out of Git**. The fixture
contains only source-free raw numeric observations, not source code or
full captured provenance. The frozen
`tools/worldgen_26_2_stock_noisechunk_adjacent_fixture.py`
validates full original receipt byte-for-byte if supplied, verifies all
768 numbers and their coordinates, rejects gate/source/bit tampering,
and independently validates the 32 coordinate overlaps against the
earlier immutable 512-bit fixture. CI needs neither the original source
archive nor the official JVM to replay this source-free qualification.

Run the cheap, source-free verification (do **not** recapture the already
completed 16/128/512/768 sample sets):

```bash
cd ~/Crucible
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_stock_noisechunk_adjacent_fixture.py
python3 -m unittest tools.tests.test_worldgen_26_2_stock_noisechunk_adjacent_fixture

# Only if the exact original JSON still exists locally:
python3 tools/worldgen_26_2_stock_noisechunk_adjacent_fixture.py \
  --capture /tmp/helve-26_2-stock-noisechunk-adjacent-768.json
```

**Precise limit:** This certifies an **observed experimental candidate**
across a real adjacent-cell and slice-swap lifecycle, *not* original
`NoiseBasedChunkGenerator.doFill` control-flow equivalence, full
vertical extent, source-reviewed cache/marker semantics, or a compiled
Rust world-seeded finalDensity evaluator. No canonical, VAR/SEM,
numerical-router, or production worldgen gate may open. Next real work
is a bounded source-owned **semantic** review of the exact stock
`doFill` loop nesting, coordinate arguments, and `NoiseChunk`
buffer state, followed by Rust numeric parity against these immutable
test vectors, not another blind Java capture.

## Next private source-owned semantic-review frontier: nested control structure

All frozen stock JVM values are already captured; do NOT recapture any
16/128/512/768 numerical samples. The remaining gap is determining what
the genuine stock generator *does* with cells, buffers and cache wrappers.

The next distinct tool,
`tools/worldgen_26_2_noisechunk_structural_review.py`,
reopens the **same exact private** 26.2 source archive and pinned
Atlas; validates the actual source bytes against the existing 11
method-body hashes; and emits only:

- brace-delimited `for` / `if` / `while` / `switch` / exception and block
  nesting (relative lines, sanitized header hash and operator shapes);
- selected lifecycle call names, opaque argument expression fingerprints,
  number of arguments and enclosing-control IDs;
- explicit counts for unbraced controls that were **not** structurally
  resolved, and all qualification gates forced **false**.

It covers the real `doFill` / `fillFromNoise` plus nine relevant
`NoiseChunk` methods. The earlier flat lifecycle packet cannot
answer even loop ancestry; this tool adds that missing structural layer.
Neither packet by itself verifies semantics: without evaluating branch
conditions, loop-variable meanings, cache marker state or dynamic calls
we still cannot declare a canonical Mojang production traversal.

**One private, original-source run** from the first merged revision
containing this new script:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_noisechunk_structural_review.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-noisechunk-structural-review.json
```

The output was successfully captured and validated: use the frozen
27,255-byte receipt above; do not rerun or re-upload it.
We can then compare the stock `doFill` call nesting against the
experimental X/Z/Y and `swapSlices` traversal, inspect only
the remaining exact private method obligations, and decide whether to
adapt the Rust workspace/caches. Do not promote any review flag based
only on hashes or brace nesting.


## Real 26.2 source-owned structural review — complete receipt (20 October)

The user completed the source-owning loop ancestry run after PR #471
merged at `bd4065acf393573fc57ccf1b7e13a2d51f1f9b24`.
The genuine source-free private JSON has **27,255 bytes**, SHA-256
`130070ea39c064d1de37fa0fa3b651b8799e650e066b176a2f419e3e5ff89fab`,
and matches the existing exact source archive and **11/11** original
method body identities. Every method reports `unbraced_control_count=0`
and `source_method_reviewed=false`. No source text is included.

**New genuine structural evidence:**
- `doFill` has six nested `for` loops with increment, increment,
  decrement, decrement, increment, increment lexical direction hints.
- `initializeForFirstCellX` is before the outer loop.
- `advanceCellX` is inside only the outer loop.
- `selectCellYZ` is inside three enclosing loops; `updateForY` in
  four, `updateForX` in five, and `updateForZ` in six.
- `swapSlices` occurs **inside only the outer loop**, after the
  nested block traversals; `stopInterpolation` after that loop.
- `fillFromNoise` calls `doFill` under a `try` block and has
  separate cleanup structure.

That hierarchy is **consistent with the experimental** X/Z/Y/Y/X/Z
sampling order, but lexical structure does not establish exact loop
bounds, variable bindings, relative/absolute argument expressions,
dynamic cache behaviour, or full-height traversal. No genuine
canonical semantics or VAR/SEM gates have opened.

The checked-in **6,567-byte source-free condensed fixture** is
`vanilla/reports/worldgen-26_2-noisechunk-source-free-brace-ancestry.json`
(SHA-256 `7a62758cabb02e7370d7708955c58bdf2010d67551b12059543ae9dd790621a7`).
The validator
`tools/worldgen_26_2_noisechunk_structural_fixture.py` pins the
original JSON bytes/SHA if supplied, checks all source identities and
call/loop ancestries, and refuses to promote any qualification flags.

A second important **real-stock numerical counterexample** from the
existing 768 words: naive trilinear interpolation of the *final output*
from eight independently observed corner values fails to reproduce
the interior `finalDensity` values. For seed
`0x0123456789abcdef`, chunk origin `(0,0)`, world point
`(3,71,3)`, the absolute difference is approximately `0.02416587807`.
A new Rust negative-control regression checks all eight seed/chunk
contexts directly from the immutable stock bits. This is **not** Rust
`finalDensity` parity. It prevents treating the final node as a
plain trilinearly interpolated scalar field.

**Do not repeat any source/JVM capture.** To verify the already
collected structural receipt and compact source-free evidence:

```bash
cd ~/Crucible
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_noisechunk_structural_fixture.py
# Optional: only when the original exact JSON still exists locally
python3 tools/worldgen_26_2_noisechunk_structural_fixture.py \
  --capture /tmp/helve-26_2-noisechunk-structural-review.json
```

**Next actual source-semantic obligation:** identify the exact original
loop variable/bound/argument laws, full vertical sweep, start/stop and
cache/interpolator state transitions; then compile the entire observed
world-seeded finalDensity graph in the existing borrowed Rust density
program without a second world owner. Numeric parity must compare
computed Rust outputs to original Java bits.

## First compiled source-observed Rust mixed delegate under existing density program

The existing `StockVanillaMixedDensity262` is already checked against
**1,920 actual stock Minecraft 26.2 JVM** mixed Noise/Y-primitive
`add/mul` results, including the positive-zero `Ap2` shortcut
and signed-zero `MulOrAdd` distinction. A new
`StockDensityNode262::ObservedMixed` puts this **existing**
source-observed evaluator inside the immutable, bounded Rust density
program rather than creating another evaluator/world owner.

Its one-node compiled path reuses the specialized scalar/coherent-plane/
caller-owned-cell routines. A separate executable Rust regression
recomputes **all 1,920** independent official Java words through that
compiled leaf, checks signed-zero delegate distinction, and tests
full plane/cell scalar-bit coherence. Arbitrary eager expression DAG
combination is explicitly **not** a newly qualified Java 26.2 factory
law: composing observed components does not admit the full Overworld
`finalDensity` router.

This is the first narrow compiled observed mixed subgraph; it is **not**
the finalDensity evaluator, not source-reviewed `doFill` cache/marker
semantics, and not approval for chunk publication. Keep all production,
VAR/SEM, canonical traversal and full-router parity gates closed.

## Actual `finalDensity` root operator/map/holder semantic diagnostic

Stock bound 26.2 `finalDensity` is recorded as a Java
`DensityFunctions$Ap2` with first-level
`Mapped` and `HolderHolder` children. **That class identity does
not determine whether the root applies ADD, MUL or another operator.**
The earlier 128-value real SinglePointContext JVM oracle provides
exact root **outputs**, not child values or mapping/holder types. The
Rust `ExplicitAp2Multiply` work in PR #475 is therefore
not authorization to compile the stock root as multiplication.

The new **distinct** source-owned tool
`tools/worldgen_26_2_stock_final_density_root_semantics.py` reuses
the exact four seeds × 32 XYZ positions of the **already frozen**
128-word actual stock final-density fixture. It rebuilds genuine
VanillaRegistries → RandomState → Overworld NoiseRouter **once per
seed**, reads (via typed record accessors) the runtime Ap2 operator
enum, Mapped transform enum and immediate input class, and follows
the HolderHolder **public Holder.value()** into its concrete bound
density class. At those **same** points it computes both actual Java
first-level children and the original final root, and it refuses to
accept any final root word that differs from the existing immutable
128-word fixture.

It also checks the pinned original source ZIP and Atlas, stock server
JAR, and exact existing Ap2/HolderHolder method identities. The first
source-owner run after PR #476 exposed a reviewer mistake: **Mapped
does not have a directly indexed compute(FunctionContext) body**.
Instead, the already-pinned 26.2 `DensityFunctions$PureTransformer.compute`
body (SHA-256
`80087cd337e4ac54a98884a9c47579f4573740fc983f033ed2243e579515a6dd`)
is the delegated candidate. The repaired review now requires **zero
direct Mapped.compute declarations**, **exactly one** original indexed
PureTransformer.compute with the existing known body fingerprint, and
the **actual runtime** Mapped.compute declaring class to equal
PureTransformer. This corrects the diagnostic; it is not a new
independent source-law admission. No stock root operator/child output
has been observed by this new run yet. It does NOT
interpret those source bodies. No private Java source or original
registry data is committed or exported. Output is a source-free,
bounded, mode-0600 private JSON. **This is new operator/child evidence,
not a redundant repeat of the earlier 128-value root capture.**

Run exactly once on a merged checkout with the previously verified
local source, Atlas and official JAR:

```bash
cd ~/Crucible
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_root_semantics.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-final-root-semantics-128.json
```

Upload **only** the source-free result JSON or the precise fail-closed
error. A failure involving an unknown record component is a legitimate
unresolved source-law frontier: do not invent or auto-adjust the
Java operator or the Mapped/Holder data. Full semantic review,
mapped transform math, recursive holder graph, NoiseChunk markers,
full-router numeric parity, VAR/SEM and production worldgen
remain **OPEN**.

## Engineering boundary

All seven gates stay **false**:
`stock_noisechunk_canonical_traversal_qualified`,
`stock_noisechunk_full_lifecycle_qualified`,
`world_seed_random_state_bound`, `full_router_graph_qualified`,
`router_numeric_parity_qualified`,
`independent_var_sem_admitted`, and
`production_worldgen_enabled`.

Next: complete the original 26.2 control-flow and cache/marker source
review, then reuse the **already frozen 768 inter-cell reference words**
for exact Rust numeric parity; build a compiled seed-initialized
finalDensity evaluator using the existing optimized kernels.
Do not create a second world owner or publish procedural chunks yet.
