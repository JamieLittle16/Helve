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
