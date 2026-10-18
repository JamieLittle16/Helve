# R2C Current State — Demo-First Ledger

**As of:** 18 October 2026  
**Verified `main` baseline:** `8ffc05b8828b7a1440abcabc41b8c3e0f3bf9c0e` (PR #375)  
**Target:** Minecraft Java 26.2, protocol 776, DataVersion 4903  
**Milestone state:** **NOT YET DEMONSTRATED IN THE UNMODIFIED STOCK CLIENT**  
**Next action:** [R2C stock-client demo runbook](R2C_STOCK_CLIENT_DEMO_RUNBOOK.md)

This is the canonical *current* implementation/qualification ledger. Older
per-slice handoffs and candidate-frontier documents record the history of
individual investigations; they do **not** override later merged admissions,
implementations or CI results. Git history retains the earlier detailed ledger.
Do not restart a closed source-review family based on an old pending note.

## Source admission — already completed

PR #268 independently admitted and promoted the R2C **world-state**
BIOMES / HEIGHTMAPS / LIGHT source bundle: **58 reviewed methods, 20
SEM rules, zero gate failures**. The canonical committed files are:

- `vanilla/gates/network/GATE-NET-R2C-WORLD-STATE-26_2-001.json`
- `vanilla/semantics/network/R2C_WORLD_STATE_SEMANTICS.md`
- `vanilla/reports/r2c-world-state-source-admission-26.2.json`
- `vanilla/reports/r2c-world-state-admitted-bundle-manifest.json`

The manifest explicitly states
`source_admitted=true` and
`production_implementation_authorized=true`, while preserving
`runtime_behavior_implemented=false` **at the evidence-promotion
boundary**. That last historical field does *not* undo the subsequent
runtime implementation and differential tests. It is not a live
status field for the server.

**Do not request a second source review of the same 58 methods or
treat the generic world-state predicates as unadmitted.** Their
concrete 32,366-entry official-runtime state-ID table is separate:
its SHA-pinned byte candidate and tests exist, but it has not been
promoted as an independent source-admitted production table.

## Verified implementation — reuse, do not duplicate

| Slice | Current result | What is *not* implied |
| --- | --- | --- |
| R2B stock-client entry | Replay-free Configuration/Play, retained `R2bPlaySession`, teleport, keep-alive and single bounded driver already landed | A visible R2C world |
| Stored-world ingestion | Real 26.2 Anvil/NBT block import, 12,696-section / 52,002,816-block official-save differential, one coherent resident owner, saved 4×4×4 biome import and light ownership | Every possible external save/profile |
| World-state SEM | 58-method independent source-gate promotion; three source-defined heightmaps, biome palette law and light-mask law reviewed | Automatically generated, source-admitted state-ID bits |
| Biome ID agreement | All 66 loaded official biome IDs cross-checked directly against the pinned runtime's `byId/getId/getKey` and the Configuration stream; selected R1B image checked ordinal-by-ordinal | Receiving-client known-pack and registry-registration SEM fully admitted |
| Heightmap data | Twice-reproduced official runtime 32,366-state candidate; frozen dense SHA; bounded, fail-closed COLD consumer; receipt-bound projected heightmaps | Full per-state source/VAR/SEM closure for production |
| Chunk/light projection | Existing reference section, heightmap, biome and light serializers; selected block-entity list explicitly empty in the tested profile; nine chunk bodies audited | General block-entity or arbitrary-world support |
| Same-driver delivery | R2C cache centre, batch start/finish, chunk-with-light, quota, ACK and 20 Hz service already implemented; retained socket-loop test (PRs #373–374) | An unmodified stock client has rendered terrain |
| Play IDs | Five R2C positions bound against nine *already reviewed* R0 builder/dispatch VAR laws, 141/69 client Play registration census, zero-indexed bundle law (PR #375) | Full outer Play lifecycle admission |
| Product R2C publication | `R2cSourceAdmission` is **uninhabited** outside Rust tests; production passes `None` to the existing publisher | Publication is not activated merely by CLI flags |

**Most important integration result:** PR #374 sends nine genuine
Anvil-*formatted test fixture* chunks spanning four region files through
the **original retained Play TCP loop**, verifies their frame bodies
and serverbound rate ACK over localhost, and checks original driver/egress
ownership. This is considerably beyond a mocked serializer test.
However, its receiving peer is a synthetic client and its positive source
witness exists **only under `cfg(test)`**. The fixture is not proof of
a complete real pregenerated-world stock-client join.

## Precisely what is still between us and the demo

1. **Select one exact compatible pregenerated 26.2 save/profile and
   client session.** Confirm the actual existing `level.dat`, namespaced
   Overworld region files, source position/empty block entities,
   light-correctness, selected packs/biomes and source-receipt coverage.
   The current CLI already admits a *non-publishing* COLD import/audit.
2. **Close only residual *selected* receiving-client and outer-Play
   obligations.** Reuse the world-state 58-method gate, R0 packet-ID
   builder VAR/SEM and the frozen runtime/capture cross-oracles. The
   source-free client order/known-pack probe and Play lifecycle first-pass
   inventories remain review leads, not automatic R2C VAR/SEM admission.
   Write a minimal missing-method/branch inventory; do not rebuild the
   heightmap, registry parser, client builder or world importer.
3. **Wire the existing publisher through the product boundary *only after*
   the selected remaining source/VAR/SEM and world-profile gate passes.**
   In production `serve_r2b_playtest_with_r2c_cold_plan` currently
   passes `None` to `serve_world_projection_wait`; never bypass the
   uninhabited witness with an environment variable, unchecked feature
   or an asserted boolean.
4. **Run the first actual stock-client experiment** with unmodified 26.2,
   the one admitted pregenerated save, zero captured Play world packets,
   and the existing R2B-to-R2C driver. Preserve logs, packet counts,
   exact save/runtime/commit identities and a screen/video of rendered
   terrain. Keep a negative test that proves removal of the chunk
   publisher prevents the demo from passing.

The **only** milestone exit is *unmodified stock-client renders Helve-owned
pregenerated terrain while the same connection remains live*. No
Rust test, JVM bytecode hash, capture digest or simulated ACK alone
meets that exit.

## Demo-ready actions, in order

See `R2C_STOCK_CLIENT_DEMO_RUNBOOK.md` for exact commands and
observations. The steps are ordered deliberately:

1. Start from the green, verified main commit and reconfirm the
   admission bundle using the already existing verifier.
2. Run the existing official Java 25 heightmap job and
   `nine_disk_chunks_cross_four_regions_and_reach_one_receipted_batch`
   with the *actual* candidate table. Preserve the source-free outputs.
3. Validate the actual demo save and R2B image through the **existing**
   CLI's `--r2b-playtest-image`, `--r2c-world-plan` and optional
   `--r2c-heightmap-candidate` flags. **Today this is COLD and never
   sends chunks**; treating it as a visual demonstration would be false.
4. Resolve the bounded final source/selected-profile gap, activate the
   existing `SourceAdmittedPlayPublisher` without duplicating the
   network/world owner, then perform the stock-client visual gate.

## Performance policy: between the R2C demo and R2D

For the **first constrained R2C demo**, prefer the already-correct
transparent/reference projection and bounded existing transport over a
speculative whole-path optimisation. Preserve ownership, safety,
backpressure and reasonable finite resource caps now; do not make the
demo depend on winning a cache/SIMD/COW/storage tournament first.

After a *successful visible demo*, but **before committing to the
broader R2D production-performance profile**, undertake the
M0.3D section-policy choice, R2C.6 mechanism tournament,
initial-view/cached-chunk sharing, reduced copies/allocations, import
throughput, controlled target-hardware p99/tail measurements, and any
necessary modular cleanup. Use the established qualification standard:
reference equivalence first, target-hardware measurements second,
and a retained decision record. Do not retroactively label a
reference-only demo path a fully qualified production-performance winner.

**R2D world generation is not a prerequisite for R2C.** Future
movement/gameplay, indefinite operation, relighting beyond the
selected source-light profile, arbitrary datapacks and broad-world
compatibility are not part of the finite initial visual checkpoint.

## Admission labels must remain precise

- `source_admitted` for the **world-state 58-method gate**: **true**.
- Numeric Play-ID composition: checked against admitted R0 generic
  laws; separate remaining Play lifecycle gates must not be conflated.
- Client biome ordered-profile / dense heightmap runtime facts:
  **strong cross-oracle candidates**, with distinct remaining source
  admission obligations.
- Production live R2C publication: **false** on this baseline.
- Stock-client visible world: **not yet demonstrated**.

If a future PR changes one of these statuses, update *this* ledger,
link the exact new evidence, and delete or qualify the superseded
pending statement. No additional progress report should present
already merged source laws as an unsolved starting point.
