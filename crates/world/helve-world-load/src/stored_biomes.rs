//! COLD composition from persisted sparse quart-biomes to one coherent resident chunk.
//!
//! No biome defaults are fabricated: the imported saved biome sections must cover the entire
//! frozen dimension lattice before the authoritative owner is admitted. The section objects
//! move directly into the existing one-directory semantic installer without copying quart cells.

use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_import::{
    ImportedBiomeSection, ImportedStoredChunkWithBiomeLight, ImportedStoredChunkWithLight,
};
use helve_world_runtime::{
    DimensionRuntimeProfile, SemanticDimensionInstance,
};

use crate::{
    InstalledStoredChunk, SemanticResidentInstallError, SourceChunkPublicationReceipt,
    install_imported_semantic_chunk,
};

/// Source saved-biome sections are incomplete, inconsistent or fail admission to one dimension.
#[derive(Debug)]
pub enum StoredBiomeResidencyError {
    /// Every logical dimension section must contain one exact source-resolved biome section.
    SectionCountMismatch {
        expected: usize,
        actual: usize,
    },
    /// Sorting still left a missing, repeated or out-of-lattice signed section coordinate.
    SectionYMismatch {
        expected: i32,
        actual: i32,
    },
    /// One section-list index could not be represented on the target host.
    SectionIndexOverflow,
    /// Block/biome/light composition or final resident directory admission failed.
    Resident(SemanticResidentInstallError),
}

/// One result of exact source-biome installation into the authoritative resident chunk directory.
pub type StoredBiomeResidentInstallResult =
    Result<InstalledStoredChunk, StoredBiomeResidencyError>;

/// Moves fully source-decoded quart biomes into the exact loaded-dimension section lattice.
///
/// Each supplied section must correspond to exactly one logical section, with no gaps.
/// Sorting the small COLD section vector is permitted; no default biome can be substituted
/// for missing source data, and the final semantic sections are moved rather than copied.
///
/// # Errors
///
/// Rejects incomplete, duplicate or out-of-range section identities without mutating residency.
pub fn compose_saved_biome_sections<Section>(
    profile: DimensionRuntimeProfile,
    mut sparse: Vec<ImportedBiomeSection<Section>>,
) -> Result<Vec<Section>, StoredBiomeResidencyError> {
    let expected_count = profile.section_count();
    if sparse.len() != expected_count {
        return Err(StoredBiomeResidencyError::SectionCountMismatch {
            expected: expected_count,
            actual: sparse.len(),
        });
    }

    sparse.sort_unstable_by_key(|section| section.section_y);
    for (index, section) in sparse.iter().enumerate() {
        let offset = i32::try_from(index)
            .map_err(|_| StoredBiomeResidencyError::SectionIndexOverflow)?;
        let expected = profile.min_section_y() + offset;
        let actual = i32::from(section.section_y);
        if actual != expected {
            return Err(StoredBiomeResidencyError::SectionYMismatch { expected, actual });
        }
    }

    Ok(sparse.into_iter().map(|section| section.section).collect())
}

/// Admits blocks, fully resolved persisted biomes and saved light as one chunk incarnation.
///
/// This is a COLD link from the one-pass Anvil import transaction to the already qualified
/// `install_imported_semantic_chunk` path. All data is moved; no second NBT pass, biome
/// cell copying, heap-backed side directory or independent semantic revision is introduced.
///
/// # Errors
///
/// Fails without installing any resident state when the biome lattice is incomplete/invalid
/// or the underlying atomic chunk admission rejects blocks, light or the chunk incarnation.
pub fn install_source_biome_chunk<S, BlockStorage, B, BiomeStorage, MakeEmpty>(
    dimension: &mut SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>,
    imported: ImportedStoredChunkWithBiomeLight<BlockStorage, BiomeStorage>,
    make_empty_section: MakeEmpty,
) -> StoredBiomeResidentInstallResult
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
    MakeEmpty: FnMut() -> BlockStorage,
{
    install_source_biome_chunk_with_receipt(dimension, imported, make_empty_section)
        .map(SourceChunkPublicationReceipt::installed)
}

/// Installs one source-biome chunk and returns provenance bound to its real incarnation.
///
/// No receipt exists on admission failure. The saved header and block-entity
/// evidence are copied **before** moving the final block/biome/light sections
/// into their unique authoritative resident owner. This is a small COLD
/// caller-held value, never a second world state or per-cell tax.
///
/// # Errors
///
/// Same exact fail-closed conditions as `install_source_biome_chunk`.
pub fn install_source_biome_chunk_with_receipt<S, BlockStorage, B, BiomeStorage, MakeEmpty>(
    dimension: &mut SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>,
    imported: ImportedStoredChunkWithBiomeLight<BlockStorage, BiomeStorage>,
    make_empty_section: MakeEmpty,
) -> Result<SourceChunkPublicationReceipt, StoredBiomeResidencyError>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
    MakeEmpty: FnMut() -> BlockStorage,
{
    let source_header = imported.stored.blocks.header;
    let block_entities = imported.block_entities;
    let sections = compose_saved_biome_sections(dimension.profile(), imported.biomes.sections)?;
    let stored = ImportedStoredChunkWithLight {
        stored: imported.stored,
        light: imported.light,
        block_entities,
    };
    let installed = install_imported_semantic_chunk(dimension, stored, sections, make_empty_section)
        .map_err(StoredBiomeResidencyError::Resident)?;
    Ok(SourceChunkPublicationReceipt::from_admission(
        installed,
        source_header,
        block_entities,
    ))
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_import::{
        ChunkCompression, ImportedBiomeSection, ImportedBlockSection, ImportedChunkBlocks,
        ImportedStoredBiomes, ImportedStoredChunk, ImportedStoredChunkWithBiomeLight,
        ImportedStoredLight, ImportedStoredLightSection, StoredChunkHeader,
        StoredChunkSourceMetadata, TARGET_DATA_VERSION_26_2,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{
        DimensionRuntimeProfile, SemanticDimensionInstance, SemanticResidentLoadError,
    };

    use super::{StoredBiomeResidencyError, compose_saved_biome_sections, install_source_biome_chunk};

    struct Facts;

    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, state: u8) -> SectionStateFacts {
            SectionStateFacts::new(state != 0, false, false, false)
        }
    }

    type Blocks = DirectBlockSection<u8>;
    type Biomes = DirectBiomeSection<u16>;
    type Dimension = SemanticDimensionInstance<u8, Blocks, u16, Biomes>;

    fn profile() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(3), -16, 32, true)
            .expect("two section profile")
    }

    fn original(pos: ChunkPos, source_y: [i8; 2]) -> ImportedStoredChunkWithBiomeLight<Blocks, Biomes> {
        ImportedStoredChunkWithBiomeLight {
            stored: ImportedStoredChunk {
                blocks: ImportedChunkBlocks {
                    header: StoredChunkHeader {
                        data_version: TARGET_DATA_VERSION_26_2,
                        position: pos,
                        stored_section_count: 2,
                    },
                    sections: vec![ImportedBlockSection {
                        section_y: -1,
                        section: DirectBlockSection::filled(1_u8, &Facts),
                    }],
                },
                source: StoredChunkSourceMetadata {
                    region_timestamp: 99,
                    compression: ChunkCompression::Zlib,
                    external: false,
                },
            },
            light: ImportedStoredLight {
                persisted_light_correct: true,
                sections: vec![ImportedStoredLightSection {
                    section_y: -2,
                    block: Some(vec![0x55; 2048]),
                    sky: Some(vec![0x77; 2048]),
                }],
            },
            block_entities: helve_world_import::StoredBlockEntityEvidence::Absent,
            biomes: ImportedStoredBiomes {
                // Deliberately reverse saved order; no resident slot can depend on NBT ordering.
                sections: vec![
                    ImportedBiomeSection {
                        section_y: source_y[0],
                        section: DirectBiomeSection::filled(22_u16),
                    },
                    ImportedBiomeSection {
                        section_y: source_y[1],
                        section: DirectBiomeSection::filled(11_u16),
                    },
                ],
            },
        }
    }

    #[test]
    fn source_biomes_join_one_coherent_resident_in_dimension_order() {
        let pos = ChunkPos { x: 5, z: -3 };
        let mut dim = Dimension::new(DimensionId(5), profile());
        let mut empty_calls = 0;
        let installed = install_source_biome_chunk(
            &mut dim,
            original(pos, [0, -1]),
            || {
                empty_calls += 1;
                DirectBlockSection::filled(0_u8, &Facts)
            },
        )
        .expect("source biome resident");
        assert_eq!(empty_calls, 1);
        assert_eq!(installed.handle.generation, ChunkGeneration(1));
        assert_eq!(installed.source.region_timestamp, 99);
        let state = dim.resolve_chunk(installed.handle).expect("resident");
        assert_eq!(
            state.get_biome(-1, SectionBiomePos::new(0, 0, 0).unwrap()),
            Ok(11),
        );
        assert_eq!(
            state.get_biome(0, SectionBiomePos::new(3, 3, 3).unwrap()),
            Ok(22),
        );
        assert!(state.current_initial_light().is_some());
        let position = BlockPos { x: 80, y: -16, z: -48 };
        let changed = dim.resolve_chunk_mut(installed.handle).unwrap()
            .replace_block(position, 0, &Facts).expect("valid real mutation");
        assert!(changed.changed);
        assert!(dim.resolve_chunk(installed.handle).unwrap().current_initial_light().is_none());
    }

    #[test]
    fn missing_and_repeated_saved_biomes_cannot_create_a_resident_chunk() {
        let pos = ChunkPos { x: 1, z: 2 };
        let mut dim = Dimension::new(DimensionId(5), profile());
        let mut incomplete = original(pos, [0, -1]);
        incomplete.biomes.sections.pop();
        assert!(matches!(
            install_source_biome_chunk(&mut dim, incomplete, || DirectBlockSection::filled(0, &Facts)),
            Err(StoredBiomeResidencyError::SectionCountMismatch {
                expected: 2, actual: 1
            })
        ));
        assert!(matches!(
            install_source_biome_chunk(
                &mut dim,
                original(pos, [-1, -1]),
                || DirectBlockSection::filled(0, &Facts)
            ),
            Err(StoredBiomeResidencyError::SectionYMismatch { .. })
        ));
        assert!(matches!(
            install_source_biome_chunk(
                &mut dim,
                original(pos, [0, 1]),
                || DirectBlockSection::filled(0, &Facts)
            ),
            Err(StoredBiomeResidencyError::SectionYMismatch { .. })
        ));
        assert_eq!(dim.resident_chunk_count(), 0);
        let first = install_source_biome_chunk(
            &mut dim,
            original(pos, [0, -1]),
            || DirectBlockSection::filled(0, &Facts),
        )
        .expect("first valid source uses generation one");
        assert_eq!(first.handle.generation, ChunkGeneration(1));
        assert!(matches!(
            install_source_biome_chunk(
                &mut dim,
                original(pos, [0, -1]),
                || DirectBlockSection::filled(0, &Facts),
            ),
            Err(StoredBiomeResidencyError::Resident(
                SemanticResidentLoadError::AlreadyResident { .. }
            ))
        ));
    }

    #[test]
    fn composing_sorted_biome_sections_moves_sections_without_copy() {
        let profile = profile();
        let sections = vec![
            ImportedBiomeSection { section_y: 0, section: Box::new([22u8; 64]) },
            ImportedBiomeSection { section_y: -1, section: Box::new([11u8; 64]) },
        ];
        let originals = [
            std::ptr::from_ref(sections[0].section.as_ref()),
            std::ptr::from_ref(sections[1].section.as_ref()),
        ];
        let result = compose_saved_biome_sections(profile, sections).expect("valid");
        assert!(std::ptr::eq(
            std::ptr::from_ref(result[0].as_ref()),
            originals[1],
        ));
        assert!(std::ptr::eq(
            std::ptr::from_ref(result[1].as_ref()),
            originals[0],
        ));
    }
}
