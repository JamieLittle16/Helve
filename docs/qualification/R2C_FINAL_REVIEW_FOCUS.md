# R2C final source review: consume verified inventories, not a second source scan

The 17 October 2026 parallel review passed its **discovery** stage. The independently
verified manifest binds the official Minecraft Java 26.2 source archive
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`
to the loaded-biome and chunk-wire inventories. It also carries forward
**seven already independently admitted inner-wire VAR methods** from the existing
world-state gate. None of this authorizes a live chunk packet.

Use `tools/r2c_final_review_focus.py` to consume the existing three files,
verify their content-addressed receipts against the source-free prior admission,
and derive an exact **first-pass** reviewer agenda. It selects 10 biome-registry
and 9 *new* outer-wire methods by pinned signature and normalized/body SHA-256.
The seven previously admitted methods are deliberately excluded.

```bash
python3 tools/r2c_final_review_focus.py \
  --manifest /tmp/helve-r2c-source-review-<run>/review-frontier-manifest.json \
  --biome /tmp/helve-r2c-source-review-<run>/biome-client-id-source-inventory.json \
  --wire /tmp/helve-r2c-source-review-<run>/chunk-wire-source-inventory.json \
  --output "/tmp/helve-r2c-review-focus-$(date +%s).json"
```

All inputs remain outside the repo. Output is source-free, immutable by default
(the destination must not exist), and explicitly unadmitted. No source ZIP,
Atlas re-index or network implementation is required to produce this shortlist.

**These 19 methods are starting anchors, not a complete proof.** Inspect the
actual pinned Java implementations and reached delegates, including client
Configuration handler invocation, ordered asynchronous registration/exception
paths, block-entity absence and packet-codec identity, Play first-send ordering,
batch ACK and remote rate. The existing 32,366-entry heightmap oracle is a
**separate** predicate-source-review track and is not supplied by these
inventories. Extend the reviewed source set whenever an obligation reaches
outside these exact first-pass roots; never treat an absent delegate as proven.

Before constructing a production `R2cSourceAdmission` capability, separately
complete human source inspection, explicit VAR/SEM, an independent bound
Atlas gate, exact selected known-pack and saved-world qualification, and the
stock client visible-world test. Continue using `ColdImportedView`,
`SourceAdmittedPlayPublisher`, source receipts, and the **original R2B
session/driver**. Do not create another biome mapping, heightmap engine, egress
queue, or unreviewed production switch.
