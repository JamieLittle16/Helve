//! Explicit, source-unadmitted **COLD** Anvil import for the R2C development
//! boundary. The ordinary executable creates one server-lifetime resident
//! dimension and immutable source receipts before accepting clients, while
//! the stock-client diagnostic retains its separate test-only import path.
//! Sessions own cursors, not chunks. No second queue or Play publication.
//!
//! Reference sections are a correctness baseline for the *development demo*
//! only, not the M0.3D/issue #19 production section representation decision.

use std::path::Path;
use std::sync::Arc;

use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
use helve_types::{ChunkPos, DimensionId, DimensionTypeId};
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
use helve_connection_core::ConnectionBufferError;
use helve_connection_driver::DriverError;
use helve_target_26_2::r2c_play_wire::append_chunk_with_light_packet_id;

use crate::r2c_chunk_batch::{ChunkBatchStep, R2cBatchTickClock, R2cChunkBatchState};
use crate::r2c_configured_biomes::with_candidate_biomes_from_context;
use crate::r2c_disk_first_view::{
    DiskFirstViewRequest, import_disk_first_view, plan_explicit_teleport_first_view,
    plan_pending_teleport_first_view,
};
use crate::r2c_heightmap_facts::CandidateHeightmapFacts;
use crate::r2c_play_inbound::{
    R2cPlayInboundError, R2cPlayInboundStep, process_one_r2c_play_inbound,
};
use crate::r2c_section_candidate::{
    ReceiptBoundBodyCandidateError, append_receipt_bound_empty_chunk_body_candidate,
};
use helve_target_26_2::Target26_2R1xContext;

/// **Bounded, development-only** initial load: no world generator, no
/// cross-client cache. Separate source/profile/pack admission is required
/// before using these source receipts to send any chunk.
const CHUNKS: usize = 9;
#[cfg(test)]
const RENDER_HALO_CHUNKS: usize = 25;
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

pub(crate) type ColdDimension = SemanticDimensionInstance<
    BlockStateId,
    DirectBlockSection<BlockStateId>,
    u16,
    DirectBiomeSection<u16>,
>;

/// The server owns one immutable initial resident dimension and source-receipt
/// selection across independent client lifetimes. This is a COLD, pre-R2D
/// bridge: the future active mutation authority is not an Arc or socket.
/// The selected world is not independently source-admitted for publication.
pub struct R2cColdWorldHost {
    dimension: Arc<ColdDimension>,
    receipts: Arc<[SourceChunkPublicationReceipt]>,
    center: ChunkPos,
    profile: DimensionRuntimeProfile,
    max_chunks: usize,
}

impl std::fmt::Debug for R2cColdWorldHost {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("R2cColdWorldHost")
            .field("center", &self.center)
            .field("resident_chunks", &self.chunks())
            .field("source_receipts", &self.receipts.len())
            .finish_non_exhaustive()
    }
}

impl R2cColdWorldHost {
    /// Test-only bridge from the real multi-region Anvil fixture. This shares
    /// existing semantic residents and source receipts, never fabricates a
    /// source-admission witness or makes the ordinary publisher constructible.
    #[cfg(test)]
    pub(crate) fn from_test_source(
        dimension: ColdDimension,
        receipts: Vec<SourceChunkPublicationReceipt>,
        center: ChunkPos,
        profile: DimensionRuntimeProfile,
        max_chunks: usize,
    ) -> Self {
        Self {
            dimension: Arc::new(dimension),
            receipts: receipts.into(),
            center,
            profile,
            max_chunks,
        }
    }

    /// Validate that a new session's actual pending teleport selects exactly
    /// the original server-owned source window before attaching its own cursor.
    /// No world data, receipt, or chunk memory is copied.
    pub(crate) fn attach(&self, session: &R2bPlaySession) -> Result<ColdImportedView, String> {
        let (center, selected) =
            plan_pending_teleport_first_view(session, self.profile, VIEW_DISTANCE, self.max_chunks)
                .map_err(|error| format!("session teleport differs from hosted view: {error:?}"))?;
        if center != self.center || selected.len() != self.receipts.len() {
            return Err("session first view differs from server-owned source selection".to_owned());
        }
        Ok(ColdImportedView {
            dimension: Arc::clone(&self.dimension),
            receipts: Arc::clone(&self.receipts),
            batch: R2cChunkBatchState::new_with_initial_cache_center(self.receipts.len(), center),
        })
    }

    pub(crate) fn chunks(&self) -> usize {
        self.dimension.resident_chunk_count()
    }

    pub(crate) fn receipts(&self) -> usize {
        self.receipts.len()
    }

    /// Do one server-lifetime candidate preflight, not a full re-encode at
    /// every join. Publication remains disabled until independent VAR/SEM.
    pub(crate) fn audit_candidate_bodies(
        &self,
        heightmap_candidate: &[u8],
    ) -> Result<ColdCandidateAudit, String> {
        audit_receipt_bound_candidate_bodies(
            &self.dimension,
            &self.receipts,
            heightmap_candidate,
            66,
        )
    }
}

/// Only the chunk-batch cursor and ACK/rate state belong to the connection.
/// The resident dimension and exact source receipts belong to the server.
#[allow(
    dead_code,
    reason = "R2C disk import is COLD non-publishing until source admission"
)]
pub(crate) struct ColdImportedView {
    dimension: Arc<ColdDimension>,
    receipts: Arc<[SourceChunkPublicationReceipt]>,
    batch: R2cChunkBatchState,
}

impl ColdImportedView {
    /// Reuse a fully imported test fixture to validate the final retained
    /// scheduler without introducing a second product-world constructor.
    #[cfg(test)]
    pub(crate) fn from_test_source(
        dimension: ColdDimension,
        receipts: Vec<SourceChunkPublicationReceipt>,
        batch: R2cChunkBatchState,
    ) -> Self {
        Self {
            dimension: Arc::new(dimension),
            receipts: receipts.into(),
            batch,
        }
    }

    /// Test-only identity probe: a second join reuses exactly the same
    /// resident directory and receipt storage, not an identical re-import.
    #[cfg(test)]
    pub(crate) fn shares_resident_with(&self, other: &Self) -> bool {
        Arc::ptr_eq(&self.dimension, &other.dimension)
            && Arc::ptr_eq(&self.receipts, &other.receipts)
    }

    pub(crate) fn chunks(&self) -> usize {
        self.dimension.resident_chunk_count()
    }

    pub(crate) fn receipts(&self) -> usize {
        self.receipts.len()
    }

    /// The ignored local stock-client test can inspect the existing batch
    /// state after the TCP peer closes. No counters are added to the
    /// production connection driver or ordinary R2C HOT path.
    #[cfg(test)]
    pub(crate) fn diagnostic_batch_progress(&self) -> (usize, usize, u8) {
        (
            self.batch.next_chunk_index(),
            self.receipts.len(),
            self.batch.unacknowledged_batches(),
        )
    }

    /// Reuse R2B control and already implemented R2C batch-ACK parsing on
    /// the *original* Play ingress owner. This is safe before admission:
    /// without any published finished batch, an unsolicited ACK fails
    /// transactionally and cannot advance the source publication cursor.
    ///
    /// # Errors
    /// Preserves typed R2B/ACK errors and never constructs a second queue.
    pub(crate) fn process_one_play_inbound(
        &mut self,
        session: &mut R2bPlaySession,
        now_ms: u64,
    ) -> Result<R2cPlayInboundStep, R2cPlayInboundError> {
        process_one_r2c_play_inbound(session, &mut self.batch, now_ms)
    }
}

/// Strict pre-publication projection audit, with no driver or socket access.
///
/// The first-view receipt ordering, world and ACK controller remain owned by
/// the original COLD import; this is an *inspection*, not a second packet
/// owner or independent state source. All byte counts describe disposable
/// scratch, never bytes queued for Play.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct ColdCandidateAudit {
    pub(crate) chunks: usize,
    pub(crate) total_body_bytes: usize,
    pub(crate) maximum_body_bytes: usize,
}

/// Re-use the actual source-receipt-bound 26.2 projector over all imported
/// chunks, with a single cleared COLD buffer. Never append to the R2B driver.
///
/// A successful audit establishes that source receipts can be converted to
/// candidate chunk bodies for this saved world and candidate heightmap table.
/// It is **not** an admission of biome IDs, motion/leaves predicates or Play
/// packet semantics. Errors are fail-closed; no partial packet escapes.
///
/// # Errors
/// Rejects unsupported table bits/length/ID consistency, stale/invalid
/// receipts, absent block-entity evidence, packet overflow and accounting
/// inconsistencies without modifying world or transport.
pub(crate) fn audit_receipt_bound_candidate_bodies(
    dimension: &ColdDimension,
    receipts: &[SourceChunkPublicationReceipt],
    heightmap_candidate: &[u8],
    registry_count: usize,
) -> Result<ColdCandidateAudit, String> {
    const MAX_PACKET_BODY: usize = 65_535;
    if receipts.is_empty() || receipts.len() != dimension.resident_chunk_count() {
        return Err("COLD projection requires one source receipt per selected resident".to_owned());
    }
    let facts = CandidateHeightmapFacts::from_oracle_bytes(heightmap_candidate)
        .map_err(|error| format!("heightmap table rejected: {error:?}"))?;
    if registry_count != 66 {
        return Err(format!(
            "COLD client registry candidate has {registry_count} biomes, not 66"
        ));
    }

    // Bounded one-owner COLD scratch. No packet list, no cloned chunks and
    // no insertion into the continuing connection's outbound buffer.
    let mut scratch = Vec::with_capacity(MAX_PACKET_BODY);
    let mut total_body_bytes = 0_usize;
    let mut maximum_body_bytes = 0_usize;
    for receipt in receipts {
        scratch.clear();
        append_receipt_bound_empty_chunk_body_candidate(
            dimension,
            receipt,
            &facts,
            registry_count,
            MAX_PACKET_BODY,
            &mut scratch,
        )
        .map_err(|error| format!("source receipt chunk candidate rejected: {error:?}"))?;
        if scratch.is_empty() || scratch.len() > MAX_PACKET_BODY {
            return Err(format!(
                "COLD candidate body length {} outside 1..={MAX_PACKET_BODY}",
                scratch.len()
            ));
        }
        total_body_bytes = total_body_bytes
            .checked_add(scratch.len())
            .ok_or_else(|| "COLD candidate body accounting overflow".to_owned())?;
        maximum_body_bytes = maximum_body_bytes.max(scratch.len());
    }
    Ok(ColdCandidateAudit {
        chunks: receipts.len(),
        total_body_bytes,
        maximum_body_bytes,
    })
}

impl ColdImportedView {
    /// Immutable, non-publishing candidate check of the same retained world.
    ///
    /// # Errors
    /// Rejects an invalid source, candidate table, stale receipt or body.
    pub(crate) fn audit_candidate_bodies(
        &self,
        heightmap_candidate: &[u8],
    ) -> Result<ColdCandidateAudit, String> {
        if self.batch.next_chunk_index() != 0 || self.batch.unacknowledged_batches() != 0 {
            return Err("COLD audit cannot advance an already published batch".to_owned());
        }
        audit_receipt_bound_candidate_bodies(
            &self.dimension,
            &self.receipts,
            heightmap_candidate,
            66,
        )
    }
}

/// Only an independently source-admitted biome-ID, heightmap, outer-wire
/// and Play lifecycle bundle may authorize queueing chunk packets.
///
/// In normal builds this enum is *uninhabited*. There is no construction
/// path, runtime flag, CLI switch or environment-variable override. Tests
/// can instantiate their own witness to exercise the already implemented
/// driver and source-receipt projection, but cannot promote that candidate
/// evidence to a production source admission.
#[cfg(not(test))]
pub(crate) enum R2cSourceAdmission {}

/// Test-only capability for checking publication composition; never
/// compiled as a constructible value into the product server.
#[cfg(test)]
pub(crate) struct R2cSourceAdmission;

/// Compose the already implemented receipt-bound chunk encoder with the
/// ACK/quota-aware publisher on the **same** continuing R2B Play driver.
///
/// This function does not construct a new world, packet list, buffer owner,
/// network dispatcher or registry. It consumes an opaque source-admission
/// witness, which has no values in production until the independent
/// Minecraft 26.2 VAR/SEM and complete client registry law are admitted.
/// Each chunk resolves a fresh source receipt before its bytes can be queued.
///
/// # Errors
/// Returns the existing transactional driver's source/egress error. A
/// rejected chunk does not advance the batch cursor or append a frame.
#[cfg_attr(
    not(test),
    allow(
        dead_code,
        reason = "uninhabited R2C source admission forbids live chunk publication"
    )
)]
pub(crate) fn service_one_source_admitted_chunk(
    session: &mut R2bPlaySession,
    dimension: &ColdDimension,
    receipts: &[SourceChunkPublicationReceipt],
    batch: &mut R2cChunkBatchState,
    facts: &CandidateHeightmapFacts<'_>,
    scratch: &mut Vec<u8>,
    _admission: &R2cSourceAdmission,
) -> Result<ChunkBatchStep, DriverError<ReceiptBoundBodyCandidateError>> {
    session.service_r2c_chunk_batch_one(batch, scratch, |index, output| {
        let receipt =
            receipts
                .get(index)
                .ok_or(ReceiptBoundBodyCandidateError::MissingReceipt {
                    index,
                    available: receipts.len(),
                })?;
        append_chunk_with_light_packet_id(output);
        append_receipt_bound_empty_chunk_body_candidate(
            dimension, receipt, facts, 66, 65_535, output,
        )
        .map(|_| ())
    })
}

/// A source-gated, allocation-bounded publication opportunity in the
/// retained R2B Play service. The only per-connection outbound storage is the
/// original driver plus one reused COLD scratch buffer. No packet vector,
/// duplicate resident data or independent scheduler is introduced.
///
/// **Production has no constructible admission witness.** Merely compiling
/// this ready-to-connect service does not make candidate chunks publishable.
#[cfg_attr(
    not(test),
    allow(
        dead_code,
        reason = "R2C client/wire VAR/SEM admission remains pending"
    )
)]
pub(crate) struct SourceAdmittedPlayPublisher<'a> {
    admission: &'a R2cSourceAdmission,
    facts: CandidateHeightmapFacts<'a>,
    scratch: Vec<u8>,
    clock: R2cBatchTickClock,
}

#[cfg_attr(
    not(test),
    allow(
        dead_code,
        reason = "R2C client/wire VAR/SEM admission remains pending"
    )
)]
impl<'a> SourceAdmittedPlayPublisher<'a> {
    const MAX_ACTIONS_PER_TICK: usize = 32;
    const MAX_BODY_BYTES: usize = 65_535;

    /// Validate the exact source-selected facts once and widen the **same**
    /// driver to the already bounded legal Play frame limits. Requires the
    /// separate uninhabited-in-production source admission capability.
    ///
    /// # Errors
    /// A bad table, allocation failure or driver limit rejection aborts
    /// activation before the first chunk publication.
    pub(crate) fn new(
        session: &mut R2bPlaySession,
        facts_bytes: &'a [u8],
        start_ms: u64,
        admission: &'a R2cSourceAdmission,
    ) -> Result<Self, String> {
        let facts = CandidateHeightmapFacts::from_official_oracle_bytes(facts_bytes)
            .map_err(|error| format!("R2C source facts rejected: {error:?}"))?;
        let mut scratch = Vec::new();
        scratch
            .try_reserve_exact(Self::MAX_BODY_BYTES)
            .map_err(|error| format!("R2C bounded projection scratch rejected: {error:?}"))?;
        session
            .widen_play_limits_for_chunks()
            .map_err(|error| format!("R2C retained Play limits rejected: {error:?}"))?;
        Ok(Self {
            admission,
            facts,
            scratch,
            clock: R2cBatchTickClock::new(start_ms),
        })
    }

    /// Never sleep beyond the next R2C send tick or the earlier liveness
    /// deadline. The caller performs one bounded Play ingress/control pass
    /// before calling this method, and continues using the original socket.
    pub(crate) fn next_wake_deadline_ms(
        &self,
        world: &ColdImportedView,
        liveness_deadline_ms: u64,
    ) -> u64 {
        if world.batch.needs_send_service() {
            self.clock.next_wake_deadline_ms(liveness_deadline_ms)
        } else {
            liveness_deadline_ms
        }
    }

    /// Issue at most 32 *individual* transactional publication admissions
    /// per service opportunity. The internal 20-Hz clock replenishes quota
    /// once, skipping any expired periods after delayed socket wake-up.
    /// This services an in-progress batch without inventing new quota; ACK
    /// state remains in `world.batch` and source receipts in `world.receipts`.
    ///
    /// # Errors
    /// The existing source receipt or egress error is propagated; neither
    /// cursor progress nor packet bytes are committed on rejection.
    pub(crate) fn service(
        &mut self,
        session: &mut R2bPlaySession,
        world: &mut ColdImportedView,
        now_ms: u64,
    ) -> Result<usize, DriverError<ReceiptBoundBodyCandidateError>> {
        self.clock.poll_tick(now_ms, &mut world.batch);
        let mut queued = 0_usize;
        for _ in 0..Self::MAX_ACTIONS_PER_TICK {
            let step = match service_one_source_admitted_chunk(
                session,
                &world.dimension,
                &world.receipts,
                &mut world.batch,
                &self.facts,
                &mut self.scratch,
                self.admission,
            ) {
                Ok(step) => step,
                // Expected bounded egress congestion is NOT a source error:
                // the driver and cursor are transactional, so stop sending
                // until the original socket drains its pending output.
                Err(DriverError::Buffer(ConnectionBufferError::EgressLimitExceeded { .. })) => {
                    break;
                }
                Err(error) => return Err(error),
            };
            match step {
                ChunkBatchStep::CacheCenterQueued { .. }
                | ChunkBatchStep::Started { .. }
                | ChunkBatchStep::ChunkQueued { .. }
                | ChunkBatchStep::Finished { .. } => queued += 1,
                ChunkBatchStep::Complete
                | ChunkBatchStep::WaitingForTick
                | ChunkBatchStep::WaitingForAcknowledgement => break,
            }
        }
        Ok(queued)
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
    import_selected_cold_world_bounded(session, context, world, CHUNKS)
}

/// COLD-only additional authentic neighbor chunks for the first renderer
/// experiment. Never exposes a source-admission witness in product builds.
#[cfg(test)]
pub(crate) fn import_selected_cold_world_with_render_halo(
    session: &R2bPlaySession,
    context: &Target26_2R1xContext,
    world: &Path,
) -> Result<ColdImportedView, String> {
    import_selected_cold_world_bounded(session, context, world, RENDER_HALO_CHUNKS)
}

fn selected_overworld_profile() -> Result<DimensionRuntimeProfile, String> {
    DimensionRuntimeProfile::new(DimensionTypeId(0), -64, 384, true)
        .map_err(|error| format!("selected overworld profile invalid: {error:?}"))
}

/// Prepare one source-backed immutable resident dimension before accepting
/// clients. Position selection uses the exact same checked teleport planner
/// as the retained R2B session. No packet is sent or admission granted.
pub(crate) fn import_selected_cold_world_host(
    context: &Target26_2R1xContext,
    world: &Path,
    teleport: (f64, f64, f64),
) -> Result<R2cColdWorldHost, String> {
    let profile = selected_overworld_profile()?;
    let (center, requested) = plan_explicit_teleport_first_view(
        teleport.0,
        teleport.1,
        teleport.2,
        profile,
        VIEW_DISTANCE,
        CHUNKS,
    )
    .map_err(|error| format!("bootstrap teleport rejects hosted world: {error:?}"))?;
    let view = import_selected_cold_world_positions(context, world, profile, center, requested)?;
    Ok(R2cColdWorldHost {
        dimension: view.dimension,
        receipts: view.receipts,
        center,
        profile,
        max_chunks: CHUNKS,
    })
}

fn import_selected_cold_world_bounded(
    session: &R2bPlaySession,
    context: &Target26_2R1xContext,
    world: &Path,
    max_chunks: usize,
) -> Result<ColdImportedView, String> {
    let profile = selected_overworld_profile()?;
    let (center, requested) =
        plan_pending_teleport_first_view(session, profile, VIEW_DISTANCE, max_chunks)
            .map_err(|error| format!("selected pending teleport rejected: {error:?}"))?;
    import_selected_cold_world_positions(context, world, profile, center, requested)
}

fn import_selected_cold_world_positions(
    context: &Target26_2R1xContext,
    world: &Path,
    profile: DimensionRuntimeProfile,
    center: ChunkPos,
    mut requested: Vec<ChunkPos>,
) -> Result<ColdImportedView, String> {
    let mut dimension = ColdDimension::new(DimensionId(0), profile);
    let mut receipts = Vec::with_capacity(requested.len());
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
        import_disk_first_view(
            DiskFirstViewRequest {
                world,
                requested: &mut requested,
                center,
                view_distance: VIEW_DISTANCE,
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
        .map_err(|error| format!("source Anvil import rejected: {error:?}"))
    })
    .map_err(|error| format!("selected Configuration biomes rejected: {error:?}"))?
    .map(|batch| ColdImportedView {
        dimension: Arc::new(dimension),
        receipts: receipts.into(),
        batch,
    })
}
