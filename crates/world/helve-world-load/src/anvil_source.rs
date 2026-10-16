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
