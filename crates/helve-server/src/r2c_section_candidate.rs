//! COLD composition candidate connecting the borrowed authoritative chunk to the 26.2
//! target-owned section encoder, without making an unadmitted Play publication path.
//!
//! The complete coherent image (including verified initial light) is a caller-owned
//! immutable borrow. The output is a *section sequence*, never a Play packet.
//! Numeric biome IDs and outer world-wire law must be independently qualified.

use helve_generated::{BLOCK_STATE_COUNT, BlockStateId, to_vanilla_state_id};
use helve_target_26_2::r2c_block_palette::{BlockPaletteError, PackedBlockContainer};
use helve_target_26_2::r2c_chunk_data::{
    HeightmapMapError, SectionLengthError, append_heightmap_map_candidate,
    append_length_prefixed_sections,
};
use helve_target_26_2::r2c_light::{
    LightWireError, LightWireMasks, append_light_masks_candidate,
    append_light_update_count_candidate, append_light_update_layer_candidate,
};
use helve_world_chunk::{
    BiomeProjectionError, InitialChunkReference, LightKind, LightMaskReferenceError,
};
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

/// The exact borrowed world could not form the two leading chunk-data fields.
///
/// This remains an **incomplete** chunk-data prefix: block-entity payloads,
/// enclosing chunk coordinates/packet identity and light data are absent.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ChunkDataCandidateError {
    /// Packed heightmaps failed independent target-boundary validation.
    Heightmaps(HeightmapMapError),
    /// The section sequence was incomplete, too large or semantically invalid.
    Sections(SectionLengthError<SectionCandidateError>),
}

/// Append source-backed heightmap map and a length-delimited full section column.
///
/// Reads one immutable, whole-chunk-stamped owner. Exact heightmap/section
/// semantics use the previously admitted R2C world-state source group;
/// numeric biome IDs still require issue #285 and full chunk packet admission.
///
/// The target owns all emitted bytes. The resident world owns none. On any
/// failure, only the candidate bytes are truncated; the original output
/// prefix is preserved without an intermediate serialized chunk allocation.
///
/// # Errors
///
/// Heightmap, source-section, caller-size-cap or empty-section errors all
/// reject the entire candidate and restore the original caller buffer.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "R2C chunk packet, entity and biome ID publication remain unadmitted"
    )
)]
pub(crate) fn append_coherent_chunk_data_fields_candidate<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    biome_registry_count: usize,
    max_section_bytes: usize,
    output: &mut Vec<u8>,
) -> Result<(), ChunkDataCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let before = output.len();
    let maps = image.heightmaps().entries();
    let height = image
        .blocks()
        .section_count()
        .checked_mul(16)
        .and_then(|blocks| u16::try_from(blocks).ok())
        .expect("initial verified heightmap reference has representable section height");
    append_heightmap_map_candidate(
        output,
        height,
        [maps[0].words(), maps[1].words(), maps[2].words()],
    )
    .map_err(ChunkDataCandidateError::Heightmaps)?;

    if let Err(error) = append_length_prefixed_sections(output, max_section_bytes, |destination| {
        append_coherent_section_column_candidate(image, biome_registry_count, destination)
    }) {
        output.truncate(before);
        return Err(ChunkDataCandidateError::Sections(error));
    }
    Ok(())
}

/// A coherent source image could not be projected to initial light fields.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum LightPayloadCandidateError {
    /// Source-derived mask count/shape failed target validation.
    Wire(LightWireError),
    /// A previously classified data mask did not resolve to its source layer.
    Source(LightMaskReferenceError),
    /// Mask population and source visit count unexpectedly disagreed.
    CountMismatch {
        kind: LightKind,
        expected: usize,
        actual: usize,
    },
}

/// Append exact initial sky/block mask and raw array *field candidates*.
///
/// This uses one current and immutable `InitialChunkReference`, and writes
/// packed layers directly to the final caller scratch. A 2048-byte layer
/// is never materialized into a second temporary copy. All source failures
/// roll back to the original output prefix.
///
/// This field sequence is not itself a complete chunk-with-light Play packet.
/// The clientbound packet identity, biome registry IDs and publication order
/// remain separately source-admission blocked.
///
/// # Errors
///
/// Rejects invalid mask/lattice shape, stale or missing source layers, and
/// any disagreement between data-mask population and visited source layers.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "R2C chunk-with-light publication is not yet fully source-admitted"
    )
)]
pub(crate) fn append_coherent_light_payload_candidate<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    output: &mut Vec<u8>,
) -> Result<(), LightPayloadCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let before = output.len();
    let source = image.light_masks();
    let masks = LightWireMasks {
        sky_data: source.data_mask(LightKind::Sky),
        block_data: source.data_mask(LightKind::Block),
        sky_empty: source.empty_mask(LightKind::Sky),
        block_empty: source.empty_mask(LightKind::Block),
    };
    append_light_masks_candidate(output, source.light_section_count(), masks)
        .map_err(LightPayloadCandidateError::Wire)?;

    for kind in [LightKind::Sky, LightKind::Block] {
        let expected = usize::try_from(source.data_mask(kind).count_ones())
            .expect("at most 66 light sections");
        if let Err(error) = append_light_update_count_candidate(output, expected) {
            output.truncate(before);
            return Err(LightPayloadCandidateError::Wire(error));
        }
        let result = source.for_each_update(kind, |_section_y, layer| {
            append_light_update_layer_candidate(output, |raw| layer.write_raw_into(raw));
        });
        match result {
            Ok(actual) if actual == expected => {}
            Ok(actual) => {
                output.truncate(before);
                return Err(LightPayloadCandidateError::CountMismatch {
                    kind,
                    expected,
                    actual,
                });
            }
            Err(error) => {
                output.truncate(before);
                return Err(LightPayloadCandidateError::Source(error));
            }
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

    use helve_target_26_2::r2c_chunk_data::{
        SectionLengthError, append_heightmap_map_candidate, append_length_prefixed_sections,
    };
    use helve_target_26_2::r2c_light::{
        LightWireMasks, append_light_masks_candidate, append_light_update_count_candidate,
        append_light_update_layer_candidate,
    };

    use super::{
        ChunkDataCandidateError, SectionCandidateError,
        append_coherent_chunk_data_fields_candidate, append_coherent_light_payload_candidate,
        append_coherent_section_candidate, append_coherent_section_column_candidate,
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
    fn coherent_chunk_data_fields_match_independent_target_assembly() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut expected = vec![0xE1, 0xE2];
        let maps = image.heightmaps().entries();
        append_heightmap_map_candidate(
            &mut expected,
            32,
            [maps[0].words(), maps[1].words(), maps[2].words()],
        )
        .unwrap();
        append_length_prefixed_sections(&mut expected, 16_384, |output| {
            append_coherent_section_candidate(&image, -1, 66, output)?;
            append_coherent_section_candidate(&image, 0, 66, output)
        })
        .unwrap();

        let mut actual = Vec::with_capacity(16_384);
        actual.extend_from_slice(&[0xE1, 0xE2]);
        let allocation = actual.as_ptr();
        append_coherent_chunk_data_fields_candidate(&image, 66, 16_384, &mut actual).unwrap();
        assert_eq!(actual, expected);
        assert_eq!(actual.as_ptr(), allocation);
        assert_eq!(image.stamp(), semantic.stamp());

        // A 32-block tall world has 26 longs per heightmap. Their
        // target-owned map field starts with count=3 and type-ID=1.
        assert_eq!(&actual[2..5], &[3, 1, 26]);
    }

    #[test]
    fn late_biome_failure_and_section_limit_rollback_whole_chunk_data_suffix() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut output = Vec::with_capacity(16_384);
        output.extend_from_slice(&[0xAA, 0xBB, 0xCC]);
        let allocation = output.as_ptr();

        // Lower section biome=2 is valid in [0,3); upper section=5 is
        // invalid. Entire preceding heightmap field is also removed.
        assert!(matches!(
            append_coherent_chunk_data_fields_candidate(&image, 3, 16_384, &mut output),
            Err(ChunkDataCandidateError::Sections(
                SectionLengthError::Source(SectionCandidateError::Biome(_))
            ))
        ));
        assert_eq!(output, &[0xAA, 0xBB, 0xCC]);

        assert!(matches!(
            append_coherent_chunk_data_fields_candidate(&image, 66, 1, &mut output),
            Err(ChunkDataCandidateError::Sections(
                SectionLengthError::ExceedsLimit { .. }
            ))
        ));
        assert_eq!(output, &[0xAA, 0xBB, 0xCC]);
        assert_eq!(output.as_ptr(), allocation);

        append_coherent_chunk_data_fields_candidate(&image, 66, 16_384, &mut output).unwrap();
        assert!(output.len() > 3);
        assert_eq!(output.as_ptr(), allocation);
    }

    #[test]
    fn source_borrowed_light_payload_matches_explicit_four_masks_and_layers() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let source = image.light_masks();
        let mut expected = vec![0x43, 0x21];
        let masks = LightWireMasks {
            sky_data: source.data_mask(helve_world_chunk::LightKind::Sky),
            block_data: source.data_mask(helve_world_chunk::LightKind::Block),
            sky_empty: source.empty_mask(helve_world_chunk::LightKind::Sky),
            block_empty: source.empty_mask(helve_world_chunk::LightKind::Block),
        };
        append_light_masks_candidate(&mut expected, source.light_section_count(), masks).unwrap();
        append_light_update_count_candidate(&mut expected, 1).unwrap();
        append_light_update_layer_candidate(&mut expected, |raw| raw.fill(0xFF));
        append_light_update_count_candidate(&mut expected, 1).unwrap();
        append_light_update_layer_candidate(&mut expected, |raw| raw.fill(0x33));

        let mut actual = Vec::with_capacity(8_192);
        actual.extend_from_slice(&[0x43, 0x21]);
        let allocation = actual.as_ptr();
        append_coherent_light_payload_candidate(&image, &mut actual).unwrap();
        assert_eq!(actual, expected);
        assert_eq!(actual.as_ptr(), allocation);
        assert_eq!(semantic.stamp(), image.stamp());

        // No intermediate 2048-byte scratch: each raw layer is written
        // exactly once through the target-owned destination.
        assert_eq!(actual.len(), 2 + 4 * 9 + 2 * (1 + 2 + 2048));
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
