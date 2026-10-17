//! COLD receipt-selection batching through the one retained R2B Play connection.
//!
//! The selected immutable receipt window is caller-owned. This tiny per-client
//! state owns only a publication cursor, vanilla remote-client rate/quota
//! bookkeeping and an active batch boundary. No packet copy, second connection
//! buffer, runtime registry, or HOT per-block overhead is introduced.
//! Production publication remains gated by client biome-ID/pack-profile source
//! admission and a stock-client-qualified world lifecycle.

use helve_connection_driver::{DriverError, OutboundBatch, TransactionResult};
use helve_publication_core::{PublicationCursor, PublicationStep};
use helve_target_26_2::r2c_play_wire::{
    CLIENTBOUND_CHUNK_BATCH_FINISHED, CLIENTBOUND_CHUNK_BATCH_START, ChunkBatchWireError,
    MAX_REMOTE_CHUNKS_PER_BATCH, append_set_chunk_cache_center, decode_chunk_batch_ack,
    normalize_remote_chunk_rate,
};
use helve_types::ChunkPos;

use crate::r2b_server::R2bPlaySession;

const INITIAL_RATE: f32 = 9.0;
const MAX_OUTSTANDING_AFTER_ACK: u8 = 10;

/// A monotonic, fixed-phase 20 Hz chunk-service clock for the eventual
/// source-admitted Play loop. One poll admits at most one logical send tick,
/// even after a late socket wake-up: missed ticks never become a burst of
/// accumulated chunk quota. The caller must separately cap its blocking
/// read deadline to the earlier of this clock and Play liveness.
///
/// Constructing or polling this clock does not authorize chunk publication.
#[cfg_attr(
    not(test),
    allow(dead_code, reason = "live R2C send ticks await source admission")
)]
pub(crate) struct R2cBatchTickClock {
    next_due_ms: u64,
}

#[cfg_attr(
    not(test),
    allow(dead_code, reason = "live R2C send ticks await source admission")
)]
impl R2cBatchTickClock {
    const TICK_MS: u64 = 50;

    /// Start with one immediately due service opportunity, not a burst.
    pub(crate) const fn new(now_ms: u64) -> Self {
        Self {
            next_due_ms: now_ms,
        }
    }

    /// The earliest permitted wake-up time for chunk or liveness service.
    pub(crate) const fn next_wake_deadline_ms(&self, liveness_deadline_ms: u64) -> u64 {
        if self.next_due_ms < liveness_deadline_ms {
            self.next_due_ms
        } else {
            liveness_deadline_ms
        }
    }

    /// Supply no more than one tick and skip entire overdue tick intervals.
    /// No batch cursor, packet bytes or source receipt are mutated here.
    pub(crate) fn poll_tick(&mut self, now_ms: u64, batch: &mut R2cChunkBatchState) -> bool {
        if now_ms < self.next_due_ms {
            return false;
        }
        let overdue = now_ms - self.next_due_ms;
        let intervals = overdue / Self::TICK_MS + 1;
        self.next_due_ms = self
            .next_due_ms
            .saturating_add(intervals.saturating_mul(Self::TICK_MS));
        batch.on_tick();
        true
    }
}

/// Convert only a verified, source-capped nonnegative quota. Truncation
/// matches Java's floor for these finite, nonnegative values.
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_sign_loss,
    reason = "quota is finite and between 0 and 64 after source-bounded replenishment"
)]
fn bounded_floor_quota(quota: f32) -> usize {
    debug_assert!(quota.is_finite() && (0.0..=64.0).contains(&quota));
    quota as usize
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum BatchPhase {
    Ready,
    Sending { end: usize, count: u8 },
    Finishing { count: u8 },
}

/// Compact progress, rate, and acknowledgement state for one immutable COLD
/// selection. Callers must retain the same ordered source receipts until
/// this instance is complete; the chunk projector checks receipt freshness.
#[derive(Clone, Copy, Debug)]
pub(crate) struct R2cChunkBatchState {
    selected: usize,
    cursor: PublicationCursor,
    phase: BatchPhase,
    pending_center: Option<ChunkPos>,
    desired_per_tick: f32,
    quota: f32,
    unacknowledged: u8,
    max_unacknowledged: u8,
}

/// Exactly one publication packet or a no-op is attempted per service call.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ChunkBatchStep {
    Complete,
    WaitingForTick,
    WaitingForAcknowledgement,
    CacheCenterQueued { x: i32, z: i32 },
    Started { count: u8 },
    ChunkQueued { index: usize, body_bytes: usize },
    Finished { count: u8 },
}

/// A serverbound packet was malformed or not a valid acknowledgement.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ChunkBatchInboundError {
    Unclaimed(i32),
    Wire(ChunkBatchWireError),
    NoFinishedBatchToAcknowledge,
}

/// One finite transactional attempt at a received chunk-batch acknowledgement.
#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum ChunkBatchInboundStep {
    Incomplete,
    Unclaimed { packet_id: i32 },
    Received { desired_per_tick: f32 },
}

#[derive(Clone, Copy, Debug)]
struct PreparedChunkAck {
    next: R2cChunkBatchState,
    desired_per_tick: f32,
}

impl OutboundBatch for PreparedChunkAck {
    type Body = [u8; 0];

    fn outbound_frames(&self) -> &[Self::Body] {
        &[]
    }
}

impl R2cChunkBatchState {
    /// Start a single immutable caller-selected receipt window, including
    /// the valid empty window. Selection priority is resolved upstream.
    #[must_use]
    pub(crate) const fn new(selected: usize) -> Self {
        Self {
            selected,
            cursor: PublicationCursor::new(),
            phase: BatchPhase::Ready,
            pending_center: None,
            desired_per_tick: INITIAL_RATE,
            quota: 0.0,
            unacknowledged: 0,
            max_unacknowledged: 1,
        }
    }

    /// One initial-world selection at an explicit source-known chunk-cache
    /// center. Unlike the legacy generic test constructor, this emits the
    /// 26.2 clientbound center update before any batch-start packet.
    ///
    /// The caller selects the center from the admitted player/view position;
    /// it is not inferred from unsorted receipts or an arbitrary chunk.
    #[must_use]
    pub(crate) const fn new_with_initial_cache_center(selected: usize, center: ChunkPos) -> Self {
        let mut state = Self::new(selected);
        state.pending_center = Some(center);
        state
    }

    #[must_use]
    pub(crate) const fn next_chunk_index(self) -> usize {
        self.cursor.next_index()
    }

    #[must_use]
    pub(crate) const fn unacknowledged_batches(self) -> u8 {
        self.unacknowledged
    }

    /// Whether an actual chunk send opportunity remains, without requiring
    /// an ACK from the remote client. Once selected chunks are sent or the
    /// unacknowledged window is full, the socket can block on liveness/ingress
    /// rather than waking uselessly at 20 Hz.
    #[must_use]
    pub(crate) fn needs_send_service(&self) -> bool {
        self.pending_center.is_some()
            || self.phase != BatchPhase::Ready
            || (self.cursor.next_index() != self.selected
                && self.unacknowledged < self.max_unacknowledged)
    }

    /// Replenish at most one vanilla send-tick quota. Do not count every
    /// individual packet admission as a separate server tick.
    pub(crate) fn on_tick(&mut self) {
        if self.cursor.next_index() == self.selected
            || self.phase != BatchPhase::Ready
            || self.unacknowledged >= self.max_unacknowledged
        {
            return;
        }
        let maximum = self.desired_per_tick.max(1.0);
        self.quota = (self.quota + self.desired_per_tick).min(maximum);
    }

    fn acknowledge(&mut self, rate: f32) -> Result<(), ChunkBatchInboundError> {
        // A currently open batch has not emitted its finish frame. The stock
        // client cannot acknowledge it, but it may acknowledge an *earlier*
        // batch while a newer one is in progress.
        let not_yet_finished = u8::from(self.phase != BatchPhase::Ready);
        if self.unacknowledged <= not_yet_finished {
            return Err(ChunkBatchInboundError::NoFinishedBatchToAcknowledge);
        }
        self.unacknowledged -= 1;
        self.desired_per_tick = normalize_remote_chunk_rate(rate);
        if self.unacknowledged == 0 {
            self.quota = 1.0;
        }
        self.max_unacknowledged = MAX_OUTSTANDING_AFTER_ACK;
        Ok(())
    }
}

impl R2bPlaySession {
    /// Admit at most one cache-center, start, chunk or finish frame through
    /// the identical R2B Play driver. Retry unchanged on bounded backpressure.
    ///
    /// The callback must append one *complete* current-source checked packet
    /// body with the already-inspected 26.2 chunk-with-light packet identity.
    /// A caller cannot change the selected receipt list or its ordering.
    ///
    /// # Errors
    ///
    /// Propagates source or egress rejection without advancing the phase,
    /// chunk cursor, pending center, outstanding count or queued wire bytes.
    pub(crate) fn service_r2c_chunk_batch_one<E>(
        &mut self,
        state: &mut R2cChunkBatchState,
        scratch: &mut Vec<u8>,
        append_chunk: impl FnOnce(usize, &mut Vec<u8>) -> Result<(), E>,
    ) -> Result<ChunkBatchStep, DriverError<E>> {
        if let Some(center) = state.pending_center {
            // A center packet has 1 ID byte + 2 signed VarInts (at most
            // 5 bytes each). Append to the *same* caller-owned scratch
            // for this attempt and restore its original prefix whether
            // or not the sole egress owner admits the framed packet.
            // No additional packet list, queue, or owned body is created.
            let original_len = scratch.len();
            append_set_chunk_cache_center(scratch, center.x, center.z);
            let admission = self.driver.queue_frame::<E>(&scratch[original_len..]);
            scratch.truncate(original_len);
            admission?;
            state.pending_center = None;
            return Ok(ChunkBatchStep::CacheCenterQueued {
                x: center.x,
                z: center.z,
            });
        }

        match state.phase {
            BatchPhase::Ready => {
                if state.cursor.next_index() == state.selected {
                    return Ok(ChunkBatchStep::Complete);
                }
                if state.unacknowledged >= state.max_unacknowledged {
                    return Ok(ChunkBatchStep::WaitingForAcknowledgement);
                }
                let budget = bounded_floor_quota(state.quota)
                    .min(MAX_REMOTE_CHUNKS_PER_BATCH)
                    .min(state.selected - state.cursor.next_index());
                if budget == 0 {
                    return Ok(ChunkBatchStep::WaitingForTick);
                }

                self.driver
                    .queue_frame::<E>(&[CLIENTBOUND_CHUNK_BATCH_START])?;
                let count = u8::try_from(budget).expect("source bounded remote batch <= 64");
                state.unacknowledged += 1;
                state.phase = BatchPhase::Sending {
                    end: state.cursor.next_index() + budget,
                    count,
                };
                Ok(ChunkBatchStep::Started { count })
            }
            BatchPhase::Sending { end, count } => {
                match self.service_play_projected_one(
                    end,
                    &mut state.cursor,
                    scratch,
                    append_chunk,
                )? {
                    PublicationStep::Queued { index, body_bytes } => {
                        if state.cursor.next_index() == end {
                            state.phase = BatchPhase::Finishing { count };
                        }
                        Ok(ChunkBatchStep::ChunkQueued { index, body_bytes })
                    }
                    PublicationStep::Complete => {
                        // The previous successfully admitted final chunk
                        // always moves phase to Finishing. This is unreachable
                        // for any state constructible by this module.
                        state.phase = BatchPhase::Finishing { count };
                        Ok(ChunkBatchStep::WaitingForTick)
                    }
                }
            }
            BatchPhase::Finishing { count } => {
                let body = [CLIENTBOUND_CHUNK_BATCH_FINISHED, count];
                self.driver.queue_frame::<E>(&body)?;
                state.quota -= f32::from(count);
                state.phase = BatchPhase::Ready;
                Ok(ChunkBatchStep::Finished { count })
            }
        }
    }

    /// Atomically consume one serverbound batch acknowledgement on the
    /// existing driver. Unknown packet identities are retained for the
    /// appropriate R2B/R3 handler; malformed or premature acknowledgements
    /// remain unread and cannot modify rate/batch state.
    ///
    /// # Errors
    ///
    /// Propagates malformed matching ack, unexpected early ack, and driver
    /// transactional failures without consuming ingress or adopting state.
    pub(crate) fn process_one_r2c_chunk_batch_ack(
        &mut self,
        state: &mut R2cChunkBatchState,
    ) -> Result<ChunkBatchInboundStep, DriverError<ChunkBatchInboundError>> {
        let original = *state;
        let action = self.driver.process_one_transactional(|frame| {
            let rate = decode_chunk_batch_ack(frame)
                .map_err(ChunkBatchInboundError::Wire)?
                .ok_or(ChunkBatchInboundError::Unclaimed(frame.packet_id()))?;
            let mut next = original;
            next.acknowledge(rate)?;
            Ok(PreparedChunkAck {
                next,
                desired_per_tick: next.desired_per_tick,
            })
        });

        match action {
            Ok(TransactionResult::Incomplete) => Ok(ChunkBatchInboundStep::Incomplete),
            Ok(TransactionResult::Committed(ack)) => {
                *state = ack.next;
                Ok(ChunkBatchInboundStep::Received {
                    desired_per_tick: ack.desired_per_tick,
                })
            }
            Err(DriverError::Handler(ChunkBatchInboundError::Unclaimed(packet_id))) => {
                Ok(ChunkBatchInboundStep::Unclaimed { packet_id })
            }
            Err(error) => Err(error),
        }
    }
}

#[cfg(test)]
mod tests {
    use helve_connection_core::{ConnectionBufferError, ConnectionLimits};
    use helve_connection_driver::{ConnectionDriver, DriverError};
    use helve_session_core::LivenessState;
    use helve_target_26_2::r2b::TeleportTransaction;
    use helve_types::ChunkPos;

    use super::{
        ChunkBatchInboundError, ChunkBatchInboundStep, ChunkBatchStep, R2cChunkBatchState,
    };
    use crate::r2b_server::R2bPlaySession;

    fn session(egress: usize) -> R2bPlaySession {
        R2bPlaySession {
            driver: ConnectionDriver::new(
                ConnectionLimits::new(egress.saturating_sub(1).min(64), 256, egress)
                    .expect("finite driver"),
            ),
            read_scratch: vec![0; 32].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).expect("valid origin"),
        }
    }

    #[expect(
        clippy::unnecessary_wraps,
        reason = "synthetic projector must share the fallible source-projection interface in retry tests"
    )]
    fn synthetic_chunk(index: usize, bytes: &mut Vec<u8>) -> Result<(), &'static str> {
        // Only in tests: a real 26.2 *identity* with deliberately non-real
        // body bytes. No source admission or user-facing packet is implied.
        bytes.extend_from_slice(&[
            helve_target_26_2::r2c_play_wire::CLIENTBOUND_CHUNK_WITH_LIGHT,
            u8::try_from(index).expect("small synthetic selection"),
        ]);
        Ok(())
    }

    #[test]
    fn logical_send_clock_is_phase_stable_and_never_replays_late_ticks() {
        use super::R2cBatchTickClock;

        let mut batch = R2cChunkBatchState::new(40);
        let mut clock = R2cBatchTickClock::new(1_000);
        assert_eq!(clock.next_wake_deadline_ms(1_200), 1_000);
        assert_eq!(clock.next_wake_deadline_ms(900), 900);
        assert!(!clock.poll_tick(999, &mut batch));
        assert!(clock.poll_tick(1_000, &mut batch));
        assert_eq!(batch.quota.to_bits(), 9.0_f32.to_bits());
        assert!(!clock.poll_tick(1_000, &mut batch));
        assert!(!clock.poll_tick(1_049, &mut batch));
        assert_eq!(clock.next_wake_deadline_ms(1_080), 1_050);

        // Late I/O wake skips four old deadlines, supplying one tick only.
        assert!(clock.poll_tick(1_263, &mut batch));
        assert_eq!(clock.next_wake_deadline_ms(1_500), 1_300);
        assert_eq!(batch.quota.to_bits(), 9.0_f32.to_bits());
        assert!(!clock.poll_tick(1_299, &mut batch));
        assert!(clock.poll_tick(1_300, &mut batch));
        assert_eq!(clock.next_wake_deadline_ms(1_400), 1_350);
    }

    #[test]
    fn logical_send_clock_does_not_spin_at_clock_saturation() {
        use super::R2cBatchTickClock;

        let mut batch = R2cChunkBatchState::new(1);
        let mut clock = R2cBatchTickClock::new(u64::MAX - 10);
        assert!(clock.poll_tick(u64::MAX - 10, &mut batch));
        assert!(!clock.poll_tick(u64::MAX - 1, &mut batch));
        assert_eq!(clock.next_wake_deadline_ms(u64::MAX), u64::MAX);
    }

    #[test]
    fn cache_center_precedes_first_batch_and_retries_without_losing_scratch_or_state() {
        let mut conn = session(16);
        let read_ptr = conn.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(32);
        scratch.push(0xee);
        let scratch_ptr = scratch.as_ptr();
        let mut state =
            R2cChunkBatchState::new_with_initial_cache_center(1, ChunkPos { x: -3, z: 4 });
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(state.unacknowledged_batches(), 0);

        // Entire same-driver egress is occupied by an unrelated control.
        conn.driver.queue_frame::<()>(&[0x72; 15]).unwrap();
        let before = conn.pending_play_egress().to_vec();
        assert!(matches!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Err(DriverError::Buffer(
                ConnectionBufferError::EgressLimitExceeded { .. }
            ))
        ));
        assert_eq!(conn.pending_play_egress(), before);
        assert_eq!(state.pending_center, Some(ChunkPos { x: -3, z: 4 }));
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(state.unacknowledged_batches(), 0);
        assert_eq!(scratch, [0xee]);
        assert_eq!(scratch.as_ptr(), scratch_ptr);
        assert_eq!(conn.read_scratch.as_ptr(), read_ptr);
        conn.consume_play_written(before.len()).unwrap();

        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::CacheCenterQueued { x: -3, z: 4 })
        );
        assert_eq!(scratch, [0xee]);
        assert_eq!(scratch.as_ptr(), scratch_ptr);
        assert_eq!(conn.read_scratch.as_ptr(), read_ptr);
        assert_eq!(state.pending_center, None);
        assert_eq!(state.unacknowledged_batches(), 0);
        assert_eq!(state.next_chunk_index(), 0);
        // One signed x VarInt, then positive z VarInt, 26.2 center ID=94.
        assert_eq!(
            conn.pending_play_egress(),
            [7, 94, 0xfd, 0xff, 0xff, 0xff, 0x0f, 4]
        );

        // The center packet neither consumes quota nor starts a batch.
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::WaitingForTick)
        );
        state.on_tick();
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Started { count: 1 })
        );
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::ChunkQueued {
                index: 0,
                body_bytes: 2
            })
        );
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Finished { count: 1 })
        );
        // Exact center, start, test-only synthetic chunk, finish ordering.
        assert_eq!(
            conn.pending_play_egress(),
            [
                7, 94, 0xfd, 0xff, 0xff, 0xff, 0x0f, 4, 1, 12, 2, 45, 0, 2, 11, 1,
            ]
        );
        assert_eq!(state.next_chunk_index(), 1);
        assert_eq!(state.unacknowledged_batches(), 1);
        assert_eq!(scratch.as_ptr(), scratch_ptr);
        assert_eq!(conn.read_scratch.as_ptr(), read_ptr);
    }

    #[test]
    fn nine_chunk_initial_batch_then_ack_unlocks_new_window() {
        let mut conn = session(128);
        let read_ptr = conn.read_scratch.as_ptr();
        let mut scratch = Vec::with_capacity(32);
        scratch.push(0xfe);
        let scratch_ptr = scratch.as_ptr();
        let mut state = R2cChunkBatchState::new(12);
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk,),
            Ok(ChunkBatchStep::WaitingForTick)
        );
        state.on_tick();
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk,),
            Ok(ChunkBatchStep::Started { count: 9 })
        );
        for index in 0..9 {
            assert_eq!(
                conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk,),
                Ok(ChunkBatchStep::ChunkQueued {
                    index,
                    body_bytes: 2
                })
            );
        }
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Finished { count: 9 })
        );
        assert_eq!(state.next_chunk_index(), 9);
        assert_eq!(state.unacknowledged_batches(), 1);
        assert_eq!(scratch, [0xfe]);
        assert_eq!(scratch.as_ptr(), scratch_ptr);
        assert_eq!(conn.read_scratch.as_ptr(), read_ptr);
        // Start, nine distinct synthetic frames, finish.
        let stream = conn.pending_play_egress();
        assert_eq!(&stream[..2], &[1, 12]);
        assert_eq!(&stream[stream.len() - 3..], &[2, 11, 9]);

        state.on_tick();
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::WaitingForAcknowledgement)
        );
        assert_eq!(state.next_chunk_index(), 9);
        conn.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            conn.process_one_r2c_chunk_batch_ack(&mut state),
            Ok(ChunkBatchInboundStep::Received {
                desired_per_tick: 9.0
            })
        );
        assert_eq!(state.unacknowledged_batches(), 0);
        state.on_tick();
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Started { count: 3 })
        );
        for index in 9..12 {
            assert!(matches!(
                conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
                Ok(ChunkBatchStep::ChunkQueued { index: actual, .. }) if actual == index
            ));
        }
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Finished { count: 3 })
        );
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Complete)
        );
        assert_eq!(conn.read_scratch.as_ptr(), read_ptr);
        assert_eq!(scratch.as_ptr(), scratch_ptr);
    }

    #[test]
    fn source_and_egress_rejection_do_not_advance_start_chunk_or_finish() {
        let mut conn = session(10);
        let mut scratch = vec![0x9a];
        let mut state = R2cChunkBatchState::new(1);
        state.on_tick();
        // Pre-existing framed control bytes fill the egress first.
        conn.driver.queue_frame::<()>(&[0x3f; 9]).unwrap();
        let original = conn.pending_play_egress().to_vec();
        assert!(matches!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Err(DriverError::Buffer(
                ConnectionBufferError::EgressLimitExceeded { .. }
            ))
        ));
        assert_eq!(conn.pending_play_egress(), original);
        assert_eq!(state.unacknowledged_batches(), 0);
        conn.consume_play_written(original.len()).unwrap();

        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Started { count: 1 })
        );
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, |_, bytes| {
                bytes.extend_from_slice(&[45, 99]);
                Err::<(), _>("stale receipt")
            }),
            Err(DriverError::Handler("stale receipt"))
        );
        assert_eq!(state.next_chunk_index(), 0);
        assert_eq!(conn.pending_play_egress(), [1, 12]);
        assert_eq!(scratch, [0x9a]);

        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::ChunkQueued {
                index: 0,
                body_bytes: 2
            })
        );
        // Saturate the same egress: finish must not commit prematurely.
        conn.driver.queue_frame::<()>(&[0xee; 4]).unwrap();
        let full = conn.pending_play_egress().to_vec();
        assert!(matches!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Err(DriverError::Buffer(
                ConnectionBufferError::EgressLimitExceeded { .. }
            ))
        ));
        assert_eq!(conn.pending_play_egress(), full);
        assert_eq!(state.unacknowledged_batches(), 1);
        assert_eq!(state.next_chunk_index(), 1);
        conn.consume_play_written(full.len()).unwrap();
        assert_eq!(
            conn.service_r2c_chunk_batch_one(&mut state, &mut scratch, synthetic_chunk),
            Ok(ChunkBatchStep::Finished { count: 1 })
        );
        assert_eq!(conn.pending_play_egress(), [2, 11, 1]);
    }

    #[test]
    fn inbound_ack_is_transactional_and_unclaimed_packets_are_retained() {
        let mut conn = session(64);
        let mut state = R2cChunkBatchState::new(1);
        conn.ingest_play(&[2, 28, 99]).unwrap();
        assert_eq!(
            conn.process_one_r2c_chunk_batch_ack(&mut state),
            Ok(ChunkBatchInboundStep::Unclaimed { packet_id: 28 })
        );
        assert_eq!(conn.buffered_ingress(), 3);
        // Consume the unrelated frame with the same retained driver.
        let outcome = conn.driver.process_one_transactional::<(), _, _>(|_| {
            Ok(super::PreparedChunkAck {
                next: state,
                desired_per_tick: 9.0,
            })
        });
        assert!(outcome.is_ok());
        assert_eq!(conn.buffered_ingress(), 0);

        conn.ingest_play(&[5, 11, 0x41, 0x10, 0, 0]).unwrap();
        assert_eq!(
            conn.process_one_r2c_chunk_batch_ack(&mut state),
            Err(DriverError::Handler(
                ChunkBatchInboundError::NoFinishedBatchToAcknowledge
            ))
        );
        assert_eq!(conn.buffered_ingress(), 6);
        assert_eq!(state.unacknowledged_batches(), 0);
    }
}
