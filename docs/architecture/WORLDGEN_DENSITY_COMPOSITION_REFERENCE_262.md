# Minecraft Java 26.2 — official composed-density capture frontier

**Status:** candidate collector and synthetic transport, **not an observed official composition oracle**. Exact 26.2 source/VAR/SEM, router semantics and production chunk publication all remain **closed**.

## Why this boundary

The official JVM has now supplied 640 pinned raw-bit outputs for `DensityFunctions.constant` and `DensityFunctions.yClampedGradient` (PR #431). Rust reproduces all 640, but the earlier `density_kernel_262.rs` operations `Add` and `Multiply` deliberately mean only **caller-chosen eager arithmetic**, *not* vanilla `DensityFunctions` composition. The next requirement is to test Minecraft's actual `DensityFunctions.add(DensityFunction,DensityFunction)` and `mul(DensityFunction,DensityFunction)` factories and their reached implementations.

The factory names and argument types are **candidate** signatures suggested by older public mappings. This collector requires the actual private 26.2 Atlas to bind each declaration exactly once with both body and normalized hashes, and official 26.2 runtime reflection to confirm the public static signatures and return types. Unknown/changed methods halt without creating an output. Even a successful factory capture does not independently source-review runtime delegate behavior, evaluate the full router, or qualify lazy/short-circuiting/cache semantics.

## Profiles and inputs

Eight composed graph objects are assembled using the four already observed primitive leaves:

| Profile | Official graph factory invocation |
| --- | --- |
| `add_gradients` | `add(worldHeightGradient, reverseGradient)` |
| `mul_gradients` | `mul(worldHeightGradient, reverseGradient)` |
| `add_zero_left` | `add(constant(-0.0), worldHeightGradient)` |
| `add_zero_right` | `add(worldHeightGradient, constant(-0.0))` |
| `mul_zero_left` | `mul(constant(-0.0), worldHeightGradient)` |
| `mul_zero_right` | `mul(worldHeightGradient, constant(-0.0))` |
| `add_self` | `add(worldHeightGradient, worldHeightGradient)` (same object twice) |
| `mul_half` | `mul(worldHeightGradient, constant(0.5))` |

The two gradients and two constants use the **exact parameter bits** from the previously captured primitive reference, not input conversions from JSON floats. For each profile, 5 existing **seed labels** × 32 signed integer block X/Y/Z positions produce **1280 exact IEEE-754 raw-bit observations**. These operations do not instantiate or verify any world-seed random state. The labels are used only to keep an identical test design and test expected seed-independence.

The standalone JVM transport first calls `SharedConstants.tryDetectVersion()`, then `Bootstrap.bootStrap()`, then constructs the four primitive leaves and eight composed functions by reflection. It calls official `DensityFunction.compute(SinglePointContext)`, serialises with `Double.doubleToRawLongBits` and never performs a local substitute for addition, multiplication, gradient evaluation or factory optimisation.

The source-free manifest records the exact input vectors, composition graph descriptions, 4 previously bound primitive-method fingerprints, 2 newly bound factory-method fingerprints, both pinned archive/runtime hashes, startup sequence, and strictly false admission flags. Output is outside the Git repository, atomically exclusive, mode 0600.

## Run on the source-owning machine

```bash
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_density_composition_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-density-composed-official-01.json
```

If it succeeds, upload **only** the source-free JSON; never the private source archive, Atlas database, original jar or class files. If a 26.2 signature fails, report the failure verbatim: do not patch to guessed name mappings. The local source-owning verification is essential because hosted CI **only** exercises independently authored toy Java implementations, corruption refusal, source-method binding structure and the reflective transport. CI cannot verify official density outputs.

## After an official result arrives

1. Revalidate every source-free manifest field, number and context; ensure exact official runtime/source hashes and six Atlas method identities. Retain all 1280 raw bits unchanged.
2. Identify the observed factory/compute semantics, checking operand order, signed zeros and any constant-folding/lazy behavior. An observed fast path at a chosen profile is not proof about every possible function.
3. Add **new versioned, typed integer-block-context composed density nodes** in Rust, reusing the immutable primitive leaves. Explicitly isolate any unqualified eager generic DAG. Test each output bit against the official manifest before calling parity.
4. Extend to noise-dependent density nodes, random-state/world-seed binding, interpolation, splines, actual router profiles, aquifers, surface and biomes. Reuse the existing semantic owner and section builder and keep production gates closed until the necessary independent source/VAR/SEM reviews.
5. Benchmark scalar and batch density, full cell build and semantic resident installation; shared CI timings are diagnostic only.

This is forward progress on the **evidence boundary** for real terrain, not yet a generated vanilla world.
