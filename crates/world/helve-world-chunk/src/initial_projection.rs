//! One COLD borrowed, whole-chunk-coherent reference for initial client world publication.
//!
//! This is not a packet encoder, second resident owner, light engine or persistent cache.
//! Source chunks own blocks, biomes and optional initial light under one existing revision.
//! A fresh immutable borrow yields all three directly; heightmap packing is computed only
//! at this reference/publication boundary and cannot drift under the borrow.

use helve_types::{ChunkPos, ChunkStamp};
use helve_world_contract::{BiomeSection, BlockSection};

use crate::{
    ChunkBiomeColumn, HeightmapProjectionError, HeightmapStateFacts, InitialLightMaskReference,
    LightMaskReferenceError, LiveChunkCore, LiveChunkSemanticState, PackedClientHeightmaps,
};

/// A whole initial chunk cannot be represented by an exact verified semantic snapshot.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum InitialChunkReferenceError {
    /// No persisted initial light exists, light is unverified, or a real mutation invalidated it.
    NoCurrentVerifiedLight,
    /// The independently supplied target state facts or heightmap shape cannot be projected.
    Heightmaps(HeightmapProjectionError),
    /// The initial light source layer or its mask interpretation was rejected.
    LightMasks(LightMaskReferenceError),
}

/// One immutable, target-neutral, complete initial chunk reference.
///
/// Contains only a direct **borrow** of the current semantic owner plus COLD derived masks
/// and heightmaps. A caller must independently source-qualify numeric biome IDs and all
/// `HeightmapStateFacts`; this type does not confer any unreviewed wire-packet authority.
#[derive(Debug)]
pub struct InitialChunkReference<'a, S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    source: &'a LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
    heightmaps: PackedClientHeightmaps,
    light_masks: InitialLightMaskReference<'a>,
}

impl<'a, S, BlockStorage, B, BiomeStorage>
    InitialChunkReference<'a, S, BlockStorage, B, BiomeStorage>
where
    S: Copy + Eq,
    BlockStorage: BlockSection<S>,
    B: Copy + Eq,
    BiomeStorage: BiomeSection<B>,
{
    /// Builds a complete, immutable initial reference from one current semantic owner.
    ///
    /// This performs no directory lookup, new live-state tracking, source parse, or
    /// packet serialization. The exact target predicate provider is statically bound,
    /// and the source chunk stays immutably borrowed through any later projection.
    ///
    /// # Errors
    ///
    /// Rejects a missing/unverified/stale initial light, invalid exact heightmaps, or
    /// inconsistently classified light layers. Never manufactures fallback lighting.
    ///
    /// # Panics
    ///
    /// Only if the already validated resident chunk internally violates the invariant
    /// that each section has exactly its admitted number of logical cells.
    pub fn derive<F>(
        source: &'a LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
        facts: &F,
    ) -> Result<Self, InitialChunkReferenceError>
    where
        F: HeightmapStateFacts<S>,
    {
        let light = source
            .current_initial_light()
            .ok_or(InitialChunkReferenceError::NoCurrentVerifiedLight)?;
        let light_masks = InitialLightMaskReference::derive(light)
            .map_err(InitialChunkReferenceError::LightMasks)?;
        let heightmaps = PackedClientHeightmaps::derive(source, facts)
            .map_err(InitialChunkReferenceError::Heightmaps)?;

        Ok(Self {
            source,
            heightmaps,
            light_masks,
        })
    }

    /// Exact source chunk position; requires no resolution or copy.
    #[must_use]
    pub const fn position(&self) -> ChunkPos {
        self.source.position()
    }

    /// Whole-chunk generation and revision shared by all borrowed components.
    #[must_use]
    pub const fn stamp(&self) -> ChunkStamp {
        self.source.stamp()
    }

    /// Borrow canonical section block state; it is not a packet-shaped duplicate.
    #[must_use]
    pub const fn blocks(&self) -> &'a LiveChunkCore<S, BlockStorage> {
        self.source.blocks()
    }

    /// Borrow canonical quart biomes, which must have been bound to source-verified IDs.
    #[must_use]
    pub const fn biomes(&self) -> &'a ChunkBiomeColumn<B, BiomeStorage> {
        self.source.biomes()
    }

    /// Exact stamped three-map client heightmap long-array reference.
    #[must_use]
    pub const fn heightmaps(&self) -> &PackedClientHeightmaps {
        &self.heightmaps
    }

    /// Independently classified initial sky/block data and empty masks with borrowed payloads.
    #[must_use]
    pub const fn light_masks(&self) -> &InitialLightMaskReference<'a> {
        &self.light_masks
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use crate::{
        ChunkBiomeColumn, HeightmapStateFacts, HeightmapStateProperties, ImportedLightSection,
        InitialChunkLight, LightDataLayer, LightKind, LiveChunkCore, LiveChunkSemanticState,
        VerticalSectionLattice,
    };

    use super::{InitialChunkReference, InitialChunkReferenceError};

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

    type Semantic =
        LiveChunkSemanticState<u8, DirectBlockSection<u8>, u16, DirectBiomeSection<u16>>;

    fn chunk(correct: bool, with_light: bool) -> Semantic {
        let position = ChunkPos { x: -3, z: 4 };
        let generation = ChunkGeneration(9);
        let blocks = LiveChunkCore::new(
            position,
            generation,
            -1,
            vec![
                DirectBlockSection::filled(0, &Facts),
                DirectBlockSection::filled(0, &Facts),
            ],
        )
        .expect("two resident sections");
        let biomes = ChunkBiomeColumn::new(
            position,
            generation,
            -1,
            vec![
                DirectBiomeSection::filled(2_u16),
                DirectBiomeSection::filled(5_u16),
            ],
        )
        .expect("identical lattice");
        let semantic = LiveChunkSemanticState::from_parts(blocks, biomes).expect("whole owner");
        if !with_light {
            return semantic;
        }
        let light = InitialChunkLight::from_imported(
            position,
            generation,
            VerticalSectionLattice::new(-1, 2).expect("lattice"),
            true,
            correct,
            vec![ImportedLightSection {
                section_y: -2,
                block: Some(LightDataLayer::homogeneous(3).expect("nibble")),
                sky: Some(LightDataLayer::homogeneous(15).expect("nibble")),
            }],
        )
        .expect("source light");
        semantic.with_initial_light(light).expect("fresh identity")
    }

    #[test]
    fn one_read_only_snapshot_reuses_original_owner_and_current_source_light() {
        let semantic = chunk(true, true);
        let projected =
            InitialChunkReference::derive(&semantic, &Facts).expect("verified whole initial image");
        assert_eq!(projected.position(), semantic.position());
        assert_eq!(projected.stamp(), semantic.stamp());
        assert!(std::ptr::eq(projected.blocks(), semantic.blocks()));
        assert!(std::ptr::eq(projected.biomes(), semantic.biomes()));
        assert_eq!(projected.heightmaps().entries().len(), 3);
        assert!(projected.heightmaps().is_current_for(&semantic));
        assert_eq!(projected.light_masks().min_light_section_y(), -2);
        assert_eq!(projected.light_masks().light_section_count(), 4);
        assert_eq!(projected.light_masks().data_mask(LightKind::Sky), 1);
        assert_eq!(projected.light_masks().data_mask(LightKind::Block), 1);
        let mut visited = Vec::new();
        projected
            .light_masks()
            .for_each_update(LightKind::Block, |y, _| {
                visited.push(y);
            })
            .expect("canonical layer visits");
        assert_eq!(visited, vec![-2]);
        assert_eq!(
            projected
                .biomes()
                .get(-1, SectionBiomePos::new(0, 0, 0).expect("valid quart"),),
            Ok(2),
        );
    }

    #[test]
    fn no_source_light_or_unverified_saved_light_fails_closed() {
        assert!(matches!(
            InitialChunkReference::derive(&chunk(true, false), &Facts),
            Err(InitialChunkReferenceError::NoCurrentVerifiedLight),
        ));
        assert!(matches!(
            InitialChunkReference::derive(&chunk(false, true), &Facts),
            Err(InitialChunkReferenceError::NoCurrentVerifiedLight),
        ));
    }

    #[test]
    fn real_block_or_biome_mutation_prevents_reusing_initial_lighting() {
        let mut semantic = chunk(true, true);
        assert!(InitialChunkReference::derive(&semantic, &Facts).is_ok());
        let noop = semantic
            .replace_biome(-1, SectionBiomePos::new(0, 0, 0).unwrap(), 2)
            .expect("identical biome");
        assert!(!noop.changed);
        assert!(InitialChunkReference::derive(&semantic, &Facts).is_ok());
        semantic
            .replace_biome(-1, SectionBiomePos::new(0, 0, 0).unwrap(), 4)
            .expect("real biome edit");
        assert!(matches!(
            InitialChunkReference::derive(&semantic, &Facts),
            Err(InitialChunkReferenceError::NoCurrentVerifiedLight),
        ));

        let mut block_changed = chunk(true, true);
        block_changed
            .replace_block(
                BlockPos {
                    x: -48,
                    y: -16,
                    z: 64,
                },
                1,
                &Facts,
            )
            .expect("real source block edit");
        assert!(matches!(
            InitialChunkReference::derive(&block_changed, &Facts),
            Err(InitialChunkReferenceError::NoCurrentVerifiedLight),
        ));
    }
}
