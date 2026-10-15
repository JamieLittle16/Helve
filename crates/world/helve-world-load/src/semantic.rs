//! Cold transactional installation of imported blocks, caller-provided biomes and source light.
//!
//! This composes into the single existing coherent resident-directory ownership mode, not an
//! independent lighting cache or block directory. The directory allocates the generation inside
//! atomic admission; only then is imported lighting bound to that exact generation.

use helve_types::ChunkPos;
use helve_world_chunk::{
    ChunkBiomeColumn, ChunkBiomeColumnError, ChunkCoreError, ChunkSemanticStateError,
    LiveChunkCore, LiveChunkSemanticState,
};
use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_import::ImportedStoredChunkWithLight;
use helve_world_runtime::{SemanticDimensionInstance, SemanticResidentLoadError};

use crate::{
    InitialLightCompositionError, InstalledStoredChunk, ResidentInstallError,
    compose_block_sections, prepare_imported_chunk_light,
};

/// Fail-closed failures while constructing a semantic resident from one imported chunk.
#[derive(Debug)]
pub enum SemanticImportBuildError {
    /// Exact stored sparse block section validation or final section construction failed.
    Blocks(ResidentInstallError),
    /// The caller has not supplied one actual biome section for every dimension section.
    BiomeSectionCountMismatch { expected: usize, actual: usize },
    /// Source light could not be moved into a dimension-bound, generation-owned light column.
    InitialLight(InitialLightCompositionError),
    /// The final authoritative block core refused construction.
    BlockCore(ChunkCoreError),
    /// The final authoritative biome column refused construction.
    Biomes(ChunkBiomeColumnError),
    /// The whole-chunk ownership/initial-light identity contract rejected composition.
    Semantic(ChunkSemanticStateError),
}

/// Cold installation failures, including directory duplicate/stale-generation protection.
pub type SemanticResidentInstallError = SemanticResidentLoadError<SemanticImportBuildError>;

/// Atomically installs imported blocks, exact caller-provided biome sections and source lighting.
///
/// This accepts the complete one-pass imported Anvil block/light result, plus **real semantic
/// biome sections already resolved by the caller**. Biomes are deliberately mandatory: this API
/// never manufactures a plains/default biome from an absent source field. When a source-backed
/// biome importer exists it will provide these sections directly.
///
/// The same existing sparse block-section assembler moves the stored sections into exactly one
/// final contiguous resident column, with only missing sections coming from the supplied empty
/// factory. The resolved biome sections are also moved, not copied. On the vacant-directory path,
/// generation allocation precedes light construction, so the final initial-light column is bound
/// to the actual incarnation—not an externally predicted generation.
///
/// Both partial input rejection and failed semantic composition leave the dimension unchanged.
/// An occupied position does not invoke the builder or empty-section factory. After admission,
/// HOT mutation operates through the direct `LiveChunkSemanticState` borrow with one revision,
/// not a secondary light invalidation loop or directory lookup.
///
/// # Errors
///
/// Rejects duplicate residents, generation exhaustion, incomplete biome sections, source-light
/// errors, invalid/duplicate/out-of-range imported blocks and mismatched whole-chunk semantics.
pub fn install_imported_semantic_chunk<S, BlockStorage, B, BiomeStorage, MakeEmpty>(
    dimension: &mut SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>,
    imported: ImportedStoredChunkWithLight<BlockStorage>,
    biome_sections: Vec<BiomeStorage>,
    mut make_empty_section: MakeEmpty,
) -> Result<InstalledStoredChunk, SemanticResidentInstallError>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
    MakeEmpty: FnMut() -> BlockStorage,
{
    let position: ChunkPos = imported.stored.blocks.header.position;
    let source = imported.stored.source;
    let handle = dimension.admit_chunk(position, move |generation, profile| {
        if biome_sections.len() != profile.section_count() {
            return Err(SemanticImportBuildError::BiomeSectionCountMismatch {
                expected: profile.section_count(),
                actual: biome_sections.len(),
            });
        }
        let prepared = prepare_imported_chunk_light(imported, generation, profile)
            .map_err(SemanticImportBuildError::InitialLight)?;
        let resident_sections = compose_block_sections(
            profile,
            prepared.stored.blocks.sections,
            &mut make_empty_section,
        )
        .map_err(SemanticImportBuildError::Blocks)?;
        let blocks = LiveChunkCore::new(
            position,
            generation,
            profile.min_section_y(),
            resident_sections,
        )
        .map_err(SemanticImportBuildError::BlockCore)?;
        let biomes = ChunkBiomeColumn::new(
            position,
            generation,
            profile.min_section_y(),
            biome_sections,
        )
        .map_err(SemanticImportBuildError::Biomes)?;
        LiveChunkSemanticState::from_parts(blocks, biomes)
            .map_err(SemanticImportBuildError::Semantic)?
            .with_initial_light(prepared.light)
            .map_err(SemanticImportBuildError::Semantic)
    })?;
    Ok(InstalledStoredChunk { handle, source })
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_import::{
        ChunkCompression, ImportedBlockSection, ImportedChunkBlocks, ImportedStoredChunk,
        ImportedStoredChunkWithLight, ImportedStoredLight, ImportedStoredLightSection,
        StoredChunkHeader, StoredChunkSourceMetadata, TARGET_DATA_VERSION_26_2,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance, SemanticResidentLoadError};

    use super::{SemanticImportBuildError, install_imported_semantic_chunk};
    use crate::ResidentInstallError;

    struct Facts;
    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, state: u8) -> SectionStateFacts {
            SectionStateFacts::new(state != 0, false, false, false)
        }
    }

    type Blocks = DirectBlockSection<u8>;
    type Biomes = DirectBiomeSection<u16>;
    type Dim = SemanticDimensionInstance<u8, Blocks, u16, Biomes>;

    fn profile() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(4), -16, 32, true)
            .expect("two-section profile")
    }

    fn make_stored(position: ChunkPos, light_y: i8) -> ImportedStoredChunkWithLight<Blocks> {
        ImportedStoredChunkWithLight {
            stored: ImportedStoredChunk {
                blocks: ImportedChunkBlocks {
                    header: StoredChunkHeader {
                        data_version: TARGET_DATA_VERSION_26_2,
                        position,
                        stored_section_count: 2,
                    },
                    sections: vec![ImportedBlockSection {
                        section_y: -1,
                        section: DirectBlockSection::filled(1_u8, &Facts),
                    }],
                },
                source: StoredChunkSourceMetadata {
                    region_timestamp: 37,
                    compression: ChunkCompression::Zlib,
                    external: false,
                },
            },
            block_entities: helve_world_import::StoredBlockEntityEvidence::Absent,
            light: ImportedStoredLight {
                persisted_light_correct: true,
                sections: vec![ImportedStoredLightSection {
                    section_y: light_y,
                    block: Some(vec![0xa5; 2048]),
                    sky: Some(vec![0x3c; 2048]),
                }],
            },
        }
    }

    fn biomes() -> Vec<Biomes> {
        vec![DirectBiomeSection::filled(9_u16), DirectBiomeSection::filled(11_u16)]
    }

    fn air() -> Blocks {
        DirectBlockSection::filled(0_u8, &Facts)
    }

    #[test]
    fn atomic_stored_import_enters_one_coherent_directory_under_real_generation() {
        let pos = ChunkPos { x: 3, z: -2 };
        let mut dim = Dim::new(DimensionId(7), profile());
        let mut empty_calls = 0;
        let installed = install_imported_semantic_chunk(
            &mut dim,
            make_stored(pos, -2),
            biomes(),
            || {
                empty_calls += 1;
                air()
            },
        )
        .expect("one semantic resident");
        assert_eq!(empty_calls, 1);
        assert_eq!(installed.handle.generation, ChunkGeneration(1));
        assert_eq!(dim.discover_chunk(pos), Some(installed.handle));
        assert_eq!(dim.resident_chunk_count(), 1);
        assert_eq!(installed.source.region_timestamp, 37);
        let state = dim.resolve_chunk(installed.handle).expect("resident");
        assert_eq!(state.generation(), installed.handle.generation);
        assert_eq!(
            state.get_biome(-1, SectionBiomePos::new(0, 0, 0).expect("quart")),
            Ok(9_u16)
        );
        assert_eq!(
            state.get_biome(0, SectionBiomePos::new(3, 3, 3).expect("quart")),
            Ok(11_u16)
        );
        assert!(state.current_initial_light().is_some());
        let block = BlockPos { x: 48, y: -16, z: -32 };
        let no_change = dim.resolve_chunk_mut(installed.handle).unwrap()
            .replace_block(block, 1, &Facts).expect("same state");
        assert!(!no_change.changed);
        assert!(dim.resolve_chunk(installed.handle).unwrap().current_initial_light().is_some());
        let changed = dim.resolve_chunk_mut(installed.handle).unwrap()
            .replace_block(block, 0, &Facts).expect("real change");
        assert!(changed.changed);
        assert_eq!(dim.resolve_chunk(installed.handle).unwrap().revision().0, 1);
        assert!(dim.resolve_chunk(installed.handle).unwrap().current_initial_light().is_none());
        let whole = dim.unload_chunk(installed.handle).expect("unload whole state");
        let (_, _, light) = whole.into_parts();
        assert!(light.is_some());
        assert_eq!(dim.resident_chunk_count(), 0);
    }

    #[test]
    fn nonempty_unadmitted_block_entities_never_become_resident() {
        let pos = ChunkPos { x: 6, z: -4 };
        let mut dim = Dim::new(DimensionId(3), profile());
        let mut stored = make_stored(pos, -2);
        stored.block_entities =
            helve_world_import::StoredBlockEntityEvidence::UnhandledEntries { count: 2 };
        let mut empty_calls = 0;
        assert!(matches!(
            install_imported_semantic_chunk(&mut dim, stored, biomes(), || {
                empty_calls += 1;
                air()
            }),
            Err(SemanticResidentLoadError::Build(
                SemanticImportBuildError::InitialLight(
                    crate::InitialLightCompositionError::UnadmittedBlockEntities { count: 2 }
                )
            ))
        ));
        assert_eq!(empty_calls, 0);
        assert_eq!(dim.resident_chunk_count(), 0);

        // Rejection consumes no generation and cannot leave a partial source
        // block-entity or light owner in the directory.
        let installed =
            install_imported_semantic_chunk(&mut dim, make_stored(pos, -2), biomes(), air)
                .expect("first valid resident after failed source transaction");
        assert_eq!(installed.handle.generation, ChunkGeneration(1));
    }

    #[test]
    fn invalid_semantic_import_is_transactional_and_does_not_consume_generation() {
        let pos = ChunkPos { x: 1, z: 2 };
        let mut dim = Dim::new(DimensionId(3), profile());
        assert!(matches!(
            install_imported_semantic_chunk(
                &mut dim, make_stored(pos, -2), vec![DirectBiomeSection::filled(7_u16)], air
            ),
            Err(SemanticResidentLoadError::Build(
                SemanticImportBuildError::BiomeSectionCountMismatch { expected: 2, actual: 1 }
            ))
        ));
        assert!(matches!(
            install_imported_semantic_chunk(
                &mut dim, make_stored(pos, 2), biomes(), air
            ),
            Err(SemanticResidentLoadError::Build(SemanticImportBuildError::InitialLight(_)))
        ));
        let mut duplicate = make_stored(pos, -2);
        duplicate.stored.blocks.sections.push(ImportedBlockSection {
            section_y: -1,
            section: air(),
        });
        assert!(matches!(
            install_imported_semantic_chunk(&mut dim, duplicate, biomes(), air),
            Err(SemanticResidentLoadError::Build(
                SemanticImportBuildError::Blocks(
                    ResidentInstallError::DuplicateSectionY { section_y: -1 }
                )
            ))
        ));
        assert_eq!(dim.resident_chunk_count(), 0);
        let installed = install_imported_semantic_chunk(
            &mut dim, make_stored(pos, -2), biomes(), air,
        ).expect("first valid import still has generation one");
        assert_eq!(installed.handle.generation, ChunkGeneration(1));
        let mut empty_calls = 0;
        let duplicate = install_imported_semantic_chunk(
            &mut dim,
            make_stored(pos, -2),
            biomes(),
            || {
                empty_calls += 1;
                air()
            },
        );
        assert!(matches!(
            duplicate,
            Err(SemanticResidentLoadError::AlreadyResident { handle }) if handle == installed.handle
        ));
        assert_eq!(empty_calls, 0);
        assert_eq!(dim.resident_chunk_count(), 1);
    }
}
