//! Moves admitted persisted 26.2 light arrays into the chunk's target-neutral initial light image.
//!
//! This is a COLD import-to-semantics adapter, not a light simulator or protocol encoder.
//! Stored NBT identity is decoded by helve-world-import; live representation, sentinel slots,
//! and light-correctness law belong to helve-world-chunk. No source-shaped second world
//! representation is retained after a successful move.

use helve_types::{ChunkGeneration, ChunkPos};
use helve_world_chunk::{
    ChunkLightError, ImportedLightSection, InitialChunkLight, LightDataLayer, LightKind,
    LightLayerError, VerticalSectionLattice, VerticalSectionLatticeError,
};
use helve_world_import::{ImportedStoredChunk, ImportedStoredChunkWithLight, ImportedStoredLight};
use helve_world_runtime::DimensionRuntimeProfile;

/// Fail-closed errors while moving stored light into a validated semantic chunk lattice.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum InitialLightCompositionError {
    /// A dimension profile could not be represented by the shared semantic lattice.
    Lattice(VerticalSectionLatticeError),
    /// A source layer length was not the admitted packed nibble length.
    Layer {
        section_y: i32,
        kind: LightKind,
        error: LightLayerError,
    },
    /// Stored section identity, duplicate section or dimension sentinel bounds failed.
    Column(ChunkLightError),
}

impl From<VerticalSectionLatticeError> for InitialLightCompositionError {
    fn from(value: VerticalSectionLatticeError) -> Self {
        Self::Lattice(value)
    }
}

impl From<ChunkLightError> for InitialLightCompositionError {
    fn from(value: ChunkLightError) -> Self {
        Self::Column(value)
    }
}

/// One prepared COLD import transaction with exact semantic initial light ownership.
///
/// Neither block sections nor light cells are copied when this object is constructed.
/// Resident publication still requires separate lifecycle admission and a coherent owner.
#[derive(Debug)]
pub struct PreparedImportedChunkLight<Section> {
    pub stored: ImportedStoredChunk<Section>,
    pub light: InitialChunkLight,
}

/// Moves a fully decoded, validated stored-chunk transaction into the initial light representation.
///
/// Light uses **the position in the validated stored block header**, rather than a caller-supplied
/// position that could accidentally bind another chunk's light bytes. The supplied generation is
/// the actual intended resident incarnation and must be checked when the composite owner accepts
/// this image. This seam does not itself install anything into the dimension's resident directory.
///
/// # Errors
///
/// Propagates source light-length and dimension/light-lattice composition failures. A failure
/// returns no prepared transaction and does not change resident world state.
pub fn prepare_imported_chunk_light<Section>(
    imported: ImportedStoredChunkWithLight<Section>,
    generation: ChunkGeneration,
    profile: DimensionRuntimeProfile,
) -> Result<PreparedImportedChunkLight<Section>, InitialLightCompositionError> {
    let ImportedStoredChunkWithLight { stored, light } = imported;
    let initial = compose_imported_initial_light(
        stored.blocks.header.position,
        generation,
        profile,
        light,
    )?;
    Ok(PreparedImportedChunkLight {
        stored,
        light: initial,
    })
}

/// Consumes source-extracted light arrays into exactly one immutable live initial-light column.
///
/// The dimension profile supplies the already-qualified vertical lattice and skylight policy.
/// The chunk position and lifecycle generation are supplied by the caller's eventual authoritative
/// resident incarnation, not inferred from persisted light arrays. The complete caller must still
/// attach the result through `LiveChunkSemanticState::with_initial_light`, which checks identity,
/// lattice and pristine revision together.
///
/// Raw 2048-byte arrays are *moved* into `LightDataLayer` without per-cell copying. Explicit raw
/// zero arrays remain packed rather than being conflated with homogeneous-zero layers. In a
/// dimension without skylight, persisted sky arrays are deliberately ignored before allocation.
/// A false or absent source `isLightOn` is never promoted to true here.
///
/// This is COLD boundary work: it introduces no HOT per-block mutation checks, new revision clock,
/// global chunk directory or target-specific network representation.
///
/// # Errors
///
/// Rejects an invalid dimension lattice, malformed source layers, out-of-lattice sections,
/// duplicate source sections or invalid sentinel bounds without modifying resident state.
fn compose_imported_initial_light(
    position: ChunkPos,
    generation: ChunkGeneration,
    profile: DimensionRuntimeProfile,
    source: ImportedStoredLight,
) -> Result<InitialChunkLight, InitialLightCompositionError> {
    let lattice = VerticalSectionLattice::new(profile.min_section_y(), profile.section_count())?;
    let mut decoded = Vec::with_capacity(source.sections.len());

    for section in source.sections {
        let section_y = i32::from(section.section_y);
        let block = section
            .block
            .map(LightDataLayer::from_raw_bytes)
            .transpose()
            .map_err(|error| InitialLightCompositionError::Layer {
                section_y,
                kind: LightKind::Block,
                error,
            })?;
        let sky = if profile.has_skylight() {
            section
                .sky
                .map(LightDataLayer::from_raw_bytes)
                .transpose()
                .map_err(|error| InitialLightCompositionError::Layer {
                    section_y,
                    kind: LightKind::Sky,
                    error,
                })?
        } else {
            None
        };
        decoded.push(ImportedLightSection {
            section_y,
            block,
            sky,
        });
    }

    Ok(InitialChunkLight::from_imported(
        position,
        generation,
        lattice,
        profile.has_skylight(),
        source.persisted_light_correct,
        decoded,
    )?)
}

#[cfg(test)]
mod tests {
    use helve_types::{
        BlockPos, ChunkGeneration, ChunkPos, DimensionTypeId,
    };
    use helve_world_chunk::{
        ChunkBiomeColumn, ChunkLightError, LightKind, LiveChunkCore, LiveChunkSemanticState,
    };
    use helve_world_contract::{BlockStateFacts, SectionStateFacts, SectionBlockPos};
    use helve_world_import::{
        ChunkCompression, ImportedChunkBlocks, ImportedStoredChunk, ImportedStoredChunkWithLight,
        ImportedStoredLight, ImportedStoredLightSection, StoredChunkHeader,
        StoredChunkSourceMetadata, TARGET_DATA_VERSION_26_2,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::DimensionRuntimeProfile;

    use super::{
        InitialLightCompositionError, compose_imported_initial_light, prepare_imported_chunk_light,
    };

    fn profile(has_skylight: bool) -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(1), -64, 384, has_skylight)
            .expect("24-section overworld-like dimension")
    }

    fn source(
        persisted_light_correct: bool,
        sections: Vec<ImportedStoredLightSection>,
    ) -> ImportedStoredLight {
        ImportedStoredLight {
            persisted_light_correct,
            sections,
        }
    }

    fn section(
        section_y: i8,
        block: Option<Vec<u8>>,
        sky: Option<Vec<u8>>,
    ) -> ImportedStoredLightSection {
        ImportedStoredLightSection {
            section_y,
            block,
            sky,
        }
    }

    fn compose(
        light: ImportedStoredLight,
        has_skylight: bool,
    ) -> Result<helve_world_chunk::InitialChunkLight, InitialLightCompositionError> {
        compose_imported_initial_light(
            ChunkPos { x: -2, z: 7 },
            ChunkGeneration(8),
            profile(has_skylight),
            light,
        )
    }

    #[test]
    fn source_layers_move_to_exact_signed_sentinel_slots_without_cell_copy() {
        let light = compose(
            source(
                true,
                vec![
                    section(-5, Some(vec![0xa5; 2048]), None),
                    section(20, None, Some(vec![0x3c; 2048])),
                ],
            ),
            true,
        )
        .expect("admitted initial source light");
        assert_eq!(light.position(), ChunkPos { x: -2, z: 7 });
        assert_eq!(light.generation(), ChunkGeneration(8));
        assert_eq!(light.min_light_section_y(), -5);
        assert_eq!(light.light_section_count(), 26);
        assert!(light.persisted_light_correct());
        let lower = light.layer(LightKind::Block, -5).expect("min sentinel").unwrap();
        let p0 = SectionBlockPos::new(0, 0, 0).expect("origin");
        let p1 = SectionBlockPos::new(1, 0, 0).expect("next cell");
        assert_eq!(lower.get(p0), 5);
        assert_eq!(lower.get(p1), 10);
        assert!(!lower.is_empty());
        assert!(light.layer(LightKind::Sky, -5).expect("min").is_none());
        let upper = light.layer(LightKind::Sky, 20).expect("max sentinel").unwrap();
        assert_eq!(upper.get(p0), 12);
        assert_eq!(upper.get(p1), 3);
        assert!(light.layer(LightKind::Block, 20).expect("max").is_none());
    }

    #[test]
    fn no_skylight_dimension_drops_sky_and_keeps_source_correctness_false() {
        let light = compose(
            source(
                false,
                vec![section(-4, Some(vec![0; 2048]), Some(vec![0x33; 2048]))],
            ),
            false,
        )
        .expect("valid source without skylight");
        assert!(!light.persisted_light_correct());
        assert!(!light.has_skylight());
        assert!(light.layer(LightKind::Sky, -4).unwrap().is_none());
        assert!(!light.layer(LightKind::Block, -4).unwrap().unwrap().is_empty());
        assert!(light.layer(LightKind::Block, 0).unwrap().is_none());
    }

    #[test]
    fn malformed_raw_layers_and_source_section_errors_fail_closed() {
        let malformed = source(true, vec![section(0, Some(vec![0; 2047]), None)]);
        assert!(matches!(
            compose(malformed, true),
            Err(InitialLightCompositionError::Layer {
                section_y: 0,
                kind: LightKind::Block,
                ..
            })
        ));
        let malformed_sky = source(true, vec![section(0, None, Some(vec![0; 2049]))]);
        assert!(matches!(
            compose(malformed_sky, true),
            Err(InitialLightCompositionError::Layer {
                section_y: 0,
                kind: LightKind::Sky,
                ..
            })
        ));
        let duplicate = source(
            true,
            vec![section(-5, None, None), section(-5, None, None)],
        );
        assert_eq!(
            compose(duplicate, true).unwrap_err(),
            InitialLightCompositionError::Column(ChunkLightError::DuplicateSection {
                section_y: -5,
            })
        );
        let outside = source(true, vec![section(21, Some(vec![0; 2048]), None)]);
        assert!(matches!(
            compose(outside, true),
            Err(InitialLightCompositionError::Column(
                ChunkLightError::SectionOutsideLightLattice { section_y: 21, .. }
            ))
        ));
    }

    #[test]
    fn prepared_transaction_binds_light_to_validated_stored_block_header_position() {
        let source_position = ChunkPos { x: 15, z: -12 };
        let transaction = ImportedStoredChunkWithLight {
            stored: ImportedStoredChunk {
                blocks: ImportedChunkBlocks::<Vec<u8>> {
                    header: StoredChunkHeader {
                        data_version: TARGET_DATA_VERSION_26_2,
                        position: source_position,
                        stored_section_count: 1,
                    },
                    sections: Vec::new(),
                },
                source: StoredChunkSourceMetadata {
                    region_timestamp: 25,
                    compression: ChunkCompression::Uncompressed,
                    external: false,
                },
            },
            light: source(true, vec![section(-5, Some(vec![0x21; 2048]), None)]),
        };
        let prepared = prepare_imported_chunk_light(
            transaction,
            ChunkGeneration(4),
            profile(true),
        )
        .expect("one identity-bound composition");
        assert_eq!(prepared.stored.blocks.header.position, source_position);
        assert_eq!(prepared.light.position(), source_position);
        assert_eq!(prepared.light.generation(), ChunkGeneration(4));
        assert_eq!(prepared.stored.source.region_timestamp, 25);
    }

    struct Facts;

    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, block: u8) -> SectionStateFacts {
            SectionStateFacts::new(block != 0, false, false, false)
        }
    }

    #[test]
    fn imported_light_joins_existing_coherent_chunk_clock_and_invalidates_on_change() {
        let position = ChunkPos { x: -2, z: 7 };
        let generation = ChunkGeneration(8);
        let initial_light = compose(
            source(true, vec![section(-5, Some(vec![0x11; 2048]), None)]),
            true,
        )
        .expect("valid imported light");

        let blocks = LiveChunkCore::new(
            position,
            generation,
            -4,
            (0..24)
                .map(|_| DirectBlockSection::filled(0_u8, &Facts))
                .collect(),
        )
        .expect("valid blocks");
        let biomes = ChunkBiomeColumn::new(
            position,
            generation,
            -4,
            (0..24).map(|_| DirectBiomeSection::filled(7_u16)).collect(),
        )
        .expect("valid biomes");
        let mut state = LiveChunkSemanticState::from_parts(blocks, biomes)
            .expect("block/biome composition")
            .with_initial_light(initial_light)
            .expect("light identity and pristine revision match");

        assert!(state.current_initial_light().is_some());
        let block = BlockPos {
            x: -32,
            y: -64,
            z: 112,
        };
        let no_change = state.replace_block(block, 0, &Facts).expect("no-op");
        assert!(!no_change.changed);
        assert!(state.current_initial_light().is_some());
        let changed = state.replace_block(block, 1, &Facts).expect("real mutation");
        assert!(changed.changed);
        assert!(state.current_initial_light().is_none());
    }
}
