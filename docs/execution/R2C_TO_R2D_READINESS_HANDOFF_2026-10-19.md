# Helve — R2C closure and R2D readiness handoff (19 October 2026)

**Canonical handoff for the next context.** Target: Minecraft Java **26.2**, protocol **776**, DataVersion **4903**. Repository: `JamieLittle16/Helve`; normal branch `main`. **Verified source baseline:** `9edd1cbb03707a8496081a68f5aaa11f62a92c31` (PR #409). This is a point-in-time baseline; fetch and verify the newest `main`, PRs and checks before changing code. Read this alongside `R2C_CURRENT_STATE.md`, `R2C_POST_VISUAL_PRE_R2D_AUDIT_2026-10-18.md`, and the normative architecture/qualification documents, **not** instead of them.

## Executive decision: do not start R2D as though R2C were production-ready

- **Visual/technical R2C checkpoint: ACHIEVED in a test-only stock-client diagnostic.** An unmodified 26.2 client received **25 authentic Anvil-sourced chunk columns** and visibly meshed the **central 3×3**. The extra one-chunk perimeter is present as the expected loaded/unmeshed halo. The operator removed **two genuine saved block entities using vanilla** before the successful selected empty-block-entity import; the importer did **not** discard them. The earlier nine-column case meshed only one central column.
- **Resident world ownership: substantially correct already.** `SemanticDimensionInstance` owns one authoritative `ResidentDirectory<LiveChunkSemanticState>` (one block/biome/light semantic truth, generations and revisions). The normal executable opens **one** `R2cColdWorldHost` outside the accept loop and attaches **independent per-session cursors**. PRs #389, #392, #393 and #400 cover the server lifetime, 25-column selection, checked attach and repeated physical TCP join reuse. Do **not** add a second world/chunk model.
- **Positive production publication: BLOCKED ON PURPOSE.** `R2cSourceAdmission` is uninhabited in normal builds, ordinary `WorldPublicationMode::NoChunks` remains selected, and `SourceAdmittedPlayPublisher` positive test admission is under `#[cfg(test)]`. A visual screenshot, synthetic packet equality or source-declaration hash cannot unlock it.
- **Performance freeze: OPEN.** `DirectBlockSection<u16>` remains the transparent reference; M0.3D section policy and R2C.6 projection/caching/fan-out tournament have not been selected by controlled representative target-hardware evidence.
- **R2D is a persistent, indefinitely live, repeatable *pregenerated* visible-world server**, with Helve-owned Handshake/Login/Configuration/Play, bounded resource/backpressure and no captured Play replay. **World generation is not an R2C or R2D precondition**; movement/collision, dynamic interest tracking, regionized ticking and generic block entities are later work (R3 or explicit profile expansion). See `EXECUTION_MASTER_PLAN.md` and `R2_R3_LIVE_ENGINE_ARCHITECTURE.md`.

## Source truth: what is finished vs. not finished

| Slice | Verified and reusable | Still unadmitted / next required work |
| --- | --- | --- |
| R2C generic world-state | **PR #268:** independent **58-method, 20-SEM-rule** BIOMES/HEIGHTMAPS/LIGHT source gate, promoted with zero failures | Do not repeat those 58 methods or misapply this gate to numeric loaded-biome IDs or enclosing chunk/Play packet |
| Stored-world import | Exact 26.2 Anvil/NBT bounded importer; 12,696-section / 52,002,816-block official-save differential, source receipts, 4×4×4 saved biomes, selected light, fail-closed block-entity presence | Selected real-world positive evidence + full product gates; arbitrary saved profiles and nonempty entities unadmitted |
| Biome numeric ID candidate | All **66** official loaded IDs cross-checked against byId/getId/getKey and *actually transmitted* Configuration registry entries; immutable pack-time selected-profile agreement | Independently prove the **stock client**'s selected known-packs, Configuration order, loader completion, actual registration/no partial-publication law and which registry the chunk palette uses |
| Receiving-client evidence | PRs **#401–#409** source inventories corrected, exact client `Util.sequence` empty/single/multi normal paths and operands pinned, `MappedRegistry.register` explicit early throws and dense-ID success path pinned, `registerElements` handler **and monitor** pinned, exact `Either.ifLeft`/success registry vs `ifRight`/error-map local operand construction pinned, conditional failure JDK models checked | These are **official-bytecode/source-free structural witnesses, not independent VAR/SEM admission**. Review concrete `WritableRegistry` receiver and `MappedRegistry` dispatch, `Either` effects, duplicate/exception handling, error-map finalization, chosen known packs, client palette ID consumption |
| Per-state heightmap table | Twice-reproduced official-runtime **32,366-state** candidate; first-pass four-file Java source *inspected* with source-free findings for CLIENT heightmaps, motion/solidity, fluids, leaves; 16-bit truth-table cases tested | Close reached `Fluid.isEmpty`, `VoxelShape.bounds`, `AABB.getSize/getYsize`, collision/dynamic-shape/cache/bootstrap and block special-case delegates; independent **per-state source VAR/SEM + runtime table binding**, not just a digest |
| Chunk/light/Play outer wire | Existing inner chunk/light serializers, source receipts, selected empty block-entity law candidate; client packets, Play IDs, 25-column source-backed TCP/ACK test and independent bytes at selected points | Independent exact enclosing chunk-with-light packet and IDs, heightmap/section/block-entity/light ordering/lengths, batch start/finish/ACK pacing, cache-centre and Play first-send timing; add explicit full error/delegate closure and source admission |
| Source review inventories | Post-#401 source-free archive hash-verified: **127 biome** declarations (23 declaration-only, not implementations), **44** chunk/Play declarations; PR #402 pins exact follow-up roots | Inventories are **discovery**, never runtime semantics. Stop creating new broad inventories; review exact existing roots and reached delegates |

### Review provenance / exact work already completed

- Official source archive SHA-256: `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.
- Corrected biome inventory SHA-256: `1f463c0ff1144e605053e4e0362bdfb85b08935600fbeebf78622978b588ba03` (52,888 bytes); chunk inventory SHA-256: `f02742fd0238c60417aab736dd2f9a729fdf149a537fc2881bfaedacdbafede3` (19,694 bytes).
- Human first-pass `Heightmap.java`, `BlockBehaviour.java`, `FluidState.java`, `LeavesBlock.java` facts: `R2C_HEIGHTMAP_FOUR_FILE_REVIEW_FINDINGS.md` and `vanilla/reviews/network/r2c-heightmap-four-file-source-findings.json`. **First-pass source inspection is not full delegate closure**.
- PR #409 is **merged** on `main` at `9edd1cbb03707a8496081a68f5aaa11f62a92c31` with its official-client ordering, lambda-bootstrap, CI and CLA workflows green. It distinguishes a thrown registration callback (previous entries may remain) from a per-entry *reported* error (a modeled skip may shift later dense IDs), and pins the callback field/operand shapes. The test model is **not** evidence that the real client will publish a partially populated registry.
- Keep all source-rich Mojang Java files **private/local**. Only source-free reviewed findings, exact full method/owner/signature hashes, hazard closures, VAR/SEM decisions and gate results may enter Git. The previous corrected inventory was already generated; **do not rerun broad declaration discovery** without a source drift.

## Ownership and world division — what is built, what belongs later

The authoritative path is:

```text
bounded signed Anvil regions / typed COLD parser / exact source receipts
  -> SemanticDimensionInstance<...> (one dimension/profile authority)
  -> ResidentDirectory<LiveChunkSemanticState> (sparse lifecycle boundary)
  -> owner-resolved ResidentChunkHandle / generation / semantic revision
  -> borrowed InitialChunkReference / source-admitted target projection
  -> immutable/bounded encoded output (possibly cached by exact stamp)
  -> per-client R2cChunkBatchState / observation cursor
  -> existing R2bPlaySession + single ConnectionDriver + transactional queue
```

**No packet IDs, codecs, client sessions or compression are stored in the semantic world.** Compact immutable `DimensionRuntimeProfile` facts resolve once; local world accesses must not re-hash global directories or acquire new world-global locks. The single world authority has already been built for **COLD, immutable, selected** R2C hosting.

**Not yet claimed:** R3 simulation-domain ownership, active region-cell scheduling, dense `ResolvedChunkWindow` as the default live mutation path, merge/split transfers, concurrent multi-client serving, writable block-entity gameplay, movement/collision/relighting. Preserve their boundaries, **do not build them merely to start R2D**. Region-domain authority is not the same as physical threads; later regions must transition generation/ownership without duplicating semantic chunk state. A serial `TcpListener::accept` loop is still a limitation for actual simultaneous observers; R2D should test and decide needed safe concurrency while retaining **one world and independent session state**, never a global shared mutating client cursor.

## Ordered work to reach an honest R2D GO

### P0 — finish the *remaining* R2C semantic admission

1. **Biome + Configuration client semantics.** Inspect the pinned full method bodies/reached delegates of `MappedRegistry.register/getId/byId`, `RegistryLoadTask.registerElements` and callbacks, `NetworkRegistryLoadTask.load`, `Util.sequence`, `RegistryDataLoader.load`, `SynchronizeRegistriesTask`, and `PalettedContainerFactory.createForBiomes`. Prove exact 66-entry selected known-pack/packet order, ordered futures and per-entry outcomes, finalization policy, registration IDs, client palette lookup and all reachable errors. The full fingerprints are documented in `R2C_REMAINING_SOURCE_REVIEW_BUNDLE.md`; use PRs #403–#409 actual-client evidence as supporting data. Separately audit **34 selected Configuration packet bodies**: these are from a frozen R1B *capture-derived image*. R2B **Play** packets are replay-free, but that fact alone does not make the entire product launch capture-independent. Reuse any existing source-qualified target-owned Configuration builder/artifact; do not create a parallel protocol engine.
2. **Heightmap dense state SEM.** Reuse the inspected four-file findings; close exact remaining delegate chain and state/bootstrap derivation against the 32,366-state official runtime table. The three CLIENT maps are WORLD_SURFACE, MOTION_BLOCKING and MOTION_BLOCKING_NO_LEAVES. The generic formula is already admitted; bind *each state fact* to independently reviewed source semantics, with unsupported states failing closed.
3. **Outer Play chunk/lifecycle SEM.** Review target 26.2 `ClientboundLevelChunkWithLightPacket`, `ClientboundLevelChunkPacketData`, `ClientboundLightUpdatePacketData`, `PlayerChunkSender`, the serverbound batch ACK, cache centre and first send. Qualify `block_entities = []` **only for source-verified explicitly empty saved lists**. The two entries in the operator's original outer ring were **removed through vanilla**, not lost by the importer. No general nonempty list support is required for the selected first profile.
4. **Independent admission.** Record reviewed VARs with complete owner/signature and content digests, hazards, reached delegates, semantics/error paths and human decision; use existing independent Vanilla Atlas/source gate and committed source-free admission mechanics (model after the *already completed* #268 process). Source-free inventory, client JAR shape or JDK model alone **must never promote** `R2cSourceAdmission`. Fail closed if any obligation cannot be proved. Limit to the admitted chosen Overworld/world/pack profile.

### P0 — connect admitted evidence to the *existing* product boundary

5. **Make only the admitted producer inhabitable in a normal build** after gate pass, using existing `R2cColdWorldHost`, `SourceAdmittedPlayPublisher`, `R2bPlaySession`, `ConnectionDriver` and target 26.2 codec. Remove/retain diagnostic switches behind test-only interfaces; do not add `--trust-me`, environment-authorized bypass, replayed chunk bodies, a second queue or a second world owner.
6. **Run an authentic, reproducible production client gate** with the exact clean 25-column saved-world fixture: source file checksums and original/edited provenance, source-free evidence JSON from `r2c_stock_client_diagnostic.py`, real server/client logs, screenshot/video, exact sent chunk positions/counts, cache centre, teleport confirm, batch ACKs and keepalives. Verify no protocol disconnect and an explicit negative control with no admission. The prior manual 3×3 visible observation has **not** independently established all of these counters. Check 9- and 25-column negative/positive fixture tests and malformed/missing/nonempty block entities.

### P1 — measured architecture and production hardening before R2D

7. **M0.3D section representation decision.** Use `tools/section_m03d_qualification.py`, correctness and representative population corpora, controlled target CPU, synthetic mutation+population and dimension-separated Pareto evidence; use `tools/section_policy_decision.py` to record the **human-reviewed** production winner (direct/adaptive/fast-local/packed-local or dimension-specific decision). A reference-only demo does not select the production section policy.
8. **R2C.6 projection/fan-out tournament.** Against the identical reference semantics compare full-copy, direct-to-scratch borrowed path, exact revision/target-keyed immutable output sharing and COW/finer cache only *if justified*. Include preflight double-encoding, repeated heightmap/section scans, compression, 1/2/8/32/128 subscribers, cold/warm joins, source bytes copied, allocations, RSS, p50/p95/p99/max, owner-thread tail, mutated/stale generation, tiny egress, churn and slow client. Strict bounded cache eviction; no per-block refcount/atomic/packet work in mutation HOT paths. **Choose the simplest evidence-backed whole-cost winner** and record rejected options.
9. **One-server repeated-session qualification.** Keep one resident authority while clients attach/disconnect; verify cold and warm full handshake reconnect, independent fresh cursors, shared immutable world identity, backpressure and bounded queue, rate ACK, keepalive fairness under bursts, idle/disconnect resource release, failure isolation and graceful shutdown. Existing two physical localhost joins are **after the R2B handoff** and are not a complete full-protocol reconnect or indefinite liveness test. Concurrent clients remain a new design/qualification decision; reuse existing I/O owner rules.
10. **Source and docs cleanup.** Remove or clearly label stale pre-#389 per-connection world-import comments and superseded PR #401 inventory labels; preserve benchmark losers as experiments and record actual gate/PR/CI hashes. Inspect performance and memory before claiming the stage is done; never replace tested code just for architectural aesthetics.

## R2C exit / R2D entry gate — all must be demonstrably true

- [ ] Production `R2cSourceAdmission` exists **only for a fully VAR/SEM-admitted selected 26.2 profile**; independent Atlas/source gate green.
- [ ] Real non-test stock 26.2 client receives selected pregenerated world from **Helve semantic state**, no captured chunk/light Play replay, complete protocol/Configuration ownership truth honestly recorded.
- [ ] Correct 25-source halo and expected central visible neighborhood, empty-BE policy fail-closed, stable x/z/Y/biomes/light/heightmaps and complete batch/ACK + teleport + keepalive evidence.
- [ ] One server-lifetime dimension authority survives repeated full joins; each session has separate bounded observation and egress; no second mutable chunk authority.
- [ ] No unbounded memory/queue, no stale generation/revision publication, malformed input and slow client fail closed; source-reproducible ordinary reconnect test green.
- [ ] M0.3D production section policy and R2C.6 projection choice recorded from controlled target-hardware performance/whole-cost evidence, or explicit measured choice to retain the simple baseline.
- [ ] Every relevant qualification/test and CI source-profile check green on a named `main` head, with verified stock client logs, saved-world provenance and numbers; remaining limitations documented.

When the gate is met, **R2D** extends the *existing* production publisher to indefinite liveness, deterministic full reconnect, sustained server-resource/backpressure testing and repeat joins that reuse immutable target/world work. It is **not** an instruction to rewrite R2C or implement an R3 scheduler.

## First action for the next context

1. `cd /home/Jamie/Crucible && git pull --ff-only && git status --short && git rev-parse HEAD`; read this handoff and `R2C_CURRENT_STATE.md`; verify any newer merged work and CI.
2. Work in **parallel bounded tracks**: (A) biome/Configuration VAR/SEM and receiving-client concrete registration/failure, (B) heightmap predicate delegates, (C) outer packet/lifecycle; (D) independent section+projection performance qualification. Keep disjoint files/PRs, do not race on the same review inventory or root document.
3. Aim first for an independently reviewed *source-free* admission dossier and gate, **not** a tenth broad client discovery pass. Use the already verified review bundle and private local official source/Atlas only where needed. Do not upload/commit Mojang source-rich excerpts.
4. After independent admission, merge a **separate** minimal ordinary-server publication PR, verify real client product behavior, then qualify representative performance and R2D-specific sustained/reconnect behavior.

### Normative references

- `docs/architecture/R2C_WORLD_PROJECTION_IMPLEMENTATION.md`, `R2_R3_LIVE_ENGINE_ARCHITECTURE.md`, `OWNERSHIP_SIMULATION_CONTRACT.md`, `R2_R3_PERFORMANCE_SEARCH_PLAN.md`, `R2_R3_PERFORMANCE_DECISION_REGISTER.md`.
- `docs/execution/R2C_CURRENT_STATE.md`, `R2C_EXECUTION_PLAN.md`, `R2C_POST_VISUAL_PRE_R2D_AUDIT_2026-10-18.md`, `EXECUTION_MASTER_PLAN.md`, `R2C_STOCK_CLIENT_DEMO_RUNBOOK.md`.
- `docs/qualification/R2C_REMAINING_SOURCE_REVIEW_BUNDLE.md`, `R2C_BIOME_ID_SOURCE_FRONTIER.md`, `R2C_CLIENT_ORDER_SEMANTIC_FRONTIER.md`, `R2C_CLIENT_LAMBDA_BOOTSTRAP_FRONTIER.md`, `R2C_HEIGHTMAP_FOUR_FILE_REVIEW_FINDINGS.md`, `R2C_CHUNK_WIRE_SOURCE_FRONTIER.md`, `R2C_BLOCK_ENTITY_IMPORT_GATE.md`, `R2C_SELECTED_BIOME_RUNTIME_ID_PREFLIGHT.md`, `section/SECTION_M03D_FINAL_QUALIFICATION.md`, `PERFORMANCE_QUALIFICATION_STANDARD.md`.

**Helve principles are binding:** vanilla-faithful externally; internally different, efficient and clean; static monomorphized HOT paths; one semantic authority; modularity when it does not degrade performance; no redundant parser/queue/registry/owner/cache; fail-closed exact source truth; benchmark before freezing complexity.
