# R2C 26.2 Biome Registry — Configuration Witness Candidate

**Status:** parser and synthetic fail-closed qualification only. **Not a source-admitted numeric biome registry map.** Parent: #285.
Target: Minecraft Java 26.2 / protocol 776 / DataVersion 4903.

## Why this path

The SHA-pinned Mojang datagen registry report does not contain the loaded
worldgen biome ID map. Its 66 biome resource JSON names are real source
evidence, but lexicographic order is not client registry numeric order.

The R1B source-admitted selected Configuration route sends ordered registry-data
packets, including a biome registry. A previously captured default 26.2
Configuration route is pinned by complete body and frame commitments in the
R1B witness. This probe consumes the **R1B join capture image** produced from
that exact capture. It does not read packet replay data into the live Helve
server or modify the resident world.

The narrow selected profile uses matching known packs minecraft:core@26.2.
For the 66 built-in biome entries, the expected packet has resource key strings
and absent inline entry NBT. The probe rejects any inline entry payload rather
than guessing how to skip it. It also rejects duplicate, missing, malformed,
non-source-inventory, noncanonical, and trailing-byte entries.

## Reproduce locally with the original pinned capture

Run from repository root with the existing **exact R1B capture** stored
on the qualification machine, not an arbitrary proxy session:

    python3 tools/r1b_join_capture_image.py /path/to/26.2-verified-capture.json \
      --output /tmp/r1b-selected-capture-image.json --play-frame-limit 0

    python3 tools/r2c_biome_registry_capture.py \
      /tmp/r1b-selected-capture-image.json \
      --output /tmp/r2c-biome-registry-CANDIDATE.json

The join-image tool first checks its canonical full-capture SHA-256 and
the complete frozen Configuration frame/body witnesses. The new tool
independently checks its Configuration packet-body digests, target, source
archive, registry-packet ordering, biome entry payload, and frozen official
66-key inventory. It records the network entry order exactly with a content
digest, without alphabetically sorting values. The official server SHA-256
value is copied from the target's source lock; this is **not** cryptographic
proof of the captured process's JAR bytes.

Output intentionally includes candidate_names_by_network_ordinal and
numeric_id_authority = UNQUALIFIED_CAPTURE_CANDIDATE. It cannot be passed
to production world admission by assertion or field renaming.

## Further requirements to resolve #285

1. Obtain an independent loaded-world registry map from the same SHA-pinned
   official server and exact datapack/known-pack profile. Record explicit
   numeric ID/key pairs, and reject any gaps, duplicates or unknown keys.
2. Source-admit the exact 26.2 bridge from loaded server registry iteration
   through Configuration entry ordering to client registry numeric ordinals,
   including delegated methods. A capture alone is not semantic authority.
3. Compare all 66 network entries with independent loaded-registry identities
   **by ordinal**, not only by key set or resource digest.
4. Freeze the checked ordered source-free artifact (world profile, exact
   official JAR/source hashes, and both evidence digests), regenerate in CI,
   and only then bind OrderedBiomeRegistry to production.
5. Confirm chunk-source and client output against stock-client observation.
   No guessed Plains substitution, save-observed ID map or packet replay.

## Test boundary

    python3 -m unittest discover -s tools/tests -p 'test_r2c_biome_registry_capture.py' -v

Synthetic tests cover ordered encoding, VarInt canonicality/bounds,
identifier validation, duplicate entries and registries, malformed
optional-data flags, source-inventory identity and non-admitted status.
They do **not** claim a pinned-capture output was regenerated in CI, since
the full source capture is not committed. This limitation is intentional.
