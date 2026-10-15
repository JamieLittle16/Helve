//! Immutable source-law reference for one Java 26.2 quart-biome paletted container.
//!
//! This is a COLD publication/reference mechanism, not a resident codec or a second biome
//! authority. It consumes fully resolved *registry ordinal* IDs from the coherent chunk
//! owner, checks the independently qualified registry length, and produces exactly one
//! section's paletted container bytes. It cannot certify the provenance of those IDs.
//!
//! The caller must admit the complete source registry order and outer chunk packet law
//! independently. Do not send a partial section as a standalone protocol packet.

use helve_types::{ChunkPos, ChunkStamp};
use helve_world_contract::{BiomeSection, BlockSection, SectionBiomePos};

use crate::{ChunkSemanticStateError, LiveChunkSemanticState};

const QUART_CELLS: usize = 64;
const WORD_BITS: usize = 64;
const LOCAL_PALETTE_LIMIT: usize = 8;
const MAX_BIOME_IDS: usize = 65_536;

/// Exact source strategy selected from the count of *distinct* semantic quart-biome IDs.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BiomePaletteMode {
    /// Width=0; exactly one global ID and no long-array words.
    SingleValue,
    /// Width=ceil(log2(distinct)) in 1–3; first-use local palette with global IDs.
    LinearLocal,
    /// More than eight distinct values; all 64 cells store global registry IDs.
    RegistryGlobal,
}

/// A caller must never substitute an unknown biome or fabricate a global registry width.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BiomeProjectionError {
    /// Section-Y was outside the coherent resident lattice.
    Section(ChunkSemanticStateError),
    /// Exact externally qualified registry is empty or exceeds the compact ID capacity.
    RegistryCardinality { count: usize },
    /// A resolved biome ordinal is absent from the declared registry.
    RegistryIdOutOfRange { cell: usize, id: u16, count: usize },
}

impl From<ChunkSemanticStateError> for BiomeProjectionError {
    fn from(value: ChunkSemanticStateError) -> Self {
        Self::Section(value)
    }
}

/// A single immutable, stamped biome container reference ready to be appended to the
/// admitted 26.2 section sequence after the block-state container, not a whole packet.
#[derive(Debug, Eq, PartialEq)]
pub struct PackedBiomeSectionReference {
    position: ChunkPos,
    stamp: ChunkStamp,
    section_y: i32,
    mode: BiomePaletteMode,
    storage_bits: u8,
    palette: Box<[u16]>,
    words: Box<[u64]>,
}

impl PackedBiomeSectionReference {
    /// Captures 64 quart cells from the authoritative, generation/revision-stamped owner.
    ///
    /// This is explicitly a reference implementation: it uses one small stack cell array,
    /// builds first-use local palettes deterministically, and packs directly to immutable
    /// non-spanning long-array words. No changes occur on ordinary HOT biome mutation.
    ///
    /// # Errors
    ///
    /// Rejects missing source sections, unknown registry ordinals and invalid registry size.
    ///
    /// # Panics
    ///
    /// Only if one of the 64 explicitly bounded local 4×4×4 coordinates is unexpectedly rejected.
    pub fn derive<S, BlockStorage, BiomeStorage>(
        chunk: &LiveChunkSemanticState<S, BlockStorage, u16, BiomeStorage>,
        section_y: i32,
        registry_count: usize,
    ) -> Result<Self, BiomeProjectionError>
    where
        S: Copy + Eq,
        BlockStorage: BlockSection<S>,
        BiomeStorage: BiomeSection<u16>,
    {
        if registry_count == 0 || registry_count > MAX_BIOME_IDS {
            return Err(BiomeProjectionError::RegistryCardinality {
                count: registry_count,
            });
        }
        let mut cells = [0_u16; QUART_CELLS];
        let mut palette = [0_u16; QUART_CELLS];
        let mut distinct = 0_usize;
        for (index, cell) in cells.iter_mut().enumerate() {
            let x = u8::try_from(index & 3).expect("bounded local quart x");
            let z = u8::try_from((index >> 2) & 3).expect("bounded local quart z");
            let y = u8::try_from((index >> 4) & 3).expect("bounded local quart y");
            let pos = SectionBiomePos::new(x, y, z).expect("bounded quart coordinates");
            let id = chunk.get_biome(section_y, pos)?;
            if usize::from(id) >= registry_count {
                return Err(BiomeProjectionError::RegistryIdOutOfRange {
                    cell: index,
                    id,
                    count: registry_count,
                });
            }
            *cell = id;
            if !palette[..distinct].contains(&id) {
                palette[distinct] = id;
                distinct += 1;
            }
        }
        // Exactly 64 cells have been inspected, so distinct is necessarily nonzero.
        let mode = match distinct {
            1 => BiomePaletteMode::SingleValue,
            2..=LOCAL_PALETTE_LIMIT => BiomePaletteMode::LinearLocal,
            _ => BiomePaletteMode::RegistryGlobal,
        };
        let bits = match mode {
            BiomePaletteMode::SingleValue => 0,
            BiomePaletteMode::LinearLocal => ceil_log2(distinct),
            BiomePaletteMode::RegistryGlobal => ceil_log2(registry_count),
        };
        let words = pack_cells(&cells, &palette[..distinct], mode, bits);
        let palette = match mode {
            BiomePaletteMode::RegistryGlobal => Vec::new(),
            _ => palette[..distinct].to_vec(),
        };
        Ok(Self {
            position: chunk.position(),
            stamp: chunk.stamp(),
            section_y,
            mode,
            storage_bits: u8::try_from(bits).expect("registry size is bounded to 2^16"),
            palette: palette.into_boxed_slice(),
            words: words.into_boxed_slice(),
        })
    }

    /// Verifies the full coherent chunk revision, not only the biome section content.
    #[must_use]
    pub fn is_current_for<S, BlockStorage, BiomeStorage>(
        &self,
        chunk: &LiveChunkSemanticState<S, BlockStorage, u16, BiomeStorage>,
    ) -> bool
    where
        S: Copy + Eq,
        BlockStorage: BlockSection<S>,
        BiomeStorage: BiomeSection<u16>,
    {
        self.position == chunk.position() && self.stamp == chunk.stamp()
    }

    #[must_use]
    pub const fn mode(&self) -> BiomePaletteMode {
        self.mode
    }

    #[must_use]
    pub const fn storage_bits(&self) -> u8 {
        self.storage_bits
    }

    #[must_use]
    pub const fn section_y(&self) -> i32 {
        self.section_y
    }

    /// Global IDs in first-use order for single and linear modes; none for global mode.
    #[must_use]
    pub fn local_palette(&self) -> &[u16] {
        &self.palette
    }

    #[must_use]
    pub fn packed_words(&self) -> &[u64] {
        &self.words
    }

    /// Number of bytes emitted by the exact container-only representation.
    ///
    /// This permits a chunk projector to reserve once for multiple section
    /// containers rather than allocating a temporary byte buffer per section.
    ///
    /// # Panics
    ///
    /// Only if an internally validated palette/word count invariant fails.
    #[must_use]
    pub fn encoded_len(&self) -> usize {
        let palette_bytes = match self.mode {
            BiomePaletteMode::SingleValue => varint_len(u32::from(self.palette[0])),
            BiomePaletteMode::LinearLocal => {
                varint_len(u32::try_from(self.palette.len()).expect("<=8"))
                    + self
                        .palette
                        .iter()
                        .map(|&id| varint_len(u32::from(id)))
                        .sum::<usize>()
            }
            BiomePaletteMode::RegistryGlobal => 0,
        };
        1 + palette_bytes
            + varint_len(u32::try_from(self.words.len()).expect("<=64"))
            + self.words.len() * 8
    }

    /// Appends the exact source-law container bytes into a caller-owned buffer.
    ///
    /// No temporary encoded-container allocation is performed: a caller with
    /// pre-reserved capacity can append all chunk sections into one destination.
    /// The existing reference encoding delegates here, so both paths remain
    /// byte-identical. This is a container only, never an entire Play packet.
    ///
    /// # Panics
    ///
    /// Only if an internally validated palette/word count invariant fails.
    pub fn append_container(&self, bytes: &mut Vec<u8>) {
        bytes.reserve(self.encoded_len());
        bytes.push(self.storage_bits);
        match self.mode {
            BiomePaletteMode::SingleValue => {
                push_varint(bytes, u32::from(self.palette[0]));
            }
            BiomePaletteMode::LinearLocal => {
                push_varint(bytes, u32::try_from(self.palette.len()).expect("<=8"));
                for &id in &self.palette {
                    push_varint(bytes, u32::from(id));
                }
            }
            BiomePaletteMode::RegistryGlobal => {}
        }
        push_varint(bytes, u32::try_from(self.words.len()).expect("<=64"));
        for &word in &self.words {
            bytes.extend_from_slice(&word.to_be_bytes());
        }
    }

    /// Source-law container-only representation: width byte, palette, then VarInt-counted
    /// fixed long-array words in network big-endian order. No enclosing section headers.
    ///
    /// # Panics
    ///
    /// Only if the already-validated reference violates its palette/word bounds.
    #[must_use]
    pub fn encode_container(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(self.encoded_len());
        self.append_container(&mut bytes);
        bytes
    }
}

fn varint_len(mut value: u32) -> usize {
    let mut size = 1;
    while value >= 0x80 {
        value >>= 7;
        size += 1;
    }
    size
}

fn ceil_log2(count: usize) -> usize {
    (usize::BITS - (count - 1).leading_zeros()) as usize
}

fn pack_cells(
    cells: &[u16; QUART_CELLS],
    palette: &[u16],
    mode: BiomePaletteMode,
    bits: usize,
) -> Vec<u64> {
    if bits == 0 {
        return Vec::new();
    }
    let per_word = WORD_BITS / bits;
    let mut words = vec![0_u64; QUART_CELLS.div_ceil(per_word)];
    for (cell, &id) in cells.iter().enumerate() {
        let index = if mode == BiomePaletteMode::RegistryGlobal {
            usize::from(id)
        } else {
            palette
                .iter()
                .position(|&value| value == id)
                .expect("the palette was built from these exact 64 cells")
        };
        words[cell / per_word] |=
            u64::try_from(index).expect("bounded ID") << ((cell % per_word) * bits);
    }
    words
}

fn push_varint(output: &mut Vec<u8>, mut value: u32) {
    while value & !0x7f != 0 {
        output.push(u8::try_from(value & 0x7f).expect("seven bits") | 0x80);
        value >>= 7;
    }
    output.push(u8::try_from(value).expect("remaining seven bits"));
}

#[cfg(test)]
mod tests {
    use helve_types::{BlockPos, ChunkGeneration, ChunkPos};
    use helve_world_contract::{BlockStateFacts, SectionBiomePos, SectionStateFacts};
    use helve_world_reference::{DirectBiomeSection, DirectBlockSection};

    use super::{BiomePaletteMode, BiomeProjectionError, PackedBiomeSectionReference};
    use crate::{ChunkBiomeColumn, LiveChunkCore, LiveChunkSemanticState};

    struct Facts;

    impl BlockStateFacts<u8> for Facts {
        fn facts(&self, state: u8) -> SectionStateFacts {
            SectionStateFacts::new(state != 0, false, false, false)
        }
    }

    type Owner = LiveChunkSemanticState<u8, DirectBlockSection<u8>, u16, DirectBiomeSection<u16>>;

    fn owner() -> Owner {
        let pos = ChunkPos { x: 4, z: -2 };
        let blocks = LiveChunkCore::new(
            pos,
            ChunkGeneration(4),
            -1,
            vec![DirectBlockSection::filled(0, &Facts)],
        )
        .expect("blocks");
        let biomes = ChunkBiomeColumn::new(
            pos,
            ChunkGeneration(4),
            -1,
            vec![DirectBiomeSection::filled(2)],
        )
        .expect("biomes");
        LiveChunkSemanticState::from_parts(blocks, biomes).expect("one owner")
    }

    fn quart_index(index: usize) -> SectionBiomePos {
        SectionBiomePos::new(
            u8::try_from(index & 3).expect("x"),
            u8::try_from((index >> 4) & 3).expect("y"),
            u8::try_from((index >> 2) & 3).expect("z"),
        )
        .expect("quart")
    }

    #[test]
    fn uniform_source_id_has_no_storage_words_or_local_count_varint() {
        let state = owner();
        let encoded = PackedBiomeSectionReference::derive(&state, -1, 16).expect("uniform");
        assert_eq!(encoded.mode(), BiomePaletteMode::SingleValue);
        assert_eq!(encoded.storage_bits(), 0);
        assert_eq!(encoded.local_palette(), &[2]);
        assert!(encoded.packed_words().is_empty());
        assert_eq!(encoded.encode_container(), [0, 2, 0]);
        assert!(encoded.is_current_for(&state));
    }

    #[test]
    fn one_two_and_three_bit_local_palette_packs_all_cells_nonspanning() {
        for unique in [2_u16, 3, 4, 5, 8] {
            let mut state = owner();
            for i in 0..64 {
                let id = 1 + u16::try_from((i * 5 + (i / 7)) % usize::from(unique)).unwrap();
                state.replace_biome(-1, quart_index(i), id).expect("valid");
            }
            let encoded = PackedBiomeSectionReference::derive(&state, -1, 256).unwrap();
            assert_eq!(encoded.mode(), BiomePaletteMode::LinearLocal);
            let bits = usize::from(encoded.storage_bits());
            assert_eq!(
                bits,
                (usize::BITS - (usize::from(unique) - 1).leading_zeros()) as usize
            );
            let per_word = 64 / bits;
            assert_eq!(encoded.packed_words().len(), 64usize.div_ceil(per_word));
            for i in 0..64 {
                let word = encoded.packed_words()[i / per_word];
                let palette_index =
                    usize::try_from((word >> ((i % per_word) * bits)) & ((1 << bits) - 1)).unwrap();
                let actual = encoded.local_palette()[palette_index];
                assert_eq!(actual, state.get_biome(-1, quart_index(i)).unwrap());
            }
            let wire = encoded.encode_container();
            assert_eq!(wire[0], encoded.storage_bits());
            assert_eq!(usize::from(wire[1]), encoded.local_palette().len());
        }
    }

    #[test]
    fn more_than_eight_values_switches_to_registry_global_ids_not_local_indices() {
        let mut state = owner();
        for i in 0..64 {
            state
                .replace_biome(-1, quart_index(i), u16::try_from(i + 31).expect("test id"))
                .expect("valid");
        }
        let projected = PackedBiomeSectionReference::derive(&state, -1, 127).unwrap();
        assert_eq!(projected.mode(), BiomePaletteMode::RegistryGlobal);
        assert_eq!(projected.storage_bits(), 7);
        assert!(projected.local_palette().is_empty());
        let per_word = 64 / 7;
        assert_eq!(projected.packed_words().len(), 64usize.div_ceil(per_word));
        for i in 0..64 {
            let word = projected.packed_words()[i / per_word];
            assert_eq!(
                (word >> ((i % per_word) * 7)) & 127,
                u64::try_from(i + 31).unwrap(),
            );
        }
        let wire = projected.encode_container();
        assert_eq!(wire[0], 7);
        assert_eq!(usize::from(wire[1]), projected.packed_words().len());
        assert_eq!(wire.len(), 2 + projected.packed_words().len() * 8);
    }

    #[test]
    fn encoded_length_and_reused_destination_match_all_palette_modes() {
        let mut destination = Vec::with_capacity(4096);
        destination.extend_from_slice(&[0xee, 0x0f]);
        let allocation = destination.as_ptr();
        for unique in [1_usize, 3, 9] {
            let mut state = owner();
            for index in 0..64 {
                let id = 130 + u16::try_from(index % unique).expect("bounded ID");
                state
                    .replace_biome(-1, quart_index(index), id)
                    .expect("valid source biome");
            }
            let projected = PackedBiomeSectionReference::derive(&state, -1, 256).unwrap();
            let stand_alone = projected.encode_container();
            assert_eq!(projected.encoded_len(), stand_alone.len());
            if unique == 1 {
                assert_eq!(stand_alone, [0, 0x82, 0x01, 0]);
            }
            let before = destination.len();
            projected.append_container(&mut destination);
            assert_eq!(&destination[before..], stand_alone.as_slice());
            assert_eq!(&destination[..2], &[0xee, 0x0f]);
            assert_eq!(
                destination.as_ptr(),
                allocation,
                "no reallocation with capacity"
            );
        }
    }

    #[test]
    fn invalid_registry_ids_and_section_fail_before_encoding() {
        let state = owner();
        assert_eq!(
            PackedBiomeSectionReference::derive(&state, -1, 2),
            Err(BiomeProjectionError::RegistryIdOutOfRange {
                cell: 0,
                id: 2,
                count: 2
            })
        );
        assert_eq!(
            PackedBiomeSectionReference::derive(&state, -1, 0),
            Err(BiomeProjectionError::RegistryCardinality { count: 0 })
        );
        assert_eq!(
            PackedBiomeSectionReference::derive(&state, -1, 65_537),
            Err(BiomeProjectionError::RegistryCardinality { count: 65_537 })
        );
        assert!(matches!(
            PackedBiomeSectionReference::derive(&state, 17, 16),
            Err(BiomeProjectionError::Section(_))
        ));
    }

    #[test]
    fn shared_revision_invalidates_after_block_or_biome_change() {
        let mut state = owner();
        let before = PackedBiomeSectionReference::derive(&state, -1, 16).unwrap();
        state
            .replace_block(
                BlockPos {
                    x: 64,
                    y: -16,
                    z: -32,
                },
                1,
                &Facts,
            )
            .unwrap();
        assert!(!before.is_current_for(&state));
        let after = PackedBiomeSectionReference::derive(&state, -1, 16).unwrap();
        assert!(after.is_current_for(&state));
        state.replace_biome(-1, quart_index(0), 5).unwrap();
        assert!(!after.is_current_for(&state));
    }
}
