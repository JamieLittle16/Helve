//! Source provenance for a COLD imported chunk, minted only after resident admission.
//!
//! This is an ephemeral caller-owned receipt, not a resident field, persistent
//! block-entity cache, second revision clock, network packet, or HOT-path tax.
//! Every use resolves the authoritative directory handle, rejecting unload,
//! replacement, and mutation before source evidence can authorize publication.

use helve_types::ChunkRevision;
use helve_world_chunk::LiveChunkSemanticState;
use helve_world_contract::{BiomeSection, BlockSection};
use helve_world_import::{
    EmptyBlockEntityEvidenceError, StoredBlockEntityEvidence, StoredChunkHeader,
};
use helve_world_runtime::{
    ResidentChunkAccessError, SemanticDimensionInstance,
};

use crate::InstalledStoredChunk;

/// Only the successful source-biome import transaction can mint this receipt.
///
/// The source header and saved block-entity evidence are bound to the returned
/// authoritative dimension/position/generation handle at admission time.
/// Copying a receipt does not prolong its validity across mutation or unload.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SourceChunkPublicationReceipt {
    installed: InstalledStoredChunk,
    stored: StoredChunkHeader,
    block_entities: StoredBlockEntityEvidence,
}

/// A source receipt cannot establish current initial publication authority.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SourceChunkReceiptError {
    /// The original authoritative directory handle no longer resolves.
    Resident(ResidentChunkAccessError),
    /// The chunk is from the right incarnation but its source snapshot changed.
    Revised { actual: ChunkRevision },
    /// An absent or nonempty list cannot authorize the empty-entity profile.
    BlockEntities(EmptyBlockEntityEvidenceError),
}

/// Borrow of the verified current resident and its bound original source header.
///
/// A type alias keeps the COLD method signature straightforward without
/// allocating or manufacturing an independent semantic world representation.
pub type ExplicitlyEmptyImportedSource<'a, S, BlockStorage, B, BiomeStorage> = (
    &'a LiveChunkSemanticState<S, BlockStorage, B, BiomeStorage>,
    StoredChunkHeader,
);

impl SourceChunkPublicationReceipt {
    /// Constructible only by a successful source-biome resident installation.
    pub(crate) const fn from_admission(
        installed: InstalledStoredChunk,
        stored: StoredChunkHeader,
        block_entities: StoredBlockEntityEvidence,
    ) -> Self {
        Self {
            installed,
            stored,
            block_entities,
        }
    }

    /// The exact admitted handle; caller may retain it for normal COLD discovery.
    #[must_use]
    pub const fn installed(self) -> InstalledStoredChunk {
        self.installed
    }

    /// Resolve an explicitly empty block-entity source on its *original* pristine resident.
    ///
    /// This performs exactly one COLD resident-directory handle resolution. The
    /// underlying dimension checks dimension ID, position and generation; then
    /// the receipt refuses any nonzero semantic revision. Only an explicitly
    /// empty saved list is allowed. The returned borrow prevents mutation or
    /// unload during synchronous COLD packet-candidate projection.
    ///
    /// This remains **source-evidence identity** only: it does not admit the
    /// target biome numeric IDs, outer packet law, or actual client publication.
    ///
    /// # Errors
    ///
    /// Rejects stale/foreign/unloaded handles, mutated chunks, or source
    /// evidence other than a uniquely present empty block-entity list.
    pub fn resolve_explicitly_empty<'a, S, BlockStorage, B, BiomeStorage>(
        &self,
        dimension: &'a SemanticDimensionInstance<S, BlockStorage, B, BiomeStorage>,
    ) -> Result<
        ExplicitlyEmptyImportedSource<'a, S, BlockStorage, B, BiomeStorage>,
        SourceChunkReceiptError,
    >
    where
        S: Copy + Eq,
        BlockStorage: BlockSection<S>,
        B: Copy + Eq,
        BiomeStorage: BiomeSection<B>,
    {
        let chunk = dimension
            .resolve_chunk(self.installed.handle)
            .map_err(SourceChunkReceiptError::Resident)?;
        if chunk.revision() != ChunkRevision(0) {
            return Err(SourceChunkReceiptError::Revised {
                actual: chunk.revision(),
            });
        }
        self.block_entities
            .require_explicitly_empty()
            .map_err(SourceChunkReceiptError::BlockEntities)?;
        Ok((chunk, self.stored))
    }
}
