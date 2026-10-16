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
use helve_world_runtime::SemanticDimensionInstance;

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
    fn source_chunks_from_two_disk_regions_feed_one_nearest_first_batch() {
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
        let state = import_disk_first_view(
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
