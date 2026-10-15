//! Source-admitted initial Minecraft light semantics without a network-shaped world image.
//!
//! Imported light is immutable until an authoritative live light owner exists. The persisted
//! light-correct flag is retained verbatim; neither absence of data nor a false flag may be
//! silently upgraded to freshly computed light. Subsequent gameplay mutations must invalidate
//! or replace this initial image through the one whole-chunk freshness authority.

use helve_types::{ChunkGeneration, ChunkPos};
use helve_world_contract::SectionBlockPos;

use crate::VerticalSectionLattice;

/// Exactly 4096 four-bit cells per 16×16×16 light section.
pub const LIGHT_SECTION_BYTES: usize = 2048;
const MAX_LIVE_SECTIONS: usize = u64::BITS as usize;

/// Error when constructing an exact four-bit light layer.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LightLayerError {
    /// A homogeneous light value must fit in one nibble.
    InvalidIntensity { intensity: u8 },
    /// A packed light layer must have precisely 2048 bytes.
    InvalidByteCount { actual: usize },
}

/// Exact semantic form of Minecraft's DataLayer.
///
/// A homogeneous layer remains one tagged byte until a consumer explicitly requests materialized
/// bytes. Packed layers own precisely 2048 bytes. In particular, a packed all-zero layer remains
/// distinct from a homogeneous empty layer for the source-admitted packet mask classification.
/// No per-cell heap allocation, registry lookup or dynamic dispatch is involved.
#[derive(Debug, Eq, PartialEq)]
pub enum LightDataLayer {
    Homogeneous(u8),
    Packed(Box<[u8; LIGHT_SECTION_BYTES]>),
}

impl LightDataLayer {
    /// Creates a non-materialized homogeneous layer of intensity 0..15.
    ///
    /// # Errors
    ///
    /// Rejects any value larger than 15 instead of truncating it to a nibble.
    pub const fn homogeneous(intensity: u8) -> Result<Self, LightLayerError> {
        if intensity > 15 {
            return Err(LightLayerError::InvalidIntensity { intensity });
        }
        Ok(Self::Homogeneous(intensity))
    }

    /// Moves an exact persisted 2048-byte layer into its final owned representation.
    ///
    /// This cold/import operation does not clone or unpack the incoming cell data.
    ///
    /// # Errors
    ///
    /// Rejects malformed byte lengths; a missing layer is represented by None in its owner.
    pub fn from_raw_bytes(data: Vec<u8>) -> Result<Self, LightLayerError> {
        let actual = data.len();
        if actual != LIGHT_SECTION_BYTES {
            return Err(LightLayerError::InvalidByteCount { actual });
        }
        let boxed = data.into_boxed_slice();
        let packed = boxed
            .try_into()
            .map_err(|_| LightLayerError::InvalidByteCount { actual })?;
        Ok(Self::Packed(packed))
    }

    /// Whether vanilla's unmaterialized-zero DataLayer empty test succeeds.
    ///
    /// An explicitly packed all-zero array is **not** an empty DataLayer for this predicate.
    #[must_use]
    pub const fn is_empty(&self) -> bool {
        matches!(self, Self::Homogeneous(0))
    }

    /// Reads the exact four-bit value at a validated section-local position.
    ///
    /// The section contract already supplies y-major, z-middle, x-minor indexing.
    #[inline]
    #[must_use]
    pub fn get(&self, pos: SectionBlockPos) -> u8 {
        match self {
            Self::Homogeneous(intensity) => *intensity,
            Self::Packed(data) => {
                let index = pos.index();
                (data[index >> 1] >> ((index & 1) * 4)) & 15
            }
        }
    }

    /// Writes the exact raw 2048-byte payload to a caller-owned reusable output buffer.
    ///
    /// Uniform layers expand directly into the supplied buffer. Packed layers perform one bounded
    /// copy. The live representation never materializes merely because it was observed.
    pub fn write_raw_into(&self, output: &mut [u8; LIGHT_SECTION_BYTES]) {
        match self {
            Self::Homogeneous(intensity) => output.fill((*intensity << 4) | *intensity),
            Self::Packed(data) => output.copy_from_slice(data.as_ref()),
        }
    }
}

/// Which semantic light layer a world consumer requests.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LightKind {
    Block,
    Sky,
}

/// One explicitly tagged persisted light-section record, already decoded from NBT.
///
/// The input producer must preserve the difference between an absent tag (None), a homogeneous
/// layer, and an explicitly present 2048-byte layer.
#[derive(Debug)]
pub struct ImportedLightSection {
    pub section_y: i32,
    pub block: Option<LightDataLayer>,
    pub sky: Option<LightDataLayer>,
}

#[derive(Debug, Default)]
struct LightSectionSlot {
    block: Option<LightDataLayer>,
    sky: Option<LightDataLayer>,
}

/// Fail-closed errors when accepting decoded initial light into one chunk column.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ChunkLightError {
    /// This compact chunk kernel supports at most 64 ordinary sections.
    TooManySections { count: usize },
    /// The two sentinel light-section identities could not be represented.
    LightSectionRangeOverflow,
    /// A persisted section lies outside the dimension's one-below/one-above light lattice.
    SectionOutsideLightLattice {
        section_y: i32,
        min_light_section_y: i32,
        section_count: usize,
    },
    /// Two input records claim the same logical light section, including empty records.
    DuplicateSection { section_y: i32 },
}

/// Immutable initial light image for one chunk incarnation.
///
/// This object is a COLD import component, not an independent live lighting engine. It owns
/// exactly (dimension section count + 2) contiguous slots, including the two boundary sections
/// specified by the admitted 26.2 light lattice. Its sparse input is moved into one final boxed
/// array; a temporary u128 bitset detects duplicates without allocating a second directory.
///
/// The persisted correctness flag is preserved, not inferred. Mutations of block/biome state do
/// not pass through this object, so a future composite owner must coordinate invalidation under
/// its existing generation/revision clock before publishing any light.
#[derive(Debug)]
pub struct InitialChunkLight {
    position: ChunkPos,
    generation: ChunkGeneration,
    lattice: VerticalSectionLattice,
    min_light_section_y: i32,
    has_skylight: bool,
    persisted_light_correct: bool,
    slots: Box<[LightSectionSlot]>,
}

impl InitialChunkLight {
    /// Moves decoded, section-addressed light layers into one bounded column.
    ///
    /// When the dimension has no skylight, persisted sky arrays are ignored exactly at the cold
    /// reconstruction boundary rather than becoming live sky state. Missing arrays remain None;
    /// they must never be synthesized as empty or correct by this constructor.
    ///
    /// # Errors
    ///
    /// Rejects excessive/overflowing lattices, out-of-range section records and duplicates.
    pub fn from_imported(
        position: ChunkPos,
        generation: ChunkGeneration,
        lattice: VerticalSectionLattice,
        has_skylight: bool,
        persisted_light_correct: bool,
        sections: Vec<ImportedLightSection>,
    ) -> Result<Self, ChunkLightError> {
        let section_count = lattice.section_count();
        if section_count > MAX_LIVE_SECTIONS {
            return Err(ChunkLightError::TooManySections {
                count: section_count,
            });
        }
        let min_light_section_y = lattice
            .min_section_y()
            .checked_sub(1)
            .ok_or(ChunkLightError::LightSectionRangeOverflow)?;
        let slot_count = section_count + 2;
        let mut slots: Vec<LightSectionSlot> = (0..slot_count)
            .map(|_| LightSectionSlot::default())
            .collect();
        let mut seen = 0_u128;

        for section in sections {
            let index = section
                .section_y
                .checked_sub(min_light_section_y)
                .and_then(|offset| usize::try_from(offset).ok())
                .filter(|&index| index < slot_count)
                .ok_or(ChunkLightError::SectionOutsideLightLattice {
                    section_y: section.section_y,
                    min_light_section_y,
                    section_count: slot_count,
                })?;
            let bit = 1_u128 << index;
            if seen & bit != 0 {
                return Err(ChunkLightError::DuplicateSection {
                    section_y: section.section_y,
                });
            }
            seen |= bit;
            slots[index] = LightSectionSlot {
                block: section.block,
                sky: if has_skylight { section.sky } else { None },
            };
        }

        Ok(Self {
            position,
            generation,
            lattice,
            min_light_section_y,
            has_skylight,
            persisted_light_correct,
            slots: slots.into_boxed_slice(),
        })
    }

    /// Semantic chunk column position for later composite identity checking.
    #[must_use]
    pub const fn position(&self) -> ChunkPos {
        self.position
    }

    /// Exact live incarnation to which this initial light belongs.
    #[must_use]
    pub const fn generation(&self) -> ChunkGeneration {
        self.generation
    }

    /// Validated ordinary block-section lattice; light adds one slot at each endpoint.
    #[must_use]
    pub const fn vertical_lattice(&self) -> VerticalSectionLattice {
        self.lattice
    }

    /// Lowest section Y in the light lattice, one below the ordinary block sections.
    #[must_use]
    pub const fn min_light_section_y(&self) -> i32 {
        self.min_light_section_y
    }

    /// Number of light slots, equal to the dimension's section count plus two.
    #[must_use]
    pub fn light_section_count(&self) -> usize {
        self.slots.len()
    }

    /// The exact persisted isLightOn/lightCorrect flag, with no claim of recomputation.
    #[must_use]
    pub const fn persisted_light_correct(&self) -> bool {
        self.persisted_light_correct
    }

    /// Whether this dimension supports skylight.
    #[must_use]
    pub const fn has_skylight(&self) -> bool {
        self.has_skylight
    }

    /// Borrows a present source layer without allocating or silently manufacturing a missing one.
    ///
    /// # Errors
    ///
    /// Rejects any section outside the full light lattice.
    #[inline]
    pub fn layer(
        &self,
        kind: LightKind,
        section_y: i32,
    ) -> Result<Option<&LightDataLayer>, ChunkLightError> {
        let index = section_y
            .checked_sub(self.min_light_section_y)
            .and_then(|offset| usize::try_from(offset).ok())
            .filter(|&index| index < self.slots.len())
            .ok_or(ChunkLightError::SectionOutsideLightLattice {
                section_y,
                min_light_section_y: self.min_light_section_y,
                section_count: self.slots.len(),
            })?;
        let slot = &self.slots[index];
        Ok(match kind {
            LightKind::Block => slot.block.as_ref(),
            LightKind::Sky => slot.sky.as_ref(),
        })
    }
}

#[cfg(test)]
mod tests {
    use helve_types::{ChunkGeneration, ChunkPos};
    use helve_world_contract::SectionBlockPos;

    use super::{
        ChunkLightError, ImportedLightSection, InitialChunkLight, LIGHT_SECTION_BYTES,
        LightDataLayer, LightKind, LightLayerError,
    };
    use crate::VerticalSectionLattice;

    fn local(x: u8, y: u8, z: u8) -> SectionBlockPos {
        SectionBlockPos::new(x, y, z).expect("test position is within one section")
    }

    #[test]
    fn uniform_layers_validate_nibbles_and_remain_unmaterialized() {
        assert_eq!(
            LightDataLayer::homogeneous(16),
            Err(LightLayerError::InvalidIntensity { intensity: 16 })
        );
        let zero = LightDataLayer::homogeneous(0).expect("zero intensity");
        let seven = LightDataLayer::homogeneous(7).expect("seven intensity");
        assert!(zero.is_empty());
        assert!(!seven.is_empty());
        assert_eq!(seven.get(local(15, 15, 15)), 7);
        let mut bytes = [0_u8; LIGHT_SECTION_BYTES];
        seven.write_raw_into(&mut bytes);
        assert!(bytes.iter().all(|&byte| byte == 0x77));
        zero.write_raw_into(&mut bytes);
        assert!(bytes.iter().all(|&byte| byte == 0));
        assert_eq!(seven, LightDataLayer::Homogeneous(7));
    }

    #[test]
    fn raw_size_and_even_low_odd_high_nibble_order_are_exact() {
        assert_eq!(
            LightDataLayer::from_raw_bytes(vec![0; 2047]),
            Err(LightLayerError::InvalidByteCount { actual: 2047 })
        );
        assert_eq!(
            LightDataLayer::from_raw_bytes(vec![0; 2049]),
            Err(LightLayerError::InvalidByteCount { actual: 2049 })
        );
        let mut raw = vec![0_u8; LIGHT_SECTION_BYTES];
        raw[0] = 0xa3;
        raw[8] = 0x0f;
        raw[128] = 0x4c;
        raw[LIGHT_SECTION_BYTES - 1] = 0xd2;
        let layer = LightDataLayer::from_raw_bytes(raw.clone()).expect("exact layer");
        assert_eq!(layer.get(local(0, 0, 0)), 3);
        assert_eq!(layer.get(local(1, 0, 0)), 10);
        assert_eq!(layer.get(local(0, 0, 1)), 15);
        assert_eq!(layer.get(local(0, 1, 0)), 12);
        assert_eq!(layer.get(local(15, 15, 15)), 13);
        let mut roundtrip = [0_u8; LIGHT_SECTION_BYTES];
        layer.write_raw_into(&mut roundtrip);
        assert_eq!(roundtrip.as_slice(), raw.as_slice());
    }

    #[test]
    fn explicitly_present_zero_bytes_are_not_an_empty_datalayer() {
        let raw_zero =
            LightDataLayer::from_raw_bytes(vec![0; LIGHT_SECTION_BYTES]).expect("exact raw");
        let homogeneous_zero = LightDataLayer::homogeneous(0).expect("valid zero");
        assert!(!raw_zero.is_empty());
        assert!(homogeneous_zero.is_empty());
        assert_eq!(
            raw_zero.get(local(0, 0, 0)),
            homogeneous_zero.get(local(0, 0, 0))
        );
    }

    fn section(section_y: i32, block: bool, sky: bool) -> ImportedLightSection {
        ImportedLightSection {
            section_y,
            block: block.then(|| LightDataLayer::homogeneous(0).expect("valid zero")),
            sky: sky.then(|| LightDataLayer::homogeneous(15).expect("valid full")),
        }
    }

    fn initial_light(
        has_skylight: bool,
        persisted_light_correct: bool,
        sections: Vec<ImportedLightSection>,
    ) -> Result<InitialChunkLight, ChunkLightError> {
        InitialChunkLight::from_imported(
            ChunkPos { x: -5, z: 8 },
            ChunkGeneration(17),
            VerticalSectionLattice::new(-4, 24).expect("Overworld dimension"),
            has_skylight,
            persisted_light_correct,
            sections,
        )
    }

    #[test]
    fn light_lattice_includes_both_boundary_sections_and_preserves_absence() {
        let light = initial_light(
            true,
            true,
            vec![section(-5, true, true), section(20, false, true)],
        )
        .expect("valid endpoints");
        assert_eq!(light.position(), ChunkPos { x: -5, z: 8 });
        assert_eq!(light.generation(), ChunkGeneration(17));
        assert_eq!(light.vertical_lattice().min_section_y(), -4);
        assert_eq!(light.min_light_section_y(), -5);
        assert_eq!(light.light_section_count(), 26);
        assert!(light.has_skylight());
        assert!(light.persisted_light_correct());
        assert!(
            light
                .layer(LightKind::Block, -5)
                .expect("min light")
                .is_some()
        );
        assert!(
            light
                .layer(LightKind::Sky, 20)
                .expect("max light")
                .is_some()
        );
        assert!(
            light
                .layer(LightKind::Block, 20)
                .expect("max light")
                .is_none()
        );
        assert!(
            light
                .layer(LightKind::Sky, 4)
                .expect("missing layer")
                .is_none()
        );
        assert!(matches!(
            light.layer(LightKind::Block, -6),
            Err(ChunkLightError::SectionOutsideLightLattice { .. })
        ));
        assert!(matches!(
            light.layer(LightKind::Sky, 21),
            Err(ChunkLightError::SectionOutsideLightLattice { .. })
        ));
    }

    #[test]
    fn duplicate_and_outside_sections_fail_even_if_empty() {
        assert!(matches!(
            initial_light(
                true,
                false,
                vec![section(0, false, false), section(0, false, false)]
            ),
            Err(ChunkLightError::DuplicateSection { section_y: 0 })
        ));
        assert!(matches!(
            initial_light(true, false, vec![section(-6, false, false)]),
            Err(ChunkLightError::SectionOutsideLightLattice { section_y: -6, .. })
        ));
        assert!(matches!(
            initial_light(true, false, vec![section(21, false, false)]),
            Err(ChunkLightError::SectionOutsideLightLattice { section_y: 21, .. })
        ));
    }

    #[test]
    fn no_skylight_dimension_ignores_stored_sky_and_preserves_false_correctness() {
        let light = initial_light(false, false, vec![section(-4, false, true)])
            .expect("no-skylight dimension");
        assert!(!light.has_skylight());
        assert!(!light.persisted_light_correct());
        assert!(light.layer(LightKind::Sky, -4).expect("in range").is_none());
        assert!(
            light
                .layer(LightKind::Block, -4)
                .expect("in range")
                .is_none()
        );
        assert!(
            light
                .layer(LightKind::Block, -3)
                .expect("missing")
                .is_none()
        );
    }

    #[test]
    fn full_sixty_four_section_lattice_uses_sixty_six_light_slots() {
        let lattice = VerticalSectionLattice::new(-40, 64).expect("max chunk lattice");
        let light = InitialChunkLight::from_imported(
            ChunkPos { x: 0, z: 0 },
            ChunkGeneration(2),
            lattice,
            true,
            true,
            vec![section(-41, true, false), section(24, false, true)],
        )
        .expect("64+2 valid");
        assert_eq!(light.light_section_count(), 66);
        assert!(light.layer(LightKind::Block, -41).expect("first").is_some());
        assert!(light.layer(LightKind::Sky, 24).expect("last").is_some());

        let oversized = VerticalSectionLattice::new(0, 65).expect("shared lattice permits 65");
        assert!(matches!(
            InitialChunkLight::from_imported(
                ChunkPos { x: 0, z: 0 },
                ChunkGeneration(1),
                oversized,
                true,
                true,
                vec![]
            ),
            Err(ChunkLightError::TooManySections { count: 65 })
        ));
    }
}
