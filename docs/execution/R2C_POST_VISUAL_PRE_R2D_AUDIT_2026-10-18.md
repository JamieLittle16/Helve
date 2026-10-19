# R2C post-visual audit — pre-R2D closure (18 October 2026)

Baseline: `093ae2cee68c86706beebaeb6986d5c088d62e57`; official Minecraft Java 26.2, protocol 776, DataVersion 4903.

**Current closure/readiness status (19 October 2026):** [R2C → R2D readiness handoff](R2C_TO_R2D_READINESS_HANDOFF_2026-10-19.md) supersedes this document for PR #389–#409 progress and the R2C exit checklist. Keep the original 18 October findings as historical evidence; in particular, no normal-path per-session Anvil import remains, but production positive chunk publication and independent remaining VAR/SEM are still blocked. The post-#409 client callback verification is *source-free structural evidence*, not final admission. R2D remains a **pregenerated-world persistent liveness/reconnect** stage; world generation is not required for entry.

**Historical audit update (PR #389, 18 October):** The ordinary
executable now creates a single nonpublishing COLD `R2cColdWorldHost`
before the accept loop and reuses its resident directory/receipts across
sequential client lifetimes, with a fresh client batch cursor. The
per-connection import finding below describes the *pre-PR #389* baseline
and still applies to the isolated ignored stock-client diagnostic.
Source-admitted Play publication, concurrency and R3 active region ownership
remain open. See `R2C_CURRENT_STATE.md` for the authoritative current ledger.

**New manual evidence:** user reports a successful test-only native 25-source-chunk join: the center 3×3 chunk columns are visibly rendered in unmodified Minecraft; the surrounding ring is loaded but unmeshed, matching the expected neighbor dependency. This proves real visible terrain from the Anvil-backed Helve pipeline, not complete VAR/SEM production admission or measured multi-client throughput. The two offending block entities in the extended halo were removed using vanilla before the successful test. Archive exact world/client/source hashes, screenshot, complete server log and accepted batch/teleport/keep-alive status separately; visual success alone does not certify those counters.

## Architecture findings

- **Single semantic chunk truth (good):** `SemanticDimensionInstance` uses one `ResidentDirectory<LiveChunkSemanticState>` with blocks, biomes and imported initial light. The directory owns generation; the chunk owns one block/biome revision clock; stale handles fail closed. No target-packet state enters the world core. Keep these abstractions.
- **Source and receipts (good, selected scope):** the bounded `world_files` importer reads each signed region once, streams typed NBT to one resident installer, and records exact `SourceChunkPublicationReceipt` checks. Missing and nonempty saved block-entity lists still reject for the selected profile.
- **Publication and connection (good):** direct borrowed `InitialChunkReference`, target-26.2 candidate encoder, one scratch buffer and `R2cChunkBatchState` reuse the retained R2B `ConnectionDriver`. Queue admission is transactional, with 20Hz paced quota and ACK. No second queue or client-owned chunk representation is necessary.
- **Not final server-wide ownership:** `serve_r2b_playtest_with_optional_r2c_plan` instantiates `ColdImportedView` inside the connection. The demo has one authority *per session*, but the production server must open one dimension independently of clients and share immutable publications, not reload or clone the world on each join. `main.rs` presently serves accepted connections serially.
- **Still test-only:** `R2cSourceAdmission` is uninhabited outside tests; the ordinary `--r2c-world-plan` path audits without publishing chunks. Unclaimed Play frames are discarded in an intentionally incomplete test loop. Never use an environment flag to make this production-authorized.
- **Selected Configuration input is capture-derived:** `tools/r2b_pack_playtest.py` obtains the 34 source-validated Configuration bodies from the frozen R1B capture/image; the R2B **Play** bootstrap is replay-free. For R2D's stated *full Helve-owned Handshake/Login/Configuration/Play* requirement, audit whether those Configuration artifacts are truly immutable admitted target-profile definitions or still require native construction. Do not falsely call the entire launch capture-independent merely because no captured **Play** bodies are sent. Reuse any existing admissible target-owned Configuration composer rather than creating a second registry/protocol engine.
- **Reference storage is not production policy:** the demo uses `DirectBlockSection<u16>`. Its 25 columns × 24 full-height sections × 4096 × 2 bytes give **4,915,200 bytes** just for block-cell arrays, excluding all other memory; this is a structural estimate, not benchmark RSS. Four already-qualified M0.3D candidates are `direct`, `adaptive`, `fast-local`, `packed-local`; no final winner is recorded.
- **Repeat work:** the demo preflight encodes all candidate chunks and later encodes them again during sending. Each `InitialChunkReference::derive` builds heightmaps; each section palette is built from an owner-local 4096-cell scan. This is acceptable as a COLD diagnostic but must be measured and improved for shared production fan-out, without moving work into ordinary mutation HOT paths.
- **Do not redo proven optimizations:** packed-import performance work already rejected word-major unpacking and selected a 256-byte-table CRC32 mechanism after same-run whole-decoder improvement. Residual NBT/packed-cell work needs further decomposition before rewrite.

## Work in dependency order

### P0: evidence and source-law correctness

1. Freeze the authentic 25-chunk demo save, exact original-versus-edited provenance, visible screenshot/video, client/server logs, region checksums, R1B commitments and the candidate heightmap SHA. Preserve a nine-source-chunk test, full halo test, missing/unsupported-entity negative cases and an absent-publisher negative control. Confirm real keep-alive and batch-ACK output; do not infer from pixels.
2. Reuse the **already admitted** 58-method BIOMES/HEIGHTMAPS/LIGHT world-state gate. Finish the *remaining* selected receiving-client/known-pack biome ordering law (issue #285), the 32,366-state heightmap predicate lookup's independent source binding (the generic heightmap predicates are already admitted), and the enclosing client/server 26.2 chunk/light + initial cache-centre + batch ACK + Play lifecycle VAR/SEM. Use independent client-format byte vectors, not only a symmetric encoder/decoder round trip.
3. Admit the exact chosen Overworld/biome/pack/source profile with fail-closed version/schema/receipt/registry checks, before making the test-only R2C publication capability inhabitable in the **non-test** build. No support for arbitrary saves or nonempty block entities is implied.
   Audit the 34 selected Configuration bodies' capture-derived provenance against R2D's full Helve-owned session requirement. A source-qualified immutable target-profile artifact may be appropriate, but a replay-dependent Configuration shortcut is not a substitute for independently admitted product semantics.

### P0: permanent ownership boundary

4. Move the semantic world lifetime outside the connection handler. A server-owned `SemanticDimensionInstance`/resident directory is authoritative; compact per-client interest/observation and `R2bPlaySession` are not world owners. Retain existing importer, receipts, stamps, target encoders, transactional egress and control prioritization. Do not introduce a global world mutex in block HOT paths or preemptively implement a region scheduler.
5. Wire the normal executable to a fully admitted, bounded R2C producer that renders a pregenerated selected world with zero captured chunk bodies. Keep the ignored stock-client path as a regression fixture and quarantine demo-only discard/logging/candidate-input options.

### P1: qualified efficiency (before freezing R2D production shape)

6. Finish existing M0.3D controlled target-machine synthetic+real-section-corpus Pareto chain using `section_m03d_qualification.py` and human-reviewed `section_policy_decision.py`. Measure CPU, p50/p95/p99/max, release correctness, resident bytes/RSS, allocations and mutation/transition tails. Statically bind the selected production section storage and its Anvil builder; retain direct reference semantics.
7. Run R2C.6 projection tournament: (a) full-copy reference `PublishedChunk`, (b) current borrowed direct-to-scratch projector, (c) exact revision/target-keyed immutable encoded artifact cache/shared send, (d) more granular/COW variant **only if** measured. Benchmark cold/warm join, 1/2/8/32/128 observers, stale revision, slow client, single edit, join bursts, compression, copied bytes and owner-thread p99. Select the simplest whole-cost winner with bounded cache and exact freshness.
8. Benchmark and red-team importer grouping, live resident access, decompression/CRC, section builder, scratch/retry and all packet limits. Tune only documented bottlenecks; ensure no HOT allocation, repeated global lookup, per-block refcount increment or source-unstable cache key.

### P1: product hardening / handoff

9. Test authentic multi-session same-world reuse, repeated clean join/disconnect, keep-alive fairness under chunk bursts, malformed and stale input, slow-client backpressure, reconnect, tiny egress, partial import and shutdown. Record per-client queue bound, memory/RSS, p99/p99.9/max and exact source/projection digests. At least the R2A long-idle gate and initial repeat-join evidence must exist; R2D then extends indefinite/reconnect product red-team.
10. Update `R2C_CURRENT_STATE.md`, old source-frontier statuses and user runbook to distinguish *manual visual achieved* from *production source admitted* and *performance qualified*. Avoid duplicate codecs, world owners, packet queues, parsers and misleading legacy TODOs.

## Scope boundaries

**Do not block narrow R2C on:** general nonempty block-entity serialization, arbitrary DataVersion/datapack support, world generation, movement/collision authority, dynamic chunk interest, full relighting or regionized parallel simulation. These are separately qualified later capabilities (broad world support and R3A–R3D). Preserve extensible typed sidecars and existing source gates rather than silently dropping their data.

**R2C pre-R2D GO:** real non-test selected world renders; one authoritative server-owned dimension spans sessions; source/VAR/SEM and reference bytes admitted; section and projector production choices evidence-qualified; bounded memory/egress/freshness/repeated-join tests green. Otherwise remain on R2C. **R2D** is qualification of a persistent *pregenerated* visible world under indefinite liveness and reconnects, not automatically a world-generation milestone.

All material choices remain governed by `docs/architecture/R2C_WORLD_PROJECTION_IMPLEMENTATION.md`, `docs/architecture/R2_R3_LIVE_ENGINE_ARCHITECTURE.md`, `docs/architecture/OWNERSHIP_SIMULATION_CONTRACT.md`, and `docs/qualification/PERFORMANCE_QUALIFICATION_STANDARD.md`.
