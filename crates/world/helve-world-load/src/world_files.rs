//! Bounded COLD file ingress for a selected set of pregenerated Anvil
//! chunks from one on-disk region. The selection belongs to the caller:
//! this module does not scan a whole world, choose a spawn, manufacture
//! missing chunks, or create another authoritative world representation.
//!
//! One validated region byte buffer is retained throughout a callback
//! sequence; optional external `.mcc` payloads are individually bounded
//! and released after each caller's synchronous import transaction.
//! The only callback input is `SelectedAnvilSource`, directly compatible
//! with `import_and_install_anvil_source`. No HOT world/packet work.

use std::fs::{self, File};
use std::io::{self, Read};
use std::path::Path;

use helve_types::ChunkPos;
use helve_world_import::{
    ExternalChunkPayload, RegionError, RegionLimits, RegionView,
};

use crate::SelectedAnvilSource;

const REGION_AXIS: i32 = 32;
const REGION_SLOTS: usize = 1024;
const SLOT_MASK_WORDS: usize = REGION_SLOTS / 64;

/// Caller-selected finite bounds for one real pregenerated region and
/// its separately stored external records.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct PregeneratedRegionLimits {
    /// Bounded Anvil framing, including maximum inline compressed record.
    pub region: RegionLimits,
    /// Maximum compressed bytes allowed from one external `.mcc` record.
    pub max_external_bytes: usize,
}

/// A selected on-disk source cannot be loaded without weakening its
/// exact region/chunk/evidence identity or caller-owned limits.
#[derive(Debug)]
pub enum PregeneratedRegionError<E> {
    /// At least one explicit bound was zero or a read bound overflowed.
    InvalidLimits,
    /// A caller selected more than the 1024 slots available in a region.
    TooManyChunks { count: usize },
    /// The given absolute chunk position does not belong to this region.
    ForeignPosition {
        position: ChunkPos,
        region_x: i32,
        region_z: i32,
    },
    /// A selected position occurred twice in one requested batch.
    DuplicatePosition { position: ChunkPos },
    /// Selected region directory is absent, not a directory or a link.
    InvalidRegionDirectory,
    /// A selected file is a link or not a regular file.
    InvalidSourceFile,
    /// Reading a selected source file failed.
    Io(io::ErrorKind),
    /// The read source grew larger than its explicit cap.
    FileExceedsLimit { limit: usize },
    /// The Anvil header/sector-location framing failed validation.
    Region(RegionError),
    /// The caller-selected source slot is not present in the region file.
    MissingChunk { position: ChunkPos },
    /// One selected region chunk's metadata was invalid.
    Chunk(RegionError),
    /// The caller's synchronous source decoder/installer rejected this slot.
    Visit(E),
}

fn checked_read<E>(
    path: &Path,
    limit: usize,
) -> Result<Vec<u8>, PregeneratedRegionError<E>> {
    if limit == 0 {
        return Err(PregeneratedRegionError::InvalidLimits);
    }
    let cap = u64::try_from(limit)
        .ok()
        .and_then(|n| n.checked_add(1))
        .ok_or(PregeneratedRegionError::InvalidLimits)?;
    let metadata = fs::symlink_metadata(path).map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    if !metadata.is_file() || metadata.file_type().is_symlink() {
        return Err(PregeneratedRegionError::InvalidSourceFile);
    }
    if metadata.len() > u64::try_from(limit).expect("limit was validated") {
        return Err(PregeneratedRegionError::FileExceedsLimit { limit });
    }
    let mut file = File::open(path).map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    let mut bytes = Vec::new();
    file.by_ref()
        .take(cap)
        .read_to_end(&mut bytes)
        .map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    if bytes.len() > limit {
        return Err(PregeneratedRegionError::FileExceedsLimit { limit });
    }
    Ok(bytes)
}

/// Read one region exactly once, validate the caller-selected positions,
/// and synchronously visit only those stored chunks. There is no global
/// directory traversal, coordinate-to-name guessing, or repeated region
/// materialization per chunk.
///
/// Region/chunk membership and duplicate checks happen before file I/O;
/// all region framing is checked before any callback. External `.mcc`
/// payloads are read only for records that explicitly carry the external
/// flag. The caller supplies the qualified decoder/installer and keeps
/// authoritative world ownership. This boundary does **not** guarantee
/// all-or-nothing admission of an entire *multiple-chunk* view; each
/// source receipt is transactional separately.
///
/// # Errors
///
/// Returns a fail-closed error on malformed caller selection, unbounded
/// or unsupported file, malformed source framing, absent selected chunk,
/// unsupported external bytes, or any callback admission failure.
pub fn visit_pregenerated_region<E>(
    world: &Path,
    region_x: i32,
    region_z: i32,
    selected: &[ChunkPos],
    limits: PregeneratedRegionLimits,
    mut visit: impl for<'a, 'r> FnMut(SelectedAnvilSource<'a, 'r>) -> Result<(), E>,
) -> Result<usize, PregeneratedRegionError<E>> {
    if selected.len() > REGION_SLOTS {
        return Err(PregeneratedRegionError::TooManyChunks {
            count: selected.len(),
        });
    }
    if limits.region.max_region_bytes == 0
        || limits.region.max_inline_chunk_payload_bytes == 0
        || limits.max_external_bytes == 0
    {
        return Err(PregeneratedRegionError::InvalidLimits);
    }
    // One fixed 128-byte stack bitset rejects all duplicate slots, with
    // no per-chunk hash lookup, allocation or quadratic preflight.
    let mut seen = [0_u64; SLOT_MASK_WORDS];
    for &position in selected {
        if position.x.div_euclid(REGION_AXIS) != region_x
            || position.z.div_euclid(REGION_AXIS) != region_z
        {
            return Err(PregeneratedRegionError::ForeignPosition {
                position,
                region_x,
                region_z,
            });
        }
        let slot = usize::try_from(position.z.rem_euclid(REGION_AXIS)).expect("0..31")
            * 32
            + usize::try_from(position.x.rem_euclid(REGION_AXIS)).expect("0..31");
        let mask = 1_u64 << (slot % 64);
        let word = &mut seen[slot / 64];
        if *word & mask != 0 {
            return Err(PregeneratedRegionError::DuplicatePosition { position });
        }
        *word |= mask;
    }
    if selected.is_empty() {
        return Ok(0);
    }

    let directory = world.join("region");
    let metadata = fs::symlink_metadata(&directory)
        .map_err(|_| PregeneratedRegionError::InvalidRegionDirectory)?;
    if !metadata.is_dir() || metadata.file_type().is_symlink() {
        return Err(PregeneratedRegionError::InvalidRegionDirectory);
    }
    let path = directory.join(format!("r.{region_x}.{region_z}.mca"));
    let bytes = checked_read(&path, limits.region.max_region_bytes)?;
    let region = RegionView::new(&bytes, region_x, region_z, limits.region)
        .map_err(PregeneratedRegionError::Region)?;

    for &position in selected {
        let local_x = u8::try_from(position.x.rem_euclid(REGION_AXIS)).expect("0..31");
        let local_z = u8::try_from(position.z.rem_euclid(REGION_AXIS)).expect("0..31");
        let chunk = region
            .chunk(local_x, local_z)
            .map_err(PregeneratedRegionError::Chunk)?
            .ok_or(PregeneratedRegionError::MissingChunk { position })?;

        let external = if chunk.external {
            let path = directory.join(format!("c.{}.{}.mcc", position.x, position.z));
            Some(checked_read(&path, limits.max_external_bytes)?)
        } else {
            None
        };
        let external_payload = external
            .as_deref()
            .map(|bytes| ExternalChunkPayload { bytes });
        visit(SelectedAnvilSource {
            region: &region,
            local_x,
            local_z,
            external_payload,
        })
        .map_err(PregeneratedRegionError::Visit)?;
    }
    Ok(selected.len())
}
