//! One alternate *ownership mode* of the existing resident directory for coherent world chunks.
//!
//! This replaces the block-only payload inside a loaded dimension; it is not a second map,
//! staging cache or parallel world. The directory and generation allocator are unchanged.
//! Callers resolve handles at the lifecycle boundary and borrow chunks directly for HOT work.

use helve_types::{ChunkGeneration, ChunkPos, ChunkRevision, DimensionId};
use helve_world_chunk::LiveChunkSemanticState;
use helve_world_contract::{BiomeSection, BlockSection};

use crate::{
    DimensionRuntimeProfile, ResidentAdmissionError, ResidentChunkAccessError, ResidentChunkHandle,
    resident::{ResidentChunkIdentity, ResidentDirectory},
};

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

/// Failure to admit a complete coherent semantic chunk into a loaded dimension.
#[derive(Debug)]
pub enum SemanticResidentLoadError<E> {
    /// The sparse resident directory already owns this semantic chunk position.
    AlreadyResident { handle: ResidentChunkHandle },
    /// The monotonically increasing incarnation allocator has been exhausted.
    GenerationExhausted,
    /// The caller's statically dispatched cold builder rejected source data or composition.
    Build(E),
    /// The constructed chunk belongs to a different x/z column.
    PositionMismatch {
        expected: ChunkPos,
        actual: ChunkPos,
    },
    /// The constructed chunk used a generation other than the one allocated by this directory.
    GenerationMismatch {
        expected: ChunkGeneration,
        actual: ChunkGeneration,
    },
    /// The chunk's vertical section lattice does not match its loaded dimension.
    LatticeMismatch {
        expected_min_section_y: i32,
        expected_section_count: usize,
        actual_min_section_y: i32,
        actual_section_count: usize,
    },
    /// An already-mutated chunk is not an admissible freshly imported incarnation.
    NonPristineChunk { revision: ChunkRevision },
}

/// One loaded dimension owning coherent block/biome/initial-light chunks.
///
/// This is an **alternative** to the existing block-only `DimensionInstance`: a dimension
/// constructs one of these owners, never both. Both modes use the exact same generic
/// `ResidentDirectory`, single sparse map and generation allocation/handle checking logic.
/// No target packets, NBT parsing, biome registry lookup or scheduler placement enter this type.
///
/// The caller's cold builder receives the generation *from the authoritative directory* and
/// the frozen dimension profile. That permits imported lighting to be composed with the
/// genuine incarnation, rather than pre-allocating a guessed generation. Rejected builds consume
/// no generation and install no partial resident state.
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

impl<S, BlockStorage, B, BiomeStorage> SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    /// Creates one empty semantic dimension without pre-reserving directory capacity.
    #[must_use]
    pub fn new(id: DimensionId, profile: DimensionRuntimeProfile) -> Self {
        Self::with_chunk_capacity(id, profile, 0)
    }

    /// Creates a dimension with one COLD sparse-directory capacity hint.
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

    /// Loaded dimension identity for this sole authoritative resident directory.
    #[must_use]
    pub const fn id(&self) -> DimensionId {
        self.resident.id()
    }

    /// Pre-resolved source-backed dimension profile.
    #[must_use]
    pub const fn profile(&self) -> DimensionRuntimeProfile {
        self.profile
    }

    /// Number of authoritative coherent chunks currently resident.
    #[must_use]
    pub fn resident_chunk_count(&self) -> usize {
        self.resident.len()
    }

    /// Resolves a chunk position to the current process-local incarnation (COLD/BOUNDARY).
    #[must_use]
    pub fn discover_chunk(&self, position: ChunkPos) -> Option<ResidentChunkHandle> {
        self.resident.discover(position)
    }

    /// Atomically constructs and admits one whole semantic chunk under a single generation.
    ///
    /// `build` executes only if the position is vacant and receives the actual reserved
    /// generation and immutable dimension profile. The returned block, biome and initial-light
    /// components must be coherent. This boundary also validates the dimension lattice, exact
    /// generation and pristine revision before committing the resident entry.
    ///
    /// This is COLD lifecycle work. After admission, every HOT read or mutation operates on a
    /// directly resolved `&LiveChunkSemanticState` / `&mut LiveChunkSemanticState`, without
    /// repeated map lookups or any additional independent revision.
    ///
    /// # Errors
    ///
    /// Fails closed on duplicate residency, exhausted generations, a builder error, mismatched
    /// chunk position/incarnation/lattice or an already-mutated imported chunk. Failure installs
    /// nothing and consumes no generation.
    pub fn admit_chunk<E, Build>(
        &mut self,
        position: ChunkPos,
        build: Build,
    ) -> Result<ResidentChunkHandle, SemanticResidentLoadError<E>>
    where
        Build: FnOnce(
            ChunkGeneration,
            DimensionRuntimeProfile,
        )
            -> Result<LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>, E>,
    {
        let profile = self.profile;
        match self.resident.admit_with(position, move |generation| {
            let chunk = build(generation, profile).map_err(SemanticResidentLoadError::Build)?;
            if chunk.position() != position {
                return Err(SemanticResidentLoadError::PositionMismatch {
                    expected: position,
                    actual: chunk.position(),
                });
            }
            if chunk.generation() != generation {
                return Err(SemanticResidentLoadError::GenerationMismatch {
                    expected: generation,
                    actual: chunk.generation(),
                });
            }
            let lattice = chunk.vertical_lattice();
            if lattice.min_section_y() != profile.min_section_y()
                || lattice.section_count() != profile.section_count()
            {
                return Err(SemanticResidentLoadError::LatticeMismatch {
                    expected_min_section_y: profile.min_section_y(),
                    expected_section_count: profile.section_count(),
                    actual_min_section_y: lattice.min_section_y(),
                    actual_section_count: lattice.section_count(),
                });
            }
            if chunk.revision() != ChunkRevision(0) {
                return Err(SemanticResidentLoadError::NonPristineChunk {
                    revision: chunk.revision(),
                });
            }
            Ok(chunk)
        }) {
            Ok(handle) => Ok(handle),
            Err(ResidentAdmissionError::AlreadyResident { handle }) => {
                Err(SemanticResidentLoadError::AlreadyResident { handle })
            }
            Err(ResidentAdmissionError::GenerationExhausted) => {
                Err(SemanticResidentLoadError::GenerationExhausted)
            }
            Err(ResidentAdmissionError::Build(error)) => Err(error),
        }
    }

    /// Borrows one current coherent chunk after one exact handle lookup.
    ///
    /// # Errors
    ///
    /// Rejects foreign-dimension, unloaded and old-incarnation handles.
    pub fn resolve_chunk(
        &self,
        handle: ResidentChunkHandle,
    ) -> Result<&LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>, ResidentChunkAccessError>
    {
        self.resident.resolve(handle)
    }

    /// Mutably borrows one current coherent chunk, retaining its sole semantic revision.
    ///
    /// The caller keeps this borrow for HOT work; it must not repeatedly resolve per cell.
    ///
    /// # Errors
    ///
    /// Rejects foreign-dimension, unloaded and old-incarnation handles.
    pub fn resolve_chunk_mut(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<
        &mut LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
        ResidentChunkAccessError,
    > {
        self.resident.resolve_mut(handle)
    }

    /// Unloads and returns the complete authoritative chunk, including imported light.
    ///
    /// No cell or light array is copied and the directory is probed exactly once.
    ///
    /// # Errors
    ///
    /// Rejects foreign-dimension, unloaded and old-incarnation handles.
    pub fn unload_chunk(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>, ResidentChunkAccessError>
    {
        self.resident.unload(handle)
    }
}

#[cfg(test)]
mod tests {
    use core::convert::Infallible;

    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
    use helve_world_chunk::{
        ChunkBiomeColumn, ImportedLightSection, InitialChunkLight, LightDataLayer, LiveChunkCore,
        LiveChunkSemanticState, VerticalSectionLattice,
    };
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use super::{SemanticDimensionInstance, SemanticResidentLoadError};
    use crate::{DimensionRuntimeProfile, ResidentChunkAccessError};

    struct Facts;

    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, state: u8) -> SectionStateFacts {
            SectionStateFacts::new(state != 0, false, false, false)
        }
    }

    type Blocks = DirectBlockSection<u8>;
    type Biomes = DirectBiomeSection<u16>;
    type Semantic = LiveChunkSemanticState<u8, Blocks, u16, Biomes>;
    type Dimension = SemanticDimensionInstance<u8, Blocks, u16, Biomes>;

    fn profile() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(1), -16, 32, true)
            .expect("two section profile")
    }

    fn chunk(
        pos: ChunkPos,
        generation: ChunkGeneration,
        lattice_min: i32,
        include_light: bool,
    ) -> Semantic {
        let sections = (0..2)
            .map(|_| DirectBlockSection::filled(0_u8, &Facts))
            .collect();
        let blocks =
            LiveChunkCore::new(pos, generation, lattice_min, sections).expect("valid core");
        let biomes = ChunkBiomeColumn::new(
            pos,
            generation,
            lattice_min,
            (0..2).map(|_| DirectBiomeSection::filled(7_u16)).collect(),
        )
        .expect("valid biomes");
        let state =
            LiveChunkSemanticState::from_parts(blocks, biomes).expect("same identity and lattice");
        if include_light {
            let light = InitialChunkLight::from_imported(
                pos,
                generation,
                VerticalSectionLattice::new(lattice_min, 2).expect("lattice"),
                true,
                true,
                vec![ImportedLightSection {
                    section_y: lattice_min - 1,
                    block: Some(LightDataLayer::homogeneous(0).expect("zero")),
                    sky: Some(LightDataLayer::homogeneous(15).expect("full")),
                }],
            )
            .expect("valid initial light");
            state.with_initial_light(light).expect("pristine")
        } else {
            state
        }
    }

    #[test]
    fn a_single_directory_owns_block_biome_and_initial_light_together() {
        let mut dim = Dimension::new(DimensionId(9), profile());
        let pos = ChunkPos { x: -2, z: 8 };
        let handle = dim
            .admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, generation, -1, true))
            })
            .expect("atomic semantic admission");
        assert_eq!(dim.discover_chunk(pos), Some(handle));
        assert_eq!(dim.resident_chunk_count(), 1);
        assert_eq!(handle.generation, ChunkGeneration(1));
        let state = dim.resolve_chunk(handle).expect("resident");
        assert_eq!(state.generation(), handle.generation);
        assert!(state.current_initial_light().is_some());
        assert_eq!(
            state.get_biome(-1, SectionBiomePos::new(0, 0, 0).expect("quart position")),
            Ok(7),
        );

        let block = BlockPos {
            x: -32,
            y: -16,
            z: 128,
        };
        let no_change = dim
            .resolve_chunk_mut(handle)
            .expect("mutable chunk")
            .replace_block(block, 0, &Facts)
            .expect("same state");
        assert!(!no_change.changed);
        assert!(
            dim.resolve_chunk(handle)
                .unwrap()
                .current_initial_light()
                .is_some()
        );
        let changed = dim
            .resolve_chunk_mut(handle)
            .expect("mutable chunk")
            .replace_block(block, 1, &Facts)
            .expect("real change");
        assert!(changed.changed);
        let state = dim.resolve_chunk(handle).expect("same incarnation");
        assert_eq!(state.revision().0, 1);
        assert!(state.current_initial_light().is_none());
        let unloaded = dim.unload_chunk(handle).expect("complete owner returns");
        let (_, _, light) = unloaded.into_parts();
        assert!(light.is_some());
        assert_eq!(dim.resident_chunk_count(), 0);
    }

    #[test]
    fn rejected_builds_do_not_consume_generation_or_replace_residents() {
        let mut dim = Dimension::new(DimensionId(1), profile());
        let pos = ChunkPos { x: 2, z: 3 };
        assert!(matches!(
            dim.admit_chunk(pos, |_gen, _| Err::<Semantic, _>("invalid source")),
            Err(SemanticResidentLoadError::Build("invalid source"))
        ));
        assert!(matches!(
            dim.admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(ChunkPos { x: 8, z: 3 }, generation, -1, false))
            }),
            Err(SemanticResidentLoadError::PositionMismatch { .. })
        ));
        assert!(matches!(
            dim.admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, ChunkGeneration(generation.0 + 1), -1, false))
            }),
            Err(SemanticResidentLoadError::GenerationMismatch { .. })
        ));
        assert!(matches!(
            dim.admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, generation, 0, false))
            }),
            Err(SemanticResidentLoadError::LatticeMismatch { .. })
        ));
        assert!(matches!(
            dim.admit_chunk(pos, |generation, _| {
                let mut state = chunk(pos, generation, -1, false);
                state
                    .replace_block(
                        BlockPos {
                            x: 32,
                            y: -16,
                            z: 48,
                        },
                        1,
                        &Facts,
                    )
                    .expect("change");
                Ok::<_, Infallible>(state)
            }),
            Err(SemanticResidentLoadError::NonPristineChunk { .. })
        ));
        assert_eq!(dim.resident_chunk_count(), 0);
        let first = dim
            .admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, generation, -1, true))
            })
            .expect("first accepted generation");
        assert_eq!(first.generation, ChunkGeneration(1));
        let mut builder_called = false;
        let rejection = dim.admit_chunk(pos, |generation, _| {
            builder_called = true;
            Ok::<_, Infallible>(chunk(pos, generation, -1, false))
        });
        assert!(matches!(
            rejection,
            Err(SemanticResidentLoadError::AlreadyResident { handle }) if handle == first
        ));
        assert!(!builder_called);
        assert!(
            dim.resolve_chunk(first)
                .unwrap()
                .current_initial_light()
                .is_some()
        );
    }

    #[test]
    fn unload_reload_and_cross_dimension_handles_fail_closed() {
        let mut first = Dimension::new(DimensionId(4), profile());
        let second = Dimension::new(DimensionId(5), profile());
        let pos = ChunkPos { x: 0, z: 0 };
        let handle = first
            .admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, generation, -1, false))
            })
            .expect("first");
        assert!(matches!(
            second.resolve_chunk(handle),
            Err(ResidentChunkAccessError::WrongDimension { .. })
        ));
        first.unload_chunk(handle).expect("unload");
        assert!(matches!(
            first.resolve_chunk(handle),
            Err(ResidentChunkAccessError::NotResident { .. })
        ));
        let newer = first
            .admit_chunk(pos, |generation, _| {
                Ok::<_, Infallible>(chunk(pos, generation, -1, false))
            })
            .expect("new incarnation");
        assert_eq!(newer.generation, ChunkGeneration(handle.generation.0 + 1));
        assert!(matches!(
            first.resolve_chunk(handle),
            Err(ResidentChunkAccessError::StaleGeneration { .. })
        ));
        assert!(first.resolve_chunk(newer).is_ok());
    }
}
