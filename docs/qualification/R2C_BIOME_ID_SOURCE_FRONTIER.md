# R2C — Loaded biome ID source closure frontier

**Status:** finite declaration discovery only; not a source review or production admission.

Official runtime evidence (#294 and #295) established that the loaded Minecraft
Java 26.2 server's `Registry<Biome>` ordinal table and its Configuration
`registry_data` publication agree exactly on all 66 default known-pack
biomes. The full candidate was frozen in #296. That evidence remains
`RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING`.

The already admitted `GATE-NET-R2C-WORLD-STATE-26_2-001` proves the
biome *container* / palette binding, not **how loaded dynamic biome
numeric IDs are assigned**, nor how the receiving 26.2 client associates
each ordered Configuration key with an ID. Do not extend its status by
implication.

## Focused official-source review

A separate, bounded plan at
`vanilla/reviews/network/r2c-biome-id-source-frontier.json`
contains three distinct non-overlapping proof obligations:

1. Loaded registry insertion and `byId`/`getId` ID allocation;
2. Selected default known-packs branch and ordered Configuration emission;
3. Bound biome paletted-container identity from the loaded registry.

To prepare source-free declaration fingerprints from the pinned local source
archive and disposable Atlas database, run:

```bash
python3 tools/r2c_biome_id_source_frontier.py \
  --source ~/Documents/mc-source/mc-src.zip \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-r2c-biome-id-source-frontier.json
```

The tool must resolve every named source class exactly once, verify
the official source SHA-256 and Atlas lock, and freeze declaration
signatures and fingerprints with observed hazard leads. The cap is
256 methods per root type, and missing/ambiguous declarations fail.
No official source body/excerpt is emitted or committed.

The output always says `source_inspected: false`,
`client_assignment_proven: false` and
`production_admitted: false`. **Atlas metadata is not review.**
The source ZIP itself must remain local.

After the bounded source review, explicitly select the narrow declarations
actually relied upon, close reachable delegates and hazards, produce
reviewed VAR/SEM records, and pass an independent fingerprint-pinned
source gate with provenance. The initial server-only source corpus is
not proof of the client's registry assignment behavior; that requires
separate exact client code/source or equally authoritative evidence.

**Do not** wire the frozen biome fixture into the runtime
`OrderedBiomeRegistry` or 26.2 Play chunk publication until that last
qualification is complete. The first R2C demo continues to rely on
pregenerated world import, not R2D world generation.
