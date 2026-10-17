//! COLD multi-region first-view composition, deliberately unconnected
//! to the live R2B Play transport until client-visible VAR/SEM admission.
//!
//! The caller owns one finite requested-position vector, one source-receipt
//! vector and one semantic dimension. We hand selected positions to the existing world-load region grouper,
//! which reads each region only once,
//! import each selected slot directly into the sole resident owner, then
//! validate and order the resulting receipts for the continuing R2C batch.
//!
//! All grouping and allocation happens before publication at the COLD
//! world-loading boundary. There is no per-chunk HOT lookup, second world
//! owner, extra outbound transport queue or duplicate NBT decode.

use std::path::Path;

use helve_generated::BlockStateId;
use helve_types::ChunkPos;
use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_import::stored_biomes::SectionBiomeDecoder;
use helve_world_import::{
    BlockStateResolver, ChunkPayloadDecoder, ImportedBlockSectionBuilder, StoredBlockImporter,
};
use helve_world_load::{
    AnvilSourceAdmissionError, PregeneratedRegionError, PregeneratedRegionLimits,
    SourceChunkPublicationReceipt, import_and_install_anvil_source,
    visit_selected_pregenerated_world,
};
use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};

use crate::r2b_server::R2bPlaySession;
use crate::r2c_chunk_batch::R2cChunkBatchState;
use crate::r2c_initial_view::{
    InitialViewSelectionError, in_initial_view, prepare_initial_source_view,
};

const MIN_VIEW_DISTANCE: i32 = 2;
const MAX_VIEW_DISTANCE: i32 = 32;
const VIEW_NEIGHBOR_BUFFER: i32 = 2;
const MAX_REQUESTED_CHUNKS: usize = 4096;

/// COLD bounded first-view planning or source-ingress failure.
///
/// If one source region fails after others were admitted, previous chunks
/// and receipts remain independently valid resident objects. **No Play
/// bytes are enqueued**, and no batch state is returned; callers must
/// abort this attempted bootstrap rather than expose a partial view.
#[derive(Debug)]
#[allow(
    dead_code,
    reason = "candidate-only source admission diagnostics await the live R2C consumer"
)]
pub(crate) enum DiskFirstViewError<E> {
    InvalidViewDistance { actual: i32 },
    InvalidChunkLimit { actual: usize },
    NoSelectedChunks,
    AlreadyHasReceipts { actual: usize },
    OutsideView { position: ChunkPos },
    Disk(PregeneratedRegionError<AnvilSourceAdmissionError<E>>),
    FinalView(InitialViewSelectionError),
}

fn distance_squared(center: ChunkPos, position: ChunkPos) -> u64 {
    let dx = (i64::from(position.x) - i64::from(center.x)).unsigned_abs();
    let dz = (i64::from(position.z) - i64::from(center.z)).unsigned_abs();
    dx * dx + dz * dz
}

/// Build an optional complete/partial initial-view **request**, not a
/// claim that those chunks exist on disk or can be published.
///
/// Uses exactly the source-reviewed 26.2 two-chunk-buffered rounded
/// tracking boundary. The cap bounds the work and can represent a small
/// first visible demo before larger view windows are attempted.
/// Closest chunks are selected first; exact distance ties use (x,z)
/// only for reproducible candidate tests. Full source receipts are still
/// validated separately after disk import.
///
/// # Errors
///
/// Rejects invalid view distances or zero/excessive requested chunk caps.
pub(crate) fn plan_first_view_positions(
    center: ChunkPos,
    view_distance: i32,
    max_chunks: usize,
) -> Result<Vec<ChunkPos>, DiskFirstViewError<()>> {
    if !(MIN_VIEW_DISTANCE..=MAX_VIEW_DISTANCE).contains(&view_distance) {
        return Err(DiskFirstViewError::InvalidViewDistance {
            actual: view_distance,
        });
    }
    if !(1..=MAX_REQUESTED_CHUNKS).contains(&max_chunks) {
        return Err(DiskFirstViewError::InvalidChunkLimit { actual: max_chunks });
    }

    let radius = view_distance + VIEW_NEIGHBOR_BUFFER;
    // At most (2*34+1)^2 = 4761 candidate coordinates even for
    // the largest supported view distance. Overflowing i32 world
    // coordinates are skipped, never wrapped into another region.
    let mut requested = Vec::new();
    for dz in -radius..=radius {
        for dx in -radius..=radius {
            let (Some(x), Some(z)) = (center.x.checked_add(dx), center.z.checked_add(dz)) else {
                continue;
            };
            let position = ChunkPos { x, z };
            if in_initial_view(center, position, view_distance) {
                requested.push(position);
            }
        }
    }
    requested.sort_unstable_by_key(|&position| {
        (distance_squared(center, position), position.x, position.z)
    });
    requested.truncate(max_chunks);
    Ok(requested)
}

/// COLD player/world alignment errors before reading any selected region.
#[derive(Debug)]
pub(crate) enum PendingTeleportViewError {
    /// The retained R2B session no longer has a destination to bind.
    MissingTeleport,
    /// NaN or infinity is never a source-valid player position.
    NonFiniteTeleport,
    /// The selected, independently qualified dimension lattice excludes the
    /// requested teleport Y; publishing saved chunks would not fix it.
    OutsideVerticalLattice {
        y: f64,
        minimum: i32,
        maximum_exclusive: i32,
    },
    /// The source player position cannot be represented as a signed chunk
    /// coordinate; saturating float-to-integer conversion is forbidden.
    ChunkCoordinateOutOfRange { x: f64, z: f64 },
    /// The ordinary bounded first-view selector rejected the request.
    Request(DiskFirstViewError<()>),
}

/// Derive the COLD initial view from the *actual pending R2B teleport*.
///
/// The caller supplies the separately source-qualified dimension profile and
/// R2B view distance; those facts are NOT inferred from a world save or
/// guessed from a receipt. This candidate does not itself admit either fact.
///
/// Minecraft block-to-chunk coordinates use floor(x / 16), *not* Rust's
/// truncation toward zero. Negative fractional block positions therefore
/// select the correct negative chunk, including across signed Anvil regions.
///
/// No driver, teleport transaction, first-view receipt, or egress byte is
/// mutated. The resulting centre and request must be retained together as
/// one immutable pre-publication selection and passed to the already-existing
/// `import_disk_first_view`, never separately recomputed.
///
/// **Admission limit:** the coordinate rule must be tied to the official
/// selected 26.2 client/player source law before live world publication.
/// The selected bootstrap dimension/pack, source-save dimension and profile
/// still require their independent identity checks.
///
/// # Errors
///
/// Rejects absent/non-finite/out-of-lattice/unrepresentable teleport
/// coordinates and invalid finite first-view bounds before filesystem I/O.
#[expect(
    clippy::cast_possible_truncation,
    reason = "floored float chunk coordinates are explicitly checked within the full signed i32 range"
)]
pub(crate) fn plan_pending_teleport_first_view(
    session: &R2bPlaySession,
    profile: DimensionRuntimeProfile,
    view_distance: i32,
    max_chunks: usize,
) -> Result<(ChunkPos, Vec<ChunkPos>), PendingTeleportViewError> {
    let pending = session
        .teleport_transaction()
        .awaiting()
        .ok_or(PendingTeleportViewError::MissingTeleport)?;
    if !(pending.x.is_finite() && pending.y.is_finite() && pending.z.is_finite()) {
        return Err(PendingTeleportViewError::NonFiniteTeleport);
    }
    if pending.y < f64::from(profile.min_block_y())
        || pending.y >= f64::from(profile.max_block_y_exclusive())
    {
        return Err(PendingTeleportViewError::OutsideVerticalLattice {
            y: pending.y,
            minimum: profile.min_block_y(),
            maximum_exclusive: profile.max_block_y_exclusive(),
        });
    }
    let x = (pending.x / 16.0).floor();
    let z = (pending.z / 16.0).floor();
    if x < f64::from(i32::MIN)
        || x > f64::from(i32::MAX)
        || z < f64::from(i32::MIN)
        || z > f64::from(i32::MAX)
    {
        return Err(PendingTeleportViewError::ChunkCoordinateOutOfRange { x, z });
    }
    let center = ChunkPos {
        x: x as i32,
        z: z as i32,
    };
    let requested = plan_first_view_positions(center, view_distance, max_chunks)
        .map_err(PendingTeleportViewError::Request)?;
    Ok((center, requested))
}

/// Borrowed and finite initial-view request, grouped without owning another
/// source selection or allocating transport/bookkeeping storage.
pub(crate) struct DiskFirstViewRequest<'a> {
    pub(crate) world: &'a Path,
    pub(crate) requested: &'a mut [ChunkPos],
    pub(crate) center: ChunkPos,
    pub(crate) view_distance: i32,
    pub(crate) limits: PregeneratedRegionLimits,
}

/// Move a finite, source-selected first view from *real* pregenerated
/// Anvil files across any number of regions into the single authoritative
/// semantic dimension and prepare the receipt-backed batch cursor.
///
/// Every position is preflighted (view membership, existing receipt
/// state) **before filesystem I/O**. The world-load visitor separately
/// rejects duplicate coordinates before any filesystem access. The caller-owned position
/// vector is then sorted in place by signed source region, with no hash
/// map or duplicate position list. Each contiguous region group is
/// borrowed by `visit_pregenerated_region`, which reads and validates
/// that region once, and which in turn directly admits its selected
/// blocks/biomes/light through the source-checked import operation.
///
/// On success the caller-owned receipts are reorganized nearest-first
/// by `prepare_initial_source_view`, and the result sends the
/// source-selected cache centre before the first chunk batch.
///
/// On failure, earlier region admissions remain in the authoritative
/// dimension and `receipts` may contain their valid receipts; this
/// function is not an all-or-nothing world transaction. No publication
/// cursor is returned and the live driver is untouched.
///
/// This is a **COLD candidate seam**, not live stock-client R2C.
/// Official client biome ordinals, complete heightmap predicates and
/// outer packet admission remain independent non-negotiable gates.
///
/// # Errors
///
/// Rejects invalid request constraints, source read/import errors,
/// and source-residency errors. No packet bytes are admitted on error.
pub(crate) fn import_disk_first_view<R, SB, D, BD, MakeEmpty>(
    request: DiskFirstViewRequest<'_>,
    dimension: &mut SemanticDimensionInstance<BlockStateId, SB::Section, u16, BD::Section>,
    importer: &mut StoredBlockImporter<'_, R, SB, D>,
    biome_decoder: &mut BD,
    receipts: &mut Vec<SourceChunkPublicationReceipt>,
    mut make_empty_section: MakeEmpty,
) -> Result<R2cChunkBatchState, DiskFirstViewError<D::Error>>
where
    R: BlockStateResolver<State = BlockStateId>,
    SB: ImportedBlockSectionBuilder<BlockStateId>,
    SB::Section: BlockSection<BlockStateId>,
    D: ChunkPayloadDecoder,
    BD: SectionBiomeDecoder,
    BD::Section: BiomeSection<u16>,
    MakeEmpty: FnMut() -> SB::Section,
{
    let DiskFirstViewRequest {
        world,
        requested,
        center,
        view_distance,
        limits,
    } = request;
    if !(MIN_VIEW_DISTANCE..=MAX_VIEW_DISTANCE).contains(&view_distance) {
        return Err(DiskFirstViewError::InvalidViewDistance {
            actual: view_distance,
        });
    }
    if requested.len() > MAX_REQUESTED_CHUNKS {
        return Err(DiskFirstViewError::InvalidChunkLimit {
            actual: requested.len(),
        });
    }
    if requested.is_empty() {
        return Err(DiskFirstViewError::NoSelectedChunks);
    }
    if !receipts.is_empty() {
        return Err(DiskFirstViewError::AlreadyHasReceipts {
            actual: receipts.len(),
        });
    }
    for &position in requested.iter() {
        if !in_initial_view(center, position, view_distance) {
            return Err(DiskFirstViewError::OutsideView { position });
        }
    }
    // The existing world-load boundary owns signed region grouping,
    // duplicate preflight and one validation/read per region.
    visit_selected_pregenerated_world(world, requested, limits, |source| {
        let receipt = import_and_install_anvil_source(
            dimension,
            importer,
            source,
            biome_decoder,
            &mut make_empty_section,
        )?;
        receipts.push(receipt);
        Ok(())
    })
    .map_err(DiskFirstViewError::Disk)?;
    prepare_initial_source_view(dimension, receipts, center, view_distance)
        .map_err(DiskFirstViewError::FinalView)
}

/// One immutable COLD saved-world request for a continuing R2B player.
///
/// The profile is an explicit caller-supplied *candidate*, not proof of the
/// Configuration dimension/pack or of the persisted save's identity.
#[derive(Clone, Copy)]
pub(crate) struct PendingTeleportDiskFirstViewRequest<'a> {
    pub(crate) world: &'a Path,
    pub(crate) profile: DimensionRuntimeProfile,
    pub(crate) view_distance: i32,
    pub(crate) max_chunks: usize,
    pub(crate) limits: PregeneratedRegionLimits,
}

/// Pre-publication binding failures retain separate alignment and disk causes.
#[derive(Debug)]
pub(crate) enum PendingTeleportDiskImportError<E> {
    ProfileMismatch {
        selected: DimensionRuntimeProfile,
        resident: DimensionRuntimeProfile,
    },
    Player(PendingTeleportViewError),
    Source(DiskFirstViewError<E>),
}

/// Bind the actual retained R2B teleport to exactly one selected saved-world
/// import, using the *existing* single-authority dimension and loader.
///
/// All player/profile checks run before filesystem access and before semantic
/// installation. On success the receipts remain in caller-owned nearest-first
/// order and the returned state is the existing ACK-aware publication cursor.
/// A failed source import can still leave individually verified chunks resident,
/// as documented by `import_disk_first_view`, but never emits Play bytes.
///
/// The explicit selected profile must later be *independently* bound to the
/// world save, Configuration dimension, pack fingerprint, and official 26.2
/// biome/heightmap/outer-wire evidence. This function does not grant source
/// admission and does not enable a live publisher.
///
/// # Errors
///
/// Rejects selected/resident profile drift or invalid player view before I/O,
/// or retains the original typed bounded source-import error.
pub(crate) fn import_pending_teleport_disk_first_view<R, SB, D, BD, MakeEmpty>(
    session: &R2bPlaySession,
    request: PendingTeleportDiskFirstViewRequest<'_>,
    dimension: &mut SemanticDimensionInstance<BlockStateId, SB::Section, u16, BD::Section>,
    importer: &mut StoredBlockImporter<'_, R, SB, D>,
    biome_decoder: &mut BD,
    receipts: &mut Vec<SourceChunkPublicationReceipt>,
    make_empty_section: MakeEmpty,
) -> Result<(ChunkPos, R2cChunkBatchState), PendingTeleportDiskImportError<D::Error>>
where
    R: BlockStateResolver<State = BlockStateId>,
    SB: ImportedBlockSectionBuilder<BlockStateId>,
    SB::Section: BlockSection<BlockStateId>,
    D: ChunkPayloadDecoder,
    BD: SectionBiomeDecoder,
    BD::Section: BiomeSection<u16>,
    MakeEmpty: FnMut() -> SB::Section,
{
    let resident = dimension.profile();
    if resident != request.profile {
        return Err(PendingTeleportDiskImportError::ProfileMismatch {
            selected: request.profile,
            resident,
        });
    }
    let (center, mut requested) = plan_pending_teleport_first_view(
        session,
        request.profile,
        request.view_distance,
        request.max_chunks,
    )
    .map_err(PendingTeleportDiskImportError::Player)?;
    let state = import_disk_first_view(
        DiskFirstViewRequest {
            world: request.world,
            requested: &mut requested,
            center,
            view_distance: request.view_distance,
            limits: request.limits,
        },
        dimension,
        importer,
        biome_decoder,
        receipts,
        make_empty_section,
    )
    .map_err(PendingTeleportDiskImportError::Source)?;
    Ok((center, state))
}

#[cfg(test)]
mod tests {
    use helve_types::ChunkPos;

    use super::{DiskFirstViewError, MAX_REQUESTED_CHUNKS, plan_first_view_positions};

    use helve_generated::{AIR, BlockStateId, GeneratedStateFacts};
    use helve_types::{DimensionId, DimensionTypeId};
    use helve_world_contract::{BLOCK_SECTION_CELLS, BlockSection, SectionBlockPos};
    use helve_world_import::{
        BiomeDecodeScratch, BlockSectionDecodeScratch, ChunkPayloadLimits, ExactBiomeDecoder,
        ImportedBiomeSectionBuilder, ImportedBlockSectionBuilder, NbtLimits, OrderedBiomeRegistry,
        RegionLimits, StoredBlockImporter, TagType, Target262BlockStateResolver,
        UncompressedChunkPayloadDecoder,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};
    use std::fs;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    use super::{DiskFirstViewRequest, import_disk_first_view};
    use helve_world_load::PregeneratedRegionLimits;

    fn retained_session_with_teleport(x: f64, y: f64, z: f64) -> crate::R2bPlaySession {
        use helve_connection_core::ConnectionLimits;
        use helve_connection_driver::ConnectionDriver;
        use helve_session_core::LivenessState;
        use helve_target_26_2::r2b::TeleportTransaction;

        let mut session = crate::R2bPlaySession {
            driver: ConnectionDriver::new(ConnectionLimits::new(65_535, 131_072, 262_144).unwrap()),
            read_scratch: vec![0_u8; 64].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        };
        session.teleport.issue(x, y, z, 0.0, 0.0);
        session
    }

    fn test_overworld_lattice() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(0), -64, 384, true).unwrap()
    }

    #[test]
    fn initial_request_is_bound_to_actual_pending_r2b_teleport_not_spawn_origin() {
        let session =
            retained_session_with_teleport(10.390_952_126_751_907, 84.0, -5.815_159_807_324_014);
        let read_scratch = session.read_scratch.as_ptr();
        let (center, positions) =
            super::plan_pending_teleport_first_view(&session, test_overworld_lattice(), 10, 9)
                .unwrap();
        assert_eq!(center, ChunkPos { x: 0, z: -1 });
        assert_eq!(positions.len(), 9);
        assert_eq!(positions[0], center);
        assert_eq!(session.queued_egress(), 0);
        assert_eq!(session.buffered_ingress(), 0);
        assert_eq!(session.read_scratch.as_ptr(), read_scratch);
        assert!(session.teleport_transaction().awaiting().is_some());
    }

    #[test]
    fn negative_coordinates_use_floor_not_zero_truncation() {
        for (x, z, expected) in [
            (-0.000_001, -0.000_001, ChunkPos { x: -1, z: -1 }),
            (-16.0, -16.0, ChunkPos { x: -1, z: -1 }),
            (-16.000_001, -16.000_001, ChunkPos { x: -2, z: -2 }),
            (16.0, 16.0, ChunkPos { x: 1, z: 1 }),
        ] {
            let session = retained_session_with_teleport(x, 70.0, z);
            let (center, positions) =
                super::plan_pending_teleport_first_view(&session, test_overworld_lattice(), 2, 1)
                    .unwrap();
            assert_eq!(center, expected);
            assert_eq!(positions, [expected]);
        }
    }

    #[test]
    fn missing_invalid_or_wrong_lattice_teleport_is_rejected_before_selection() {
        use super::{PendingTeleportViewError, plan_pending_teleport_first_view};

        let session = crate::R2bPlaySession {
            driver: helve_connection_driver::ConnectionDriver::new(
                helve_connection_core::ConnectionLimits::new(65_535, 131_072, 262_144).unwrap(),
            ),
            read_scratch: vec![0_u8; 64].into_boxed_slice(),
            teleport: helve_target_26_2::r2b::TeleportTransaction::new(),
            liveness: helve_session_core::LivenessState::new(0, 0).unwrap(),
        };
        assert!(matches!(
            plan_pending_teleport_first_view(&session, test_overworld_lattice(), 2, 1),
            Err(PendingTeleportViewError::MissingTeleport)
        ));
        let invalid = retained_session_with_teleport(f64::NAN, 70.0, 0.0);
        assert!(matches!(
            plan_pending_teleport_first_view(&invalid, test_overworld_lattice(), 2, 1),
            Err(PendingTeleportViewError::NonFiniteTeleport)
        ));
        let high = retained_session_with_teleport(0.0, 320.0, 0.0);
        match plan_pending_teleport_first_view(&high, test_overworld_lattice(), 2, 1) {
            Err(PendingTeleportViewError::OutsideVerticalLattice {
                y,
                minimum,
                maximum_exclusive,
            }) => {
                assert_eq!(y.to_bits(), 320.0_f64.to_bits());
                assert_eq!(minimum, -64);
                assert_eq!(maximum_exclusive, 320);
            }
            other => panic!("expected selected dimension vertical error: {other:?}"),
        }
        let out_of_range = retained_session_with_teleport(f64::MAX, 70.0, 0.0);
        match plan_pending_teleport_first_view(&out_of_range, test_overworld_lattice(), 2, 1) {
            Err(PendingTeleportViewError::ChunkCoordinateOutOfRange { x, z }) => {
                assert!(x > f64::from(i32::MAX));
                assert_eq!(z.to_bits(), 0.0_f64.to_bits());
            }
            other => panic!("expected out-of-range chunk centre: {other:?}"),
        }
        let ordinary = retained_session_with_teleport(0.0, 70.0, 0.0);
        assert!(matches!(
            plan_pending_teleport_first_view(&ordinary, test_overworld_lattice(), 1, 9),
            Err(PendingTeleportViewError::Request(
                super::DiskFirstViewError::InvalidViewDistance { actual: 1 }
            ))
        ));
    }

    static NEXT_WORLD: AtomicU64 = AtomicU64::new(1);
    const SECTOR: usize = 4096;

    struct WorldFixture {
        root: PathBuf,
    }

    impl WorldFixture {
        fn new() -> Self {
            let seq = NEXT_WORLD.fetch_add(1, Ordering::Relaxed);
            let root = std::env::temp_dir().join(format!(
                "helve-r2c-disk-multiregion-{}-{seq}",
                std::process::id()
            ));
            fs::create_dir_all(root.join("region")).unwrap();
            Self { root }
        }

        fn write(&self, region_x: i32, slot: usize, x: i32, z: i32) {
            let nbt = saved_chunk_nbt(x, z);
            let mut bytes = vec![0_u8; 3 * SECTOR];
            let pointer = (2_u32 << 8) | 1;
            bytes[slot * 4..slot * 4 + 4].copy_from_slice(&pointer.to_be_bytes());
            bytes[SECTOR + slot * 4..SECTOR + slot * 4 + 4].copy_from_slice(&17_u32.to_be_bytes());
            bytes[2 * SECTOR..2 * SECTOR + 4]
                .copy_from_slice(&u32::try_from(nbt.len() + 1).unwrap().to_be_bytes());
            bytes[2 * SECTOR + 4] = 3;
            bytes[2 * SECTOR + 5..2 * SECTOR + 5 + nbt.len()].copy_from_slice(&nbt);
            fs::write(self.root.join(format!("region/r.{region_x}.0.mca")), bytes).unwrap();
        }
    }

    impl Drop for WorldFixture {
        fn drop(&mut self) {
            fs::remove_dir_all(&self.root).unwrap();
        }
    }

    fn nbt_name(output: &mut Vec<u8>, name: &str) {
        output.extend_from_slice(&u16::try_from(name.len()).unwrap().to_be_bytes());
        output.extend_from_slice(name.as_bytes());
    }

    fn nbt_field(output: &mut Vec<u8>, kind: TagType, name: &str) {
        output.push(kind as u8);
        nbt_name(output, name);
    }

    fn saved_chunk_nbt(x: i32, z: i32) -> Vec<u8> {
        let mut output = vec![TagType::Compound as u8, 0, 0];
        for (name, value) in [("DataVersion", 4903), ("xPos", x), ("zPos", z)] {
            nbt_field(&mut output, TagType::Int, name);
            output.extend_from_slice(&value.to_be_bytes());
        }
        nbt_field(&mut output, TagType::Byte, "isLightOn");
        output.push(1);
        nbt_field(&mut output, TagType::List, "block_entities");
        output.push(TagType::Compound as u8);
        output.extend_from_slice(&0_i32.to_be_bytes());
        nbt_field(&mut output, TagType::List, "sections");
        output.push(TagType::Compound as u8);
        output.extend_from_slice(&1_i32.to_be_bytes());

        nbt_field(&mut output, TagType::Byte, "Y");
        output.push(0);
        nbt_field(&mut output, TagType::Compound, "block_states");
        nbt_field(&mut output, TagType::List, "palette");
        output.push(TagType::Compound as u8);
        output.extend_from_slice(&1_i32.to_be_bytes());
        nbt_field(&mut output, TagType::String, "Name");
        nbt_name(&mut output, "minecraft:stone");
        output.push(TagType::End as u8);
        output.push(TagType::End as u8);

        nbt_field(&mut output, TagType::Compound, "biomes");
        nbt_field(&mut output, TagType::List, "palette");
        output.push(TagType::String as u8);
        output.extend_from_slice(&1_i32.to_be_bytes());
        nbt_name(&mut output, "minecraft:plains");
        output.push(TagType::End as u8); // biomes
        output.push(TagType::End as u8); // section
        output.push(TagType::End as u8); // root
        output
    }

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
                        let position = SectionBlockPos::new(x, y, z).unwrap();
                        section.replace(position, states[position.index()], &GeneratedStateFacts);
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

    #[test]
    #[expect(
        clippy::too_many_lines,
        reason = "one source import checks three fail-closed preflights and the retained-session success path"
    )]
    fn pending_teleport_import_checks_profile_and_source_before_residency() {
        use super::{
            PendingTeleportDiskFirstViewRequest, PendingTeleportDiskImportError,
            PendingTeleportViewError, import_pending_teleport_disk_first_view,
        };

        let world = WorldFixture::new();
        world.write(-1, 31, -1, 0);
        let profile = DimensionRuntimeProfile::new(DimensionTypeId(1), 0, 16, true).unwrap();
        let other = DimensionRuntimeProfile::new(DimensionTypeId(4), 0, 16, true).unwrap();
        let mut dimension: SemanticDimensionInstance<
            BlockStateId,
            DirectBlockSection<BlockStateId>,
            u16,
            DirectBiomeSection<u16>,
        > = SemanticDimensionInstance::new(DimensionId(2), profile);
        let resolver = Target262BlockStateResolver;
        let mut block_builder = BlockBuilder;
        let mut block_scratch = BlockSectionDecodeScratch::new();
        let mut decompressor = UncompressedChunkPayloadDecoder;
        let mut importer = StoredBlockImporter::new(
            ChunkPayloadLimits::new(32 * SECTOR, 32 * SECTOR),
            NbtLimits::new(512, 4096, 4096, 32).unwrap(),
            &mut decompressor,
            &resolver,
            &mut block_builder,
            &mut block_scratch,
        );
        let keys = ["minecraft:plains"];
        let registry = OrderedBiomeRegistry::new(4903, &keys).unwrap();
        let mut biome_builder = BiomeBuilder;
        let mut biome_scratch = BiomeDecodeScratch::new();
        let mut biome_decoder =
            ExactBiomeDecoder::new(&registry, &mut biome_builder, &mut biome_scratch);
        let mut receipts = Vec::new();
        let request = |selected_profile| PendingTeleportDiskFirstViewRequest {
            world: &world.root,
            profile: selected_profile,
            view_distance: 2,
            max_chunks: 1,
            limits: PregeneratedRegionLimits {
                region: RegionLimits::new(8 * SECTOR, SECTOR),
                max_external_bytes: 8 * SECTOR,
            },
        };

        let session = retained_session_with_teleport(-0.1, 8.0, 0.0);
        match import_pending_teleport_disk_first_view(
            &session,
            request(other),
            &mut dimension,
            &mut importer,
            &mut biome_decoder,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        ) {
            Err(PendingTeleportDiskImportError::ProfileMismatch { selected, resident }) => {
                assert_eq!(selected, other);
                assert_eq!(resident, profile);
            }
            _ => panic!("wrong selected lattice must reject"),
        }
        let bad_y = retained_session_with_teleport(-0.1, 20.0, 0.0);
        match import_pending_teleport_disk_first_view(
            &bad_y,
            request(profile),
            &mut dimension,
            &mut importer,
            &mut biome_decoder,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        ) {
            Err(PendingTeleportDiskImportError::Player(
                PendingTeleportViewError::OutsideVerticalLattice {
                    maximum_exclusive, ..
                },
            )) => assert_eq!(maximum_exclusive, 16),
            _ => panic!("out-of-lattice player must reject"),
        }
        let absent = retained_session_with_teleport(64.0, 8.0, 0.0);
        match import_pending_teleport_disk_first_view(
            &absent,
            request(profile),
            &mut dimension,
            &mut importer,
            &mut biome_decoder,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        ) {
            Err(PendingTeleportDiskImportError::Source(DiskFirstViewError::Disk(_))) => {}
            _ => panic!("missing saved region must not fall back to synthetic world"),
        }
        assert_eq!(dimension.resident_chunk_count(), 0);
        assert!(receipts.is_empty());
        assert_eq!(session.queued_egress(), 0);

        let original_reader = session.read_scratch.as_ptr();
        let (center, state) = import_pending_teleport_disk_first_view(
            &session,
            request(profile),
            &mut dimension,
            &mut importer,
            &mut biome_decoder,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        )
        .expect("real negative-region source joins the actual teleport");
        assert_eq!(center, ChunkPos { x: -1, z: 0 });
        assert_eq!(receipts.len(), 1);
        assert_eq!(receipts[0].installed().handle.position, center);
        assert_eq!(dimension.resident_chunk_count(), 1);
        assert!(receipts[0].resolve_explicitly_empty(&dimension).is_ok());
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(state.unacknowledged_batches(), 0);
        assert_eq!(session.read_scratch.as_ptr(), original_reader);
        assert!(session.teleport_transaction().awaiting().is_some());
        assert_eq!(session.queued_egress(), 0);
    }

    #[test]
    #[expect(
        clippy::too_many_lines,
        reason = "one test checks source-backed cross-region disk import through exact official wire and ACK"
    )]
    fn source_chunks_from_two_disk_regions_feed_one_nearest_first_batch() {
        use helve_connection_core::{ConnectionLimits, IngressBuffer};
        use helve_connection_driver::{ConnectionDriver, DriverError};
        use helve_session_core::LivenessState;
        use helve_target_26_2::r2b::TeleportTransaction;
        use helve_target_26_2::r2c_chunk_data::append_heightmap_map_candidate;
        use helve_target_26_2::r2c_play_wire::{
            CLIENTBOUND_CHUNK_BATCH_FINISHED, CLIENTBOUND_CHUNK_BATCH_START,
            CLIENTBOUND_CHUNK_WITH_LIGHT,
        };
        use helve_world_chunk::HeightmapStateFacts;

        use crate::r2b_server::R2bPlaySession;
        use crate::r2c_chunk_batch::{ChunkBatchInboundStep, ChunkBatchStep, R2cChunkBatchState};
        use crate::r2c_cold_demo_import::{
            ColdImportedView, R2cSourceAdmission, SourceAdmittedPlayPublisher,
            service_one_source_admitted_chunk,
        };
        use crate::r2c_heightmap_facts::CandidateHeightmapFacts;
        use crate::r2c_section_candidate::ReceiptBoundBodyCandidateError;

        let world = WorldFixture::new();
        // At the origin the selected fixed view straddles signed
        // Anvil region -1 and 0, without inventing a third region.
        world.write(-1, 31, -1, 0);
        world.write(0, 0, 0, 0);

        let profile = DimensionRuntimeProfile::new(DimensionTypeId(1), 0, 16, true).unwrap();
        let mut dimension: SemanticDimensionInstance<
            BlockStateId,
            DirectBlockSection<BlockStateId>,
            u16,
            DirectBiomeSection<u16>,
        > = SemanticDimensionInstance::new(DimensionId(2), profile);

        let resolver = Target262BlockStateResolver;
        let mut block_builder = BlockBuilder;
        let mut block_scratch = BlockSectionDecodeScratch::new();
        let mut decompressor = UncompressedChunkPayloadDecoder;
        let mut importer = StoredBlockImporter::new(
            ChunkPayloadLimits::new(32 * SECTOR, 32 * SECTOR),
            NbtLimits::new(512, 4096, 4096, 32).unwrap(),
            &mut decompressor,
            &resolver,
            &mut block_builder,
            &mut block_scratch,
        );
        let keys = ["minecraft:plains"];
        let registry = OrderedBiomeRegistry::new(4903, &keys).unwrap();
        let mut biome_builder = BiomeBuilder;
        let mut biome_scratch = BiomeDecodeScratch::new();
        let mut biome_decoder =
            ExactBiomeDecoder::new(&registry, &mut biome_builder, &mut biome_scratch);

        let center = ChunkPos { x: 0, z: 0 };
        let mut selected = vec![center, ChunkPos { x: -1, z: 0 }];
        let mut receipts = Vec::new();
        let mut state = import_disk_first_view(
            DiskFirstViewRequest {
                world: &world.root,
                requested: &mut selected,
                center,
                view_distance: 2,
                limits: PregeneratedRegionLimits {
                    region: RegionLimits::new(8 * SECTOR, SECTOR),
                    max_external_bytes: 8 * SECTOR,
                },
            },
            &mut dimension,
            &mut importer,
            &mut biome_decoder,
            &mut receipts,
            || DirectBlockSection::filled(AIR, &GeneratedStateFacts),
        )
        .expect("both real region files produce one source-valid batch");

        assert_eq!(
            selected,
            [ChunkPos { x: -1, z: 0 }, ChunkPos { x: 0, z: 0 },]
        );
        assert_eq!(dimension.resident_chunk_count(), 2);
        assert_eq!(receipts.len(), 2);
        assert_eq!(receipts[0].installed().handle.position, center);
        assert_eq!(
            receipts[1].installed().handle.position,
            ChunkPos { x: -1, z: 0 }
        );
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(state.unacknowledged_batches(), 0);
        for receipt in &receipts {
            assert!(receipt.resolve_explicitly_empty(&dimension).is_ok());
        }

        // The ordinary hermetic test proves disk import and source-receipt
        // integrity. Only the dedicated pinned *official* runtime workflow
        // can additionally authorize these candidate heightmap test bytes.
        let Some(path) = std::env::var_os("HELVE_R2C_HEIGHTMAP_CANDIDATE") else {
            return;
        };

        let oracle = std::fs::read(path).expect("source-pinned official 26.2 oracle");
        let facts = CandidateHeightmapFacts::from_oracle_bytes(&oracle)
            .expect("actual oracle IDs match qualified generated state facts");

        // Exercise the exact *product-bound* COLD audit over actual
        // disk-imported, receipt-bound semantic chunks before checking
        // the existing batch sender. No packet is queued by this audit.
        let cold_audit = crate::r2c_cold_demo_import::audit_receipt_bound_candidate_bodies(
            &dimension, &receipts, &oracle, 66,
        )
        .expect("two selected Anvil chunks reach the single bounded COLD projector");
        assert_eq!(cold_audit.chunks, 2);
        assert!(cold_audit.total_body_bytes >= cold_audit.maximum_body_bytes);
        assert!(cold_audit.maximum_body_bytes > 8);

        let stone = helve_world_import::resolve_target_26_2_block_state("minecraft:stone", &[])
            .expect("exact saved stone identity");
        let predicate = facts.properties(stone);
        assert!(predicate.non_air());
        assert!(predicate.blocks_motion());
        assert!(!predicate.leaves());
        assert!(!predicate.fluid_non_empty());

        // 16 fully solid source blocks per column, therefore all three
        // 26.2 maps must have exactly relative height 16. The independent
        // expected bits are packed manually, 5 bits x 12 lanes/long.
        let mut words = [0_u64; 22];
        for column in 0..256_usize {
            words[column / 12] |= 16_u64 << ((column % 12) * 5);
        }
        let mut expected_maps = Vec::new();
        append_heightmap_map_candidate(&mut expected_maps, 16, [&words; 3])
            .expect("independent expected exact map bytes");

        let limits = ConnectionLimits::new(65_535, 131_072, 262_144).unwrap();
        let mut session = R2bPlaySession {
            driver: ConnectionDriver::new(limits),
            read_scratch: vec![0_u8; 64].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        };
        let original_reader = session.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(65_536);
        let original_scratch = scratch.as_ptr();
        state.on_tick();
        // The positive source-admission witness exists in *tests only*.
        // Production uses an uninhabited capability, so none of these
        // candidate packets can be sent by the actual binary.
        let admission = R2cSourceAdmission;
        assert!(matches!(
            service_one_source_admitted_chunk(
                &mut session,
                &dimension,
                &receipts,
                &mut state,
                &facts,
                &mut scratch,
                &admission,
            ),
            Ok(ChunkBatchStep::CacheCenterQueued { x: 0, z: 0 })
        ));
        assert!(matches!(
            service_one_source_admitted_chunk(
                &mut session,
                &dimension,
                &receipts,
                &mut state,
                &facts,
                &mut scratch,
                &admission,
            ),
            Ok(ChunkBatchStep::Started { count: 2 })
        ));
        for index in 0..2 {
            if index == 1 {
                // A truncated receipt selection must reject without panic,
                // appending bytes, or advancing the source publication cursor.
                let queued_before = session.pending_play_egress().to_vec();
                let cursor_before = state.next_chunk_index();
                assert!(matches!(
                    service_one_source_admitted_chunk(
                        &mut session,
                        &dimension,
                        &receipts[..1],
                        &mut state,
                        &facts,
                        &mut scratch,
                        &admission,
                    ),
                    Err(DriverError::Handler(
                        ReceiptBoundBodyCandidateError::MissingReceipt {
                            index: 1,
                            available: 1
                        }
                    ))
                ));
                assert_eq!(session.pending_play_egress(), queued_before);
                assert_eq!(state.next_chunk_index(), cursor_before);
                assert!(scratch.is_empty());
            }
            assert!(matches!(
                service_one_source_admitted_chunk(
                &mut session,
                &dimension,
                &receipts,
                &mut state,
                &facts,
                &mut scratch,
                &admission,
            ),
                Ok(ChunkBatchStep::ChunkQueued { index: actual, .. }) if actual == index
            ));
        }
        assert!(matches!(
            service_one_source_admitted_chunk(
                &mut session,
                &dimension,
                &receipts,
                &mut state,
                &facts,
                &mut scratch,
                &admission,
            ),
            Ok(ChunkBatchStep::Finished { count: 2 })
        ));
        assert_eq!(scratch.as_ptr(), original_scratch);
        assert_eq!(session.read_scratch.as_ptr(), original_reader);
        assert!(scratch.is_empty());
        assert_eq!(state.next_chunk_index(), 2);
        assert_eq!(state.unacknowledged_batches(), 1);

        let mut wire = IngressBuffer::new(limits);
        wire.push(session.pending_play_egress()).unwrap();
        let center_frame = wire.peek_frame().unwrap().unwrap();
        assert_eq!(center_frame.packet_id(), 94);
        assert_eq!(center_frame.payload(), [0, 0]);
        let taken = center_frame.stream_bytes();
        wire.consume(taken).unwrap();
        let start = wire.peek_frame().unwrap().unwrap();
        assert_eq!(start.packet_id(), i32::from(CLIENTBOUND_CHUNK_BATCH_START));
        let taken = start.stream_bytes();
        wire.consume(taken).unwrap();

        for expected in [center, ChunkPos { x: -1, z: 0 }] {
            let packet = wire.peek_frame().unwrap().unwrap();
            assert_eq!(packet.packet_id(), i32::from(CLIENTBOUND_CHUNK_WITH_LIGHT));
            assert_eq!(&packet.payload()[..4], &expected.x.to_be_bytes());
            assert_eq!(&packet.payload()[4..8], &expected.z.to_be_bytes());
            assert_eq!(
                &packet.payload()[8..8 + expected_maps.len()],
                expected_maps,
                "saved source and independent heightmap projection must match"
            );
            assert!(packet.payload().len() > 8 + expected_maps.len());
            let taken = packet.stream_bytes();
            wire.consume(taken).unwrap();
        }
        let finish = wire.peek_frame().unwrap().unwrap();
        assert_eq!(
            finish.packet_id(),
            i32::from(CLIENTBOUND_CHUNK_BATCH_FINISHED)
        );
        assert_eq!(finish.payload(), [2]);
        let taken = finish.stream_bytes();
        wire.consume(taken).unwrap();
        assert_eq!(wire.buffered_len(), 0);

        // Real 26.2 float32 rate acknowledgement: 9.0 chunks/tick.
        session.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            session.process_one_r2c_chunk_batch_ack(&mut state),
            Ok(ChunkBatchInboundStep::Received {
                desired_per_tick: 9.0,
            })
        );
        assert_eq!(state.unacknowledged_batches(), 0);

        // Independently exercise the now-connected Play scheduling seam:
        // move, do not copy, the SAME dimension and receipts into its owner.
        // This is deliberately source-admitted in tests ONLY, with the
        // already verified official heightmap table supplied as an argument.
        let previous_egress = session.pending_play_egress().to_vec();
        let mut retained = ColdImportedView::from_test_source(
            dimension,
            receipts,
            R2cChunkBatchState::new_with_initial_cache_center(2, center),
        );
        let mut publication =
            SourceAdmittedPlayPublisher::new(&mut session, &oracle, 100, &admission)
                .expect("test-only receipt publisher reuses the original driver");
        assert_eq!(publication.next_wake_deadline_ms(800), 100);
        assert_eq!(publication.service(&mut session, &mut retained, 99).unwrap(), 1);
        // A cache-centre update is allowed even before a tick; the batch
        // START is still quota-gated.
        assert_eq!(publication.service(&mut session, &mut retained, 100).unwrap(), 4);
        assert_eq!(publication.service(&mut session, &mut retained, 100).unwrap(), 0);
        assert_eq!(publication.next_wake_deadline_ms(800), 150);
        // The two independently assembled source-bound publications agree
        // byte for byte, including cache centre, start, heightmaps, sections,
        // light, finish and their framing, on the same continuing driver.
        assert_eq!(
            &session.pending_play_egress()[previous_egress.len()..],
            previous_egress.as_slice(),
        );
        assert_eq!(session.read_scratch.as_ptr(), original_reader);
        session.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert!(matches!(
            retained.process_one_play_inbound(&mut session, 150),
            Ok(crate::r2c_play_inbound::R2cPlayInboundStep::ChunkBatchAcknowledged { .. })
        ));
    }

    #[test]
    fn bounded_nearest_first_plan_respects_vanilla_round_corners() {
        let center = ChunkPos { x: 0, z: 0 };
        let requested = plan_first_view_positions(center, 2, 9).unwrap();
        assert_eq!(requested.len(), 9);
        assert_eq!(requested[0], center);
        assert_eq!(requested[1], ChunkPos { x: -1, z: 0 });
        assert_eq!(requested[2], ChunkPos { x: 0, z: -1 });
        assert_eq!(requested[3], ChunkPos { x: 0, z: 1 });
        assert_eq!(requested[4], ChunkPos { x: 1, z: 0 });
        assert_eq!(requested[1].x.div_euclid(32), -1);
        assert_eq!(requested[2].z.div_euclid(32), -1);
        assert_eq!(requested[3].x.div_euclid(32), 0);
        assert_eq!((-33_i32).div_euclid(32), -2);
    }

    #[test]
    fn complete_plan_is_finite_and_has_no_duplicate_positions() {
        let center = ChunkPos { x: -27, z: 30 };
        let mut requested = plan_first_view_positions(center, 32, MAX_REQUESTED_CHUNKS).unwrap();
        assert!(requested.len() > 3500);
        assert!(requested.len() <= MAX_REQUESTED_CHUNKS);
        requested.sort_unstable_by_key(|pos| (pos.x, pos.z));
        assert!(requested.windows(2).all(|pair| pair[0] != pair[1]));
    }

    #[test]
    fn unsupported_bounds_and_overflowing_world_coordinates_fail_closed() {
        let center = ChunkPos {
            x: i32::MAX,
            z: i32::MIN,
        };
        assert!(matches!(
            plan_first_view_positions(center, 1, 9),
            Err(DiskFirstViewError::InvalidViewDistance { actual: 1 })
        ));
        assert!(matches!(
            plan_first_view_positions(center, 2, 0),
            Err(DiskFirstViewError::InvalidChunkLimit { actual: 0 })
        ));
        assert!(matches!(
            plan_first_view_positions(center, 2, MAX_REQUESTED_CHUNKS + 1),
            Err(DiskFirstViewError::InvalidChunkLimit { .. })
        ));
        let requested = plan_first_view_positions(center, 2, 17).unwrap();
        assert_eq!(requested[0], center);
        assert!(
            requested
                .iter()
                .all(|pos| pos.x <= center.x && pos.z >= center.z)
        );
        assert!(
            requested
                .iter()
                .all(|&pos| super::in_initial_view(center, pos, 2))
        );
    }
}
