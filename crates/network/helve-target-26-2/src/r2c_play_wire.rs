//! Source-reviewed 26.2 chunk-observation packet envelope; COLD only.
//!
//! Positions and scalar encodings are verified against the SHA-pinned 26.2
//! server source and bundle-delimiter offset. Live R2C publication is still
//! blocked on client biome registry and world-entry qualification.

use helve_connection_core::FrameView;

/// 26.2 Play packet candidates backed by independently inspected exact client
/// `GameProtocols` registration order. Complete source/VAR/SEM admission
/// is separate from these numeric identities.
pub const CLIENTBOUND_CHUNK_WITH_LIGHT: u8 = 45;
pub const CLIENTBOUND_CHUNK_BATCH_START: u8 = 12;
pub const CLIENTBOUND_CHUNK_BATCH_FINISHED: u8 = 11;
pub const CLIENTBOUND_SET_CHUNK_CACHE_CENTER: u8 = 94;
pub const SERVERBOUND_CHUNK_BATCH_RECEIVED: i32 = 11;
/// Selected remote-client `PlayerChunkSender` upper bound.
pub const MAX_REMOTE_CHUNKS_PER_BATCH: usize = 64;

/// Fail-closed validation of the finite 26.2 batch scalar codecs.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ChunkBatchWireError {
    InvalidRemoteBatchSize { count: usize },
    InvalidAcknowledgementLength { actual: usize },
}

/// Emit the verified outer chunk-with-light packet identity, followed by a
/// separately receipt-bound, source-coherent body from the COLD projector.
pub fn append_chunk_with_light_packet_id(output: &mut Vec<u8>) {
    output.push(CLIENTBOUND_CHUNK_WITH_LIGHT);
}

/// Start a vanilla 26.2 chunk batch (no payload beyond packet identity).
pub fn append_chunk_batch_start(output: &mut Vec<u8>) {
    output.push(CLIENTBOUND_CHUNK_BATCH_START);
}

/// Close a nonempty remote-client batch with its exact `VarInt` chunk count.
///
/// The batch publication owner must independently prove `count` successful
/// chunks between this packet and its preceding start packet.
///
/// # Errors
///
/// Invalid count restores/preserves all caller bytes.
///
/// # Panics
///
/// Only on violation of the already-checked 1..=64 integer conversion invariant.
pub fn append_chunk_batch_finished(
    output: &mut Vec<u8>,
    count: usize,
) -> Result<(), ChunkBatchWireError> {
    if !(1..=MAX_REMOTE_CHUNKS_PER_BATCH).contains(&count) {
        return Err(ChunkBatchWireError::InvalidRemoteBatchSize { count });
    }
    output.push(CLIENTBOUND_CHUNK_BATCH_FINISHED);
    output.push(u8::try_from(count).expect("source-limited batch count <= 64"));
    Ok(())
}

fn append_signed_varint(output: &mut Vec<u8>, value: i32) {
    let mut remaining = value.cast_unsigned();
    while remaining >= 0x80 {
        output.push(((remaining & 0x7f) as u8) | 0x80);
        remaining >>= 7;
    }
    output.push((remaining & 0x7f) as u8);
}

/// Cache-centre signed chunk coordinates use Java two's-complement `VarInt`,
/// *not* zigzag. No permanent network-specific spatial state is introduced.
pub fn append_set_chunk_cache_center(output: &mut Vec<u8>, x: i32, z: i32) {
    output.push(CLIENTBOUND_SET_CHUNK_CACHE_CENTER);
    append_signed_varint(output, x);
    append_signed_varint(output, z);
}

/// Decode the float32 big-endian acknowledgement from the correct Play ID.
///
/// # Errors
///
/// A matching packet with any payload length other than four is rejected.
pub fn decode_chunk_batch_ack(frame: FrameView<'_>) -> Result<Option<f32>, ChunkBatchWireError> {
    if frame.packet_id() != SERVERBOUND_CHUNK_BATCH_RECEIVED {
        return Ok(None);
    }
    let bytes: &[u8; 4] = frame.payload().try_into().map_err(|_| {
        ChunkBatchWireError::InvalidAcknowledgementLength {
            actual: frame.payload().len(),
        }
    })?;
    Ok(Some(f32::from_be_bytes(*bytes)))
}

/// Exact `PlayerChunkSender` acknowledgement normalization (0.01 .. 64).
#[must_use]
pub fn normalize_remote_chunk_rate(desired: f32) -> f32 {
    if desired.is_nan() {
        0.01
    } else {
        desired.clamp(0.01, 64.0)
    }
}

#[cfg(test)]
mod tests {
    use helve_connection_core::{ConnectionLimits, IngressBuffer};

    use super::{
        CLIENTBOUND_CHUNK_BATCH_FINISHED, CLIENTBOUND_CHUNK_BATCH_START,
        CLIENTBOUND_CHUNK_WITH_LIGHT, CLIENTBOUND_SET_CHUNK_CACHE_CENTER, ChunkBatchWireError,
        MAX_REMOTE_CHUNKS_PER_BATCH, SERVERBOUND_CHUNK_BATCH_RECEIVED, append_chunk_batch_finished,
        append_chunk_batch_start, append_chunk_with_light_packet_id, append_set_chunk_cache_center,
        decode_chunk_batch_ack, normalize_remote_chunk_rate,
    };

    #[test]
    fn source_reviewed_clientbound_identities_and_remote_bounds() {
        // ProtocolInfoBuilder.withBundlePacket registers delimiter at index 0.
        assert_eq!(CLIENTBOUND_CHUNK_BATCH_FINISHED, 11);
        assert_eq!(CLIENTBOUND_CHUNK_BATCH_START, 12);
        assert_eq!(CLIENTBOUND_CHUNK_WITH_LIGHT, 45);
        assert_eq!(CLIENTBOUND_SET_CHUNK_CACHE_CENTER, 94);
        assert_eq!(SERVERBOUND_CHUNK_BATCH_RECEIVED, 11);
        assert_eq!(MAX_REMOTE_CHUNKS_PER_BATCH, 64);
    }

    #[test]
    fn batching_is_zero_payload_and_count_rejection_is_transactional() {
        let mut output = Vec::with_capacity(16);
        let ptr = output.as_ptr();
        append_chunk_batch_start(&mut output);
        append_chunk_with_light_packet_id(&mut output);
        append_chunk_batch_finished(&mut output, 1).unwrap();
        assert_eq!(output, [12, 45, 11, 1]);
        assert_eq!(output.as_ptr(), ptr);
        assert_eq!(
            append_chunk_batch_finished(&mut output, 0),
            Err(ChunkBatchWireError::InvalidRemoteBatchSize { count: 0 })
        );
        assert_eq!(
            append_chunk_batch_finished(&mut output, 65),
            Err(ChunkBatchWireError::InvalidRemoteBatchSize { count: 65 })
        );
        assert_eq!(output, [12, 45, 11, 1]);
        let mut max = Vec::new();
        append_chunk_batch_finished(&mut max, 64).unwrap();
        assert_eq!(max, [11, 64]);
    }

    #[test]
    fn signed_cache_center_uses_twos_complement_not_zigzag() {
        let mut output = Vec::new();
        append_set_chunk_cache_center(&mut output, 0, -1);
        assert_eq!(output, [94, 0, 255, 255, 255, 255, 15]);
        output.clear();
        append_set_chunk_cache_center(&mut output, -7, 300);
        assert_eq!(output, [94, 249, 255, 255, 255, 15, 172, 2]);
    }

    #[test]
    fn serverbound_ack_is_exact_float32_and_other_packets_are_untouched() {
        let limits = ConnectionLimits::new(128, 256, 256).unwrap();
        let mut input = IngressBuffer::new(limits);
        input.push(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            decode_chunk_batch_ack(input.peek_frame().unwrap().unwrap()),
            Ok(Some(9.0))
        );
        let mut unrelated = IngressBuffer::new(limits);
        unrelated.push(&[2, 12, 0]).unwrap();
        assert_eq!(
            decode_chunk_batch_ack(unrelated.peek_frame().unwrap().unwrap()),
            Ok(None)
        );
        let mut malformed = IngressBuffer::new(limits);
        malformed.push(&[2, 11, 0]).unwrap();
        assert_eq!(
            decode_chunk_batch_ack(malformed.peek_frame().unwrap().unwrap()),
            Err(ChunkBatchWireError::InvalidAcknowledgementLength { actual: 1 })
        );
    }

    #[test]
    fn remote_client_rate_matches_vanilla_float_boundary() {
        fn assert_exact(input: f32, expected: f32) {
            assert_eq!(
                normalize_remote_chunk_rate(input).to_bits(),
                expected.to_bits()
            );
        }

        assert_exact(f32::NAN, 0.01);
        assert_exact(f32::NEG_INFINITY, 0.01);
        assert_exact(-1.0, 0.01);
        assert_exact(0.0, 0.01);
        assert_exact(9.0, 9.0);
        assert_exact(128.0, 64.0);
        assert_exact(f32::INFINITY, 64.0);
    }
}
