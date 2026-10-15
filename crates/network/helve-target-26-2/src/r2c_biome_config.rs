//! COLD, source-shaped extraction of ordered biome keys from the exact
//! Configuration registry-data bodies that the selected R1X/R2B profile sends.
//!
//! Minecraft 26.2 `ConfigurationProtocols` assigns clientbound registry-data
//! packet ID 7; `ClientboundRegistryDataPacket` serializes registry key
//! followed by a VarInt-sized list of `PackedRegistryEntry` values (key,
//! optional NBT contents). Under the selected core@26.2 known-pack branch,
//! the 66 biome entries omit their NBT contents. This parser intentionally
//! supports **only** that finite source-observed representation.
//!
//! This is a non-authoritative COLD cross-check. The receiving client's
//! numeric assignment and future arbitrary pack profiles are not certified;
//! it must not enable world packets before independent R2C-BIOMES admission.

use helve_packet_core::{PacketCodecError, PacketReader};

/// Exact selected 26.2 clientbound Configuration registry-data identity.
const REGISTRY_DATA_PACKET_ID: i32 = 7;
const BIOME_REGISTRY_KEY: &str = "minecraft:worldgen/biome";
const CORE_BIOME_COUNT: usize = 66;
const CORE_BIOME_COUNT_WIRE: i32 = 66;
const MAX_IDENTIFIER_UTF16_UNITS: usize = 32_767;

/// A different Configuration image or pack profile cannot claim this order.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BiomeConfigOrderError {
    /// A registry-data header/list/entry violated the target packet codec.
    Codec(PacketCodecError),
    /// No registry-data body named the biome registry.
    MissingBiomeRegistry,
    /// Two registry packets claimed to describe the same biome registry.
    DuplicateBiomeRegistry,
    /// The selected core known-pack profile must publish 66 entries.
    WrongBiomeCount { actual: i32 },
    /// An entry's identifier was empty (full syntax validation occurs in
    /// the target-neutral `OrderedBiomeRegistry` consumer).
    EmptyEntryKey { index: usize },
    /// The selected known-pack path sends only keys, never NBT payloads.
    DataBearingBiome { index: usize },
}

impl From<PacketCodecError> for BiomeConfigOrderError {
    fn from(error: PacketCodecError) -> Self {
        Self::Codec(error)
    }
}

/// Borrow exactly the 66 biome keys in the order emitted by a validated
/// Configuration image. No key strings are copied and no numeric ID is
/// manufactured from an alphabetical sort.
///
/// The caller owns the byte image and must retain it for the returned
/// `&str` lifetimes. The only allocation is a 66-element pointer vector.
/// The source/runtime image commitment and known-pack handshake remain
/// independent prerequisites to selecting this narrow profile.
///
/// # Errors
///
/// Rejects absent/duplicate biome registries, malformed byte fields,
/// a different biome cardinality or any entry carrying inline NBT.
pub fn borrow_core_biome_order<B>(
    configuration_bodies: &[B],
) -> Result<Vec<&str>, BiomeConfigOrderError>
where
    B: AsRef<[u8]>,
{
    let mut found = None;
    for body in configuration_bodies {
        let mut reader = PacketReader::new(body.as_ref());
        if reader.read_var_int()? != REGISTRY_DATA_PACKET_ID {
            continue;
        }
        let registry = reader.read_string(MAX_IDENTIFIER_UTF16_UNITS)?;
        if registry != BIOME_REGISTRY_KEY {
            continue;
        }
        if found.is_some() {
            return Err(BiomeConfigOrderError::DuplicateBiomeRegistry);
        }

        let count = reader.read_var_int()?;
        if count != CORE_BIOME_COUNT_WIRE {
            return Err(BiomeConfigOrderError::WrongBiomeCount { actual: count });
        }
        let mut keys = Vec::with_capacity(CORE_BIOME_COUNT);
        for index in 0..CORE_BIOME_COUNT {
            let key = reader.read_string(MAX_IDENTIFIER_UTF16_UNITS)?;
            if key.is_empty() {
                return Err(BiomeConfigOrderError::EmptyEntryKey { index });
            }
            if reader.read_bool()? {
                return Err(BiomeConfigOrderError::DataBearingBiome { index });
            }
            keys.push(key);
        }
        reader.finish()?;
        found = Some(keys);
    }
    found.ok_or(BiomeConfigOrderError::MissingBiomeRegistry)
}

#[cfg(test)]
mod tests {
    use helve_packet_core::PacketWriter;

    use super::{BiomeConfigOrderError, borrow_core_biome_order};

    fn build_selected_biome_body() -> Vec<u8> {
        let mut writer = PacketWriter::new(6_000).unwrap();
        writer.write_var_int(7).unwrap();
        writer
            .write_string("minecraft:worldgen/biome", 32_767)
            .unwrap();
        writer.write_var_int(66).unwrap();
        // Deliberately reversed: numeric IDs are sent-order, never sorted.
        for index in (0..66).rev() {
            writer
                .write_string(&format!("minecraft:test_{index}"), 32_767)
                .unwrap();
            writer.write_bool(false).unwrap();
        }
        writer.into_bytes()
    }

    #[test]
    fn borrowed_ordinals_follow_exact_configuration_order_not_key_sorting() {
        let bodies = [vec![0x01, 0x00], build_selected_biome_body(), vec![0x03]];
        let ordered = borrow_core_biome_order(&bodies).unwrap();
        assert_eq!(ordered.len(), 66);
        assert_eq!(ordered[0], "minecraft:test_65");
        assert_eq!(ordered[65], "minecraft:test_0");
        assert_eq!(ordered[7], "minecraft:test_58");
        assert_eq!(ordered[0].as_ptr(), {
            let source = &bodies[1];
            let needle = b"minecraft:test_65";
            let offset = source
                .windows(needle.len())
                .position(|w| w == needle)
                .unwrap();
            source[offset..].as_ptr()
        });
    }

    #[test]
    fn duplicate_missing_and_wrong_cardinality_fail_closed() {
        let correct = build_selected_biome_body();
        assert_eq!(
            borrow_core_biome_order(&[vec![3]]),
            Err(BiomeConfigOrderError::MissingBiomeRegistry)
        );
        assert_eq!(
            borrow_core_biome_order(&[correct.clone(), correct.clone()]),
            Err(BiomeConfigOrderError::DuplicateBiomeRegistry)
        );
        // Find the VarInt(66) directly after the registry key.
        let mut wrong = correct;
        let index = wrong
            .windows(b"minecraft:worldgen/biome".len())
            .position(|w| w == b"minecraft:worldgen/biome")
            .unwrap()
            + b"minecraft:worldgen/biome".len();
        assert_eq!(wrong[index], 66);
        wrong[index] = 65;
        assert_eq!(
            borrow_core_biome_order(&[wrong]),
            Err(BiomeConfigOrderError::WrongBiomeCount { actual: 65 })
        );
    }

    #[test]
    fn known_pack_inline_payload_and_extra_bytes_are_rejected() {
        let mut body = build_selected_biome_body();
        // The first entry's boolean immediately follows its key.
        let needle = b"minecraft:test_65";
        let index = body
            .windows(needle.len())
            .position(|w| w == needle)
            .unwrap()
            + needle.len();
        assert_eq!(body[index], 0);
        body[index] = 1;
        assert_eq!(
            borrow_core_biome_order(&[body]),
            Err(BiomeConfigOrderError::DataBearingBiome { index: 0 })
        );

        let mut extra = build_selected_biome_body();
        extra.push(0xaa);
        assert!(matches!(
            borrow_core_biome_order(&[extra]),
            Err(BiomeConfigOrderError::Codec(
                PacketCodecError::TrailingBytes { remaining: 1 }
            ))
        ));
    }
}
