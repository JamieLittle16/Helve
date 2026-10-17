//! Narrow COLD version check for the root metadata of an official 26.2 save.
//!
//! The caller supplies bounded, independently gzip-verified `level.dat` NBT.
//! This source-format check has no world-resident owner, packet authority or
//! known-pack/biome-ID admission. It reuses the standard bounded NBT reader
//! instead of introducing a generic NBT tree or a second source parser.

use crate::chunk::TARGET_DATA_VERSION_26_2;
use crate::nbt::{NbtError, NbtLimits, NbtReader, TagType};

/// An exact-target saved-world root metadata check failed.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LevelMetadataError {
    /// The shared bounded NBT reader rejected the payload.
    Nbt(NbtError),
    /// `level.dat` has an unexpected named NBT root.
    NamedRoot,
    /// The mandatory saved-world `Data` compound is absent.
    MissingData,
    /// The saved-world `Data` compound occurs more than once.
    DuplicateData,
    /// The `Data` field is not a compound.
    WrongDataTag { actual: TagType },
    /// `Data.DataVersion` is absent.
    MissingDataVersion,
    /// `Data.DataVersion` occurs more than once.
    DuplicateDataVersion,
    /// `Data.DataVersion` is not a signed 32-bit integer.
    WrongDataVersionTag { actual: TagType },
    /// This save cannot be interpreted under the selected 26.2 importer.
    WrongDataVersion { observed: i32 },
}

impl From<NbtError> for LevelMetadataError {
    fn from(value: NbtError) -> Self {
        Self::Nbt(value)
    }
}

/// Require the official 26.2 save-root `Data.DataVersion == 4903`.
///
/// Parses one borrowed NBT payload with the same depth/length limits as the
/// existing importer; unrelated fields are skipped, not materialized. The
/// whole root must be well formed, with exactly one Data compound and one
/// DataVersion, even when a duplicate comes after the expected value.
///
/// This is a *necessary* COLD save-identity check, not a source certificate
/// for the world profile, packs, client biome IDs or packet publication.
///
/// # Errors
/// Rejects malformed NBT, noncanonical fields, duplicates, wrong version,
/// resource-limit failures and trailing bytes before any world packets exist.
pub fn require_target_26_2_level_metadata(
    source: &[u8],
    limits: NbtLimits,
) -> Result<(), LevelMetadataError> {
    let mut nbt = NbtReader::new(source, limits);
    if !nbt.begin_root_compound()?.is_empty() {
        return Err(LevelMetadataError::NamedRoot);
    }
    let mut saw_data = false;
    while let Some(field) = nbt.next_compound_field()? {
        if field.name != "Data" {
            nbt.skip_payload(field.tag_type)?;
            continue;
        }
        if saw_data {
            return Err(LevelMetadataError::DuplicateData);
        }
        if field.tag_type != TagType::Compound {
            return Err(LevelMetadataError::WrongDataTag {
                actual: field.tag_type,
            });
        }
        saw_data = true;
        let mut version = None;
        while let Some(entry) = nbt.next_compound_field()? {
            if entry.name == "DataVersion" {
                if version.is_some() {
                    return Err(LevelMetadataError::DuplicateDataVersion);
                }
                if entry.tag_type != TagType::Int {
                    return Err(LevelMetadataError::WrongDataVersionTag {
                        actual: entry.tag_type,
                    });
                }
                version = Some(nbt.read_i32()?);
            } else {
                nbt.skip_payload(entry.tag_type)?;
            }
        }
        let observed = version.ok_or(LevelMetadataError::MissingDataVersion)?;
        if observed != TARGET_DATA_VERSION_26_2 {
            return Err(LevelMetadataError::WrongDataVersion { observed });
        }
    }
    if !saw_data {
        return Err(LevelMetadataError::MissingData);
    }
    nbt.finish_root()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{LevelMetadataError, require_target_26_2_level_metadata};
    use crate::nbt::{NbtError, NbtLimits, TagType};

    fn limits() -> NbtLimits {
        NbtLimits::new(4096, 32768, 32768, 64).unwrap()
    }

    fn target_nbt(version: i32) -> Vec<u8> {
        let mut nbt = vec![10, 0, 0, 10, 0, 4];
        nbt.extend_from_slice(b"Data");
        nbt.extend_from_slice(&[3, 0, 11]);
        nbt.extend_from_slice(b"DataVersion");
        nbt.extend_from_slice(&version.to_be_bytes());
        nbt.extend_from_slice(&[0, 0]);
        nbt
    }

    #[test]
    fn exact_save_version_requires_complete_bounded_root() {
        let good = target_nbt(4903);
        require_target_26_2_level_metadata(&good, limits()).unwrap();
        let mut trailing = good.clone();
        trailing.push(0xff);
        assert_eq!(
            require_target_26_2_level_metadata(&trailing, limits()),
            Err(LevelMetadataError::Nbt(NbtError::TrailingBytes {
                remaining: 1
            }))
        );
        assert!(matches!(
            require_target_26_2_level_metadata(&good[..good.len() - 2], limits()),
            Err(LevelMetadataError::Nbt(NbtError::UnexpectedEof { .. }))
        ));
        assert_eq!(
            require_target_26_2_level_metadata(&target_nbt(4902), limits()),
            Err(LevelMetadataError::WrongDataVersion { observed: 4902 })
        );
    }

    #[test]
    fn malformed_missing_and_duplicated_schema_fields_fail_closed() {
        let mut wrong_data_tag = target_nbt(4903);
        wrong_data_tag[3] = 3;
        assert_eq!(
            require_target_26_2_level_metadata(&wrong_data_tag, limits()),
            Err(LevelMetadataError::WrongDataTag {
                actual: TagType::Int
            })
        );
        let mut wrong_version_tag = target_nbt(4903);
        wrong_version_tag[10] = 4;
        assert_eq!(
            require_target_26_2_level_metadata(&wrong_version_tag, limits()),
            Err(LevelMetadataError::WrongDataVersionTag {
                actual: TagType::Long
            })
        );
        assert_eq!(
            require_target_26_2_level_metadata(&[10, 0, 0, 0], limits()),
            Err(LevelMetadataError::MissingData)
        );
        let mut without_version = vec![10, 0, 0, 10, 0, 4];
        without_version.extend_from_slice(b"Data");
        without_version.extend_from_slice(&[0, 0]);
        assert_eq!(
            require_target_26_2_level_metadata(&without_version, limits()),
            Err(LevelMetadataError::MissingDataVersion)
        );
        // Second DataVersion is rejected even if the first matches 4903.
        let mut duplicate_version = target_nbt(4903);
        let insert = duplicate_version.len() - 2;
        let mut copy = vec![3, 0, 11];
        copy.extend_from_slice(b"DataVersion");
        copy.extend_from_slice(&4903_i32.to_be_bytes());
        duplicate_version.splice(insert..insert, copy);
        assert_eq!(
            require_target_26_2_level_metadata(&duplicate_version, limits()),
            Err(LevelMetadataError::DuplicateDataVersion)
        );
        // A second Data compound after one valid payload is not ignored.
        let mut duplicate_data = target_nbt(4903);
        duplicate_data.pop();
        duplicate_data.extend_from_slice(&[10, 0, 4]);
        duplicate_data.extend_from_slice(b"Data");
        duplicate_data.extend_from_slice(&[0, 0]);
        assert_eq!(
            require_target_26_2_level_metadata(&duplicate_data, limits()),
            Err(LevelMetadataError::DuplicateData)
        );
    }
}
