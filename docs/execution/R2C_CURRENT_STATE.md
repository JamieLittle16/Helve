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
- one whole-chunk `ChunkRevision` coherence baseline shared by block and biome mutation, also used to invalidate any attached imported light after real changes;
- atomic same-driver publication admission and allocation-free one-body publication progression;
- independently promoted source-free source admission for 58 reviewed world-state methods and 20 biome/heightmap/light SEM rules (PR #268);
- a one-command local runner retained to reproduce the independently admitted source boundary;
- source-law heightmap recomputation oracle with no extra HOT mutation bookkeeping (reference projection input; generated 26.2 predicate facts and coherent ownership remain pending);
- target-neutral, immutable initial light layers with exact nibble semantics and bounded sentinel-section ownership;
- source-admitted one-pass persisted NBT light extraction alongside exact block-section import (#272);
- cold source-to-semantic light composition into a dimension-bound initial-light column with no per-cell copy (#273);
- one coherent resident chunk ownership mode over the *existing* sparse directory and generation allocator (#274);
- transactional imported-block, explicit biome and source-light admission into that one coherent resident owner (#275);
- source-law initial light mask classification reference (#276);
- exact schema-directed source quart-biome palette decoding in the existing Anvil NBT pass (#277; full source-biome differential/registry binding still pending);
- strict no-default COLD composition of those saved biome sections into coherent resident dimension lattice (this PR; target registry and Play projection pending).

The selected BIOMES / HEIGHTMAPS / LIGHT semantic source boundary was independently admitted and promoted in #268 (main commit `3e5fe9b`). It authorizes implementation, **not** a completed runtime behavior. Target-generated heightmap predicate facts, target biome registry binding/official differential, packet projection and remaining world-wire groups remain separate engineering gates.

The remaining world-publication groups outside the completed BIOMES / HEIGHTMAPS / LIGHT review also remain independently unadmitted: world-entry ordering, chunk-span/batch state, block-section publication law not already covered by admitted lower layers, selected block-entity publication, pacing/acknowledgement and exact packet identities.

```text
admitted BIOME / HEIGHTMAP / LIGHT semantics (#268)
        ↓
heightmap reference + exact target facts; imported light primitives
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
| R2C.1 world-state source review | **INDEPENDENTLY ADMITTED AND PROMOTED (#268)** | BIOMES, HEIGHTMAPS and LIGHT: 58 required reviewed methods, 20 admitted SEM rules, zero gate failures. Target semantics are authorized for implementation, but the admission record explicitly states that runtime behavior is not implemented. Other world-wire groups remain unadmitted. |
| R2C.1 remaining world-wire review | **PENDING** | World-entry, chunk-span, selected block-entity, pacing/acknowledgement and exact packet-identity/order law still require bounded source admission. Existing lower-layer block-section evidence may be reused only where its admitted claim exactly matches the R2C route. |
| R2C.2 resident-world substrate | **BLOCK AND COHERENT RESIDENT MODES LANDED (#274)** | `DimensionInstance` supplies block-only lifecycle. `SemanticDimensionInstance` reuses the exact same generic sparse directory for a coherent block/biome/initial-light payload, allocating the generation inside atomic admission and checking exact dimension lattice and pristine revision. One chosen mode owns each dimension; no parallel directory or separate clock. |
| R2C.2 whole-chunk freshness | **BLOCK + BIOME COMPOSITE AND INITIAL-LIGHT ATTACHMENT LANDED** | `LiveChunkSemanticState` owns one shared revision. The new optional imported-light component is accepted only for exactly matching chunk position/generation/lattice at revision zero, and becomes unavailable after any real block or biome mutation without extra HOT invalidation operations. No secondary revision, dynamic dispatch or network-shaped state is introduced. |
| R2C.2 resident qualification | **CORRECTNESS/HOSTED DIAGNOSTICS LANDED; TARGET PERFORMANCE ADMISSION SEPARATE** | Lifecycle/HOT-path qualification and the official-save import-through-residency path are green. Hosted timing is diagnostic only. |
| R2C.2S block-section production policy | **DECISION PIPELINE LANDED; REAL EVIDENCE/POLICY NOT FROZEN** | Direct, adaptive-local, fast-local and packed candidates are correctness-qualified. M0.3D/issue #19 has the complete measurement/Pareto/policy machinery; the remaining work is real four-seed population evidence, exact-revision correctness sealing, controlled physical target-hardware runs and the explicit reviewed winner/loser record. `SEC-REF-DIRECT` remains reference-only. |
| R2C.3 pregenerated-world block import | **LANDED AND GENUINE-SAVE DIFFERENTIAL GREEN** | Bounded Anvil framing, DEFLATE, schema-directed NBT, exact persisted-state resolution and final section construction are on `main`. Independent official-save comparison covers 12,696 block-bearing sections / 52,002,816 block cells exactly. |
| R2C.3 import → residency qualification | **BLOCK PATH + COHERENT THREE-COMPONENT INSTALL LANDED; SOURCE BIOMES IN REVIEW** | Genuine official save passes validated region read → bounded decompression → semantic block import → final section construction → `DimensionInstance` residency with exact evidence identity. The new `install_imported_semantic_chunk` reuses one section assembler and one resident directory, accepts explicit caller-resolved biome sections, and composes saved light with the allocated incarnation under atomic admission. Full official source biome import remains pending. |
| R2C.3 selected cold-import mechanisms | **LANDED** | Byte-table gzip CRC32 and four-bit packed-state specialization crossed semantic + benchmark qualification. Generic five-bit-and-wider packed decoding remains intact and regression-covered. |
| R2C.4 biome semantics | **TARGET-NEUTRAL STORAGE + ONE-PASS SAVED-BIOME CODEC LANDED (#277); DIMENSION INSTALL IN REVIEW** | One 64-sample biome lattice per logical section is live under static storage. A statically selected persisted-biome codec now resolves exact resource-name palette entries, uniform and non-spanning 1–6-bit quart packed storage in the existing block/light NBT pass; unknown identities and absent source columns never become fabricated Plains. This PR adds a bounded source-order-to-numeric-ID resolver with once-per-loading-session sorted-index construction, borrowed exact keys and no per-cell registry lookup. A **qualified complete 26.2 registry order** and independent official-save biome differential still need to be supplied before target parity can be claimed; network palette encoding remains pending. |
| R2C.4 heightmap semantics | **SEM ADMITTED; RECOMPUTATION + PACKED-LONG REFERENCE IN REVIEW; TARGET FACTS PENDING** | A stamped reference computes all three exact client maps from authoritative blocks in one descending pass per column. The new immutable reference packs each 256-entry map using ceil(log2(height+1)) non-spanning long storage with exact client type IDs 1/4/5 and whole-chunk freshness, without a live cache or secondary clock. Generated 26.2 block-motion/fluid/leaves predicates and remaining world-wire projection are still missing. |
| R2C.4 light semantics | **SEM/ONE-PASS IMPORT + COLD COMPOSITION LANDED** | `LightDataLayer` preserves homogeneous versus packed 2048-byte layers and exact 4-bit YZX indexing; `InitialChunkLight` already binds to the coherent owner with one revision. The statically specialised importer from #272 captures `isLightOn` and `BlockLight`/`SkyLight` without parsing NBT twice. The new COLD adapter consumes their bytes into the validated dimension-bound initial-light column. Coherent resident-world installation is now available; live relighting and Play projection remain pending. |
| R2C.5 reference projector | **PENDING R2C.4 + REMAINING WORLD-WIRE ADMISSION** | Must consume one coherent semantic chunk state and remain the permanent correctness/freshness oracle before projection optimization. |
| R2C.6 production projector | **PENDING REFERENCE PATH + MECHANISM EVIDENCE** | Cache/snapshot/layout choices remain a mechanism tournament. No network-shaped second world representation may become live truth. |
| R2C.7 same-driver publication | **TRANSPORT/FAIRNESS SUBSTRATE LANDED; PROJECTOR INTEGRATION PENDING** | Internal server composition admits already target-encoded bodies through the exact continuing `ConnectionDriver`. Atomic batches reuse transactional queue admission; large ordered publications reuse the generic one-word `PublicationCursor`. Backpressure advances neither egress transaction state nor cursor progress. There is no second queue/socket or public raw-packet injection API. |
| R2C.8 stock-client native world | **MILESTONE EXIT** | Complete only when an unmodified 26.2 client renders Helve-owned terrain with zero captured world/chunk/light replay. |

## Biome registry binding gate

A biome's compact numeric ID is its **source registry ordinal**, not its alphabetical resource-key rank. `OrderedBiomeRegistry` binds the exact source order supplied by a caller and constructs one COLD lexicographically indexed lookup table without duplicating key strings. It requires DataVersion 4903 and rejects empty, malformed, duplicate or oversized registries. The saved-biome palette decoder consumes this binder directly as its `BiomeStateResolver`, so resolved sections retain numeric IDs without a HOT lookup. The constructor validates input **shape**, not origin: the complete Minecraft 26.2 runtime registry order still needs an independent extraction, pinned content hash and source-grounded acceptance evidence. Do not imply that the synthetic test input or a registry whose names merely happen to match is a source-qualified target list.

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

These claims were independently source-admitted in #268. This **authorizes implementation only**: generated target state facts, in-memory light semantics and complete world-wire projection must still be implemented and tested.

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

PR #268 promoted the independently verified source-free artifact to `main`. The following command remains a **reproduction path**, not an unfinished milestone:

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

The admitted bundle is present under `vanilla/records/network/r2/world-state/`, `vanilla/semantics/network/` and `vanilla/reports/`. The remaining wire families must not inherit authorization from this narrower gate.

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

1. Complete generated 26.2 heightmap predicate facts against admitted source data, then differential-qualify the new recomputation oracle; do not infer motion/leaves/fluid from section counts.
2. Bind the source biome name resolver to a validated 26.2 registry snapshot and qualify genuine-save biome differential end to end through the new no-default coherent resident installer; do not introduce a second map, clock, synthetic biome image or double parse.
3. Integrate the complete heightmap/biome/light view into one authoritative chunk projection snapshot without introducing network-shaped live state.
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

- runtime NBT import, complete relighting/refresh and end-to-end client qualification of the already admitted BIOME / HEIGHTMAP / LIGHT SEM bundle;
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
