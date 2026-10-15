//! Permanent COLD reference for source-admitted initial client light-mask classification.
//!
//! The reference borrows the canonical `InitialChunkLight` directly: it is not a second
//! light engine or network-shaped world state. Packed-present zero is not the same as empty.
//! Packet encoding and outbound publication remain deliberately outside this module.

use crate::{ChunkLightError, InitialChunkLight, LightDataLayer, LightKind};

/// One light section's classification in the target-neutral 26.2 initial light lattice.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LightSectionClass {
    /// No source layer exists here; set no present or empty mask bit.
    Absent,
    /// The source layer is present, homogeneous and unmaterialized with zero intensity.
    Empty,
    /// A present non-empty layer whose 2048-byte payload can be materialized on demand.
    Data,
}

/// Fail-closed reference projection errors. They never upgrade unverified source lighting.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LightMaskReferenceError {
    /// Persisted lighting has not been validated as correct for this initial image.
    UnverifiedLight,
    /// The exact source light lattice refused a section access.
    Layer(ChunkLightError),
    /// Bounded light slot index cannot be represented as a signed section offset.
    SectionIndexOverflow { index: usize },
    /// A data mask bit did not resolve to its expected canonical source layer.
    InconsistentDataBit { kind: LightKind, section_y: i32 },
}

/// The exact initial light masks derived on demand from one borrowed semantic light column.
///
/// The selected light section count is dimension section count + 2 (at most 66) and fits in four
/// `u128` masks. Bits are local to the light lattice, beginning at minSectionY-1.
/// This is a **reference**, not a persistent cache. No extra light revision, heap allocation,
/// copied 2048-byte array or HOT block/biome mutation work is introduced.
#[derive(Debug)]
pub struct InitialLightMaskReference<'a> {
    light: &'a InitialChunkLight,
    sky_data: u128,
    block_data: u128,
    sky_empty: u128,
    block_empty: u128,
}

impl<'a> InitialLightMaskReference<'a> {
    /// Classifies every light section under the admitted null/empty/data mask law.
    ///
    /// The caller should obtain the input through
    /// `LiveChunkSemanticState::current_initial_light`, which additionally rejects lighting
    /// invalidated by subsequent block or biome mutations. This constructor itself rejects
    /// persisted false correctness even when called directly.
    ///
    /// # Errors
    ///
    /// Rejects unverified lighting and any impossible section lookup failure without
    /// fabricating a fallback light image.
    pub fn derive(light: &'a InitialChunkLight) -> Result<Self, LightMaskReferenceError> {
        if !light.persisted_light_correct() {
            return Err(LightMaskReferenceError::UnverifiedLight);
        }

        let mut result = Self {
            light,
            sky_data: 0,
            block_data: 0,
            sky_empty: 0,
            block_empty: 0,
        };
        for index in 0..light.light_section_count() {
            // At most 66 source-backed light slots; u128 admits every possible mask bit.
            let bit = 1_u128 << index;
            let offset = i32::try_from(index)
                .map_err(|_| LightMaskReferenceError::SectionIndexOverflow { index })?;
            let section_y = light.min_light_section_y() + offset;
            for kind in [LightKind::Sky, LightKind::Block] {
                let layer = light
                    .layer(kind, section_y)
                    .map_err(LightMaskReferenceError::Layer)?;
                match (kind, classify(layer)) {
                    (_, LightSectionClass::Absent) => {}
                    (LightKind::Sky, LightSectionClass::Empty) => result.sky_empty |= bit,
                    (LightKind::Block, LightSectionClass::Empty) => result.block_empty |= bit,
                    (LightKind::Sky, LightSectionClass::Data) => result.sky_data |= bit,
                    (LightKind::Block, LightSectionClass::Data) => result.block_data |= bit,
                }
            }
        }
        Ok(result)
    }

    /// First source light section in both sky and block mask coordinate systems.
    #[must_use]
    pub const fn min_light_section_y(&self) -> i32 {
        self.light.min_light_section_y()
    }

    /// Source-derived light mask width, exactly dimension section count plus two.
    #[must_use]
    pub fn light_section_count(&self) -> usize {
        self.light.light_section_count()
    }

    /// Mask of present layers whose full 2048-byte data is required.
    #[must_use]
    pub const fn data_mask(&self, kind: LightKind) -> u128 {
        match kind {
            LightKind::Sky => self.sky_data,
            LightKind::Block => self.block_data,
        }
    }

    /// Mask of present homogeneous-zero layers, distinct from null layers.
    #[must_use]
    pub const fn empty_mask(&self, kind: LightKind) -> u128 {
        match kind {
            LightKind::Sky => self.sky_empty,
            LightKind::Block => self.block_empty,
        }
    }

    /// Visits data-bearing sections in *ascending light-section index* order, without allocation.
    ///
    /// This is the order in which the admitted light update lists must be formed. The
    /// caller-provided visitor may stream materialization of each layer through an existing
    /// reusable `[u8; 2048]` buffer. No array is copied merely to build the mask reference.
    ///
    /// # Errors
    ///
    /// Returns an error if a mask bit cannot be resolved to a present non-empty source layer.
    pub fn for_each_update(
        &self,
        kind: LightKind,
        mut visit: impl FnMut(i32, &LightDataLayer),
    ) -> Result<usize, LightMaskReferenceError> {
        let mut mask = self.data_mask(kind);
        let mut updates = 0;
        while mask != 0 {
            let index = mask.trailing_zeros();
            mask &= mask - 1;
            let offset = i32::try_from(index).map_err(|_| {
                LightMaskReferenceError::SectionIndexOverflow {
                    index: index as usize,
                }
            })?;
            let section_y = self.min_light_section_y() + offset;
            let layer = self
                .light
                .layer(kind, section_y)
                .map_err(LightMaskReferenceError::Layer)?;
            let Some(layer) = layer.filter(|layer| !layer.is_empty()) else {
                return Err(LightMaskReferenceError::InconsistentDataBit { kind, section_y });
            };
            visit(section_y, layer);
            updates += 1;
        }
        Ok(updates)
    }
}

fn classify(layer: Option<&LightDataLayer>) -> LightSectionClass {
    match layer {
        None => LightSectionClass::Absent,
        Some(layer) if layer.is_empty() => LightSectionClass::Empty,
        Some(_) => LightSectionClass::Data,
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{ChunkGeneration, ChunkPos};
    use helve_world_contract::SectionBlockPos;

    use crate::{
        ImportedLightSection, InitialChunkLight, LightDataLayer, LightKind, VerticalSectionLattice,
    };

    use super::{InitialLightMaskReference, LightMaskReferenceError, LightSectionClass, classify};

    fn uniform(value: u8) -> LightDataLayer {
        LightDataLayer::homogeneous(value).expect("one valid nibble")
    }

    fn packed_zero() -> LightDataLayer {
        LightDataLayer::from_raw_bytes(vec![0; 2048]).expect("exact packed bytes")
    }

    fn light(
        correct: bool,
        skylight: bool,
        sections: Vec<ImportedLightSection>,
    ) -> InitialChunkLight {
        InitialChunkLight::from_imported(
            ChunkPos { x: 2, z: 3 },
            ChunkGeneration(7),
            VerticalSectionLattice::new(-1, 2).expect("two sections"),
            skylight,
            correct,
            sections,
        )
        .expect("valid light fixture")
    }

    fn section(
        y: i32,
        sky: Option<LightDataLayer>,
        block: Option<LightDataLayer>,
    ) -> ImportedLightSection {
        ImportedLightSection {
            section_y: y,
            block,
            sky,
        }
    }

    #[test]
    fn null_uniform_zero_and_packed_zero_have_distinct_admitted_masks() {
        let zero = uniform(0);
        let raw = packed_zero();
        assert_eq!(classify(None), LightSectionClass::Absent);
        assert_eq!(classify(Some(&zero)), LightSectionClass::Empty);
        assert_eq!(classify(Some(&raw)), LightSectionClass::Data);
        let source = light(
            true,
            true,
            vec![
                section(-2, None, Some(uniform(0))),
                section(-1, Some(uniform(15)), Some(raw)),
                section(0, Some(uniform(0)), None),
                section(1, Some(uniform(5)), Some(uniform(0))),
            ],
        );
        let masks = InitialLightMaskReference::derive(&source).expect("correct source");
        assert_eq!(masks.light_section_count(), 4);
        assert_eq!(masks.min_light_section_y(), -2);
        assert_eq!(masks.data_mask(LightKind::Sky), 0b1010);
        assert_eq!(masks.empty_mask(LightKind::Sky), 0b0100);
        assert_eq!(masks.data_mask(LightKind::Block), 0b0010);
        assert_eq!(masks.empty_mask(LightKind::Block), 0b1001);

        let mut sky_updates = Vec::new();
        assert_eq!(
            masks.for_each_update(LightKind::Sky, |y, layer| {
                sky_updates.push((y, layer.get(SectionBlockPos::new(0, 0, 0).unwrap())));
            }),
            Ok(2)
        );
        assert_eq!(sky_updates, vec![(-1, 15), (1, 5)]);
        let mut block_updates = Vec::new();
        assert_eq!(
            masks.for_each_update(LightKind::Block, |y, layer| {
                block_updates.push((y, layer.get(SectionBlockPos::new(0, 0, 0).unwrap())));
            }),
            Ok(1)
        );
        assert_eq!(block_updates, vec![(-1, 0)]);
    }

    #[test]
    fn correct_no_skylight_dimension_does_not_create_sky_updates() {
        let source = light(
            true,
            false,
            vec![section(-2, Some(uniform(15)), Some(uniform(3)))],
        );
        let masks = InitialLightMaskReference::derive(&source).expect("correct source");
        assert_eq!(masks.data_mask(LightKind::Sky), 0);
        assert_eq!(masks.empty_mask(LightKind::Sky), 0);
        assert_eq!(masks.data_mask(LightKind::Block), 1);
        assert_eq!(
            masks.for_each_update(LightKind::Sky, |_, _| panic!("no sky data")),
            Ok(0)
        );
    }

    #[test]
    fn unverified_source_lighting_is_not_silently_published() {
        let source = light(false, true, vec![section(-2, Some(uniform(15)), None)]);
        assert!(matches!(
            InitialLightMaskReference::derive(&source),
            Err(LightMaskReferenceError::UnverifiedLight)
        ));
    }

    #[test]
    fn complete_sixty_four_section_dimension_uses_sixty_six_mask_bits() {
        let source = InitialChunkLight::from_imported(
            ChunkPos { x: 0, z: 0 },
            ChunkGeneration(1),
            VerticalSectionLattice::new(-32, 64).expect("64 section lattice"),
            true,
            true,
            vec![section(32, Some(uniform(15)), Some(uniform(0)))],
        )
        .expect("upper light sentinel");
        let masks = InitialLightMaskReference::derive(&source).expect("correct source");
        assert_eq!(masks.light_section_count(), 66);
        assert_eq!(masks.data_mask(LightKind::Sky), 1_u128 << 65);
        assert_eq!(masks.empty_mask(LightKind::Block), 1_u128 << 65);
        let mut visited = Vec::new();
        masks
            .for_each_update(LightKind::Sky, |y, _| visited.push(y))
            .unwrap();
        assert_eq!(visited, vec![32]);
    }
}
