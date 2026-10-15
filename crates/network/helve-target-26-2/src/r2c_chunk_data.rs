//! COLD, target-owned 26.2 chunk-data field candidates.
//!
//! These are *not* Play packet bodies: caller must separately establish the
//! enclosing packet identity, chunk coordinates, block entities, light payload,
//! numeric biome registry ID authority and complete publication ordering.
//! No resident copy, packet replay, reflection, or HOT-world operation exists here.

const HEIGHTMAP_COLUMNS: usize = 256;
const MAX_HEIGHT: u16 = 1024;
const MIN_HEIGHT: u16 = 16;
const HEIGHTMAP_WIRE_IDS: [u8; 3] = [1, 4, 5];

/// Rejected exact 26.2 heightmap-map candidate, before any bytes are written.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum HeightmapMapError {
    /// The semantic dimension has no supported section-height mapping.
    InvalidDimensionHeight { blocks: u16 },
    /// Each of the three maps must have the source-required word count.
    WrongWordCount {
        map: usize,
        expected: usize,
        actual: usize,
    },
    /// A height is outside the dimension or an unused long bit was set.
    InvalidWordValue { map: usize, word: usize },
}

/// A length-delimited section byte sequence was rejected transactionally.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SectionLengthError<E> {
    /// The caller limit cannot be represented by the target length codec.
    InvalidLimit { max_bytes: usize },
    /// A source section was rejected; no output suffix remains.
    Source(E),
    /// Encoded data exceeded the externally selected bound.
    ExceedsLimit { actual: usize, max_bytes: usize },
    /// A valid chunk contains at least one section.
    Empty,
}

fn length_as_varint(mut length: u32) -> ([u8; 5], usize) {
    let mut bytes = [0_u8; 5];
    let mut count = 0;
    loop {
        let mut next = (length & 0x7f) as u8;
        length >>= 7;
        if length != 0 {
            next |= 0x80;
        }
        bytes[count] = next;
        count += 1;
        if length == 0 {
            return (bytes, count);
        }
    }
}

/// Append the three client heightmap (type-ID, long-array) field candidates.
///
/// Uses source-bound Heightmap.Types 1/4/5 and non-spanning packed longs.
/// Validate all three arrays before the first output byte. No temporary
/// encoded map is allocated. Still not a complete chunk Play packet.
///
/// # Errors
///
/// Rejects dimensions, array counts, stored values or padding that cannot
/// describe the exact target heightmap source law.
///
/// # Panics
///
/// Only if the compile-time source-bounded heightmap word-count/width
/// invariants or allocation capacity cannot be honored.
pub fn append_heightmap_map_candidate(
    output: &mut Vec<u8>,
    dimension_height_blocks: u16,
    map_words: [&[u64]; 3],
) -> Result<(), HeightmapMapError> {
    let height = usize::from(dimension_height_blocks);
    if !(usize::from(MIN_HEIGHT)..=usize::from(MAX_HEIGHT)).contains(&height)
        || !height.is_multiple_of(16)
    {
        return Err(HeightmapMapError::InvalidDimensionHeight {
            blocks: dimension_height_blocks,
        });
    }
    let width = usize::try_from((u32::from(dimension_height_blocks)).ilog2() + 1)
        .expect("heightmap width <= 11");
    let per_word = 64 / width;
    let expected = HEIGHTMAP_COLUMNS.div_ceil(per_word);
    let mask = (1_u64 << width) - 1;

    // Validate before writing; leaves the caller prefix unchanged on failure.
    for (map, words) in map_words.iter().enumerate() {
        if words.len() != expected {
            return Err(HeightmapMapError::WrongWordCount {
                map,
                expected,
                actual: words.len(),
            });
        }
        for (word_index, &word) in words.iter().enumerate() {
            for lane in 0..per_word {
                let entry = word_index * per_word + lane;
                let raw = (word >> (lane * width)) & mask;
                if (entry < HEIGHTMAP_COLUMNS && raw > u64::from(dimension_height_blocks))
                    || (entry >= HEIGHTMAP_COLUMNS && raw != 0)
                {
                    return Err(HeightmapMapError::InvalidWordValue {
                        map,
                        word: word_index,
                    });
                }
            }
            // High word bits beyond complete non-spanning storage lanes.
            let occupied = per_word * width;
            if occupied < 64 && (word >> occupied) != 0 {
                return Err(HeightmapMapError::InvalidWordValue {
                    map,
                    word: word_index,
                });
            }
        }
    }

    // At the 1024-block cap, each array is <=52 longs, hence its
    // canonical length and each enum ID are single-byte VarInts.
    debug_assert!(expected <= 127);
    output.reserve(1 + 3 * (2 + expected * 8));
    output.push(3);
    for (wire_id, words) in HEIGHTMAP_WIRE_IDS.into_iter().zip(map_words) {
        output.push(wire_id);
        output.push(u8::try_from(words.len()).expect("bounded map word count"));
        for &word in words {
            output.extend_from_slice(&word.to_be_bytes());
        }
    }
    Ok(())
}

/// Append a VarInt-length-prefixed complete section sequence without a second
/// serialized section buffer.
///
/// The callback writes directly to caller scratch. After success, insert the
/// canonical prefix with one in-place move. Source/length/empty errors restore
/// the exact caller prefix. The externally selected uncompressed bound is not
/// automatically target Play packet-size authority.
///
/// # Errors
///
/// The destination length and bytes remain unchanged on every rejection.
///
/// # Panics
///
/// Only if a successful source append violates the caller's Vec capacity
/// invariants during the final in-place VarInt prefix insertion.
pub fn append_length_prefixed_sections<E>(
    output: &mut Vec<u8>,
    max_bytes: usize,
    append_sections: impl FnOnce(&mut Vec<u8>) -> Result<(), E>,
) -> Result<(), SectionLengthError<E>> {
    if max_bytes == 0 || max_bytes > u32::MAX as usize {
        return Err(SectionLengthError::InvalidLimit { max_bytes });
    }
    let before = output.len();
    if let Err(source) = append_sections(output) {
        output.truncate(before);
        return Err(SectionLengthError::Source(source));
    }
    let section_bytes = output.len() - before;
    if section_bytes == 0 {
        output.truncate(before);
        return Err(SectionLengthError::Empty);
    }
    if section_bytes > max_bytes {
        output.truncate(before);
        return Err(SectionLengthError::ExceedsLimit {
            actual: section_bytes,
            max_bytes,
        });
    }
    let (length, count) =
        length_as_varint(u32::try_from(section_bytes).expect("validated <= u32::MAX"));
    let end = output.len();
    output.resize(end + count, 0);
    output.copy_within(before..end, before + count);
    output[before..before + count].copy_from_slice(&length[..count]);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        HeightmapMapError, SectionLengthError, append_heightmap_map_candidate,
        append_length_prefixed_sections,
    };

    #[test]
    fn exact_three_map_field_sequence_is_big_endian() {
        // 32 blocks -> width 6 -> 10 heights per long -> 26 longs/map.
        let words = [0_u64; 26];
        let mut out = vec![0xAB, 0xCD];
        append_heightmap_map_candidate(&mut out, 32, [&words, &words, &words]).unwrap();
        assert_eq!(out.len(), 2 + 1 + 3 * (2 + 26 * 8));
        assert_eq!(&out[..5], &[0xAB, 0xCD, 3, 1, 26]);
        let second = 2 + 1 + (2 + 26 * 8);
        let third = second + (2 + 26 * 8);
        assert_eq!(&out[second..second + 2], &[4, 26]);
        assert_eq!(&out[third..third + 2], &[5, 26]);

        let mut nonzero = [0_u64; 26];
        nonzero[0] = 32 | (17_u64 << 6);
        let mut actual = Vec::new();
        append_heightmap_map_candidate(&mut actual, 32, [&nonzero, &words, &words]).unwrap();
        assert_eq!(&actual[3..11], &nonzero[0].to_be_bytes());
    }

    #[test]
    fn invalid_later_map_never_mutates_prefix() {
        let words = [0_u64; 26];
        let short = [0_u64; 25];
        let mut out = vec![0xAA, 0xBB];
        assert_eq!(
            append_heightmap_map_candidate(&mut out, 32, [&words, &words, &short]),
            Err(HeightmapMapError::WrongWordCount {
                map: 2,
                expected: 26,
                actual: 25
            })
        );
        let mut invalid = words;
        invalid[3] = 33;
        assert_eq!(
            append_heightmap_map_candidate(&mut out, 32, [&words, &invalid, &words]),
            Err(HeightmapMapError::InvalidWordValue { map: 1, word: 3 })
        );
        invalid[3] = 0;
        invalid[25] = 1_u64 << 63;
        assert_eq!(
            append_heightmap_map_candidate(&mut out, 32, [&words, &invalid, &words]),
            Err(HeightmapMapError::InvalidWordValue { map: 1, word: 25 })
        );
        assert_eq!(
            append_heightmap_map_candidate(&mut out, 17, [&words, &words, &words]),
            Err(HeightmapMapError::InvalidDimensionHeight { blocks: 17 })
        );
        assert_eq!(out, [0xAA, 0xBB]);
    }

    #[test]
    fn length_prefix_is_canonical_varint_and_reuses_destination() {
        let mut out = Vec::with_capacity(4096);
        out.push(0xF7);
        let allocation = out.as_ptr();
        append_length_prefixed_sections(&mut out, 3000, |bytes| {
            bytes.extend_from_slice(&[0xBB; 128]);
            Ok::<(), ()>(())
        })
        .unwrap();
        assert_eq!(&out[..4], &[0xF7, 0x80, 0x01, 0xBB]);
        assert_eq!(out.len(), 1 + 2 + 128);
        assert_eq!(out.as_ptr(), allocation);
        append_length_prefixed_sections(&mut out, 3000, |bytes| {
            bytes.extend_from_slice(&[0x22; 127]);
            Ok::<(), ()>(())
        })
        .unwrap();
        assert_eq!(&out[131..133], &[127, 0x22]);
        assert_eq!(out.as_ptr(), allocation);
    }

    #[test]
    fn source_and_limit_failures_roll_back_bytes() {
        let mut out = vec![0xFA, 0xCE];
        assert_eq!(
            append_length_prefixed_sections(&mut out, 128, |bytes| {
                bytes.extend_from_slice(&[0; 48]);
                Err::<(), _>(9_u8)
            }),
            Err(SectionLengthError::Source(9))
        );
        assert_eq!(
            append_length_prefixed_sections(&mut out, 5, |bytes| {
                bytes.extend_from_slice(&[1, 2, 3, 4, 5, 6]);
                Ok::<(), u8>(())
            }),
            Err(SectionLengthError::ExceedsLimit {
                actual: 6,
                max_bytes: 5
            })
        );
        assert_eq!(
            append_length_prefixed_sections(&mut out, 128, |_bytes| Ok::<(), u8>(())),
            Err(SectionLengthError::Empty)
        );
        assert_eq!(
            append_length_prefixed_sections(&mut out, 0, |_bytes| Ok::<(), u8>(())),
            Err(SectionLengthError::InvalidLimit { max_bytes: 0 })
        );
        assert_eq!(out, [0xFA, 0xCE]);
    }
}
