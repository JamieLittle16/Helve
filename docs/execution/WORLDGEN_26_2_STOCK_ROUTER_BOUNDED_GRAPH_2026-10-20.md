# Helve — stock Minecraft 26.2 bounded bound-graph frontier

**20 October 2026 — actual independent official bound roots received.**
Minecraft Java 26.2, protocol 776, DataVersion 4903. Structural evidence;
NOT a source-reviewed compiled vanilla graph or a generation admission.

## Original stock router evidence is now real, not guessed

The source-owning-machine report
`/tmp/helve-26_2-stock-router-roots-4.json` succeeded against the original
`VanillaRegistries` + stock Overworld `RandomState.router()` path, using
the four previously independent held-out world seed bitwords.

- **28,439 bytes, SHA-256**
  `81cc1fb15388998f9b812803ee96a30c792ef68df8120490b05f38acd3338736`.
- **60/60 ordered bound roots**, fifteen for each of four distinct seeds.
- All four inventories have identical field names, concrete root class,
  reached `compute` class, and immediate typed density children.
  This is structure agreement, *not* numerical seed-invariance.
- Exactly twelve typed immediate child edges *per seed*, 48 total.
- `NoiseRouter.mapAll` and `RandomState.router` indexed body SHA
  and original official source/JAR hashes match the locked evidence.
- **Root signature pinned** in
  `vanilla/reports/worldgen-26_2-stock-router-roots-15-observed.tsv`,
  **2,896 bytes, SHA-256**
  `27187403bfcccea13370f3d1d218a58d243a98c194684f71bc6f1c5fbe824dd1`.

The actual observed fifteen roots, in order, are:
`barrierNoise`, `fluidLevelFloodednessNoise`, `fluidLevelSpreadNoise`,
`lavaNoise`, `temperature`, `vegetation`, `continents`, `erosion`,
`depth`, `ridges`, `preliminarySurfaceLevel`, `finalDensity`,
`veinToggle`, `veinRidged`, `veinGap`.

Selected original edges:

- `temperature` and `vegetation`: real `ShiftedNoise` roots
  with `shiftX: HolderHolder`, `shiftY: Constant`,
  `shiftZ: HolderHolder`.
- `continents`, `erosion`, `depth`, `ridges`: `HolderHolder`
  roots, which are *opaque* in the existing first-level inventory.
- `preliminarySurfaceLevel`: `FindTopSurface`, with
  `density: MulOrAdd`, `upperBound: Clamp`.
- `finalDensity`: `Ap2`, with `argument1: Mapped`,
  `argument2: HolderHolder`.
- `veinToggle`: `Marker` → `RangeChoice`;
  `veinRidged`: `MulOrAdd` (`PureTransformer.compute`) →
  `Ap2`; `veinGap`: `Noise`.

These are actual *bound runtime object types*, not codec declarations
or old-version guesses. The original full source-free receipt is not
committed; its SHA and compact invariant summary are retained instead.

## The next bounded original-JVM graph inspection

The original `HelveStockNoiseRouterRoots262.java` now has a second,
separate `--router-graph-4` mode; original `--router-roots-4` mode
remains unchanged. The new mode still calls actual stock
`VanillaRegistries.createLookup`, `RandomState.create`, and
`RandomState.router()`. It does **not** reinterpret or reconstruct
Minecraft's graph. For each original seed it:

1. Demands the same fifteen real `NoiseRouter` record fields in their
   exact original order.
2. Uses an `IdentityHashMap` to record object identity **within that
   particular JVM graph**, sharing nodes rather than duplicating them.
3. Walks only declared record components assignable to
   `DensityFunction` with **depth strictly below 4**, at most 384 nodes,
   at most 32 components per node and at most 4096 density/opaque edges.
   A node at depth 4 is explicitly marked **uninspected**.
4. Records only **names and declared types** of non-density record
   components; critically it **does not invoke** holder, spline,
   parameter, enum or cache-related accessors. It cannot silently
   cross `HolderHolder` boundaries.
5. Checks original `compute(FunctionContext)` method declaring
   owners, just as the first capture did, without ever calling
   `compute` or producing numeric density values.
6. Emits ordered source-free `HEAD/ROOT/NODE/EDGE/OPAQUE/END` framed
   records with exact depth, IDs, and edge checksums, fail-closed
   on missing, duplicate or reordered frames.

The Python collector **requires the exact original 28,439-byte root
JSON** and source-free 2,896-byte fixture, rechecks both digests,
validates all 60 prior roots, and cross-checks every graph root and
its immediate child edges against the prior real JVM observations.
The archived source/JAR/Atlas fingerprints and two unreviewed router
method bodies are rechecked. It never includes proprietary source,
jar bytes or source code in its output.

### Source-owning execution

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_router_graph_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --roots /tmp/helve-26_2-stock-router-roots-4.json \
  --output /tmp/helve-26_2-stock-router-graph-depth4.json
```

The output path must not exist. Upload **only** the resulting source-free
graph JSON. If the official runtime rejects any method or field, supply
the tagged `JVM PHASE` error rather than guessing a class or allowing
arbitrary unsafe Java reflection.

### What this still does NOT prove

Even a green expanded graph is not a *complete* `NoiseRouter`.
`HolderHolder` delegates, nested registry references, spline
coefficients, cache/interpolation contracts, accurate Minecraft
`NoiseChunk` sampling context, and stock final-density values still
need separate original source-law review and numerical JVM captures.

After the graph report, identify the first opaque holder type and
its pinned source methods. Source-review its exact resolution semantics
before selectively extending the bounded graph beyond this boundary.
Only then acquire a real `finalDensity` JVM oracle and write a separately
named, output-qualified compiled Rust path, reusing existing bit-exact
world-seeded noise primitives and COLD worker scratch.

`world_seed_random_state_bound`,
`full_router_graph_qualified`,
`router_numeric_parity_qualified`,
`independent_var_sem_admitted` and
`production_worldgen_enabled` all remain **false**. No production
chunk publisher or extra dimension/world owner is introduced.
