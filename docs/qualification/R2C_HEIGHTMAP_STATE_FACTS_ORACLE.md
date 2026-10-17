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

## Independent runtime reproducibility and exact frozen state-fact identity

The official Java 25 heightmap workflow now executes the full
`Block.BLOCK_STATE_REGISTRY` reflection oracle **twice** against
the SHA-256-pinned official 26.2 server and independently compares
all 32,366 ID-indexed four-bit records, byte for byte. The small,
source-free audit contains a digest, a 16-bin histogram and three
heightmap-predicate counts. A changed value at even one ID, missing
record, unpinned source identity or source/production admission flag
fails closed.

On 17 October 2026, the full second official runtime run reproduced:

- Dense 32,366-byte SHA-256:
  `6dc4edc0f6178490af9d79463eca0373b8b359e351d173ebc51cf6166d74c3eb`
- 4-bit flag histogram in `0..15` order:
  `[3,3924,0,16493,0,623,0,11015,0,0,0,154,0,0,0,154]`
- Topmost-height predicate matching state counts:
  `WORLD_SURFACE=32363`,
  `MOTION_BLOCKING=28439`,
  `MOTION_BLOCKING_NO_LEAVES=28131`.
- Additional independent field counts:
  `leaves=308`, `fluid_non_empty=11792`.

These exact numbers are **frozen as independent CI expectations**
against the official runtime probe. The server identity and source
review anchors are checked against the existing lock. Only an
ephemeral 7-day audit/report and the original source-free candidate
are uploaded; the second full candidate is removed after comparison.

This is stronger determinism/identity evidence for the eventual
immutable cold-path table. It is **not a second implementation of the
heightmap source predicates** and does not qualify
`BlockStateBase.calculateSolid`, source/VAR/SEM or live
chunk publication. Those must remain separate gates.

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

## Full packet-envelope integration using the official oracle

The same dedicated Java-25 runtime workflow now also runs
`r2c_section_candidate::tests::official_heightmap_facts_reach_receipt_bound_chunk_packet`
with the **actual 32,366-byte ephemeral runtime table**. Its COLD
fixture constructs a structured imported chunk with two verified
vanilla state IDs selected directly from the official predicates:
motion-blocking leaf above motion-blocking non-leaf ground in the
same column. It installs the chunk into the authoritative
`SemanticDimensionInstance`, retains the minted source receipt,
prepares the source-selected initial view, and sends cache centre,
batch start, source-receipted **complete** chunk-with-light body,
and batch finish through the continuing R2B driver. It then
consumes a genuine matching batch acknowledgement.

The test independently checks exact big-endian heightmap wire words
inside the framed chunk body. The selected column must have relative
`WORLD_SURFACE=32`, `MOTION_BLOCKING=32`, and
`MOTION_BLOCKING_NO_LEAVES=4`, with other columns empty. The
rest of the packet and signed centre coordinates are checked at the
frame boundary. This catches a swapped or approximated leaf-motion
heightmap **inside actual packet assembly**, not only inside a
standalone heightmap reference result.

The fixture is a **structured COLD import**, not a captured or
byte-decoded natural Anvil file, and the receiving official client is
not launched. Consequently, even a successful full-envelope test
does not itself close VAR/SEM source admission or the R2C milestone.

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

## Extended real-oracle predicate branch coverage

The dedicated official 26.2 heightmap workflow now feeds **additional
runtime-selected global state IDs** to the same existing borrowed fact
adapter and `ClientHeightmaps::derive` COLD reference test. The
selected exact flag combinations must exist within the independently
reproduced 32,366-state official registry:

| Four-bit flags | Source-observed case | Expected client maps |
| --- | --- | --- |
| `0b0101` | Non-air, no `blocksMotion`, nonempty fluid, not leaves | All three maps |
| `0b0001` | Non-air, no motion, no fluid, not leaves | WORLD_SURFACE only |
| `0b1111` | Waterlogged motion-blocking leaf | WORLD_SURFACE and MOTION_BLOCKING, **not** NO_LEAVES |

Those cases are placed into distinct columns of the already existing
two-section source-test chunk, alongside the ground-below-dry-leaves
case. The expected *relative* first-available heights are checked on
all three maps at every column, including expected zeros where a
column has no matching source predicate.

No state ID or block name is hard-coded: each case is found by scanning
the actual official runtime table. The test intentionally fails on
missing cases, swapped predicates, wrong section/column indexing or
incorrect leaves/fluid precedence. This adds genuine source-derived
branch diversity to the existing official-oracle/Helve integration
without another state table, geometry implementation, or HOT-path
bookkeeping.

This remains a **runtime-oracle integration test**, not the independent
source/VAR/SEM admission of the whole state-fact table or a stock-client
visual world witness. The production R2C publisher remains gated.
