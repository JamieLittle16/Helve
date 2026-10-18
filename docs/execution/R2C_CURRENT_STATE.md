# R2C Current State — Demo-First Ledger

**As of:** 18 October 2026  
**Post-visual audited `main` baseline:** `093ae2cee68c86706beebaeb6986d5c088d62e57` (PR #387)  
**Server-lifetime COLD owner merged:** `c9a03549c4de915129591c693a36b8960e7445bb` (PR #389; normal server path, nonpublishing)  
**Follow-on ownership improvements merged:** PR #392 (allocation-free checked session attach) and PR #393 (25-source server-host selection), on `main` at `437ca9a532906412c3620d605b99f9d799b22ef8` before this qualification.  
**Target:** Minecraft Java 26.2, protocol 776, DataVersion 4903  
**Milestone state:** **VISUAL TEST-ONLY CHECKPOINT ACHIEVED: 25 real Anvil chunks sent, central 3×3 visibly rendered in the unmodified stock client; production source admission and optimized product integration NOT YET CLOSED**  
**Next action:** [Post-visual architecture audit and pre-R2D closure plan](R2C_POST_VISUAL_PRE_R2D_AUDIT_2026-10-18.md) and [stock-client runbook](R2C_STOCK_CLIENT_DEMO_RUNBOOK.md)

This is the canonical *current* implementation/qualification ledger. The detailed
post-visual closure plan is linked above. Older
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
| Same-driver delivery | R2C cache centre, batch start/finish, chunk-with-light, quota, ACK and 20 Hz service implemented; subsequent ignored stock-client test published real source chunks | Source-admitted normal product server publication |
| Play IDs | Five R2C positions bound against nine *already reviewed* R0 builder/dispatch VAR laws, 141/69 client Play registration census, zero-indexed bundle law (PR #375) | Full outer Play lifecycle admission |
| Product R2C publication | `R2cSourceAdmission` remains **uninhabited** outside Rust tests, even after the stock-client proof; production passes `None` to the existing publisher | Publication is not activated by CLI flags, source save selection or live-client observation |

**Historical pre-visual integration baseline:** PR #374 sends nine genuine
Anvil-*formatted test fixture* chunks spanning four region files through
the **original retained Play TCP loop**, verifies their frame bodies
and serverbound rate ACK over localhost, and checks original driver/egress
ownership. This is considerably beyond a mocked serializer test.
However, its receiving peer is a synthetic client and its positive source
witness exists **only under `cfg(test)`**. The fixture is not proof of
a complete real pregenerated-world stock-client join.

## Post-visual server ownership integration (PR #389)

The ordinary server executable now prepares one source-checked **COLD**
`R2cColdWorldHost` **before accepting connections**. It holds one immutable
`SemanticDimensionInstance` and the original source receipts, shared across
sequential R2B client lifetimes. Each client attaches only a fresh
`R2cChunkBatchState`; no Anvil re-import or candidate re-encode audit occurs
at each ordinary join. Its pending teleport must pass the same
finite/lattice/signed-coordinate first-view planner and match the hosted view.

The pinned nine-Anvil-chunk regression exercises two independent session
attachments to exactly the same resident and receipt allocations, a mismatched
teleport rejection, and independent batch cursors. PR #389's CI, R0 server
gate and official heightmap facts workflow were green at reviewed head
`eed6bcedfbb43b155f8f16e87c4e775595f3f592`.
The public legacy per-connection world import entrypoint was removed.

**Selected visible halo adjustment (post-PR #392):** The ordinary server-owned
COLD host now selects the same **25** genuine source positions as the
successful 5×5 stock-client renderer-halo diagnostic, rather than the old
nine-column reference selection. The original nine-column importer remains
only for existing finite reference/diagnostic regressions. The central 3×3
still represents the demonstrated mesh-ready neighborhood, not a claimed
25-column visible world. This changes only up-front source import cost and
resident COLD shape; **ordinary Play chunk publication remains disabled**
and no optimized storage-policy or source/VAR/SEM admission is implied.

**25-source ownership regression (follow-on qualification):** A hermetic
four-signed-region, 25-Anvil-column test uses the already existing
`WorldFixture`, bounded typed import, complete nearest-first receipt
ordering and the actual `R2cColdWorldHost` shared-attacher boundary. It
checks two independent Play sessions reuse the exact same resident and
receipt allocations with fresh, unadvanced cursors. Removing a required
source region after hosting cannot affect already resident attachments;
a *new* import must fail closed, without queueing Play data. This test
uses the existing uncompressed test-only Anvil writer and does **not**
substitute for a product startup test on an actual 26.2 save, a target
hardware result, or the source/VAR/SEM publication gate.

**Scope is deliberately limited:** this is a server-lifetime
**immutable COLD world**, not a writable region-owned simulation executor.
`TcpListener::accept` still serves client connections serially, the opted-in
25-source-chunk *stock-client diagnostic* still imports in its isolated
test-only route, and the ordinary executable still cannot construct
`R2cSourceAdmission` or send chunk packets. Selected 26.2
source/VAR/SEM, production section policy, shared projection/fan-out and
multi-client long-lived concurrency remain independently open.

## Actual stock-client checkpoint (18 October 2026)

PRs #377–387 introduced the opt-in ignored **real** client diagnostic and source-preserving 25-chunk renderer-halo path. The unmodified stock client joins the replay-free R2B handoff and now visibly renders the **inner 3×3** of 25 genuine Anvil-sourced columns; the other 16 form an outer loaded but unmeshed ring. The two saved block entities in the expanded halo were removed through the vanilla client, not through an importer omission. An earlier nine-chunk test rendered only the center column. The observed client crash at `LinearPalette.read` identified an extra packed-long array length prefix; #383 corrected the block/biome encoders with independent byte-level regressions.

This is **true visual feasibility**, beyond synthetic TCP/ACK rehearsal. Preserve the clean source save and full terminal/client log, including exact chunk-batch/teleport/keep-alive counts and the visual screenshot. Those detailed 25-chunk counters were not independently reproduced in the repository review and must not be inferred solely from the screenshot.

The positive R2C publisher is still **only constructible under `#[cfg(test)]`**. Product `--r2c-world-plan` does a COLD nonpublishing import and audit. Visual success does not source-admit the runtime 66-biome receiving-client order, the 32,366-heightmap-state table, the outer chunk/Play lifecycle, or arbitrary block-entity-bearing save files.

The **next actions are not another rewrite of the importer or session spine**. Follow the [pre-R2D architecture closure plan](R2C_POST_VISUAL_PRE_R2D_AUDIT_2026-10-18.md):

1. Freeze reproducible visual-world evidence and its negative tests.
2. Close only residual selected client registry/heightmap/outer packet/Play VAR/SEM obligations, reusing the independently admitted 58-method world-state gate.
3. Extend and qualify PR #389's server-lifetime **nonpublishing COLD world host** for the selected product route; retain one semantic authority, validate repeated sessions/concurrency separately, and activate positive publication only after the independent admission gate.
4. Finish M0.3D section selection and R2C.6 reference/direct/cache/share performance tournament using controlled target-hardware evidence.
5. Red-team bounded TCP/ACK/keepalive/reconnect/memory/resource behavior before beginning R2D sustained-world qualification.

## Nine/25-chunk retained TCP/ACK qualification (post-visual hardening)

The original nine-Anvil-chunk/four-signed-region retained-driver test
now shares its source loader, wire checker and localhost peer with a
**25-source-chunk** variant. Both use the *same* original R2B Play
driver, source receipts, immutable server-owned COLD host and
test-only R2C publication witness. The peer reads framed TCP chunks,
acknowledges **each finished batch** through the original inbound
handler, and only half-closes once every source-backed column was
received. The 25-column case forces more than one batch/ACK window;
independent assertions verify center-first ordering, exact signed
chunk positions, source-backed heightmap wire words, batch counts,
outbound drain, per-client receipt cursor completion and zero pending
ACKs. All tests using real source-specific heightmap candidate bytes
remain conditional on the pinned official heightmap workflow; the
ordinary hermetic CI path still checks the 9/25 multi-region source
and shared ownership before that candidate is present.

This closes a **finite 25-column TCP/ACK integration regression**,
not a full vanilla-client runtime proof, source/VAR/SEM admission,
product chunk publication, hardware performance winner or sustained
reconnect/concurrency validation. The nine-source regression stays
available to the existing local launcher unchanged.

**25-source ACK/backpressure + Play-control fairness regression:** The
existing official-heightmap-backed, source-Anvil, retained-TCP test
now *withholds the first finished-batch ACK* for a bounded socket
timeout. The simulated client asserts no subsequent wire bytes arrive
until it grants progress, then submits the already-pending teleport
confirmation (serverbound Play ID 0, sequence 1) immediately before
the 26.2 batch ACK (ID 11), on the **same TCP stream**. The original
Play ingress parser must accept the teleport and advance the batch
without duplicate, reordered or prematurely emitted chunks, and drain
all 25 receipts with zero unacknowledged batches. The nine-column
reference remains unchanged. This is a finite synthetic-peer fairness
and backpressure check, not a 15-second real keep-alive test, an
arbitrary slow-client quota, production admission or concurrent-server
readiness claim.

## Post-visual evidence reproducibility tooling (unadmitted)

The existing `tools/r2c_stock_client_diagnostic.py` launcher now offers
`--evidence-json` as an optional, COLD-only source-free input digest
snapshot. It reuses the already implemented 9/25-position selector and
saved-block-entity source auditor. An external, fresh `0600` JSON records
the exact selected chunk coordinates, SHA-256/length commitments for
`level.dat` and the four selected Anvil regions, the selected R2B
image and heightmap candidate. A staged unmodified vanilla source must
match its disposable copy; post-test rehashing refuses a success record
if any selected inputs changed. The output is never generated on a
failed Rust rehearsal or failed ignored real-client test.

**Qualification scope:** this freezes reproducible **input identity**
and the fact that a local test transport completed. It does not
archive client video/logs, establish an independent rendered-pixels
observation, admit Minecraft source VAR/SEM or populate the uninhabited
production `R2cSourceAdmission` witness. All status booleans are
explicitly false. An operator must retain the exact Git commit,
client/server transcripts and visual proof alongside the source-free
record. No user-private save, source-rich file or binary is committed.

## Direct reference section COLD construction cleanup

The source import path previously filled each 4,096-cell reference
block section with air and replayed every decoded cell via 4,096
individual `BlockSection::replace` calls. The transparent
`DirectBlockSection` reference type now provides
`from_decoded_cells`: copy the already bounded, decoded cell slice into
a single directly owned array and derive non-air, counted-fluid,
random-block and random-fluid summaries in **one traversal**.
The R2C COLD builder uses this path only for a full decoded section;
the existing uniform construction and all runtime mutation behavior
remain unchanged.

An independent mixed-state test compares every returned cell and all
summary counters against the original mutation-by-mutation reference;
it also checks post-import mutation and malformed partial input. The
existing 9/25-column real-Anvil import, receipt resolution and
official-heightmap TCP/ACK regressions continue through the same
server-owned world. This is a bounded COLD import-path simplification,
**not a measured speedup, production storage-policy selection,
source-admission claim, or extra HOT block mutation work**. M0.3D
target-machine qualification remains open.

## Remaining source-review handoff (pre-admission tooling)

The post-visual **client numeric biome IDs, 32,366 per-state heightmap
predicates and outer chunk/light Play lifecycle** are still independently
source/VAR/SEM unadmitted. The already admitted **58-method/20-rule**
world-state gate from #268 remains unchanged.

The new [single-entry source review bundle](../qualification/R2C_REMAINING_SOURCE_REVIEW_BUNDLE.md)
reuses the three existing pinned review frontiers **without creating a
second source parser or packet implementation**. It prepares two
source-free biome-ID/packet declaration inventories and one *separate*
private local four-file heightmap source-text review. A source-free
index binds their digests and enumerates the exact remaining independent
source-review obligations, with all semantic/admission/product
permission flags **false**. The private directory and its Mojang
source-rich JSON must never be uploaded or committed. Existing
first-view and actual stock-client functionality are unaffected.

**This is reproducible reviewer preparation, not a completed human
VAR/SEM review or promotion**, and it does not make the ordinary
server's `R2cSourceAdmission` constructible. Only a separate
independent source gate can authorize that later product change.

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
- Stock-client visible world: **test-only 25-source-chunk visual demonstration observed, central 3×3 rendered; production product not yet admitted**.

If a future PR changes one of these statuses, update *this* ledger,
link the exact new evidence, and delete or qualify the superseded
pending statement. No additional progress report should present
already merged source laws as an unsolved starting point.
