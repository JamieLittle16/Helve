use helve_types::{ChunkGeneration, ChunkPos, DimensionId};
use helve_world_chunk::{
    ChunkBiomeColumn, ChunkBiomeColumnError, ChunkCoreError, ChunkSemanticStateError, LiveChunkCore,
    LiveChunkSemanticState,
};
use helve_world_contract::{BiomeSection, BlockSection};

use crate::{DimensionRuntimeProfile, ResidentChunkAccessError, ResidentChunkHandle};
use crate::resident::{ResidentAdmissionError, ResidentChunkIdentity, ResidentDirectory};

/// COLD/BOUNDARY failures while admitting one coherent block+biome resident chunk.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LoadSemanticChunkError {
    /// The semantic position is already resident in this dimension.
    AlreadyResident {
        /// Existing resident identity.
        handle: ResidentChunkHandle,
    },
    /// Supplied block-section count differs from the frozen dimension lattice.
    BlockSectionCountMismatch {
        /// Required logical section count.
        expected: usize,
        /// Supplied block-section count.
        actual: usize,
    },
    /// Supplied biome-section count differs from the frozen dimension lattice.
    BiomeSectionCountMismatch {
        /// Required logical section count.
        expected: usize,
        /// Supplied biome-section count.
        actual: usize,
    },
    /// The process-local chunk generation sequence is exhausted.
    GenerationExhausted,
    /// Block-core construction failed.
    Blocks(ChunkCoreError),
    /// Biome-column construction failed.
    Biomes(ChunkBiomeColumnError),
    /// Final block/biome coherence validation failed.
    Semantic(ChunkSemanticStateError),
}

impl<S, BlockStorage, B, BiomeStorage> ResidentChunkIdentity
    for LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    fn generation(&self) -> ChunkGeneration {
        LiveChunkSemanticState::generation(self)
    }
}

/// Loaded dimension whose resident authority is coherent block + biome semantic state.
///
/// This is the R2C structural bridge from the block-only bootstrap runtime to the eventual complete
/// semantic chunk owner. It reuses the exact same sparse [`ResidentDirectory`] as
/// [`crate::DimensionInstance`]; there is no second lifecycle map, generation allocator or stale
/// handle implementation.
///
/// The type is target-neutral. `B` is an already-resolved semantic biome identity chosen by the
/// caller; this layer knows nothing about Minecraft registry ids, palette widths or packet law.
#[derive(Debug)]
pub struct SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    profile: DimensionRuntimeProfile,
    resident: ResidentDirectory<LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>>,
}

impl<S, BlockStorage, B, BiomeStorage>
    SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    /// Creates an empty coherent loaded dimension without pre-reserving directory storage.
    #[must_use]
    pub fn new(id: DimensionId, profile: DimensionRuntimeProfile) -> Self {
        Self::with_chunk_capacity(id, profile, 0)
    }

    /// Creates an empty coherent loaded dimension with a COLD directory capacity hint.
    #[must_use]
    pub fn with_chunk_capacity(
        id: DimensionId,
        profile: DimensionRuntimeProfile,
        chunk_capacity: usize,
    ) -> Self {
        Self {
            profile,
            resident: ResidentDirectory::with_capacity(id, chunk_capacity),
        }
    }

    /// Compact process-local identity of this loaded dimension instance.
    #[must_use]
    pub const fn id(&self) -> DimensionId {
        self.resident.id()
    }

    /// Pre-resolved immutable dimension facts.
    #[must_use]
    pub const fn profile(&self) -> DimensionRuntimeProfile {
        self.profile
    }

    /// Number of currently resident semantic chunks.
    #[must_use]
    pub fn resident_chunk_count(&self) -> usize {
        self.resident.len()
    }

    /// Discovers the exact current handle for one resident semantic position.
    #[must_use]
    pub fn discover_chunk(&self, position: ChunkPos) -> Option<ResidentChunkHandle> {
        self.resident.discover(position)
    }

    /// Installs one coherent block+biome chunk incarnation through one sparse-directory probe.
    ///
    /// Duplicate residency is checked before component validation/construction. Both component
    /// vectors must exactly match the frozen dimension lattice. The directory supplies one generation
    /// to both constructors; final composition then validates position, generation and lattice again
    /// before insertion. Generation advances only after the whole composite is constructed.
    ///
    /// # Errors
    ///
    /// Returns a fail-closed error for duplicate residency, component-count mismatch, generation
    /// exhaustion or any block/biome/composite construction failure.
    pub fn load_chunk(
        &mut self,
        position: ChunkPos,
        block_sections: Vec<BlockStorage>,
        biome_sections: Vec<BiomeStorage>,
    ) -> Result<ResidentChunkHandle, LoadSemanticChunkError> {
        let profile = self.profile;
        match self.resident.admit_with(position, move |generation| {
            let expected = profile.section_count();
            if block_sections.len() != expected {
                return Err(LoadSemanticChunkError::BlockSectionCountMismatch {
                    expected,
                    actual: block_sections.len(),
                });
            }
            if biome_sections.len() != expected {
                return Err(LoadSemanticChunkError::BiomeSectionCountMismatch {
                    expected,
                    actual: biome_sections.len(),
                });
            }

            let blocks = LiveChunkCore::new(
                position,
                generation,
                profile.min_section_y(),
                block_sections,
            )
            .map_err(LoadSemanticChunkError::Blocks)?;
            let biomes = ChunkBiomeColumn::new(
                position,
                generation,
                profile.min_section_y(),
                biome_sections,
            )
            .map_err(LoadSemanticChunkError::Biomes)?;
            LiveChunkSemanticState::from_parts(blocks, biomes)
                .map_err(LoadSemanticChunkError::Semantic)
        }) {
            Ok(handle) => Ok(handle),
            Err(ResidentAdmissionError::AlreadyResident { handle }) => {
                Err(LoadSemanticChunkError::AlreadyResident { handle })
            }
            Err(ResidentAdmissionError::GenerationExhausted) => {
                Err(LoadSemanticChunkError::GenerationExhausted)
            }
            Err(ResidentAdmissionError::Build(error)) => Err(error),
        }
    }

    /// Resolves an already-known handle to direct immutable coherent chunk access.
    ///
    /// # Errors
    ///
    /// Rejects wrong-dimension, unloaded and stale-generation handles.
    pub fn resolve_chunk(
        &self,
        handle: ResidentChunkHandle,
    ) -> Result<&LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>, ResidentChunkAccessError>
    {
        self.resident.resolve(handle)
    }

    /// Resolves an already-known handle to direct authoritative coherent chunk mutation.
    ///
    /// # Errors
    ///
    /// Rejects wrong-dimension, unloaded and stale-generation handles.
    pub fn resolve_chunk_mut(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<
        &mut LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
        ResidentChunkAccessError,
    > {
        self.resident.resolve_mut(handle)
    }

    /// Removes exactly the named coherent chunk incarnation and returns its semantic state.
    ///
    /// # Errors
    ///
    /// Rejects wrong-dimension, unloaded and stale-generation handles without changing residency.
    pub fn unload_chunk(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<
        LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
        ResidentChunkAccessError,
    > {
        self.resident.unload(handle)
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, ChunkRevision, DimensionId, DimensionTypeId};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use crate::{DimensionRuntimeProfile, ResidentChunkAccessError};

    use super::{LoadSemanticChunkError, SemanticDimensionInstance};

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Block {
        Air,
        Stone,
    }

    struct Facts;

    impl BlockStateFacts<Block> for Facts {
        fn facts(&self, state: Block) -> SectionStateFacts {
            match state {
                Block::Air => SectionStateFacts::new(false, false, false, false),
                Block::Stone => SectionStateFacts::new(true, false, false, false),
            }
        }
    }

    type Blocks = DirectBlockSection<Block>;
    type Biomes = DirectBiomeSection<u16>;
    type Dimension = SemanticDimensionInstance<Block, Blocks, u16, Biomes>;

    fn profile() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(2), -16, 32, true)
            .expect("two-section coherent dimension")
    }

    fn block_sections(count: usize) -> Vec<Blocks> {
        (0..count)
            .map(|_| DirectBlockSection::filled(Block::Air, &Facts))
            .collect()
    }

    fn biome_sections(count: usize) -> Vec<Biomes> {
        (0..count)
            .map(|_| DirectBiomeSection::filled(7_u16))
            .collect()
    }

    fn biome_pos() -> SectionBiomePos {
        SectionBiomePos::new(2, 1, 3).expect("bounded quart-biome coordinate")
    }

    #[test]
    fn resident_block_and_biome_mutations_share_one_revision() {
        let profile = profile();
        let mut dimension = Dimension::new(DimensionId(3), profile);
        let position = ChunkPos { x: 0, z: 0 };
        let handle = dimension
            .load_chunk(
                position,
                block_sections(profile.section_count()),
                biome_sections(profile.section_count()),
            )
            .expect("coherent chunk load");
        assert_eq!(handle.generation, ChunkGeneration(1));

        let chunk = dimension.resolve_chunk_mut(handle).expect("current handle");
        assert_eq!(chunk.revision(), ChunkRevision(0));
        let block = BlockPos { x: 1, y: -16, z: 2 };
        assert!(
            chunk
                .replace_block(block, Block::Stone, &Facts)
                .expect("block mutation")
                .changed
        );
        assert_eq!(chunk.revision(), ChunkRevision(1));
        assert!(
            chunk
                .replace_biome(-1, biome_pos(), 9)
                .expect("biome mutation")
                .changed
        );
        assert_eq!(chunk.revision(), ChunkRevision(2));
        assert_eq!(chunk.get_block(block), Ok(Block::Stone));
        assert_eq!(chunk.get_biome(-1, biome_pos()), Ok(9));
    }

    #[test]
    fn failed_component_validation_does_not_consume_generation() {
        let profile = profile();
        let mut dimension = Dimension::new(DimensionId(4), profile);
        let position = ChunkPos { x: 0, z: 0 };
        assert_eq!(
            dimension.load_chunk(position, block_sections(1), biome_sections(2)),
            Err(LoadSemanticChunkError::BlockSectionCountMismatch {
                expected: 2,
                actual: 1,
            })
        );

        let handle = dimension
            .load_chunk(position, block_sections(2), biome_sections(2))
            .expect("valid load after rejected construction");
        assert_eq!(handle.generation, ChunkGeneration(1));
    }

    #[test]
    fn unload_reload_keeps_stale_handle_rejection_for_composite_state() {
        let profile = profile();
        let mut dimension = Dimension::new(DimensionId(5), profile);
        let position = ChunkPos { x: -2, z: 3 };
        let first = dimension
            .load_chunk(position, block_sections(2), biome_sections(2))
            .expect("first coherent load");
        dimension.unload_chunk(first).expect("first unload");
        let second = dimension
            .load_chunk(position, block_sections(2), biome_sections(2))
            .expect("coherent reload");
        assert_eq!(second.generation, ChunkGeneration(first.generation.0 + 1));
        assert!(matches!(
            dimension.resolve_chunk(first),
            Err(ResidentChunkAccessError::StaleGeneration { current, handle, .. })
                if current == second.generation && handle == first.generation
        ));
        assert!(dimension.resolve_chunk(second).is_ok());
    }
}
