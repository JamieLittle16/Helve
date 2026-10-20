# Helve — stock Minecraft Java 26.2 NoiseRouter root-binding frontier

**20 October 2026. Minecraft Java 26.2, protocol 776, DataVersion 4903.**

## Why we do not immediately invent a "vanilla" router graph

The actual independently observed stack now includes 2,016 exact stock
world-seeded registered noise outputs and 1,920 exact mixed-density
add/multiply outputs. PR #456 also confirmed the distinct dynamic `Ap2`
and constant `MulOrAdd` paths, including seven positive-zero exceptions.

**None of that identifies the actual default Overworld router DAG.** The
26.2 `NoiseRouter` has 15 recorded root fields, but our source-free
evidence does not yet establish their full runtime values, graph node
identities, recursive children, noise settings, interpolation boundaries,
spline coefficients or caching contracts. There is no basis for silently
constructing a plausible legacy Minecraft router and calling it faithful.

## Actual stock, read-only bound-router probe

The new `tools/worldgen_26_2_stock_router_roots_capture.py` and
`tools/worldgen_java/HelveStockNoiseRouterRoots262.java` reuse the
already verified original source-free Java 26.2 reflection bootstrap.
They do **not** construct a guessed `NoiseRouter`.

1. Load the **real** official `VanillaRegistries.createLookup()`
   `HolderLookup.Provider`, demand its real
   `HolderGetter.Provider` relationship, and pass the pinned
   `NoiseGeneratorSettings.OVERWORLD` key.
2. For each of the four previously independent held-out signed world
   seeds, construct actual stock `RandomState.create(provider,key,seed)`,
   call the original **`RandomState.router()` method**, and require
   an instance of the actual `NoiseRouter` class.
3. Enumerate exactly **15 public Java record components** in their
   original order. Each component must have the declared exact type
   `DensityFunction`; capture its **name, bound object's concrete
   runtime type**, and the class actually declaring `compute`.
4. For each bound root, record just its **immediate** record components
   whose type implements `DensityFunction`: name and runtime child
   class, maximum 32. Other objects (holders, splines, caches, arrays)
   are **opaque**, not assumed absent or recursively traversed.
5. The original private Atlas independently checks a real
   `NoiseRouter.mapAll(Visitor)` method with exact already indexed body
   hash `61ea5c6e319640ee561342ceeb9833aaf9c832ce3aa296e27a2bc1f965a9897c`,
   plus the original `RandomState.router()` accessor source identity.
   These hashes are **indexed, not independently reviewed**.
6. The resulting JSON is outside the repository, exclusively created
   with permissions 0600. No machine-owned source, jar, registry
   contents, class bytes, samples, source bodies or database are
   copied; only structural names, metadata and method-body hashes.

The validated result must contain **60 stock-bound root occurrences**,
in original seed × router-record order, with consistent field names
across seeds. It records the original source and server digests,
original world-seeded 1,440 noise and 1,920 mixed JVM fixture pins,
and only closed production / VAR/SEM gates.

No values are sampled. The object returned by `RandomState.router()`
is source-grounded but its nested graph has **not** been reconstructed
or source-qualified. This is a true binding inventory, not yet a
complete router implementation.

## Run once on the machine owning the pinned source

The local repo folder may still be named `Crucible`.

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_router_roots_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --output /tmp/helve-26_2-stock-router-roots-4.json
```

Output must not already exist. Upload **only that source-free JSON**.
If reflection or Atlas refuses, provide the exact tagged
`JVM PHASE`/source method error; do not fabricate an alternative
getter, holder or router. The CI synthetic Java sample tests the
transport contract, **not** Mojang's actual router classes.

## Next work on returned evidence

- Verify all 60 root entries; freeze the authentic original JSON SHA
  and sorted source-free structure as a regression fixture.
- Select the exact concrete first-level root types (especially
  `finalDensity`, `initialDensityWithoutJaggedness`, climate fields).
- Extend the bound read-only graph inventory using independently
  reviewed delegate/record edge rules, *not* arbitrary object traversal
  or generic graph reordering.
- Capture bounded actual stock router leaf evaluations in the correct
  `DensityFunction.FunctionContext`, verifying where
  `SinglePointContext` is valid and where the genuine
  `NoiseChunk` interpolation context is required.
- Compile the now-grounded graph into immutable, owner-borrowed
  sampler state with caller-owned scratch; preserve the already
  qualified arithmetic semantics and measure performance at real
  per-chunk cost before declaring an optimization.

**All gates remain closed:**
`router_full_graph_qualified=false`,
`router_numeric_parity_qualified=false`,
`world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false`,
`production_worldgen_enabled=false`.
This patch does **not** connect generation to R2C publication or
create an extra world/dimension owner.

## Actual source-owning probe failure and strict repair — 20 October

The first official stock runtime capture genuinely reached
`router-field-0-10` before failing with a
`java.lang.IllegalAccessException`: the standalone Java probe could
not invoke a public generated record accessor whose declaring
implementation class was the package-private
`DensityFunctions$FindTopSurface`.

**This is an access-control / reflection transport problem, not a
finding about the correct shape or numeric meaning of the router.**
No complete four-seed inventory was produced or admitted by that run.

The fixed probe checks `canAccess(target)` and, only for already
type-checked `NoiseRouter` components and immediate typed
`DensityFunction` record children, invokes
`trySetAccessible()` on that exact `Method`. A denied request
still fails closed with a tagged JVM phase; it does **not** set
global module openness, use JVM `--add-opens` flags, recurse into
opaque objects, or bypass expected record types.

The synthetic JVM CI now includes a **package-private record at
router field 10 with a typed density child** to reproduce the
previously missing access case. Re-run the same pinned capture
command above after the fix merges, with the same output path if
the failed run did not create it. The capture only writes output
after fully validating all four seeds.
