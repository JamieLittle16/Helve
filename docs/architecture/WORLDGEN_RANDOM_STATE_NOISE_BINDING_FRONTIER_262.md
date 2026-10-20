# Minecraft Java 26.2 — world-seed noise/registry binding frontier

**20 October 2026 · exact source-locked method shape discovery · no world-seed parity yet**

## Already proven, and what this does not duplicate

PR #438 established **480/480 exact official JVM raw-bit** matches for the direct
`RandomSource.create(long) → NormalNoise.create → NoiseHolder → DensityFunctions$Noise.compute`
path, under three XZ/Y scale profiles. These are real noise-backed density
values, but the constructor intentionally bypasses `RandomState`, world
generator settings, noise resource keys and `NoiseRouter.mapAll`.

The next semantic seam is therefore **world seed + noise registry key → held
parameters → `RandomState` random/noise creation → substitution into the density
graph**. Applying the existing direct-seeded `NormalNoise262` to a world seed
would be unjustified even if the final noise math is perfectly bit-matched.

## Bounded exact source and JVM discovery

`tools/worldgen_26_2_random_state_binding_frontier.py` has two independent
inputs, checked before producing any source-free manifest:

- **Pinned private Atlas**: require the exact Java 26.2 source archive and
  method identities; fail unless three previously observed method body
  SHA-256 fingerprints still match:
  - `RandomState.create(NoiseGeneratorSettings, HolderGetter, long)`:
    `cf52d92bbb7a73f32a72e7480ed98c2d08efdd48f5815b4342e37f8191eaf64f`.
  - `RandomState.getOrCreateNoise(ResourceKey)`:
    `056547e13816f7c7dd9a3a82e1acadbbc7e5729da50b3103f28b6d20a115e7ca`.
  - `NoiseRouter.mapAll(Visitor)`:
    `61ea5c6e319640ee561342ceeb9833aaf9c832ce3aa296e27a2bc1f965a9897c`.
- **Pinned official server JVM**: bootstrap `SharedConstants.tryDetectVersion`
  then `Bootstrap.bootStrap`, reflect the actual methods, constructors,
  selected static-key/registry fields and erasure parameter types for 12
  identified `RandomState`/noise/holder/router/registry classes. The JVM
  only reads reflection metadata: it **does not call** source methods under
  investigation, request chunks, instantiate `RandomState` or invent a
  registry. Only bootstrap is executed.

Source Atlas records retain bounded exact signatures, per-method body and
normalised hashes, syntactic callsite counts and unresolved-callsite counts.
The manifest deliberately labels every method `reviewed:false`. Runtime
reflection uses a dedicated process-stdout-descriptor stream with tagged,
ordered, bounded records to survive `System.out` replacement. The parser
rejects missing mandatory runtime classes, missing exact erasure method
signatures, unknown member types, duplicate/reordered records and unexpected
output framing.

The outputs are enough to design a genuinely type-accurate **next** original
Java test for `RandomState` with real holder/registry construction. They do
*not* prove anything about the code bodies, seed derivation, holder values,
registry bootstrapping, NoiseRouter visitation, or final-density computation.

## Source-owning-machine command

After the PR merges:

```bash
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_random_state_binding_frontier.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-random-state-binding-frontier-01.json
```

Upload only the resulting **source-free JSON** or the exact fail-closed error.
Never upload the private source archive, Atlas database, Mojang server jar,
bytecode, decompiled class bodies or any private registry snapshot.

The output explicitly asserts
`world_seed_random_state_bound:false`,
`independent_var_sem_admitted:false`,
`production_worldgen_enabled:false`, and
`source_text_included:false`.

## Next after the real JVM shape capture

1. Reconcile the *observed* `NoiseGeneratorSettings`, `HolderGetter`,
   `ResourceKey`, `Noises.instantiate` and noise holder constructor/method
   shapes with their exact pinned Atlas callsite targets.
2. Select a real built-in noise key and its registered parameters. Use the
   official registry/bootstrap path, not an invented `HolderGetter` with
   guessed numeric amplitudes.
3. Capture an official **world-seed-backed** noise instance's numeric
   construction state and `DensityFunctions$Noise.compute` raw-bit results.
   Verify distinct world seeds and a fixed key, repeat across XYZ coordinates.
4. Translate only source-reviewed, result-verified laws into a Rust
   `RandomState`-bound builder sharing immutable noise state; keep
   evaluation allocation-free and avoid a second world owner or router cache.
5. Later prove the actual `NoiseRouter.mapAll` visitor, cache topology,
   broader density graph and chunk-level worldgen publication independently.

Independent CI includes a wholly original miniature Java API with an
intentional stdout redirect and strict mutation tests. Hosted CI has **no
Minecraft jar or original source**. Its tests qualify the collector shape and
fail-closed gates, not actual vanilla world-seed parity.
