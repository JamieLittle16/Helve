//! Target-owned 26.2 block-state paletted-container reference (COLD).
//!
//! Inputs are exactly 4096 resolved global state IDs in y-z-x order, read
//! through one coherent caller borrow. This is not live storage or a packet.
//! R2C block-wire source admission and stock-client qualification are pending.
//! 26.2 uses fixed-size packed-word data, without a VarInt word-count prefix.

const CELLS: usize = 4096;
const LOCAL_MAX: usize = 256;
const MAX_IDS: usize = 65_536;

/// Fresh, canonical palette representation, not a resident storage policy.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BlockPaletteMode {
    /// One state; no stored bit words.
    Single,
    /// Four to eight bits; first-use palette order.
    Local,
    /// Global registry IDs stored directly, without an entry palette.
    Global,
}

/// Invalid input cannot be promoted into an encoded container.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BlockPaletteError {
    /// Declared global-state universe is empty or too large.
    RegistryCardinality { count: usize },
    /// One source identity does not exist in that universe.
    UnknownState { cell: usize, id: u16, count: usize },
}

/// A source-independent immutable, one-section reference for target projection.
#[derive(Debug, Eq, PartialEq)]
pub struct PackedBlockContainer {
    mode: BlockPaletteMode,
    bits: u8,
    palette: Box<[u16]>,
    words: Box<[u64]>,
}

impl PackedBlockContainer {
    /// Builds a canonical reference using exactly one read of each source cell.
    ///
    /// The caller must ensure the callback reads the same immutable section.
    /// No intermediate 4096-cell heap copy or runtime registry lookup is needed.
    ///
    /// # Errors
    ///
    /// Rejects invalid registry cardinalities and global IDs.
    ///
    /// # Panics
    ///
    /// Only on an internal bounded-index invariant violation or callback panic.
    pub fn derive(
        registry_count: usize,
        mut state_at: impl FnMut(usize) -> u16,
    ) -> Result<Self, BlockPaletteError> {
        if registry_count == 0 || registry_count > MAX_IDS {
            return Err(BlockPaletteError::RegistryCardinality {
                count: registry_count,
            });
        }
        // Reference-only stack scratch. No representation is retained in the world.
        let mut global = [0_u16; CELLS];
        let mut local = [0_u16; CELLS];
        let mut palette = Vec::new();
        let mut global_mode = false;
        for i in 0..CELLS {
            let id = state_at(i);
            if usize::from(id) >= registry_count {
                return Err(BlockPaletteError::UnknownState {
                    cell: i,
                    id,
                    count: registry_count,
                });
            }
            global[i] = id;
            if global_mode {
                continue;
            }
            if let Some(slot) = palette.iter().position(|&candidate| candidate == id) {
                local[i] = u16::try_from(slot).expect("at most 256 palette positions");
            } else if palette.len() == LOCAL_MAX {
                global_mode = true;
            } else {
                local[i] = u16::try_from(palette.len()).expect("at most 256 palette positions");
                palette.push(id);
            }
        }
        let mode = if global_mode {
            BlockPaletteMode::Global
        } else if palette.len() == 1 {
            BlockPaletteMode::Single
        } else {
            BlockPaletteMode::Local
        };
        let bits = match mode {
            BlockPaletteMode::Single => 0,
            BlockPaletteMode::Local => ceil_log2(palette.len()).max(4),
            BlockPaletteMode::Global => ceil_log2(registry_count),
        };
        let words = if bits == 0 {
            Vec::new()
        } else {
            let per_word = 64_usize.checked_div(bits).expect("positive palette width");
            let mut words = vec![0_u64; CELLS.div_ceil(per_word)];
            for i in 0..CELLS {
                let value = if global_mode { global[i] } else { local[i] };
                words[i / per_word] |= u64::from(value) << ((i % per_word) * bits);
            }
            words
        };
        if global_mode {
            palette.clear();
        }
        Ok(Self {
            mode,
            bits: u8::try_from(bits).expect("registry limit 65536"),
            palette: palette.into_boxed_slice(),
            words: words.into_boxed_slice(),
        })
    }

    /// Selected reference representation.
    #[must_use]
    pub const fn mode(&self) -> BlockPaletteMode {
        self.mode
    }

    /// Width of each packed entry, or zero for uniform data.
    #[must_use]
    pub const fn storage_bits(&self) -> u8 {
        self.bits
    }

    /// Ordered global IDs; empty in global-palette mode.
    #[must_use]
    pub fn local_palette(&self) -> &[u16] {
        &self.palette
    }

    /// Packed non-spanning values, each in a 64-bit word.
    #[must_use]
    pub fn packed_words(&self) -> &[u64] {
        &self.words
    }

    /// Exact byte count of this isolated container candidate.
    ///
    /// # Panics
    ///
    /// Only if an internal palette/word bound fails.
    #[must_use]
    pub fn encoded_len(&self) -> usize {
        let palette_bytes = match self.mode {
            BlockPaletteMode::Single => varint_len(u32::from(self.palette[0])),
            BlockPaletteMode::Local => {
                varint_len(u32::try_from(self.palette.len()).expect("<=256"))
                    + self
                        .palette
                        .iter()
                        .map(|&id| varint_len(u32::from(id)))
                        .sum::<usize>()
            }
            BlockPaletteMode::Global => 0,
        };
        // Client PalettedContainer.Data.read consumes exactly the implied
        // number of longs; an encoded word count desynchronizes the section.
        1 + palette_bytes + self.words.len() * 8
    }

    /// Appends isolated container bytes to a reusable caller-owned destination.
    ///
    /// No per-container encoded byte allocation. Do not publish this as a packet.
    ///
    /// # Panics
    ///
    /// Only if an internal palette/word bound fails.
    pub fn append_container(&self, output: &mut Vec<u8>) {
        output.reserve(self.encoded_len());
        output.push(self.bits);
        match self.mode {
            BlockPaletteMode::Single => push_varint(output, u32::from(self.palette[0])),
            BlockPaletteMode::Local => {
                push_varint(output, u32::try_from(self.palette.len()).expect("<=256"));
                for &id in &self.palette {
                    push_varint(output, u32::from(id));
                }
            }
            BlockPaletteMode::Global => {}
        }
        // Wire data is a fixed-size long array, not a VarInt-prefixed list.
        for &word in &self.words {
            output.extend_from_slice(&word.to_be_bytes());
        }
    }

    /// Appends one COLD section-sequence candidate in target-owned field order.
    ///
    /// Prefixes the verified non-air and counted-fluid shorts before the block
    /// container and delegates the biome-container append to the already-built
    /// source reference. This remains an isolated candidate: enclosing chunk
    /// packet law, numeric biome registry identity and world-entry publication
    /// are not yet independently qualified. Never publish this as a Play packet.
    ///
    /// Both palette references and summary counts must be validated by the
    /// caller before invoking this method, so source validation is transactional
    /// against the caller-owned output. An exact upfront reserve avoids a
    /// separate encoded buffer and permits reusable whole-chunk scratch.
    ///
    /// # Panics
    ///
    /// Only if an internal packed-word invariant fails or the trusted
    /// `append_biome` callback emits a length different from `biome_bytes`.
    pub fn append_section_candidate(
        &self,
        non_air_count: u16,
        fluid_count: u16,
        biome_bytes: usize,
        output: &mut Vec<u8>,
        append_biome: impl FnOnce(&mut Vec<u8>),
    ) {
        output.reserve(4 + self.encoded_len() + biome_bytes);
        output.extend_from_slice(&non_air_count.to_be_bytes());
        output.extend_from_slice(&fluid_count.to_be_bytes());
        self.append_container(output);
        let biome_start = output.len();
        append_biome(output);
        debug_assert_eq!(output.len() - biome_start, biome_bytes);
    }

    /// Allocating standalone reference, permanently available for differential tests.
    ///
    /// # Panics
    ///
    /// Only if an internal palette/word bound fails.
    #[must_use]
    pub fn encode_container(&self) -> Vec<u8> {
        let mut output = Vec::with_capacity(self.encoded_len());
        self.append_container(&mut output);
        output
    }
}

fn ceil_log2(count: usize) -> usize {
    (usize::BITS - (count - 1).leading_zeros()) as usize
}

fn varint_len(mut value: u32) -> usize {
    let mut len = 1;
    while value >= 128 {
        value >>= 7;
        len += 1;
    }
    len
}

fn push_varint(output: &mut Vec<u8>, mut value: u32) {
    while value >= 128 {
        output.push(u8::try_from(value & 127).expect("low 7 bits") | 128);
        value >>= 7;
    }
    output.push(u8::try_from(value).expect("high 7 bits"));
}

#[cfg(test)]
mod tests {
    use super::{BlockPaletteError, BlockPaletteMode, CELLS, PackedBlockContainer};

    // Independent byte-level decoding oracle, not a mirror of the packing algorithm.
    fn decode(bytes: &[u8], registry_count: usize) -> Vec<u16> {
        fn read_varint(bytes: &[u8], index: &mut usize) -> usize {
            let mut value = 0_usize;
            let mut shift = 0;
            loop {
                let byte = bytes[*index];
                *index += 1;
                value |= usize::from(byte & 127) << shift;
                if byte < 128 {
                    break value;
                }
                shift += 7;
            }
        }
        let width = usize::from(bytes[0]);
        let mut cursor = 1;
        let palette = if width == 0 {
            vec![u16::try_from(read_varint(bytes, &mut cursor)).unwrap()]
        } else if width <= 8 {
            let count = read_varint(bytes, &mut cursor);
            (0..count)
                .map(|_| u16::try_from(read_varint(bytes, &mut cursor)).unwrap())
                .collect::<Vec<_>>()
        } else {
            Vec::new()
        };
        let count = if width == 0 {
            0
        } else {
            CELLS.div_ceil(64 / width)
        };
        assert_eq!(bytes.len() - cursor, count * 8);
        let words: Vec<u64> = bytes[cursor..]
            .chunks_exact(8)
            .map(|chunk| u64::from_be_bytes(chunk.try_into().unwrap()))
            .collect();
        if width == 0 {
            assert_eq!(words.len(), 0);
            return vec![palette[0]; CELLS];
        }
        let per_word = 64 / width;
        assert_eq!(words.len(), CELLS.div_ceil(per_word));
        (0..CELLS)
            .map(|i| {
                let value = usize::try_from(
                    (words[i / per_word] >> ((i % per_word) * width)) & ((1_u64 << width) - 1),
                )
                .unwrap();
                if width <= 8 {
                    palette[value]
                } else {
                    assert!(value < registry_count);
                    u16::try_from(value).unwrap()
                }
            })
            .collect()
    }

    #[test]
    fn uniform_encoding_is_zero_bits_and_no_words() {
        let mut calls = 0;
        let packed = PackedBlockContainer::derive(32_366, |_| {
            calls += 1;
            251
        })
        .unwrap();
        assert_eq!(calls, CELLS);
        assert_eq!(packed.mode(), BlockPaletteMode::Single);
        assert_eq!(packed.local_palette(), &[251]);
        assert!(packed.packed_words().is_empty());
        assert_eq!(packed.encode_container(), [0, 251, 1]);
        assert_eq!(decode(&packed.encode_container(), 32_366), vec![251; CELLS]);
    }

    #[test]
    fn fixed_size_words_follow_palette_without_a_length_varint() {
        // Two-item palette: one width byte, count=2, two global IDs,
        // immediately followed by 256 packed 4-bit longs (4096/16).
        // A VarInt(256) here would be [0x80, 0x02] and the actual
        // client would misinterpret it as the start of the packed longs.
        let packed = PackedBlockContainer::derive(32_366, |i| {
            if i & 1 == 0 { 1 } else { 2 }
        })
        .unwrap();
        assert_eq!(packed.storage_bits(), 4);
        assert_eq!(packed.local_palette(), &[1, 2]);
        let encoded = packed.encode_container();
        assert_eq!(&encoded[..4], &[4, 2, 1, 2]);
        assert_eq!(packed.packed_words().len(), 256);
        assert_eq!(encoded.len(), 4 + 256 * 8);
        assert_eq!(&encoded[4..12], &0x1010_1010_1010_1010_u64.to_be_bytes());
        assert_eq!(decode(&encoded, 32_366)[1], 2);

        // A global palette has no local count/entries and likewise
        // starts directly with packed longs after the width byte.
        let global = PackedBlockContainer::derive(32_366, |i| {
            u16::try_from(i % 257).unwrap()
        })
        .unwrap();
        assert_eq!(global.mode(), BlockPaletteMode::Global);
        assert_eq!(global.encode_container().len(), 1 + global.packed_words().len() * 8);
    }

    #[test]
    fn every_local_palette_threshold_roundtrips() {
        for &distinct in &[2_usize, 16, 17, 32, 33, 64, 128, 129, 256] {
            let cells: Vec<u16> = (0..CELLS)
                .map(|i| u16::try_from(300 + i % distinct).unwrap())
                .collect();
            let packed = PackedBlockContainer::derive(32_366, |i| cells[i]).unwrap();
            assert_eq!(packed.mode(), BlockPaletteMode::Local);
            assert_eq!(packed.local_palette().len(), distinct);
            let expected_width =
                u8::try_from(usize::BITS - (distinct - 1).leading_zeros()).unwrap();
            assert_eq!(packed.storage_bits(), expected_width.max(4));
            assert_eq!(decode(&packed.encode_container(), 32_366), cells);
        }
    }

    #[test]
    fn global_palette_uses_original_registry_values() {
        let cells: Vec<u16> = (0..CELLS)
            .map(|i| u16::try_from(1200 + (i * 17) % 1021).unwrap())
            .collect();
        let packed = PackedBlockContainer::derive(32_366, |i| cells[i]).unwrap();
        assert_eq!(packed.mode(), BlockPaletteMode::Global);
        assert_eq!(packed.storage_bits(), 15);
        assert!(packed.local_palette().is_empty());
        assert_eq!(decode(&packed.encode_container(), 32_366), cells);
        let maximum =
            PackedBlockContainer::derive(65_536, |i| u16::try_from(i % 257).unwrap()).unwrap();
        assert_eq!(maximum.storage_bits(), 16);
        assert_eq!(decode(&maximum.encode_container(), 65_536).len(), CELLS);
    }

    #[test]
    fn section_candidate_writes_two_big_endian_shorts_then_containers() {
        let packed = PackedBlockContainer::derive(32_366, |_| 251).unwrap();
        let mut output = vec![0x99];
        let before = output.len();
        packed.append_section_candidate(4096, 17, 3, &mut output, |bytes| {
            bytes.extend_from_slice(&[0, 5, 0]);
        });
        assert_eq!(&output[..before], &[0x99]);
        assert_eq!(&output[before..before + 4], &[0x10, 0x00, 0x00, 0x11]);
        assert_eq!(
            &output[before + 4..before + 4 + packed.encoded_len()],
            packed.encode_container()
        );
        assert_eq!(&output[before + 4 + packed.encoded_len()..], &[0, 5, 0]);

        // A pre-reserved multi-section destination is never reallocated.
        let mut reserved = Vec::with_capacity(output.len() * 2);
        let pointer = reserved.as_ptr();
        for _ in 0..2 {
            packed.append_section_candidate(12, 0, 3, &mut reserved, |bytes| {
                bytes.extend_from_slice(&[0, 5, 0]);
            });
        }
        assert_eq!(reserved.as_ptr(), pointer);
    }

    #[test]
    fn malformed_state_domain_fails_before_publication() {
        for &count in &[0, 65_537] {
            assert_eq!(
                PackedBlockContainer::derive(count, |_| panic!("must not read")),
                Err(BlockPaletteError::RegistryCardinality { count })
            );
        }
        assert_eq!(
            PackedBlockContainer::derive(3, |i| if i == 511 { 3 } else { 2 }),
            Err(BlockPaletteError::UnknownState {
                cell: 511,
                id: 3,
                count: 3,
            })
        );
    }

    #[test]
    fn append_into_preallocated_chunk_buffer_does_not_reallocate() {
        let mut target = Vec::with_capacity(64_000);
        target.extend_from_slice(&[0x11, 0x22]);
        let address = target.as_ptr();
        for &distinct in &[1_usize, 16, 17, 256, 257] {
            let packed = PackedBlockContainer::derive(32_366, |i| {
                u16::try_from(300 + i % distinct).unwrap()
            })
            .unwrap();
            let expected = packed.encode_container();
            assert_eq!(packed.encoded_len(), expected.len());
            let from = target.len();
            packed.append_container(&mut target);
            assert_eq!(&target[from..], expected);
            assert_eq!(&target[..2], &[0x11, 0x22]);
            assert_eq!(target.as_ptr(), address);
        }
    }
}
