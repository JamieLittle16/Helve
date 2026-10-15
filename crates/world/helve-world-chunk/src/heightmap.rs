//! Source-admitted client heightmap semantics, independent of Minecraft wire packing.
//!
//! The reference path reads authoritative section state and produces one explicitly stamped
//! immutable result. No derived arrays or invalidation hooks are added to the HOT mutation path.
//! A later production mechanism may cache or incrementally maintain equivalent results, but must
//! compare against this direct recomputation oracle and preserve the generation/revision stamp.

use helve_types::ChunkStamp;
use helve_world_contract::{BlockSection, SectionBlockPos};

use crate::LiveChunkCore;

const AXIS: usize = 16;
/// Number of x/z columns represented by each client heightmap.
pub const HEIGHTMAP_COLUMNS: usize = AXIS * AXIS;

const WORLD_SURFACE: u8 = 1;
const MOTION_BLOCKING: u8 = 2;
const MOTION_BLOCKING_NO_LEAVES: u8 = 4;

/// The three client-visible heightmap semantics admitted for the selected 26.2 route.
///
/// Numerical target registry IDs and packed wire representation belong to the target adapter.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ClientHeightmapKind {
    WorldSurface,
    MotionBlocking,
    MotionBlockingNoLeaves,
}

/// Independent, pre-resolved predicates for one semantic block state.
///
/// Section-count flags alone cannot provide these predicates: counted fluid, motion blocking and
/// leaves are distinct properties. A target provider must obtain all four facts from independently
/// admitted state data instead of guessing from the section summary or stored NBT Heightmaps.
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct HeightmapStateProperties(u8);

impl HeightmapStateProperties {
    const NON_AIR: u8 = 1;
    const BLOCKS_MOTION: u8 = 2;
    const FLUID_NON_EMPTY: u8 = 4;
    const LEAVES: u8 = 8;

    /// Packs the four independent admitted predicates into one byte.
    #[must_use]
    #[expect(
        clippy::fn_params_excessive_bools,
        reason = "four distinct source-admitted block properties are packed into one byte"
    )]
    pub const fn new(
        non_air: bool,
        blocks_motion: bool,
        fluid_non_empty: bool,
        leaves: bool,
    ) -> Self {
        let mut flags = 0;
        if non_air {
            flags |= Self::NON_AIR;
        }
        if blocks_motion {
            flags |= Self::BLOCKS_MOTION;
        }
        if fluid_non_empty {
            flags |= Self::FLUID_NON_EMPTY;
        }
        if leaves {
            flags |= Self::LEAVES;
        }
        Self(flags)
    }

    /// Whether the block is not air (the `WORLD_SURFACE` predicate).
    #[must_use]
    pub const fn non_air(self) -> bool {
        self.0 & Self::NON_AIR != 0
    }

    /// Whether the state blocks motion.
    #[must_use]
    pub const fn blocks_motion(self) -> bool {
        self.0 & Self::BLOCKS_MOTION != 0
    }

    /// Whether the state contains a non-empty fluid.
    #[must_use]
    pub const fn fluid_non_empty(self) -> bool {
        self.0 & Self::FLUID_NON_EMPTY != 0
    }

    /// Whether the state is leaves.
    #[must_use]
    pub const fn leaves(self) -> bool {
        self.0 & Self::LEAVES != 0
    }

    fn matching_kinds(self) -> u8 {
        let mut matching = 0;
        if self.non_air() {
            matching |= WORLD_SURFACE;
        }
        if self.blocks_motion() || self.fluid_non_empty() {
            matching |= MOTION_BLOCKING;
            if !self.leaves() {
                matching |= MOTION_BLOCKING_NO_LEAVES;
            }
        }
        matching
    }
}

/// Supplies source-admitted heightmap facts at a static boundary.
///
/// Production will use a generated dense lookup for the selected target. This trait introduces
/// neither runtime dispatch nor per-mutation derived-state bookkeeping.
pub trait HeightmapStateFacts<S: Copy> {
    /// Returns the exact four source-backed predicates for a semantic block-state identity.
    fn properties(&self, state: S) -> HeightmapStateProperties;
}

/// An immutable, generation/revision-stamped three-map reference result.
///
/// Each entry is "first available Y - chunk minY"; zero means no matching block. The maximum
/// admitted chunk height is 64 sections (1024 blocks), so a u16 is sufficient for each entry.
/// This representation is semantic, not the target's packed-long network representation.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ClientHeightmaps {
    stamp: ChunkStamp,
    min_block_y: i32,
    world_surface: [u16; HEIGHTMAP_COLUMNS],
    motion_blocking: [u16; HEIGHTMAP_COLUMNS],
    motion_blocking_no_leaves: [u16; HEIGHTMAP_COLUMNS],
}

impl ClientHeightmaps {
    /// Derives the complete client set directly from one authoritative block chunk.
    ///
    /// One descending traversal per x/z column fills all three maps together, stopping when all
    /// predicates have found their topmost matching state. No world-coordinate multiplication,
    /// world-directory lookup, scratch heap allocation or live-state mutation is required. This
    /// recomputation is a cold/reference operation; do not invoke it on each block mutation.
    ///
    /// # Panics
    ///
    /// Only if the existing validated chunk section-count or section-local coordinate
    /// invariants are broken. Both conversion bounds are guaranteed by `LiveChunkCore`.
    #[must_use]
    pub fn derive<S, Section, Facts>(chunk: &LiveChunkCore<S, Section>, facts: &Facts) -> Self
    where
        S: Copy + Eq,
        Section: BlockSection<S>,
        Facts: HeightmapStateFacts<S>,
    {
        let mut world_surface = [0_u16; HEIGHTMAP_COLUMNS];
        let mut motion_blocking = [0_u16; HEIGHTMAP_COLUMNS];
        let mut motion_blocking_no_leaves = [0_u16; HEIGHTMAP_COLUMNS];

        for z in 0_u8..16 {
            for x in 0_u8..16 {
                let column = usize::from(x) + AXIS * usize::from(z);
                let mut remaining = WORLD_SURFACE | MOTION_BLOCKING | MOTION_BLOCKING_NO_LEAVES;
                'scan: for section_index in (0..chunk.sections.len()).rev() {
                    let section = &chunk.sections[section_index];
                    for y in (0_u8..16).rev() {
                        let pos =
                            SectionBlockPos::new(x, y, z).expect("loop bounds are section-local");
                        let matched =
                            facts.properties(section.get(pos)).matching_kinds() & remaining;
                        if matched == 0 {
                            continue;
                        }
                        let relative_y = u16::try_from(section_index * AXIS + usize::from(y) + 1)
                            .expect("chunk mask admits at most 64 sections");
                        if matched & WORLD_SURFACE != 0 {
                            world_surface[column] = relative_y;
                        }
                        if matched & MOTION_BLOCKING != 0 {
                            motion_blocking[column] = relative_y;
                        }
                        if matched & MOTION_BLOCKING_NO_LEAVES != 0 {
                            motion_blocking_no_leaves[column] = relative_y;
                        }
                        remaining &= !matched;
                        if remaining == 0 {
                            break 'scan;
                        }
                    }
                }
            }
        }

        Self {
            stamp: chunk.stamp(),
            min_block_y: chunk.vertical_lattice().min_block_y(),
            world_surface,
            motion_blocking,
            motion_blocking_no_leaves,
        }
    }

    /// Exact generation and revision of the semantic blocks used for this result.
    #[must_use]
    pub const fn stamp(&self) -> ChunkStamp {
        self.stamp
    }

    /// Returns all 256 first-available Y offsets in x + 16*z order, without allocation.
    #[must_use]
    pub const fn relative_heights(&self, kind: ClientHeightmapKind) -> &[u16; HEIGHTMAP_COLUMNS] {
        match kind {
            ClientHeightmapKind::WorldSurface => &self.world_surface,
            ClientHeightmapKind::MotionBlocking => &self.motion_blocking,
            ClientHeightmapKind::MotionBlockingNoLeaves => &self.motion_blocking_no_leaves,
        }
    }

    /// Returns the first available absolute block Y, or None for an invalid local x/z.
    #[must_use]
    pub fn first_available(&self, kind: ClientHeightmapKind, x: u8, z: u8) -> Option<i32> {
        if x >= 16 || z >= 16 {
            return None;
        }
        let column = usize::from(x) + AXIS * usize::from(z);
        Some(self.min_block_y + i32::from(self.relative_heights(kind)[column]))
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos};
    use helve_world_contract::{BlockStateFacts, SectionStateFacts};
    use helve_world_reference::DirectBlockSection;

    use super::{
        ClientHeightmapKind as Kind, ClientHeightmaps, HeightmapStateFacts,
        HeightmapStateProperties,
    };
    use crate::LiveChunkCore;

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Block {
        Air,
        Stone,
        Water,
        Leaves,
        TallGrass,
    }

    struct Facts;

    impl BlockStateFacts<Block> for Facts {
        fn facts(&self, state: Block) -> SectionStateFacts {
            SectionStateFacts::new(state != Block::Air, state == Block::Water, false, false)
        }
    }

    impl HeightmapStateFacts<Block> for Facts {
        fn properties(&self, state: Block) -> HeightmapStateProperties {
            HeightmapStateProperties::new(
                state != Block::Air,
                matches!(state, Block::Stone | Block::Leaves),
                state == Block::Water,
                state == Block::Leaves,
            )
        }
    }

    type Chunk = LiveChunkCore<Block, DirectBlockSection<Block>>;

    fn chunk() -> Chunk {
        LiveChunkCore::new(
            ChunkPos { x: -2, z: 3 },
            ChunkGeneration(7),
            -1,
            vec![
                DirectBlockSection::filled(Block::Air, &Facts),
                DirectBlockSection::filled(Block::Air, &Facts),
            ],
        )
        .expect("two-section chunk")
    }

    fn set(chunk: &mut Chunk, y: i32, block: Block) {
        let result = chunk
            .replace_block(BlockPos { x: -27, y, z: 55 }, block, &Facts)
            .expect("selected cell lies inside signed chunk");
        assert_eq!(result.changed, result.old != block);
    }

    #[test]
    fn empty_columns_and_invalid_local_coordinates() {
        let heights = ClientHeightmaps::derive(&chunk(), &Facts);
        for kind in [
            Kind::WorldSurface,
            Kind::MotionBlocking,
            Kind::MotionBlockingNoLeaves,
        ] {
            assert_eq!(heights.relative_heights(kind), &[0_u16; 256]);
            assert_eq!(heights.first_available(kind, 0, 0), Some(-16));
            assert_eq!(heights.first_available(kind, 5, 7), Some(-16));
            assert_eq!(heights.first_available(kind, 16, 0), None);
            assert_eq!(heights.first_available(kind, 0, 16), None);
        }
    }

    #[test]
    fn all_three_predicates_follow_exact_topmost_matches_and_revisions() {
        let mut core = chunk();
        let before = ClientHeightmaps::derive(&core, &Facts);
        set(&mut core, -14, Block::Water);
        set(&mut core, -1, Block::Leaves);
        set(&mut core, 13, Block::TallGrass);
        let heights = ClientHeightmaps::derive(&core, &Facts);

        assert_ne!(before.stamp(), heights.stamp());
        assert_eq!(heights.first_available(Kind::WorldSurface, 5, 7), Some(14));
        assert_eq!(heights.first_available(Kind::MotionBlocking, 5, 7), Some(0));
        assert_eq!(
            heights.first_available(Kind::MotionBlockingNoLeaves, 5, 7),
            Some(-13)
        );
        assert_eq!(heights.first_available(Kind::WorldSurface, 0, 0), Some(-16));
        assert_eq!(heights.relative_heights(Kind::WorldSurface)[5 + 16 * 7], 30);

        set(&mut core, 15, Block::Stone);
        let with_stone = ClientHeightmaps::derive(&core, &Facts);
        for kind in [
            Kind::WorldSurface,
            Kind::MotionBlocking,
            Kind::MotionBlockingNoLeaves,
        ] {
            assert_eq!(with_stone.first_available(kind, 5, 7), Some(16));
        }
        set(&mut core, 15, Block::Air);
        let restored = ClientHeightmaps::derive(&core, &Facts);
        for kind in [
            Kind::WorldSurface,
            Kind::MotionBlocking,
            Kind::MotionBlockingNoLeaves,
        ] {
            assert_eq!(
                restored.relative_heights(kind),
                heights.relative_heights(kind)
            );
        }
        assert_ne!(restored.stamp(), heights.stamp());
        let same_stamp = core.stamp();
        set(&mut core, 15, Block::Air);
        assert_eq!(core.stamp(), same_stamp);
    }

    #[test]
    fn height_derivation_does_not_materialize_world_coordinates_at_chunk_extremes() {
        let extreme = LiveChunkCore::new(
            ChunkPos {
                x: i32::MAX,
                z: i32::MIN,
            },
            ChunkGeneration(1),
            i32::MIN / 16,
            vec![DirectBlockSection::filled(Block::Air, &Facts)],
        )
        .expect("valid minimum Y");
        let heights = ClientHeightmaps::derive(&extreme, &Facts);
        assert_eq!(
            heights.first_available(Kind::MotionBlocking, 15, 15),
            Some(i32::MIN)
        );
    }

    #[test]
    fn fused_scan_matches_independent_per_kind_brute_force() {
        let mut core = chunk();
        for y in -16..16 {
            for z in 0_u8..16 {
                for x in 0_u8..16 {
                    let block = match (y + i32::from(x) * 3 + i32::from(z) * 5).rem_euclid(11) {
                        0 => Block::Stone,
                        1 => Block::Water,
                        2 => Block::Leaves,
                        3 => Block::TallGrass,
                        _ => Block::Air,
                    };
                    core.replace_block(
                        BlockPos {
                            x: -32 + i32::from(x),
                            y,
                            z: 48 + i32::from(z),
                        },
                        block,
                        &Facts,
                    )
                    .expect("valid cell");
                }
            }
        }
        let fused = ClientHeightmaps::derive(&core, &Facts);
        for z in 0_u8..16 {
            for x in 0_u8..16 {
                for kind in [
                    Kind::WorldSurface,
                    Kind::MotionBlocking,
                    Kind::MotionBlockingNoLeaves,
                ] {
                    let mut expected = -16;
                    for y in (-16..16).rev() {
                        let block = core
                            .get_block(BlockPos {
                                x: -32 + i32::from(x),
                                y,
                                z: 48 + i32::from(z),
                            })
                            .expect("valid cell");
                        let props = Facts.properties(block);
                        let matches_kind = match kind {
                            Kind::WorldSurface => props.non_air(),
                            Kind::MotionBlocking => {
                                props.blocks_motion() || props.fluid_non_empty()
                            }
                            Kind::MotionBlockingNoLeaves => {
                                (props.blocks_motion() || props.fluid_non_empty())
                                    && !props.leaves()
                            }
                        };
                        if matches_kind {
                            expected = y + 1;
                            break;
                        }
                    }
                    assert_eq!(fused.first_available(kind, x, z), Some(expected));
                }
            }
        }
        assert_eq!(fused.stamp(), core.stamp());
    }
}
