# Minecraft Java 26.2 — density delegate and NoiseRouter source frontier

**20 October 2026. Source-locked discovery only; no source/VAR/SEM or production admission.**

## Current exact-bit baseline

PRs #429–#433 established source-locked official Java 26.2 outputs for 640 primitive and 1,280 composed density observations, alongside 480 raw-bit samples of improved/Perlin/Normal noise. One 26.2 edge is nontrivial: `DensityFunctions.mul(two gradients)` returns raw **positive zero** at Y=128 where ordinary `+0.0 * -0.75` returns negative zero. The generic eager DAG is intentionally **not** promoted to vanilla node semantics; the bounded two-primitive composition candidate has its own implementation.

## What was missing

The source-free composed JSON pinned the `DensityFunctions.add` and `mul` **factory methods**, but did not reveal **which runtime classes** they created, **which concrete or inherited compute methods** those classes reached, or **which exact classes and call sites** are on the router/noise-state path. Guessing older decompiled class names here risks falsely validating a shortcut or ignoring noise/caching/seed boundaries.

## Single source-owning-machine inspection

`tools/worldgen_26_2_density_delegate_frontier.py` obtains both sides of that seam:

1. **Actual official JVM reflection:** after the already qualified `SharedConstants.tryDetectVersion()` and `Bootstrap.bootStrap()` sequence, create the *same eight* composed density graphs as the successful official composition capture. Without evaluating or reproducing any private math, record their actual `Class.getName()`, the class declaring their public `compute(FunctionContext)` method, and the superclass. No bytecode or source is dumped.
2. **Pinned private Atlas:** require the exact 26.2 source archive, Atlas metadata and server jar hashes; recheck the already observed add/mul factory body fingerprints. Resolve every runtime class and reached compute method exactly. Enumerate the `DensityFunctions$...` class family, plus the `DensityFunction` and `DensityFunctions` roots and plausible `NoiseRouter`, `NoiseChunk`, `RandomState`, `NoiseSettings` and `NoiseRouterData` roots. Optional *name guesses* are reported as absent, **not silently resolved**. Concrete runtime delegate class identities and their compute source declarations **must exist**, exactly once, with an Atlas body fingerprint.
3. **Bounded delegate/source-free output:** for the resolved classes, retain exact source method identities, normalized/body SHA-256 where available, heuristic hazard classifications, syntactically resolved/unresolved call inventories, and explicit `reviewed: false`. Interfaces may have declarations without bodies; such null hashes remain marked and cannot pass as source-reviewed code.
4. **Closed gates:** JSON output is exclusively created outside the repository (mode 0600); machine-owned source, jar, class files, snippets, private DB and method bodies remain private. `source_text_included`, `independent_var_sem_admitted`, and `production_worldgen_enabled` are **false**.

This is an **implementation-target selection tool**. It does *not* establish a full dynamic call graph, close Atlas unresolved calls or independently verify vanilla router semantics. Java reflection reveals which method would be invoked, but not by itself every delegate called *inside* that method.

Run on the source-owning machine after merging the PR:

```bash
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_density_delegate_frontier.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-density-delegate-router-frontier-01.json
```

If the command succeeds, upload only the source-free JSON; otherwise provide the verbatim failure. The client-side tests use entirely original synthetic Java. GitHub Actions **cannot** prove the official JVM class results because the private locked runtime/source do not enter hosted CI.

## Next engineering step following the frontier

Use concrete `runtime_profiles`, `compute_declaring_class` and `atlas_frontier` to prioritise the **actual** reached add/mul compute delegates, their runtime shortcuts and relevant noise-holder/sampling contexts. Review source bodies locally against their recorded fingerprints and source/VAR/SEM hazards before generalising signed-zero behavior or building nested typed DAG nodes. Then select the narrowest true noise router leaf and capture official `DensityFunction.compute` with resolved seed/parameters and integer block coordinates, followed by bitwise Rust tests.

Implementation efficiency requirement: keep a single immutable compiled world/dimension sampler owner, share existing exact-bit `NormalNoise262`, retain caller-owned scratch for batched samples and do not build an NBT or packet representation on the hot path. Measure whole-cost chunk generation before declaring performance qualification.


### Official JVM output framing correction

A first source-owning run failed during `parse_runtime_output` with
`incorrect runtime profile order or shape: add_gradients`, **after** the
version/source/runtime checks. This is a collector transport failure, not a
new finding about density algebra. The exact unframed JVM stdout was not
recorded, so the specific interfering line has not been established.

The collector now emits an explicit `HELVE26_2_DENSITY_DELEGATE|` prefix and
pipe-delimited records for each of its eight profiles. Only fully tagged rows
participate in structural validation; unrelated JVM bootstrap logging is
ignored, while missing, extra, repeated, reordered or malformed tagged rows
fail closed. Output size and line count are bounded. The independent toy-JVM
tests exercise both clean output and interleaved startup log messages.

Re-run the same source-owning command after this change reaches `main`.
Neither admission nor official delegate inventory is claimed until that actual
probe succeeds.
