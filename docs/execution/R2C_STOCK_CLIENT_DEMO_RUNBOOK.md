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
COLD saved-world import/projection audit **once at server startup, before
accepting any client**. The server-owned COLD host now selects all 25
source-backed 5×5 initial halo columns, matching the successful
test-only visual profile (nine of these have a complete mesh halo).
A nine-source-chunk-only save is no longer sufficient for this normal
startup audit. Missing or nonempty saved block-entity evidence anywhere
in the selected 25 still fails closed; the test-only nine-column
reference rehearsal remains separate.

**Automated ownership regression:** the standard Rust test
`twenty_five_disk_chunks_share_one_host_and_missing_region_fails_closed`
builds a disposable 25-column Anvil-format fixture spanning four signed
regions. It verifies exact nearest-first source receipts, the single
`R2cColdWorldHost` resident allocation shared across independent
sessions, and no Play egress. It also removes one required region file:
existing hosted residents must remain attachable, while a new import
must reject the now-incomplete source. The test uses the established
**uncompressed** synthetic Anvil writer; it does not replace the
official 26.2 source save, actual-client log or full independent wire
source qualification. CLI normalization supplies the
capture-qualified session epoch; the server checks its image,
`level.dat`, region location and candidate table before accepting
connections.

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

### Freeze exact source evidence for a diagnostic run

The existing launcher supports an optional **local source-free evidence
manifest**, written to a **new, private** JSON file *outside* Helve.
It reuses the existing first-view selection, source audit, R2B packer,
heightmap validator and Rust test: no second NBT decoder or source-law
shortcut is introduced.

```bash
python3 tools/r2c_stock_client_diagnostic.py \
  --world "/absolute/path/to/26.2-save" \
  --r2b-image "/absolute/path/to/helve-r2b-playtest.bin" \
  --heightmap-bin "/absolute/path/to/26.2-heightmap-state-facts-candidate.bin" \
  --render-halo \
  --evidence-json "/tmp/helve-r2c-25-source-evidence.json"
```

This records the **ordered 25 source coordinates**, SHA-256 and byte
lengths of `level.dat` and each selected signed Anvil region, and
digests for the R2B image and dense heightmap candidate. It rejects
missing, oversized or linked files. With `--stage-vanilla-overworld`,
the disposable snapshot must match the original save byte-for-byte.
All input hashes are checked again **after** the test; source drift
withholds the success report rather than claiming a reproducible run.

The report is created mode `0600`, never overwritten or committed under
the repository. It contains **only relative filenames and hashes**,
not NBT payloads, Mojang source, saved chunks, absolute user paths or
network captures. It explicitly fixes
`source_var_sem_admitted=false`,
`production_chunk_publication_admitted=false`, and
`stock_client_pixels_independently_verified=false`.

Add `--preflight-only` for a digest snapshot without any listener:
`PREFLIGHT_ONLY_NO_CLIENT`. A successfully completed ignored TCP
diagnostic instead records `TEST_ONLY_TRANSPORT_COMPLETED_VISUAL_MANUAL`.
Neither proves pixels or source admission. Record the exact Git commit,
complete terminal/client logs, ACK/keep-alive observations and a
screenshot/video separately. Do not upload private source worlds.

For a quick **no-socket** file preflight add `--preflight-only` to
either invocation. For an already-green local nine-chunk rehearsal add
`--skip-rehearsal`. To avoid a busy localhost port use
`--port 25566` and connect to `localhost:25566`.

The test-only listener now accepts a **bounded eight pre-Play
connections within 180 seconds**. A status-only query or early pre-Play
EOF is recorded as a **nonpassing probe**, and the listener remains
ready for a *new* direct-login socket. Once any connection actually
reaches Play, only the original R2B → R2C socket/driver is used,
and genuine Play errors never trigger a silent retry. This is a
test-harness fix for `SessionClosedBeforeWorld`; it does not prove that
a particular prior close was a status ping.

**Selected capture profile:** the R1B fixture is pinned to offline
player name `Stato16` (offline UUID
`682014fe-ad63-3699-aada-79aa08d95b45`). In Prism Launcher,
select a matching **offline** account for this qualification run,
rather than silently changing Helve's fixed source-backed capture
identity. Client version must remain vanilla **26.2**.
A wrong name/version may be a real Login error, not a status probe.

For a concrete local re-run using the already found paths:

```bash
cd /home/Jamie/Crucible
git switch main
git pull --ff-only
python3 tools/r2c_stock_client_diagnostic.py \
  --world "/home/Jamie/.crucible/oracles/minecraft-26.2/world" \
  --r1b-image "/home/Jamie/Downloads/r1b-join-replay-image.json" \
  --generate-heightmap
```

After `listening on 127.0.0.1:25565`, connect with Minecraft 26.2
**Multiplayer → Direct Connection**, not just the multiplayer
server-list ping. If console says `pre-Play-only connection`, do
not conclude R2C failed: another login connection is still awaited.
If joining fails again, preserve the **first** Rust preplay/packet
error and `$HOME/.local/share/PrismLauncher/instances/26.2/minecraft/logs/latest.log`.
No production feature flag or source-law downgrade is appropriate.

The launcher and normal Rust tests cannot confirm rendered screen
pixels. A diagnostic **PASS** requires a clean peer EOF, accepted
teleport, at least one valid keep-alive and *all selected source-receipted chunk bodies completed with no
unacknowledged batch* (nine by default, 25 with `--render-halo`). The screen
still must be checked manually, and even success is **not** a
production/source-admitted R2C milestone.

If the launcher fails, copy the first `R2C diagnostic NO-GO`
message and its preceding Rust or client log. Wrong saved-world
layout, missing capture image and missing/corrupt oracle are **input
preparation issues**; a packet mismatch or no visible terrain after
an accepted batch is a narrower genuine receiving-client integration
issue. Do not fix either by replaying captured Play world packets.

## Interrupted or unaligned Anvil source: do not edit the region bytes

A subsequent read-only 25-chunk audit of `Helve R2C Clean` on 18
October rejected `r.0.-1.mca` because the whole region byte count was
**not a multiple of 4,096**. This is a different failure from the
earlier source-backed two block entities. The existing Rust
`RegionView::new` and Python `vanilla_section_extractor` both
correctly require at least two 4 KiB header sectors and fully aligned
region size. We **must not round/truncate/pad** region bytes as a
shortcut, especially not in the original save. This result alone
does not identify whether an in-flight write, incomplete flush,
interruption or persisted malformed save caused the mismatch.

With the vanilla world **closed** (Save and Quit, and exit any
other open single-player instances using this save), inspect the
actual file and other signed source regions without opening
the network or modifying them:

```bash
WORLD="$HOME/.local/share/PrismLauncher/instances/26.2/minecraft/saves/Helve R2C Clean"
find "$WORLD/dimensions/minecraft/overworld/region" \
  -maxdepth 1 -name 'r.*.*.mca' -type f \
  -printf '%f bytes=%s modified=%TY-%Tm-%Td_%TH:%TM:%TS\n'
python3 - "$WORLD/dimensions/minecraft/overworld/region/r.0.-1.mca" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
length = p.stat().st_size
print(f"Anvil region: {p.name}; bytes={length}; trailing={length % 4096}; aligned={length >= 8192 and length % 4096 == 0}")
PY
```

Rerun the read-only `--render-halo` audit only on a
stable, saved/closed source. If the file remains misaligned, use a
**different authentic vanilla save** for the finite demo, and preserve
this one for diagnosis; do not manually append zero bytes or alter
source chunks. If normal Save and Quit through vanilla makes the file
valid, it must still independently pass the 25-chunk saved-entity
audit and existing Rust source/receipt admission before another
stock-client test.

## 25-chunk halo source failure: inspect before running Java or opening TCP

The first `--render-halo` stock-client attempts on 18 October 2026
failed *before* any chunk was published:
`Source(Disk(Visit(BlockEntities(UnhandledEntries { count: 2 }))))`.
Both identical attempts used the same verified `Helve R2C Clean`
source save, which had passed the **nine-chunk** explicit-empty gate;
the expanded 25-source-chunk view introduced unsupported saved block
entities in the additional halo. This does **not** contradict the
successful one-chunk render or establish a problem with the halo theory.

Use the existing immutable-source NBT inspection oracle with the same
25-position selector **before** re-generating any heightmap:

```bash
cd /home/Jamie/Crucible
python3 tools/r2c_first_view_block_entities.py \
  --world "$HOME/.local/share/PrismLauncher/instances/26.2/minecraft/saves/Helve R2C Clean" \
  --render-halo
```

The new COLD audit prints each selected saved chunk's explicit-empty,
missing or nonempty evidence, and the original saved block-entity
`id,x,y,z`. The 25-chunk launcher option now **calls this same
read-only audit before the R1B packer, Java heightmap oracle, rehearse
and live socket**; a failing source cannot waste another full
expensive attempt. It does not rewrite NBT, drop block entities, fake
light, promote a source receipt, or change production R2C. Rust still
re-verifies every receipt before Play.

For a quick first 3×3 visibly meshed demonstration, an independent
**unmodified 26.2** clean single-player fixture generated as
**Superflat, structures off** can supply a legitimate dense 5×5
with explicitly empty block-entity lists; generate/save all 25 chunks
around `(chunk X=0, Z=-1)`, then audit it first. The visual
proof uses genuine vanilla-generated flat blocks rather than missing
or invented chunks. Alternatively, use an independently prepared
*copy* of a terrain save without block entities in the selected
25 positions, leaving the previous successful nine-source-chunk
fixture untouched. Do not silently strip saved entities from source
Anvil data; proper support for nonempty lists remains a separate
source- and wire-qualified feature.

## 18 October 2026: successful first visible chunk and renderer-neighbor halo

After the fixed-length palette repair (#383), the **unmodified**
Minecraft Java 26.2 client renders the center chunk in the genuine
saved `Helve R2C Clean` world. The other eight chunks contain block
collision (the operator could walk on them), but remain invisible.
This is a **first real visual R2C proof**, not nine visibly rendered
chunks or complete source/VAR/SEM production admission.

This pattern is consistent with the official client initial section
mesher's eight-loaded-and-lit-neighbor gate: a selected 3×3 area has
only one chunk column with all surrounding columns loaded. To
**test that specific hypothesis**, without altering the default,
a new COLD-only `--render-halo` option selects **25 genuine
source-backed chunks (5×5)** around the same R2B teleport.
All of the center 3×3 then have their eight adjacent chunk columns
available; the outermost 5×5 ring may still be unrendered until a
larger halo is provided.

Run the already working unmodified 26.2 save and captured image:

```bash
cd /home/Jamie/Crucible
python3 tools/r2c_stock_client_diagnostic.py \
  --world "$HOME/.local/share/PrismLauncher/instances/26.2/minecraft/saves/Helve R2C Clean" \
  --r1b-image "$HOME/Downloads/r1b-join-replay-image.json" \
  --generate-heightmap \
  --render-halo
```

The unchanged **nine-chunk TCP/ACK rehearsal always runs first**.
The actual ignored Rust test then reads and validates every one of
the 25 real source chunks using the same one-pass Anvil visitor,
transactional receipts, original R2B connection and publisher.
This is an **opt-in diagnostic only**: the production COLD importer
still selects its original nine chunks, and normal binaries do not
recognize or construct positive R2C source admission.
No missing chunk may be fabricated; any additional chunk's nonempty
block entities, missing light or invalid source data still cause
the whole test to reject before emitting a partial batch.

Observe whether the inner 3×3 now render; preserve screenshots and
the live ACK / keepalive trace. If they do, that supports the
neighbor-gating explanation. The first visible chunk result alone
does not prove all client rendering/wire semantics, and outer-ring
visibility is **not** a required assertion for this experiment.

## First real source-backed nine-chunk client batch: protocol fault follow-up

On **18 October 2026**, the fresh unmodified 26.2 structures-disabled
save `Helve R2C Clean` achieved the first real in-client
R2C chunk-batch interaction, far beyond the previous saved-entity
import guard. The console observed:

- nine actual saved source chunks resident with nine verified receipts;
- 299,717 bytes of chunk body candidate, max 39,176 bytes;
- `R2B WorldProjectionReady` on the original bounded transport;
- nine source-receipted candidate chunks published and an actual client
  chunk-batch acknowledgement received (`unacknowledged_batches=0`);
- accepted teleport confirmation on the same Play session;
- **zero keep-alive replies** before the client closed, nine other
  serverbound gameplay frames discarded by the intentionally limited
  diagnostic, and an on-screen **Network protocol error**.

**This is partial wire success, NOT a successful visual demonstration.**
Chunk-batch acknowledgement proves the client advanced through the
batch protocol; it is **not** proof of all chunk/light/biome bytes being
valid, consumed or rendered. The client terminated in ~6 seconds, before
the experiment could verify a keep-alive response; zero keep-alives
alone is **not** evidence that the keep-alive implementation is wrong.
Do not mark complete R2C or source-admit the clientbound codec on this
evidence.

The *next required artifact is the client exception and packet class*,
not another identical server launch or a bypass of the keep-alive gate:

```bash
LOG="$HOME/.local/share/PrismLauncher/instances/26.2/minecraft/logs/latest.log"
grep -n -i -C 12 -E \
  'network protocol error|decoderexception|encoderexception|failed to handle packet|exception|packet handling|disconnect|reported exception' \
  "$LOG" | tail -n 180
```

In a locally rerun test-only diagnostic, the preexisting original
serverbound Play loop now additionally reports **up to the first 16
unclaimed packet IDs** (numeric ID and monotone observation time only,
no payload capture). Any early peer EOF *after* a complete chunk ACK
prints `R2C DIAGNOSTIC PARTIAL WIRE RESULT` and **fails** the test
unless a complete keep-alive roundtrip was observed. This log exposure
does not add a production world packet, second ingress owner or HOT
trace. The exact official client stack trace should direct the next
narrow packet-codec/registry/profile repair.

## Source diagnosis before another live-client attempt

Both the original oracle and the separate Prism `New World` real 26.2
saves have now failed at precisely the same **nonempty saved
block-entity source list** guard, after the replay-free Login/Configuration
path entered WorldProjection. Re-running unchanged inputs cannot resolve
that provenance constraint.

Use the **read-only** official-save qualification parser before the
next expensive Java heightmap run or stock-client connection:

```bash
cd /home/Jamie/Crucible
python3 tools/r2c_first_view_block_entities.py \
  --world "/home/Jamie/.local/share/PrismLauncher/instances/26.2/minecraft/saves/New World"
```

For comparison, run the same command with
`--world "$HOME/.crucible/oracles/minecraft-26.2/world"`.
The tool inspects **only the nine actual requested chunks** nearest the
fixed R2B teleport centre `(0,-1)` and prints each chunk coordinate,
explicit empty/absent/nonempty evidence, exact saved `id`, `x`,
`y`, `z` for any nonempty entry and a region SHA-256 prefix. It
reuses `tools/vanilla_section_extractor.py` for region framing,
compression and NBT parsing, rather than adding a second saved-world
codec. The audit never writes to the save and returns nonzero if any
of those nine source chunks is not positively explicitly empty.

**Do not remove a named source entity automatically.** If it is
legitimate gameplay content (e.g., a chest, sign, bed or furnace), the
correct general fix is an independently source-qualified
nonempty-block-entity chunk packet encoder. For a **narrow first
visibility diagnostic**, start a *separate* vanilla 26.2 world with
structures disabled and without any manually placed block entities,
ensure the nine target chunks around `(0,-1)` are generated and
saved, then run this audit first. Do not use NBT edits or fake
empty-list substitutions; a clean diagnostic fixture must still be an
authentic vanilla save. Client-visible success remains a separate
observation even after this COLD audit passes.

## 3A.1. Real-save fallback when the original oracle contains block entities

The selected oracle may contain a valid saved block entity in the nine-chunk
initial view, causing `Source(Disk(Visit(BlockEntities(UnhandledEntries
{ count: 1 }))))` at the COLD admission boundary **after R2B is ready**.
This is a correct fail-closed rejection, **not** evidence of a broken
chunk codec, source receipts, packet ID or TCP driver.

The first visual demo still deliberately requires **explicitly empty**
`block_entities` source lists: see
[`R2C_BLOCK_ENTITY_IMPORT_GATE.md`](../qualification/R2C_BLOCK_ENTITY_IMPORT_GATE.md).
No production code is authorized to discard non-empty entries or treat a
missing list as empty.

For the first *diagnostic*, an unmodified 26.2 **vanilla** save with a
structure-free initial area is appropriate. The COLD launcher can now
stage its **unchanged source bytes** to the exact namespaced development
layout without requiring the user to relocate/mutate the original
Minecraft `region/` directory:

```bash
cd /home/Jamie/Crucible
python3 tools/r2c_stock_client_diagnostic.py \
  --world "/home/Jamie/.local/share/PrismLauncher/instances/26.2/minecraft/saves/New World" \
  --stage-vanilla-overworld \
  --r1b-image "/home/Jamie/Downloads/r1b-join-replay-image.json" \
  --generate-heightmap
```

Make sure the source save is generated by **unmodified Java 26.2**,
saved/closed before copying, and has genuine generated chunks in the
four files `r.-1.-1.mca`, `r.-1.0.mca`, `r.0.-1.mca`,
`r.0.0.mca` (the nine selected chunks span the signed origin). The
first view is pinned to the retained R2B teleport near X=10, Z=-6;
a different source world's spawn does not move that selected teleport.
The staging command refuses a missing file or symlink; it never
synthesizes missing regions or changes any NBT.

The source `level.dat` and these four entire region files are copied
into an automatically removed temp directory. The existing Rust
`R2cColdWorldPlan` and one-pass Anvil importer then validate the
original bytes, including DataVersion=4903, source light, biome profile
and **empty** block-entity evidence. Non-empty block entities still
reject. This staging is **test-only**, not a permanent proposed saved
world layout or an argument to expand source admission. If another
saved world fails the same guard, use a real structure-free generated
world for the demo or close the separate block-entity source codec
before claiming general-world support.

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
