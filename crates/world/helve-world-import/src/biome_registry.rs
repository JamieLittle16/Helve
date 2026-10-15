//! Bounded COLD biome identity binding for an **externally qualified** 26.2 registry order.
//!
//! The source of truth for numeric biome IDs is the *exact registry order* supplied at world
//! configuration/target qualification, not sorted resource names or an alphabetical enum.
//! This mechanism does not assert that any particular list is official. Publication callers
//! must separately qualify the list against the pinned Java 26.2 biome registry.
//!
//! The sorted ordinal index is constructed once per loading session. Its binary search resolves
//! each persisted palette entry in O(log N), with no allocations, key copies or HOT cell lookups.

use crate::{stored_biomes::BiomeStateResolver, TARGET_DATA_VERSION_26_2};

/// Maximum supported registry cardinality for one compact `u16` identity.
const MAX_BIOME_IDS: usize = 65_536;

/// Invalid or unsupported registry evidence. No canonical ID is guessed on failure.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BiomeRegistryError {
    /// A registry must contain at least one source-backed biome resource key.
    Empty,
    /// The caller supplied a registry belonging to an unsupported saved chunk version.
    WrongDataVersion { expected: i32, actual: i32 },
    /// The registry exceeds the compact exact-ID representation.
    TooManyKeys { actual: usize, limit: usize },
    /// A registry key is not a canonical, lower-case, namespaced Minecraft resource location.
    MalformedKey { index: usize },
    /// Two distinct numeric IDs claim exactly the same resource location.
    DuplicateKey { first_id: u16, second_id: u16 },
}

/// One immutable, borrowed registry-order to compact-biome-ID binding.
///
/// Numeric IDs are *exactly* the ordinals of `source_order`, not the sort order. One small
/// sorted index is the only allocation and is created once at the COLD registry boundary.
/// The object never owns duplicate key strings or extends semantic chunk memory.
#[derive(Debug)]
pub struct OrderedBiomeRegistry<'a> {
    source_order: &'a [&'a str],
    lexicographic_ids: Box<[u16]>,
}

impl<'a> OrderedBiomeRegistry<'a> {
    /// Builds a fail-closed numeric resolver from independently supplied biome registry order.
    ///
    /// The caller remains responsible for proving that `source_order` is the *complete and exact*
    /// Java 26.2 runtime biome ID-map order. Syntactic and uniqueness checks **cannot** by
    /// themselves certify a source/runtime-generated registry snapshot.
    ///
    /// # Errors
    ///
    /// Rejects mismatched data version, empty/oversized registries, malformed namespaced
    /// resource locations, and duplicate names. Nothing is installed into resident world state.
    pub fn new(
        data_version: i32,
        source_order: &'a [&'a str],
    ) -> Result<Self, BiomeRegistryError> {
        if data_version != TARGET_DATA_VERSION_26_2 {
            return Err(BiomeRegistryError::WrongDataVersion {
                expected: TARGET_DATA_VERSION_26_2,
                actual: data_version,
            });
        }
        if source_order.is_empty() {
            return Err(BiomeRegistryError::Empty);
        }
        if source_order.len() > MAX_BIOME_IDS {
            return Err(BiomeRegistryError::TooManyKeys {
                actual: source_order.len(),
                limit: MAX_BIOME_IDS,
            });
        }
        let mut sorted = Vec::with_capacity(source_order.len());
        for (index, &name) in source_order.iter().enumerate() {
            if !valid_resource_location(name) {
                return Err(BiomeRegistryError::MalformedKey { index });
            }
            // The count has already been bounded above by the compact ID universe.
            let id = u16::try_from(index).map_err(|_| BiomeRegistryError::TooManyKeys {
                actual: source_order.len(),
                limit: MAX_BIOME_IDS,
            })?;
            sorted.push(id);
        }
        sorted.sort_unstable_by(|&left, &right| {
            source_order[usize::from(left)].cmp(source_order[usize::from(right)])
        });
        for adjacent in sorted.windows(2) {
            let left = adjacent[0];
            let right = adjacent[1];
            if source_order[usize::from(left)] == source_order[usize::from(right)] {
                return Err(BiomeRegistryError::DuplicateKey {
                    first_id: left,
                    second_id: right,
                });
            }
        }
        Ok(Self {
            source_order,
            lexicographic_ids: sorted.into_boxed_slice(),
        })
    }

    /// Number of exact source-ordered ID slots, useful for qualification evidence.
    #[must_use]
    pub fn len(&self) -> usize {
        self.source_order.len()
    }

    /// Returns true only when the source-ordered registry has no biome entries.
    ///
    /// A successfully built registry is always nonempty; this method also satisfies
    /// the standard `len`/`is_empty` API pairing.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.source_order.is_empty()
    }

    /// Returns the exact source-ordered resource key for an already-bound numeric ID.
    #[must_use]
    pub fn key(&self, id: u16) -> Option<&'a str> {
        self.source_order.get(usize::from(id)).copied()
    }

    /// Obtains the *source ordinal* from one persisted namespaced palette key.
    #[must_use]
    pub fn id_of(&self, key: &str) -> Option<u16> {
        self.lexicographic_ids
            .binary_search_by(|&id| self.source_order[usize::from(id)].cmp(key))
            .ok()
            .map(|index| self.lexicographic_ids[index])
    }
}

impl BiomeStateResolver for OrderedBiomeRegistry<'_> {
    type Biome = u16;

    #[inline]
    fn resolve(&self, resource_name: &str) -> Option<Self::Biome> {
        self.id_of(resource_name)
    }
}

fn valid_resource_location(name: &str) -> bool {
    let Some((namespace, path)) = name.split_once(':') else {
        return false;
    };
    !namespace.is_empty()
        && !path.is_empty()
        && namespace.bytes().all(|byte| {
            byte.is_ascii_lowercase()
                || byte.is_ascii_digit()
                || matches!(byte, b'_' | b'.' | b'-')
        })
        && path.bytes().all(|byte| {
            byte.is_ascii_lowercase()
                || byte.is_ascii_digit()
                || matches!(byte, b'_' | b'.' | b'-' | b'/')
        })
}

#[cfg(test)]
mod tests {
    use super::{BiomeRegistryError, OrderedBiomeRegistry};
    use crate::{
        TARGET_DATA_VERSION_26_2,
        nbt::{NbtLimits, NbtReader, TagType},
        stored_biomes::{
            BiomeDecodeScratch, BiomeImportError, BiomeStateResolver, ExactBiomeDecoder,
            ImportedBiomeSectionBuilder, SectionBiomeDecoder,
        },
    };

    const SOURCE_ORDER: &[&str] = &[
        "minecraft:forest",
        "minecraft:plains",
        "minecraft:desert",
        "test:custom/biome",
    ];

    #[test]
    fn preserves_registry_ordinals_instead_of_alphabetical_rank() {
        let registry = OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, SOURCE_ORDER)
            .expect("exact synthetic registry");
        assert_eq!(registry.len(), 4);
        assert!(!registry.is_empty());
        assert_eq!(registry.id_of("minecraft:forest"), Some(0));
        assert_eq!(registry.id_of("minecraft:plains"), Some(1));
        assert_eq!(registry.id_of("minecraft:desert"), Some(2));
        assert_eq!(registry.id_of("test:custom/biome"), Some(3));
        assert_eq!(registry.key(0), Some("minecraft:forest"));
        assert_eq!(registry.key(3), Some("test:custom/biome"));
        assert_eq!(registry.key(4), None);
        assert_eq!(registry.id_of("minecraft:snowy_plains"), None);
        assert_eq!(registry.id_of("minecraft:Forest"), None);
        for _ in 0..1_000 {
            assert_eq!(registry.resolve("minecraft:desert"), Some(2));
        }
    }

    #[test]
    fn rejects_wrong_target_version_duplicate_and_malformed_source_keys() {
        assert_eq!(
            OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2 - 1, SOURCE_ORDER).unwrap_err(),
            BiomeRegistryError::WrongDataVersion {
                expected: TARGET_DATA_VERSION_26_2,
                actual: TARGET_DATA_VERSION_26_2 - 1,
            },
        );
        assert_eq!(
            OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, &[]).unwrap_err(),
            BiomeRegistryError::Empty,
        );
        let repeated = ["minecraft:plains", "minecraft:forest", "minecraft:plains"];
        assert_eq!(
            OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, &repeated).unwrap_err(),
            BiomeRegistryError::DuplicateKey {
                first_id: 0,
                second_id: 2,
            },
        );
        for bad in [
            "", "plains", ":plains", "minecraft:", "minecraft:bad:biome",
            "Minecraft:forest", "minecraft:Snow", "minecraft:with space",
            "minecraft:é", "minecraft:./?bad",
        ] {
            assert_eq!(
                OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, &[bad]).unwrap_err(),
                BiomeRegistryError::MalformedKey { index: 0 },
                "bad key: {bad}",
            );
        }
    }

    #[test]
    fn compact_max_id_bound_and_sorted_binary_search_are_exact() {
        let names: Vec<String> = (0..256)
            .map(|i| format!("test:biome/{:04}", 255 - i))
            .collect();
        let borrowed: Vec<&str> = names.iter().map(String::as_str).collect();
        let registry = OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, &borrowed)
            .expect("all 256 compact IDs");
        for (id, &name) in borrowed.iter().enumerate() {
            assert_eq!(registry.id_of(name), u16::try_from(id).ok());
            assert_eq!(registry.key(u16::try_from(id).expect("test bound")), Some(name));
        }
    }

    #[derive(Default)]
    struct VecBuilder;

    impl ImportedBiomeSectionBuilder<u16> for VecBuilder {
        type Section = Vec<u16>;

        fn build_uniform(&mut self, biome: u16) -> Self::Section {
            vec![biome; 64]
        }

        fn build_biomes(&mut self, cells: &[u16]) -> Self::Section {
            cells.to_vec()
        }
    }

    #[test]
    fn resolves_saved_quart_palette_into_actual_registry_ordinals() {
        let registry = OrderedBiomeRegistry::new(TARGET_DATA_VERSION_26_2, SOURCE_ORDER)
            .expect("registry order input");
        let mut section = Vec::new();
        section.push(TagType::List as u8);
        section.extend_from_slice(&(7_u16.to_be_bytes()));
        section.extend_from_slice(b"palette");
        section.push(TagType::String as u8);
        section.extend_from_slice(&(1_i32.to_be_bytes()));
        let name = "minecraft:desert";
        section.extend_from_slice(
            &u16::try_from(name.len()).expect("short name").to_be_bytes(),
        );
        section.extend_from_slice(name.as_bytes());
        section.push(TagType::End as u8);

        let mut builder = VecBuilder;
        let mut scratch = BiomeDecodeScratch::new();
        let mut decoder = ExactBiomeDecoder::new(&registry, &mut builder, &mut scratch);
        let mut reader = NbtReader::new(
            &section,
            NbtLimits::new(128, 64, 64, 8).expect("bounded"),
        );
        assert_eq!(
            decoder.decode_section(&mut reader, 0),
            Ok(vec![2_u16; 64]),
        );
        assert_eq!(reader.offset(), section.len());

        let mut unknown = section.clone();
        let start = unknown.len() - (name.len() + 1);
        // The source name is not substituted; corruption fails rather than defaulting Plains.
        unknown[start] = b'!';
        let mut reader = NbtReader::new(
            &unknown,
            NbtLimits::new(128, 64, 64, 8).expect("bounded"),
        );
        assert!(matches!(
            decoder.decode_section(&mut reader, 0),
            Err(BiomeImportError::UnknownBiome {
                section_index: 0,
                palette_index: 0,
            }),
        ));
    }
}
