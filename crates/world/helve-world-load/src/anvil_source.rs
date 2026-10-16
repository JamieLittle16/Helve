//! One-pass COLD import and authoritative admission of source-backed 26.2
//! Anvil chunk data, biomes and persisted light.
//!
//! The actual region framing, decompressor, NBT decoder and palette
//! resolvers belong to helve-world-import. This module only links their
//! successful output to the *existing* semantic resident dimension,
//! returning the original source-backed publication receipt.
//! No second chunk, copy of the decoded sections, second directory or
//! target-dependent state is introduced.
//!
//! This narrow first-visibility candidate requires an explicitly empty
//! persisted block-entity list. A chunk with nonempty or absent list is
//! not silently republished as though it contained no block entities.

use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_import::{
    BlockStateResolver, ChunkPayloadDecoder, EmptyBlockEntityEvidenceError, ExternalChunkPayload,
    ImportedBlockSectionBuilder, RegionView, SectionBiomeDecoder, StoredBlockImporter,
    StoredChunkImportError,
};
use helve_world_runtime::SemanticDimensionInstance;

use crate::{
    SourceChunkPublicationReceipt, StoredBiomeResidencyError,
    install_source_biome_chunk_with_receipt,
};

/// An Anvil chunk failed before it could produce one source-backed
/// authoritative resident incarnation with an explicitly empty entity list.
#[derive(Debug)]
pub enum AnvilSourceAdmissionError<E> {
    /// Source region/decompression/NBT/palette input failed before installation.
    Decode(StoredChunkImportError<E>),
    /// This first-visibility profile cannot silently omit block entities.
    BlockEntities(EmptyBlockEntityEvidenceError),
    /// Exact biome lattice, initial light or resident admission failed.
    Install(StoredBiomeResidencyError),
}

/// One caller-selected chunk in an already bounded and validated Anvil
/// region, with optional separately bounded external `.mcc` payload.
/// Region backing remains caller-owned and borrowed for this transaction.
#[derive(Clone, Copy, Debug)]
pub struct SelectedAnvilSource<'a, 'r> {
    /// Borrow of the validated region header and inline compressed bytes.
    pub region: &'a RegionView<'r>,
    /// Local chunk X within this 32×32 region.
    pub local_x: u8,
    /// Local chunk Z within this 32×32 region.
    pub local_z: u8,
    /// External record payload, if the region record requires one.
    pub external_payload: Option<ExternalChunkPayload<'a>>,
}

/// Move one real region chunk into the authoritative semantic resident
/// directory and mint its exact source publication receipt.
///
/// All supplied inputs are already caller-owned COLD mechanisms; the
/// selected biome decoder can, for example, use the exact ordered keys
/// borrowed from the sent Configuration image. The complete source is
/// parsed **once**, and the decoded block/biome/light vectors are moved
/// straight into the existing source receipt installer.
///
/// On any decode or unsupported-entity failure the resident world is
/// unchanged. Once installation begins, the resident importer's
/// transactional admission performs its own fail-closed checks.
/// A source receipt does **not** authorize unadmitted client numeric
/// biome IDs, final packet law, or production publication.
///
/// # Errors
///
/// Rejects all source decoding, empty-list qualification and semantic
/// admission failures without returning a publication receipt.
pub fn import_and_install_anvil_source<R, SB, D, BD, Biome, MakeEmpty>(
    dimension: &mut SemanticDimensionInstance<R::State, SB::Section, Biome, BD::Section>,
    importer: &mut StoredBlockImporter<'_, R, SB, D>,
    source: SelectedAnvilSource<'_, '_>,
    biome_decoder: &mut BD,
    make_empty_section: MakeEmpty,
) -> Result<SourceChunkPublicationReceipt, AnvilSourceAdmissionError<D::Error>>
where
    R: BlockStateResolver,
    SB: ImportedBlockSectionBuilder<R::State>,
    SB::Section: BlockSection<R::State>,
    D: ChunkPayloadDecoder,
    BD: SectionBiomeDecoder,
    Biome: Copy + Eq,
    BD::Section: BiomeSection<Biome>,
    MakeEmpty: FnMut() -> SB::Section,
{
    let imported = importer
        .import_region_chunk_with_biomes(
            source.region,
            source.local_x,
            source.local_z,
            source.external_payload,
            biome_decoder,
        )
        .map_err(AnvilSourceAdmissionError::Decode)?;
    imported
        .block_entities
        .require_explicitly_empty()
        .map_err(AnvilSourceAdmissionError::BlockEntities)?;
    install_source_biome_chunk_with_receipt(dimension, imported, make_empty_section)
        .map_err(AnvilSourceAdmissionError::Install)
}

#[cfg(test)]
mod tests {
    use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
    use helve_types::{ChunkPos, DimensionId, DimensionTypeId};
    use helve_world_contract::{BLOCK_SECTION_CELLS, BlockSection, SectionBlockPos};
    use helve_world_import::{
        BiomeDecodeScratch, BlockSectionDecodeScratch, ChunkPayloadLimits,
        ExactBiomeDecoder, ImportedBiomeSectionBuilder, ImportedBlockSectionBuilder, NbtLimits,
        OrderedBiomeRegistry,
        RegionLimits, RegionView, Target262BlockStateResolver, TagType,
        UncompressedChunkPayloadDecoder,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};

    use super::{
        AnvilSourceAdmissionError, SelectedAnvilSource, import_and_install_anvil_source,
    };

    const REGION_HEADER: usize = 8192;
    const SECTOR: usize = 4096;
    const STONE: &str = "minecraft:stone";

    struct BlockBuilder;

    impl ImportedBlockSectionBuilder<BlockStateId> for BlockBuilder {
        type Section = DirectBlockSection<BlockStateId>;

        fn build_uniform(&mut self, state: BlockStateId) -> Self::Section {
            DirectBlockSection::filled(state, &GeneratedStateFacts)
        }

        fn build_states(&mut self, states: &[BlockStateId]) -> Self::Section {
            assert_eq!(states.len(), BLOCK_SECTION_CELLS);
            let mut section = DirectBlockSection::filled(AIR, &GeneratedStateFacts);
            for y in 0..16 {
                for z in 0..16 {
                    for x in 0..16 {
                        let pos = SectionBlockPos::new(x, y, z).unwrap();
                        section.replace(pos, states[pos.index()], &GeneratedStateFacts);
                    }
                }
            }
            section
        }
    }

    struct BiomeBuilder;

    impl ImportedBiomeSectionBuilder<u16> for BiomeBuilder {
        type Section = DirectBiomeSection<u16>;

        fn build_uniform(&mut self, biome: u16) -> Self::Section {
            DirectBiomeSection::filled(biome)
        }

        fn build_biomes(&mut self, cells: &[u16]) -> Self::Section {
            assert_eq!(cells.len(), 64);
            let mut section = DirectBiomeSection::filled(cells[0]);
            section.fill_with(|x, y, z| {
                cells[usize::from(x) + 4 * usize::from(z) + 16 * usize::from(y)]
            });
            section
        }
    }

    fn name(out: &mut Vec<u8>, value: &str) {
        out.extend_from_slice(&u16::try_from(value.len()).unwrap().to_be_bytes());
        out.extend_from_slice(value.as_bytes());
    }

    fn field(out: &mut Vec<u8>, kind: TagType, label: &str) {
        out.push(kind as u8);
        name(out, label);
    }

    fn int_field(out: &mut Vec<u8>, label: &str, value: i32) {
        field(out, TagType::Int, label);
        out.extend_from_slice(&value.to_be_bytes());
    }

    // Source-schema NBT bytes, NOT a captured Anvil save or a production
    // qualification fixture. The importer, residency and receipt are real.
    fn source_nbt(data_version: i32, explicit_entities: bool) -> Vec<u8> {
        let mut out = vec![TagType::Compound as u8, 0, 0];
        int_field(&mut out, "DataVersion", data_version);
        int_field(&mut out, "xPos", 0);
        int_field(&mut out, "zPos", 0);
        field(&mut out, TagType::Byte, "isLightOn");
        out.push(1);

        if explicit_entities {
            field(&mut out, TagType::List, "block_entities");
            out.push(TagType::Compound as u8);
            out.extend_from_slice(&0_i32.to_be_bytes());
        }

        field(&mut out, TagType::List, "sections");
        out.push(TagType::Compound as u8);
        out.extend_from_slice(&1_i32.to_be_bytes());
        field(&mut out, TagType::Byte, "Y");
        out.push(0);

        field(&mut out, TagType::Compound, "block_states");
        field(&mut out, TagType::List, "palette");
        out.push(TagType::Compound as u8);
        out.extend_from_slice(&1_i32.to_be_bytes());
        field(&mut out, TagType::String, "Name");
        name(&mut out, STONE);
        out.push(TagType::End as u8); // block palette entry
        out.push(TagType::End as u8); // block_states

        field(&mut out, TagType::Compound, "biomes");
        field(&mut out, TagType::List, "palette");
        out.push(TagType::String as u8);
        out.extend_from_slice(&1_i32.to_be_bytes());
        name(&mut out, "minecraft:plains");
        out.push(TagType::End as u8); // biomes
        out.push(TagType::End as u8); // section
        out.push(TagType::End as u8); // root
        out
    }

    fn region_bytes(payload: &[u8]) -> Vec<u8> {
        let sector_count = (payload.len() + 5).div_ceil(SECTOR);
        let mut region = vec![0_u8; REGION_HEADER + sector_count * SECTOR];
        let location = (2_u32 << 8) | u32::try_from(sector_count).unwrap();
        region[..4].copy_from_slice(&location.to_be_bytes());
        region[SECTOR..SECTOR + 4].copy_from_slice(&17_u32.to_be_bytes());
        region[REGION_HEADER..REGION_HEADER + 4]
            .copy_from_slice(&u32::try_from(payload.len() + 1).unwrap().to_be_bytes());
        region[REGION_HEADER + 4] = 3; // actual Anvil uncompressed record
        region[REGION_HEADER + 5..REGION_HEADER + 5 + payload.len()].copy_from_slice(payload);
        region
    }

    type Blocks = DirectBlockSection<BlockStateId>;
    type Biomes = DirectBiomeSection<u16>;
    type Dimension = SemanticDimensionInstance<BlockStateId, Blocks, u16, Biomes>;

    fn dim() -> Dimension {
        let profile = DimensionRuntimeProfile::new(DimensionTypeId(1), 0, 16, true).unwrap();
        Dimension::new(DimensionId(2), profile)
    }

    fn run_import(
        dimension: &mut Dimension,
        bytes: &[u8],
    ) -> Result<crate::SourceChunkPublicationReceipt, AnvilSourceAdmissionError<helve_world_import::UncompressedPayloadError>> {
        let region = RegionView::new(
            bytes, 0, 0, RegionLimits::new(64 * SECTOR, 32 * SECTOR),
        )
        .unwrap();
        let resolver = Target262BlockStateResolver;
        let mut blocks = BlockBuilder;
        let mut block_scratch = BlockSectionDecodeScratch::new();
        let mut decompress = UncompressedChunkPayloadDecoder;
        let mut importer = helve_world_import::StoredBlockImporter::new(
            ChunkPayloadLimits::new(32 * SECTOR, 32 * SECTOR),
            NbtLimits::new(512, 4096, 4096, 32).unwrap(),
            &mut decompress,
            &resolver,
            &mut blocks,
            &mut block_scratch,
        );
        let registry = OrderedBiomeRegistry::new(
            4903, &["minecraft:plains"],
        )
        .unwrap();
        let mut biome_builder = BiomeBuilder;
        let mut biome_scratch = BiomeDecodeScratch::new();
        let mut decoder =
            ExactBiomeDecoder::new(&registry, &mut biome_builder, &mut biome_scratch);
        import_and_install_anvil_source(
            dimension,
            &mut importer,
            SelectedAnvilSource {
                region: &region,
                local_x: 0,
                local_z: 0,
                external_payload: None,
            },
            &mut decoder,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        )
    }

    #[test]
    fn real_anvil_record_to_pristine_resident_receipt_without_second_world() {
        let bytes = region_bytes(&source_nbt(4903, true));
        let mut dimension = dim();
        let receipt = run_import(&mut dimension, &bytes)
            .expect("complete NBT schema must admit one source chunk");
        assert_eq!(dimension.resident_chunk_count(), 1);
        assert_eq!(receipt.installed().handle.position, ChunkPos { x: 0, z: 0 });
        assert_eq!(receipt.installed().source.region_timestamp, 17);
        let (chunk, source) = receipt.resolve_explicitly_empty(&dimension)
            .expect("untouched imported source still authorizes a receipt");
        assert_eq!(source.position, ChunkPos { x: 0, z: 0 });
        assert_eq!(source.data_version, 4903);
        assert_eq!(chunk.revision().0, 0);
        assert!(dimension.discover_chunk(ChunkPos { x: 0, z: 0 }).is_some());
    }

    #[test]
    fn missing_entity_evidence_rejects_before_resident_install() {
        let bytes = region_bytes(&source_nbt(4903, false));
        let mut dimension = dim();
        assert!(matches!(
            run_import(&mut dimension, &bytes),
            Err(AnvilSourceAdmissionError::BlockEntities(
                helve_world_import::EmptyBlockEntityEvidenceError::MissingList
            ))
        ));
        assert_eq!(dimension.resident_chunk_count(), 0);
    }

    #[test]
    fn wrong_source_version_and_duplicate_incarnation_do_not_mutate_residency() {
        let mut dimension = dim();
        let wrong = region_bytes(&source_nbt(4902, true));
        assert!(matches!(
            run_import(&mut dimension, &wrong),
            Err(AnvilSourceAdmissionError::Decode(_))
        ));
        assert_eq!(dimension.resident_chunk_count(), 0);

        let valid = region_bytes(&source_nbt(4903, true));
        let receipt = run_import(&mut dimension, &valid).unwrap();
        assert!(matches!(
            run_import(&mut dimension, &valid),
            Err(AnvilSourceAdmissionError::Install(_))
        ));
        assert_eq!(dimension.resident_chunk_count(), 1);
        assert!(receipt.resolve_explicitly_empty(&dimension).is_ok());
    }
}
