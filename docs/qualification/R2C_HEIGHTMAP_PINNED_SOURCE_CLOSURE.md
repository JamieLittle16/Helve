# R2C — exact-source closure for 32,366 heightmap state predicates

**Status:** source review required; production and independent VAR/SEM gates **closed**.

The first-pass 19-method review of biome ordering and chunk outer wire
is retained at `vanilla/reviews/network/r2c-first-pass-source-free-observations.json`.
It does **not** source-qualify the per-state inputs to heightmaps.

## Already reproduced — do not regenerate another guess

The official Java 26.2 runtime oracle
(`tools/official_r2c_heightmap_facts.py`) traversed the actual
32,366-state global registry twice; the independently reproduced
dense four-bit byte table is identified by SHA-256
`6dc4edc0f6178490af9d79463eca0373b8b359e351d173ebc51cf6166d74c3eb`.
The 16-bin distribution and three heightmap counts are frozen in
`docs/qualification/R2C_HEIGHTMAP_STATE_FACTS_ORACLE.md`.

The Rust server already validates the source-unadmitted table against
the independently qualified global per-state non-air and counted-fluid
mutation flags, borrows the table in its COLD projector, and has a
bounded receipt-bound chunk packet test against exact heightmap words.
This is candidate **data and integration** evidence, not semantic
source admission.

## New: read the actual four pinned predicate source files

The exact official 26.2 Java sources behind the three exposed
heightmap predicates and relevant solidity/leaf/fluid state semantics
are now collected with a single local operator command:

```bash
git pull
python3 tools/r2c_heightmap_predicate_source_review.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output "/tmp/helve-r2c-heightmap-sources-$(date +%s).json"
```

The exporter reuses the canonical pinned Vanilla Atlas/source-lock
preflight and the **four existing source-file SHA-256 commitments** in
`official_r2c_heightmap_facts.py`. It reads only:
`Heightmap.java`, `BlockBehaviour.java`, `FluidState.java`
and `LeavesBlock.java`, checks that each archive path is unique, has
an exact SHA-256 match, decodes as UTF-8, and fits the fixed per-file
and aggregate bounds. The external output is new-only, mode 0600.

**Do not commit/upload the source-rich artifact to GitHub.** Keep it
temporary and local for independent source review. Its fields explicitly
say `source_inspected=false`,
`independent_source_var_sem_admitted=false` and
`production_admitted=false`. It cannot build, substitute or authorize
the runtime source-admission capability.

## Required semantic closure

Review the four pinned source files and their actual method/delegate
edges, including:

1. `Heightmap.Types` predicates for `WORLD_SURFACE`,
   `MOTION_BLOCKING`, and `MOTION_BLOCKING_NO_LEAVES`.
2. `BlockBehaviour.BlockStateBase.blocksMotion()`, the solidity
   cache computation and its block-type exceptions. Close any delegate
   reached outside the four files with exact pinned methods; do not
   approximate collision shapes from a block ID or inferred name.
3. `FluidState.isEmpty()`, the getter from a concrete block state,
   and the class/type identity for `LeavesBlock`.
4. Reconcile full 32,366 runtime facts with source predicate *semantics*,
   checking the previously frozen per-state digest and density,
   independent Atlas VAR/SEM source decisions, and chosen world/packet
   COLD projection behavior. The existing CI run certifies
   reproducibility, not semantic correctness.

This particular track does not complete the independent *client
receiving registry* proof. The client-order and invokedynamic
bootstrap frontiers already record official-client instruction-hash
and error-path evidence; they still need independent semantic branch
review, selected `minecraft:core@26.2` profile agreement and
a complete source-free VAR/SEM admission. Avoid conflating the
server-side ZIP and the separate official client JAR.

Only after all the biome-ID, predicate, outer-wire and Play lifecycle
gate obligations are satisfied may the live `R2cSourceAdmission`
capability be inhabited and the currently dormant publisher connected.
The first real demonstration uses pregenerated vanilla Anvil chunks;
world generation remains R2D.
