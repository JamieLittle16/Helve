//! Target-owned 26.2 block-state paletted-container reference (COLD).
//!
//! Inputs are exactly 4096 resolved global state IDs in y-z-x order, read
//! through one coherent caller borrow. This is not live storage or a packet.
//! R2C block-wire source admission and stock-client qualification are pending.

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
            let per_word = 64 / bits;
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
        1 + palette_bytes
            + varint_len(u32::try_from(self.words.len()).expect("<=4096"))
            + self.words.len() * 8
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
        push_varint(output, u32::try_from(self.words.len()).expect("<=4096"));
        for &word in &self.words {
            output.extend_from_slice(&word.to_be_bytes());
        }
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
        let count = read_varint(bytes, &mut cursor);
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
                    (words[i / per_word] >> ((i % per_word) * width))
                        & ((1_u64 << width) - 1),
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
        assert_eq!(packed.encode_container(), [0, 251, 1, 0]);
        assert_eq!(decode(&packed.encode_container(), 32_366), vec![251; CELLS]);
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
            let expected_width = (usize::BITS - (distinct - 1).leading_zeros()) as u8;
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
        let maximum = PackedBlockContainer::derive(65_536, |i| {
            u16::try_from(i % 257).unwrap()
        })
        .unwrap();
        assert_eq!(maximum.storage_bits(), 16);
        assert_eq!(decode(&maximum.encode_container(), 65_536).len(), CELLS);
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
