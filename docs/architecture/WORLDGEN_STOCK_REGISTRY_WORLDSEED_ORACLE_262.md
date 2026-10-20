# Minecraft 26.2 — stock-registry world-seeded density oracle

**20 October 2026 · candidate numeric evidence path only · no VAR/SEM or production admission**

## Why this is a genuinely different oracle

The source-free exact **RandomState shape** observation (uploaded after #439)
has SHA-256 `1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7`
and confirms the pinned Minecraft 26.2 source/server SHA-256. It records
the actual public methods:
- `RandomState.create(HolderGetter.Provider, ResourceKey<NoiseGeneratorSettings>, long)`.
- `RandomState.getOrCreateNoise(ResourceKey<NoiseParameters>)`.
- `Noises.instantiate(HolderGetter<NoiseParameters>, PositionalRandomFactory, ResourceKey)`.
- `DensityFunction$NoiseHolder(Holder<NoiseParameters>, NormalNoise)` and
  `DensityFunctions$Noise(NoiseHolder, double, double)`.
- The three real `Noises` resource-key fields `TEMPERATURE`, `CONTINENTALNESS`, `EROSION`.
- The Overworld settings key and `Registries.NOISE` field.

We already have **480/480** raw-bit matches for the direct
`RandomSource.create(seed)` path. That does *not* mean the world seed is
converted using the same RNG factory. The new probe instead asks the
**official JVM** to run the actual world-seed-aware `RandomState` constructor
against a **real stock built-in `HolderGetter.Provider`**, and only then
samples the official `DensityFunctions$Noise.compute`.

## Construction and provenance

The original bridge at
`tools/worldgen_java/HelveWorldSeededDensity262.java` uses reflection
against the **pinned official 26.2 server runtime**; it contains no copied
Mojang implementation or decompiled bodies. The exact flow is:

1. `SharedConstants.tryDetectVersion()` and `Bootstrap.bootStrap()`.
2. Official `VanillaRegistries.createLookup()`, requiring a real
   `HolderLookup.Provider`; then `asGetterLookup()`.
3. Resolve the **real** `Registries.NOISE` via the official
   `HolderGetter.Provider` accessor and obtain a keyed `Holder.Reference`
   using `getOrThrow`. No `Holder.direct` substitute or fabricated
   `NoiseParameters` is accepted.
4. Call the **real** `RandomState.create(provider, NoiseGeneratorSettings.OVERWORLD,
   worldSeed)` and `getOrCreateNoise` for one of the three registered noise
   keys. Reuse each created state per world seed.
5. Create `NoiseHolder(holder, noise)` and `DensityFunctions$Noise`, and
   invoke the actual `compute(SinglePointContext)` method; retain raw
   IEEE-754 bits, including signed zeros.

Three XZ/Y scale profiles × five exact signed seed bit patterns × three real
noise keys × 32 integer XYZ contexts = **1,440 output records**. The collector
validates the prior source-free frontier SHA, exact five source-method
fingerprints including `Noises.instantiate`, plus the **new local
`VanillaRegistries.createLookup` Atlas body hash**, source archive SHA,
runtime jar SHA, transport ordering, vector values and strict admission flags.

The bridge fails closed if the official jar cannot load the built-in
registries, if `VanillaRegistries.createLookup` has changed shape, if the
provider is not a real stock registry holder, or if any key/constructor path
fails. Do **not** change to a fake `HolderGetter` to make the output pass.

A fake **independent test JVM** exists only in CI for reflection/signature,
manifest, stdout redirection and request framing validation. Hosted CI does
**not** contain private Minecraft runtime/source and does **not** prove the
numeric 1,440 official results.

## Local official run

The previous source-free frontier JSON must remain available at its
original `/tmp` path, or be supplied with `--frontier`:

```bash
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_world_seed_density_capture.py \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-world-seed-stock-registry-density-01.json
```

Upload **only** the generated source-free JSON, or the precise failure
diagnostic. Do not upload original Minecraft source, Atlas databases,
server jars, extracted Java class files or decompiled source bodies.

## Proof boundary and next implementation

A successful manifest sets `world_seed_random_state_observed:true` and
`stock_registry_used:true` (a **specific bounded JVM observation**), but
keeps `world_seed_random_state_bound:false`,
`independent_var_sem_admitted:false` and
`production_worldgen_enabled:false`. Official output parity does not
independently review all relevant source laws or prove the entire router.

After success, freeze all 1,440 genuine output bits, compare with Rust
and local source-review the exact `RandomState` seed factory and
`Noises.instantiate` parameter/registry binding. Build an immutable
registry-keyed per-world sampler owner with construction outside the
sampling loop; reuse existing exact-bit noise kernels and caller-owned
buffers. Extend later to `NoiseRouter.mapAll` caching and broad vanilla
surface/cave/biome/chunk parity. Keep the normal executable's worldgen
publication gate closed until separately qualified.


## First source-owning runtime failure and diagnostic correction

The first official local run on 20 October 2026 passed the source/frontier/server
preflight and reached the JVM, but exited nonzero before the 1,440-vector
manifest was written. The error printed several JOML `sun.misc.Unsafe`
terminal-deprecation **warnings** and only the beginning of
`Exception in thread "main"`: the Python collector incorrectly used
`run.stderr[:1600]`, hiding the actual exception and any deepest
`Caused by:` root. **Do not interpret the JOML warnings as the cause**, and
do not treat this as evidence for or against any world-seed math.

The collector now removes only the *pre-exception warning preface* in
fail-closed error reporting and preserves the Java exception and, for
oversized stacks, both its first frames and deepest cause. It still exits
with failure; it does not skip stock-registry checks or substitute manually
constructed holders. A toy subprocess regression test simulates JOML
warnings before `NoSuchMethodException` and nested reflection causes.

Rerun with an output filename that does not already exist, then report the
complete `OFFICIAL ... NOT QUALIFIED` exception. The next change should
address only the **actual observed method/registry failure**, not guess at
the error from the warning preface.


### Second source-owning diagnostic — clipped terminal stack

The immediate rerun of the original official JVM probe again exited nonzero.
The warning preface had been correctly removed, but the copied terminal
diagnostic contained only `Exception in thread "main"`; it did **not**
provide the Java exception type or a `Caused by` line. Consequently the
actual failing JVM method is **still unknown**. Do not guess, bypass,
or mark `RandomState` admitted.

The error formatter now places `JVM ROOT CAUSE: ...` on the **first terminal
line** and retains a bounded stack below it. If the Java stack includes a
nested `Caused by:`, the last/deepest one is promoted to that first line,
along with the top-level exception class. This is deliberately display-only:
the strict official registry, source SHA, vector and publication gates remain
unchanged.

A fallback diagnostic independent of terminal copy/paste is to redirect the
collector stderr into a temporary file outside the repo and inspect its
`JVM ROOT CAUSE`, `Exception in thread` and `Caused by` lines. No
private source, Minecraft jar or Atlas database should be uploaded.


### Official JVM uncaught-exception output is itself truncated

After #442 the user's captured stderr file contained exactly **two lines**:
`... JVM ROOT CAUSE: Exception in thread "main"` and
`Exception in thread "main"`. There was **no exception type, message or
stack trace** in the underlying subprocess stderr. This is therefore not
a Python formatting/terminal-copy issue; the official bootstrapped JVM has
not provided its normal uncaught exception stack to the collector.

The original Java probe now catches `Throwable` *inside the probe's main
entrypoint*, unwraps the deepest reflected `InvocationTargetException`
cause, tracks the bounded source-free phase (bootstrap, actual class lookup,
stock registry, seed-state creation, bound holder, or numeric compute),
and writes a **single tagged error** directly to `FileDescriptor.out`,
which the existing official runtime capture method has demonstrated is
available even when Minecraft replaces `System.out`.

The Python capture validates that exact one-row error protocol, refuses
malformed/duplicated error tags, and **always fails closed**. An original,
independently compiled toy JVM now exercises an exception thrown by
`VanillaRegistries.createLookup()` *after* bootstrap's stdout redirect and
confirms a phase and Java exception class survive end-to-end. This is
diagnostics, not independent registry/source/VAR/SEM or numeric admission.


### 20 October — qualified failure isolated to obsolete provider adapter

The source-owning JVM now reports the exact failure (not an inferred one):

```text
JVM PHASE: stock-registry-asGetterLookup | ROOT CAUSE: java.lang.NoSuchMethodException: net.minecraft.core.HolderLookup$Provider.asGetterLookup() | OUTER: java.lang.NoSuchMethodException
```

The preceding official `VanillaRegistries.createLookup()` call returned
successfully, but the bridge tried to use the **obsolete**
`HolderLookup.Provider.asGetterLookup()` API. In the modern provider
architecture `HolderLookup.Provider` extends `HolderGetter.Provider`
directly. The bridge now **validates this superinterface relationship
using `Class.isAssignableFrom` and verifies the real stock instance
implements it**, then passes *that same stock object* to the actual
`RandomState.create(HolderGetter.Provider, ResourceKey, long)` method.
This does **not** construct a new getter, copy a registry or synthesize
a holder; it eliminates only the legacy adapter. The official
subinterface relationship is still independently checked at runtime
and fails closed if the pinned 26.2 jar unexpectedly differs.

The independent toy JVM test has been updated to use the modern
superinterface rather than the wrong legacy `asGetterLookup()`
method; a negative test uses an intentionally unrelated provider
type and checks that the diagnostic rejects it. The rest of the
official bound noise constructor/oracle stays unchanged. This
corrects an **API shape failure**, but does not yet prove that
the remaining registry calls, actual world-seed values, or all
1,440 numeric results succeed in the source-owning official JVM.


## 20 October 2026 — first successful 1,440-vector official worldseed capture

The source-owning, pinned Minecraft Java 26.2 runtime successfully evaluated
stock-registry world-seeded RandomState.create(HolderGetter.Provider,
ResourceKey, long), getOrCreateNoise, and DensityFunctions$Noise.compute
over 32 signed XYZ contexts. The acquisition is not a predicted API shape.

Source-free original capture file SHA-256:
ee2135a89e196e482ea13eb374423cf14fb73a2c7f3e1e175dda1fbf785dced4

Additional pinned identities:
- Official server: cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5
- Source archive: 1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750
- Runtime binding frontier: 1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7
- Stock lookup method body: 63167b8b8e1f8ffd687a6577e61ab06c9e87ecb16457b9a65c67a8d8f07bf16d

The compact, checked-in source-free reference is
vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt.
It stores exactly 1,440 newline-separated lowercase raw double bit strings,
16 hex digits each; SHA-256:
79bf0251f2cf8bb7f4bfb226be0ba7912a7a574c6aaf8e8f5a9560dd2edfe414.
There are no Minecraft sources, jar contents, manually invented noise holders,
or hidden original registry parameters in the fixture.

The line index is fixed by the original input_rows() generator and iterates:
1. Profiles: unit, quarter_xz, quarter_xz_half_y, in this explicit order;
2. World seed patterns: zero, one, minus one, signed 64-bit minimum,
   and 0x9e3779b97f4a7c15;
3. Registered noise keys: TEMPERATURE, CONTINENTALNESS, EROSION;
4. The 32 original signed XYZ contexts, including large/wrapped coordinates.

CAUTION: JSON profile object keys are alphabetically sorted on serialization,
but the sample iteration order above follows the original Python insertion
order. Do not reorder the captured bit stream by JSON property order.

The new tools/worldgen_26_2_stock_worldseed_fixture.py validates:
- Frozen fixture byte length, SHA, bit encoding and finite values;
- Exact original capture SHA if passed --capture /path/to/original.json;
- Locked source and server identities, five pinned noise/seed method body
  hashes, stock lookup identity, exact row content/ordering, and closed gates.
Its regression and mutation tests run in the worldgen GitHub workflow.
No private source is needed in CI.

WHAT IS PROVEN: Authentic official stock-registry world-seeded noise outputs
were captured, immutable raw bits were retained, and provenance is pinned.

WHAT IS NOT YET PROVEN: A Rust world-seed/registered-noise derivation exists
and produces 1,440/1,440 matching bits. These are reference values, not Rust
parity results. Independent VAR/SEM source admission, NoiseRouter/terrain,
biome and surface rules, and production chunk/worldgen publication also
remain separate open obligations.

The source file itself correctly records world_seed_random_state_observed=true,
world_seed_random_state_bound=false, independent_var_sem_admitted=false,
and production_worldgen_enabled=false.


## Next implementation handoff (20 October 2026)

The official 1,440-vector source-free capture and fixture validator are merged
in PR #445, with all PR and post-merge main checks green. The next context
should **not** rebuild the oracle; proceed to source-grounded stock
registered-noise parameters, RandomState keyed seed/RNG construction and
exact Rust replay.

Canonical, detailed next-context work plan:
[World-seed to Rust parity handoff](../execution/WORLDGEN_26_2_STOCK_WORLDSEED_TO_RUST_PARITY_HANDOFF_2026-10-20.md).

Do not conflate observed official output with Rust worldseed parity, or
R2C/R2D pre-generated-world milestones with production terrain generation.
