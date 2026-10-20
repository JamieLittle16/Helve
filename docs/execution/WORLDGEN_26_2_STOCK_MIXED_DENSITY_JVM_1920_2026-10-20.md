# Helve — actual stock 26.2 world-seeded mixed density capture

**Date:** 20 October 2026. **Version:** Minecraft Java 26.2, protocol
776, DataVersion 4903.

## Why this capture is the next necessary gate

PR #453 verified **2,016/2,016 exact raw IEEE-754 output bits** for the
three registered stock noises against the original Minecraft JVM, including
**576 genuinely held-out** worldseed/coordinate samples.
PR #454 merged a bounded, immutable, fast 16³ program combining those leaves
with previously measured constant/Y-gradient density primitives, but its
ordered Add/Multiply nodes deliberately mean **eager IEEE arithmetic**.
They are not independently qualified vanilla mixed `DensityFunctions`.

The existing 1,280 two-primitive JVM results show **one real counterexample**
to blanket eager multiplication: the original `Ap2` two-gradient profile
returned **+0** when its dynamic left gradient evaluated to +0 at Y=128,
while IEEE multiplication with a negative right operand would produce -0.
Constant-factor multiplication retains distinct behaviour. A real stock
registered-noise + gradient/constant oracle is therefore required before
any 26.2 source-faithful mixed arithmetic fast path.

## Frozen acquisition shape

**Exactly 1,920** stock JVM evaluations:

- **10 original `DensityFunctions.add`/`mul` profiles:**
  `add_noise_gradient`, `add_gradient_noise`,
  `mul_noise_gradient`, `mul_gradient_noise`,
  `add_noise_negative_zero`, `add_negative_zero_noise`,
  `mul_noise_negative_zero`, `mul_negative_zero_noise`,
  `mul_noise_half`, `mul_half_noise`.
- **4 existing genuinely held-out world seeds:**
  `0x0123456789abcdef`, `0x7fffffffffffffff`,
  `0x8000000000000001`, `0xf0e1d2c3b4a59687`.
- **3 real registered stock noise keys:** TEMPERATURE, CONTINENTALNESS,
  EROSION, each resolved through the original `VanillaRegistries.createLookup`
  and `RandomState.getOrCreateNoise`, not custom holder parameters.
- **16 3D block contexts:** notably Y=127, 128 and 129 (zero-crossing
  and adjacent values), Y extrema, signed near-i32 bounds and ±2²⁵
  coordinate wrapping.
- **Only the previously observed scale pair** X/Z=0.25, Y=0.5.
  Exact primitive parameters: gradient `(-64,320,-1.0,+1.0)`,
  constant `-0.0` and constant `+0.5`.

Loop order **profile → world seed → key → XYZ**, one sequence-numbered
raw `f64::to_bits` value per record.

The additional original-JVM **actual implementation class, compute-declaring
class and superclass** are captured **once per profile** (10 source-free
records), without assuming the factory always returns the same delegate.
That matters because `Ap2`, `MulOrAdd` and other concrete return classes
can differ at runtime.

The new Java class `HelveStockMixedDensity262.java` compiles **together with**
the previously working `HelveWorldSeededDensity262.java` and directly
reuses its official bootstrap, typed registry and reflection helpers.
It uses the **real** `DensityFunctions.add/mul` factory and
`DensityFunction.compute(SinglePointContext)`; it does not copy source
algorithms, rewrite multiplication or calculate its own expected bits.
The original 1,440/576 JVM noise bridges remain unchanged.

Capture refuses changed private source archive or server JAR, changed
previous `RandomState`/stock lookup method identities, wrong original or
held-out source-free fixture pins, or an unfamiliar 26.2
`DensityFunctions.add/mul` factory body SHA. Primitive factory method
identities and all returned concrete compute delegates are included.
The original source files, JAR, Atlas and method bodies never enter the
repository or output file.

## One source-owning local run, after merge

From the existing checked-out Helve repo (the local folder may still be
`~/Crucible`):

```bash
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_mixed_density_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --output /tmp/helve-26_2-stock-mixed-density-1920.json
```

The output path must **not** preexist. The helper creates it exclusively
with permissions 0600 and prints a SHA-256 and a record count. Upload
**only the source-free JSON** and its printed SHA; never the private
Minecraft archive or JAR. If the official JVM or source method signature
refuses, report its tagged phase/error verbatim rather than guessing
the method contract.

## After an independently observed result

1. Verify entire original JSON SHA, source/method digests, concrete
   delegate identities and **1,920/1,920** raw-bit framing.
2. Check the exact differences against the PR #454 eager candidate, with
   focus on dynamic +0 versus constant -0, operation order, factory
   simplification and whether the first operand can skip the second.
3. Add a **separate typed 26.2 vanilla-operation plan** rather than
   changing `StockDensityProgram262` eager arithmetic semantics. Gate
   every single captured raw bit in both debug and optimized release.
4. After that, independently source-review the reached compute delegates
   and progress toward actual nested router and interpolation semantics.

**All open:** independent VAR/SEM source laws, complete NoiseRouter, caches,
interpolation, final density, terrain, biomes, production generation and
R2C publication. **All capture flags remain false**, including
`world_seed_random_state_bound`,
`independent_var_sem_admitted`, and
`production_worldgen_enabled`. A successful capture alone is **not**
a proof of Rust mixed-expression parity.
