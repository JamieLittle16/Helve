# Helve — first genuine stock 26.2 bound final-density numeric oracle

**20 October 2026.** Minecraft Java 26.2 · protocol 776 · DataVersion
4903. Source-free real original JVM observations, **not** compiled vanilla
graph equivalence, full chunk interpolation or production worldgen authority.

## New original stock evidence: all HolderHolder binding targets known

The user ran the real source-owning four-seed `HolderHolder.function ->
Holder.value()` collector from PR #460. The actual
`helve-26_2-stock-router-bound-holders-4.json` is **15,260 bytes**,
SHA-256:
`1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64`.

For each of the four previously independent world seeds, all **eight**
bound `HolderHolder` positions have exactly the same class and type
signature, and use the real `net.minecraft.core.Holder$Direct`:

| Original graph node | Connected root/path | Bound `DensityFunctions$` class |
| --- | --- | --- |
| 6 | `continents` | `Marker` |
| 7 | `erosion` | `Marker` |
| 8 | `depth` | `Ap2` |
| 9 | `ridges` | `Marker` |
| 15 | `temperature/vegetation.shiftX` | `Marker` |
| 17 | `temperature/vegetation.shiftZ` | `Marker` |
| 21 | `finalDensity.argument2` | `RangeChoice` |
| 27 | `veinToggle.RangeChoice.input` | `YClampedGradient` |

**These are runtime class observations only**. `HolderHolder.compute`
was only indexed, not independently source-reviewed; no actual density
value has been qualified by the prior holder probe. The four seed
inventories were structurally identical; their numerical values and
underlying sampled noise are not thereby seed-independent.

## Actual finalDensity scalar sampling instead of a guessed graph

The new `tools/worldgen_java/HelveStockFinalDensitySinglePoint262.java`
builds the original stock `VanillaRegistries.createLookup()` provider,
requires the genuine `HolderGetter.Provider` subtype relationship,
creates `RandomState.create(provider, OVERWORLD, worldSeed)` using
each one of the four previously held-out signed seeds, and gets the
actual bound `NoiseRouter.finalDensity` record field (index 11).
For every seed, the probe checks the already independently observed:

- actual root concrete type `DensityFunctions$Ap2`;
- `argument1` concrete type `DensityFunctions$Mapped`;
- `argument2` concrete type `DensityFunctions$HolderHolder`.

It then invokes the actual public `DensityFunction.compute` interface
on the *real bound stock final-density node* with a new original
`DensityFunction.SinglePointContext(x,y,z)` for each of 32 explicit
coordinates. The resulting 128 **raw IEEE-754 64-bit outputs** are
serialized as 16 lowercase hexadecimal digits, retaining negative
zero. Java failure phases are tagged and fail-closed; nonfinite results
are refused.

These points include the Overworld vertical limits, neighbouring
Y-values, positive and negative coordinates, 16-block chunk edges,
and larger stress coordinates. Input order, seed count, and every
point are source-free and fixed in the collector.

### What this proves and what it does not

This is the first prospective **actual bound finalDensity numerical
oracle**; its numerical values still require a successful source-owning
JVM capture. A passed synthetic CI fixture proves our transport and
schema contract, **not** Mojang's final-density numbers.

An authentic `SinglePointContext` point computation is **not** the
same as the `NoiseChunk` evaluation used during actual terrain
generation. We have NOT certified cache/interpolation markers, aquifer
path, surface/noise settings, terrain block choice, biome sampling,
actual density-grid or stock chunk parity. We do not assert that the
early standalone numerical results are equal to the chunk-context
results. All VAR/SEM and production gates remain **false**.

The collector requires exact byte SHA-256 checks on the three real,
independent, user-owned receipts:

1. Fifteen root fields × four seeds: **28,439 bytes**, SHA
   `81cc1fb15388998f9b812803ee96a30c792ef68df8120490b05f38acd3338736`.
2. Depth-four graph × four seeds: **141,287 bytes**, SHA
   `5911470e36725da99e7b82b5b8b4eef03a1d150662aa44c71b6c64340e4a46fb`.
3. Holder bindings × four seeds: **15,260 bytes**, SHA
   `1b7e991f619094c4219138393edad0b5abdb22595dc1d4390a0617ab8de1ac64`.

It also reruns pinned original 26.2 source/JAR and private Atlas source
identity checks, including indexed `DensityFunctions$Ap2.compute`
method body SHA (`reviewed: false`). No original source or JAR,
registry payloads, Atlas DB or JVM objects are exposed in the output.
The JSON file is exclusively created with permissions 0600 outside the
repository. CI uses an **independently compiled toy Java registry and
record types**, including a package-private `HolderHolder`, to verify
reflection/transport. It is not substituted for an official capture.

## Source-owning command, after CI-green merge

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_final_density_singlepoint_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --roots /tmp/helve-26_2-stock-router-roots-4.json \
  --graph /tmp/helve-26_2-stock-router-graph-depth4.json \
  --holders /tmp/helve-26_2-stock-router-bound-holders-4.json \
  --output /tmp/helve-26_2-stock-final-density-singlepoint-128.json
```

The output path must **not** exist. Upload only the final source-free
JSON, or paste the full tagged `JVM PHASE` error so the exact official
runtime constraint can be addressed without guessing a Minecraft
implementation.

## Next steps after authentic values

1. Freeze numerical raw-bit observations only after source-owning
   capture; discriminate negative zero, NaNs and boundary positions.
2. Independently source-review the exact `Ap2`, `Mapped`,
   `RangeChoice`, `Marker`, holder and noise delegates actually
   encountered; do not call a source hash a proof of evaluation law.
3. Build a **separate** stock `NoiseChunk`-correct reference capture
   for interpolated grid samples with the real `NoiseChunk` scope,
   cache lifecycle and settings. Compare it to standalone points, but
   do not silently treat them as interchangeable.
4. Compile and cache only the independently qualified shape/laws in
   Rust, reusing Helve's existing server-lifetime world and SIMD/plane/
   16³ scratch as appropriate, without a second sampler or ownership
   model. Benchmark once correctness is qualified.

CLOSED: `world_seed_random_state_bound`,
`router_numeric_parity_qualified`, `full_router_graph_qualified`,
`stock_noisechunk_interpolation_observed`,
`independent_var_sem_admitted`, `production_worldgen_enabled`.


## Update: original 128 numeric values received and frozen (20 October 2026)

The source-owning-machine command above now **succeeded**; the first
`finalDensity.compute(SinglePointContext)` reference is no longer
prospective or synthetic:

- Official original `/tmp/helve-26_2-stock-final-density-singlepoint-128.json`:
  **25,704 bytes**; SHA-256
  `0c294020fb2ad882f6ed88e5759e032c6955d48be3cfef1a19a089f561bb059d`.
- **128/128** ordered genuine numeric results, four distinct world-seed bitwords
  × 32 prescribed signed-coordinate locations.
- Every returned value is a finite raw IEEE-754 `f64`, including the
  full value/significant bits rather than a formatted/rounded decimal.
- 97 distinct raw bitwords across all 128 results; 18 equal
  `bfdd555555555555` (the observed value -0.4583333333333333).
  The four Y=-64 samples all have `3fa330e560418937`; the four
  Y=320 samples all have `bf99983c131d5acc`. **Only these tested
  coordinates are claimed**; these coincidences do not establish a
  global clamping or interpolation formula.
- Source-free, original-order 128-word fixture:
  `vanilla/reports/worldgen-26_2-stock-final-density-singlepoint-128-bits.txt`,
  **2,176 bytes**; SHA-256
  `058846dd4c755802ffe43f829b109884331962712ac7556f4d5cb4320a597e4f`.
  The private full original JSON is **not committed**.
- Exact method body hashes (all `reviewed: false`): official
  `DensityFunctions$Ap2.compute` SHA
  `54d44e99cae188665438eda580ab0a76204c0c486b80edb603f32fa4375b3e48`;
  `DensityFunctions$HolderHolder.compute` SHA
  `766c33ffa1e2b33e38704aff1091b8abcf90e88365d12fbd274edfb70f1082aa`;
  previous `RandomState.router` and `NoiseRouter.mapAll` pins unchanged.

`tools/worldgen_26_2_stock_final_density_singlepoint_fixture.py` independently
requires the exact 2,176-byte fixture SHA and finite/raw-bit records.
If asked to validate the source-owning receipt, it demands the exact
original 25,704-byte JSON SHA, exact 26.2 archive/JAR/three-prior-receipt
hashes, exact coordinate/seed order and all four indexed source-method
signatures, their original body + normalized hashes and their
`reviewed:false` status. No earlier admission gate can be set true.
Standalone fixture verification needs no private JVM, archive or Atlas.

```bash
cd ~/Crucible
python3 tools/worldgen_26_2_stock_final_density_singlepoint_fixture.py

# Additional source-owning receipt authentication (optional):
python3 tools/worldgen_26_2_stock_final_density_singlepoint_fixture.py \
  --capture /tmp/helve-26_2-stock-final-density-singlepoint-128.json
```

### Stop repeated shape discovery; move to chunk-accurate numeric parity

The central next milestone is **a real `NoiseChunk`-scoped
`finalDensity` value sample on the actual chunk interpolation lattice**,
not a speculative port and not a new shallow graph-fingerprint capture.

Before emitting any stock `NoiseChunk` numeric vectors, source-review
the exact 26.2 `NoiseChunk` factory/constructor, settings/grid dimensions,
random-state router wrapping/visitor, interpolator fill/start/swap/update
order, cache and vertical slice lifetime, and the precise sampling
callback. Record source method body hashes and reviewed conclusions;
only call stock numerical APIs with these verified contracts.

The comparison basis is now permanent: this immutable
`SinglePointContext` oracle **cannot be silently relabelled as**
`NoiseChunk` values. A new oracle must declare its actual context
and explicitly state when the stock function is cache-sensitive and
the two sampling paths legitimately differ.

For any subsequent Rust compiled graph, use one owned, typed
`NoiseRouter`-data programme attached to Helve's existing server
world owner; no allocations in the per-block hot path and no
per-coordinate registry lookups. Combine stage-level density arrays
with qualified 16×16 planes and 16³ scratch where legal, deduplicate
seeded NoiseHolder resolution once per state and benchmark whole-cost
chunks, not only scalar microbenchmarks.

**All gates remain closed**:
`world_seed_random_state_bound=false`,
`full_router_graph_qualified=false`,
`router_numeric_parity_qualified=false`,
`stock_noisechunk_interpolation_observed=false`,
`independent_var_sem_admitted=false`,
`production_worldgen_enabled=false`.

## First source-confirmed stock finalDensity operator and compiled Rust candidate

The owner independently ran the **original stock Minecraft Java 26.2**
root+children diagnostic introduced by merged PR #476 and repaired in
PR #477. The exact **source-free** private receipt has SHA-256
`2c8094e2c561f13aff9a392081bf0f7c3fa41b94f1c8d3d922c308269db78e8d`
(38,630 bytes) and is **not** committed to the repository.

Across the same four seeds × 32 original SinglePointContext XYZ frames,
the actual bound Overworld `finalDensity` is:

```text
Ap2(type = MIN; observed bounds -0.4583333333333333 .. +0.4583333333333333)
  argument1 = Mapped(type = SQUEEZE, input = Marker)
  argument2 = HolderHolder(holder.value() = RangeChoice)
```

This identity follows real `VanillaRegistries`, original
`RandomState.create` and `NoiseRouter.finalDensity` reflection, with
the inherited `PureTransformer.compute` declared class and source body
pinned. All **128 original root values** match the earlier independent
frozen `SinglePointContext` oracle exactly. A **separate** pair of
original stock child operand words was obtained for each of the same
128 coordinates.

Among these 128 observations, the left Mapped child is the smaller
operand **124** times, and the right RangeChoice holder **four**
times (zero-indexed rows 21, 66, 67, 87). The root is MIN, **not**
MUL, and neither child may be unconditionally removed. Crucially this
measurement is **not** a source-law proof for NaNs, signed zeros,
short-circuiting, mapping math, interpolation, or cache lifetime.

The compact original-JVM operand/output record now lives in
`crates/world/helve-world-gen/tests/data/stock_finaldensity_min_root_128_rawbits.tsv`.
Its **6,528 bytes** are pinned to SHA-256
`5693d6d923ccd3fd29847350c825556349ba1f5eb1a5a7671537d8328ac485fd`
by `tools/worldgen_26_2_stock_finaldensity_min_root_fixture.py`,
which also requires all 128 root result words to match the **earlier
independent** frozen stock fixture. The exact original 38,630-byte
source-free owner JSON can optionally be checked locally with
`--capture /path/to/helve-26_2-final-root-semantics-128.json`.

The real Rust compiler extension
`StockDensityNode262::ExplicitAp2Min { left, right }` combines two
finite independently evaluated density results in the **same**
immutable, caller-owned `StockDensityProgram262` DAG. It is a
typed operator **candidate**, not the full source-bound graph.
The new Rust tests reconstruct these 128 original root results from
their frozen independent JVM **first-level operand words** and check
the full 16×16 / 16³ sampling logic as well as nesting with lazy Ap2
multiplication. **It does not recompute either stock Mapped or
RangeChoice subtree in Rust.** Only those original child values are
injected for root-operator parity. Do not mislabel this end-to-end
Rust-versus-JVM `finalDensity` parity.

**Next after this PR:** implement and source-review the exact
`SQUEEZE`-mapped Marker input and bound `RangeChoice` subtree, with
true Rust evaluations against **independent JVM child outputs** and
explicit `NoiseChunk` cache/interpolation lifecycle. Full router,
VAR/SEM, canonical traversal and production worldgen flags remain
**false**; no second world owner and no old captures need repeating.


## Inner graph implementation and genuinely new stock input frontier

After merged PR #478 at `10915192613ccf8298658547a36a5622f60a0b07`, the 26.2
finalDensity first-level root is correctly observed to be
`Ap2 MIN(Mapped SQUEEZE(Marker), HolderHolder(RangeChoice))`.
The existing compact 128-row fixture pins **real original stock JVM**
Mapped and holder output words. It does **not** contain the Marker input
to SQUEEZE, the RangeChoice selector or its two branch results.

The next compiler increment, in
`crates/world/helve-world-gen/src/stock_density_program_262.rs`,
adds **`StockDensityNode262::CandidateSqueeze { input }`** as
a typed unary node in the existing immutable bounded Rust graph.
Its implementation is the *candidate* Java-order expression

```text
c = clamp(input, -1.0, +1.0)
result = c / 2.0 - c * c * c / 24.0
```

with original left-to-right multiplication order and no per-sample
allocation. The COLD constructor checks one strict backward edge and
rejects disconnected nodes. The candidate works both in ordinary
eager graph sampling and beneath the existing demand-evaluated Ap2
multiplication; coherent planes and volumes reuse the caller's
existing buffers. **This is not yet original-JVM-qualified
SQUEEZE**: the original Marker *input* was not part of the 128
first-level child receipt, and the actual Mapped apply source branch
has not undergone manual source-law review. Never promote any VAR/SEM
or production gate on the basis of those candidate tests.

### One new input capture, without repeating past work

The new read-only original Java 26.2 diagnostic is
`tools/worldgen_26_2_stock_final_density_inner_semantics.py`,
with bridge
`tools/worldgen_java/HelveStockFinalDensityInnerSemantics262.java`.

It reuses the exact already-frozen four seeds × 32 world coordinates;
there are **no additional old finalDensity root values to capture**.
For each original seeded stock `RandomState`, it unwraps:

- `Mapped(SQUEEZE)`'s real `Marker` input, the
  marker's original type and its one directly wrapped density input;
- the `RangeChoice` target behind the existing
  `HolderHolder`, its real selector, two branch types,
  and exact inclusive/exclusive double thresholds;
- raw IEEE-754 bits from both new original paths — Marker value,
  wrapped value, selector value, whenInRange value, whenOutOfRange
  value — plus two **comparison-only** previously captured Mapped and
  holder outputs.

The Python validator requires the two old output words at all 128
points to match **exactly** the independent 6,528-byte PR #478
fixture; the holder must agree with an actually computed branch,
but this observation alone does not establish the source branch
predicate (including boundary handling), ordering, or NoiseChunk
cache lifetimes. It also re-verifies the exact stock source archive,
Atlas fingerprints, version lock and official server JAR. The private
source-free output is deliberately not committed; all admission flags
remain **false**.

Once this PR is merged, run **only this new inner review**, without
repeating the earlier root/512/768/noise captures:

```bash
cd ~/Crucible
git switch main && git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_inner_semantics.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-final-inner-marker-rangechoice-128.json
```

Upload only the source-free JSON, or the specific fail-closed error.
With those **new** original Marker-input/Mapped-output pairs, test the
Rust SQUEEZE candidate against all 128 independent JVM words and
separately inspect source-law operation order. With the RangeChoice
selector and both branch words, implement a typed Rust RangeChoice
operator with independently verified boundary and branch semantics.
Then expand recursively to the actual underlying noise and spline
graph, followed by separate NoiseChunk/interpolator and 768/512
original-cell parity. Do not instantiate a production terrain
publisher until the documented gates are satisfied.


### First private inner-review run: marker enum transport correction

The first source-owning local run following PR #479 reached the Java
diagnostic and then failed inside the Python *parser* with
`unqualified original marker/range classes`. Its Python enum grammar
incorrectly required uppercase underscore-separated names, although
the original Java `Marker$Type` enum may use conventional
UpperCamelCase identifiers (such as `CacheAllInCell`).

The repaired parser now accepts only short ASCII Java-style identifiers
while requiring the **exact** declaring class
`net.minecraft.world.level.levelgen.DensityFunctions$Marker$Type`,
safe bounded qualified names for wrapped/selector/branch classes,
and finite IEEE-754 threshold words. Errors now distinguish an altered
enum declaring class, malformed enum name, invalid runtime class or
invalid numeric threshold. CI tests simulate CamelCase constants and
reject malformed names and class substitutions.

This is **a reviewer transport correction**, not a source-law
admission. The first run produced **no** source-free inner JSON; no new
Marker/RangeChoice numerical evidence has yet been committed or
validated. Rerun only this same **new** inner review after its fix is
merged. The prior 128 first-level, 512 cell and 768 NoiseChunk oracle
records remain frozen and require no recapture.


## Verified deeper 26.2 inner graph — 128 original JVM pairs

The previously requested *new* inner source-owning diagnostic succeeded
after PR #480 fixed the exact Java Marker enum grammar. The user-supplied,
source-free report is **67,785 bytes**, SHA-256
`22c8473fa1cc409f9833731306a1d35cb633808c6571ea75fbb84a45150c56b1`;
no Minecraft Java source, JAR or registry state is committed. The
four-seed × 32 original `SinglePointContext` XYZ inputs are unchanged,
and all **128 Mapped and holder output words match** the previously
frozen PR #478 first-level fixture.

The real 26.2 Overworld graph has the following *now independently
observed* deeper nodes across all four seeds:

```text
finalDensity = Ap2 MIN
├── Mapped SQUEEZE
│   └── Marker(type = Interpolated)
│       └── MulOrAdd [actual wrapped original runtime class]
└── HolderHolder -> RangeChoice
    ├── input: Marker
    ├── minInclusive: -1000000.0 (0xc12e848000000000)
    ├── maxExclusive: 0.0 (0x0000000000000000)
    ├── whenInRange: Constant(64.0)
    └── whenOutOfRange: Ap2
```

The **new numeric input/output evidence** confirms:
- the existing Rust `CandidateSqueeze`'s clamped ordered polynomial
  matches **128/128 original JVM Mapped outputs bit-for-bit** when given
  the real Marker input; values include magnitudes beyond one;
- in stock `SinglePointContext`, the `Interpolated` Marker output
  equals the wrapped `MulOrAdd` value at all 128 recorded inputs;
  **this does not establish how NoiseChunk interpolation works**;
- the observed predicate `selector >= -1000000.0 && selector < 0.0`
  selects the exact original holder branch in **128/128** cases:
  **47 in-range** and **81 out-of-range**;
- the in-range original branch yields exactly `64.0` at all 128
  points. The outer `Ap2` branch remains an **unimplemented
  underlying subgraph**. Four original root points favour the holder.

The compact, source-free and independently testable fixture is
`crates/world/helve-world-gen/tests/data/stock_finaldensity_inner_128_rawbits.tsv`:
**15,232 bytes**, SHA-256
`967c9203950f0e22a8b69f73dfe5e1bd1438ef1224fcc4346b8d578409c45170`.
The tool
`tools/worldgen_26_2_stock_finaldensity_inner_fixture.py` checks
all 128 new operand tuples, historical first-level and root output
SHA pins, the exact 47/81 and four holder-winner counts, formula raw
bits, stock constant, range decision, and optionally the original
private user receipt with `--capture /path/to/helve-26_2-final-inner-marker-rangechoice-128.json`.
No future duplicate capture of these facts is warranted.

### Rust implementation scope

The bounded compiled `StockDensityProgram262` now has
`CandidateRangeChoice { selector, when_in_range, when_out_of_range,
min_inclusive, max_exclusive }`. The COLD constructor requires
finite strictly ascending bounds and backward-reachable dependencies.
The existing fixed scratch/demand evaluator computes the selector,
then **only the chosen branch** — no eager evaluation of the unused
RangeChoice subtree, heap work, or second world owner. The already
implemented candidate SQUEEZE remains the **same** ordered arithmetic
validated by the stock marker/mapped words. Rust tests reconstruct all
128 original first-level and MIN-root words using the real Marker
input, range selector, and two **stock-JVM-provided** range alternative
values. The marker's nested `MulOrAdd`, the out-of-range `Ap2` and
RangeChoice selector's true density graphs **are not computed from
original seeded noise in Rust yet**. This is **operator+partial
composition parity, not full end-to-end finalDensity parity**.

The code is still a source-law **candidate** until original 26.2
SQUEEZE and RangeChoice methods' exact branch/FP details are
independently reviewed. Numerical observations do not qualify NaN,
signed-zero, range boundary or full stateful `NoiseChunk` context.
The existing 768 NoiseChunk and 512 cell records remain frozen;
the full-router, VAR/SEM, cache/interpolation and production worldgen
admission gates stay **false**.

**Next:** source-review exact `Mapped` transform / `RangeChoice.compute`,
then recursively bind the selector Marker, `MulOrAdd`, and out-of-range
`Ap2` via the existing typed compiler and observed seeded noise
primitives. Finally implement the genuine NoiseChunk cache/interpolation
lifecycle and match the 768 adjacent JVM words, without a second
semantic world owner.


## Next original 26.2 finalDensity subgraph: fused MulOrAdd and second-layer witnesses

The 128-row inner JVM receipt has already established
`Mapped SQUEEZE(Marker(Interpolated, MulOrAdd))` and
`RangeChoice(input=Marker, bounds=[-1000000,0), in=Constant(64),
out=Ap2)`, and the stock SQUEEZE transform matches 128 raw-bit
input/output pairs. This does **not** reveal the MulOrAdd operand and
constant, the range selector's wrapped density, or the outer Ap2's
operation and its two operands.

The new `StockDensityNode262::CandidateMulOrAdd { input, argument,
operation }` implements caller-**explicit**, fused constant addition
or ordinary IEEE multiplication in the **same** fixed-bounded density
DAG. Unlike an Ap2 multiply, it does not skip positive zero. Its cold
graph constructor rejects forward/unused nodes and nonfinite
arguments, while allowing signed zero. Both eager and memoized-demand
sampling paths reuse the existing caller-owned scratch; no additional
world owner, heap allocation or per-block virtual dispatch.

This operator is independently tested against **1,152 real official
Minecraft 26.2 stock mixed-noise/constant delegate raw-bit outputs**
from the earlier 1,920-word frozen JVM fixture, across four seeds,
three registered noise types and sixteen XYZ contexts for six
constant profiles. It is **not** asserted to be the actual original
MulOrAdd root instance until the operation, parameter and real
subgraph input are separately observed and bound.

### Exactly one new semantic witness, no old recapture

New source-free reviewer:
`tools/worldgen_26_2_stock_final_density_second_layer.py`,
with reflection bridge
`tools/worldgen_java/HelveStockFinalDensitySecondLayer262.java`.

The bridge follows the **actual** pinned original Minecraft Java 26.2
VanillaRegistries → RandomState → Overworld finalDensity MIN root,
without source code or class/JAR serialization. For each of the old
four-seed × 32 fixed SinglePointContexts, it observes only:
- `MulOrAdd`'s real enum operation, floating argument, upstream
  density runtime class and **upstream input raw bits**;
- `RangeChoice`'s selector `Marker` type and **wrapped density
  input raw bits**;
- the actual out-of-range `Ap2` enum operation, the two input
  runtime classes and their **independent raw IEEE bits**.

The three **already observed** values (MulOrAdd output, range
selector output and outer Ap2 output) are included only as fixed
equality anchors to the 128 existing source-free **inner** fixture.
The Python validator rejects any modified prior output word, wrong
seed/coordinate, nonfinite bits, class/enum substitution, source/Atlas
or server JAR pin change, unordered evidence, unexpected extra frames
or false-to-true qualification gate promotion. CI tests exercise
synthetic frames and compile the reflection bridge **without needing
the private JVM**.

After this PR merges, run *only this new original second-layer
diagnostic* from the existing private source-owner checkout:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_second_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-final-second-layer-128.json
```

Upload the source-free JSON, or the exact fail-closed JVM phase error.
No earlier 128 root, 128 inner, 512 cell or 768 NoiseChunk data need
recapturing. After real evidence, validate original MulOrAdd input
against the Rust fused node with its **actual** parameter and operation;
then recursively implement the underlying selector and out Ap2
dependencies and NoiseChunk interpolation/cache timeline.

**All source-law review, full-router and canonical NoiseChunk numeric
parity, independent VAR/SEM admission and production generation gates
remain false.** This PR does not publish terrain.
