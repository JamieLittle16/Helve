# R2C Current State — Native World Projection

Status: **live engineering ledger**  
Target: **Minecraft: Java Edition 26.2 / protocol 776 / DataVersion 4903**  
Canonical plan: `R2C_EXECUTION_PLAN.md`  
Architecture: `../architecture/R2C_WORLD_PROJECTION_IMPLEMENTATION.md`  
Milestone qualification: `../qualification/R2C_WORLD_PROJECTION_QUALIFICATION.md`

This file records the implementation/evidence boundary actually present on `main`. The architecture and exit criteria remain normative; this ledger exists so contributors do not reconstruct status from historical branches or experimental benchmarks.

## Current boundary

R2B is complete: a stock 26.2 client reaches replay-free Play and the exact bounded connection driver remains live through the explicit `WorldProjection` handoff.

R2C has crossed the stored-world/import boundary and now also has the first coherent multi-component chunk owner. `main` owns:

- resident chunk lifecycle with compact generation identity and stale-handle rejection;
- exact 26.2 stored block-state import with genuine-save differential evidence;
- import-to-residency qualification and selected cold-import optimizations;
- target-neutral 4×4×4 biome semantic storage;
- one whole-chunk `ChunkRevision` coherence baseline shared by block and biome mutation;
- atomic same-driver publication admission and allocation-free one-body publication progression;
- completed source-free human review and explicit semantic decisions for the selected biome, heightmap and light laws;
- a one-command local runner that regenerates the exact reviewed world-state dossier and performs the independent Vanilla Atlas admission gate.

The world-state review is therefore **not** the current blocker. The remaining admission boundary is independent local Atlas validation and explicit promotion of that exact source-free bundle. Production heightmap/light and 26.2 world-state wire implementation remain forbidden until that promotion succeeds.

The remaining world-publication groups outside the completed BIOMES / HEIGHTMAPS / LIGHT review also remain independently unadmitted: world-entry ordering, chunk-span/batch state, block-section publication law not already covered by admitted lower layers, selected block-entity publication, pacing/acknowledgement and exact packet identities.

```text
completed human BIOME / HEIGHTMAP / LIGHT source review
        ↓
independent local Atlas gate + explicit promotion
        ↓
Helve-native heightmap/light state
        ↓
coherent resident block + biome + heightmap + light ownership
        ↓
remaining world-wire source admission
        ↓
transparent reference projector
        ↓
qualified production projection mechanism
        ↓
landed same-driver bounded publication substrate
        ↓
stock-client native Helve world
```

Packet/wire facts are never inferred merely because the runtime substrate or a human review record exists.

## Slice ledger

| Slice | State | Evidence / boundary |
| --- | --- | --- |
| R2C.0 frontier/contracts | **ESTABLISHED** | Finite pregenerated-world-first scope and ownership/evidence boundaries are frozen. World generation and movement-driven interest are not prerequisites for the first R2C gate. |
| R2C.1 world-state source review | **HUMAN REVIEW COMPLETE; INDEPENDENT ATLAS ADMISSION/PROMOTION PENDING** | BIOMES, HEIGHTMAPS and LIGHT now have explicit source-free selected/rejected closure and semantic decisions bound to the pinned 26.2 source identity. `r2c_world_state_local_admission.py` regenerates the exact dossier, materializes VAR/SEM evidence and runs the independent Atlas gate. Production admission is still false until a green gate is explicitly promoted. |
| R2C.1 remaining world-wire review | **PENDING** | World-entry, chunk-span, selected block-entity, pacing/acknowledgement and exact packet-identity/order law still require bounded source admission. Existing lower-layer block-section evidence may be reused only where its admitted claim exactly matches the R2C route. |
| R2C.2 resident-world substrate | **LANDED** | `DimensionInstance`, compact chunk generations, direct resolved access, unload/reload and stale-handle rejection are on `main`. Sparse directory lookup is a lifecycle boundary, not a HOT cell-access mechanism. |
| R2C.2 whole-chunk freshness | **BLOCK + BIOME COMPOSITE LANDED** | `LiveChunkSemanticState` composes existing block and biome owners without copying, requires exact position/generation/lattice identity and uses the existing `LiveChunkCore` revision as the sole whole-chunk semantic clock. Real block or biome changes advance that one revision; no-ops/rejected mutations do not. No secondary revision, dynamic dispatch or projection work was introduced. |
| R2C.2 resident qualification | **CORRECTNESS/HOSTED DIAGNOSTICS LANDED; TARGET PERFORMANCE ADMISSION SEPARATE** | Lifecycle/HOT-path qualification and the official-save import-through-residency path are green. Hosted timing is diagnostic only. |
| R2C.2S block-section production policy | **DECISION PIPELINE LANDED; REAL EVIDENCE/POLICY NOT FROZEN** | Direct, adaptive-local, fast-local and packed candidates are correctness-qualified. M0.3D/issue #19 has the complete measurement/Pareto/policy machinery; the remaining work is real four-seed population evidence, exact-revision correctness sealing, controlled physical target-hardware runs and the explicit reviewed winner/loser record. `SEC-REF-DIRECT` remains reference-only. |
| R2C.3 pregenerated-world block import | **LANDED AND GENUINE-SAVE DIFFERENTIAL GREEN** | Bounded Anvil framing, DEFLATE, schema-directed NBT, exact persisted-state resolution and final section construction are on `main`. Independent official-save comparison covers 12,696 block-bearing sections / 52,002,816 block cells exactly. |
| R2C.3 import → residency qualification | **LANDED** | Genuine official save passes validated region read → bounded decompression → semantic import → final section construction → `DimensionInstance` residency with exact evidence identity and scratch high-water checks. |
| R2C.3 selected cold-import mechanisms | **LANDED** | Byte-table gzip CRC32 and four-bit packed-state specialization crossed semantic + benchmark qualification. Generic five-bit-and-wider packed decoding remains intact and regression-covered. |
| R2C.4 biome semantics | **TARGET-NEUTRAL STORAGE LANDED; 26.2 HUMAN REVIEW COMPLETE; ADMISSION PENDING** | One 64-sample biome lattice per logical section is live under static target-neutral storage. Reviewed 26.2 palette/wire law is source-free evidence only until Atlas promotion. |
| R2C.4 heightmap semantics | **HUMAN REVIEW COMPLETE; IMPLEMENTATION BLOCKED ON ADMISSION** | Selected client heightmaps are reviewed as derived state from authoritative blocks rather than persisted Heightmaps NBT becoming live truth. Runtime derivation starts only after independent promotion. |
| R2C.4 light semantics | **HUMAN REVIEW COMPLETE; IMPLEMENTATION BLOCKED ON ADMISSION** | Persisted `isLightOn`, DataLayer shape, lookup, mask classification and initial wire law are reviewed. Missing/false light-correctness cannot be silently upgraded; without relighting the unsupported route must fail closed. Runtime ownership starts only after independent promotion. |
| R2C.5 reference projector | **PENDING R2C.4 + REMAINING WORLD-WIRE ADMISSION** | Must consume one coherent semantic chunk state and remain the permanent correctness/freshness oracle before projection optimization. |
| R2C.6 production projector | **PENDING REFERENCE PATH + MECHANISM EVIDENCE** | Cache/snapshot/layout choices remain a mechanism tournament. No network-shaped second world representation may become live truth. |
| R2C.7 same-driver publication | **TRANSPORT/FAIRNESS SUBSTRATE LANDED; PROJECTOR INTEGRATION PENDING** | Internal server composition admits already target-encoded bodies through the exact continuing `ConnectionDriver`. Atomic batches reuse transactional queue admission; large ordered publications reuse the generic one-word `PublicationCursor`. Backpressure advances neither egress transaction state nor cursor progress. There is no second queue/socket or public raw-packet injection API. |
| R2C.8 stock-client native world | **MILESTONE EXIT** | Complete only when an unmodified 26.2 client renders Helve-owned terrain with zero captured world/chunk/light replay. |

## World-state human review now closed

The committed source-free semantic decision record is `vanilla/reviews/network/r2c-world-state-semantic-admission-decisions.json`. It records explicit human-authored rules rather than generated semantic inference.

Important selected laws include:

### Biomes

- one biome container is serialized after the block-state container inside each logical section;
- the semantic lattice is 4×4×4 = 64 entries with local index `x + 4*z + 16*y`;
- the 26.2 biome strategy selects single-value, linear-local or registry-global palette modes by required width;
- selected palette/container/network storage behavior and non-spanning packed-word law are explicitly reviewed;
- target biome resolution remains fail-closed before encoding rather than relying on Mojang's encode-side unknown-id fallback.

### Heightmaps

- the client set is WORLD_SURFACE, MOTION_BLOCKING and MOTION_BLOCKING_NO_LEAVES;
- each map has 256 x/z columns and stores first-available Y relative to dimension/chunk minimum Y;
- priming scans downward and records `y + 1` at the first state satisfying each selected predicate;
- Helve R2C intentionally derives these client heightmaps from authoritative block state instead of treating persisted Heightmaps NBT as independently fresh live truth.

### Light

- persisted `isLightOn` is explicit and defaults false;
- BlockLight/SkyLight arrays are independent optional persisted layers;
- R2C may treat persisted layers as publication-ready only when the imported chunk is light-correct; false/missing correctness fails closed until relighting exists;
- a DataLayer is 4096 nibbles / exactly 2048 raw bytes with Y-Z-X logical indexing and low/high nibble placement;
- initial light masks distinguish null, empty-present and non-empty-present layers;
- the reviewed light lattice is dimension section count + 2 and initial wire ordering is explicit in the human decision record.

These are reviewed claims, **not yet production authorization**. The independent Atlas gate still owns that transition.

## Whole-chunk coherence baseline

`LiveChunkSemanticState` is now the first multi-component resident semantic owner. It deliberately does not introduce a second revision counter.

```text
LiveChunkCore blocks ─┐
                      ├─ LiveChunkSemanticState ── one ChunkRevision / ChunkStamp
ChunkBiomeColumn ─────┘
```

Composition is O(1): existing owned components are moved under the composite after exact position, generation and vertical-lattice equality checks. Ordinary reads remain statically dispatched. Real biome mutation advances the same revision already used by block mutation; same-value mutation and rejected access do not invalidate the stamp.

This is intentionally the conservative R2C baseline. Per-layer block/biome/height/light revisions remain an optimization hypothesis and may be added only if measured avoided rebuild work justifies the extra HOT bookkeeping and retained bytes.

The existing block-only `PublishedChunk` remains valid as a reference block image, and its stamp is conservatively invalidated by any real biome change because the revision is shared. It must not become the final full-world projector snapshot once biome/height/light are target-visible inputs.

## R2C.1 independent admission boundary

The canonical local command is now:

```bash
cd ~/Helve
git switch main
git pull --ff-only

STAMP="$(date +%s)"
OUT="$HOME/Downloads/helve-r2c-world-state-admission-$STAMP.tar.gz"

python3 tools/r2c_world_state_local_admission.py \
  --db .crucible/vanilla/atlas.sqlite \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --output "$OUT"
```

The runner regenerates the exact current dossier, binds the committed human review/semantic decisions, materializes the source-free VAR/SEM/gate bundle and runs the independent Atlas gate against source archive SHA-256:

`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`

It does not promote repository evidence automatically. Only a content-bound `admitted=true` result may be fed to `r2c_world_state_admission_promote.py`. Promotion then revalidates the complete staging/report relationship and writes the canonical committed evidence with:

```text
source_admitted = true
production_implementation_authorized = true
runtime_behavior_implemented = false
```

Until that succeeds, reviewed target-specific biome IDs/palette law, heightmap IDs/packing and light masks/arrays remain unavailable to production target code.

## R2C.2S section-policy gate

M0.3D remains independent of semantic admission. Its infrastructure is complete; its final evidence/policy is not.

The remaining decision evidence is:

1. one admitted complete `vanilla-section-representative-v1` four-seed population artifact;
2. a fresh sealed full correctness bundle from the exact revision being measured;
3. at least five balanced rounds of `tools/section_m03d_qualification.py` on controlled physical target hardware;
4. inspection of the dimension-separated Pareto/noise result;
5. an explicit human-reviewed production-policy record with durable survivor/loser rationales.

No hosted-runner timing may select the production representation.

## Immediate next engineering moves

1. Run the independent local world-state Atlas admission and explicitly promote the exact green source-free artifact. Human review is already complete; do not rebuild that review pipeline.
2. In parallel, finish the resident-lifecycle composition so the new coherent semantic chunk owner reuses the existing sparse directory/generation/stale-handle machinery rather than creating a second map or clock.
3. After promotion, implement target-neutral heightmap derivation from authoritative blocks and target-neutral imported light ownership with the explicit light-correctness boundary. Join both to the same whole-chunk revision.
4. Close the remaining selected world-wire source groups: world entry/order, chunk span/batch state, selected block entities, pacing/acknowledgement and exact packet identities. Reuse existing admitted lower-layer evidence only where claim identity matches exactly.
5. Build R2C.5 as a transparent reference projector from one coherent semantic chunk state into the fully admitted 26.2 law.
6. Only then benchmark projection/cache/snapshot mechanism candidates and select production R2C.6 by whole-path cost.
7. Integrate the selected projector through the already-landed internal atomic/fair same-driver publication seams; no second egress path or R2C-specific cursor is permitted.
8. In parallel, finish M0.3D with real physical target-hardware evidence and the explicit section-policy decision.
9. Close R2C with a stock 26.2 client rendering a Helve-owned pregenerated world with zero captured world/chunk/light replay.

## Evidence classes: do not conflate them

| Evidence | What it may establish | What it may not establish |
| --- | --- | --- |
| unit/integration test | local semantic/structural invariant | vanilla parity or production performance |
| completed human source review | explicit reviewed candidate/semantic interpretation | independent source admission |
| independent source/Atlas admission | exact selected vanilla law and production implementation authorization | fastest Helve mechanism |
| hosted benchmark diagnostic | harness health, semantic equivalence, rough direction | target-hardware throughput guarantee |
| qualified target-run artifact | controlled single-process measurement with provenance | cross-process stability or automatic winner |
| cross-process report | consistent target-hardware distribution/direction | automatic performance admission |
| decision record | selected production mechanism/profile after review | future validity after a requalification trigger |

A lower evidence class never substitutes for a higher one.

## Explicitly not yet proved

Current `main` does **not** yet prove:

- independent Atlas admission/promotion of the reviewed BIOME / HEIGHTMAP / LIGHT bundle;
- production target implementation of the reviewed biome palette/wire law;
- production derived client heightmaps;
- production light ownership / light-correct import path;
- complete admitted 26.2 world-entry/chunk/block-entity/pacing/packet ordering law;
- production block-section representation selection;
- coherent full-world reference projection;
- optimized native chunk projection;
- final world-publication sequencing or target-hardware throughput;
- movement/collision/walkability;
- persistence/save/restart behavior;
- R2C milestone completion.

Those claims become valid only at their own evidence gates.
