# R2C — parallel remaining source-review frontiers

**Status: human source review and independent VAR/SEM admission still
required.** This is not the already-admitted generic
`R2C-BIOMES/R2C-HEIGHTMAPS/R2C-LIGHT` palette contract. The
remaining client-loaded biome *numeric assignment*, all 32,366
per-state heightmap predicates and full outer chunk/Play wire law
have separate, noninterchangeable source gates.

## Run the two ZIP/Atlas discovery frontiers concurrently

On the machine holding the **exact** official Minecraft Java 26.2
server source ZIP (SHA-256
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`)
and verified Vanilla Atlas SQLite database:

```bash
cd ~/Helve
python3 tools/r2c_parallel_source_frontiers.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output-dir "/tmp/helve-r2c-source-review-$(date +%s)"
```

This runs the repository's *existing* official-source-bound
`r2c_biome_id_source_frontier.py` and
`r2c_chunk_wire_source_frontier.py` in parallel rather than
inventing a second source parser. The output is atomic and
contains only two source-free inventories and a manifest that
hashes both. A mismatch in the exact official-source identity,
review plan, Atlas database, expected method-root groups,
or source-admission flags rejects the entire result. It never
copies source text or Java disassembly to Git.

**Do not repeat the admitted inner-wire review.** The runner also intersects
the fresh chunk-wire Atlas declaration signatures and both normalized/body
SHA-256 hashes with the **already independently admitted**, promoted
`r2c-world-state-source-admission-26.2.json` report. Seven exact
`ClientboundLevelChunkPacketData`/`ClientboundLightUpdatePacketData`
methods have previously reviewed VAR IDs and limited HEIGHTMAP/LIGHT SEM
claims. The manifest's
`reused_independently_admitted_inner_wire_methods` contains their original
VAR IDs, exact hashes and admitted rule IDs; any missing, drifted or forged
match fails closed. This is **only a reuse map**: the existing world-state
gate is not authorization for enclosing packet identities, entry-order law,
block entities, player pacing/ACK, client biome ID assignment or live chunk
publication. Those are the remaining new semantic reviews.

### If the parallel biome inventory fails closed

The wrapper now preserves **only** a bounded, source-free failure category
(e.g. exact missing/ambiguous Atlas root, `net.minecraft.util.Util#sequence`
lookup, or source/Atlas lock mismatch), not arbitrary child stderr or Mojang
text. If the category is insufficient, execute the **existing** biome probe
directly, with the same pinned inputs and a fresh output outside the repo:

```bash
python3 tools/r2c_biome_id_source_frontier.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output "/tmp/helve-r2c-biome-inventory-$(date +%s).json"
```

This emits its specific reason on stderr. A missing method cannot be
substituted with a guessed owner or silently omitted. The 17 October
failure `named delegate owner must resolve once: net.minecraft.Util`
exposed a stale package in the review plan; the separately pinned official
26.2 client probes resolve `net.minecraft.util.Util`. The corrected plan
and source inventory now require that **exact** owner and bounded
`sequence` overloads in the local pinned Atlas. Missing, duplicated or
over-cap declarations still fail closed, and the same official source ZIP
must be fingerprint-verified. This is only the source-discovery fix;
**ordered client assignment and production admission remain unproven**.
Rerun the whole parallel runner to verify the local pinned source matches
the corrected owner. Both inventories remain atomic review inputs,
**never production admission**.

### Independent obligations after discovery

**Biome:** close selected/default known packs and Configuration
registry entries, exact receiving-client registry construction and
`WritableRegistry.register` concrete dispatch, successful
allocation in `MappedRegistry`, error/duplicate/finalization behavior,
and identical client palette numeric IDs for all 66 transmitted names.
Client bytecode evidence PRs #331–#340 is complementary, not
equivalent to source-admitted semantics.

**Heightmap:** independently source-inspect the exact predicates for
`WORLD_SURFACE`, `MOTION_BLOCKING` and
`MOTION_BLOCKING_NO_LEAVES`; pin source delegation and all
32,366 per-state flags. The independent twice-run official-runtime
digest and census from PR #342 proves extraction reproducibility,
not VAR/SEM admission.

**Outer wire:** source-inspect exact protocol-776 packet ID registry,
chunk x/z coordinates, heightmap and palette framing, block entity
empty/nonempty inclusion, light masks and payload lengths/order,
batch/ACK/pacing and first Play entry. Client-side bytecode
observations in PR #341 provide an independent counterpart but
cannot authorize server emission.

Only source-bound human review, independently successful Atlas
gate, source-free promoted manifest and an explicitly checked
production consumer can mark any gate admitted. The parallel
inventory manifest deliberately has **all admission flags false**.
It is not a runtime flag or grant to remove the R2B
`WorldProjectionReady` publication hold.

The opt-in COLD real Anvil view import introduced in #344 is
also non-publishing: it retains one authoritative dimension,
source receipts and existing batch state until these gates pass.
The first actual visible-world result still requires a running
unmodified client and direct rendering/liveness evidence; passing
CI alone cannot establish that milestone.
