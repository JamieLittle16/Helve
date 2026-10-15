//! COLD 26.2 outer chunk-with-light *body candidate*, not a Play packet.
//!
//! The exact enclosing packet identity, profile/registry source admission,
//! block-entity inclusion law and world-entry publication remain unadmitted.
//! These are target-owned candidate field codecs only: no server-side packet
//! registry, new socket owner, resident state or HOT-world cost.

/// Appends candidate chunk-column coordinates as two big-endian signed ints.
///
/// This source-review-pending field must not be used to claim a qualified
/// 26.2 outer Play packet ID or publication law. Appends exactly eight bytes.
pub fn append_chunk_coordinates_candidate(output: &mut Vec<u8>, x: i32, z: i32) {
    output.reserve(8);
    output.extend_from_slice(&x.to_be_bytes());
    output.extend_from_slice(&z.to_be_bytes());
}

/// Writes a *candidate* empty block-entity collection as one zero `VarInt`.
///
/// **Precondition:** the server COLD adapter has independently verified a
/// uniquely present, explicitly empty saved block-entity source list for
/// the same chunk. This target-only primitive is deliberately not an
/// admission or verification of that source evidence; its caller must
/// check it before invoking this function.
///
/// No nonempty list, block-entity type, local position or NBT encoding is
/// supported here. Source review of the outer packet and list-size codec
/// is still required before any of these bytes can reach Play.
pub fn append_empty_block_entities_candidate(output: &mut Vec<u8>) {
    output.push(0);
}

#[cfg(test)]
mod tests {
    use super::{append_chunk_coordinates_candidate, append_empty_block_entities_candidate};

    #[test]
    fn signed_chunk_coordinates_use_network_big_endian_without_allocation() {
        let mut output = Vec::with_capacity(32);
        output.extend_from_slice(&[0xAD, 0xDE]);
        let pointer = output.as_ptr();
        append_chunk_coordinates_candidate(&mut output, -1, 0x1234_5678);
        assert_eq!(
            output,
            [0xAD, 0xDE, 0xff, 0xff, 0xff, 0xff, 0x12, 0x34, 0x56, 0x78]
        );
        assert_eq!(output.as_ptr(), pointer);
    }

    #[test]
    fn empty_list_candidate_uses_zero_varint_only() {
        let mut output = vec![0x23];
        append_empty_block_entities_candidate(&mut output);
        assert_eq!(output, [0x23, 0]);
    }
}
