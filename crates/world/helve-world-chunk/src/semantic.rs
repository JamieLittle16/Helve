use helve_types::{BlockPos, ChunkGeneration, ChunkPos, ChunkRevision, ChunkStamp};
use helve_world_contract::{BiomeSection, BlockSection, BlockStateFacts, SectionBiomePos};

use crate::{
    ChunkBiomeColumn, ChunkBiomeColumnError, ChunkCoreError, LiveChunkCore, MutationFacts,
    SectionMasks, VerticalSectionLattice,
};

/// One authoritative biome mutation committed through [`LiveChunkSemanticState`].
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BiomeMutationFacts<B: Copy + Eq> {
    /// Logical section containing the quart-biome cell.
    pub section_y: i32,
    /// Section-local 4×4×4 biome coordinate.
    pub local: SectionBiomePos,
    /// Exact biome present before the operation.
    pub old: B,
    /// Requested replacement biome.
    pub new: B,
    /// Whether the semantic biome image actually changed.
    pub changed: bool,
}

/// Fail-closed composition/access errors for [`LiveChunkSemanticState`].
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ChunkSemanticStateError {
    /// Block and biome components describe different semantic chunk positions.
    PositionMismatch {
        /// Position owned by the block core.
        blocks: ChunkPos,
        /// Position owned by the biome column.
        biomes: ChunkPos,
    },
    /// Block and biome components belong to different live chunk incarnations.
    GenerationMismatch {
        /// Generation owned by the block core.
        blocks: ChunkGeneration,
        /// Generation owned by the biome column.
        biomes: ChunkGeneration,
    },
    /// Block and biome components describe different vertical section lattices.
    LatticeMismatch {
        /// Lattice owned by the block core.
        blocks: VerticalSectionLattice,
        /// Lattice owned by the biome column.
        biomes: VerticalSectionLattice,
    },
    /// Block access or mutation failed.
    Blocks(ChunkCoreError),
    /// Biome access or mutation failed.
    Biomes(ChunkBiomeColumnError),
}

impl From<ChunkCoreError> for ChunkSemanticStateError {
    fn from(value: ChunkCoreError) -> Self {
        Self::Blocks(value)
    }
}

impl From<ChunkBiomeColumnError> for ChunkSemanticStateError {
    fn from(value: ChunkBiomeColumnError) -> Self {
        Self::Biomes(value)
    }
}

/// Coherent target-neutral semantic state for one live chunk incarnation.
///
/// This is the R2C whole-chunk freshness baseline. The existing block core remains the sole owner
/// of the generation-local [`ChunkRevision`]; biome mutations advance that same clock rather than
/// introducing an independently drifting sidecar revision. Heightmap, light and block-entity state
/// can join this owner after their own semantic admission without changing the freshness law.
///
/// Composition consumes already-final block/biome components and performs no allocation or per-cell
/// copy. The component position, generation and vertical lattice must match exactly before ownership
/// is accepted. Mutable component references are intentionally not exposed: all semantic mutation
/// must pass through this type so one real change advances the shared revision exactly once.
#[derive(Debug)]
pub struct LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    blocks: LiveChunkCore<S, BlockStorage>,
    biomes: ChunkBiomeColumn<B, BiomeStorage>,
}

impl<S, BlockStorage, B, BiomeStorage> LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    /// Composes already-owned block and biome state under one authoritative freshness clock.
    ///
    /// This operation is O(1): it validates identity/lattice metadata and moves the existing owned
    /// components without allocating or rebuilding either semantic image.
    ///
    /// # Errors
    ///
    /// Rejects position, generation or vertical-lattice mismatch without modifying either input.
    pub fn from_parts(
        blocks: LiveChunkCore<S, BlockStorage>,
        biomes: ChunkBiomeColumn<B, BiomeStorage>,
    ) -> Result<Self, ChunkSemanticStateError> {
        if blocks.position() != biomes.position() {
            return Err(ChunkSemanticStateError::PositionMismatch {
                blocks: blocks.position(),
                biomes: biomes.position(),
            });
        }
        if blocks.generation() != biomes.generation() {
            return Err(ChunkSemanticStateError::GenerationMismatch {
                blocks: blocks.generation(),
                biomes: biomes.generation(),
            });
        }
        if blocks.vertical_lattice() != biomes.vertical_lattice() {
            return Err(ChunkSemanticStateError::LatticeMismatch {
                blocks: blocks.vertical_lattice(),
                biomes: biomes.vertical_lattice(),
            });
        }
        Ok(Self { blocks, biomes })
    }

    /// Semantic chunk-column position shared by every component.
    #[must_use]
    pub const fn position(&self) -> ChunkPos {
        self.blocks.position()
    }

    /// Identity of this live chunk incarnation.
    #[must_use]
    pub const fn generation(&self) -> ChunkGeneration {
        self.blocks.generation()
    }

    /// Current whole-chunk semantic revision.
    #[must_use]
    pub const fn revision(&self) -> ChunkRevision {
        self.blocks.revision()
    }

    /// Exact generation/revision identity for deferred projection freshness checks.
    #[must_use]
    pub const fn stamp(&self) -> ChunkStamp {
        self.blocks.stamp()
    }

    /// Shared validated vertical section lattice.
    #[must_use]
    pub const fn vertical_lattice(&self) -> VerticalSectionLattice {
        self.blocks.vertical_lattice()
    }

    /// Number of contiguous logical sections in both block and biome state.
    #[must_use]
    pub fn section_count(&self) -> usize {
        self.blocks.section_count()
    }

    /// Incrementally maintained block-section summary masks.
    #[must_use]
    pub const fn block_masks(&self) -> SectionMasks {
        self.blocks.masks()
    }

    /// Read-only access to the authoritative block component.
    ///
    /// Mutation is deliberately not exposed through this view; use [`Self::replace_block`] so the
    /// composite freshness contract cannot be bypassed.
    #[must_use]
    pub const fn blocks(&self) -> &LiveChunkCore<S, BlockStorage> {
        &self.blocks
    }

    /// Read-only access to the authoritative biome component.
    ///
    /// Mutation is deliberately not exposed through this view; use [`Self::replace_biome`] so the
    /// shared revision advances on every real semantic change.
    #[must_use]
    pub const fn biomes(&self) -> &ChunkBiomeColumn<B, BiomeStorage> {
        &self.biomes
    }

    /// Reads one exact semantic block state.
    ///
    /// # Errors
    ///
    /// Propagates the block core's fail-closed chunk/lattice access error.
    pub fn get_block(&self, pos: BlockPos) -> Result<S, ChunkSemanticStateError> {
        Ok(self.blocks.get_block(pos)?)
    }

    /// Performs one authoritative block replacement under the shared whole-chunk revision.
    ///
    /// The underlying block core already advances the revision exactly once for a real change and
    /// not at all for same-state replacement, so this wrapper adds no second clock or bookkeeping.
    ///
    /// # Errors
    ///
    /// Propagates the block core's fail-closed chunk/lattice access error.
    pub fn replace_block<F: BlockStateFacts<S>>(
        &mut self,
        pos: BlockPos,
        state: S,
        facts: &F,
    ) -> Result<MutationFacts<S>, ChunkSemanticStateError> {
        Ok(self.blocks.replace_block(pos, state, facts)?)
    }

    /// Reads one exact semantic biome from the chunk's 4×4×4 section lattice.
    ///
    /// # Errors
    ///
    /// Propagates the biome column's fail-closed vertical-lattice access error.
    pub fn get_biome(
        &self,
        section_y: i32,
        local: SectionBiomePos,
    ) -> Result<B, ChunkSemanticStateError> {
        Ok(self.biomes.get(section_y, local)?)
    }

    /// Performs one authoritative biome replacement under the shared whole-chunk revision.
    ///
    /// Same-biome replacement is a semantic no-op and leaves the revision unchanged. A real biome
    /// change advances the exact same revision used by block mutation, exactly once and without any
    /// allocation, scan, hash lookup or projection work.
    ///
    /// # Errors
    ///
    /// Propagates the biome column's fail-closed vertical-lattice access error. Rejected operations
    /// do not advance the revision.
    pub fn replace_biome(
        &mut self,
        section_y: i32,
        local: SectionBiomePos,
        biome: B,
    ) -> Result<BiomeMutationFacts<B>, ChunkSemanticStateError> {
        let previous = self.biomes.replace(section_y, local, biome)?;
        let changed = previous != biome;
        if changed {
            self.blocks.advance_semantic_revision();
        }
        Ok(BiomeMutationFacts {
            section_y,
            local,
            old: previous,
            new: biome,
            changed,
        })
    }

    /// Decomposes the coherent owner back into its already-owned semantic components.
    ///
    /// No copy or allocation occurs. This is intended for lifecycle/persistence boundaries, not for
    /// ordinary mutation where splitting authority would defeat the freshness contract.
    #[must_use]
    pub fn into_parts(
        self,
    ) -> (
        LiveChunkCore<S, BlockStorage>,
        ChunkBiomeColumn<B, BiomeStorage>,
    ) {
        (self.blocks, self.biomes)
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, ChunkRevision};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use crate::{
        ChunkBiomeColumn, ChunkSemanticStateError, LiveChunkCore, LiveChunkSemanticState,
        VerticalSectionLattice,
    };

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
    type Semantic = LiveChunkSemanticState<Block, Blocks, u16, Biomes>;

    fn biome_pos(x: u8, y: u8, z: u8) -> SectionBiomePos {
        SectionBiomePos::new(x, y, z).expect("bounded biome position")
    }

    fn parts(
        position: ChunkPos,
        generation: ChunkGeneration,
        min_section_y: i32,
        count: usize,
    ) -> (LiveChunkCore<Block, Blocks>, ChunkBiomeColumn<u16, Biomes>) {
        let blocks = LiveChunkCore::new(
            position,
            generation,
            min_section_y,
            (0..count)
                .map(|_| DirectBlockSection::filled(Block::Air, &Facts))
                .collect(),
        )
        .expect("valid block core");
        let biomes = ChunkBiomeColumn::new(
            position,
            generation,
            min_section_y,
            (0..count)
                .map(|_| DirectBiomeSection::filled(7_u16))
                .collect(),
        )
        .expect("valid biome column");
        (blocks, biomes)
    }

    fn semantic() -> Semantic {
        let (blocks, biomes) = parts(ChunkPos { x: 0, z: 0 }, ChunkGeneration(3), -1, 2);
        LiveChunkSemanticState::from_parts(blocks, biomes).expect("coherent semantic state")
    }

    #[test]
    fn composition_requires_exact_identity_and_lattice() {
        let (blocks, _) = parts(ChunkPos { x: 1, z: 2 }, ChunkGeneration(4), -2, 2);
        let (_, position_mismatch) = parts(ChunkPos { x: 2, z: 2 }, ChunkGeneration(4), -2, 2);
        assert!(matches!(
            LiveChunkSemanticState::from_parts(blocks, position_mismatch),
            Err(ChunkSemanticStateError::PositionMismatch { .. })
        ));

        let (blocks, _) = parts(ChunkPos { x: 1, z: 2 }, ChunkGeneration(4), -2, 2);
        let (_, generation_mismatch) = parts(ChunkPos { x: 1, z: 2 }, ChunkGeneration(5), -2, 2);
        assert!(matches!(
            LiveChunkSemanticState::from_parts(blocks, generation_mismatch),
            Err(ChunkSemanticStateError::GenerationMismatch { .. })
        ));

        let (blocks, _) = parts(ChunkPos { x: 1, z: 2 }, ChunkGeneration(4), -2, 2);
        let (_, lattice_mismatch) = parts(ChunkPos { x: 1, z: 2 }, ChunkGeneration(4), -1, 2);
        assert_eq!(
            LiveChunkSemanticState::from_parts(blocks, lattice_mismatch).unwrap_err(),
            ChunkSemanticStateError::LatticeMismatch {
                blocks: VerticalSectionLattice::new(-2, 2).unwrap(),
                biomes: VerticalSectionLattice::new(-1, 2).unwrap(),
            }
        );
    }

    #[test]
    fn block_and_biome_changes_share_one_revision_clock() {
        let mut state = semantic();
        let initial_stamp = state.stamp();
        assert_eq!(state.revision(), ChunkRevision(0));

        let block = BlockPos { x: 1, y: -16, z: 2 };
        let changed = state
            .replace_block(block, Block::Stone, &Facts)
            .expect("block mutation");
        assert!(changed.changed);
        assert_eq!(state.revision(), ChunkRevision(1));
        assert_ne!(state.stamp(), initial_stamp);

        let local = biome_pos(2, 1, 3);
        let biome = state.replace_biome(-1, local, 9).expect("biome mutation");
        assert!(biome.changed);
        assert_eq!(biome.old, 7);
        assert_eq!(state.revision(), ChunkRevision(2));
        assert_eq!(state.get_block(block), Ok(Block::Stone));
        assert_eq!(state.get_biome(-1, local), Ok(9));
    }

    #[test]
    fn semantic_noops_do_not_invalidate_projection_freshness() {
        let mut state = semantic();
        let block = BlockPos { x: 0, y: -1, z: 0 };
        let biome = biome_pos(1, 2, 3);
        let stamp = state.stamp();

        let block_result = state
            .replace_block(block, Block::Air, &Facts)
            .expect("same-state block mutation");
        assert!(!block_result.changed);
        let biome_result = state
            .replace_biome(-1, biome, 7)
            .expect("same-biome mutation");
        assert!(!biome_result.changed);
        assert_eq!(state.stamp(), stamp);
    }

    #[test]
    fn rejected_biome_access_cannot_advance_revision() {
        let mut state = semantic();
        let stamp = state.stamp();
        let error = state
            .replace_biome(1, biome_pos(0, 0, 0), 8)
            .expect_err("section is outside two-section lattice");
        assert!(matches!(error, ChunkSemanticStateError::Biomes(_)));
        assert_eq!(state.stamp(), stamp);
    }
}
