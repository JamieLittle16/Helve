# Helve — Worldgen handoff after the successful 512-value stock NoiseChunk cell

**Handoff date:** 20 October 2026 (Europe/London).  
**Repo:** https://github.com/JamieLittle16/Helve  
**Starting branch:** `main`. Before this handoff's fixture/docs PR, verified
`main` was `ce523a3dcda7328f66393fcdf5344c52c4142717`,
which already **included merged PR #466**. Refresh HEAD, open PRs and
CI on entry; this SHA is not a promise that main has stopped moving.  
**Target:** Minecraft Java **26.2**, protocol **776**, DataVersion **4903**.
**User checkout:** `~/Crucible`, branch `main`.  
**Purpose:** seamless next-context worldgen work. **No redoing successful
JVM captures, source inventories, R2C import or numeric noise kernels.**

## Immediate executive state

**The official stock Java 26.2 runtime has now successfully evaluated
`NoiseRouter.finalDensity` through an authentic wrapped
`NoiseChunk` at every one of the 128 voxels of one 4×8×4 cell, for
four world seeds: 512 finite raw IEEE-754 `f64` results.**

The actual 512-source-free JSON was uploaded in the conversation as
`helve-26_2-stock-noisechunk-complete-cell-512.json`.
Size **122,792 bytes**, exact SHA-256:

`1ce45d95a09eae9d5f95754e4ef582244fa707ca08598223eeb52930d7c65fb9`.

Every output is finite. 512/512 bitwords are distinct. All **16**
original independently captured measurements (four positions × four
seeds) **match the corresponding values exactly, bit for bit** within
the new 512 results. Their two authentic receipts did not require
replacing the vanilla registry or copying source math.

**This handoff PR freezes the newly received 512 result words**, without
checking in the original private JSON:
`vanilla/reports/worldgen-26_2-stock-noisechunk-complete-cell-512-bits.txt`,
size **8,704 bytes**, SHA-256
`71da8201d571fbd2856848066a18b5f844a83533742937e2b0dcefcae55049eb`.
New verifier
`tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py`
checks the 512 bits, previous 16 overlaps and closed gates, with
optional exact-byte validation of the original stock JSON. CI
regression tests enforce this.

**The next action is NOT another 4×8×4 single-cell capture or shallow
NoiseRouter inventory.** It is to inspect **the original 26.2
NoiseBasedChunkGenerator and NoiseChunk cache/interpolation lifecycle**
and then observe **canonically ordered adjacent cell transitions**,
before building or qualifying a complete Rust Overworld density
evaluation.

## Verified merged PR progression (20 October 2026)

| PR | Completed work |
|---|---|
| #457–#458 | Four-seed actual stock NoiseRouter 15 named roots and package-private record-access fix |
| #459 | Bounded depth-four density DAG inventory; **structure only**, all gate flags false |
| #460 | All 32 four-seed `HolderHolder` bindings; eight per seed; actual `Holder$Direct` delegates |
| #461 | Original-JVM `finalDensity.compute(SinglePointContext)` capture bridge |
| #462 | Freeze **128** official stock single-point raw-bit reference values |
| #463 | First actual `NoiseChunk`-context 4×8×4-cell **16-point** JVM bridge |
| #464 | Exact `BeardifierMarker.INSTANCE` reflection fix for package-private nested enum; toy regression |
| #465 | Freeze **16** authentic source-owned `NoiseChunk` values, including four exact matching original SinglePointContext intersections |
| #466 | Complete 4×8×4-cell JVM capture mode, **512 points**; existing 16-point JVM mode preserved; new source-pinned collector and synthetic tests |

**No need to reopen any of these.** This handoff adds the 512-result
numerical fixture and updates the current execution guide rather than
reimplementing the complete-cell bridge. Check this handoff PR's merged
status and the latest main HEAD before making new branches.

## Exact authoritative evidence and private environment

Pinned source/target:
- Original source archive:
  `$HOME/Documents/mc-source/mc-src.zip`;
  SHA-256 `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.
- Official server JAR:
  SHA-256 `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`.
- Atlas: `.crucible/vanilla/atlas.sqlite`.
- Lock: `vanilla/vanilla.lock.toml`.
- Original real-worldseed frontier:
  `/tmp/helve-26_2-random-state-binding-frontier-01.json`.

Previous bounded shape/raw numerical receipts:

| Evidence | Private/source-free file on user machine | Exact original receipt SHA-256 | Git status |
|---|---|---|---|
| Fifteen stock router roots × 4 seeds | `/tmp/helve-26_2-stock-router-roots-4.json` | `81cc1fb15388998f9b812803ee96a30c792ef68df8120490b05f38acd3338736` | Source-free root evidence; not a full graph |
| Depth-4 density DAG × 4 seeds | `/tmp/helve-26_2-stock-router-graph-depth4.json` | `5911470e36725da99e7b82b5b8b4eef03a1d150662aa44c71b6c64340e4a46fb` | Source-free structural evidence |
| 8 `HolderHolder` bindings × 4 seeds | `/tmp/helve-26_2-stock-router-bound-holders-4.json` | `1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64` | Original typed binding observation |
| 128 real `SinglePointContext` finalDensity bits | `/tmp/helve-26_2-stock-final-density-singlepoint-128.json` | `0c294020fb2ad882f6ed88e5759e032c6955d48be3cfef1a19a089f561bb059d` | Frozen PR #462 |
| 16 real `NoiseChunk` first-contact cell bits | `/tmp/helve-26_2-stock-noisechunk-cell-16.json` | `3ea20f5ed1b1236f5e166a847e5405ca54169d39f98810e0c8bf7029e3e74169` | Frozen PR #465 |
| **512** real complete cell bits | `/tmp/helve-26_2-stock-noisechunk-complete-cell-512.json` | **`1ce45d95a09eae9d5f95754e4ef582244fa707ca08598223eeb52930d7c65fb9`** | **New 512 rawbit fixture in handoff PR** |

The 128 rawbits fixture is
`vanilla/reports/worldgen-26_2-stock-final-density-singlepoint-128-bits.txt`
(2,176 bytes, SHA
`058846dd4c755802ffe43f829b109884331962712ac7556f4d5cb4320a597e4f`).
The original 16 rawbits fixture is
`vanilla/reports/worldgen-26_2-stock-noisechunk-cell-16-bits.txt`
(272 bytes, SHA
`aa65bf127ecbf17864f35fbef177afbd4c6c0d90331566017427a0a053409289`).

**Privacy:** All raw original source, actual server JARs, Atlas indexes
and complete original JSON receipts remain on the user's machine or
as conversation upload. Only source-free rawbit fixtures, verifiers,
bounded numeric status and docs may be published. Never print or
commit original Minecraft source bodies. `reviewed:false` source
method hashes are identity receipts, NOT independently proven source
laws.

## Exactly what the new 512 proof establishes

Four seeds:
`0x0123456789abcdef`,
`0x7fffffffffffffff`,
`0x8000000000000001`,
`0xf0e1d2c3b4a59687`.

The original bound stock Overworld
`RandomState.router().finalDensity` is wrapped into a real
`NoiseChunk`, using the stock provider, registered generator
settings, actual fluid-picker, genuine marker, empty blender, and
26.2 constructor (no synthetic registry or rebuilt graph). The
single cell is `cell_x=0, cell_y=16, cell_z=0`:
`x=0..3`, `y=64..71`, `z=0..3` (cell width 4, cell height
8, world minY -64, height 384). Observed root wrapper class
`DensityFunctions$Ap2`. Exactly **128** positions per seed,
traversed **Y-ascending, then X-ascending, then Z-ascending**,
with actual original `NoiseChunk.updateForY/X/Z` and compute
calls, and the bounding `initializeForFirstCellX,
advanceCellX(0), selectCellYZ(16,0), stopInterpolation` calls.
The existing 16-point single-cell mode remains unchanged and
its four specified positions match the full 512 independently
for every seed.

**Critical limitation:** The 512-order is a deliberately chosen
**experimental** traversal. Its correspondence to the *actual*
`NoiseBasedChunkGenerator.fillFromNoise` **production order is not
source-reviewed or admitted**. It neither proves all cache/interpolator
states are valid nor samples neighbouring Y/Z/X cells, slice swaps,
full chunk, aquifers, block determination, surface rules, biomes,
features or live generation. Numerical values can be order/caching
sensitive. For example actual seed
`0x0123456789abcdef` recorded at `(0,70,3)` the real bitword
`0x3fd56bd4106a5f4d` (~0.335), much higher than some
neighbouring samples around 0.08. Do **not** assume this is a true
terrain discontinuity; it motivates explicit controlled traversal
order and cache investigations. Never silently 'correct' observed
bits to a smoother model.

### Current gates (ALL STILL FALSE)

`stock_noisechunk_canonical_traversal_qualified`  
`stock_noisechunk_full_lifecycle_qualified`  
`world_seed_random_state_bound` (production-grade Rust router bound)  
`full_router_graph_qualified`  
`router_numeric_parity_qualified`  
`independent_var_sem_admitted`  
`production_worldgen_enabled`

These flags are semantic promises. Do not flip them based on a
successful original JVM capture or synthetic Java harness.

## Existing Rust substrate — reuse, do not rewrite

The original seeded noise and arithmetic substrate has already
advanced well beyond basic noise experimentation. Relevant real paths:

- `crates/world/helve-world-gen/src/registered_noise_state_262.rs`
- `crates/world/helve-world-gen/src/seeded_registered_noise_262.rs`
- `crates/world/helve-world-gen/src/improved_noise_262.rs`
- `crates/world/helve-world-gen/src/explicit_noise_stack_262.rs`
- `crates/world/helve-world-gen/src/density_noise_direct_262.rs`
- `crates/world/helve-world-gen/tests/explicit_noise_stack_262.rs`
- `crates/world/helve-world-gen/tests/density_noise_direct_262.rs`
- `crates/world/helve-world-gen/benches/improved_noise_262.rs`
- `crates/world/helve-world-gen/benches/worldgen_cold.rs`

Earlier PRs #447–#456 already obtained independently pinned stock
noise registrations and world-seed replay plus the 576 held-out vectors,
1,920 mixed-density output vectors, and qualified lower-level Rust
implementations. Those do NOT automatically confer all actual
Overworld `finalDensity` DAG laws and `NoiseChunk` cache semantics.
Read the qualified portions, use a single Rust world-seed owner
with prebuilt immutable state, caller-owned contiguous scratch and
allocation-free interior loops. Avoid copies, virtual dispatch,
per-block hash lookups and repeated noise initialization in the
hot path. Do not fork an independent sampler or world owner.

R2C remains a **real visually verified pregenerated/imported world
in a stock client**; it is distinct from procedural world generation.
R2D's persistence/liveness readiness work is also a distinct track:
see `docs/execution/R2C_TO_R2D_READINESS_HANDOFF_2026-10-19.md`.
Do not conflate R2C rendered import, R2D durable world state and
procedural Overworld generation; preserve the server-lifetime semantic
world owner and reuse its publication boundary when new terrain is
eventually admitted.

## Immediate fresh-context start — no user requests for repeated data

1. `git switch main && git pull --ff-only`; verify actual GitHub main
   SHA, latest merged PRs and three CI checks (CI, CLA, Worldgen
   Qualification). Confirm this 512-fixture/handoff PR merged.
2. Read **this document** and
   `docs/execution/WORLDGEN_26_2_STOCK_NOISECHUNK_COMPLETE_CELL_2026-10-20.md`.
   Do NOT rerun `--stock-noisechunk-cell-16`,
   `--stock-noisechunk-complete-cell-512`, root/holder inventories,
   or original scalar capture; all data are frozen.
3. Run the source-free regression fixture **without private source**
   as a smoke test:
   ```bash
   python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py
   ```
   Optional, only if reauthenticating the original uploaded file:
   ```bash
   python3 tools/worldgen_26_2_stock_noisechunk_complete_cell_fixture.py \
     --capture /tmp/helve-26_2-stock-noisechunk-complete-cell-512.json
   ```
4. Start a **new separate PR** for the *26.2 production block sampling
   traversal and cell/slice lifecycle source review*, not for
   another single-cell number-capture transport.

## Precise forward engineering plan

**Stage A — pin the true canonical stock chunk algorithm.**
On the user's original 26.2 source archive and Atlas, inspect the
specific current `NoiseBasedChunkGenerator.fillFromNoise` /
`doFill` or actual equivalent production path, `NoiseChunk`'s
actual visitor/wrapping, interp cell configuration, `swapSlices`,
`initializeForFirstCellX`, `advanceCellX`, `selectCellYZ`,
`updateForY/X/Z`, `stopInterpolation` and cache marker /
interpolator callbacks. Determine exact (X/Y/Z) outer/inner loop order,
positive/negative coordinates, off-by-one extent, fluid/block
interactions, cell-to-cell continuity, and source constructor signatures
for **26.2** only. Store method-owner/body hashes and the conclusions
in **source-free** documentation. Source method hashes currently say
`reviewed:false` and must not be promoted without real review.
If unavailable in remote GitHub, add a bounded source-owning-only
review packet; do NOT infer laws from 26.3 or a wiki.

**Stage B — canonical stock numeric oracles crossing real boundaries.**
Extend existing `tools/worldgen_java/HelveStockNoiseChunkCell262.java`
with a distinct new optional mode; keep prior 16 and 512 modes
bitwise unchanged. Under the verified real loop order and
noise/noisechunk state, sample at least:
- consecutive cells in X and Z and adjacent vertical Y cell,
- an X slice flip through `swapSlices` and a second X column,
- previously sampled overlapping edge/corner positions in controlled
  conditions, where lawful,
- multiple independent seeds and at least one negative X/Z coordinate.

Pin exact finite raw IEEE `f64` values from the original stock JVM
and freeze a compact bit fixture and fail-closed schema. Explicitly
distinguish **canonical** production traversal from the former 512
**experimental** traversal. Look for reproducible differences/order
effects; compare only positions under matching state and traversal,
not blindly assert context equality. Resist creating new unrelated
capture scripts when one targeted extension to the proven bridge
suffices.

**Stage C — source-review and compile actual finalDensity DAG.**
Close the exact stock `DensityFunctions` evaluation and
`NoiseChunk` delegate laws on **this observed graph** before
implementing them: `Ap2`, `Mapped`, `Marker` (including caches),
`RangeChoice`, holders, splines and keyed noises. Use the existing
source-free roots/graph/holder evidence, the frozen real scalar-128,
cell-16 and complete-cell-512 outputs to build bitwise Rust tests
that really execute Rust code. Prefer an immutable compact
instruction/program representation, cold keyed holder resolution
and reusable thread/caller-owned workspaces; respect signed-zero,
interpolation and floating-point evaluation order. Compare across
held-out coordinates and seeds; do NOT claim Rust parity by merely
re-reading a fixture.

**Stage D — actual terrain semantics and whole-cost benchmarking.**
After canonical NoiseChunk and compiled Rust `finalDensity` parity,
add verified block decision, aquifers, sea-level fluids, biome/surface
rules and chunk publication under the existing server-world owner.
Run differential pregenerated-world and live stock-client tests and
representative whole-chunk performance benchmarks; never quote
Steel speedups before a matched comparable end-to-end test. Keep
all production authority gates closed until each independent law
and parity evidence is admitted.

### Acceptance criteria for next milestone

Source-free review names true 26.2 canonical loop, slice swap and
cache lifecycle with provenance; independently runnable stock JVM
cross-cell/slice oracle; at least one bounded contiguous neighbouring
cell example with exact finite bits and immutable schema; existing
`128`/`16`/`512` fixtures unchanged and all CI green; no source
leak, Rust hot-path regression or unsupported gate promotion. A
different method or an error must be diagnosed at the exact original
26.2 source point, not patched by inventing semantics.

## Final new-chat instruction (paste alongside this handoff)

> Continue Helve worldgen from the latest verified GitHub `main`,
> using `docs/execution/HANDOFF_2026-10-20_HELVE_WORLDGEN_AFTER_512.md`.
> The authentic 512-value stock `NoiseChunk` complete-cell capture is
> **already successful and frozen**; do not repeat the 16/128/512
> captures or the router/holder inventories. Start the original
> Minecraft Java 26.2 canonical `NoiseChunk` generation-order and
> cell/slice lifecycle review, then build the first adjacent-cell and
> slice-swap oracle, keeping Helve's efficiency/vanilla/source-law
> disciplines and CI/PR workflow. All production worldgen and VAR/SEM
> gates are still closed.

## October 20 additive handoff — PRs #468/#469 and successful stock 768

**This section supersedes the earlier unexecuted adjacent-cell to-do and
old “start the adjacent-cell oracle” instruction, but does not change the
historical original 512 baseline or any source-review/production gates.**

- **PR #468** merged at
  `a6462d1904a011c8a7a40c5b0be78e45756c7352`: the experimental
  2-chunk/2×2×3-cell/4-seed stock JVM collector and source-free method
  callsite review packet.
- **PR #469** merged at
  `66590d26e91054d2289422dab1fcdf007b006de7`: correct 0-based
  local X/Z cell indices for `advanceCellX` and `selectCellYZ`.
  Previous negative chunk (-16,-16) had genuinely failed at
  `adjacent-select-0-1-0-0-17`: `Index -4 out of bounds for length 5`.
  The fixed collector retains absolute world-block coordinates for
  its construction and `updateForX/Z`.
- **Source-free lifecycle receipt** collected from the user's pinned
  archive/Atlas: 8,827 bytes, SHA-256
  `ff46d300be0e7a683e8f301c6bc476b7babc892207540074f167b698ce4fa1b2`.
  Twelve method identities and syntactic callsites only; `reviewed:false`.
  Original Java bodies are not copied or reviewed semantically.
- **Genuine stock 768 numerical JSON** captured successfully *after*
  PR #469, uploaded to this conversation:
  `helve-26_2-stock-noisechunk-adjacent-768.json`.
  150,067 bytes, SHA-256
  `86f33de3a4fe19a6bcc202badaaeb23bdef83bab29405e01534bd12c226bbcc1`.
  Four world-seeds × two chunk origins (0,0),(-16,-16) × 96
  selected boundary observations = 768, all unique and finite f64 bits,
  exact source/JAR fingerprints and **32/32** exact-bit coordinate matches
  with the already frozen 512-voxel same-cell original values.
- **Next fixture PR** `worldgen/262-noisechunk-adjacent-768-fixture`:
  freeze 13,056 bytes/768 source-free hex words with SHA-256
  `906ef4684d025d633e7d04f8c963b62b41c725b800739ce37e3256d8f484c95f`,
  add original JSON byte/SHA validation, 32 frozen 512 overlaps,
  negative mutation and all-false gate tests, CI and runbook changes.
  Only describe it as merged once GitHub actually reports that.
- Reuse without recapture:
  `python3 tools/worldgen_26_2_stock_noisechunk_adjacent_fixture.py`
  and optional `--capture /tmp/helve-26_2-stock-noisechunk-adjacent-768.json`.
  Do **not** rerun old 16/128/512 or new 768 JVM sampling just to
  reproduce completed observations.

**What is solved:** a successful, source-owned **EXPERIMENTAL**
neighbour-cell + slice-swap numeric run, immutable reference bitwords,
cross-capture overlap consistency, negative-index repair. Earlier
512/128/16 samples and R2C import demo are unaffected.

**What is still open:** independent semantic/source-body review of exact
`NoiseBasedChunkGenerator.doFill` real 26.2 loop nesting, Y extent,
cache/wrapper marker and interpolation lifetime; establishing that an
adjacent candidate is **canonical** production traversal; building and
testing a seed-initialized **Rust** compiled `finalDensity` evaluation
against these stock words, plus full router/parity/VAR/SEM/production
admission. **Every canonical and production worldgen gate stays false.**

**Next concrete engineering action:** finish the source-owned semantic
loop review using the private 26.2 archive and pinned body hashes,
without publishing original code. Then implement a Rust hot-path-friendly
finalDensity evaluation against frozen real Java numerical vectors;
compare **actual Rust calculations**, not only fixture playback.
Never manufacture a source law or enable chunk publication on evidence
from a syntactic Atlas inventory alone.

The detailed runbook with exact provenance and parser CLI is
`docs/execution/WORLDGEN_26_2_STOCK_NOISECHUNK_ADJACENT_FRONTIER_2026-10-20.md`.


## Source-owned 26.2 structural control-review follow-on

After frozen 768 source-free adjacent raw bits were merged in PR #470
(main at `e94e08fd119be6ea10277a7e42c38de57e6b4a9c`),
the next work begins **actual source-backed structural review**,
not another numerical recapture. The existing 8,827-byte flat Atlas
receipt cannot determine which loops enclose `advanceCellX`,
`selectCellYZ`, `updateForY/X/Z` or `swapSlices`.

A distinct new source-owning script is being added in branch
`worldgen/262-noisechunk-structural-control-review`:
`tools/worldgen_26_2_noisechunk_structural_review.py`.
It checks original method **byte and token hashes**, then returns
bounded, source-free brace-based control ancestry, opaque argument
shapes and explicit unbraced-control counts for `doFill`,
`fillFromNoise` and 9 `NoiseChunk` methods.
The script has synthetic Java regression tests and fails closed; no
private source is committed. The detailed command and usage appear in
`WORLDGEN_26_2_STOCK_NOISECHUNK_ADJACENT_FRONTIER_2026-10-20.md`.
Once its PR merges, run it **once** against the pinned local source
archive and upload the resulting sanitized JSON. No 768/512/128/16
recaptures are required.

This structural packet is **not** independent semantic review,
canonical stock `doFill` verification, or evidence that Rust computes
stock `finalDensity` values. For actual Rust parity the compiled
world-seed/router DAG must use the existing no-allocation density
kernels, preserve 26.2 `Ap2` signed-zero/early-return behavior,
and eventually match **computed** output against the frozen Java words.

All canonical lifecycle/traversal, numerical router, VAR/SEM, and
production worldgen gates remain **false**.

## Completed private source structural receipt and Rust nontrilinearity guard

After PR #471 merged, the user completed the **one** original private
26.2 structural source review. The 27,255-byte source-free original JSON
(SHA-256 `130070ea39c064d1de37fa0fa3b651b8799e650e066b176a2f419e3e5ff89fab`)
confirms 11 exact method body hashes. `doFill` has six nested loops with
direction hints ++, ++, --, --, ++, ++; the call ancestry strictly
matches the relative nesting of our bounded candidate X/Z/Y/Y/X/Z
probe. `swapSlices` is only inside the outer X-level loop and
`stopInterpolation` is outside; `initializeForFirstCellX` is before.
All 11 method observations have `unbraced_control_count=0`.

The next evidence PR,
`worldgen/262-noisechunk-structure-and-nonaffinity`, pins a compact
source-free 6,567-byte structural summary with exact original byte
hash/identities and regression tests. It also adds a **Rust negative
control** against the existing 768 authentic stock observations:
the full `finalDensity` output cannot be obtained simply by
trilinearly interpolating eight sampled final-output corner values.
This is **not** a compiled Rust density graph or Rust parity proof.

Important distinction: the structural packet proves braces/call nesting,
**not** source-semantically verified loop bounds and arguments, full
48-cell Y extent, NoiseChunk cache/wrapper state or parity at any
computed Rust finalDensity value. The earlier numerical captures
(16/128/512/768) and the two source-free packets are already complete;
do not ask the source owner to repeat them. All production/VAR/SEM,
canonical traversal and full-router parity flags remain false.

**Next work:** derive and independently verify the actual stock
`doFill` variable and loop-bound semantics, interpolation
`NoiseChunk` cache marker lifetimes, and the observed
world-seeded `finalDensity` DAG. Then implement the compiled
source-version-specific evaluator in the **existing**
`helve-world-gen` density program, with immutable graph and
caller-owned scratch; compare actual Rust-computed outputs against
frozen official JVM bits, not merely oracle replay. No new world
owner and no publication gate promotion.

The updated runbook is
`docs/execution/WORLDGEN_26_2_STOCK_NOISECHUNK_ADJACENT_FRONTIER_2026-10-20.md`.

## Compiled observed stock mixed-density leaf — next implemented Rust step

The first direct Rust compiler-path extension beyond the
source-evidence packets is `StockDensityNode262::ObservedMixed` in
`crates/world/helve-world-gen/src/stock_density_program_262.rs`.
This **reuses**, rather than forks or rewrites, the existing
`StockVanillaMixedDensity262` interpreter backed by genuine Minecraft
26.2 `DensityFunctions.add/mul` factory/delegate evidence.

- An immutable, bounded program can hold one observed stock
  noise/Y-primitive mixed delegate as a **prepared typed leaf**. Its
  scalar path directly computes seeded Rust noise and primitive math.
- If the mixed leaf is the whole program, the existing coherent
  16×16 plane and 16³ cell fast path is retained, with caller-owned
  outputs and no per-sample heap allocations or new world/registry.
- General explicit eager graph operations can also combine observed
  leaves; that *outer* arbitrary graph is NOT thereby qualified as a
  vanilla factory composition.
- The new Rust test computes every one of the **1,920 authentic frozen
  stock JVM** mixed-density words through this *compiled program*
  (four seeds × three registered keys × ten delegate profiles × sixteen
  coordinates), separately exercises original Ap2 positive-zero vs
  MulOrAdd signed-zero, and checks plane/volume/scalar consistency.

**Important scope:** This is a **true compiled Rust numerical path on
the observed mixed subgraph**, not the full source-owned `finalDensity`
NoiseRouter graph. Marker/cache, splines, range-choice, full Y-loop
semantics, and the source-owned bind of all router roots still need
exact original 26.2 review and independent numeric parity. It must not
open any production/canonical/VAR/SEM flags or instantiate another
world owner. Next: expand the compiled graph only with separately
source-reviewed/delegate-qualified node semantics, then compare actual
Rust whole-`finalDensity` to the already frozen 768 JVM outputs.

## Further compiled stock density progress — two-primitive observed leaf

After PR #473 merged at
`8838b89d38197085380eb80851b429c420df8fc4`, the same immutable
`StockDensityProgram262` now also supports
`StockDensityNode262::ObservedPrimitiveComposition`: a typed,
preconstructed `DensityComposition262` node backed by **1,280 genuine
26.2 JVM output vectors**. It is not a new evaluator and must never
be converted into generic eager multiply.

The new compiled regression runs **every one of those 1,280 source-free
original JVM words through actual Rust program evaluation**, rather than
just testing the standalone composition. It retains the `Ap2`
first-operand positive-zero early return vs `MulOrAdd` signed-zero
multiplication; in a one-node program it also uses exactly one
composition evaluation per output Y-plane, caller-owned 16×16 plane and
16³ cell buffers, and atomic coordinate-overflow rejection.

Both qualified primitive-composition and noise/primitive-mixed leaves
are compiled in the **existing** bounded immutable DAG. A generic
`Add` or `Multiply` node remains *explicit eager arithmetic*, **not**
automatic qualification of vanilla `DensityFunctions` or a router graph.
This is meaningful COLD compiler-substrate progress but still not the
full 26.2 `finalDensity`, cache/interpolation semantics, or R2D
production terrain. No source-law/VAR/SEM gate may change.

**Next:** resolve the exact 26.2 source laws of `RangeChoice` and
marker/interpolator wrappers (including per-cell state), and the
stock route to `finalDensity`; extend typed immutable graph nodes
only after source-law review and independently captured numeric
evidence. Keep all canonical/VAR/SEM/production gates **false**.


## Explicit demand-evaluated 26.2 Ap2 multiply in bounded Rust density DAG

After PR #474, the next source-observed graph-control step is
`StockDensityNode262::ExplicitAp2Multiply { left, right }` in the
**same** immutable 32-node `StockDensityProgram262`. This does not
introduce a second world or a new independently assumed router.

Unlike the older generic eager `Multiply` node, an explicitly selected
`Ap2` multiply first evaluates its left dependency and returns
**positive zero immediately** when the left result has exact `+0`
IEEE bits. Only when the left is not positive zero does it demand its
right subtree and multiply in the original operand order. COLD-validated
backward dependencies cap nesting at 32; one per-sample stack-backed
`[bool; N]` mask memoizes shared nodes and avoids heap allocation.
Skipped subtree scratch slots are deliberately left unchanged. Programs
without any explicit `Ap2` continue on the previous eager hot path.

The implementation is qualified only on **genuine, independently
observed JVM-selected `Ap2` examples**:

- **384** original stock mixed dynamic Noise/Y-gradient multiply words
  (profiles 2 and 3 of the frozen 1,920), across four world seeds and
  three registered noise keys;
- **160** original two-gradient multiply words (one frozen
  1,280-composition profile, across five seeds and 32 positions);
- explicit nested left-expression `+0` short-circuit, no right-subtree
  demand, reinitialised per-sample scratch and full 16×16/16³ scalar
  coherence including y=128.

**Critical:** `ExplicitAp2Multiply` is a *caller-chosen node type*.
The compiler must NOT infer Mojang's factory choice for arbitrary
children, map a stock `finalDensity` root to multiplication merely
because its Java class is `Ap2`, or treat pure memoization as the
stock `NoiseChunk` cache/interpolator lifetime. The observed
`finalDensity` root is `Ap2(Mapped, HolderHolder)`, but the operation,
mapped transform, holder target and their source laws require a
separate grounded review. No production/canonical/VAR/SEM/worldgen
permission changes. Next: inspect the exact root's operation and
`Mapped` transformation and resolve its bound holder before
instantiating a stock full-router graph. Reuse already-frozen JVM
numeric observations; never fabricate missing nodes or source laws.


## Narrow finalDensity root semantics frontier after PR #475

With the graph-level typed `ExplicitAp2Multiply` compiled in
merged PR #475 at `32dadd70b95a661b5ba9c1dd5cc5534eb4b95c87`,
**do not assume** the original stock finalDensity root is a multiply:
only its Java **runtime class** `DensityFunctions$Ap2` has been
observed. The original root has first-level `Mapped` and
`HolderHolder` children, but neither the bound
operator enum nor mapping enum nor concrete right-hand bound holder
was included in the earlier source-free root fixture.

In branch `worldgen/262-finaldensity-root-operator-review`,
new **actual stock JVM introspection** is implemented in:

- `tools/worldgen_java/HelveStockFinalDensityRootSemantics262.java`
- `tools/worldgen_26_2_stock_final_density_root_semantics.py`
- `tools/tests/test_worldgen_26_2_stock_final_density_root_semantics.py`

It checks exact source/JAR/lock identities, the prior frozen 128
original finalDensity outputs, and strict Java record accessors to
extract the real Ap2 operator, Mapped transform and input class,
HolderHolder public-bound concrete target, and 128 **new pairs**
of independently computed first-level child numeric words. The
tool always reports all source-law, VAR/SEM, canonical lifecycle,
router numeric-parity, and production gates **false**. It does not
capture more arbitrary points or rebuild the previous router graph.

A human must run it once against their exact pinned local 26.2
source/Atlas and JVM after its PR has merged, and upload its **source
free** JSON. The command is written in
`docs/execution/WORLDGEN_26_2_STOCK_NOISECHUNK_ADJACENT_FRONTIER_2026-10-20.md`.

**Next code:** use actual observed op/transform/target plus
source-owned review of their compute bodies to choose the
**correct typed graph operators**. Compile the reachable Mapped /
holder subgraphs on the same bounded Rust program only when their
laws and inputs have independent JVM parity; preserve the
NoiseChunk cell and marker lifecycle separately. Do not convert
the existing Ap2 multiply implementation into an unsupported
stock finalDensity root or open production generation yet.
