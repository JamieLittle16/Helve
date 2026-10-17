//! Explicit, source-unadmitted **COLD** Anvil import for the opted-in R2B
//! playtest. No target packet ID, new world owner, outbound queue, or Play
//! publication. The returned one-authority resident is retained by the
//! original connection service loop, not discarded after import.
//!
//! Reference sections are a correctness baseline for the *development demo*
//! only, not the M0.3D/issue #19 production section representation decision.

use std::path::Path;

use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
use helve_types::{DimensionId, DimensionTypeId};
use helve_world_contract::{BLOCK_SECTION_CELLS, BlockSection, SectionBlockPos};
use helve_world_import::RegionLimits;
use helve_world_import::{
    BiomeDecodeScratch, BlockSectionDecodeScratch, ChunkPayloadLimits, DeflateChunkPayloadDecoder,
    ExactBiomeDecoder, ImportedBiomeSectionBuilder, ImportedBlockSectionBuilder, NbtLimits,
    StoredBlockImporter, Target262BlockStateResolver,
};
use helve_world_load::{PregeneratedRegionLimits, SourceChunkPublicationReceipt};
use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};

use crate::r2b_server::R2bPlaySession;
use crate::r2c_chunk_batch::R2cChunkBatchState;
use crate::r2c_configured_biomes::with_candidate_biomes_from_context;
use crate::r2c_disk_first_view::{
    PendingTeleportDiskFirstViewRequest, import_pending_teleport_disk_first_view,
};
use helve_target_26_2::Target26_2R1xContext;

/// **Bounded, development-only** initial load: no world generator, no
/// cross-client cache. Separate source/profile/pack admission is required
/// before using these source receipts to send any chunk.
const CHUNKS: usize = 9;
const VIEW_DISTANCE: i32 = 10;
const MAX_REGION_BYTES: usize = 64 * 1024 * 1024;
const MAX_CHUNK_BYTES: usize = 16 * 1024 * 1024;

/// A transparent correctness baseline. This type deliberately does not claim
/// the future production HOT section layout or storage Pareto decision.
struct BlockBuilder;

impl ImportedBlockSectionBuilder<BlockStateId> for BlockBuilder {
    type Section = DirectBlockSection<BlockStateId>;

    fn build_uniform(&mut self, state: BlockStateId) -> Self::Section {
        DirectBlockSection::filled(state, &GeneratedStateFacts)
    }

    fn build_states(&mut self, states: &[BlockStateId]) -> Self::Section {
        debug_assert_eq!(states.len(), BLOCK_SECTION_CELLS);
        let mut section = DirectBlockSection::filled(AIR, &GeneratedStateFacts);
        for y in 0..16 {
            for z in 0..16 {
                for x in 0..16 {
                    let pos = SectionBlockPos::new(x, y, z)
                        .expect("bounded section-local cell coordinate");
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

    fn build_uniform(&mut self, id: u16) -> Self::Section {
        DirectBiomeSection::filled(id)
    }

    fn build_biomes(&mut self, ids: &[u16]) -> Self::Section {
        debug_assert_eq!(ids.len(), 64);
        let mut section = DirectBiomeSection::filled(ids[0]);
        section.fill_with(|x, y, z| ids[usize::from(x) + 4 * usize::from(z) + 16 * usize::from(y)]);
        section
    }
}

type ColdDimension = SemanticDimensionInstance<
    BlockStateId,
    DirectBlockSection<BlockStateId>,
    u16,
    DirectBiomeSection<u16>,
>;

/// This owns the ONLY imported dimension for this development connection and
/// its existing immutable source receipts. No publication bytes are produced.
#[allow(
    dead_code,
    reason = "R2C disk import is COLD non-publishing until source admission"
)]
pub(crate) struct ColdImportedView {
    dimension: ColdDimension,
    receipts: Vec<SourceChunkPublicationReceipt>,
    batch: R2cChunkBatchState,
}

impl ColdImportedView {
    pub(crate) fn chunks(&self) -> usize {
        self.dimension.resident_chunk_count()
    }

    pub(crate) fn receipts(&self) -> usize {
        self.receipts.len()
    }
}

/// Load the first finite world view into one retained semantic dimension.
/// Exact selected Configuration biome order is *candidate-only*. Unknown
/// source state/biome/light, missing region/section, nonempty block entities,
/// unsupported codec, wrong `DataVersion` or invalid source fail closed.
///
/// On a failed multi-region import, earlier regions can remain resident in
/// this temporary owner; the entire owner is dropped and **no Play packet**
/// is admitted. On success the caller retains the original source receipts
/// and ACK-state object for a later independently qualified publisher.
///
/// # Errors
///
/// Returns descriptive bounded COLD source/profile/data failures without
/// modifying the retained Play transport or permitting source promotion.
pub(crate) fn import_selected_cold_world(
    session: &R2bPlaySession,
    context: &Target26_2R1xContext,
    world: &Path,
) -> Result<ColdImportedView, String> {
    let profile = DimensionRuntimeProfile::new(DimensionTypeId(0), -64, 384, true)
        .map_err(|error| format!("selected overworld profile invalid: {error:?}"))?;
    let mut dimension = ColdDimension::new(DimensionId(0), profile);
    let mut receipts = Vec::with_capacity(CHUNKS);
    let resolver = Target262BlockStateResolver;
    let mut blocks = BlockBuilder;
    let mut block_scratch = BlockSectionDecodeScratch::new();
    let mut decompressor = DeflateChunkPayloadDecoder::try_with_output_limit(MAX_CHUNK_BYTES)
        .map_err(|error| format!("bounded source decoder unavailable: {error:?}"))?;
    let mut importer = StoredBlockImporter::new(
        ChunkPayloadLimits::new(MAX_CHUNK_BYTES, MAX_CHUNK_BYTES),
        NbtLimits::new(4096, 32768, 32768, 64)
            .map_err(|error| format!("invalid bounded NBT profile: {error:?}"))?,
        &mut decompressor,
        &resolver,
        &mut blocks,
        &mut block_scratch,
    );
    let mut biome_builder = BiomeBuilder;
    let mut biome_scratch = BiomeDecodeScratch::new();

    with_candidate_biomes_from_context(context, |registry| {
        let mut biomes = ExactBiomeDecoder::new(registry, &mut biome_builder, &mut biome_scratch);
        import_pending_teleport_disk_first_view(
            session,
            PendingTeleportDiskFirstViewRequest {
                world,
                profile,
                view_distance: VIEW_DISTANCE,
                max_chunks: CHUNKS,
                limits: PregeneratedRegionLimits {
                    region: RegionLimits::new(MAX_REGION_BYTES, MAX_CHUNK_BYTES),
                    max_external_bytes: MAX_CHUNK_BYTES,
                },
            },
            &mut dimension,
            &mut importer,
            &mut biomes,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        )
        .map(|(_center, batch)| batch)
        .map_err(|error| format!("source Anvil import rejected: {error:?}"))
    })
    .map_err(|error| format!("selected Configuration biomes rejected: {error:?}"))?
    .map(|batch| ColdImportedView {
        dimension,
        receipts,
        batch,
    })
}
