# Helve — actual Minecraft Java 26.2 stock HolderHolder binding frontier

**20 October 2026. Structural discovery only, source/VAR/SEM and production gates closed.**

## Independently observed official depth-four graph

The user's real stock four-seed `--router-graph-4` capture succeeded:
**141,287 bytes**, SHA-256
`5911470e36725da99e7b82b5b8b4eef03a1d150662aa44c71b6c64340e4a46fb`.
For each signed world seed it observed exactly 42 identity-unique
DensityFunctions nodes, 31 typed density edges and 85 declared opaque
record components. This is 168 node observations, 124 edges, 340 opaque
slots across four independent seeds, all with the same declared shape.
Six nodes per seed were stopped, uninspected, at exactly depth 4.

The actual `finalDensity` path is:
`Ap2(argument1 = Mapped(input = Marker(wrapped = MulOrAdd(input = Marker[cutoff]))), argument2 = HolderHolder(function = Holder[opaque]))`.
The class and relationships are independently **observed**; no
`Ap2` opcode value, `Mapped` transform enum, `Marker` cache policy,
or holder-reached semantic meaning is inferred from class names.

The most prominent remaining *structural* boundary is the actual
`DensityFunctions$HolderHolder` record. Its single declared component
is `function: net.minecraft.core.Holder`, not another
`DensityFunction` record slot. The previous typed graph walker
correctly leaves it opaque. Across each seed, exactly eight of the 42
observed nodes are `HolderHolder`, including the final-density second
argument and climate roots.

## Narrowly inspect the real stock binding, not an invented registry

The new separate `--router-holder-4` mode keeps the **exact previous
graph frames** and additionally visits *only* actual, exact-name
`DensityFunctions$HolderHolder` objects already in that bounded graph:

1. Verify that record has exactly one component named `function` with
   the exact `net.minecraft.core.Holder` declared type.
2. Invoke only the *typed* public `Holder.value()` method on that
   original holder object. This may resolve the actual registered
   density function value. Demand it is a `DensityFunction` and
   record its concrete `Class.getName()` and actual `compute`
   declaring class, but **never invoke compute or descend into the
   returned object**.
3. Record the runtime holder implementation class, original graph
   node ID and original graph depth for each bound item. At most 64
   holder rows per seed.
4. The source-owning collector strictly requires the 141,287-byte
   previous graph JSON with the SHA above, the original 28,439-byte
   root receipt and the 15-root SHA fixture. It checks the pinned
   official 26.2 archive, JAR, old router methods and independently
   indexes `HolderHolder.compute` with `reviewed: false`.
5. The collector **rechecks the entire stock graph output bit-for-bit
   structurally** (node identity/edges/opaque fields) against the
   previous accepted JSON, then checks exactly the previously observed
   eight HolderHolder node IDs per seed, in order, their method owner
   and output shape. Out-of-order/missing/extra holder rows refuse.

No source, JAR, private database, source snippets, noise payload,
graph-disassembly or copyrighted code is exported. The source-free
JSON is exclusively written outside the repository with permissions
0600. The probes do not alter actual Minecraft server classes,
construct synthetic holders, request global Java module opens, or
add runtime worldgen/sampling overhead to Helve.

CI uses a synthetic bound-holder implementation and Java reflection,
not a claim of independently observing Mojang's `Holder.value()`
result. The next official JVM run is required.

## Source-owning command

Run from the existing checkout. Both earlier files must be present
at the exact previous output paths and unchanged:

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_router_holder_capture.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --roots /tmp/helve-26_2-stock-router-roots-4.json \
  --graph /tmp/helve-26_2-stock-router-graph-depth4.json \
  --output /tmp/helve-26_2-stock-router-bound-holders-4.json
```

Upload only the last source-free JSON, or the literal tagged error if
the original bound Holder API differs. The destination file must not
already exist.

## What remains after this step

Source review of `HolderHolder.compute` and the actual reached
wrapper/holder semantic resolution is necessary before compiling the
nested graph. A true stock `finalDensity` numerical oracle must then
be acquired with 26.2-correct sampling contexts and cache/interpolation
rules; scalar `SinglePointContext` results cannot by themselves
certify the proper `NoiseChunk` path. The already qualified Rust noise
engine and typed composition facilities must be reused for any
independently admitted nodes rather than introducing a duplicate
sampler, cache, registry or world lifetime owner.

`full_router_graph_qualified=false`,
`router_numeric_parity_qualified=false`,
`world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false`,
`production_worldgen_enabled=false`.
