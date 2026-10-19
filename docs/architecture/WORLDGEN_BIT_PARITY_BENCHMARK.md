# Minecraft 26.2 worldgen — bit parity and latency qualification

**Date:** 19 October 2026  
**Target:** Java 26.2 · Protocol 776 · DataVersion 4903  
**Official source ZIP lock:** `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`  
**Official server runtime lock:** `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`  
**Current status:** source-free bit-level differential *format* and non-vanilla whole-cost benchmark harness implemented; **no admitted 26.2 noise implementation or official noise output vectors yet**.

## Hard correctness law

Strict mode must reproduce the exact target-version externally observable generated world for the selected seed, dimension, generator settings and chunk neighbourhood. Where Java uses `double`, any intermediate stage explicitly required by its source law must compare by **all 64 IEEE-754 bits**, not by tolerance, numerical equality, string formatting or post-rounding. Signed zero and NaN payloads are distinct bit patterns even when numerical comparison would conceal a difference.

The source-owning reviewer must establish and fingerprint **exact official 26.2 methods and their reached delegates**, then capture source-free output bits from the *independent official implementation*, bound to the pinned source ZIP and server runtime. The review must account for seed mixing, coordinate wrapping, mutable RNG consumption order, chunk-status ordering, noise parameter registry, density-router selection, biome sampling, caves/aquifers, structures and decoration. **A manifest merely claiming the pinned hashes is not proof**: the runtime collector and method identity need independent source/VAR/SEM review.

### Source-free raw-bit differential tool

`tools/worldgen_noise_oracle.py` accepts two JSON manifests, one `official_26_2_noise_oracle_candidate` and one `helve_noise_candidate`. The manifests agree on source/runtime version, stage and exact method body fingerprint. Every vector has `seed_bits`, `x_bits`, `y_bits`, `z_bits`, and `value_bits` as lowercase `0x` followed by exactly 16 hex digits, preserving all IEEE-754 bits. Even a *single* differing bit is a hard failure. Missing/extra input vectors, duplicates, fewer than 16 cases, insufficient seed diversity, or omitted +/- zero and negative-coordinate probes fail. Raw bits are never converted to Python floats.

Manifest header:

```json
{
  "schema": 1,
  "kind": "official_26_2_noise_oracle_candidate",
  "minecraft": "26.2",
  "protocol": 776,
  "data_version": 4903,
  "source_archive_sha256": "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750",
  "official_server_sha256": "cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5",
  "stage": "normal_noise",
  "method_body_sha256": "REPLACE_WITH_64_HEX_DIGITS_FROM_PINNED_ATLAS",
  "source_text_included": false,
  "independent_var_sem_admitted": false,
  "production_worldgen_enabled": false,
  "vectors": []
}
```

**The example above is a deliberately invalid template**, not captured reference data. Populate it on the source-owning machine with independently observed `Double.doubleToRawLongBits` (or the exact source-equivalent output representation), 16+ diverse nonduplicate vectors, and the actual fingerprint. Do not commit official Java text or binaries. For integer RNG stages, agree on the exact bit reinterpretation contract before use; this initial formatter is principally intended for floating-point noise/density outputs.

Run:

```bash
python3 tools/worldgen_noise_oracle.py \
  --reference /private/official-26.2-source-free-normal-noise.json \
  --candidate /private/helve-source-free-normal-noise.json
python3 -m unittest discover -s tools/tests -p 'test_worldgen_noise_oracle.py' -v
```

The tool intentionally outputs `official_source_review_admitted=false` and `production_worldgen_enabled=false`, even on bit-for-bit agreement. A later independently approved source gate, not this tool, decides admission. Add reference probes on negative chunk borders, +/- zero, half-grid positions, extreme seeds, y=world-bottom/top, precision-boundary coordinates, NaN/infinity/error cases **only if** the official path permits them, and across Overworld/Nether/End selected profiles. A full generated chunk also requires exact semantic block/biome/height/light/feature comparisons; matching one noise stage is never full vanilla terrain parity.

## First executable official noise oracle: `ImprovedNoise` (26.2)

The target 26.2 source-owning capture entry point is now
`tools/worldgen_26_2_improved_noise_capture.py`. It binds the existing
local Vanilla Atlas to the **exact pinned official source ZIP**, resolves
a unique `ImprovedNoise#noise(double,double,double)` declaration and
preserves its Atlas method-body fingerprint. It checks the **official
server JAR SHA-256** before invoking a small locally compiled **original,
reflective** Java probe against the unmodified official runtime.

The probe constructs `ImprovedNoise` using `RandomSource.create(long)`
for each selected seed and invokes its public 3-coordinate method. Five
seed bit-patterns and 32 coordinate triples (160 distinct requests) include
negative grid boundaries, integer/fractional grid coordinates, positive
and negative zero, extremes and small fractional values. It captures
`Double.doubleToRawLongBits` as sixteen raw hexadecimal digits, without
converting any response to a Python floating-point number. The only
output is a source-free candidate manifest. All original source and
Java probe binaries stay local and outside the repository.

On the source-owning machine:

```bash
cd ~/Crucible
git switch main && git pull --ff-only
python3 tools/vanilla_atlas.py \
  --db .crucible/vanilla/atlas.sqlite \
  verify-source "$HOME/Documents/mc-source/mc-src.zip" \
  --lock vanilla/vanilla.lock.toml

python3 tools/worldgen_26_2_improved_noise_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-improved-noise-official-candidate.json
```

The script can download the pinned official server runtime using the
existing `official_state_data.resolve` path when `--server-jar` is absent.
It requires a working local JDK and fully populated, matching local
Atlas. Outputs are created exclusively; no existing file is overwritten
and no official source/JAR is committed. If any declared class,
constructor, method, source method fingerprint or runtime binding differs,
the run **fails closed**. Its deterministic JSON records an
`official_26_2_noise_oracle_candidate` at the `improved_noise` stage
for comparison against future Helve Rust samples with
`tools/worldgen_noise_oracle.py`.

**These are candidate samples, not a semantic admission**: a single
parent method body fingerprint is insufficient to certify constructor,
`RandomSource` creation, its PRNG sequence, the reached five-argument
noise overload, interpolation, gradient, permutation or floating-point
operation order. Those methods and dependencies require independent
VAR/SEM source review with their own identities and error/branch coverage
before the output can anchor a *source-admitted* strict parity claim.
We have **not** run this capture on the source-owning machine in this
change, and there are **no 26.2 official noise bit vectors in Git**.

The accompanying synthetic JDK test compiles a minimal original
`RandomSource`/`ImprovedNoise` fixture and validates signed zero,
source method selection, source/runtime mismatch rejection, output
exclusivity and lossless transport. It **does not** pass by substituting
a synthetic answer for the official reference.

## Reproducible performance harness (source-free, *not* a 26.2 noise result)

The current `SteppedSurface` benchmark is a mechanism baseline, not a real-noise benchmark. It records *three distinct costs* instead of quoting an isolated microbenchmark as chunk loading:

1. `256_column_samples`: just the 16×16 height samples per chunk.
2. `sample_and_construct_sections`: full 24-section 384-block-tall reference chunk production including block+biome final section construction.
3. `sample_construct_and_resident_install`: the same complete semantic build **plus** authoritative `SemanticDimensionInstance::admit_chunk` with generation/revision and directory installation.

```bash
cargo test --locked -p helve-world-gen
cargo clippy --locked -p helve-world-gen --all-targets --all-features -- -D warnings
cargo bench --locked -p helve-world-gen --bench worldgen_cold -- \
  --chunks 64 --warmup 3 --rounds 25 --output /tmp/helve-worldgen-baseline.json
```

Measurements include p50/p95/p99/max nanoseconds per chunk, count, accumulated sample duration and the existing `helve-benchmark-support` host identity (commit, rustc, target CPU, topology/affinity, governor, clocks, cache, operating system, RAM). Workload coordinates include signed chunk positions and the standard 24-section vertical profile. Workloads rotate order to reduce thermal-order bias, warm up before recording, use `black_box`, and allocate actual final reference sections. **Performance conclusions require three or more independently repeated process runs on pinned hardware**, with cold/warm cache variants, competing-workload states, and A/B baseline alternating order. No hosted-runner absolute-latency acceptance gate.

The CI job `worldgen-parity-benchmark.yml` runs a tiny representative diagnostic and uploads JSON. It confirms the benchmark works, not that it is fast, not that it matches vanilla, and not that a baseline choice was made. Tests are fully source free.

## Source-honest optimisation search: no FLOP left on the table

The eventual engine should compile immutable **seed + dimension + selected settings** into retained, statically bound parameter/permutation/router state *once per world*, not once per chunk or once per client. Evaluate the shared density computation DAG with preallocated local scratch; remove repeated hash/registry dispatch, convert invariant metadata to compact resolved IDs and avoid heap allocation and virtual dispatch in sample kernels.

Prioritise these hypotheses in measured order, each with a separate parity proof and baseline:

- **Grid/cell reuse and coordinate coherence:** sample common lattice corners once when the **exact target source method** permits reuse, and carry interpolation state across neighbouring points/chunks without changing floating-point operation order. Try sampling a batch of nearby points rather than repeated recursive density-graph calls; only publish after raw-bit equality.
- **Immutable node specialization:** remove repeated evaluation of target constants and common pure subexpressions, keyed by full semantic identity (seed/dimension/router/position/stage). Do not perform algebraic reassociation, FMA fusion, fast-math, inappropriate denormal flushing or scalar transcendental substitutions without strict cross-platform byte parity evidence. Java and Rust may differ even when both are IEEE-compliant.
- **Coordinate derivation and common noise geometry:** hoist verified integer coordinate transforms, permutation indices and integer subexpressions, and reuse immutable seed-wide tables. SIMD may batch independent lanes, preserving per-lane source floating-point evaluation order; SIMD instructions alone do **not** establish correctness.
- **Resident-world demand pipeline:** bounded generation ahead of client view-interest using generation/revision-stamped tasks, reuse prepared chunk work across simultaneous clients, and avoid running synchronous noise evaluation on the networking poll/flush path. Cold-demand latency still counts queue time, generator time, postprocessing/lighting, section commit, persistence and client-visible send time.
- **Parallelism without semantic races:** only independent noise evaluation phases may run concurrently; structures, cave dependencies and neighbour effects must preserve exact source sequencing and consume RNG in deterministic order. Stale completed work cannot overwrite a newer incarnation.

## Whole-system benchmark acceptance protocol

On target hardware, compare the **same locked official 26.2 seed set and generated chunks**:

- Source-differential: per-stage raw 64-bit outputs and exact final target block/biome/height/light/feature distributions for interior, seam, negative, extreme and multi-chunk cases.
- Stage cost: immutable initialization, noise RNG/parameters, density graph, aquifer, biomes, surfaces, population/structures, light, section build, atomic install, store and packet projection. Record total allocations, bytes copied, peak RSS, memory bandwidth and CPU cycles/cache misses.
- Client-facing cost: p50/p95/p99 and max **chunk request → available resident → projected/sent → visible in stock client** under cold generation, warm reuse, 9/25 chunk burst, 2+ viewers, travelling frontier, reconnect and slow-client backpressure.
- Mechanism comparison: run unoptimised target-faithful reference, each single optimization, and combined candidate on one locked test corpus. Exclude compilation/startup only when reporting explicitly steady-state costs; capture startup separately.
- Reject a candidate if **any** bit differs in strict mode, memory or queue growth is unbounded, or an observed improvement only shifts blocking work from one stage to another.

There is no evidence yet for a specific speedup or absolute millisecond budget; choose a production p99 budget only after we have authentic target noise baselines and whole-system traces. Worldgen is **not an R2D prerequisite** and the production R2C publication gate remains closed.
