//! Cold pregenerated-world import boundaries for Helve.
//!
//! This crate owns bounded parsing of persisted Minecraft world bytes. It deliberately does not own
//! live chunk residency, network projection, scheduling, persistence policy, or a generic NBT object
//! model. The import path should decode directly toward admitted semantic state.

#![forbid(unsafe_code)]

pub mod anvil;
pub mod biome_registry;
pub mod chunk;
pub mod compression;
pub mod level_metadata;
mod generated_state_lookup;
pub mod nbt;
pub mod state_lookup;
pub mod stored_biomes;
pub mod stored_blocks;
pub mod transaction;

pub use anvil::{ChunkCompression, RegionChunk, RegionError, RegionLimits, RegionView};
pub use biome_registry::{BiomeRegistryError, OrderedBiomeRegistry};
pub use chunk::{
    ChunkImportError, StoredChunkHeader, TARGET_DATA_VERSION_26_2, inspect_chunk_header,
};
pub use compression::{CompressedPayloadError, DeflateChunkPayloadDecoder, WrapperKind};
pub use level_metadata::{LevelMetadataError, require_target_26_2_level_metadata};
pub use nbt::{ListHeader, NamedTag, NbtError, NbtLimits, NbtReader, TagType};
pub use state_lookup::{
    Target262BlockStateResolver, canonical_state_fingerprint, resolve_target_26_2_block_state,
};
pub use stored_biomes::{
    BiomeDecodeScratch, BiomeImportError, BiomeStateResolver, ExactBiomeDecoder,
    ImportedBiomeSection, ImportedBiomeSectionBuilder, ImportedStoredBiomes,
};
pub use stored_blocks::{
    BlockProperty, BlockSectionDecodeScratch, BlockSectionImportError,
    BlockSectionScratchCapacities, BlockStateResolver, EmptyBlockEntityEvidenceError,
    ImportedBlockSection, ImportedBlockSectionBuilder, ImportedChunkBlocks,
    ImportedChunkWithBiomeLight, ImportedChunkWithLight, ImportedStoredLight,
    ImportedStoredLightSection, StoredBlockEntityEvidence, decode_chunk_block_sections,
    decode_chunk_block_sections_with_biomes, decode_chunk_block_sections_with_light,
};
pub use transaction::{
    ChunkPayloadDecoder, ChunkPayloadLimits, ExternalChunkPayload, ImportedStoredChunk,
    ImportedStoredChunkWithBiomeLight, ImportedStoredChunkWithLight, StoredBlockImporter,
    StoredChunkImportError, StoredChunkSourceMetadata, UncompressedChunkPayloadDecoder,
    UncompressedPayloadError,
};
