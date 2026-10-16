# R2C — Official 26.2 per-state client heightmap predicate oracle

**Status:** independently executable official-server runtime **candidate**;
not independently VAR/SEM source-admitted and **not production-generated**.

## Why section mutation flags cannot produce these heightmaps

Helve's existing generated `STATE_MUTATION_FLAGS` covers non-air,
counted fluid, random block ticks and random fluid ticks. It does
**not** encode the separate `blocksMotion()`, actual fluid emptiness
or `LeavesBlock` type tests required by the three client heightmaps.

The pinned official source archive SHA-256 is
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.
Source-derived unmodified Java file SHA-256 anchors:

| Source class file | Raw SHA-256 |
| --- | --- |
| `world/level/levelgen/Heightmap.java` | `399cd25b1d00b9537a96486d01ef90f4095dfb5f01a5b007925a8893fac95801` |
| `world/level/block/state/BlockBehaviour.java` | `598050c5e9c9064b8fc95f91c84d925695b573830eca129b81a964e1f171e572` |
| `world/level/material/FluidState.java` | `f861b76280724832b3fe348895f6d33f125b15c146eea51bfbfc9fe30f2a0b7f` |
| `world/level/block/LeavesBlock.java` | `327c0f09e58c457c4cd02d6bdbfb03242eedcba13263ba55727cc900d073ba39` |

`Heightmap.Types` selects:

- `WORLD_SURFACE`: `!state.isAir()`;
- `MOTION_BLOCKING`: `state.blocksMotion() || !state.getFluidState().isEmpty()`;
- `MOTION_BLOCKING_NO_LEAVES`: the second predicate and
  `!(state.getBlock() instanceof LeavesBlock)`.

Most importantly, `BlockBehaviour.BlockStateBase.blocksMotion()`
consults the cached solidity result and special-cases two block types.
The cached solidity depends on state collision shapes and explicit
force-solid overrides. **Do not infer it from non-air, section summary,
a short hand-maintained block name list, or the block state's integer ID.**

## Candidate runtime oracle

`tools/official_r2c_heightmap_facts.py` reuses the established
`official_state_data.py` pinned official-server downloader/classpath
and mapping resolver. It independently reflects exactly four
predicates for **every** entry of `Block.BLOCK_STATE_REGISTRY`:

1. non-air;
2. `blocksMotion()`;
3. fluid-state non-empty;
4. whether the block is a `LeavesBlock`.

It binds results to the official `Block.getId(state)` global state ID,
fails closed on any non-dense/duplicated/missing identifier, checks
boolean shape and obvious impossibilities, and pins the server SHA
against `vanilla.lock.toml`. No mapping by sorted strings and no
per-block world runtime lookups are introduced.

Its output is a **source-free** candidate JSON with 32,366 four-bit
records in direct vanilla-ID order. This future `u8` SoA representation
would require only ~31.6 KiB static data; it does not change the HOT
mutation path or rederive collision shapes per published section.
The existing `ClientHeightmaps::derive` remains the independent
world-level heightmap reference algorithm.

Run locally:

```bash
python3 -m unittest discover -s tools/tests -p 'test_official_r2c_heightmap_facts.py' -v
python3 tools/official_r2c_heightmap_facts.py \
  --output /tmp/26.2-heightmap-state-facts-candidate.json
```

The dedicated `R2C Official Heightmap Facts` CI workflow repeats the
hermetic tests and official runtime extraction with Java 25, checks
source/runtime commitments, and uploads a seven-day ephemeral output.
**The generated candidate is not committed and no table is wired into
production by this workflow.**

## Cross-oracle COLD projector integration (source-gated)

`tools/r2c_heightmap_candidate_bytes.py` validates the precise
official runtime JSON contract, all four source-file review anchors,
server/source hashes against `vanilla.lock.toml`, every state record,
and the explicit **false** source/production admission flags. It emits
only the 32,366-byte proposed fact array as an ephemeral workflow
artifact—not a committed or admissible production generated table.

A deliberately **dormant** server-local `CandidateHeightmapFacts` borrows
this byte array directly and implements the existing
`HeightmapStateFacts<BlockStateId>` contract in the COLD reference
projection. Construction scans the candidate exactly once and
independently cross-checks every non-air and fluid-nonempty bit against
the previously source/runtime-qualified `STATE_MUTATION_FLAGS`
generated data. It rejects missing/excessive entries, invalid upper
bits, inconsistent non-air/fluid facts, and impossible air/motion or
air/leaves combinations. After validation, each fact access is just a
dense indexed read, with no extra registry map, per-world copy, or
HOT-path bookkeeping.

The dedicated official-runtime GitHub workflow now additionally
runs an opt-in Rust integration test using the **actual** downloaded
official probe table. This selects motion-blocking leaf and non-leaf
states by their observed flags rather than handwritten IDs, builds
a two-section Helve chunk, and verifies that
`ClientHeightmaps::derive` computes exact topmost heights for
world-surface, motion-blocking, and no-leaves. The ordinary Rust CI
continues to test malformed and contradictory *synthetic* tables;
the official integration test is only enabled when its ephemeral
environment-provided fact table is present.

This makes an important independent data/algorithm cross-check,
**not** a substitute for the remaining complete source-fingerprint
and VAR/SEM admission.

## Remaining source admission and integration

Before promoting any table, establish complete exact fingerprint-pinned
source/VAR/SEM coverage for all four predicates (including
`BlockStateBase.calculateSolid` and relevant state/fluid delegates),
independently bind official runtime identities, review special cases,
prove dense table generation deterministically reproduces the
qualified artifact, then connect the immutable table only to the
**COLD** `HeightmapStateFacts<BlockStateId>` projector.

Finally replace the explicitly synthetic heightmap predicate in the
receipt/batch tests and run a stock 26.2 client with a source-admitted
pregenerated world. Neither this runtime oracle nor successful CI alone
is that proof.
