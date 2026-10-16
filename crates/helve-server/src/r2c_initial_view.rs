//! COLD first-view selection from genuine, source-bound imported chunk receipts.
//!
//! A fixed R2C initial view is chosen exactly once at the R2B `WorldProjection`
//! seam, never discovered by walking the resident directory each batch tick.
//! The caller already owns the receipt Vec. We filter and sort it *in place*;
//! after that the retained R2C batch cursor advances over its immutable order.
//! There are no new packet buffers, source-image copies or HOT world costs.
//!
//! This is a candidate integration seam, NOT live world publication. Exact
//! client registry assignment, heightmap facts and final Play wire/SEM must
//! still be independently source-admitted before connecting this to the
//! stock-client transport loop.

use helve_generated::BlockStateId;
use helve_types::{ChunkPos, DimensionId};
use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_load::{SourceChunkPublicationReceipt, SourceChunkReceiptError};
use helve_world_runtime::SemanticDimensionInstance;

use crate::r2c_chunk_batch::R2cChunkBatchState;

const MIN_VIEW_DISTANCE: i32 = 2;
const MAX_VIEW_DISTANCE: i32 = 32;
const SOURCE_NEIGHBOR_BUFFER: u64 = 2;

/// A caller-supplied initial view cannot be admitted for source-backed chunks.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum InitialViewSelectionError {
    /// Unsupported vanilla configured/requested view distance.
    InvalidViewDistance { actual: i32 },
    /// A receipt belongs to a different resident dimension.
    ForeignDimension {
        position: ChunkPos,
        actual: DimensionId,
        expected: DimensionId,
    },
    /// Two pending entries claim the same chunk column (including stale generations).
    DuplicateReceipt { position: ChunkPos },
    /// A selected source is not the pristine, current, explicitly-empty-entity chunk.
    InvalidReceipt {
        position: ChunkPos,
        error: SourceChunkReceiptError,
    },
    /// The frozen first view contains no imported and verified chunk.
    EmptyView,
}

/// Exactly the source-reviewed vanilla 26.2
/// `ChunkTrackingView.isWithinDistance(..., includeNeighbors=true)` law.
///
/// The source uses a two-chunk neighbor buffer and a strict round-corner
/// inequality. We evaluate coordinate differences as i64 (rather than
/// overflowing i32) and bound reduced coordinates before squaring.
/// This yields identical results throughout the admitted world coordinate
/// range and safely rejects adversarial extreme signed coordinates.
#[must_use]
pub(crate) fn in_initial_view(center: ChunkPos, position: ChunkPos, view_distance: i32) -> bool {
    if !(MIN_VIEW_DISTANCE..=MAX_VIEW_DISTANCE).contains(&view_distance) {
        return false;
    }
    let range = u64::try_from(view_distance).expect("validated positive view distance");
    let x = (i64::from(position.x) - i64::from(center.x))
        .unsigned_abs()
        .saturating_sub(SOURCE_NEIGHBOR_BUFFER);
    let z = (i64::from(position.z) - i64::from(center.z))
        .unsigned_abs()
        .saturating_sub(SOURCE_NEIGHBOR_BUFFER);
    // Checking the axes first avoids overflow even for extreme 32-bit
    // position differences (max possible before the buffer: 2^32-1).
    x < range && z < range && x * x + z * z < range * range
}

fn distance_squared(center: ChunkPos, position: ChunkPos) -> u64 {
    // Only in-view positions reach this ordering key, so each offset
    // is <= 34 and multiplication fits comfortably in u64.
    let dx = (i64::from(position.x) - i64::from(center.x)).unsigned_abs();
    let dz = (i64::from(position.z) - i64::from(center.z)).unsigned_abs();
    dx * dx + dz * dz
}

/// Prepare a complete, fixed, initial publication window without any
/// additional heap allocation. This intentionally borrows the *actual*
/// current dimension and checks each selected receipt before returning an
/// ACK-aware batch state with the same explicit chunk-cache centre.
///
/// Vanilla `PlayerChunkSender.collectChunksToSend` prioritizes squared
/// distance to the player's chunk. We order source-selected receipts by
/// that distance, with a deterministic (x,z) tie-breaker; vanilla ties
/// may be nondeterministic but do not change the packet content.
/// `ChunkTrackingView` uses a round-corner buffered radius rather than
/// a square or a simple unbuffered Euclidean disk.
///
/// `receipts` is a caller-owned COLD input Vec. The operation filters and
/// reorders it on success. On failure it may have been filtered/sorted,
/// but it creates no publication cursor and enqueues **zero** bytes. Do
/// not reuse a failed partial selection as a fresh input.
///
/// The caller must not alter the resulting receipt order until the
/// returned batch cursor completes; each chunk is revalidated against
/// the authoritative resident state at packet projection time.
///
/// # Errors
///
/// Rejects an unsupported distance, foreign or duplicated receipts,
/// stale/mutated or non-empty-source chunks, and a missing initial view.
pub(crate) fn prepare_initial_source_view<BlockStorage, BiomeStorage>(
    dimension: &SemanticDimensionInstance<BlockStateId, BlockStorage, u16, BiomeStorage>,
    receipts: &mut Vec<SourceChunkPublicationReceipt>,
    center: ChunkPos,
    view_distance: i32,
) -> Result<R2cChunkBatchState, InitialViewSelectionError>
where
    BlockStorage: BlockSection<BlockStateId>,
    BiomeStorage: BiomeSection<u16>,
{
    if !(MIN_VIEW_DISTANCE..=MAX_VIEW_DISTANCE).contains(&view_distance) {
        return Err(InitialViewSelectionError::InvalidViewDistance {
            actual: view_distance,
        });
    }
    let expected = dimension.id();
    for receipt in receipts.iter() {
        let handle = receipt.installed().handle;
        if handle.dimension != expected {
            return Err(InitialViewSelectionError::ForeignDimension {
                position: handle.position,
                actual: handle.dimension,
                expected,
            });
        }
    }
    receipts.retain(|receipt| {
        in_initial_view(center, receipt.installed().handle.position, view_distance)
    });
    // One sort on the already-filtered COLD list, no temporary ID vector.
    receipts.sort_unstable_by_key(|receipt| {
        let pos = receipt.installed().handle.position;
        (distance_squared(center, pos), pos.x, pos.z)
    });
    if receipts.is_empty() {
        return Err(InitialViewSelectionError::EmptyView);
    }
    for pair in receipts.windows(2) {
        let left = pair[0].installed().handle.position;
        let right = pair[1].installed().handle.position;
        if left == right {
            return Err(InitialViewSelectionError::DuplicateReceipt { position: left });
        }
    }
    for receipt in receipts.iter() {
        let position = receipt.installed().handle.position;
        receipt
            .resolve_explicitly_empty(dimension)
            .map_err(|error| InitialViewSelectionError::InvalidReceipt { position, error })?;
    }
    Ok(R2cChunkBatchState::new_with_initial_cache_center(
        receipts.len(),
        center,
    ))
}

#[cfg(test)]
mod tests {
    use helve_types::ChunkPos;

    use super::in_initial_view;

    #[test]
    fn exact_two_chunk_buffer_strict_radius_and_round_corners() {
        let center = ChunkPos { x: -7, z: 11 };
        assert!(in_initial_view(center, center, 2));
        assert!(in_initial_view(center, ChunkPos { x: -4, z: 11 }, 2));
        assert!(in_initial_view(center, ChunkPos { x: -4, z: 14 }, 2));
        assert!(!in_initial_view(center, ChunkPos { x: -3, z: 11 }, 2));
        assert!(!in_initial_view(center, ChunkPos { x: -3, z: 14 }, 2));
        assert!(in_initial_view(center, ChunkPos { x: -10, z: 8 }, 2));
        assert!(!in_initial_view(center, ChunkPos { x: -11, z: 8 }, 2));
        assert!(!in_initial_view(center, center, 0));
        assert!(!in_initial_view(center, center, 33));
    }

    #[test]
    fn extreme_coordinates_do_not_overflow_or_select_foreign_world() {
        let center = ChunkPos {
            x: i32::MIN,
            z: i32::MAX,
        };
        assert!(in_initial_view(center, center, 32));
        assert!(!in_initial_view(
            center,
            ChunkPos {
                x: i32::MAX,
                z: i32::MIN
            },
            32,
        ));
        assert!(in_initial_view(
            center,
            ChunkPos {
                x: i32::MIN + 33,
                z: i32::MAX
            },
            32,
        ));
        assert!(!in_initial_view(
            center,
            ChunkPos {
                x: i32::MIN + 34,
                z: i32::MAX
            },
            32,
        ));
    }
}
