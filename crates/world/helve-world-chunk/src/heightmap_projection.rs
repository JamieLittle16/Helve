//! Source-law COLD reference projection of stamped 26.2 client heightmaps into packed longs.
//!
//! This does not own another resident heightmap or act as a clientbound packet serializer.
//! It reads the current authoritative block core, recomputes all three admitted heightmaps
//! once, then produces immutable non-spanning packed words with an exact chunk revision stamp.

use helve_types::{ChunkPos, ChunkStamp};
use helve_world_contract::{BiomeSection, BlockSection};

use crate::{
    ClientHeightmapKind, ClientHeightmaps, HEIGHTMAP_COLUMNS, HeightmapStateFacts,
    LiveChunkSemanticState,
};

const BITS_PER_LONG: usize = u64::BITS as usize;
const BLOCKS_PER_SECTION: usize = 16;

/// Source-admitted 26.2 client heightmap numeric names; not generic registry IDs.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ClientHeightmapWireKind {
    WorldSurface = 1,
    MotionBlocking = 4,
    MotionBlockingNoLeaves = 5,
}

/// Fail-closed heightmap reference packing errors.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum HeightmapProjectionError {
    /// An impossible/unsupported section height was supplied by the resident chunk.
    HeightUnrepresentable { sections: usize },
    /// The reference height exceeded the source dimension's logical height.
    HeightOutsideDimension {
        column: usize,
        value: u16,
        height: u16,
    },
}

/// One heightmap's immutable non-spanning long storage, produced only for publication/reference.
#[derive(Debug, Eq, PartialEq)]
pub struct PackedHeightmap {
    kind: ClientHeightmapWireKind,
    bits_per_entry: u8,
    words: Box<[u64]>,
}

impl PackedHeightmap {
    /// Exact target heightmap enum ID (`WORLD_SURFACE=1`, `MOTION_BLOCKING=4`, `NO_LEAVES=5`).
    #[must_use]
    pub const fn kind(&self) -> ClientHeightmapWireKind {
        self.kind
    }

    /// Exact source storage width, ceil(log2(dimensionBlockHeight + 1)).
    #[must_use]
    pub const fn bits_per_entry(&self) -> u8 {
        self.bits_per_entry
    }

    /// Borrowed immutable, non-spanning 64-bit raw long data; no packet copies are retained.
    #[must_use]
    pub fn words(&self) -> &[u64] {
        &self.words
    }
}

/// One COLD, whole-chunk-stamped projection containing exactly the three admitted client maps.
///
/// Recompute from the authoritative block section data once per publication. Call
/// `is_current_for` at the publication boundary; biome-only mutations also advance the
/// semantic chunk stamp, preventing publication of a stale whole-chunk snapshot.
#[derive(Debug, Eq, PartialEq)]
pub struct PackedClientHeightmaps {
    position: ChunkPos,
    stamp: ChunkStamp,
    entries: [PackedHeightmap; 3],
}

impl PackedClientHeightmaps {
    /// Recomputes the three client-facing maps in one direct oracle pass and packs their raw longs.
    ///
    /// `facts` must supply independently admitted, exact target non-air, blocks-motion,
    /// fluid-nonempty and leaf predicates. This operation does not itself invent those facts.
    ///
    /// # Errors
    ///
    /// Refuses out-of-range heightmaps or an unsupported dimension section height.
    ///
    /// # Panics
    ///
    /// Only if an already-validated `LiveChunkSemanticState` violates its internal section
    /// count or cell-coordinate invariants during the existing recomputation oracle.
    pub fn derive<S, BlockStorage, B, BiomeStorage, Facts>(
        chunk: &LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
        facts: &Facts,
    ) -> Result<Self, HeightmapProjectionError>
    where
        S: Copy + Eq,
        BlockStorage: BlockSection<S>,
        B: Copy + Eq,
        BiomeStorage: BiomeSection<B>,
        Facts: HeightmapStateFacts<S>,
    {
        let section_count = chunk.section_count();
        let height = section_count
            .checked_mul(BLOCKS_PER_SECTION)
            .and_then(|value| u16::try_from(value).ok())
            .ok_or(HeightmapProjectionError::HeightUnrepresentable {
                sections: section_count,
            })?;
        if !(16..=1_024).contains(&height) {
            return Err(HeightmapProjectionError::HeightUnrepresentable {
                sections: section_count,
            });
        }
        let source = ClientHeightmaps::derive(chunk.blocks(), facts);
        Ok(Self {
            position: chunk.position(),
            stamp: chunk.stamp(),
            entries: [
                pack_source_heights(
                    source.relative_heights(ClientHeightmapKind::WorldSurface),
                    ClientHeightmapWireKind::WorldSurface,
                    height,
                )?,
                pack_source_heights(
                    source.relative_heights(ClientHeightmapKind::MotionBlocking),
                    ClientHeightmapWireKind::MotionBlocking,
                    height,
                )?,
                pack_source_heights(
                    source.relative_heights(ClientHeightmapKind::MotionBlockingNoLeaves),
                    ClientHeightmapWireKind::MotionBlockingNoLeaves,
                    height,
                )?,
            ],
        })
    }

    /// Exact position and incarnation/revision freshness, including biome-only changes.
    #[must_use]
    pub fn is_current_for<S, BlockStorage, B, BiomeStorage>(
        &self,
        chunk: &LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
    ) -> bool
    where
        S: Copy + Eq,
        BlockStorage: BlockSection<S>,
        B: Copy + Eq,
        BiomeStorage: BiomeSection<B>,
    {
        self.position == chunk.position() && self.stamp == chunk.stamp()
    }

    /// Fixed client map ordering, without adding a packet-shaped resident state.
    #[must_use]
    pub const fn entries(&self) -> &[PackedHeightmap; 3] {
        &self.entries
    }

    /// Immutable exact generation/revision stamp captured by the reference.
    #[must_use]
    pub const fn stamp(&self) -> ChunkStamp {
        self.stamp
    }
}

fn pack_source_heights(
    heights: &[u16; HEIGHTMAP_COLUMNS],
    kind: ClientHeightmapWireKind,
    height: u16,
) -> Result<PackedHeightmap, HeightmapProjectionError> {
    let bits = (u32::from(height)).ilog2() + 1;
    let width =
        usize::try_from(bits).map_err(|_| HeightmapProjectionError::HeightUnrepresentable {
            sections: usize::from(height) / BLOCKS_PER_SECTION,
        })?;
    let entries_per_long = BITS_PER_LONG / width;
    let mut words = vec![0_u64; HEIGHTMAP_COLUMNS.div_ceil(entries_per_long)];
    for (column, &value) in heights.iter().enumerate() {
        if value > height {
            return Err(HeightmapProjectionError::HeightOutsideDimension {
                column,
                value,
                height,
            });
        }
        let slot = column / entries_per_long;
        let shift = (column % entries_per_long) * width;
        words[slot] |= u64::from(value) << shift;
    }
    let bits_per_entry =
        u8::try_from(bits).map_err(|_| HeightmapProjectionError::HeightUnrepresentable {
            sections: usize::from(height) / BLOCKS_PER_SECTION,
        })?;
    Ok(PackedHeightmap {
        kind,
        bits_per_entry,
        words: words.into_boxed_slice(),
    })
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use crate::{
        ChunkBiomeColumn, HeightmapStateFacts, HeightmapStateProperties, LiveChunkCore,
        LiveChunkSemanticState,
    };

    use super::{
        ClientHeightmapWireKind, HEIGHTMAP_COLUMNS, HeightmapProjectionError,
        PackedClientHeightmaps, pack_source_heights,
    };

    struct Facts;

    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, state: u8) -> SectionStateFacts {
            SectionStateFacts::new(state != 0, false, false, false)
        }
    }

    impl HeightmapStateFacts<u8> for Facts {
        fn properties(&self, state: u8) -> HeightmapStateProperties {
            HeightmapStateProperties::new(state != 0, state != 0, false, false)
        }
    }

    fn make_chunk()
    -> LiveChunkSemanticState<u8, DirectBlockSection<u8>, u16, DirectBiomeSection<u16>> {
        let pos = ChunkPos { x: -2, z: 1 };
        let blocks = LiveChunkCore::new(
            pos,
            ChunkGeneration(8),
            -1,
            vec![
                DirectBlockSection::filled(0, &Facts),
                DirectBlockSection::filled(0, &Facts),
            ],
        )
        .expect("two sections");
        let biomes = ChunkBiomeColumn::new(
            pos,
            ChunkGeneration(8),
            -1,
            vec![DirectBiomeSection::filled(1), DirectBiomeSection::filled(2)],
        )
        .expect("biomes");
        LiveChunkSemanticState::from_parts(blocks, biomes).expect("coherent")
    }

    fn unpack(words: &[u64], bits: usize, column: usize) -> u16 {
        let per_word = 64 / bits;
        let mask = (1_u64 << bits) - 1;
        u16::try_from((words[column / per_word] >> ((column % per_word) * bits)) & mask)
            .expect("11-bit height")
    }

    #[test]
    fn nonspanning_bit_width_and_raw_word_boundaries_match_source_law() {
        for height in [16_u16, 32, 256, 384, 1_024] {
            let mut heights = [0_u16; HEIGHTMAP_COLUMNS];
            for (column, value) in heights.iter_mut().enumerate() {
                *value = u16::try_from(column % (usize::from(height) + 1)).expect("bounded height");
            }
            heights[0] = height;
            heights[255] = height;
            let result =
                pack_source_heights(&heights, ClientHeightmapWireKind::WorldSurface, height)
                    .expect("all values fit");
            let bits = (u32::from(height)).ilog2() + 1;
            let width = usize::try_from(bits).expect("small width");
            let per_word = 64 / width;
            assert_eq!(usize::from(result.bits_per_entry()), width);
            assert_eq!(result.words().len(), HEIGHTMAP_COLUMNS.div_ceil(per_word));
            for (column, &expected) in heights.iter().enumerate() {
                assert_eq!(unpack(result.words(), width, column), expected);
            }
        }
    }

    #[test]
    fn malformed_relative_height_rejected_before_publication() {
        let mut heights = [0_u16; HEIGHTMAP_COLUMNS];
        heights[64] = 33;
        assert_eq!(
            pack_source_heights(&heights, ClientHeightmapWireKind::MotionBlocking, 32),
            Err(HeightmapProjectionError::HeightOutsideDimension {
                column: 64,
                value: 33,
                height: 32,
            }),
        );
    }

    #[test]
    fn derives_three_client_type_ids_and_rejects_stale_semantic_revisions() {
        let mut chunk = make_chunk();
        let projected = PackedClientHeightmaps::derive(&chunk, &Facts).expect("valid reference");
        assert_eq!(
            projected
                .entries()
                .iter()
                .map(super::PackedHeightmap::kind)
                .collect::<Vec<_>>(),
            vec![
                ClientHeightmapWireKind::WorldSurface,
                ClientHeightmapWireKind::MotionBlocking,
                ClientHeightmapWireKind::MotionBlockingNoLeaves,
            ],
        );
        assert!(projected.is_current_for(&chunk));
        let same_biome = chunk
            .replace_biome(-1, SectionBiomePos::new(0, 0, 0).expect("quart"), 1)
            .expect("biome no-op");
        assert!(!same_biome.changed);
        assert!(projected.is_current_for(&chunk));
        let changed_biome = chunk
            .replace_biome(-1, SectionBiomePos::new(0, 0, 0).expect("quart"), 3)
            .expect("real biome edit");
        assert!(changed_biome.changed);
        assert!(!projected.is_current_for(&chunk));
        let biome_updated =
            PackedClientHeightmaps::derive(&chunk, &Facts).expect("fresh biome stamp");
        assert!(biome_updated.is_current_for(&chunk));
        assert_eq!(projected.entries()[0].bits_per_entry(), 6);
        assert!(
            projected
                .entries()
                .iter()
                .all(|entry| { entry.words().len() == HEIGHTMAP_COLUMNS.div_ceil(64 / 6) })
        );
        chunk
            .replace_block(
                BlockPos {
                    x: -32,
                    y: -16,
                    z: 16,
                },
                1,
                &Facts,
            )
            .expect("valid block edit");
        assert!(!biome_updated.is_current_for(&chunk));
        let updated = PackedClientHeightmaps::derive(&chunk, &Facts).expect("rederive");
        assert!(updated.is_current_for(&chunk));
        assert_eq!(unpack(updated.entries()[0].words(), 6, 0), 1);
        assert_eq!(unpack(updated.entries()[1].words(), 6, 0), 1);
        assert_eq!(unpack(updated.entries()[2].words(), 6, 0), 1);
    }
}
