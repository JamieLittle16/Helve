//! Retained-driver continuing-Play ingress composition for the future R2C world owner.
//!
//! This *does not* select or publish a world: receiving-client biome ordinals,
//! per-state heightmap facts and the complete outer chunk/Play law still require
//! independent source admission. It only composes the existing transactional R2B
//! control and R2C batch-ack handlers without adding an ingress queue or a
//! second packet decoder. An unowned gameplay frame remains at the front of
//! the original driver for the next explicit owner or fail-closed policy.

use helve_connection_driver::DriverError;

use crate::r2b_server::{
    R2bPlayError, R2bPlayInbound, R2bPlayProcess, R2bPlaySession,
};
use crate::r2c_chunk_batch::{
    ChunkBatchInboundError, ChunkBatchInboundStep, R2cChunkBatchState,
};

/// Exactly one complete continuing-Play frame, or no committed frame.
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum R2cPlayInboundStep {
    Incomplete,
    Control(R2bPlayInbound),
    ChunkBatchAcknowledged { desired_per_tick: f32 },
    /// A complete unowned frame is *not* consumed.
    Unclaimed { packet_id: i32 },
}

/// Source-owned control and batch-ack failures remain distinguishable.
#[derive(Debug)]
pub(crate) enum R2cPlayInboundError {
    Control(R2bPlayError),
    ChunkBatch(DriverError<ChunkBatchInboundError>),
}

/// Service at most one ingress frame on the *original* R2B Play driver.
///
/// R2B's teleport and keep-alive handler gets first refusal. When it reports
/// an unclaimed frame, the existing R2C handler receives the identical
/// still-buffered frame and can commit a chunk-batch acknowledgement. Neither
/// handler consumes incomplete or unowned frames. A malformed or premature
/// claimed packet fails closed without advancing batch state or consuming it.
///
/// This returns ownership of unknown gameplay to the caller: a future live
/// owner must explicitly handle or reject it, never silently claim it here.
///
/// # Errors
///
/// Returns either R2B control failure or R2C batch-ack failure. Both
/// transactional handlers preserve their respective live state on rejection.
pub(crate) fn process_one_r2c_play_inbound(
    session: &mut R2bPlaySession,
    batch: &mut R2cChunkBatchState,
    now_ms: u64,
) -> Result<R2cPlayInboundStep, R2cPlayInboundError> {
    match session
        .process_one_play_control(now_ms)
        .map_err(R2cPlayInboundError::Control)?
    {
        R2bPlayProcess::Incomplete => Ok(R2cPlayInboundStep::Incomplete),
        R2bPlayProcess::Committed(event) => Ok(R2cPlayInboundStep::Control(event)),
        R2bPlayProcess::Unclaimed { packet_id } => match session
            .process_one_r2c_chunk_batch_ack(batch)
            .map_err(R2cPlayInboundError::ChunkBatch)?
        {
            ChunkBatchInboundStep::Incomplete => Ok(R2cPlayInboundStep::Incomplete),
            ChunkBatchInboundStep::Received { desired_per_tick } => {
                Ok(R2cPlayInboundStep::ChunkBatchAcknowledged { desired_per_tick })
            }
            ChunkBatchInboundStep::Unclaimed {
                packet_id: batch_packet_id,
            } => {
                debug_assert_eq!(packet_id, batch_packet_id);
                Ok(R2cPlayInboundStep::Unclaimed { packet_id })
            }
        },
    }
}

#[cfg(test)]
mod tests {
    use helve_connection_core::ConnectionLimits;
    use helve_connection_driver::{ConnectionDriver, DriverError};
    use helve_session_core::LivenessState;
    use helve_target_26_2::r2b::{TeleportAckResult, TeleportTransaction};

    use super::{
        R2cPlayInboundError, R2cPlayInboundStep, process_one_r2c_play_inbound,
    };
    use crate::r2b_server::{R2bPlayError, R2bPlayInbound, R2bPlaySession};
    use crate::r2c_chunk_batch::{
        ChunkBatchInboundError, ChunkBatchStep, R2cChunkBatchState,
    };

    fn session() -> R2bPlaySession {
        R2bPlaySession {
            driver: ConnectionDriver::new(
                ConnectionLimits::new(65_535, 131_072, 262_144).unwrap(),
            ),
            read_scratch: vec![0_u8; 64].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).unwrap(),
        }
    }

    #[test]
    fn interleaved_teleport_and_ack_commit_on_one_retained_driver() {
        let mut session = session();
        let reader = session.read_scratch.as_ptr();
        let issued = session.teleport.issue(10.0, 84.0, -5.0, 0.0, 0.0);
        assert_eq!(issued.id, 1);

        let mut batch = R2cChunkBatchState::new(1);
        batch.on_tick();
        let mut scratch = Vec::new();
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut batch, &mut scratch, |_, bytes| {
                bytes.extend_from_slice(&[45, 0]); // test-only packet candidate
                Ok::<(), &'static str>(())
            }),
            Ok(ChunkBatchStep::Started { count: 1 })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut batch, &mut scratch, |_, bytes| {
                bytes.extend_from_slice(&[45, 0]);
                Ok::<(), &'static str>(())
            }),
            Ok(ChunkBatchStep::ChunkQueued { index: 0, .. })
        ));
        assert!(matches!(
            session.service_r2c_chunk_batch_one(&mut batch, &mut scratch, |_, _| {
                Ok::<(), &'static str>(())
            }),
            Ok(ChunkBatchStep::Finished { count: 1 })
        ));
        let egress_before = session.pending_play_egress().to_vec();
        assert_eq!(batch.unacknowledged_batches(), 1);

        // Serverbound teleport confirmation (ID 0, teleport 1), followed by
        // source-reviewed float32 chunk batch ACK (ID 12, 9.0f32).
        session.ingest_play(&[2, 0, 1, 5, 12, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap(),
            R2cPlayInboundStep::Control(
                R2bPlayInbound::TeleportAcknowledgement(TeleportAckResult::Accepted)
            )
        );
        assert!(session.teleport_transaction().awaiting().is_none());
        assert_eq!(batch.unacknowledged_batches(), 1);
        assert_eq!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap(),
            R2cPlayInboundStep::ChunkBatchAcknowledged {
                desired_per_tick: 9.0,
            }
        );
        assert_eq!(session.buffered_ingress(), 0);
        assert_eq!(batch.unacknowledged_batches(), 0);
        assert_eq!(session.pending_play_egress(), egress_before);
        assert_eq!(session.read_scratch.as_ptr(), reader);
    }

    #[test]
    fn fragmented_ack_is_retained_until_complete_and_premature_ack_fails_closed() {
        let mut session = session();
        let mut batch = R2cChunkBatchState::new(1);
        session.ingest_play(&[5, 12, 0x41]).unwrap();
        assert_eq!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap(),
            R2cPlayInboundStep::Incomplete
        );
        assert_eq!(session.buffered_ingress(), 3);
        session.ingest_play(&[0x10, 0, 0]).unwrap();
        assert!(matches!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0),
            Err(R2cPlayInboundError::ChunkBatch(DriverError::Handler(
                ChunkBatchInboundError::NoFinishedBatchToAcknowledge
            )))
        ));
        assert_eq!(session.buffered_ingress(), 6);
        assert_eq!(batch.next_chunk_index(), 0);
        assert_eq!(batch.unacknowledged_batches(), 0);
    }

    #[test]
    fn malformed_control_packet_preserves_original_ingress_and_typed_error() {
        let mut session = session();
        let mut batch = R2cChunkBatchState::new(1);
        // A complete serverbound teleport-confirm frame with no VarInt ID.
        session.ingest_play(&[1, 0]).unwrap();
        let error = process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap_err();
        match error {
            R2cPlayInboundError::Control(control) => {
                assert!(matches!(control, R2bPlayError::TeleportCodec(_)));
            }
            R2cPlayInboundError::ChunkBatch(_) => panic!("teleport belongs to R2B control"),
        }
        assert_eq!(session.buffered_ingress(), 2);
        assert_eq!(batch.unacknowledged_batches(), 0);
    }

    #[test]
    fn unrelated_gameplay_frame_remains_byte_for_byte_unclaimed() {
        let mut session = session();
        let mut batch = R2cChunkBatchState::new(1);
        session.ingest_play(&[2, 28, 99]).unwrap();
        assert_eq!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap(),
            R2cPlayInboundStep::Unclaimed { packet_id: 28 }
        );
        assert_eq!(session.buffered_ingress(), 3);
        // Re-processing exposes the same packet identity and length:
        // neither handler can advance the driver on an unclaimed frame.
        assert_eq!(
            process_one_r2c_play_inbound(&mut session, &mut batch, 0).unwrap(),
            R2cPlayInboundStep::Unclaimed { packet_id: 28 }
        );
        assert_eq!(session.buffered_ingress(), 3);
        assert_eq!(batch.next_chunk_index(), 0);
        assert_eq!(batch.unacknowledged_batches(), 0);
    }
}
