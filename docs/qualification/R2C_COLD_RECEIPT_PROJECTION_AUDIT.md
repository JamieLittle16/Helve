# R2C COLD receipt-to-packet audit — no live publication

**Minecraft:** Java 26.2, protocol 776, DataVersion 4903  
**Status:** development-only COLD source-receipt projector; source admission still **false**.

This integration reuses existing Helve subsystems. There is **no second
semantic dimension, new chunk packet format, duplicate network queue or
shadow world cache**.

## What already existed

- `import_pending_teleport_disk_first_view` imports real selected Anvil
  chunks into one authoritative `SemanticDimensionInstance`, with exact
  source receipts and the existing nearest-first `R2cChunkBatchState`.
- `with_candidate_biomes_from_context` borrows the 66 entries sent by the
  actual R2B Configuration image, without resorting or duplicating names.
- `append_receipt_bound_empty_chunk_body_candidate` derives the existing
  coherent source/reference chunk/heightmap/light view and performs exact
  candidate 26.2 target body serialization.
- `CandidateHeightmapFacts` validates each of 32,366 state facts against
  existing independently qualified non-air/fluid information.
- `R2bPlaySession`, world publication and ACK machinery already share one
  bounded driver and transactional frame path (still separate from this
  development route).

## New executable opt-in

The existing opt-in `--r2c-world-plan=<world>` imports the selected
world after the *real* pending teleport is issued. The additional optional
argument enables a **non-publishing projection audit**:

```sh
helve --r2b-playtest-image=<r2b-image> \
      --r2c-world-plan=<pregenerated-world> \
      --r2c-heightmap-candidate=<26.2-official-state-facts.bin>
```

The official 26.2 heightmap facts workflow emits
`26.2-heightmap-state-facts-candidate.bin` as a short-lived GitHub
Actions artifact. **This is only a runtime candidate** and does not
admit the heightmap predicates. The CLI rejects a missing world flag,
repeated file flag, symlink, nonregular file, non-32,366-byte table or
invalid generated state identity *before opening the listener*. The
one immutable candidate buffer is held by the selected development plan,
not copied per block or biome lookup.

After the regular R2B entry, the already resident COLD dimension and
source receipts are examined with one bounded 65,535-byte reusable scratch
buffer. For each selected source receipt, the existing
`append_receipt_bound_empty_chunk_body_candidate` is run once; empty,
oversized, invalid or stale receipt output fails closed. The audit
reports number of candidate chunks, aggregate body bytes, and maximum
per-chunk body bytes. It never attaches these scratch bytes to the
continuing driver, advances the ACK controller, creates a packet list or
publishes a chunk. The original R2B keep-alive and teleport owner remains
unchanged. The original no-flag R2B route is unmodified.

## Evidence

The official state runtime workflow already tests
`source_chunks_from_two_disk_regions_feed_one_nearest_first_batch`,
covering real saved source chunks from signed Anvil regions, an
immutable receipt-bound heightmap/light projector and the retained R2B
driver. That exact official-oracle test is extended to call the new
COLD production-audit helper *before* the existing send/ACK candidate
test. Additional unit tests reject incomplete and reserved-bit
candidate tables; the executable parser enforces opt-in only with the
selected R2B first-view route.

## Remaining admission and product work

This remains **source-unadmitted**. Client numeric 66-biome ID
assignment, full official heightmap predicate SEM/VAR, packet envelope
and Play lifecycle source admission, and matching save/Configuration
world profile are separate gates. The audit does not verify
server-to-client network visibility and cannot be used to claim a
working R2C stock-client demo.

Once those gates pass, the next integration should use the existing
`R2cChunkBatchState`, receipt projector and R2C inbound handling on
the **same** `R2bPlaySession`; it should not introduce new packet
routing, secondary state or speculative world generation.
