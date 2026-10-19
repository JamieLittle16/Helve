# Minecraft Java 26.2 — official composed-density capture frontier

**Status (updated 20 October 2026):** official 1,280-vector output capture completed; bounded Rust primitive-composition candidate implemented, with remaining independent source/delegate review and all production gates **closed**. The following earlier capture instructions describe the evidence-producing step; the result and its limits are recorded below.

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

## Official JVM result received — 20 October 2026

The **real pinned official 26.2 JVM capture completed** and the source-free JSON passed strict metadata, integer XYZ coordinate ordering, all five seed labels, eight frozen factory profiles and every record bit-string validation. The complete original JSON SHA-256 is:

`a303cc90269cf273cb5d65ed470fe118263468708c59897f89399e7fa1adff20` (259,512 bytes).

All **1,280 exact observed records** are frozen, unchanged, in `crates/world/helve-world-gen/tests/data/density_composed_26_2_rawbits.tsv` (the file includes all five seed labels, not just 256 distinct coordinate/profile combinations). The capture retains the pinned source archive SHA `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750` and official server SHA `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`, plus exact 26.2 Atlas factory body fingerprints:

| Factory | Pinned body SHA-256 |
| --- | --- |
| `DensityFunctions.add(DensityFunction,DensityFunction)` | `aff60df9dc11f0e52d061660cf39684dfd671e214ab185174a293ce96ddebe58` |
| `DensityFunctions.mul(DensityFunction,DensityFunction)` | `c5d5aaa53f8650d9068362c193487625eeeb057633eaafb0142651a4cc29d7f1` |

**Observed signed-zero distinction:** The naive two-primitive Java/Rust IEEE model exactly matches the complete **640 addition** vector set and **635/640 multiplication** vectors. The five multiplication mismatches all occur for `mul_gradients` at `blockY=128` (one occurrence for each seed label). There, the first gradient has `+0.0`, the second has `-0.75`, and the official composed density output is `+0.0` (raw `0x0000000000000000`), **not** the raw IEEE multiplication result `-0.0` (`0x8000000000000000`). By contrast, `mul_zero_left`/`mul_zero_right` with an explicit `-0.0` constant return signed zeros consistent with ordinary multiplication. These are actual discriminating official outputs; simply reusing the generic `Multiply` DAG would fail five tests.

### Source-free Rust implementation

`crates/world/helve-world-gen/src/density_composition_262.rs` implements an immutable **two-primitive** typed evaluator, using the already-validated `DensityPrimitive262` leaves:

- `add(left,right)`: ordered addition.
- `multiply(left,right)`: statically selects constant-factor multiplication (ordinary multiplication, preserving signed zero) versus two varying primitives. For two varying primitives, when the **first** sample is specifically `+0.0`, return positive zero; otherwise use ordered multiplication.
- A caller-owned 16×16 horizontal plane requires one Y evaluation; a 16³ Y/Z/X cell requires sixteen Y evaluations. No heap allocations, runtime registration, second chunk buffer/owner or virtual dispatch occur in the sampler. Overflowing Y origins fail before any write.

`tests/density_composition_262.rs` verifies **all 1280/1280 genuine official JVM raw bits**, coordinate/seed ordering, the signed-zero exception, all profile variants, full 4096-cell layout and overflow behavior. Crucially these are *source-free JVM output-qualified candidate semantics*, **not a proof of the true internal short-circuit condition**. In particular the dataset cannot prove whether the official code evaluates the second operand on an early-zero path, nor the behavior of `-0.0` as a **dynamic** first operand, arbitrary NaNs, general nested graphs, non-constant source delegation or alternate factory optimisations. The Rust shortcut is restricted to the observed `+0.0` path and to two nonconstant primitive leaves.

**Still closed:** independent source review of the actual reached 26.2 add/mul compute delegates and factory optimisations; general node semantics; noise-router graph binding and random-state world-seed resolution; caches, interpolation, splines, aquifers, biome/surface rules; source/VAR/SEM admission; and production chunk publication. Source body fingerprints identify the reviewed *factories* but do not independently certify their reached implementations. Do not present this as complete vanilla router parity, worldgen functionality, or a measured performance win.
