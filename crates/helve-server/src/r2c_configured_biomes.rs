//! COLD bridge from the Configuration bytes actually sent by R2B into
//! the existing sparse-world importer's exact compact biome ID resolver.
//!
//! This is a *candidate* consistency boundary, NOT a numeric-ID authority.
//! A validated 26.2 selected Configuration image must remain alive while
//! its borrowed biome names are in use. A future live publisher must
//! additionally pass the independent R2C-BIOMES client-assignment VAR/SEM
//! gate and matching pack-profile qualification before sending chunks.
//!
//! No registry names are copied, no registry is stored inside itself, and
//! no lookup/dispatch cost is added to HOT resident block/biome access.

use helve_target_26_2::{
    Target26_2R1xContext,
    r2c_biome_config::{BiomeConfigOrderError, borrow_core_biome_order},
};
use helve_world_import::{
    OrderedBiomeRegistry, TARGET_DATA_VERSION_26_2, biome_registry::BiomeRegistryError,
};

/// A selected Config image cannot yield a valid imported biome ID map.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ConfiguredBiomeCandidateError {
    /// Selected sent Configuration bytes were not the admitted shape.
    Configuration(BiomeConfigOrderError),
    /// Source order had invalid or duplicated keys.
    Registry(BiomeRegistryError),
}

impl From<BiomeConfigOrderError> for ConfiguredBiomeCandidateError {
    fn from(error: BiomeConfigOrderError) -> Self {
        Self::Configuration(error)
    }
}

impl From<BiomeRegistryError> for ConfiguredBiomeCandidateError {
    fn from(error: BiomeRegistryError) -> Self {
        Self::Registry(error)
    }
}

/// Borrow one compact lookup from the *exact* Configuration image associated
/// with a prospective R2B/R2C connection. The scratch key pointer vector
/// exists only inside this call; a closure cannot retain the borrowed
/// self-referential lookup accidentally.
///
/// No numeric ID is inferred by sorting: the lookup's IDs are exactly
/// the transmitted 66-element list indices. This narrow candidate carries
/// no production admission flag.
///
/// # Errors
///
/// Rejects unsupported registry shapes, malformed names, duplicate keys,
/// or any other previously unqualified Configuration representation.
#[cfg_attr(
    not(test),
    expect(
        dead_code,
        reason = "full client numeric registry assignment is still independently source-gated"
    )
)]
pub(crate) fn with_candidate_biomes_from_context<T>(
    context: &Target26_2R1xContext,
    use_registry: impl FnOnce(&OrderedBiomeRegistry<'_>) -> T,
) -> Result<T, ConfiguredBiomeCandidateError> {
    let names = context.candidate_sent_biome_order()?;
    bind_borrowed_order(&names, use_registry)
}

/// Development-only composition of exactly the same two stages, for
/// independent tests that supply synthetic Configuration body bytes.
#[cfg(test)]
fn with_candidate_biomes_from_wire<T>(
    bodies: &[Vec<u8>],
    use_registry: impl FnOnce(&OrderedBiomeRegistry<'_>) -> T,
) -> Result<T, ConfiguredBiomeCandidateError> {
    let names = borrow_core_biome_order(bodies)?;
    bind_borrowed_order(&names, use_registry)
}

fn bind_borrowed_order<T>(
    names: &[&str],
    use_registry: impl FnOnce(&OrderedBiomeRegistry<'_>) -> T,
) -> Result<T, ConfiguredBiomeCandidateError> {
    let registry = OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, names)?;
    Ok(use_registry(&registry))
}

#[cfg(test)]
mod tests {
    use helve_packet_core::PacketWriter;
    use helve_world_import::{
        nbt::{NbtLimits, NbtReader, TagType},
        stored_biomes::{
            BiomeDecodeScratch, BiomeImportError, ExactBiomeDecoder, ImportedBiomeSectionBuilder,
            SectionBiomeDecoder,
        },
    };

    use super::{
        ConfiguredBiomeCandidateError, with_candidate_biomes_from_wire,
    };

    #[derive(Default)]
    struct IntoCells;

    impl ImportedBiomeSectionBuilder<u16> for IntoCells {
        type Section = Vec<u16>;

        fn build_uniform(&mut self, id: u16) -> Self::Section {
            vec![id; 64]
        }

        fn build_biomes(&mut self, ids: &[u16]) -> Self::Section {
            ids.to_vec()
        }
    }

    fn configuration_with_names(names: &[String]) -> Vec<u8> {
        let mut writer = PacketWriter::new(16_384).unwrap();
        writer.write_var_int(7).unwrap();
        writer
            .write_string("minecraft:worldgen/biome", 32_767)
            .unwrap();
        writer.write_var_int(66).unwrap();
        for name in names {
            writer.write_string(name, 32_767).unwrap();
            writer.write_bool(false).unwrap();
        }
        writer.into_bytes()
    }

    fn saved_uniform_biome(name: &str) -> Vec<u8> {
        let mut section = Vec::new();
        section.push(TagType::List as u8);
        section.extend_from_slice(&(7_u16.to_be_bytes()));
        section.extend_from_slice(b"palette");
        section.push(TagType::String as u8);
        section.extend_from_slice(&(1_i32.to_be_bytes()));
        section.extend_from_slice(&u16::try_from(name.len()).unwrap().to_be_bytes());
        section.extend_from_slice(name.as_bytes());
        section.push(TagType::End as u8);
        section
    }

    #[test]
    fn exact_sent_configuration_order_drives_saved_biome_import_without_sorting() {
        let names: Vec<String> = (0..66).rev().map(|i| format!("minecraft:biome_{i}")).collect();
        let config = [vec![3], configuration_with_names(&names)];
        let section = saved_uniform_biome("minecraft:biome_57");

        let answer = with_candidate_biomes_from_wire(&config, |registry| {
            assert_eq!(registry.len(), 66);
            assert_eq!(registry.key(0), Some("minecraft:biome_65"));
            assert_eq!(registry.id_of("minecraft:biome_57"), Some(8));
            assert_eq!(registry.id_of("minecraft:not_in_configuration"), None);

            let mut builder = IntoCells;
            let mut scratch = BiomeDecodeScratch::new();
            let mut decoder = ExactBiomeDecoder::new(registry, &mut builder, &mut scratch);
            let mut reader =
                NbtReader::new(&section, NbtLimits::new(128, 64, 64, 8).unwrap());
            let cells = decoder.decode_section(&mut reader, 0).unwrap();
            assert_eq!(reader.offset(), section.len());
            assert_eq!(cells.len(), 64);
            assert!(cells.iter().all(|&id| id == 8));
            cells[0]
        });
        assert_eq!(answer, Ok(8));
    }

    #[test]
    fn absent_palette_entry_fails_closed_without_plains_fallback() {
        let names: Vec<String> = (0..66).map(|i| format!("minecraft:biome_{i}")).collect();
        let config = [configuration_with_names(&names)];
        let unknown = saved_uniform_biome("minecraft:unknown_biome");
        let outcome = with_candidate_biomes_from_wire(&config, |registry| {
            let mut builder = IntoCells;
            let mut scratch = BiomeDecodeScratch::new();
            let mut decoder = ExactBiomeDecoder::new(registry, &mut builder, &mut scratch);
            let mut reader =
                NbtReader::new(&unknown, NbtLimits::new(128, 64, 64, 8).unwrap());
            decoder.decode_section(&mut reader, 0)
        });
        assert_eq!(
            outcome,
            Ok(Err(BiomeImportError::UnknownBiome {
                section_index: 0,
                palette_index: 0,
            }))
        );
    }

    #[test]
    fn invalid_duplicate_sent_names_never_reach_importer() {
        let mut names: Vec<String> = (0..66).map(|i| format!("minecraft:biome_{i}")).collect();
        names[65] = names[0].clone();
        let config = [configuration_with_names(&names)];
        let outcome = with_candidate_biomes_from_wire(&config, |_| "not called");
        assert!(matches!(
            outcome,
            Err(ConfiguredBiomeCandidateError::Registry(
                helve_world_import::biome_registry::BiomeRegistryError::DuplicateKey {
                    first_id: 0,
                    second_id: 65
                }
            ))
        ));
    }
}
