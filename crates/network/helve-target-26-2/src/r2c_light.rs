//! Target-owned 26.2 initial light-payload candidate, used only at the COLD boundary.
//!
//! Exact mask classifications come from the coherent borrowed world owner.
//! This module owns the wire-shaped mask/array fields, never resident light,
//! persistence, a second light engine or an independently queued packet.
//! The outer chunk-with-light Play packet remains source-admission blocked.

/// Source-backed packed light bytes per vertical section.
pub const LAYER_BYTES: usize = 2048;
/// Maximum initial light lattice: 64 logical sections plus two boundary slots.
pub const MAX_LIGHT_SECTIONS: usize = 66;

/// Four 26.2 initial light masks, independently derived from source semantics.
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct LightWireMasks {
    pub sky_data: u128,
    pub block_data: u128,
    pub sky_empty: u128,
    pub block_empty: u128,
}

/// A source-inconsistent or unsupported mask cannot reach a packet candidate.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LightWireError {
    /// The target-neutral source did not establish a supported light lattice.
    InvalidSectionCount { count: usize },
    /// One mask has a set bit beyond the exact source-derived light section span.
    MaskOutsideSpan { mask: usize },
    /// One light section was both present with data and classified empty.
    ConflictingMask { sky: bool },
    /// The list count exceeds the exact source-backed light section bound.
    UpdateCountExceedsLimit { actual: usize },
}

fn append_bitset(output: &mut Vec<u8>, bits: u128) {
    let low = u64::try_from(bits & u128::from(u64::MAX))
        .expect("low 64 bits are bounded by the mask");
    let high = u64::try_from(bits >> 64).expect("high 64 bits fit u64");
    if high != 0 {
        output.push(2); // canonical VarInt array count, two 64-bit words.
        output.extend_from_slice(&low.to_be_bytes());
        output.extend_from_slice(&high.to_be_bytes());
    } else if low != 0 {
        output.push(1);
        output.extend_from_slice(&low.to_be_bytes());
    } else {
        output.push(0);
    }
}

/// Validates and appends four source-ordered packed `BitSet` masks.
///
/// For each mask, the target long-array length is the smallest count that
/// covers its highest set bit; long words are emitted low-index-first and
/// each word is big-endian. This preserves the distinction between absent,
/// present-but-empty and present 2048-byte layers.
///
/// Does not include the sky/block update array collections or an outer packet.
///
/// # Errors
///
/// If any mask conflicts with the source lattice or its counterpart, no
/// destination bytes are appended.
pub fn append_light_masks_candidate(
    output: &mut Vec<u8>,
    light_section_count: usize,
    masks: LightWireMasks,
) -> Result<(), LightWireError> {
    if !(3..=MAX_LIGHT_SECTIONS).contains(&light_section_count) {
        return Err(LightWireError::InvalidSectionCount {
            count: light_section_count,
        });
    }
    let valid = (1_u128 << light_section_count) - 1;
    for (mask, bits) in [
        masks.sky_data,
        masks.block_data,
        masks.sky_empty,
        masks.block_empty,
    ]
    .into_iter()
    .enumerate()
    {
        if bits & !valid != 0 {
            return Err(LightWireError::MaskOutsideSpan { mask });
        }
    }
    if masks.sky_data & masks.sky_empty != 0 {
        return Err(LightWireError::ConflictingMask { sky: true });
    }
    if masks.block_data & masks.block_empty != 0 {
        return Err(LightWireError::ConflictingMask { sky: false });
    }

    output.reserve(4 * (1 + 2 * 8));
    append_bitset(output, masks.sky_data);
    append_bitset(output, masks.block_data);
    append_bitset(output, masks.sky_empty);
    append_bitset(output, masks.block_empty);
    Ok(())
}

/// Write the bounded source-ordered count of sky *or* block payload arrays.
///
/// Count is intentionally not inferred from previously emitted bytes; the
/// caller must provide the exact count from the same validated data mask.
///
/// # Errors
///
/// Count above the admitted 66 light slots fails before modifying the buffer.
pub fn append_light_update_count_candidate(
    output: &mut Vec<u8>,
    count: usize,
) -> Result<(), LightWireError> {
    if count > MAX_LIGHT_SECTIONS {
        return Err(LightWireError::UpdateCountExceedsLimit { actual: count });
    }
    // The maximum is 66, hence this is an exact single-byte VarInt.
    let bounded = u8::try_from(count)
        .map_err(|_| LightWireError::UpdateCountExceedsLimit { actual: count })?;
    output.push(bounded);
    Ok(())
}

/// Appends one 2048-byte packed light layer with its exact `VarInt` length.
///
/// Writes raw bytes directly into the caller's growing output allocation.
/// The source visitor fills that final byte region without an intermediate
/// 2048-byte stack/heap packet copy. A homogeneous non-zero source layer
/// expands only at this COLD wire boundary.
///
/// # Panics
///
/// Only if the standard Vec allocation/resize or fixed 2048-byte slice
/// invariant fails. The caller's fill callback may also panic.
pub fn append_light_update_layer_candidate(
    output: &mut Vec<u8>,
    fill: impl FnOnce(&mut [u8; LAYER_BYTES]),
) {
    output.reserve(2 + LAYER_BYTES);
    output.extend_from_slice(&[0x80, 0x10]); // VarInt(2048)
    let start = output.len();
    output.resize(start + LAYER_BYTES, 0);
    let slice: &mut [u8; LAYER_BYTES] = (&mut output[start..])
        .try_into()
        .expect("newly extended raw layer has 2048 bytes");
    fill(slice);
}

#[cfg(test)]
mod tests {
    use super::{
        LAYER_BYTES, LightWireError, LightWireMasks, append_light_masks_candidate,
        append_light_update_count_candidate, append_light_update_layer_candidate,
    };

    #[test]
    fn four_masks_use_minimal_long_arrays_in_source_order() {
        let masks = LightWireMasks {
            sky_data: 1_u128 << 65 | 1,
            block_data: 1_u128 << 64,
            sky_empty: 1_u128 << 2,
            block_empty: 1_u128 << 1,
        };
        let mut output = vec![0xBE, 0xEF];
        append_light_masks_candidate(&mut output, 66, masks).unwrap();

        let mut oracle = vec![0xBE, 0xEF, 2];
        oracle.extend_from_slice(&1_u64.to_be_bytes());
        oracle.extend_from_slice(&2_u64.to_be_bytes());
        oracle.push(2);
        oracle.extend_from_slice(&0_u64.to_be_bytes());
        oracle.extend_from_slice(&1_u64.to_be_bytes());
        oracle.push(1);
        oracle.extend_from_slice(&4_u64.to_be_bytes());
        oracle.push(1);
        oracle.extend_from_slice(&2_u64.to_be_bytes());
        assert_eq!(output, oracle);
    }

    #[test]
    fn high_bits_overlap_and_bad_span_fail_before_writing() {
        let mut out = vec![0xDE, 0xAD];
        assert_eq!(
            append_light_masks_candidate(&mut out, 2, LightWireMasks::default()),
            Err(LightWireError::InvalidSectionCount { count: 2 })
        );
        assert_eq!(
            append_light_masks_candidate(
                &mut out,
                3,
                LightWireMasks {
                    block_empty: 1_u128 << 4,
                    ..LightWireMasks::default()
                }
            ),
            Err(LightWireError::MaskOutsideSpan { mask: 3 })
        );
        assert_eq!(
            append_light_masks_candidate(
                &mut out,
                3,
                LightWireMasks {
                    sky_data: 1,
                    sky_empty: 1,
                    ..LightWireMasks::default()
                }
            ),
            Err(LightWireError::ConflictingMask { sky: true })
        );
        assert_eq!(out, [0xDE, 0xAD]);
    }

    #[test]
    fn one_layer_writes_exact_length_and_direct_raw_destination() {
        let mut out = Vec::with_capacity(5000);
        out.push(0xE0);
        let ptr = out.as_ptr();
        append_light_update_count_candidate(&mut out, 1).unwrap();
        append_light_update_layer_candidate(&mut out, |data| {
            data.fill(0xFE);
            data[0] = 0x32;
            data[LAYER_BYTES - 1] = 0x0F;
        });
        assert_eq!(&out[..5], &[0xE0, 1, 0x80, 0x10, 0x32]);
        assert_eq!(out.len(), 1 + 1 + 2 + LAYER_BYTES);
        assert_eq!(out[5], 0xFE);
        assert_eq!(out.last(), Some(&0x0F));
        assert_eq!(out.as_ptr(), ptr);

        let before = out.clone();
        assert_eq!(
            append_light_update_count_candidate(&mut out, 67),
            Err(LightWireError::UpdateCountExceedsLimit { actual: 67 })
        );
        assert_eq!(out, before);
    }

    #[test]
    fn zero_data_mask_has_zero_length_word_array_not_an_empty_layer() {
        let mut out = Vec::new();
        append_light_masks_candidate(&mut out, 3, LightWireMasks::default()).unwrap();
        assert_eq!(out, [0, 0, 0, 0]);
        append_light_update_count_candidate(&mut out, 0).unwrap();
        append_light_update_count_candidate(&mut out, 0).unwrap();
        assert_eq!(out, [0, 0, 0, 0, 0, 0]);
    }
}
