# R2C World-State Semantics — Minecraft Java 26.2

> Generated from a human-authored, source-free admission worksheet. This file contains no
> official source text. Independent Vanilla Atlas admission is still required.

- Admission worksheet SHA-256: `feca34f7636374f369ec58f38e90ef0c062cf1527eea790d26ed467c8108077c`
- Source archive SHA-256: `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`
- Production admitted by this materialization: **no**

## R2C-BIOMES

### SEM-NET-R2C-WORLD-BIOME-SECTION-PLACEMENT

A serialized LevelChunkSection writes nonEmptyBlockCount, fluidCount, the block-state paletted container, and then the biome paletted container in that order.

Source support:
- `net.minecraft.world.level.chunk.LevelChunkSection#write(final FriendlyByteBuf buffer)`

### SEM-NET-R2C-WORLD-BIOME-REGISTRY-FACTORY

The 26.2 biome container is built over the BIOME registry holder-id map; the factory derives the biome strategy from that global id map and uses Plains as the default biome for a new biome container.

Source support:
- `net.minecraft.world.level.chunk.PalettedContainerFactory#create(final RegistryAccess registries)`
- `net.minecraft.world.level.chunk.PalettedContainerFactory#createForBiomes()`

### SEM-NET-R2C-WORLD-BIOME-LATTICE

The biome strategy uses two bits per spatial axis, contains 64 logical entries, and maps local quart coordinates to index ((y << 2) | z) << 2 | x.

Source support:
- `net.minecraft.world.level.chunk.Strategy#Strategy(final IdMap < T > globalMap , final int bitsPerAxis)`
- `net.minecraft.world.level.chunk.Strategy#createForBiomes(final IdMap < T > registry)`
- `net.minecraft.world.level.chunk.Strategy#getIndex(final int x , final int y , final int z)`

### SEM-NET-R2C-WORLD-BIOME-PALETTE-MODES

For biome containers, the required palette width is ceil(log2(distinct palette values)): width 0 uses the single-value configuration, widths 1 through 3 use linear local palettes, and larger widths use the registry-backed global configuration; hash-map palette modes are not selected by the biome strategy.

Source support:
- `net.minecraft.world.level.chunk.Strategy#<clinit>()`
- `net.minecraft.world.level.chunk.Strategy#createForBiomes(final IdMap < T > registry)`
- `net.minecraft.world.level.chunk.Strategy#getConfigurationForPaletteSize(final int paletteSize)`
- `net.minecraft.world.level.chunk.Strategy#minimumBitsRequiredForDistinctValues(final int count)`
- `net.minecraft.world.level.chunk.Configuration#Global(int bitsInMemory , int bitsInStorage)`
- `net.minecraft.world.level.chunk.Configuration#Simple(Palette . Factory factory , int bits)`

### SEM-NET-R2C-WORLD-BIOME-PALETTE-WIRE

A single-value biome palette writes one global-registry id VarInt; a linear biome palette writes its cardinality VarInt followed by that many global-registry id VarInts; a global palette writes no palette bytes and uses registry ids as palette indices.

Source support:
- `net.minecraft.world.level.chunk.SingleValuePalette#write(final FriendlyByteBuf buffer , final IdMap < T > globalMap)`
- `net.minecraft.world.level.chunk.LinearPalette#write(final FriendlyByteBuf buffer , final IdMap < T > globalMap)`
- `net.minecraft.world.level.chunk.LinearPalette#idFor(final T value , final PaletteResize < T > resizeHandler)`
- `net.minecraft.world.level.chunk.GlobalPalette#write(final FriendlyByteBuf buffer , final IdMap < T > globalMap)`
- `net.minecraft.world.level.chunk.GlobalPalette#idFor(final T value , final PaletteResize < T > resizeHandler)`
- `net.minecraft.world.level.chunk.GlobalPalette#valueFor(final int index)`

### SEM-NET-R2C-WORLD-BIOME-CONTAINER-WIRE

PalettedContainer network output delegates to its current data; the data writes one storage-bit-width byte, then the selected palette representation, then the raw storage words as a fixed-size long array using the strategy global id map.

Source support:
- `net.minecraft.world.level.chunk.PalettedContainer#write(final FriendlyByteBuf buffer)`
- `net.minecraft.world.level.chunk.PalettedContainer$Data#write(final FriendlyByteBuf buffer , final IdMap < T > globalMap)`

### SEM-NET-R2C-WORLD-BIOME-PACKED-STORAGE

Positive-width SimpleBitStorage packs floor(64/bits) non-spanning values per 64-bit word; logical index i occupies bit offset (i mod valuesPerLong)*bits in word floor(i/valuesPerLong), the required raw length is ceil(size/valuesPerLong), and the raw accessor exposes those words directly.

Source support:
- `net.minecraft.util.SimpleBitStorage#SimpleBitStorage(final int bits , final int size , final long @ Nullable [ ] data)`
- `net.minecraft.util.SimpleBitStorage#set(final int index , final int value)`
- `net.minecraft.util.SimpleBitStorage#getRaw()`

## R2C-HEIGHTMAPS

### SEM-NET-R2C-WORLD-HEIGHTMAP-CLIENT-TYPES

The 26.2 clientbound heightmap set is exactly WORLD_SURFACE (id 1), MOTION_BLOCKING (id 4), and MOTION_BLOCKING_NO_LEAVES (id 5), because those are the Heightmap.Types entries with CLIENT usage and sendToClient returns true only for CLIENT usage.

Source support:
- `net.minecraft.world.level.levelgen.Heightmap$Types#<clinit>()`
- `net.minecraft.world.level.levelgen.Heightmap$Types#sendToClient()`

### SEM-NET-R2C-WORLD-HEIGHTMAP-PREDICATES

WORLD_SURFACE accepts non-air blocks; MOTION_BLOCKING accepts a state that blocks motion or has non-empty fluid; MOTION_BLOCKING_NO_LEAVES applies the same test and additionally excludes leaves.

Source support:
- `net.minecraft.world.level.levelgen.Heightmap#<clinit>()`
- `net.minecraft.world.level.levelgen.Heightmap$Types#<clinit>()`
- `net.minecraft.world.level.levelgen.Heightmap$Types#isOpaque()`

### SEM-NET-R2C-WORLD-HEIGHTMAP-STORAGE

Each heightmap contains 256 local columns with index x + 16*z and packed width ceil(log2(chunkHeight+1)); stored values are first-available Y relative to chunk minY, and getFirstAvailable adds minY back.

Source support:
- `net.minecraft.world.level.levelgen.Heightmap#Heightmap(final ChunkAccess chunk , final Heightmap . Types heightmapType)`
- `net.minecraft.world.level.levelgen.Heightmap#getIndex(final int x , final int z)`
- `net.minecraft.world.level.levelgen.Heightmap#setHeight(final int x , final int z , final int height)`
- `net.minecraft.world.level.levelgen.Heightmap#getFirstAvailable(final int index)`
- `net.minecraft.world.level.levelgen.Heightmap#getRawData()`

### SEM-NET-R2C-WORLD-HEIGHTMAP-PRIMING

Heightmap priming scans each local x/z column downward from the highest available section and stores y+1 for each requested type at the first state satisfying that type predicate; a type with no matching state remains at its zero value, corresponding to minY.

Source support:
- `net.minecraft.world.level.levelgen.Heightmap#primeHeightmaps(final ChunkAccess chunk , final Set < Heightmap . Types > types)`
- `net.minecraft.world.level.levelgen.Heightmap#setHeight(final int x , final int z , final int height)`
- `net.minecraft.world.level.levelgen.Heightmap#getFirstAvailable(final int index)`

### SEM-NET-R2C-WORLD-HEIGHTMAP-WIRE

ClientboundLevelChunkPacketData snapshots only sendToClient heightmaps by cloning each raw long array; its heightmap field is encoded as a Heightmap.Types-to-long-array map before the section byte buffer and block-entity list.

Source support:
- `net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData#<clinit>()`
- `net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData#ClientboundLevelChunkPacketData(final LevelChunk levelChunk)`
- `net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData#write(final RegistryFriendlyByteBuf output)`

## R2C-LIGHT

### SEM-NET-R2C-WORLD-LIGHT-PERSISTED-IMPORT

Persisted chunk parsing reads isLightOn as a boolean defaulting false and independently reads optional BlockLight and SkyLight section byte arrays; a present array constructs a DataLayer and an absent tag yields no layer.

Source support:
- `net.minecraft.world.level.chunk.storage.SerializableChunkData#parse(final LevelHeightAccessor levelHeight , final PalettedContainerFactory containerFactory , final CompoundTag chunkData)`
- `net.minecraft.world.level.chunk.DataLayer#DataLayer(final byte [ ] data)`

### SEM-NET-R2C-WORLD-LIGHT-RECONSTRUCTION

Chunk reconstruction queues every present block-light DataLayer and, only when the dimension has sky light, every present sky-light DataLayer into the light engine, then copies the persisted lightCorrect value into the chunk.

Source support:
- `net.minecraft.world.level.chunk.storage.SerializableChunkData#read(final ServerLevel level , final PoiManager poiManager , final RegionStorageInfo regionInfo , final ChunkPos pos)`

### SEM-NET-R2C-WORLD-LIGHT-LATTICE

The light lattice has dimension section count plus two entries. getMinLightSection is minSectionY-1, getMaxLightSection is the exclusive end, and clientbound light section index i addresses section minLightSection+i.

Source support:
- `net.minecraft.world.level.lighting.LevelLightEngine#getLightSectionCount()`
- `net.minecraft.world.level.lighting.LevelLightEngine#getMinLightSection()`
- `net.minecraft.world.level.lighting.LevelLightEngine#getMaxLightSection()`
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#ClientboundLightUpdatePacketData(final ChunkPos chunkPos , final LevelLightEngine lightEngine , final @ Nullable BitSet skyChangedLightSectionFilter , final @ Nullable BitSet blockChangedLightSectionFilter)`
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#prepareSectionData(final ChunkPos pos , final LevelLightEngine lightEngine , final LightLayer layer , final int sectionIndex , final BitSet mask , final BitSet emptyMask , final List < byte [ ] > updates)`

### SEM-NET-R2C-WORLD-LIGHT-LAYER-LOOKUP

LevelLightEngine chooses the block or sky listener for the requested LightLayer; the concrete LightEngine converts SectionPos to its packed section key and LayerLightSectionStorage returns queued data when present, otherwise visible stored layer data.

Source support:
- `net.minecraft.world.level.lighting.LevelLightEngine#getLayerListener(final LightLayer layer)`
- `net.minecraft.world.level.lighting.LightEngine#getDataLayerData(final SectionPos pos)`
- `net.minecraft.world.level.lighting.LayerLightSectionStorage#getDataLayerData(final long sectionNode)`

### SEM-NET-R2C-WORLD-LIGHT-DATALAYER

A DataLayer represents 4096 four-bit cells in exactly 2048 raw bytes. Logical index is y*256 + z*16 + x; even indices occupy the low nibble and odd indices the high nibble. Raw construction rejects any byte length other than 2048.

Source support:
- `net.minecraft.world.level.chunk.DataLayer#DataLayer(final byte [ ] data)`
- `net.minecraft.world.level.chunk.DataLayer#get(final int x , final int y , final int z)`
- `net.minecraft.world.level.chunk.DataLayer#set(final int x , final int y , final int z , final int val)`
- `net.minecraft.world.level.chunk.DataLayer#getIndex(final int x , final int y , final int z)`
- `net.minecraft.world.level.chunk.DataLayer#getByteIndex(final int position)`
- `net.minecraft.world.level.chunk.DataLayer#getNibbleIndex(final int index)`

### SEM-NET-R2C-WORLD-LIGHT-HOMOGENEOUS-LAYER

A homogeneous DataLayer may remain unmaterialized as a default nibble; it is empty exactly when unmaterialized with default zero. Copying preserves an unmaterialized default, while getData materializes 2048 bytes and repeats a nonzero default into both nibbles of each byte.

Source support:
- `net.minecraft.world.level.chunk.DataLayer#DataLayer(final int defaultValue)`
- `net.minecraft.world.level.chunk.DataLayer#isEmpty()`
- `net.minecraft.world.level.chunk.DataLayer#copy()`
- `net.minecraft.world.level.chunk.DataLayer#getData()`
- `net.minecraft.world.level.chunk.DataLayer#packFilled(final int value)`

### SEM-NET-R2C-WORLD-LIGHT-MASK-CLASSIFICATION

For each considered light section, a null DataLayer contributes no data or empty bit; an empty present layer sets the corresponding empty mask; a non-empty present layer sets the corresponding data mask and appends a copied 2048-byte layer update. Null changed-section filters consider every light-section index.

Source support:
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#ClientboundLightUpdatePacketData(final ChunkPos chunkPos , final LevelLightEngine lightEngine , final @ Nullable BitSet skyChangedLightSectionFilter , final @ Nullable BitSet blockChangedLightSectionFilter)`
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#prepareSectionData(final ChunkPos pos , final LevelLightEngine lightEngine , final LightLayer layer , final int sectionIndex , final BitSet mask , final BitSet emptyMask , final List < byte [ ] > updates)`
- `net.minecraft.world.level.chunk.DataLayer#isEmpty()`
- `net.minecraft.world.level.chunk.DataLayer#copy()`
- `net.minecraft.world.level.chunk.DataLayer#getData()`

### SEM-NET-R2C-WORLD-LIGHT-WIRE

Clientbound light data writes sky-present mask, block-present mask, empty-sky mask, empty-block mask, then the sky update collection and block update collection; each layer update uses the 2048-byte-bounded data-layer codec.

Source support:
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#<clinit>()`
- `net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData#write(final FriendlyByteBuf output)`
