# R2C Stock-Client Demo — Finite Runbook and Go/No-Go

**Date:** 18 October 2026  
**Target:** unmodified Minecraft Java 26.2 / protocol 776 / DataVersion 4903  
**Initial evidence baseline:** `8ffc05b8828b7a1440abcabc41b8c3e0f3bf9c0e` (PR #375); subsequent #376–#377 supplied demo-first status and test-only retained TCP harness. Use the latest verified green `main` for the actual test.  
**Current status:** synthetic-client nine-chunk TCP path green; **stock-client visual demo not yet run**  
**Status authority:** [R2C_CURRENT_STATE.md](R2C_CURRENT_STATE.md)

## What counts as the first R2C demo

One ordinary 26.2 client logs into the **original R2B session**,
receives Helve-generated world/chunk/light bodies through its continuing
connection driver, and displays the selected **pregenerated** 26.2
world. There are **no replayed captured Play-world packets**, no
secondary transport/owner, and no R2D world generator. A static finite
initial view with bounded resources and the correct source profile is
sufficient for the first visual checkpoint; movement-driven loading,
complex gameplay and maximum server throughput are not.

Record all of: repository commit, world and `level.dat` digests,
source and runtime identity, selected known packs, Configuration and
chunk/ACK trace, complete initial view coordinates, unmodified client
version, server liveness/teleport result, and a clear screenshot or
video of **actually rendered** blocks. A client stuck at "loading
terrain" is **not** a pass.

## 0. Reuse existing verified work

Already landed; do not reimplement:

- The 58-method / 20-SEM **admitted** biome-heightmap-light
  world-state source bundle (PR #268).
- Complete official-save block differential; 66-id direct loaded
  biome byId/network cross-oracle; the frozen 32,366-state official
  heightmap candidate; imported light and bounded source receipts.
- Source/reference chunk body, cache-centre, chunk batch, paced sender,
  ACK ingress, one `R2bPlaySession` driver and retained read scratch.
- Full 141-clientbound / 69-serverbound Play registration census and
  five R2C ID positions reused with the reviewed R0 dispatch law
  (PR #375).
- Nine real Anvil-*fixture* chunks over **four regions** sent through
  the retained loop on loopback and receipted by a synthetic peer
  (PRs #373–374); the positive source witness is Rust `cfg(test)`
  only.

The old `R2C_CURRENT_STATE.md` text before this checkpoint
underreported several of these items. That is not a reason to
repeat their source research.

## 1. Repeat source-free admission and deterministic TCP rehearsal

From a clean checkout at the baseline or a later verified green
`main`:

```bash
python3 tools/r2c_world_state_admission_verify.py
cargo test --locked -p helve-server --lib \
  r2c_disk_first_view::tests::nine_disk_chunks_cross_four_regions_and_reach_one_receipted_batch \
  -- --exact
```

The **hermetic** test above asserts the nine saved test-fixture source
receipts. The *network emission and ACK half* of that same test runs
only when `HELVE_R2C_HEIGHTMAP_CANDIDATE` names actual official
runtime candidate bytes. A green hermetic run **alone is not a
successful nine-chunk TCP rehearsal**.

To regenerate and run the complete qualified **test-only** TCP path,
on Java 25 with the existing exact runtime oracles:

```bash
python3 tools/official_r2c_heightmap_facts.py \
  --output /tmp/26.2-heightmap-state-facts-candidate.json

python3 tools/r2c_heightmap_candidate_bytes.py \
  --input /tmp/26.2-heightmap-state-facts-candidate.json \
  --output /tmp/26.2-heightmap-state-facts-candidate.bin

HELVE_R2C_HEIGHTMAP_CANDIDATE=/tmp/26.2-heightmap-state-facts-candidate.bin \
  cargo test --locked -p helve-server --lib \
  r2c_disk_first_view::tests::nine_disk_chunks_cross_four_regions_and_reach_one_receipted_batch \
  -- --exact
```

These are exactly the preexisting official-oracle/byte-conversion and
Rust test entry points. They do **not** mint a source-admission
capability. Equivalent Java 25 CI evidence is already collected by
`.github/workflows/r2c-official-heightmap-facts.yml`; reuse the
short-lived source-free artifact where available instead of repeatedly
downloading Mojang's JAR.

## 2. Prepare the real saved world and R2B image

Inputs for the local run (outside the repository):

- `R2B_IMAGE`: compact `CRR2B001` image generated with the existing
  `tools/r2b_pack_playtest.py` from the exact validated R1B
  source-free join image. No captured Play-world frames.
- `WORLD`: a **saved-world root** with `level.dat` and
  `dimensions/minecraft/overworld/region/`. The current
  `R2cColdWorldPlan::new` checks source-root and saved version before
  listening; it is **not** an arbitrary `region/` directory flag.
  Verify DataVersion **4903**. Do not use a custom-dimension or
  arbitrary datapack world as the first fixture.
- `HEIGHTMAP`: the separate official runtime **candidate** binary
  from step 1, exactly 32,366 bytes, with pinned content SHA-256
  `6dc4edc0f6178490af9d79463eca0373b8b359e351d173ebc51cf6166d74c3eb`.
  It remains a COLD test candidate until its own remaining source
  admission.
- `CLIENT`: stock, unmodified Minecraft Java 26.2, same selected
  offline/development profile and known-pack assumptions as R2B.

To create the R2B image from an existing qualified R1B input:

```bash
python3 tools/r2b_pack_playtest.py \
  /path/to/qualified-r1b-join-replay-image.json \
  --output /tmp/helve-r2b-playtest.bin
```

The packer must report `captured_play_frames_written=0`. It
independently revalidates the source/capture/Configuration
commitments. Do not use a guessed, manually reconstructed or
network-recorded chunk image as a replacement.

The first demo fixture must have the actual requested spawn chunks in
the expected signed region files. For the selected profile, source
receipts must confirm explicit empty block entities, correct
biome IDs/section span and publication-ready saved lighting. Missing,
incompatible or corrupted sources fail **before any partial chunk
batch**; no silently substituted Plains/light/height/air.

## 3. Available *today*: honest COLD/stock-client readiness rehearsal

```bash
cargo run --release --locked -p helve-server --bin helve -- \
  127.0.0.1:25565 --once \
  --r2b-playtest-image=/tmp/helve-r2b-playtest.bin \
  --r2c-world-plan=/path/to/26.2-save-root \
  --r2c-heightmap-candidate=/tmp/26.2-heightmap-state-facts-candidate.bin
```

Connect the unmodified client to `localhost:25565`. This route
**already exists** and performs a real R2B bootstrap and optional
COLD saved-world import/projection audit at Play handoff. CLI
normalization supplies the capture-qualified session epoch; the
server checks its image, `level.dat`, region location and candidate
table at the appropriate boundaries.

**Expected today:** console explicitly says
`no chunk publication` / `production_admitted=false`. A stock
client can reach R2B but may remain on the loading-world side because
no R2C chunks are sent. **Do not call that a failed chunk renderer
or claim a successful visual demo.** Preserve the COLD source-receipt,
audit and connection logs as the final real-save preflight.

The command is intentionally not a hidden "turn on chunks" switch:
passing `--r2c-heightmap-candidate` cannot construct the
uninhabited production `R2cSourceAdmission`.

## 3A. One-command local stock-client launch (preferred)

The source-free, COLD orchestrator `tools/r2c_stock_client_diagnostic.py`
reuses the **existing** R1B-to-R2B packer, official Java 25 heightmap
oracle, pinned candidate converter and Rust test harness. It never owns a
Minecraft packet, creates a second Play driver or constructs a
production R2C source-admission witness. It validates the saved-world
directory shape, exact dense runtime candidate digest and R2B image
magic/protocol **before** running any Rust test.

Starting at the repository root, with your actual selected 26.2
pregenerated **save root** and source-qualified R1B JSON from the
existing R1B qualification:

```bash
python3 tools/r2c_stock_client_diagnostic.py \
  --world "/absolute/path/to/26.2-save" \
  --r1b-image "/absolute/path/to/qualified-r1b-join-replay-image.json" \
  --generate-heightmap
```

This command builds a fresh `CRR2B001` image via the established
R1B validator, generates and checks the 32,366-byte official runtime
**candidate** (requires Java 25), runs the preexisting nine-chunk TCP
rehearsal, then starts the **ignored** test-build-only server at
`127.0.0.1:25565`. Once the console invites you, connect the
unmodified Minecraft Java 26.2 client using **Multiplayer → Direct
Connection → localhost:25565**. Leave the client connected long enough
for at least one keep-alive reply, then disconnect normally; the Rust
test can then report its full outcome.

If you **already have** the source-free `CRR2B001` image and the
pinned 32,366-byte official candidate artifact, skip all expensive
preparation by using the same launcher with:

```bash
python3 tools/r2c_stock_client_diagnostic.py \
  --world "/absolute/path/to/26.2-save" \
  --r2b-image "/absolute/path/to/helve-r2b-playtest.bin" \
  --heightmap-bin "/absolute/path/to/26.2-heightmap-state-facts-candidate.bin"
```

For a quick **no-socket** file preflight add `--preflight-only` to
either invocation. For an already-green local nine-chunk rehearsal add
`--skip-rehearsal`. To avoid a busy localhost port use
`--port 25566` and connect to `localhost:25566`.

The launcher and normal Rust tests cannot confirm rendered screen
pixels. A diagnostic **PASS** requires a clean peer EOF, accepted
teleport, at least one valid keep-alive and *all nine source-receipted
chunk bodies completed with no unacknowledged batch*. The screen
still must be checked manually, and even success is **not** a
production/source-admitted R2C milestone.

If the launcher fails, copy the first `R2C diagnostic NO-GO`
message and its preceding Rust or client log. Wrong saved-world
layout, missing capture image and missing/corrupt oracle are **input
preparation issues**; a packet mismatch or no visible terrain after
an accepted batch is a narrower genuine receiving-client integration
issue. Do not fix either by replaying captured Play world packets.

## 3B. New: isolated local stock-client *diagnostic* over real TCP

The existing `cargo test` build now includes exactly one **ignored**
external-client test:
`r2b_playtest::r2c_stock_client_diagnostic::manual_stock_client_receives_real_anvil_chunks`.
It composes the original full R2B handshake and Play entry, **same
nonduplicated** COLD 26.2 save importer/source receipts, approved bounded
R2C section/body projector, quota-aware sender, ACK ingress, teleport
and keep-alive in the original continuing socket loop. The positive
`R2cSourceAdmission` witness exists **only inside `cfg(test)`**.
The product/server binary is unchanged and **cannot** enable it via
CLI, feature, runtime variable or a copy of the test executable.

Run this from the machine where the **unmodified Minecraft Java 26.2
client is actually available**, with the real pinned R2B image,
selected namespaced save root and SHA-checked dense heightmap
**candidate** already prepared:

```bash
HELVE_R2C_DIAGNOSTIC_CONFIRM=UNADMITTED_LOCAL_ONLY \
HELVE_R2C_DIAGNOSTIC_EPOCH=4d7f604f196a43b08987f0b2a27c2663 \
HELVE_R2C_DIAGNOSTIC_R2B_IMAGE=/tmp/helve-r2b-playtest.bin \
HELVE_R2C_DIAGNOSTIC_WORLD=/path/to/26.2-save-root \
HELVE_R2C_HEIGHTMAP_CANDIDATE=/tmp/26.2-heightmap-state-facts-candidate.bin \
cargo test --locked -p helve-server --lib \
  r2b_playtest::r2c_stock_client_diagnostic::manual_stock_client_receives_real_anvil_chunks \
  -- --exact --ignored --nocapture --test-threads=1
```

The ignored test binds **only `127.0.0.1:25565`** (optional
`HELVE_R2C_DIAGNOSTIC_PORT` to move the same loopback listener), then
waits for **one** real client. Connect to `localhost:25565`. The
diagnostic exits when the client disconnects: stay connected through
at least one keep-alive cycle, then close the client, inspect the
test result, the console output and the client logs, and record
whether blocks **actually rendered**.

The saved-world import is fail-closed: a missing/invalid selected
source chunk, biome, lighting layer, block-entity assumption or
heightmap source table aborts rather than being replaced by synthetic
world bytes. The test may likewise expose a genuine client-side
packet/registry/ordering failure. **An observed visible terrain result
is diagnostic evidence only, not source admission or production
R2C milestone completion.** Record the first failing selected
packet/client error if it does not render, rather than building another
parser. A green Rust test proves the socket exited with accepted
teleport and at least one keep-alive, **and** the nine-chunk
source-receipted batch completed with no pending rate ACK. It does
**not** machine-verify screen pixels.

The test is not run by ordinary CI, and Rust `--test` builds may be
slower than the production release path. Never copy its positive
witness into production. When the selected remaining client/outer-Play
VAR/SEM gates pass, activate the existing publisher in the normal
product route and repeat the same observation as the actual R2C exit.

## 4. Minimal missing engineering to permit *visible* demo

| Obligation | Reuse / exact action | Exit evidence |
| --- | --- | --- |
| Receiving registry and known-packs semantics | Reuse the selected 66-entry Configuration/runtime match, client order/branch hashes and existing source dossiers. Close only unreconciled client registration/exception/known-pack delegates | Explicit, narrow independent source/VAR/SEM admission covering selected profile; no sorted/surrogate biome IDs |
| Per-state heightmap authority | Reuse admitted three-map predicate SEM and twice reproduced dense runtime table. Close *only* the remaining state-method/delegate binding and independent source gate | Exact source-bound 32,366-state facts, no "candidate" promotion by renaming |
| Outer Play lifecycle | Reuse R0 ID law, exact GameProtocols registrations, source-reviewed chunk sender, batch finish/ACK and existing wire serializers | Finite world-entry, view-centre, chunk, batch/ACK order and branch VAR/SEM gate; no unnecessary general-gameplay source graph |
| True saved-world route | Consume the already resident dimension/source receipts and one known selected 26.2 save | Correct real-save import and selected chunk/light completeness before publish |
| Production connection | Bind admitted capability to **existing** `SourceAdmittedPlayPublisher` and call the original `serve_world_projection_wait` with that same owner instead of `None` | No second session/queue/decoder, no bypass, bounded transactional backpressure |
| Client visual gate | Single stock 26.2 client + selected save | Screenshot/video, actual world hashes, ACK and retained teleport/keep-alive, zero captured world-body replay |

A diagnostic test-only publication already exists. **Do not**
add a user-facing unchecked `--unsafe-r2c` flag, assert a capability,
manufacture an admitted table, or run an integration test compiled with
`cfg(test)` and report it as a production client pass.

If an actual stock-client experiment is performed before the
remaining source admission, isolate it to development/test
infrastructure and record its outcome as *unadmitted diagnostic
evidence*, never a production R2C success. A true milestone pass
requires the final gate.

## 5. Finite acceptance / failure reporting

The first successful stock-client demo must establish:

1. Handshake → Login → source-admitted Configuration → replay-free R2B
   → R2C on the **same** bounded connection.
2. Correct visible stone/terrain from the *saved selected world* (not
   merely a source-formatted synthetic test chunk), spawn/dimension
   coherent, no protocol error or fallback world replay.
3. Actual outgoing cache-centre, batch start, each independent
   source-receipted chunk/light body, batch finish, and incoming
   rate ACK in correct order, respecting tick/fairness rules.
4. Initial teleport acknowledgement and at least one keep-alive
   interaction; the client remains connected after terrain appears.
5. Source-qualified admitted runtime state/biome/height/light identity,
   bounded egress/ingress memory, no discarded R2C ACK packets.
6. Reproducible logs and world/client/commit pins. Negative control:
   removing the publisher prevents terrain from rendering.

Record **NO-GO** with the *first concrete failing step* (source
profile / prepared world / final source gate / client disconnect /
missing terrain / liveness / mismatched source body). Do not turn
it into another generic "R2C not yet implemented" project.

## 6. After the visible demo, before R2D

Move the expensive **R2C.6 production performance tournament**
and **M0.3D section-production policy selection** into an explicit
post-demo, pre-R2D optimisation/hardening phase. Measure retained
chunk representation, imports, shared packet bodies, cache policy,
allocation/copy reduction, fan-out, slow-peer resource bounds and
whole-join tail latency on controlled hardware. Make architecture and
SEM safety a prerequisite for each candidate; a slower but correct
bounded reference demo may be the right starting point.

This deferral does **not** relax source correctness, finite memory
limits, transactional publication, exact saved-world ownership or
stock-client acceptance. It defers *winner selection*, not correctness.
R2D can then focus on broader sustained operation/world generation
rather than completing the initial viewer.
