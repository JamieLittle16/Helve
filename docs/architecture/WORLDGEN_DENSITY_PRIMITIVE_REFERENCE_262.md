# Minecraft Java 26.2 — official density primitive reference capture

**Date:** 19 October 2026  
**Status:** standalone source-locked reflection transport and synthetic CI validation; **no real official density output capture is present yet**. **VAR/SEM is NOT admitted.** Production worldgen and R2C publication remain closed.

## First real density-function evidence target

Use `tools/worldgen_26_2_density_primitive_capture.py` with the actual privately pinned 26.2 official server archive, source ZIP and Atlas. Unlike the already qualified 320 raw `PerlinNoise`/`NormalNoise` **leaf** results, this captures actual output bits from `DensityFunction.compute(DensityFunction.FunctionContext)` on **integer block positions**. Its explicit primitive factories are `DensityFunctions.constant(double)` and `DensityFunctions.yClampedGradient(int,int,double,double)`, plus their nested Constant and YClampedGradient implementations. These signatures were suggested by mappings of older versions, **not asserted as true in 26.2**: the source-locked Atlas and reflective official runtime are required to independently accept every concrete method before any result can be used. Unknown names/arguments or missing method bodies fail closed; no silent fallback to older versions.

Profiles use these exact hexadecimal IEEE-754 double arguments:

- constant `-0.0` and constant `0.5`;
- gradient from Y -64 to 320, values -1.0 to 1.0;
- reversed gradient values 0.5 to -0.75 from Y -30 to 17.

Probe coordinates include -4096, -65, -64, -63, -30, -29, -1, 0, 1, 17, 18, 319, 320, 321, 1024 and other adversarial Y levels, with negative and large X/Z values. Five fixed direct 64-bit seed labels cover 32 integer coordinates each, per profile: **640 records**. The selected primitives should be seed-independent, but that is an *unverified expectation* until the real JVM confirms it. No floating-point conversion in the Python output path: Java `Double.doubleToRawLongBits` emits exactly 16 hex characters, preserved by the source-free JSON.

The official runtime requires startup before loading `DensityFunctions`: invoke `SharedConstants.tryDetectVersion()` **then** `Bootstrap.bootStrap()`. The standalone probe follows this sequence by reflection, matching the existing 26.2 `tools/official_state_data.py` source-owning block-state probe and its retained state-data manifest. The startup sequence is recorded and checked in the density manifest. This only establishes JVM registry initialisation; it does not prove density-function source semantics or relax any source/VAR/SEM gate. The synthetic JVM test deliberately throws on `DensityFunctions` class initialisation without that sequence.

The manifest binds pinned source archive SHA, server SHA, **four unique, nonempty Atlas method-body and normalized fingerprints**, integer coordinates, exact profile arguments, output bits, and closed gates. Method identities and synthetic Java transport do **not** review reached delegates and are not source/VAR/SEM proof. The runtime reflective bridge creates exactly the specified instances and calls their official `compute`; it neither reproduces nor copies their algorithms.

## Source-owning invocation

```bash
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_density_primitive_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-density-primitive-official-01.json
```

The pinned runtime is resolved via the existing resolver, or supplied with `--server-jar` and checked against the pinned SHA-256. Output is written exclusively to a fresh **private outside-repository** path with mode 0600. Upload only the source-free output JSON, never proprietary Java sources, class files or private database. Refusal on a target-version method mismatch is a useful source-review finding, not permission to patch with guesses.

CI runs independently authored fake Java density classes in a temporary directory to verify exact reflection signatures, signed-zero transport, record count and corruption refusal. **Those fake values are never official Minecraft samples.**

## What unlocks next

After a real official manifest is available and separately verified against the exact source/delegate bodies, add version-specific Rust `constant` and `yClampedGradient` typed nodes to the existing `DensityKernel262`, then compare every official 64-bit output. Expand to composition, noise-router resolution, spline/interpolation and aquifer nodes with separate source evidence. Full terrain generation must eventually use `SemanticDimensionInstance` and `GeneratedSectionBuilder`, never duplicate world ownership or publish unadmitted chunks. Cached COLD density-cell sampling must stay bit-exact; performance optimality requires controlled target-machine comparisons.

## Official source-free output received and frozen — 19 October 2026

The first pinned official 26.2 runtime capture **succeeded** on the source-owning machine following the corrected bootstrap procedure (PR #430). Its original source-free JSON has SHA-256:

`b1ee06e998b19ede5a283af2757e192dbb75fb6b761b55fa0d6a8a5f1e2297bc`

All **640 records** were transformed *without changing any observed value bits* into `crates/world/helve-world-gen/tests/data/density_primitive_26_2_rawbits.tsv` (TSV SHA-256 `c4733e68e08d3c7dd283af161ebd4efc5d0dd3e110142ee75c619c22d41d6c41`). The exact rows, profile labels, seed labels, block X/Y/Z integer contexts and raw-bit results are retained. Five seed labels produced identical values for corresponding profile/XYZ contexts; this is expected for these two primitives, but does **not** validate world-seed-to-density-router mappings.

The capture is bound to official source archive `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750` and runtime `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`, bootstrap sequence `SharedConstants.tryDetectVersion` then `Bootstrap.bootStrap`, and these 26.2 Atlas source method bodies:

| Selected method | Exact source body SHA-256 |
| --- | --- |
| `DensityFunctions.constant` | `1a3c5fd8ef141a6cd9bf8fe2b1475e267bb8f426e074f3636cb544a8e9d9aa37` |
| `DensityFunctions$Constant.compute` | `2d4dca61b23e524980e837ac3183e3edd2a497f42abcb88620ddad83b5b30b79` |
| `DensityFunctions.yClampedGradient` | `35213bdd109633d9be131dbe43fa5a5a20dd07ba35ab21291d6a51ebd36e8635` |
| `DensityFunctions$YClampedGradient.compute` | `e4ec69f8b92efb95bb0948e7fefa5ffc3d01ee9c360f94fdc3ff9693f4f52174` |

## Rust primitive calculation and hot-path design

`crates/world/helve-world-gen/src/density_primitives_262.rs` contains a version-labelled, immutable **integer-block-Y** primitive candidate, separate from the existing generic floating-coordinate density DAG. For the four observed profiles, `Constant` returns its exact original `f64` bit pattern (including `-0.0`), and `YClampedGradient` matches the ordered computation:

```text
progress = clamp((f64(blockY) - f64(fromY)) / (f64(toY) - f64(fromY)), 0, 1)
result   = fromValue + progress * (toValue - fromValue)
```

This specific order matches all captured gradient output bits; the algebraically equivalent `(1-t)*fromValue + t*toValue` differs on captured inputs. Never replace the division with reciprocal multiplication, fuse arithmetic or use the generic floating-Y graph as a substitute for the observed integer-block context.

The primitive caches constant differences in one immutable evaluator, computes per-position values without allocations or virtual dispatch, and can fill a 16×16 plane with one sample or 16³ Y/Z/X cell with just **16 Y evaluations** (caller-owned 4096-entry output). It rejects reversed/degenerate Y bounds, non-finite gradient endpoint/difference inputs, and overflowing cell origins rather than extrapolate unreviewed behavior.

`tests/density_primitives_262.rs` checks the **raw bits of all 640 official JVM observations**, full input order/positions, signed-zero and non-associative boundary cases, plane/cell coherence, and conservative construction/overflow rejection. These are independently observed **outputs** rather than expected values regenerated by the same Rust math.

**Gate remains closed:** Source body SHA bindings plus output differential evidence do not themselves amount to independent source algorithm/delegate review or general VAR/SEM admission; the full router, caches, splines, aquifers, biome resolution, surface rules and production semantic-chunk publication are still out of scope. Before integrating these primitives into full router evaluation, introduce a typed integer context for all relevant nodes (or establish an exact and source-reviewed conversion), source-review every reached delegate, and capture composed router values.
