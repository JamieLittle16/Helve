# Helve — 26.2 stock-worldseed noise → Rust parity handoff

**As of:** 20 October 2026. **Next-context starting point.**  
**Repository:** https://github.com/JamieLittle16/Helve  
**Branch:** main. **Verified merged baseline:** 492691b71d18e957e37145275df2b3dd0e8a8370 (PR #445).  
**Target:** Minecraft Java 26.2, protocol 776, DataVersion 4903.

**Important:** Fetch the current main SHA and PR/CI status when resuming. The
baseline above is evidence of this handoff's starting point, not a claim that
main will never move. The repository is sometimes locally displayed with an
older Crucible remote URL; follow the verified repository identity, not a
hardcoded assumption about the user's remote name.

## One-paragraph executive status

We have **successfully captured real vanilla, stock-registry, world-seeded**
NormalNoise-through-DensityFunctions.Noise output from the pinned Minecraft
26.2 JVM for **1,440 distinct requests**. PR #445 froze all 1,440 raw IEEE-754
bits into a source-free checked-in fixture, added an integrity/manifest
validator, mutation tests and CI, documented provenance, and **merged green**.
This is no longer an API-probing problem. It is **not yet a Rust world-seed
implementation, 1,440/1,440 Rust parity, general NoiseRouter/terrain parity,
independent VAR/SEM admission, or production generation authority**. The next
engineering work is to close the actual registered noise parameters and
world-seed positional RNG/normal-noise constructor laws, implement them as
immutable Rust cold setup, and compare genuine Rust outputs against the
pinned official 1,440-vector oracle.

## Verified state and PR chronology

- PR #439: source-free official RandomState binding shape/reflection frontier.
  Its uploaded JSON SHA-256 is
  1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7.
- PR #440: original reflective official-JVM stock-worldseed capture bridge and
  1,440-point strict collector, initially blocked on runtime diagnosis.
- PRs #441–#443: recover the actual JVM exception (Minecraft bootstrap intercepts
  ordinary Java output); final bridge catches Throwable and tags root cause +
  exact phase via FileDescriptor.out.
- PR #444: fixed observed NoSuchMethodException for obsolete
  HolderLookup.Provider.asGetterLookup(). The real 26.2 HolderLookup.Provider
  is itself a HolderGetter.Provider; the bridge verifies the subtype and
  uses the SAME stock provider object, no synthesized registry or holder.
- **PR #445:** https://github.com/JamieLittle16/Helve/pull/445 — SUCCESSFULLY
  MERGED, commit 492691b71d18e957e37145275df2b3dd0e8a8370.
  Its four PR checks were green: Rust and tooling quality, Repository guard,
  Worldgen strict-oracle format and whole-cost smoke, CLA. Its five
  post-merge main checks were also green: Rust and tooling quality,
  Repository guard, Worldgen strict-oracle format and whole-cost smoke,
  Exact 26.2 stored-state lookup, Bounded stored-world import transaction.
- **Not to repeat:** do NOT keep rebuilding the reflection/bootstrap/holder
  bridge, and do NOT request yet another capture of these exact 1,440 values.
  The reference is already captured, pinned and in the repository.

## Reference data, integrity and exact coverage

The original uploaded source-free JSON (held outside GitHub and available in
the prior conversation) is named
helve-26_2-world-seed-stock-registry-density-05.json:

- Original JSON byte SHA-256:
  ee2135a89e196e482ea13eb374423cf14fb73a2c7f3e1e175dda1fbf785dced4
  (346,656 bytes, 1,440 vectors, no Minecraft source text).
- Pinned official server JAR SHA-256:
  cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5
- Pinned Minecraft source archive SHA-256:
  1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750
- Stock VanillaRegistries.createLookup source-body SHA-256:
  63167b8b8e1f8ffd687a6577e61ab06c9e87ecb16457b9a65c67a8d8f07bf16d
- Reference fixture:
  vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt
  — exactly 1,440 LF-delimited 16-digit lowercase f64 raw-hex patterns,
  no 0x prefixes. Fixture SHA-256:
  79bf0251f2cf8bb7f4bfb226be0ba7912a7a574c6aaf8e8f5a9560dd2edfe414
  and verified Git blob SHA: 933126e315ca9cbe3d5e0691261bb68dacbc56f3.
- All 1,440 values were checked as finite double encodings.
- Reference line 0: 3fe642a30a35f266; line 480:
  bfb1cb44d1eacac0; line 1439: 3fc3cbbb372a1759.
- Dimensions: 3 ordered scaling profiles x 5 signed-worldseed patterns x
  3 registered noise keys x 32 block-coordinate triples = 1,440.
  Exact loop order:
  (1) unit, quarter_xz, quarter_xz_half_y;
  (2) 0, 1, -1, signed 64-bit MIN, 0x9e3779b97f4a7c15;
  (3) TEMPERATURE, CONTINENTALNESS, EROSION;
  (4) 32 signed block XYZ test positions with wrap/large-coordinate cases.
  **Do not alphabetize profile order based on the JSON object keys.**
- Stock JVM construction: VanillaRegistries.createLookup → the actual
  HolderLookup.Provider / HolderGetter.Provider instance →
  RandomState.create(provider, NoiseGeneratorSettings.OVERWORLD, worldSeed) →
  getOrCreateNoise(official Noises key) → official stock NOISE Holder →
  DensityFunction.NoiseHolder(Holder, NormalNoise) →
  DensityFunctions.Noise(xzScale,yScale) → SinglePointContext/compute →
  Double.doubleToRawLongBits.
  The Java helper is reflection-only, not copied Mojang source.

Manifest gate values (MUST remain distinct):
  stock_registry_used=true;
  world_seed_random_state_observed=true;
  world_seed_random_state_bound=false;
  source_text_included=false;
  independent_var_sem_admitted=false;
  production_worldgen_enabled=false.

The label *observed* describes true JVM reference acquisition, not successful
source review or verified Rust worldseed semantics. Never silently promote it.

## Relevant files — start here

**Current frozen evidence and test protocol**
- vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt
- tools/worldgen_26_2_stock_worldseed_fixture.py
- tools/tests/test_worldgen_26_2_stock_worldseed_fixture.py
- tools/worldgen_26_2_world_seed_density_capture.py
- tools/tests/test_worldgen_26_2_world_seed_density_capture.py
- tools/worldgen_java/HelveWorldSeededDensity262.java
- .github/workflows/worldgen-parity-benchmark.yml
- docs/architecture/WORLDGEN_STOCK_REGISTRY_WORLDSEED_ORACLE_262.md

**Re-usable, already-bit-matched direct-seeded Rust work**
- crates/world/helve-world-gen/src/improved_noise_262.rs
- crates/world/helve-world-gen/src/perlin_normal_262.rs
- crates/world/helve-world-gen/src/density_noise_direct_262.rs
- crates/world/helve-world-gen/src/density_kernel_262.rs
- crates/world/helve-world-gen/tests/perlin_normal_262_official.rs
- crates/world/helve-world-gen/tests/density_noise_direct_262.rs
- crates/world/helve-world-gen/tests/data/density_noise_direct_26_2_rawbits.txt
- docs/architecture/WORLDGEN_SEEDED_CONSTRUCTORS_262.md
- docs/architecture/WORLDGEN_BIT_PARITY_BENCHMARK.md

**Wider server and gating architecture**
- docs/execution/R2C_TO_R2D_READINESS_HANDOFF_2026-10-19.md
- docs/architecture/R2_R3_LIVE_ENGINE_ARCHITECTURE.md
- crates/world/helve-world-gen/src/lib.rs
- Normal production publication remains guarded; ordinary R2C is not
  automatically production-qualified merely because imported chunks render.

The improved/Perlin/Normal/direct density kernels already have exact official
vectors in their explicitly stated **direct-seed profile**, including the
480/480 direct DensityFunctions.Noise examples. In particular,
NormalNoise262::from_direct_seed_observed_profile(seed) reconstructs a
SPECIFIC observed four-slot legacy profile whose amplitude/first octave
parameters are pinned. **It must not be reused as though it were the
registered TEMPERATURE / CONTINENTALNESS / EROSION world-seed constructor.**
Different registry parameters, RNG family, salt and seed paths need explicit
proof. The existing immutable observed-parts constructor is useful for
isolated numeric-state replay.

## Next engineering plan — prioritized and concrete

### P0. Preserve the qualified baseline (no more oracle churn)

1. Verify fresh main head, PR #445 merged, CI green, and read this handoff
   and the source-free oracle architecture doc. Do not start from #440/#444.
2. Run the immutable reference checks locally:
   - python3 tools/worldgen_26_2_stock_worldseed_fixture.py
   - python3 -m unittest discover -s tools/tests -p
     'test_worldgen_26_2_stock_worldseed_fixture.py' -v
   - python3 -m unittest discover -s tools/tests -p
     'test_worldgen_26_2_world_seed_density_capture.py' -v
   - cargo test -p helve-world-gen
3. Optional, only on the private source-owning machine if original JSON is
   available: python3 tools/worldgen_26_2_stock_worldseed_fixture.py
   --capture /tmp/helve-26_2-world-seed-stock-registry-density-05.json.
   Do not upload the private Atlas DB, mc-src.zip or official JAR.
4. Keep the checked-in compact oracle immutable, not a test oracle that Rust
   can simply look up and return. Any new expected data must be independently
   sourced and pinned.

### P1. Close exact vanilla world-seed and registered-noise construction laws

Source-owning review and source-free observable witnesses, with independent
VAR/SEM admission if required, should establish for **the actual 26.2**
runtime and each of the three built-in registered noise keys:

- Registry key identity and actual NoiseParameters (first octave, all
  amplitudes and order), including the precise stock lookup scope/provider.
- RandomState.create(provider, settings key, seed): actual selection of
  settings, RNG family, base seed mixing, positional random factory and
  salts/named fork semantics, re-use/caching and seed sign/bit handling.
- RandomState.getOrCreateNoise and Noises.instantiate, plus each reached
  NormalNoise/PerlinNoise/ImprovedNoise and random factory constructor method.
- Independent source/semantic closure of reached helper delegates (named
  hash, seed mix, nextLong/nextInt/nextDouble, fork order, absent octaves,
  permutations, offsets, arithmetic rounding/wrapping). Enumerate only
  genuinely unresolved reachable methods; do not reopen qualified kernels.
- Equality of **stock registered holder/parameter provenance**, not merely a
  manually invented Holder.direct() containing plausible defaults.

Pin the exact source-body hashes or source-free numeric state receipts.
Do not infer any of the above from the previously qualified *direct*
RandomSource.create(long) path. Publish a tight source-free review/provenance
record, with unreviewed laws clearly marked. No copied Minecraft bodies.

### P2. Make one small, typed Rust source-grounded candidate

In helve-world-gen (or a justified adjacent COLD-only module), build
separate, immutable registered noise state/constructors for the three
observed keys. **No new resident world owner, no dynamic registry lookup
per sample, no network-thread generation and no per-block allocations.**
Options:
- First independently capture full numeric JVM runtime noise states and
  reconstruct them via existing from_observed_parts, to isolate sampling
  semantics from constructor/seed derivation. This is an *observed-state
  reference*, not proof of a general world-seed constructor.
- Then derive seed → stock keyed RNG → registered noise state in Rust using
  actually reviewed/pinned laws. Initialise once per seed/key (COLD),
  and borrow immutable prepared noise for dense scalar/plane/cell samples.

Use exact Java-compatible signed 64-bit and 32-bit overflow/wrap and
floating-point operation ordering, no fast-math or unproved FMA contraction.
If a registered noise profile needs more or different octaves than the
existing fixed four-slot observed direct profile, introduce a bounded,
faithful typed representation rather than silently truncating parameters
or mutating the qualified direct-seeded API.

### P3. Prove **1,440 / 1,440** actual Rust world-seed parity

Add a dedicated Rust integration test (NOT Java reflection at Rust test time)
which iterates the EXACT fixture row grid and computes every sample from the
new Rust seed/key/profile implementation. Compare each f64.to_bits() against
the line-indexed official frozen raw bits; include tuple/coordinate/expected
diagnostics on failure and stop any admission on even one mismatched bit.

Test both debug and optimized release builds. Test input validation, missing
key/unsupported parameters, signed-seed edge cases, 2^25 coordinate wrap,
constructor caching, no RNG stream cross-talk, state equality, plane/cell
versus scalar equivalence and zero hot-path allocation. Add an additional,
independent **held-out official seed/key/coordinate set** before claiming
more than qualification on the frozen 1,440 points; prevent corpus lookup
tables or formula-fitting from masquerading as a reusable generator.

Only after this outcome, update a specifically scoped parity flag to true
with the exact evidence and constraints. Independent source VAR/SEM and
production authority remain SEPARATE; do not repurpose the old
world_seed_random_state_bound field without defining/admitting its meaning.

### P4. Extend toward authentic worldgen, not prematurely to production

With a real seed-aware registered noise layer qualified, progress through
NoiseRouter.mapAll / registered density graph, interpolation, terrain
density, aquifers, biome/climate selection, surface rules, caves, structures,
lighting and exact semantic chunk output in gated, source-faithful increments.
Measure full 3D-cell output and real chunk parity before routing to the
existing SemanticDimensionInstance admission path. Keep the enclosing
R2C chunk-publication source-law and client gate independent: generating
numbers does not authorize broadcasting chunks.

**R2D planning boundary:** R2D is a persistent/repeatable visible-world
milestone on pre-generated world data. Full procedurally faithful generation
is not a prerequisite for R2D; avoid coupling these milestones or
misreporting the current R2C product gate as unlocked.

### P5. Optimize after authentic parity, against real workloads

Maintain low allocation/copy overhead, fixed/bounded memory and modular
architecture without virtual dispatch or registries in the hot scalar path.
Benchmark independent COLD setup vs steady-state density cell evaluation,
then complete chunk-request → generation → semantic install →
packet projection → stock-client visible end-to-end time with p50/p95/p99
and memory/CPU counters on matched 26.2 seed/chunk sets. Compare alternate
layouts/parallel strategies on identical data and source-exact outputs.
No numerical claim of outperforming SteelMC (or any rewrite) absent honest
end-to-end head-to-head evidence.

## Immediate first PR for a fresh context

**Preferred next unit of work:**
- inspect current 26.2 RandomState and Noises source-free review tools;
- implement one **bounded, explicit, source-free stock registered-noise
  parameter/state capture** or exact reviewed seed/positional factory law
  (prefer the latter when sufficient evidence already exists);
- ensure deterministic signed seeds and 3 keys, independent runtime receipts
  and fail-closed checks under local toy-JVM CI;
- add a typed foundation for Rust seed-aware construction, but **do not**
  claim the 1,440-bit parity until a real Rust test produces it;
- write a PR, green all relevant checks, update this handoff and docs, merge
  only when tests and gates genuinely pass.

Keep the code changes concentrated in the small worldgen layer, not an
infinite sequence of broad inventory/diagnostic PRs. If private source laws
are required, clearly specify the *single bounded source-owning run* needed.
The user has the verified mc-src.zip and Atlas DB locally; never invent
source law facts or relax hashes simply to make a demo green.

## Explicit prohibitions and success criteria

Do NOT commit or upload Minecraft source, decompiled bodies, original server
JAR, Atlas SQLite, private source-only traces or private raw environment
records. Only source-free, checksum-pinned derived evidence may enter GitHub.

Do NOT replace accurate vanilla public behavior with opportunistic
approximation to gain performance. Do NOT introduce another chunk/world
model or unblock the normal publisher outside independent admission. Do NOT
call the 1,440 captured Java values 1,440 matched Rust values.

**Next success criterion:** official stock registry parameters and seed/RNG
derivation independently established, a reusable immutable Rust constructor
implemented from those laws, and a genuine strict 1,440 / 1,440 Rust
comparison green (with appropriate held-out and source-review follow-up).
Until then: authentic reference corpus achieved; Rust worldseed parity OPEN.

## Helpful new-chat instruction

"Continue Helve from docs/execution/WORLDGEN_26_2_STOCK_WORLDSEED_TO_RUST_PARITY_HANDOFF_2026-10-20.md.
PR #445 is merged, world-seeded official 1,440-vector reference is pinned
and green, but Rust world-seed parity is NOT proved. Verify main, inspect
the source/registry parameter and RandomState RNG law gaps, implement the
next genuine Rust constructor/parity slice with precise fail-closed tests
and PRs, while preserving Helve's hyper-efficient modular, vanilla-faithful
architecture and separate R2C/R2D production gates."
