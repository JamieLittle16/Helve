# R2C — immutable Configuration / loaded biome-ID agreement at pack time

**Target:** Minecraft Java 26.2, protocol 776, data version 4903.  
**Evidence class:** cross-oracle selected-profile consistency only, **not receiving-client VAR/SEM source admission**.

## What the packer now checks

The existing `tools/r1b_pack_join_replay.py` first validates its
entire exact captured source-free R1B JSON: the source and capture SHA-256,
34 Configuration bodies, the complete Configuration concatenation
digest, and all selected experimental Play bodies. Before the selected
Configuration is converted to the immutable R1X image, the COLD
`r2c_selected_biome_profile.verify_selected_biome_profile` guard also:

1. Requires the exact 34-body Configuration packet ID sequence and
   29 distinct registry-data packet names.
2. Parses the **actual transmitted** `minecraft:worldgen/biome` body
   using the **existing** bounded Configuration biome wire parser;
   validates 66 unique IDs and rejects inline NBT under the
   selected `minecraft:core@26.2` profile.
3. Checks the *separately sourced*, already frozen
   `26.2-runtime-crosschecked-biome-ordinal-candidate.json` against
   the source and server locks, exact protocol/data version,
   profile name, 66 count, observed byId/getId/wire digest
   `97cba53b1bfd18870a345a42cea14e665e0a59f559dba939bec95cdf6fa5373d`,
   and explicit `SOURCE_SEM_ADMISSION_PENDING` authority label.
4. Compares every actual transmitted **ordinal** against the exact
   frozen runtime-ID candidate. A single swapped name, missing
   registry, duplicate packet, wrong known-pack identity or changed
   source/server lock rejects packing **before** any R1X image is written.

This uses neither name sorting nor inferred ID arithmetic. The
runtime candidate came from direct official loaded-registry
`byId/getId/getKey` enumeration compared to an independent live
Configuration observation; the R1X packet body comes from the pinned
**selected** immutable capture. These are different evidence
paths now explicitly bound in one pack-time check.

## Where it stops

The runtime candidate is *not* a source/SEM certificate for stock
client-side registry assignment. Successful pack-time equality does
not prove the receiver's selected known-packs handshake, async
registration/error paths, actual `MappedRegistry` concrete dispatch,
or that the client's Play biome palette reads precisely those numeric
IDs. This is still a required independent source/VAR/SEM gate.

Nor does a successful R1X build give permission to construct
`R2cSourceAdmission`: outer chunk/light publication, 32,366-state
heightmap semantics and first real client observation remain separate.

No new runtime registry, HOT lookup, biome-name vector retained in
world memory or production capability exists. The guard is a
source-free Python tool used once by the **COLD developer packer**
and imports the established wire decoder rather than implementing
a second parser.
