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

fn checked_read_into<E>(
    path: &Path,
    limit: usize,
    bytes: &mut Vec<u8>,
) -> Result<(), PregeneratedRegionError<E>> {
    if limit == 0 {
        return Err(PregeneratedRegionError::InvalidLimits);
    }
    let bounded = u64::try_from(limit).map_err(|_| PregeneratedRegionError::InvalidLimits)?;
    let cap = bounded
        .checked_add(1)
        .ok_or(PregeneratedRegionError::InvalidLimits)?;
    let metadata = fs::symlink_metadata(path).map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    if !metadata.is_file() || metadata.file_type().is_symlink() {
        return Err(PregeneratedRegionError::InvalidSourceFile);
    }
    if metadata.len() > bounded {
        return Err(PregeneratedRegionError::FileExceedsLimit { limit });
    }
    let mut file = File::open(path).map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    bytes.clear();
    file.by_ref()
        .take(cap)
        .read_to_end(bytes)
        .map_err(|e| PregeneratedRegionError::Io(e.kind()))?;
    if bytes.len() > limit {
        return Err(PregeneratedRegionError::FileExceedsLimit { limit });
    }
    Ok(())
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
///
/// # Panics
///
/// Only if a validated modulo-32 coordinate cannot be represented in
/// a u8/usize, which is impossible on supported targets.
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
        let selected_word = &mut seen[slot / 64];
        if *selected_word & mask != 0 {
            return Err(PregeneratedRegionError::DuplicatePosition { position });
        }
        *selected_word |= mask;
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
    let mut bytes = Vec::new();
    checked_read_into(&path, limits.region.max_region_bytes, &mut bytes)?;
    let region = RegionView::new(&bytes, region_x, region_z, limits.region)
        .map_err(PregeneratedRegionError::Region)?;
    // External bytes are short-lived borrowed input, not retained world
    // state. Reuse capacity across consecutive external records.
    let mut external_scratch = Vec::new();

    for &position in selected {
        let local_x = u8::try_from(position.x.rem_euclid(REGION_AXIS)).expect("0..31");
        let local_z = u8::try_from(position.z.rem_euclid(REGION_AXIS)).expect("0..31");
        let chunk = region
            .chunk(local_x, local_z)
            .map_err(PregeneratedRegionError::Chunk)?
            .ok_or(PregeneratedRegionError::MissingChunk { position })?;

        let external_payload = if chunk.external {
            let path = directory.join(format!("c.{}.{}.mcc", position.x, position.z));
            checked_read_into(&path, limits.max_external_bytes, &mut external_scratch)?;
            Some(ExternalChunkPayload {
                bytes: external_scratch.as_slice(),
            })
        } else {
            None
        };
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

#[cfg(test)]
mod tests {
    use std::fs;
    use std::path::{Path, PathBuf};
    use std::sync::atomic::{AtomicU64, Ordering};

    use helve_types::ChunkPos;
    use helve_world_import::RegionLimits;

    use super::{
        PregeneratedRegionError, PregeneratedRegionLimits, visit_pregenerated_region,
    };

    static NEXT_WORLD: AtomicU64 = AtomicU64::new(0);
    const SECTOR: usize = 4096;

    struct TestWorld {
        root: PathBuf,
    }

    impl TestWorld {
        fn new() -> Self {
            let number = NEXT_WORLD.fetch_add(1, Ordering::Relaxed);
            let root = std::env::temp_dir().join(format!(
                "helve-r2c-pregenerated-files-{}-{number}",
                std::process::id()
            ));
            fs::create_dir_all(root.join("region")).unwrap();
            Self { root }
        }

        fn path(&self) -> &Path {
            &self.root
        }

        fn write_region(&self, region: &[u8]) {
            fs::write(self.root.join("region/r.0.0.mca"), region).unwrap();
        }

        fn write_external(&self, bytes: &[u8]) {
            fs::write(self.root.join("region/c.0.0.mcc"), bytes).unwrap();
        }
    }

    impl Drop for TestWorld {
        fn drop(&mut self) {
            fs::remove_dir_all(&self.root).unwrap();
        }
    }

    fn limits() -> PregeneratedRegionLimits {
        PregeneratedRegionLimits {
            region: RegionLimits::new(8 * SECTOR, SECTOR),
            max_external_bytes: 16,
        }
    }

    fn region(records: &[(u8, &[u8])]) -> Vec<u8> {
        let mut region = vec![0_u8; (records.len() + 2) * SECTOR];
        for (slot, &(compression, payload)) in records.iter().enumerate() {
            let offset = 2 + slot;
            let location = (u32::try_from(offset).unwrap() << 8) | 1;
            region[slot * 4..slot * 4 + 4].copy_from_slice(&location.to_be_bytes());
            region[SECTOR + slot * 4..SECTOR + slot * 4 + 4]
                .copy_from_slice(&u32::try_from(slot + 10).unwrap().to_be_bytes());
            let start = offset * SECTOR;
            region[start..start + 4]
                .copy_from_slice(&u32::try_from(payload.len() + 1).unwrap().to_be_bytes());
            region[start + 4] = compression;
            region[start + 5..start + 5 + payload.len()].copy_from_slice(payload);
        }
        region
    }

    #[test]
    fn selected_chunks_share_one_borrowed_region_snapshot_in_requested_order() {
        let world = TestWorld::new();
        world.write_region(&region(&[(3, b"first"), (3, b"second")]));
        let selected = [ChunkPos { x: 1, z: 0 }, ChunkPos { x: 0, z: 0 }];
        let mut observed = Vec::new();
        let count = visit_pregenerated_region(
            world.path(),
            0,
            0,
            &selected,
            limits(),
            |source| {
                let chunk = source.region.chunk(source.local_x, source.local_z).unwrap().unwrap();
                observed.push((chunk.position, chunk.inline_payload.unwrap().to_vec()));
                assert!(source.external_payload.is_none());
                // Once the whole region is in memory, subsequent selected
                // chunks do not re-open/re-read its file.
                if source.local_x == 1 {
                    fs::remove_file(world.path().join("region/r.0.0.mca")).unwrap();
                }
                Ok::<_, ()>(())
            },
        )
        .unwrap();
        assert_eq!(count, 2);
        assert_eq!(
            observed,
            vec![
                (ChunkPos { x: 1, z: 0 }, b"second".to_vec()),
                (ChunkPos { x: 0, z: 0 }, b"first".to_vec())
            ]
        );
    }

    #[test]
    fn external_record_requires_its_own_bounded_file_and_never_uses_padding() {
        let world = TestWorld::new();
        world.write_region(&region(&[(0x80 | 3, b"padding")]));
        let pos = [ChunkPos { x: 0, z: 0 }];
        assert!(matches!(
            visit_pregenerated_region(
                world.path(), 0, 0, &pos, limits(), |_| Ok::<_, ()>(())
            ),
            Err(PregeneratedRegionError::Io(_))
        ));
        world.write_external(b"real-external");
        assert_eq!(
            visit_pregenerated_region(world.path(), 0, 0, &pos, limits(), |source| {
                assert_eq!(source.external_payload.unwrap().bytes, b"real-external");
                assert!(source.region.chunk(0, 0).unwrap().unwrap().inline_payload.is_none());
                Ok::<_, ()>(())
            })
            .unwrap(),
            1
        );
        world.write_external(&[0; 17]);
        assert!(matches!(
            visit_pregenerated_region(
                world.path(), 0, 0, &pos, limits(), |_| Ok::<_, ()>(())
            ),
            Err(PregeneratedRegionError::FileExceedsLimit { limit: 16 })
        ));
    }

    #[test]
    fn two_external_records_reuse_one_bounded_source_buffer() {
        let world = TestWorld::new();
        world.write_region(&region(&[
            (0x80 | 3, b"padding-a"),
            (0x80 | 3, b"padding-b"),
        ]));
        world.write_external(b"long-first-payload");
        fs::write(world.path().join("region/c.1.0.mcc"), b"next").unwrap();

        let selected = [ChunkPos { x: 0, z: 0 }, ChunkPos { x: 1, z: 0 }];
        let mut pointers = Vec::new();
        let mut lengths = Vec::new();
        let count = visit_pregenerated_region(
            world.path(),
            0,
            0,
            &selected,
            PregeneratedRegionLimits {
                region: RegionLimits::new(8 * SECTOR, SECTOR),
                max_external_bytes: 32,
            },
            |source| {
                let external = source.external_payload.expect("selected external record");
                pointers.push(external.bytes.as_ptr());
                lengths.push(external.bytes.len());
                Ok::<_, ()>(())
            },
        )
        .unwrap();
        assert_eq!(count, 2);
        assert_eq!(lengths, [18, 4]);
        assert_eq!(pointers[0], pointers[1], "second external record must reuse COLD bytes");
    }

    #[test]
    fn invalid_selection_fails_before_ever_opening_files_or_visiting_chunks() {
        let world = TestWorld::new();
        let mut calls = 0;
        let duplicate = [ChunkPos { x: 0, z: 0 }, ChunkPos { x: 0, z: 0 }];
        assert!(matches!(
            visit_pregenerated_region(world.path(), 0, 0, &duplicate, limits(), |_| {
                calls += 1;
                Ok::<_, ()>(())
            }),
            Err(PregeneratedRegionError::DuplicatePosition { .. })
        ));
        let foreign = [ChunkPos { x: 32, z: 0 }];
        assert!(matches!(
            visit_pregenerated_region(world.path(), 0, 0, &foreign, limits(), |_| {
                calls += 1;
                Ok::<_, ()>(())
            }),
            Err(PregeneratedRegionError::ForeignPosition { .. })
        ));
        assert_eq!(calls, 0);
        assert_eq!(
            visit_pregenerated_region(world.path(), 0, 0, &[], limits(), |_| {
                calls += 1;
                Ok::<_, ()>(())
            }).unwrap(),
            0
        );
        assert_eq!(calls, 0);
    }

    #[test]
    fn missing_selected_chunk_and_bad_region_framing_never_enter_caller() {
        let world = TestWorld::new();
        world.write_region(&region(&[(3, b"first")]));
        let pos = [ChunkPos { x: 3, z: 0 }];
        assert!(matches!(
            visit_pregenerated_region(world.path(), 0, 0, &pos, limits(), |_| -> Result<(), ()> {
                panic!("absent chunk must not be visited");
            }),
            Err(PregeneratedRegionError::MissingChunk { .. })
        ));
        world.write_region(&[0; 16]);
        assert!(matches!(
            visit_pregenerated_region(world.path(), 0, 0, &pos, limits(), |_| -> Result<(), ()> {
                panic!("invalid region must not reach callback");
            }),
            Err(PregeneratedRegionError::Region(_))
        ));
    }

    #[cfg(unix)]
    #[test]
    fn symbolic_linked_region_file_is_rejected_before_read() {
        use std::os::unix::fs::symlink;

        let world = TestWorld::new();
        let source = world.path().join("source.mca");
        fs::write(&source, region(&[(3, b"first")])).unwrap();
        symlink(&source, world.path().join("region/r.0.0.mca")).unwrap();
        let pos = [ChunkPos { x: 0, z: 0 }];
        assert!(matches!(
            visit_pregenerated_region(world.path(), 0, 0, &pos, limits(), |_| Ok::<_, ()>(())),
            Err(PregeneratedRegionError::InvalidSourceFile)
        ));
    }
}
