//! COLD composition candidate connecting the borrowed authoritative chunk to the 26.2
//! target-owned section encoder, without making an unadmitted Play publication path.
//!
//! The complete coherent image (including verified initial light) is a caller-owned
//! immutable borrow. The output is a *section sequence*, never a Play packet.
//! Numeric biome IDs and outer world-wire law must be independently qualified.

use helve_generated::{BLOCK_STATE_COUNT, BlockStateId, to_vanilla_state_id};
use helve_target_26_2::r2c_block_palette::{BlockPaletteError, PackedBlockContainer};
use helve_target_26_2::r2c_chunk_body::{
    append_chunk_coordinates_candidate, append_empty_block_entities_candidate,
};
use helve_target_26_2::r2c_chunk_data::{
    HeightmapMapError, SectionLengthError, append_heightmap_map_candidate,
    append_length_prefixed_sections,
};
use helve_target_26_2::r2c_light::{
    LightWireError, LightWireMasks, append_light_masks_candidate,
    append_light_update_count_candidate, append_light_update_layer_candidate,
};
use helve_types::ChunkPos;
use helve_world_chunk::{
    BiomeProjectionError, HeightmapStateFacts, InitialChunkReference, InitialChunkReferenceError,
    LightKind, LightMaskReferenceError,
};
use helve_world_contract::{BLOCK_SECTION_CELLS, BiomeSection, BlockSection, SectionBlockPos};
use helve_world_import::{
    EmptyBlockEntityEvidenceError, StoredBlockEntityEvidence, StoredChunkHeader,
    TARGET_DATA_VERSION_26_2,
};
use helve_world_load::{SourceChunkPublicationReceipt, SourceChunkReceiptError};
use helve_world_runtime::SemanticDimensionInstance;

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

/// Byte spans of two jointly derived fields in one reusable COLD buffer.
///
/// These ranges are not a chunk-with-light packet: its **block-entity list**
/// belongs between the two spans, and the packet ID/coordinates precede them.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct ChunkAndLightFieldSpans {
    /// Heightmaps followed by VarInt-length-prefixed section payloads.
    pub chunk_data_fields: std::ops::Range<usize>,
    /// Four light masks followed by ordered sky and block arrays.
    pub light_fields: std::ops::Range<usize>,
}

/// Rejected coherent chunk-data/light fragment construction.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ChunkAndLightCandidateError {
    /// The section or heightmap candidate failed validation.
    ChunkData(ChunkDataCandidateError),
    /// The initially verified light reference failed on materialization.
    Light(LightPayloadCandidateError),
}

/// Builds both R2C fragments from the *same* immutable, stamped source image.
///
/// This is COLD target-boundary construction only. No source copy, second
/// packet byte vector, second chunk revision clock, or resident cache is
/// introduced. A late light failure rolls back the **entire** fragment
/// sequence, including any preceding heightmap/section candidate bytes.
///
/// The ranges are explicitly separate, so a future source-admitted outer
/// encoder can place the proven block-entity field between them instead of
/// accidentally treating them as contiguous chunk-with-light wire bytes.
///
/// # Errors
///
/// Rejects either candidate and preserves the caller's original bytes.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "R2C outer packet and block-entity source law remain unadmitted"
    )
)]
pub(crate) fn append_coherent_chunk_and_light_fragments<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    biome_registry_count: usize,
    max_section_bytes: usize,
    output: &mut Vec<u8>,
) -> Result<ChunkAndLightFieldSpans, ChunkAndLightCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let start = output.len();
    append_coherent_chunk_data_fields_candidate(
        image,
        biome_registry_count,
        max_section_bytes,
        output,
    )
    .map_err(ChunkAndLightCandidateError::ChunkData)?;
    let split = output.len();
    if let Err(error) = append_coherent_light_payload_candidate(image, output) {
        output.truncate(start);
        return Err(ChunkAndLightCandidateError::Light(error));
    }
    Ok(ChunkAndLightFieldSpans {
        chunk_data_fields: start..split,
        light_fields: split..output.len(),
    })
}

/// Separate byte spans of a complete *candidate* body, without packet ID.
///
/// Every range addresses the same caller-owned destination. No resident
/// packet image or second serialized buffer is retained.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct EmptyChunkBodyFieldSpans {
    /// The two candidate chunk position integers.
    pub position: std::ops::Range<usize>,
    /// Heightmap map and length-prefixed section bytes.
    pub chunk_data: std::ops::Range<usize>,
    /// Explicitly empty block-entity list candidate.
    pub block_entities: std::ops::Range<usize>,
    /// Four light masks and source-ordered sky/block arrays.
    pub light: std::ops::Range<usize>,
}

/// Rejections from the selected, saved-explicitly-empty-body profile.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum EmptyChunkBodyCandidateError {
    /// The saved chunk is not the exact borrowed resident position.
    PositionMismatch {
        source: ChunkPos,
        resident: ChunkPos,
    },
    /// A different saved `DataVersion` cannot be interpreted under 26.2 rules.
    DataVersionMismatch { source: i32 },
    /// Missing or nonempty saved block entities cannot authorize an empty list.
    BlockEntities(EmptyBlockEntityEvidenceError),
    /// Heightmap/section projection was rejected.
    ChunkData(ChunkDataCandidateError),
    /// Light projection was rejected.
    Light(LightPayloadCandidateError),
}

/// Append a COLD, source-evidence-gated *candidate* 26.2 chunk-with-light body.
///
/// The saved source header and block-entity evidence must come from the same
/// caller-held import transaction. Source positional identity is checked
/// against this immutable stamped resident borrow *before* any output write.
/// No inferred empty entity list is ever accepted. Exact packet ID, registry
/// assignment, publication order and source review of the entire body remain
/// blocked; **do not send this candidate to a vanilla client**.
///
/// Only the existing caller-owned scratch is used, with checked rollback
/// across *all* fields if later section or light projection fails. This
/// code adds no HOT path check, resident cache, copy or second clock.
///
/// # Errors
///
/// Rejects target/version identity, missing/nonempty saved entity evidence,
/// section/biome encoding or light materialization. All preserve the original
/// destination prefix.
pub(crate) fn append_explicit_empty_chunk_body_candidate<BlockStorage, BiomeStorage>(
    image: &InitialChunkReference<'_, BlockStateId, BlockStorage, u16, BiomeStorage>,
    stored: &StoredChunkHeader,
    evidence: StoredBlockEntityEvidence,
    biome_registry_count: usize,
    max_section_bytes: usize,
    output: &mut Vec<u8>,
) -> Result<EmptyChunkBodyFieldSpans, EmptyChunkBodyCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    let resident = image.position();
    if stored.position != resident {
        return Err(EmptyChunkBodyCandidateError::PositionMismatch {
            source: stored.position,
            resident,
        });
    }
    if stored.data_version != TARGET_DATA_VERSION_26_2 {
        return Err(EmptyChunkBodyCandidateError::DataVersionMismatch {
            source: stored.data_version,
        });
    }
    evidence
        .require_explicitly_empty()
        .map_err(EmptyChunkBodyCandidateError::BlockEntities)?;

    let start = output.len();
    append_chunk_coordinates_candidate(output, resident.x, resident.z);
    let after_position = output.len();
    if let Err(error) = append_coherent_chunk_data_fields_candidate(
        image,
        biome_registry_count,
        max_section_bytes,
        output,
    ) {
        output.truncate(start);
        return Err(EmptyChunkBodyCandidateError::ChunkData(error));
    }
    let after_chunk_data = output.len();
    append_empty_block_entities_candidate(output);
    let after_entities = output.len();
    if let Err(error) = append_coherent_light_payload_candidate(image, output) {
        output.truncate(start);
        return Err(EmptyChunkBodyCandidateError::Light(error));
    }
    Ok(EmptyChunkBodyFieldSpans {
        position: start..after_position,
        chunk_data: after_position..after_chunk_data,
        block_entities: after_chunk_data..after_entities,
        light: after_entities..output.len(),
    })
}

/// A source receipt cannot authorize this candidate against the live owner.
#[derive(Debug)]
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "Dormant R2C source-verified body candidate has no Play consumer"
    )
)]
pub(crate) enum ReceiptBoundBodyCandidateError {
    /// The publication cursor outlived its immutable source-receipt selection.
    MissingReceipt { index: usize, available: usize },
    /// Original dimension/position/incarnation, revision, or empty-list evidence failed.
    Receipt(SourceChunkReceiptError),
    /// Current source heightmaps/light cannot form a coherent immutable borrow.
    Reference(InitialChunkReferenceError),
    /// Target-owned candidate field encoding was rejected.
    Body(EmptyChunkBodyCandidateError),
}

/// Build one explicitly-empty body only from a proven, current import receipt.
///
/// The source proof is minted by world-load *after* a real installation; it
/// cannot be synthesized by passing a header and evidence separately.
/// One COLD dimension-handle resolution verifies dimension and generation;
/// a pristine revision check rejects post-import mutation. The resulting
/// immutable chunk borrow stays live across every output write, excluding
/// concurrent/unrelated unload or mutation during synchronous projection.
///
/// All source/target work is at the COLD publication boundary. No resident
/// block-entity sidecar, extra HOT revision work, second packet buffer or
/// implicit protocol admission is introduced.
///
/// **Not a Play route.** Outer packet identity/SEM, client numeric biome IDs
/// and publication ordering still require distinct 26.2 source admission.
///
/// # Errors
///
/// Receipt, coherent reference, or candidate body failure; no bytes remain
/// appended on any rejection.
pub(crate) fn append_receipt_bound_empty_chunk_body_candidate<BlockStorage, BiomeStorage, F>(
    dimension: &SemanticDimensionInstance<BlockStateId, BlockStorage, u16, BiomeStorage>,
    receipt: &SourceChunkPublicationReceipt,
    facts: &F,
    biome_registry_count: usize,
    max_section_bytes: usize,
    output: &mut Vec<u8>,
) -> Result<EmptyChunkBodyFieldSpans, ReceiptBoundBodyCandidateError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
    F: HeightmapStateFacts<BlockStateId>,
{
    let (source, header) = receipt
        .resolve_explicitly_empty(dimension)
        .map_err(ReceiptBoundBodyCandidateError::Receipt)?;
    let image = InitialChunkReference::derive(source, facts)
        .map_err(ReceiptBoundBodyCandidateError::Reference)?;
    append_explicit_empty_chunk_body_candidate(
        &image,
        &header,
        StoredBlockEntityEvidence::ExplicitlyEmpty,
        biome_registry_count,
        max_section_bytes,
        output,
    )
    .map_err(ReceiptBoundBodyCandidateError::Body)
}

#[cfg(test)]
mod tests {
    use helve_connection_core::{ConnectionLimits, IngressBuffer};
    use helve_connection_driver::{ConnectionDriver, DriverError};
    use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
    use helve_publication_core::{PublicationCursor, PublicationStep};
    use helve_session_core::LivenessState;
    use helve_target_26_2::r2b::TeleportTransaction;
    use helve_target_26_2::r2c_chunk_body::{
        append_chunk_coordinates_candidate, append_empty_block_entities_candidate,
    };
    use helve_target_26_2::r2c_play_wire::{
        CLIENTBOUND_CHUNK_BATCH_FINISHED, CLIENTBOUND_CHUNK_BATCH_START,
        CLIENTBOUND_CHUNK_WITH_LIGHT, append_chunk_with_light_packet_id,
    };
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
    use helve_world_chunk::{
        ChunkBiomeColumn, HeightmapStateFacts, HeightmapStateProperties, ImportedLightSection,
        InitialChunkLight, InitialChunkReference, LightDataLayer, LiveChunkCore,
        LiveChunkSemanticState, VerticalSectionLattice,
    };
    use helve_world_contract::{BlockSection, SectionBlockPos};
    use helve_world_import::{
        ChunkCompression, EmptyBlockEntityEvidenceError, ImportedBiomeSection,
        ImportedBlockSection, ImportedChunkBlocks, ImportedStoredBiomes, ImportedStoredChunk,
        ImportedStoredChunkWithBiomeLight, ImportedStoredLight, ImportedStoredLightSection,
        StoredBlockEntityEvidence, StoredChunkHeader, StoredChunkSourceMetadata,
        TARGET_DATA_VERSION_26_2,
    };
    use helve_world_load::{
        SourceChunkPublicationReceipt, SourceChunkReceiptError,
        install_source_biome_chunk_with_receipt,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};

    use helve_target_26_2::r2c_chunk_data::{
        SectionLengthError, append_heightmap_map_candidate, append_length_prefixed_sections,
    };
    use helve_target_26_2::r2c_light::{
        LightWireMasks, append_light_masks_candidate, append_light_update_count_candidate,
        append_light_update_layer_candidate,
    };

    use crate::r2b_server::R2bPlaySession;
    use crate::r2c_chunk_batch::{ChunkBatchInboundStep, ChunkBatchStep};
    use crate::r2c_heightmap_facts::CandidateHeightmapFacts;
    use crate::r2c_initial_view::{InitialViewSelectionError, prepare_initial_source_view};

    use super::{
        ChunkAndLightCandidateError, ChunkDataCandidateError, EmptyChunkBodyCandidateError,
        ReceiptBoundBodyCandidateError, SectionCandidateError,
        append_coherent_chunk_and_light_fragments, append_coherent_chunk_data_fields_candidate,
        append_coherent_light_payload_candidate, append_coherent_section_candidate,
        append_coherent_section_column_candidate, append_explicit_empty_chunk_body_candidate,
        append_receipt_bound_empty_chunk_body_candidate,
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

    type ImportedDimension = SemanticDimensionInstance<
        BlockStateId,
        DirectBlockSection<BlockStateId>,
        u16,
        DirectBiomeSection<u16>,
    >;

    fn imported_source_receipt(
        evidence: StoredBlockEntityEvidence,
    ) -> (ImportedDimension, SourceChunkPublicationReceipt) {
        let mut dim = ImportedDimension::new(
            DimensionId(8),
            DimensionRuntimeProfile::new(DimensionTypeId(4), -16, 32, true).unwrap(),
        );
        let receipt =
            install_source_receipt_in_dimension(&mut dim, ChunkPos { x: 2, z: 3 }, evidence);
        (dim, receipt)
    }

    fn install_source_receipt_in_dimension(
        dim: &mut ImportedDimension,
        position: ChunkPos,
        evidence: StoredBlockEntityEvidence,
    ) -> SourceChunkPublicationReceipt {
        install_source_receipt_with_column_states(dim, position, evidence, None)
    }

    // Test-only structured import evidence: caller-selected valid global
    // vanilla IDs populate two different source sections in one column.
    // Ordinary receipt tests retain the original all-air fixture.
    fn install_source_receipt_with_column_states(
        dim: &mut ImportedDimension,
        position: ChunkPos,
        evidence: StoredBlockEntityEvidence,
        column: Option<(BlockStateId, BlockStateId)>,
    ) -> SourceChunkPublicationReceipt {
        let mut sections = Vec::new();
        if let Some((ground, leaves)) = column {
            let mut lower = DirectBlockSection::filled(AIR, &GeneratedStateFacts);
            let mut upper = DirectBlockSection::filled(AIR, &GeneratedStateFacts);
            lower.replace(
                SectionBlockPos::new(1, 3, 1).unwrap(),
                ground,
                &GeneratedStateFacts,
            );
            upper.replace(
                SectionBlockPos::new(1, 15, 1).unwrap(),
                leaves,
                &GeneratedStateFacts,
            );
            sections.push(ImportedBlockSection {
                section_y: -1,
                section: lower,
            });
            sections.push(ImportedBlockSection {
                section_y: 0,
                section: upper,
            });
        }
        let imported = ImportedStoredChunkWithBiomeLight {
            stored: ImportedStoredChunk {
                blocks: ImportedChunkBlocks {
                    header: StoredChunkHeader {
                        position,
                        data_version: TARGET_DATA_VERSION_26_2,
                        stored_section_count: 2,
                    },
                    sections,
                },
                source: StoredChunkSourceMetadata {
                    region_timestamp: 10,
                    compression: ChunkCompression::Uncompressed,
                    external: false,
                },
            },
            block_entities: evidence,
            light: ImportedStoredLight {
                persisted_light_correct: true,
                sections: vec![ImportedStoredLightSection {
                    section_y: -2,
                    block: Some(vec![0x33; 2048]),
                    sky: Some(vec![0xff; 2048]),
                }],
            },
            biomes: ImportedStoredBiomes {
                sections: vec![
                    ImportedBiomeSection {
                        section_y: -1,
                        section: DirectBiomeSection::filled(2_u16),
                    },
                    ImportedBiomeSection {
                        section_y: 0,
                        section: DirectBiomeSection::filled(5_u16),
                    },
                ],
            },
        };
        install_source_biome_chunk_with_receipt(dim, imported, || {
            DirectBlockSection::filled(AIR, &GeneratedStateFacts)
        })
        .expect("real COLD importer and directory mint receipt")
    }
    // This synthetic packet identity is strictly test-local; it is NOT a
    // Minecraft 26.2 Play ID and never reaches the product runtime.
    const SYNTHETIC_CHUNK_PACKET_ID: u8 = 0x55;

    fn emit_synthetic_receipt_window_one(
        session: &mut R2bPlaySession,
        dimension: &ImportedDimension,
        receipts: &[SourceChunkPublicationReceipt],
        cursor: &mut PublicationCursor,
        scratch: &mut Vec<u8>,
    ) -> Result<PublicationStep, DriverError<ReceiptBoundBodyCandidateError>> {
        session.service_play_projected_one(receipts.len(), cursor, scratch, |index, output| {
            output.push(SYNTHETIC_CHUNK_PACKET_ID);
            append_receipt_bound_empty_chunk_body_candidate(
                dimension,
                &receipts[index],
                &SyntheticHeightFacts,
                66,
                16_384,
                output,
            )
            .map(|_| ())
        })
    }

    #[test]
    #[expect(
        clippy::too_many_lines,
        reason = "one continuous end-to-end lifecycle must test two receipts, egress retry and stale source ownership together"
    )]
    fn two_imported_receipts_stream_through_single_r2b_driver_with_backpressure() {
        let mut dim = ImportedDimension::new(
            DimensionId(8),
            DimensionRuntimeProfile::new(DimensionTypeId(4), -16, 32, true).unwrap(),
        );
        let left = ChunkPos { x: 2, z: 3 };
        let right = ChunkPos { x: -7, z: 11 };
        let receipts = [
            install_source_receipt_in_dimension(
                &mut dim,
                left,
                StoredBlockEntityEvidence::ExplicitlyEmpty,
            ),
            install_source_receipt_in_dimension(
                &mut dim,
                right,
                StoredBlockEntityEvidence::ExplicitlyEmpty,
            ),
        ];

        // Both packets individually fit. Their combined framed bytes do
        // not, forcing a real same-driver retry rather than a second queue.
        let limits = ConnectionLimits::new(8_192, 32_768, 8_196).unwrap();
        let mut session = R2bPlaySession {
            driver: ConnectionDriver::new(limits),
            read_scratch: vec![0; 32].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        };
        let retained_read_scratch = session.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(16_384);
        scratch.push(0xEE);
        let scratch_allocation = scratch.as_ptr();
        let mut cursor = PublicationCursor::new();

        let first = emit_synthetic_receipt_window_one(
            &mut session,
            &dim,
            &receipts,
            &mut cursor,
            &mut scratch,
        )
        .expect("first receipt can publish one full synthetic body");
        assert!(matches!(first, PublicationStep::Queued { index: 0, .. }));
        assert_eq!(cursor.next_index(), 1);
        assert_eq!(scratch, [0xEE]);
        assert_eq!(scratch.as_ptr(), scratch_allocation);
        assert_eq!(session.read_scratch.as_ptr(), retained_read_scratch);

        let original_egress = session.pending_play_egress().to_vec();
        let mut reader = IngressBuffer::new(limits);
        reader.push(&original_egress).unwrap();
        let first_frame = reader.peek_frame().unwrap().unwrap();
        assert_eq!(
            first_frame.packet_id(),
            i32::from(SYNTHETIC_CHUNK_PACKET_ID)
        );
        assert_eq!(first_frame.stream_bytes(), original_egress.len());
        assert_eq!(&first_frame.payload()[..4], &left.x.to_be_bytes());
        assert_eq!(&first_frame.payload()[4..8], &left.z.to_be_bytes());

        assert!(matches!(
            emit_synthetic_receipt_window_one(
                &mut session,
                &dim,
                &receipts,
                &mut cursor,
                &mut scratch,
            ),
            Err(DriverError::Buffer(
                helve_connection_core::ConnectionBufferError::EgressLimitExceeded { .. }
            ))
        ));
        assert_eq!(cursor.next_index(), 1);
        assert_eq!(session.pending_play_egress(), original_egress);
        assert_eq!(scratch, [0xEE]);
        assert_eq!(scratch.as_ptr(), scratch_allocation);

        session
            .consume_play_written(original_egress.len())
            .expect("the original driver drains the first frame");
        assert!(matches!(
            emit_synthetic_receipt_window_one(
                &mut session,
                &dim,
                &receipts,
                &mut cursor,
                &mut scratch,
            ),
            Ok(PublicationStep::Queued { index: 1, .. })
        ));
        assert_eq!(cursor.next_index(), 2);
        assert_eq!(scratch, [0xEE]);
        assert_eq!(scratch.as_ptr(), scratch_allocation);
        assert!(matches!(
            emit_synthetic_receipt_window_one(
                &mut session,
                &dim,
                &receipts,
                &mut cursor,
                &mut scratch,
            ),
            Ok(PublicationStep::Complete)
        ));

        let second_wire = session.pending_play_egress().to_vec();
        let mut reader = IngressBuffer::new(limits);
        reader.push(&second_wire).unwrap();
        let second_frame = reader.peek_frame().unwrap().unwrap();
        assert_eq!(
            second_frame.packet_id(),
            i32::from(SYNTHETIC_CHUNK_PACKET_ID)
        );
        assert_eq!(&second_frame.payload()[..4], &right.x.to_be_bytes());
        assert_eq!(&second_frame.payload()[4..8], &right.z.to_be_bytes());

        // A new publication selection cannot silently use an old receipt
        // after a real world mutation, even with other bytes already queued.
        dim.resolve_chunk_mut(receipts[0].installed().handle)
            .unwrap()
            .replace_block(
                BlockPos {
                    x: 32,
                    y: -16,
                    z: 48,
                },
                BlockStateId::new(1).unwrap(),
                &GeneratedStateFacts,
            )
            .unwrap();
        let mut fresh_cursor = PublicationCursor::new();
        assert!(matches!(
            emit_synthetic_receipt_window_one(
                &mut session,
                &dim,
                &receipts,
                &mut fresh_cursor,
                &mut scratch,
            ),
            Err(DriverError::Handler(
                ReceiptBoundBodyCandidateError::Receipt(SourceChunkReceiptError::Revised { .. })
            ))
        ));
        assert_eq!(fresh_cursor.next_index(), 0);
        assert_eq!(session.pending_play_egress(), second_wire);
        assert_eq!(scratch, [0xEE]);
        assert_eq!(scratch.as_ptr(), scratch_allocation);
        assert_eq!(session.read_scratch.as_ptr(), retained_read_scratch);
    }

    #[test]
    #[allow(
        clippy::too_many_lines,
        reason = "one complete receipt-bound batch must test import, shared-driver output and ack lifecycle together"
    )]
    fn two_real_source_receipts_emit_exact_chunk_batch_envelope_on_retained_play_driver() {
        let (mut dim, first) = imported_source_receipt(StoredBlockEntityEvidence::ExplicitlyEmpty);
        let second = install_source_receipt_in_dimension(
            &mut dim,
            ChunkPos { x: -7, z: 11 },
            StoredBlockEntityEvidence::ExplicitlyEmpty,
        );
        // Deliberately feed reverse-distance receipts: source selection
        // must reorder them without copying chunk state or packet bytes.
        let mut receipts = vec![second, first];
        let center = ChunkPos { x: 2, z: 3 };
        let mut state = prepare_initial_source_view(&dim, &mut receipts, center, 16)
            .expect("two current source receipts lie within rounded initial view");
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(receipts[0].installed().handle.position, center);
        assert_eq!(
            receipts[1].installed().handle.position,
            ChunkPos { x: -7, z: 11 }
        );
        let limits = ConnectionLimits::new(16_384, 32_768, 65_536).unwrap();
        let mut session = R2bPlaySession {
            driver: ConnectionDriver::new(limits),
            read_scratch: vec![0; 32].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        };
        let read_ptr = session.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(16_384);
        scratch.push(0xe7);
        let projection_ptr = scratch.as_ptr();
        state.on_tick();

        let project_receipt = |index: usize, output: &mut Vec<u8>| {
            append_chunk_with_light_packet_id(output);
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipts[index],
                &SyntheticHeightFacts,
                66,
                16_384,
                output,
            )
            .map(|_| ())
        };

        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project_receipt),
            Ok(ChunkBatchStep::CacheCenterQueued { x: 2, z: 3 })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project_receipt),
            Ok(ChunkBatchStep::Started { count: 2 })
        ));
        for expected in 0..receipts.len() {
            assert!(matches!(
                session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project_receipt),
                Ok(ChunkBatchStep::ChunkQueued { index, body_bytes })
                    if index == expected && body_bytes > 8
            ));
            assert_eq!(scratch, [0xe7]);
            assert_eq!(scratch.as_ptr(), projection_ptr);
        }
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project_receipt),
            Ok(ChunkBatchStep::Finished { count: 2 })
        ));
        assert_eq!(session.read_scratch.as_ptr(), read_ptr);
        assert_eq!(state.next_chunk_index(), 2);
        assert_eq!(state.unacknowledged_batches(), 1);

        let mut reader = IngressBuffer::new(limits);
        reader.push(session.pending_play_egress()).unwrap();
        let cache_center = reader.peek_frame().unwrap().unwrap();
        assert_eq!(cache_center.packet_id(), 94);
        assert_eq!(cache_center.payload(), [2, 3]);
        let consumed = cache_center.stream_bytes();
        reader.consume(consumed).unwrap();

        let start = reader.peek_frame().unwrap().unwrap();
        assert_eq!(start.packet_id(), i32::from(CLIENTBOUND_CHUNK_BATCH_START));
        assert!(start.payload().is_empty());
        let consumed = start.stream_bytes();
        reader.consume(consumed).unwrap();

        for receipt in &receipts {
            let expected = receipt.installed().handle.position;
            let frame = reader.peek_frame().unwrap().unwrap();
            assert_eq!(frame.packet_id(), i32::from(CLIENTBOUND_CHUNK_WITH_LIGHT));
            assert_eq!(&frame.payload()[..4], &expected.x.to_be_bytes());
            assert_eq!(&frame.payload()[4..8], &expected.z.to_be_bytes());
            let consumed = frame.stream_bytes();
            reader.consume(consumed).unwrap();
        }
        let finish = reader.peek_frame().unwrap().unwrap();
        assert_eq!(
            finish.packet_id(),
            i32::from(CLIENTBOUND_CHUNK_BATCH_FINISHED)
        );
        assert_eq!(finish.payload(), [2]);
        let consumed = finish.stream_bytes();
        reader.consume(consumed).unwrap();
        assert_eq!(reader.buffered_len(), 0);

        // A genuine inbound acknowledgement uses the same retained ingress.
        session.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            session.process_one_r2c_chunk_batch_ack(&mut state),
            Ok(ChunkBatchInboundStep::Received {
                desired_per_tick: 9.0
            })
        );
        assert_eq!(state.unacknowledged_batches(), 0);
        assert_eq!(session.read_scratch.as_ptr(), read_ptr);
        assert_eq!(scratch.as_ptr(), projection_ptr);
    }

    #[test]
    fn first_view_preflight_rejects_duplicate_foreign_empty_and_stale_receipts() {
        let (mut dim, first) = imported_source_receipt(StoredBlockEntityEvidence::ExplicitlyEmpty);
        let center = first.installed().handle.position;

        let mut repeated = vec![first, first];
        assert!(matches!(
            prepare_initial_source_view(&dim, &mut repeated, center, 4),
            Err(InitialViewSelectionError::DuplicateReceipt { position })
                if position == center
        ));
        let mut only = vec![first];
        assert!(matches!(
            prepare_initial_source_view(&dim, &mut only, center, 1),
            Err(InitialViewSelectionError::InvalidViewDistance { actual: 1 })
        ));
        assert_eq!(only.len(), 1);

        let mut outside = vec![first];
        assert!(matches!(
            prepare_initial_source_view(&dim, &mut outside, ChunkPos { x: 40, z: 40 }, 2,),
            Err(InitialViewSelectionError::EmptyView)
        ));
        assert!(outside.is_empty());

        let foreign_dim = ImportedDimension::new(
            DimensionId(14),
            DimensionRuntimeProfile::new(DimensionTypeId(4), -16, 32, true).unwrap(),
        );
        let mut foreign = vec![first];
        assert!(matches!(
            prepare_initial_source_view(&foreign_dim, &mut foreign, center, 4),
            Err(InitialViewSelectionError::ForeignDimension {
                position,
                actual: DimensionId(8),
                expected: DimensionId(14),
            }) if position == center
        ));
        assert_eq!(foreign.len(), 1);

        dim.unload_chunk(first.installed().handle).unwrap();
        let mut stale = vec![first];
        assert!(matches!(
            prepare_initial_source_view(&dim, &mut stale, center, 4),
            Err(InitialViewSelectionError::InvalidReceipt { position, .. })
                if position == center
        ));
        // Failures never claim source publication authority.
        assert_eq!(stale.len(), 1);
    }

    #[test]
    #[allow(
        clippy::too_many_lines,
        reason = "official runtime facts must survive the entire source receipt/heightmap/wire/batch/ACK path"
    )]
    fn official_heightmap_facts_reach_receipt_bound_chunk_packet() {
        let Some(path) = std::env::var_os("HELVE_R2C_HEIGHTMAP_CANDIDATE") else {
            // Ordinary hermetic CI cannot claim runtime-probe evidence.
            return;
        };
        let bytes = std::fs::read(path).expect("official pinned runtime oracle bytes");
        let facts = CandidateHeightmapFacts::from_oracle_bytes(&bytes)
            .expect("all 32366 bytes must agree with independently generated mutation flags");
        let selected_leaf = bytes
            .iter()
            .position(|&f| f & 0b1011 == 0b1011)
            .expect("runtime contains motion-blocking leaves");
        let selected_ground = bytes
            .iter()
            .position(|&f| f & 0b1011 == 0b0011)
            .expect("runtime contains non-leaf motion-blocking ground");
        let leaf = BlockStateId::new(u32::try_from(selected_leaf).unwrap()).unwrap();
        let ground = BlockStateId::new(u32::try_from(selected_ground).unwrap()).unwrap();

        let mut dim = ImportedDimension::new(
            DimensionId(8),
            DimensionRuntimeProfile::new(DimensionTypeId(4), -16, 32, true).unwrap(),
        );
        let center = ChunkPos { x: -3, z: 4 };
        let receipt = install_source_receipt_with_column_states(
            &mut dim,
            center,
            StoredBlockEntityEvidence::ExplicitlyEmpty,
            Some((ground, leaf)),
        );
        let mut receipts = vec![receipt];
        let mut state = prepare_initial_source_view(&dim, &mut receipts, center, 4)
            .expect("current source fixture is inside selected view");
        let limits = ConnectionLimits::new(16_384, 32_768, 65_536).unwrap();
        let mut session = R2bPlaySession {
            driver: ConnectionDriver::new(limits),
            read_scratch: vec![0; 32].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        };
        let read_ptr = session.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(16_384);
        let projection_ptr = scratch.as_ptr();
        state.on_tick();
        let project = |index: usize, output: &mut Vec<u8>| {
            append_chunk_with_light_packet_id(output);
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipts[index],
                &facts,
                66,
                16_384,
                output,
            )
            .map(|_| ())
        };
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project),
            Ok(ChunkBatchStep::CacheCenterQueued { x: -3, z: 4 })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project),
            Ok(ChunkBatchStep::Started { count: 1 })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project),
            Ok(ChunkBatchStep::ChunkQueued { index: 0, .. })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut state, &mut scratch, project),
            Ok(ChunkBatchStep::Finished { count: 1 })
        ));
        assert_eq!(session.read_scratch.as_ptr(), read_ptr);
        assert_eq!(scratch.as_ptr(), projection_ptr);
        assert!(scratch.is_empty());

        // One two-section 32-block column, bitsPerEntry=6, ten per long.
        // Column x=1,z=1 is index 17 -> second word at bit 7*6.
        // Top leaf is at absolute Y=15 => relative height 32.
        // Lower non-leaf solid is at Y=-13 => relative height 4.
        let mut surface = [0_u64; 26];
        let mut motion = [0_u64; 26];
        let mut without_leaves = [0_u64; 26];
        surface[1] = 32_u64 << 42;
        motion[1] = 32_u64 << 42;
        without_leaves[1] = 4_u64 << 42;
        let mut expected_heightmap_bytes = Vec::new();
        append_heightmap_map_candidate(
            &mut expected_heightmap_bytes,
            32,
            [&surface, &motion, &without_leaves],
        )
        .expect("exact independent expected three-map wire projection");

        let mut reader = IngressBuffer::new(limits);
        reader.push(session.pending_play_egress()).unwrap();
        let cache_center = reader.peek_frame().unwrap().unwrap();
        assert_eq!(cache_center.packet_id(), 94);
        let consumed = cache_center.stream_bytes();
        reader.consume(consumed).unwrap();
        let start = reader.peek_frame().unwrap().unwrap();
        assert_eq!(start.packet_id(), i32::from(CLIENTBOUND_CHUNK_BATCH_START));
        let consumed = start.stream_bytes();
        reader.consume(consumed).unwrap();
        let chunk = reader.peek_frame().unwrap().unwrap();
        assert_eq!(chunk.packet_id(), i32::from(CLIENTBOUND_CHUNK_WITH_LIGHT));
        assert_eq!(&chunk.payload()[..4], &center.x.to_be_bytes());
        assert_eq!(&chunk.payload()[4..8], &center.z.to_be_bytes());
        assert_eq!(
            &chunk.payload()[8..8 + expected_heightmap_bytes.len()],
            expected_heightmap_bytes,
        );
        assert!(chunk.payload().len() > 8 + expected_heightmap_bytes.len());
        let consumed = chunk.stream_bytes();
        reader.consume(consumed).unwrap();
        let finish = reader.peek_frame().unwrap().unwrap();
        assert_eq!(
            finish.packet_id(),
            i32::from(CLIENTBOUND_CHUNK_BATCH_FINISHED)
        );
        assert_eq!(finish.payload(), [1]);
        let consumed = finish.stream_bytes();
        reader.consume(consumed).unwrap();
        assert_eq!(reader.buffered_len(), 0);

        session.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            session.process_one_r2c_chunk_batch_ack(&mut state),
            Ok(ChunkBatchInboundStep::Received {
                desired_per_tick: 9.0,
            })
        );
        assert_eq!(state.unacknowledged_batches(), 0);
    }

    #[test]
    fn source_provenance_is_resolved_before_any_candidate_byte() {
        let (mut dim, receipt) =
            imported_source_receipt(StoredBlockEntityEvidence::ExplicitlyEmpty);
        let mut actual = Vec::with_capacity(16_384);
        actual.push(0x77);
        let allocation = actual.as_ptr();
        let spans = append_receipt_bound_empty_chunk_body_candidate(
            &dim,
            &receipt,
            &SyntheticHeightFacts,
            66,
            16_384,
            &mut actual,
        )
        .expect("real receipt bounds candidate to current owner");
        assert_eq!(spans.position.start, 1);
        assert_eq!(&actual[spans.block_entities], &[0]);
        assert_eq!(actual.as_ptr(), allocation);

        dim.resolve_chunk_mut(receipt.installed().handle)
            .unwrap()
            .replace_block(
                BlockPos {
                    x: 32,
                    y: -16,
                    z: 48,
                },
                BlockStateId::new(1).unwrap(),
                &GeneratedStateFacts,
            )
            .unwrap();
        let mut stale = vec![0xAA, 0xBB];
        assert!(matches!(
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipt,
                &SyntheticHeightFacts,
                66,
                16_384,
                &mut stale
            ),
            Err(ReceiptBoundBodyCandidateError::Receipt(
                SourceChunkReceiptError::Revised { .. }
            ))
        ));
        assert_eq!(stale, [0xAA, 0xBB]);

        dim.unload_chunk(receipt.installed().handle).unwrap();
        assert!(matches!(
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipt,
                &SyntheticHeightFacts,
                66,
                16_384,
                &mut stale
            ),
            Err(ReceiptBoundBodyCandidateError::Receipt(
                SourceChunkReceiptError::Resident(_)
            ))
        ));
        assert_eq!(stale, [0xAA, 0xBB]);
    }

    #[test]
    fn receipt_body_and_reference_errors_retain_inspectable_causes() {
        let (dim, receipt) = imported_source_receipt(StoredBlockEntityEvidence::ExplicitlyEmpty);
        let mut out = vec![0x21, 0x43];
        assert!(matches!(
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipt,
                &SyntheticHeightFacts,
                1,
                16_384,
                &mut out
            ),
            Err(ReceiptBoundBodyCandidateError::Body(
                EmptyChunkBodyCandidateError::ChunkData(_)
            ))
        ));
        assert_eq!(out, [0x21, 0x43]);

        // The coherent-reference failure retains its exact source cause;
        // a future operator must not collapse it into generic packet failure.
        let rejection = ReceiptBoundBodyCandidateError::Reference(
            helve_world_chunk::InitialChunkReferenceError::NoCurrentVerifiedLight,
        );
        match rejection {
            ReceiptBoundBodyCandidateError::Reference(cause) => {
                assert_eq!(
                    cause,
                    helve_world_chunk::InitialChunkReferenceError::NoCurrentVerifiedLight
                );
            }
            other => panic!("unexpected source error class: {other:?}"),
        }
    }

    #[test]
    fn absent_saved_entities_can_reside_but_cannot_generate_candidate() {
        let (dim, receipt) = imported_source_receipt(StoredBlockEntityEvidence::Absent);
        let mut scratch = vec![0xCC];
        assert!(matches!(
            append_receipt_bound_empty_chunk_body_candidate(
                &dim,
                &receipt,
                &SyntheticHeightFacts,
                66,
                16_384,
                &mut scratch
            ),
            Err(ReceiptBoundBodyCandidateError::Receipt(
                SourceChunkReceiptError::BlockEntities(EmptyBlockEntityEvidenceError::MissingList)
            ))
        ));
        assert_eq!(scratch, [0xCC]);
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
        assert!(bytes.ends_with(&[0, 2]));
        let lower_bytes = bytes.len();

        append_coherent_section_candidate(&image, 0, 66, &mut bytes)
            .expect("synthetic upper section");
        assert_eq!(&bytes[lower_bytes..], &[0, 0, 0, 0, 0, 0, 0, 0, 5]);
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
        assert_eq!(actual.len(), 2 + 9 + 9 + 1 + 1 + 2 * (1 + 2 + 2048));
    }

    #[test]
    fn one_borrow_produces_two_distinct_fragments_in_one_allocation() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut expected = vec![0x73, 0x25];
        append_coherent_chunk_data_fields_candidate(&image, 66, 16_384, &mut expected).unwrap();
        let split = expected.len();
        append_coherent_light_payload_candidate(&image, &mut expected).unwrap();

        let mut actual = Vec::with_capacity(16_384);
        actual.extend_from_slice(&[0x73, 0x25]);
        let allocation = actual.as_ptr();
        let spans =
            append_coherent_chunk_and_light_fragments(&image, 66, 16_384, &mut actual).unwrap();
        assert_eq!(actual, expected);
        assert_eq!(spans.chunk_data_fields, 2..split);
        assert_eq!(spans.light_fields, split..actual.len());
        assert!(!actual[spans.chunk_data_fields].is_empty());
        assert!(!actual[spans.light_fields].is_empty());
        assert_eq!(actual.as_ptr(), allocation);
        assert_eq!(image.stamp(), semantic.stamp());
    }

    #[test]
    fn rejected_chunk_does_not_leave_fragment_or_mutate_prefix() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut bytes = vec![0xAA, 0xBB, 0xCC];
        assert!(matches!(
            append_coherent_chunk_and_light_fragments(&image, 3, 16_384, &mut bytes),
            Err(ChunkAndLightCandidateError::ChunkData(
                ChunkDataCandidateError::Sections(SectionLengthError::Source(
                    SectionCandidateError::Biome(_)
                ))
            ))
        ));
        assert_eq!(bytes, &[0xAA, 0xBB, 0xCC]);
        assert!(matches!(
            append_coherent_chunk_and_light_fragments(&image, 66, 1, &mut bytes),
            Err(ChunkAndLightCandidateError::ChunkData(
                ChunkDataCandidateError::Sections(SectionLengthError::ExceedsLimit { .. })
            ))
        ));
        assert_eq!(bytes, &[0xAA, 0xBB, 0xCC]);
    }

    fn source_header(position: ChunkPos) -> StoredChunkHeader {
        StoredChunkHeader {
            position,
            data_version: TARGET_DATA_VERSION_26_2,
            stored_section_count: 2,
        }
    }

    #[test]
    fn explicitly_empty_body_matches_independently_built_fields() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut expected = vec![0xFA, 0xFB];
        let position = image.position();
        append_chunk_coordinates_candidate(&mut expected, position.x, position.z);
        let a = expected.len();
        append_coherent_chunk_data_fields_candidate(&image, 66, 16_384, &mut expected).unwrap();
        let b = expected.len();
        append_empty_block_entities_candidate(&mut expected);
        let c = expected.len();
        append_coherent_light_payload_candidate(&image, &mut expected).unwrap();

        let mut actual = Vec::with_capacity(16_384);
        actual.extend_from_slice(&[0xFA, 0xFB]);
        let allocation = actual.as_ptr();
        let spans = append_explicit_empty_chunk_body_candidate(
            &image,
            &source_header(position),
            StoredBlockEntityEvidence::ExplicitlyEmpty,
            66,
            16_384,
            &mut actual,
        )
        .unwrap();
        assert_eq!(actual, expected);
        assert_eq!(spans.position, 2..a);
        assert_eq!(spans.chunk_data, a..b);
        assert_eq!(spans.block_entities, b..c);
        assert_eq!(spans.light, c..actual.len());
        assert_eq!(&actual[spans.block_entities], &[0]);
        assert_eq!(actual.as_ptr(), allocation);
        assert_eq!(image.stamp(), semantic.stamp());
    }

    #[test]
    fn missing_nonempty_mismatched_or_wrong_version_evidence_never_writes() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut bytes = vec![0xCA, 0xFE];
        let good = source_header(image.position());
        for (evidence, expected) in [
            (
                StoredBlockEntityEvidence::Absent,
                EmptyBlockEntityEvidenceError::MissingList,
            ),
            (
                StoredBlockEntityEvidence::UnhandledEntries { count: 3 },
                EmptyBlockEntityEvidenceError::UnhandledEntries { count: 3 },
            ),
        ] {
            assert_eq!(
                append_explicit_empty_chunk_body_candidate(
                    &image, &good, evidence, 66, 16_384, &mut bytes,
                ),
                Err(EmptyChunkBodyCandidateError::BlockEntities(expected))
            );
        }
        let wrong_pos = source_header(ChunkPos { x: 33, z: -24 });
        assert_eq!(
            append_explicit_empty_chunk_body_candidate(
                &image,
                &wrong_pos,
                StoredBlockEntityEvidence::ExplicitlyEmpty,
                66,
                16_384,
                &mut bytes
            ),
            Err(EmptyChunkBodyCandidateError::PositionMismatch {
                source: wrong_pos.position,
                resident: image.position(),
            })
        );
        let wrong_version = StoredChunkHeader {
            data_version: 123,
            ..good
        };
        assert_eq!(
            append_explicit_empty_chunk_body_candidate(
                &image,
                &wrong_version,
                StoredBlockEntityEvidence::ExplicitlyEmpty,
                66,
                16_384,
                &mut bytes
            ),
            Err(EmptyChunkBodyCandidateError::DataVersionMismatch { source: 123 })
        );
        assert_eq!(bytes, [0xCA, 0xFE]);
    }

    #[test]
    fn late_section_failure_discards_coordinates_and_entity_profile() {
        let semantic = coherent_source();
        let image = InitialChunkReference::derive(&semantic, &SyntheticHeightFacts).unwrap();
        let mut bytes = vec![0xCE, 0xDD];
        assert!(matches!(
            append_explicit_empty_chunk_body_candidate(
                &image,
                &source_header(image.position()),
                StoredBlockEntityEvidence::ExplicitlyEmpty,
                3,
                16_384,
                &mut bytes
            ),
            Err(EmptyChunkBodyCandidateError::ChunkData(
                ChunkDataCandidateError::Sections(SectionLengthError::Source(
                    SectionCandidateError::Biome(_)
                ))
            ))
        ));
        assert_eq!(bytes, [0xCE, 0xDD]);
        assert!(matches!(
            append_explicit_empty_chunk_body_candidate(
                &image,
                &source_header(image.position()),
                StoredBlockEntityEvidence::ExplicitlyEmpty,
                66,
                1,
                &mut bytes
            ),
            Err(EmptyChunkBodyCandidateError::ChunkData(
                ChunkDataCandidateError::Sections(SectionLengthError::ExceedsLimit { .. })
            ))
        ));
        assert_eq!(bytes, [0xCE, 0xDD]);
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
