//! COLD composition candidate connecting the borrowed authoritative chunk to the 26.2
//! target-owned section encoder, without making an unadmitted Play publication path.
//!
//! The complete coherent image (including verified initial light) is a caller-owned
//! immutable borrow. The output is a *section sequence*, never a Play packet.
//! Numeric biome IDs and outer world-wire law must be independently qualified.

use helve_generated::{BLOCK_STATE_COUNT, BlockStateId, to_vanilla_state_id};
use helve_target_26_2::r2c_block_palette::{BlockPaletteError, PackedBlockContainer};
use helve_world_chunk::{BiomeProjectionError, InitialChunkReference};
use helve_world_contract::{BLOCK_SECTION_CELLS, BiomeSection, BlockSection, SectionBlockPos};

/// A source or section invariant prevents a coherent candidate from being emitted.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum SectionCandidateError {
    /// Requested section is not in the source dimension's exact section lattice.
    MissingSection { section_y: i32 },
    /// Section counters cannot describe a 4096-cell source section.
    InvalidSummary {
        non_air_count: u16,
        fluid_count: u16,
    },
    /// The resolved global block state identity was rejected by the target reference.
    Block(BlockPaletteError),
    /// The biome ordinal or section was rejected by its source-law projection.
    Biome(BiomeProjectionError),
}

/// Appends exactly one section derived from a *single* current immutable chunk.
///
/// The target crate alone owns the section-prefix and block-container bytes.
/// Source-supplied biome IDs are not source-qualified merely by constructing this
/// reference: the biome registry ordering gate (#285) must close before Play.
///
/// Every fallible validation step finishes *before* writing to output. The only
/// long-lived owner remains the borrowed Helve semantic chunk. All work is COLD;
/// HOT get/set and chunk revision tracking are unchanged.
///
/// # Errors
///
/// Rejects an outside-lattice section, impossible summary counts, invalid block
/// identities, invalid biome registry cardinality or missing biome ordinals.
///
/// # Panics
///
/// Only if one of the already-validated 4096 local coordinates or the generated
/// 26.2 global block-state ID bound is internally inconsistent.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "R2C final packet source-admission and biome ID qualification still block live publication"
    )
)]
pub(crate) fn append_coherent_section_candidate<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    section_y: i32,
    biome_registry_count: usize,
    output: &mut Vec<u8>,
) -> Result<(), SectionCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let section = image
        .block_section(section_y)
        .ok_or(SectionCandidateError::MissingSection { section_y })?;

    let summary = section.summary();
    if usize::from(summary.non_air_count) > BLOCK_SECTION_CELLS
        || summary.fluid_count > summary.non_air_count
    {
        return Err(SectionCandidateError::InvalidSummary {
            non_air_count: summary.non_air_count,
            fluid_count: summary.fluid_count,
        });
    }

    let block = PackedBlockContainer::derive(BLOCK_STATE_COUNT, |index| {
        // The linear cell index is fixed by the source-backed YZX section law.
        // This does not compute a world coordinate, resolve a directory, or copy
        // the 4096-cell resident image.
        let x = u8::try_from(index & 15).expect("bounded local x");
        let z = u8::try_from((index >> 4) & 15).expect("bounded local z");
        let y = u8::try_from((index >> 8) & 15).expect("bounded local y");
        let pos = SectionBlockPos::new(x, y, z).expect("exact local section cell");
        u16::try_from(to_vanilla_state_id(section.get(pos)))
            .expect("generated vanilla-identity state ID is bounded by 32366")
    })
    .map_err(SectionCandidateError::Block)?;

    // Biome derivation can fail. It must run before any bytes are appended.
    let biome = image
        .biome_container(section_y, biome_registry_count)
        .map_err(SectionCandidateError::Biome)?;
    let biome_len = biome.encoded_len();

    block.append_section_candidate(
        summary.non_air_count,
        summary.fluid_count,
        biome_len,
        output,
        |bytes| biome.append_container(bytes),
    );
    Ok(())
}

/// Appends the complete bottom-to-top section column atomically to caller scratch.
///
/// Builds each section from the same borrowed world owner, with no intermediate
/// whole-column byte allocation and no second resident data representation.
/// If a *later* section has an invalid block or biome identity, truncate only
/// the candidate suffix; the caller's pre-existing bytes remain unchanged.
///
/// This is COLD candidate construction, not an admitted chunk packet or a
/// publication side effect. The caller must separately prove the 26.2 biome
/// registry order and complete enclosing chunk protocol before transmission.
///
/// # Errors
///
/// Returns the first failed section candidate and restores the original
/// destination length on any source validation error.
///
/// # Panics
///
/// Only if an already validated chunk lattice violates its signed section-Y
/// representability invariant.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "R2C outer chunk wire contract and registry IDs remain unadmitted"
    )
)]
pub(crate) fn append_coherent_section_column_candidate<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    biome_registry_count: usize,
    output: &mut Vec<u8>,
) -> Result<(), SectionCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let before = output.len();
    let blocks = image.blocks();
    for index in 0..blocks.section_count() {
        let offset = i32::try_from(index).expect("source lattice section count fits in i32");
        let section_y = blocks
            .min_section_y()
            .checked_add(offset)
            .expect("validated section lattice contains its highest section Y");
        if let Err(error) =
            append_coherent_section_candidate(image, section_y, biome_registry_count, output)
        {
            output.truncate(before);
            return Err(error);
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
    use helve_types::{ChunkGeneration, ChunkPos};
    use helve_world_chunk::{
        ChunkBiomeColumn, HeightmapStateFacts, HeightmapStateProperties, ImportedLightSection,
        InitialChunkLight, InitialChunkReference, LightDataLayer, LiveChunkCore,
        LiveChunkSemanticState, VerticalSectionLattice,
    };
    use helve_world_contract::{BlockSection, SectionBlockPos};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use super::{
        SectionCandidateError, append_coherent_section_candidate,
        append_coherent_section_column_candidate,
    };

    // Synthetic test-only predicates, deliberately NOT claimed as the 26.2
    // source-admitted global heightmap predicate table.
    struct SyntheticHeightFacts;

    impl HeightmapStateFacts<BlockStateId> for SyntheticHeightFacts {
        fn properties(&self, state: BlockStateId) -> HeightmapStateProperties {
            HeightmapStateProperties::new(state != AIR, state != AIR, false, false)
        }
    }

    type Semantic = LiveChunkSemanticState<
        BlockStateId,
        DirectBlockSection<BlockStateId>,
        u16,
        DirectBiomeSection<u16>,
    >;

    fn coherent_source() -> Semantic {
        let position = ChunkPos { x: -3, z: 4 };
        let generation = ChunkGeneration(9);
        let facts = GeneratedStateFacts;
        let mut lower = DirectBlockSection::filled(AIR, &facts);
        lower.replace(
            SectionBlockPos::new(0, 0, 0).unwrap(),
            BlockStateId::new(1).unwrap(),
            &facts,
        );
        let blocks = LiveChunkCore::new(
            position,
            generation,
            -1,
            vec![lower, DirectBlockSection::filled(AIR, &facts)],
        )
        .unwrap();
        let biomes = ChunkBiomeColumn::new(
            position,
            generation,
            -1,
            vec![
                DirectBiomeSection::filled(2_u16),
                DirectBiomeSection::filled(5_u16),
            ],
        )
        .unwrap();
        let owner = LiveChunkSemanticState::from_parts(blocks, biomes).unwrap();
        let light = InitialChunkLight::from_imported(
            position,
            generation,
            VerticalSectionLattice::new(-1, 2).unwrap(),
            true,
            true,
            vec![ImportedLightSection {
                section_y: -2,
                block: Some(LightDataLayer::homogeneous(3).unwrap()),
                sky: Some(LightDataLayer::homogeneous(15).unwrap()),
            }],
        )
        .unwrap();
        owner.with_initial_light(light).unwrap()
    }

    #[test]
    fn coherent_borrow_emits_block_and_biome_containers_in_section_order() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let original_stamp = image.stamp();
        let mut bytes = Vec::with_capacity(16_384);
        let allocation = bytes.as_ptr();

        append_coherent_section_candidate(&image, -1, 66, &mut bytes)
            .expect("synthetic lower section");
        assert_eq!(&bytes[..4], &[0, 1, 0, 0]);
        assert_eq!(&bytes[4..8], &[4, 2, 1, 0]);
        assert!(bytes.ends_with(&[0, 2, 0]));
        let lower_bytes = bytes.len();

        append_coherent_section_candidate(&image, 0, 66, &mut bytes)
            .expect("synthetic upper section");
        assert_eq!(&bytes[lower_bytes..], &[0, 0, 0, 0, 0, 0, 0, 0, 5, 0]);
        assert_eq!(bytes.as_ptr(), allocation);
        assert_eq!(image.stamp(), original_stamp);
        assert_eq!(semantic.stamp(), original_stamp);
    }

    #[test]
    fn complete_column_matches_independent_section_concatenation_in_y_order() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut expected = vec![0x81, 0x42];
        append_coherent_section_candidate(&image, -1, 66, &mut expected).unwrap();
        append_coherent_section_candidate(&image, 0, 66, &mut expected).unwrap();

        let mut actual = Vec::with_capacity(16_384);
        actual.extend_from_slice(&[0x81, 0x42]);
        let original_allocation = actual.as_ptr();
        append_coherent_section_column_candidate(&image, 66, &mut actual).unwrap();

        assert_eq!(actual, expected);
        assert_eq!(actual.as_ptr(), original_allocation);
        assert_eq!(semantic.stamp(), image.stamp());
    }

    #[test]
    fn later_section_failure_rolls_back_entire_candidate_suffix() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut output = Vec::with_capacity(16_384);
        output.extend_from_slice(&[0xAB, 0xCD, 0xEF]);
        let original_allocation = output.as_ptr();

        // Registry 0..3 accepts the lower section's ordinal 2. Its upper
        // section contains ordinal 5: the first append succeeds, but the
        // second must abort without exposing a truncated section column.
        assert!(matches!(
            append_coherent_section_column_candidate(&image, 3, &mut output),
            Err(SectionCandidateError::Biome(_))
        ));
        assert_eq!(output, &[0xAB, 0xCD, 0xEF]);
        assert_eq!(output.as_ptr(), original_allocation);

        // The same destination remains reusable after a rejected candidate.
        append_coherent_section_column_candidate(&image, 66, &mut output).unwrap();
        assert!(output.len() > 3);
        assert_eq!(output.as_ptr(), original_allocation);
    }

    #[test]
    fn rejected_section_or_registry_never_mutates_destination() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut bytes = vec![0x78, 0x56];

        assert_eq!(
            append_coherent_section_candidate(&image, -2, 66, &mut bytes),
            Err(SectionCandidateError::MissingSection { section_y: -2 })
        );
        assert_eq!(bytes, &[0x78, 0x56]);

        assert!(matches!(
            append_coherent_section_candidate(&image, -1, 0, &mut bytes),
            Err(SectionCandidateError::Biome(_))
        ));
        assert_eq!(bytes, &[0x78, 0x56]);

        assert!(matches!(
            append_coherent_section_candidate(&image, -1, 2, &mut bytes),
            Err(SectionCandidateError::Biome(_))
        ));
        assert_eq!(bytes, &[0x78, 0x56]);
    }
}
