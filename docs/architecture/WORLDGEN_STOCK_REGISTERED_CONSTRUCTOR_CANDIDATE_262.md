# Minecraft Java 26.2 — stock registered-noise keyed world-seed constructor candidate

**20 October 2026.** This is a **real Rust world-seed-derived numeric constructor candidate** for the precisely scoped built-in Overworld `TEMPERATURE`, `CONTINENTALNESS` and `EROSION` keys, not a fixture lookup. The implementation is separate from both the already-qualified direct-seeded four-slot profile and the immutable observed-state replay. The production generator, independent source VAR/SEM, general noise-router, chunk publication and arbitrary registry or parameters remain unadmitted.

## Construction evidence and verification

Pinned official original server: Minecraft 26.2, protocol 776, DataVersion 4903, SHA-256 `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`. Official source archive and method fingerprints are in the stock-worldseed handoff and numeric receipt. The actual 15 full prepared Normal/Perlin/Improved numerical states came from the *stock registry-backed JVM*, not Rust. Their source-free fixture is `crates/world/helve-world-gen/tests/data/stock_registered_observed_state_26_2.txt`. Separately, the 1,440 stock JVM output oracle is `vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt`.

The independent reconstruction found this ordered candidate path, comparing the *full* 150 independently generated live octave permutations and X/Y/Z offset bits to the official receipts before porting to Rust:

1. Reinterpret signed world seed as raw `u64` (including `-1`, `i64::MIN`, high-bit salts).
2. Apply the seed-to-128-bit Xoroshiro128++ seed upgrade and two Stafford13 mixers. Construct a mutable **COLD** Xoroshiro stream.
3. Derive an initial positional fork by drawing two consecutive 64-bit results from that stream. For one built-in key, hash its *fully namespaced* string (`minecraft:temperature`, `minecraft:continentalness`, `minecraft:erosion`) with MD5, take two **big-endian** `u64` halves and XOR them with the positional pair.
4. Make *two distinct consecutive positional forks* from the resulting key-specific normal stream, one for each Perlin branch.
5. For each branch and live octave, use its exact signed octave name (`octave_-10` through `octave_-1` for these stock keys). MD5 hash halves are big-endian; XOR with the appropriate branch positional pair. Absent amplitude slots do not create an Improved sampler or consume branch RNG.
6. For each live Improved octave, generate three offsets from Xoroshiro 53-bit doubles multiplied by 256, then produce the 256-byte permutation by Fisher–Yates using **unsigned low-32 bounded multiply-high** draws with rejection, not the legacy 48-bit LCG.
7. Derive Perlin input factor `2^firstOctave`, value factor `2^(span-1)/(2^span-1)`, and normal value correction from the first/last nonzero octave range in the *strict* observed order. Freeze all numerical states in existing immutable Rust samplers.

The Rust implementation holds the three identity hashes and ten octave-name hashes as static constants, recomputable from RFC 1321 MD5. There is no dynamic hashing, heap allocation, RNG, registry lookup or polymorphic dispatch in steady-state density evaluation. Key-specific parameter amplitude shapes remain immutable; all buffers are created once at initialization.

## Tests and scope boundaries

- The new source-level Rust module `seeded_registered_noise_262.rs` creates **new** state from any supplied 64-bit seed for the **three listed keys**, without reading official observed state or output fixtures. Its API is clearly marked `candidate` pending independent source review and held-outs.
- The integration test `stock_registered_observed_262_official.rs` must first require entire per-key/per-seed prepared states to be exactly equal (`RegisteredNormalObserved262::state_bits_equal` covers all byte permutations, all offsets, amplitude/factor bits and absent-slot masks).
- An independent second test uses the Rust-derived state and old sampler and compares **all 1,440 raw double result bits** to the separate frozen JVM oracle across three scale pairs, five signed seeds, three keys and 32 signed coordinates.
- Both tests must run in **debug and release** through the existing strict Worldgen CI. Existing direct-seed 480/480 regressions must remain green.
- An arbitrary unseen world seed is not certified by these 5 seeds alone. An additional held-out independent stock JVM capture and signed seed/branch/parameter source-law review are necessary for broader semantics.

**Strict gates:** `world_seed_random_state_observed=true`, independently verified scoped Rust parity only upon passing CI; `world_seed_random_state_bound=false`, `independent_var_sem_admitted=false`, `production_worldgen_enabled=false`. The source-method inventory records method identity, **not proof of every reached RNG helper's semantic law**. Do not promote it to production automatically, and do not conflate R2D pregenerated-world readiness with procedural world generation.

## Follow-up source review

Review the pinned 26.2 bodies, delegates and call-order for `RandomState.create`, `RandomState.getOrCreateNoise`, `Noises.instantiate`, `XoroshiroRandomSource`, `Xoroshiro128PlusPlus`, `RandomSupport.upgradeSeedTo128bit`, `XoroshiroPositionalRandomFactory.fromHashOf`, the 26.2 `NormalNoise`/ `PerlinNoise` constructors and the reached `ImprovedNoise` constructor and `nextInt/nextDouble`. Verify exact branch choice for OVERWORLD and whether registry caching/fork naming differs for arbitrary custom datapack settings. Preserve independent body SHA/hash provenance and VAR/SEM review gates.

No Mojang source text, private Atlas data or JAR is committed. The next bounded official source-owning test should be held-out seeds and arbitrary signed positions, **not** recapturing the original 1,440 values or rebuilding the completed reflection bootstrap.
