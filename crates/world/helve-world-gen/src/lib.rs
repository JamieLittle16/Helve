//! Deterministic, target-neutral COLD chunk generation into Helve's *existing* semantic owner.
//!
//! This crate deliberately does not own a world directory, a registry, an extra chunk image,
//! networking, lighting, persistence, or a scheduler. The caller obtains its generation from
//! `SemanticDimensionInstance::admit_chunk` and installs the returned *ordinary* semantic chunk.
//! Production generator kernels will replace the sample surface rule without changing ownership.
//!
//! IMPORTANT: `SteppedSurface` is a deterministic **non-vanilla example**, not Minecraft 26.2
//! noise, biome, density, surface, structure or lighting generation. It must not be advertised as
//! source-admitted terrain or routed into R2C's production publication gate.

#![forbid(unsafe_code)]

/// Exact-JVM-output-qualified, integer-block-Y composition of two density primitives.
/// Production admission and full DensityFunctions/NoiseRouter semantics remain closed.
pub mod density_composition_262;

/// Official-JVM-vector-qualified, direct-seeded noise-backed density leaf.
/// Borrow-only COLD hot path; NOT world RandomState, NoiseRouter or production admitted.
pub mod density_noise_direct_262;

/// Source-free-vector-qualified, immutable 26.2 improved-gradient noise candidate.
/// Not yet a source/SEM-admitted production terrain generator.
/// Non-admitted immutable density-expression DAG and COLD 3D cell sampling.
pub mod density_kernel_262;
/// Source-free-JVM-bit-validated 26.2 integer-block density primitive candidates.
/// Separate from the generic floating-coordinate DAG; not VAR/SEM-admitted.
pub mod density_primitives_262;
pub mod explicit_noise_stack_262;
pub mod improved_noise_262;
/// Source-free JVM-state-backed Perlin and Normal noise candidates; not seed-authorised or production-admitted.
pub mod perlin_normal_262;

use helve_types::{ChunkGeneration, ChunkPos};
use helve_world_chunk::{
    ChunkBiomeColumn, ChunkBiomeColumnError, ChunkCoreError, ChunkSemanticStateError,
    LiveChunkCore, LiveChunkSemanticState,
};
use helve_world_contract::{BIOME_SECTION_CELLS, BLOCK_SECTION_CELLS, BiomeSection, BlockSection};
use helve_world_runtime::DimensionRuntimeProfile;

/// One typed section sample. Uniform sections avoid creating, scanning or
/// copying a redundant dense 4096-cell array in the common full/empty case.
#[derive(Clone, Copy, Debug)]
pub enum SectionSamples<'a, T: Copy + Eq, const N: usize> {
    Uniform(T),
    Dense(&'a [T; N]),
}

/// A statically dispatched adapter from sampled *semantic values* to the selected
/// section mechanism. The adapter owns neither a second world nor any resident index.
/// A future palette/packed section can implement this without changing worldgen logic.
pub trait GeneratedSectionBuilder<S: Copy + Eq, B: Copy + Eq> {
    type Blocks: BlockSection<S>;
    type Biomes: BiomeSection<B>;
    type Error;

    /// Build one block section from a uniform value or 4096 Y/Z/X-linearized cells.
    ///
    /// # Errors
    /// Returns a mechanism-specific section construction error.
    fn blocks(
        &mut self,
        samples: SectionSamples<'_, S, BLOCK_SECTION_CELLS>,
    ) -> Result<Self::Blocks, Self::Error>;

    /// Build one biome section from a uniform value or 64 quart-biome cells.
    ///
    /// # Errors
    /// Returns a mechanism-specific biome-section construction error.
    fn biomes(
        &mut self,
        samples: SectionSamples<'_, B, BIOME_SECTION_CELLS>,
    ) -> Result<Self::Biomes, Self::Error>;
}

/// Explicit semantic palette for this isolated example. State and biome IDs
/// must be selected by the caller; worldgen never guesses vanilla ordinals.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SurfacePalette<S: Copy + Eq, B: Copy + Eq> {
    pub air: S,
    pub solid: S,
    pub biome: B,
}

/// Failure during COLD generation; no partially built chunk is returned.
#[derive(Debug)]
pub enum SurfaceGenerationError<E> {
    BlockSection { section_y: i32, cause: E },
    BiomeSection { section_y: i32, cause: E },
    Blocks(ChunkCoreError),
    Biomes(ChunkBiomeColumnError),
    Compose(ChunkSemanticStateError),
}

/// A small **non-vanilla** deterministic reference terrain rule.
///
/// One seeded height sample is used for each 8×8 world-space plateau.
/// Sampling is independent of chunk invocation/order/worker assignment.
/// The stable fixed-width hash is an example contract, not Mojang noise.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SteppedSurface {
    seed: u64,
    base_y: i32,
    amplitude: u8,
}

impl SteppedSurface {
    /// Constructs a wholly owned fixed-size sample kernel.
    #[must_use]
    pub const fn new(seed: u64, base_y: i32, amplitude: u8) -> Self {
        Self {
            seed,
            base_y,
            amplitude,
        }
    }

    /// Samples the topmost solid Y at any signed world coordinate.
    ///
    /// Widened arithmetic avoids overflow for even extreme i32 chunk
    /// coordinates. Euclidean division keeps the same 8×8 cells on both
    /// sides of negative chunk boundaries.
    ///
    /// # Panics
    /// The fixed u8 amplitude mathematically bounds the sample span and
    /// modulo result to fit u64 and i64 respectively; a conversion panic
    /// would indicate this invariant had been violated.
    #[must_use]
    pub fn surface_y(&self, world_x: i64, world_z: i64) -> i64 {
        let cell_x = world_x.div_euclid(8);
        let cell_z = world_z.div_euclid(8);
        let mut value = self.seed
            ^ u64::from_ne_bytes(cell_x.to_ne_bytes()).wrapping_mul(0x9e37_79b9_7f4a_7c15)
            ^ u64::from_ne_bytes(cell_z.to_ne_bytes()).wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value ^= value >> 30;
        value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value ^= value >> 27;
        value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
        value ^= value >> 31;
        let amplitude = i64::from(self.amplitude);
        let span = u64::try_from(2 * amplitude + 1).expect("u8 sample amplitude fits u64");
        let sample = i64::try_from(value % span).expect("sample fits i64") - amplitude;
        i64::from(self.base_y) + sample
    }

    /// Generate a complete, pristine ordinary Helve semantic chunk.
    ///
    /// The caller supplies the **actual** directory-reserved incarnation and
    /// pre-resolved dimension profile. Reuses a 256-column height scratch and one dense section array
    /// across sections and allocates only the two final section vectors; the
    /// section builder chooses its final storage with static dispatch.
    ///
    /// The biome rule is intentionally a single caller-selected identity.
    /// No lighting is claimed or synthesized (initial light is absent).
    ///
    /// # Errors
    /// Fails on block/biome builder error or an incompatible chunk/lattice.
    /// No world state is touched; call inside `admit_chunk` for atomic install.
    ///
    /// # Panics
    /// The frozen dimension profile admits at most 64 sections; a
    /// section-index conversion panic would violate that source contract.
    #[expect(
        clippy::type_complexity,
        reason = "The statically dispatched output encodes the exact Helve block/biome section types and typed builder error without a second owned representation"
    )]
    pub fn generate_chunk<S, B, Builder>(
        &self,
        position: ChunkPos,
        generation: ChunkGeneration,
        profile: DimensionRuntimeProfile,
        palette: SurfacePalette<S, B>,
        builder: &mut Builder,
    ) -> Result<
        LiveChunkSemanticState<S, Builder::Blocks, B, Builder::Biomes>,
        SurfaceGenerationError<Builder::Error>,
    >
    where
        S: Copy + Eq,
        B: Copy + Eq,
        Builder: GeneratedSectionBuilder<S, B>,
    {
        let section_count = profile.section_count();
        let mut blocks = Vec::with_capacity(section_count);
        let mut biomes = Vec::with_capacity(section_count);
        let mut cells = [palette.air; BLOCK_SECTION_CELLS];

        // Sample one column exactly once, even for 24+ vertical sections.
        // Two extrema permit cheap whole-section air/solid fast paths;
        // neither the surface cache nor the cell scratch escapes this call.
        let mut heights = [0_i64; 256];
        let mut lowest = i64::MAX;
        let mut highest = i64::MIN;
        for z in 0_u8..16 {
            let world_z = i64::from(position.z) * 16 + i64::from(z);
            for x in 0_u8..16 {
                let world_x = i64::from(position.x) * 16 + i64::from(x);
                let height = self.surface_y(world_x, world_z);
                heights[usize::from(z) * 16 + usize::from(x)] = height;
                lowest = lowest.min(height);
                highest = highest.max(height);
            }
        }

        for section_index in 0..section_count {
            let section_y = profile.min_section_y()
                + i32::try_from(section_index).expect("dimension has at most 64 sections");
            let min_y = i64::from(section_y) * 16;
            let samples = if min_y > highest {
                SectionSamples::Uniform(palette.air)
            } else if min_y + 15 <= lowest {
                SectionSamples::Uniform(palette.solid)
            } else {
                for y in 0_u8..16 {
                    for z in 0_u8..16 {
                        for x in 0_u8..16 {
                            let index = usize::from(y) * 256 + usize::from(z) * 16 + usize::from(x);
                            let column = usize::from(z) * 16 + usize::from(x);
                            cells[index] = if min_y + i64::from(y) <= heights[column] {
                                palette.solid
                            } else {
                                palette.air
                            };
                        }
                    }
                }
                SectionSamples::Dense(&cells)
            };
            blocks.push(
                builder
                    .blocks(samples)
                    .map_err(|cause| SurfaceGenerationError::BlockSection { section_y, cause })?,
            );
            biomes.push(
                builder
                    .biomes(SectionSamples::Uniform(palette.biome))
                    .map_err(|cause| SurfaceGenerationError::BiomeSection { section_y, cause })?,
            );
        }

        let blocks = LiveChunkCore::new(position, generation, profile.min_section_y(), blocks)
            .map_err(SurfaceGenerationError::Blocks)?;
        let biomes = ChunkBiomeColumn::new(position, generation, profile.min_section_y(), biomes)
            .map_err(SurfaceGenerationError::Biomes)?;
        LiveChunkSemanticState::from_parts(blocks, biomes).map_err(SurfaceGenerationError::Compose)
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{
        BlockPos, ChunkGeneration, ChunkPos, ChunkRevision, DimensionId, DimensionTypeId,
    };
    use helve_world_contract::{
        BIOME_SECTION_CELLS, BLOCK_SECTION_CELLS, BlockStateFacts, SectionBiomePos,
        SectionStateFacts,
    };
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
    use helve_world_runtime::{
        DimensionRuntimeProfile, SemanticDimensionInstance, SemanticResidentLoadError,
    };

    use super::{
        GeneratedSectionBuilder, SectionSamples, SteppedSurface, SurfaceGenerationError,
        SurfacePalette,
    };

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum State {
        Air,
        Solid,
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Biome {
        Test,
    }

    struct Facts;

    impl BlockStateFacts<State> for Facts {
        fn facts(&self, state: State) -> SectionStateFacts {
            SectionStateFacts::new(state == State::Solid, false, false, false)
        }
    }

    #[derive(Default)]
    struct ReferenceBuilder {
        sections_built: usize,
        uniform_blocks: usize,
        dense_blocks: usize,
        reject_at: Option<usize>,
    }

    impl GeneratedSectionBuilder<State, Biome> for ReferenceBuilder {
        type Blocks = DirectBlockSection<State>;
        type Biomes = DirectBiomeSection<Biome>;
        type Error = &'static str;

        fn blocks(
            &mut self,
            samples: SectionSamples<'_, State, BLOCK_SECTION_CELLS>,
        ) -> Result<Self::Blocks, Self::Error> {
            self.sections_built += 1;
            if self.reject_at == Some(self.sections_built) {
                return Err("deliberate builder rejection");
            }
            Ok(match samples {
                SectionSamples::Uniform(state) => {
                    self.uniform_blocks += 1;
                    DirectBlockSection::filled(state, &Facts)
                }
                SectionSamples::Dense(cells) => {
                    self.dense_blocks += 1;
                    DirectBlockSection::from_decoded_cells(cells, &Facts)
                }
            })
        }

        fn biomes(
            &mut self,
            samples: SectionSamples<'_, Biome, BIOME_SECTION_CELLS>,
        ) -> Result<Self::Biomes, Self::Error> {
            Ok(match samples {
                SectionSamples::Uniform(biome) => DirectBiomeSection::filled(biome),
                SectionSamples::Dense(cells) => {
                    let mut section = DirectBiomeSection::filled(cells[0]);
                    section.fill_with(|x, y, z| {
                        let local = SectionBiomePos::new(x, y, z).expect("4x4x4 quart coordinate");
                        cells[local.index()]
                    });
                    section
                }
            })
        }
    }

    type Dimension = SemanticDimensionInstance<
        State,
        DirectBlockSection<State>,
        Biome,
        DirectBiomeSection<Biome>,
    >;

    const PALETTE: SurfacePalette<State, Biome> = SurfacePalette {
        air: State::Air,
        solid: State::Solid,
        biome: Biome::Test,
    };

    fn profile() -> DimensionRuntimeProfile {
        DimensionRuntimeProfile::new(DimensionTypeId(3), -32, 96, true).unwrap()
    }

    #[test]
    fn negative_coordinates_and_chunk_edges_share_one_global_height_sample() {
        let rule = SteppedSurface::new(7, -7, 5);
        for (x, z) in [(-1, -1), (-8, -16), (-16, 0), (0, -1), (15, 16), (16, 16)] {
            let sample = rule.surface_y(x, z);
            assert_eq!(sample, rule.surface_y(x, z));
            assert!((-12..=-2).contains(&sample));
        }
        assert_eq!(rule.surface_y(-1, -1), rule.surface_y(-8, -8));
        assert_eq!(rule.surface_y(15, 0), rule.surface_y(8, 7));
        assert_eq!(rule.surface_y(16, 0), rule.surface_y(23, 7));
        // i32::MIN chunk coordinates are widened before multiplying by 16.
        assert!(
            (-12..=-2)
                .contains(&rule.surface_y(i64::from(i32::MIN) * 16, i64::from(i32::MAX) * 16),)
        );
    }

    #[test]
    fn fixed_width_surface_hash_has_frozen_independent_seed_vectors() {
        // Precomputed with independent wrapping-u64 arithmetic, not by
        // calling the same sampler to manufacture an expected value.
        let cases = [
            (7_u64, -7_i32, 5_u8, -1_i64, -1_i64, -11_i64),
            (7, -7, 5, -8, -16, -3),
            (7, -7, 5, 15, 16, -7),
            (7, -7, 5, 16, 16, -9),
            (901, -4, 4, -16, 0, -4),
            (901, -4, 4, -1, 0, -7),
            (44, -9, 7, 0, -3, -9),
            (
                u64::MAX,
                i32::MAX,
                u8::MAX,
                i64::from(i32::MIN) * 16,
                i64::from(i32::MAX) * 16,
                2_147_483_886,
            ),
        ];
        for (seed, base_y, amplitude, x, z, expected) in cases {
            assert_eq!(
                SteppedSurface::new(seed, base_y, amplitude).surface_y(x, z),
                expected,
                "seed={seed}, x={x}, z={z}",
            );
        }
    }

    #[test]
    fn generated_sections_match_world_coordinates_and_keep_pristine_revision() {
        let rule = SteppedSurface::new(901, -4, 4);
        let position = ChunkPos { x: -1, z: 0 };
        let mut builder = ReferenceBuilder::default();
        let chunk = rule
            .generate_chunk(
                position,
                ChunkGeneration(17),
                profile(),
                PALETTE,
                &mut builder,
            )
            .unwrap();
        assert_eq!(builder.sections_built, 6);
        assert!(builder.uniform_blocks > 0);
        assert!(builder.dense_blocks > 0);
        assert_eq!(chunk.position(), position);
        assert_eq!(chunk.generation(), ChunkGeneration(17));
        assert_eq!(chunk.revision(), ChunkRevision(0));
        assert!(chunk.current_initial_light().is_none());
        for local_x in 0..16 {
            for local_z in 0..16 {
                let x = -16 + local_x;
                let z = local_z;
                let height = rule.surface_y(i64::from(x), i64::from(z));
                for y in -32..64 {
                    assert_eq!(
                        chunk.get_block(BlockPos { x, y, z }).unwrap(),
                        if i64::from(y) <= height {
                            State::Solid
                        } else {
                            State::Air
                        },
                        "x={x}, y={y}, z={z}",
                    );
                }
            }
        }
        assert_ne!(chunk.block_masks().non_air_bits(), 0);
        for section_y in -2..4 {
            for x in 0..4 {
                for y in 0..4 {
                    for z in 0..4 {
                        assert_eq!(
                            chunk
                                .get_biome(section_y, SectionBiomePos::new(x, y, z).unwrap(),)
                                .unwrap(),
                            Biome::Test,
                        );
                    }
                }
            }
        }
    }

    #[test]
    fn independently_requested_chunks_are_order_invariant_across_dimensions() {
        let rule = SteppedSurface::new(44, -9, 7);
        let left = ChunkPos { x: -1, z: 2 };
        let right = ChunkPos { x: 0, z: 2 };
        let mut first = Dimension::new(DimensionId(2), profile());
        let mut second = Dimension::new(DimensionId(3), profile());
        let mut builder = ReferenceBuilder::default();
        let l1 = first
            .admit_chunk(left, |generation, p| {
                rule.generate_chunk(left, generation, p, PALETTE, &mut builder)
            })
            .unwrap();
        let r1 = first
            .admit_chunk(right, |generation, p| {
                rule.generate_chunk(right, generation, p, PALETTE, &mut builder)
            })
            .unwrap();
        let r2 = second
            .admit_chunk(right, |generation, p| {
                rule.generate_chunk(right, generation, p, PALETTE, &mut builder)
            })
            .unwrap();
        let l2 = second
            .admit_chunk(left, |generation, p| {
                rule.generate_chunk(left, generation, p, PALETTE, &mut builder)
            })
            .unwrap();

        for (a, b, x0) in [(l1, l2, -16), (r1, r2, 0)] {
            let aa = first.resolve_chunk(a).unwrap();
            let bb = second.resolve_chunk(b).unwrap();
            for z in 32..48 {
                for x in x0..x0 + 16 {
                    for y in -32..64 {
                        let pos = BlockPos { x, y, z };
                        assert_eq!(aa.get_block(pos).unwrap(), bb.get_block(pos).unwrap());
                    }
                }
            }
        }
        let other_seed = SteppedSurface::new(45, -9, 7);
        assert!((0..128).any(|x| rule.surface_y(x, -3) != other_seed.surface_y(x, -3)));
    }

    #[test]
    fn duplicate_residency_never_invokes_builder_or_replaces_owner() {
        let rule = SteppedSurface::new(9, 0, 1);
        let position = ChunkPos { x: 1, z: -1 };
        let mut dim = Dimension::new(DimensionId(2), profile());
        let mut builder = ReferenceBuilder::default();
        let original = dim
            .admit_chunk(position, |generation, p| {
                rule.generate_chunk(position, generation, p, PALETTE, &mut builder)
            })
            .unwrap();
        let calls = builder.sections_built;
        let rejected = dim.admit_chunk(position, |generation, p| {
            rule.generate_chunk(position, generation, p, PALETTE, &mut builder)
        });
        assert!(matches!(
            rejected,
            Err(SemanticResidentLoadError::AlreadyResident { .. })
        ));
        assert_eq!(builder.sections_built, calls);
        assert_eq!(dim.resident_chunk_count(), 1);
        assert_eq!(
            dim.resolve_chunk(original).unwrap().revision(),
            ChunkRevision(0)
        );
    }

    #[test]
    fn failed_section_build_does_not_install_or_consume_generation() {
        let rule = SteppedSurface::new(123, -11, 4);
        let position = ChunkPos { x: 8, z: 9 };
        let mut dim = Dimension::new(DimensionId(3), profile());
        let mut broken = ReferenceBuilder {
            reject_at: Some(2),
            ..ReferenceBuilder::default()
        };
        let rejected = dim.admit_chunk(position, |generation, p| {
            rule.generate_chunk(position, generation, p, PALETTE, &mut broken)
        });
        assert!(matches!(
            rejected,
            Err(SemanticResidentLoadError::Build(
                SurfaceGenerationError::BlockSection {
                    section_y: -1,
                    cause: "deliberate builder rejection",
                }
            ))
        ));
        assert_eq!(dim.resident_chunk_count(), 0);
        assert!(dim.discover_chunk(position).is_none());
        let mut good = ReferenceBuilder::default();
        let handle = dim
            .admit_chunk(position, |generation, p| {
                rule.generate_chunk(position, generation, p, PALETTE, &mut good)
            })
            .unwrap();
        assert_eq!(handle.generation, ChunkGeneration(1));
        assert_eq!(
            dim.resolve_chunk(handle).unwrap().revision(),
            ChunkRevision(0)
        );
    }
}
