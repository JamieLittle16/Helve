//! Source-independent R2C publication admission through the continuing R2B Play owner.
//!
//! This module deliberately knows no Minecraft 26.2 world packet identities or payload law. The
//! target encoder remains responsible for producing complete Play packet bodies. R2C only needs a
//! narrow way to admit those already-formed bodies through the exact bounded driver that survived
//! the R2B `WorldProjection` handoff.

use std::convert::Infallible;

use helve_connection_core::ConnectionLimits;
use helve_connection_driver::DriverError;
use helve_publication_core::{
    PublicationCursor, PublicationStep, publish_one, publish_projected_one,
};

use crate::r2b_server::{R2bPlayError, R2bPlaySession};

impl R2bPlaySession {
    /// Widen the original R2B driver for the largest legal Minecraft Play
    /// frame without recreating either buffer or the continuing connection.
    ///
    /// The 26.2 chunk-data decoder independently allows up to 2 MiB of
    /// section bytes, while the outer remote frame caps the *entire* body
    /// at 2 MiB minus one. A real chunk might exceed R2B's 64 KiB cap,
    /// even when its section bytes are valid. The new ingress/egress
    /// ceilings are hard resource bounds, not eagerly reserved memory.
    ///
    /// This intentionally does **not** publish world bytes or authorize
    /// biome registry IDs, the source profile or gameplay packet routing.
    ///
    /// # Errors
    ///
    /// Preserves existing buffer bytes and limits if the proposed complete
    /// limit set is invalid or tighter than any current bound.
    #[cfg_attr(
        not(test),
        expect(
            dead_code,
            reason = "source/admission-gated R2C world runtime will call this at the retained Play handoff"
        )
    )]
    pub(crate) fn widen_play_limits_for_chunks(&mut self) -> Result<(), R2bPlayError> {
        const MAX_PLAY_BODY: usize = (1 << 21) - 1;
        const INGRESS_LIMIT: usize = 3 * 1_024 * 1_024;
        const EGRESS_LIMIT: usize = 4 * 1_024 * 1_024;
        let limits = ConnectionLimits::new(MAX_PLAY_BODY, INGRESS_LIMIT, EGRESS_LIMIT)
            .map_err(R2bPlayError::Buffer)?;
        self.driver.widen_limits(limits).map_err(R2bPlayError::Buffer)
    }

    /// Atomically admits one target-encoded Play publication batch to the continuing connection.
    ///
    /// Every body must already contain the target-owned packet-ID `VarInt` followed by its payload.
    /// This method performs no packet lookup, world projection, semantic defaulting, or secondary
    /// buffering. It reuses the exact [`helve_connection_driver::ConnectionDriver`] retained across
    /// the R2B `WorldProjection` handoff.
    ///
    /// The complete batch is admitted or rejected as one bounded-egress transaction. A capacity or
    /// frame-law failure leaves the logical egress queue unchanged, so an R2C publication cursor may
    /// advance only after this method succeeds.
    ///
    /// This raw-body seam is intentionally crate-visible only. Target/world composition inside
    /// `helve-server` may use it, but the public [`R2bPlaySession`] API must not become an arbitrary
    /// packet-injection surface.
    ///
    /// # Errors
    ///
    /// Returns the existing fail-closed Play/driver error when the batch violates framing or egress
    /// bounds. Rejection does not partially append the batch.
    #[cfg_attr(
        not(test),
        expect(
            dead_code,
            reason = "R2C projector integration is source-admission blocked; remove when it becomes the production caller"
        )
    )]
    pub(crate) fn admit_play_publication_batch<B>(
        &mut self,
        bodies: &[B],
    ) -> Result<(), R2bPlayError>
    where
        B: AsRef<[u8]>,
    {
        self.driver
            .queue_batch::<Infallible, B>(bodies)
            .map_err(|error| map_publication_driver_error(&error))
    }

    /// Services at most one body from an ordered immutable Play publication.
    ///
    /// The caller owns both the immutable publication and the allocation-free one-word cursor. This
    /// wrapper deliberately reuses [`helve_publication_core::publish_one`] rather than introducing an
    /// R2C-specific cursor or queue. A successful call admits at most one already target-encoded
    /// body through the exact continuing Play driver and advances `cursor` exactly once. Egress
    /// backpressure or frame rejection leaves both the cursor and existing egress unchanged.
    ///
    /// This is the fairness-oriented path for a potentially large world publication. Atomic groups
    /// that genuinely require all-or-nothing egress admission may use
    /// [`Self::admit_play_publication_batch`] instead. Like the atomic raw-body seam, this method is
    /// crate-visible only so external users cannot bypass target-owned packet semantics.
    ///
    /// # Errors
    ///
    /// Returns the existing fail-closed Play/driver error without advancing `cursor` when the next
    /// body violates framing or bounded-egress capacity.
    #[cfg_attr(
        not(test),
        expect(
            dead_code,
            reason = "R2C projector integration is source-admission blocked; remove when it becomes the production caller"
        )
    )]
    pub(crate) fn service_play_publication_one<B>(
        &mut self,
        publication: &[B],
        cursor: &mut PublicationCursor,
    ) -> Result<PublicationStep, R2bPlayError>
    where
        B: AsRef<[u8]>,
    {
        publish_one::<Infallible, B>(publication, cursor, &mut self.driver)
            .map_err(|error| map_publication_driver_error(&error))
    }

    /// Projects and admits only the next ordered COLD item through this same Play driver.
    ///
    /// The caller retains a fixed ordered selection of semantic chunk receipts (not serialized
    /// packets). It validates the selected receipt and appends one target-owned complete packet
    /// body into reusable scratch. After admission, scratch length is restored and the existing
    /// one-word cursor advances. A failed projection or bounded-egress rejection preserves both
    /// cursor position and existing outbound bytes; there is no separate per-player packet queue.
    ///
    /// This is intentionally dormant until the exact R2C packet ID, numeric biome registry and
    /// initial publication laws have passed their independent source gates.
    ///
    /// # Errors
    ///
    /// Returns the projector error or existing bounded Play-driver rejection unchanged.
    #[cfg_attr(
        not(test),
        expect(
            dead_code,
            reason = "R2C chunk packet and biome source admission block production projection"
        )
    )]
    pub(crate) fn service_play_projected_one<E>(
        &mut self,
        item_count: usize,
        cursor: &mut PublicationCursor,
        scratch: &mut Vec<u8>,
        append_one: impl FnOnce(usize, &mut Vec<u8>) -> Result<(), E>,
    ) -> Result<PublicationStep, DriverError<E>> {
        publish_projected_one(item_count, cursor, &mut self.driver, scratch, append_one)
    }
}

#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "only the intentionally dormant internal R2C publication seams use this mapper"
    )
)]
fn map_publication_driver_error(error: &DriverError<Infallible>) -> R2bPlayError {
    match error {
        DriverError::Buffer(error) => R2bPlayError::Buffer(*error),
        DriverError::Handler(never) => match *never {},
        DriverError::RollbackFailed {
            operation,
            rollback,
        } => R2bPlayError::RollbackFailed {
            operation: *operation,
            rollback: *rollback,
        },
        DriverError::AccountingOverflow => R2bPlayError::AccountingOverflow,
    }
}

#[cfg(test)]
mod tests {
    use std::convert::Infallible;

    use helve_connection_core::ConnectionLimits;
    use helve_connection_driver::ConnectionDriver;
    use helve_publication_core::{PublicationCursor, PublicationStep};
    use helve_session_core::LivenessState;
    use helve_target_26_2::r2b::TeleportTransaction;

    use crate::r2b_server::{R2bPlayError, R2bPlaySession};

    fn limits(max_egress: usize) -> ConnectionLimits {
        ConnectionLimits::new(8, 128, max_egress).expect("valid test connection limits")
    }

    fn session(max_egress: usize) -> R2bPlaySession {
        R2bPlaySession {
            driver: ConnectionDriver::new(limits(max_egress)),
            read_scratch: vec![0_u8; 32].into_boxed_slice(),
            teleport: TeleportTransaction::new(),
            liveness: LivenessState::new(0, 0).expect("zero is a valid liveness origin"),
        }
    }

    fn independently_framed(max_egress: usize, bodies: &[Vec<u8>]) -> Vec<u8> {
        let mut driver = ConnectionDriver::new(limits(max_egress));
        driver
            .queue_batch::<Infallible, _>(bodies)
            .expect("independent framing fits");
        driver.pending_egress().to_vec()
    }

    #[test]
    fn world_phase_accepts_large_legal_chunk_frame_on_same_r2b_session() {
        let mut session = session(128);
        let original_read_scratch = session.read_scratch.as_ptr();
        session.admit_play_publication_batch(&[&[0x2c, 0xaa]]).unwrap();
        let queued = session.pending_play_egress().to_vec();
        let old_allocation = session.pending_play_egress().as_ptr();
        assert!(matches!(
            session.admit_play_publication_batch(&[vec![0x2d; 65_537]]),
            Err(R2bPlayError::Buffer(_))
        ));

        session.widen_play_limits_for_chunks().unwrap();
        assert_eq!(session.pending_play_egress(), queued);
        assert_eq!(session.pending_play_egress().as_ptr(), old_allocation);
        assert_eq!(session.read_scratch.as_ptr(), original_read_scratch);
        session.admit_play_publication_batch(&[vec![0x2d; 65_537]]).unwrap();
        assert!(session.pending_play_egress().starts_with(&queued));
        assert_eq!(session.read_scratch.as_ptr(), original_read_scratch);
        // Repeated no-op widening cannot discard already-admitted bytes.
        let complete = session.pending_play_egress().to_vec();
        session.widen_play_limits_for_chunks().unwrap();
        assert_eq!(session.pending_play_egress(), complete);
    }

    #[test]
    fn cold_projection_reuses_live_r2b_driver_without_a_packet_list() {
        let mut session = session(10);
        let original_read_scratch = session.read_scratch.as_ptr();
        let mut cursor = PublicationCursor::new();
        let mut scratch = Vec::with_capacity(32);
        scratch.push(0xEE);
        let original_projection_allocation = scratch.as_ptr();
        let encode = |index: usize, output: &mut Vec<u8>| {
            output.push(0x11);
            output.extend_from_slice(&[u8::try_from(index).expect("two selected indices"); 7]);
            Ok::<(), &'static str>(())
        };

        assert_eq!(
            session.service_play_projected_one(2, &mut cursor, &mut scratch, encode),
            Ok(PublicationStep::Queued {
                index: 0,
                body_bytes: 8
            })
        );
        assert_eq!(cursor.next_index(), 1);
        assert_eq!(scratch, [0xEE]);
        let before = session.pending_play_egress().to_vec();

        assert!(matches!(
            session.service_play_projected_one(2, &mut cursor, &mut scratch, encode),
            Err(helve_connection_driver::DriverError::Buffer(_))
        ));
        assert_eq!(cursor.next_index(), 1);
        assert_eq!(session.pending_play_egress(), before);
        assert_eq!(scratch, [0xEE]);
        assert_eq!(scratch.as_ptr(), original_projection_allocation);
        assert_eq!(session.read_scratch.as_ptr(), original_read_scratch);

        session
            .consume_play_written(before.len())
            .expect("drain admitted packet");
        assert_eq!(
            session.service_play_projected_one(2, &mut cursor, &mut scratch, encode),
            Ok(PublicationStep::Queued {
                index: 1,
                body_bytes: 8
            })
        );
        assert_eq!(cursor.next_index(), 2);
        assert_eq!(
            session.service_play_projected_one::<&'static str>(
                2,
                &mut cursor,
                &mut scratch,
                |_, _| panic!("must not project completed item"),
            ),
            Ok(PublicationStep::Complete)
        );
        assert_eq!(scratch, [0xEE]);
    }

    #[test]
    fn publication_batch_reuses_continuing_driver_and_preserves_body_order() {
        let bodies = vec![vec![0x11, 0xAA], vec![0x22, 0xBB, 0xCC], vec![0x33]];
        let expected = independently_framed(128, &bodies);
        let mut session = session(128);

        assert_eq!(session.queued_egress(), 0);
        session
            .admit_play_publication_batch(&bodies)
            .expect("bounded publication batch");

        assert_eq!(session.pending_play_egress(), expected);
        assert_eq!(session.queued_egress(), expected.len());
    }

    #[test]
    fn publication_batch_backpressure_is_atomic_against_existing_egress() {
        let mut session = session(10);
        let prefix = [vec![0x01, 0xAA]];
        session
            .admit_play_publication_batch(&prefix)
            .expect("prefix fits");
        let before = session.pending_play_egress().to_vec();

        let rejected = [vec![0x10, 1, 2], vec![0x11, 3, 4]];
        let error = session
            .admit_play_publication_batch(&rejected)
            .expect_err("complete batch exceeds remaining bounded egress");

        assert!(matches!(error, R2bPlayError::Buffer(_)));
        assert_eq!(session.pending_play_egress(), before);
        assert_eq!(session.queued_egress(), before.len());
    }

    #[test]
    fn publication_cursor_queues_at_most_one_body_per_service_opportunity() {
        let publication = [vec![0x10, 1, 2], vec![0x11, 3, 4]];
        let mut cursor = PublicationCursor::new();
        let mut session = session(128);

        assert_eq!(
            session.service_play_publication_one(&publication, &mut cursor),
            Ok(PublicationStep::Queued {
                index: 0,
                body_bytes: 3,
            })
        );
        assert_eq!(cursor.next_index(), 1);
        let first_egress = session.pending_play_egress().to_vec();

        assert_eq!(
            session.service_play_publication_one(&publication, &mut cursor),
            Ok(PublicationStep::Queued {
                index: 1,
                body_bytes: 3,
            })
        );
        assert_eq!(cursor.next_index(), 2);
        assert!(cursor.is_complete(&publication));
        assert!(session.pending_play_egress().starts_with(&first_egress));

        assert_eq!(
            session.service_play_publication_one(&publication, &mut cursor),
            Ok(PublicationStep::Complete)
        );
        assert_eq!(cursor.next_index(), 2);
    }

    #[test]
    fn publication_cursor_backpressure_does_not_advance_progress() {
        let publication = [vec![0x10, 1, 2, 3, 4], vec![0x11, 5, 6, 7, 8]];
        let mut cursor = PublicationCursor::new();
        let mut session = session(10);

        session
            .service_play_publication_one(&publication, &mut cursor)
            .expect("first framed body fits");
        assert_eq!(cursor.next_index(), 1);
        let before = session.pending_play_egress().to_vec();

        let error = session
            .service_play_publication_one(&publication, &mut cursor)
            .expect_err("second framed body observes bounded backpressure");
        assert!(matches!(error, R2bPlayError::Buffer(_)));
        assert_eq!(cursor.next_index(), 1);
        assert_eq!(session.pending_play_egress(), before);
    }
}
