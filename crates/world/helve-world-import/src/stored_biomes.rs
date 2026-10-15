//! Exact saved 26.2 quart-biome palette decoding in the existing section NBT traversal.
//!
//! Persistent biomes are semantic source data, not already-encoded network palette bytes.
//! The cold resolver fails closed on unknown identities. No NBT tree, second section scan,
//! dynamically dispatched codec or HOT registry lookup is introduced.

use crate::nbt::{NbtError, NbtReader, TagType};

const BIOME_CELLS: usize = 64;
const WORD_BITS: usize = 64;

/// Resolves a stored biome resource key to one compact semantic identity.
pub trait BiomeStateResolver {
    type Biome: Copy + Eq;

    /// Returns None for an unrecognized target 26.2 biome, never a synthetic Plains fallback.
    fn resolve(&self, resource_name: &str) -> Option<Self::Biome>;
}

/// Constructs the caller's final quart-biome section representation directly from resolved IDs.
///
/// A non-uniform slice contains exactly 64 semantic cells in x + 4*z + 16*y order.
pub trait ImportedBiomeSectionBuilder<B: Copy + Eq> {
    type Section;

    fn build_uniform(&mut self, biome: B) -> Self::Section;

    fn build_biomes(&mut self, cells: &[B]) -> Self::Section;
}

/// One actual persisted biome section with source section-Y identity.
#[derive(Debug, Eq, PartialEq)]
pub struct ImportedBiomeSection<Section> {
    pub section_y: i8,
    pub section: Section,
}

/// Sparse saved biome sections, preserving absence without manufacturing a default.
#[derive(Debug, Eq, PartialEq)]
pub struct ImportedStoredBiomes<Section> {
    pub sections: Vec<ImportedBiomeSection<Section>>,
}

/// Bounded, explicit violations of the selected 26.2 saved-biome codec.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum BiomeImportError {
    Nbt(NbtError),
    WrongType {
        section_index: usize,
        field: &'static str,
        expected: TagType,
        actual: TagType,
    },
    DuplicateField {
        section_index: usize,
        field: &'static str,
    },
    MissingPalette {
        section_index: usize,
    },
    WrongPaletteElementType {
        section_index: usize,
        actual: TagType,
    },
    PaletteCardinality {
        section_index: usize,
        actual: usize,
    },
    UnknownBiome {
        section_index: usize,
        palette_index: usize,
    },
    MissingPackedData {
        section_index: usize,
    },
    UniformHasData {
        section_index: usize,
        words: usize,
    },
    PackedWordCount {
        section_index: usize,
        expected: usize,
        actual: usize,
        bits: usize,
    },
    PaletteIndexOutOfRange {
        section_index: usize,
        cell: usize,
        palette_index: usize,
        palette_entries: usize,
    },
    /// The packed palette cell index is not representable on the current host.
    ArithmeticOverflow,
}

impl From<NbtError> for BiomeImportError {
    fn from(error: NbtError) -> Self {
        Self::Nbt(error)
    }
}

/// Internal statically selected codec for section NBT; the disabled mode never decodes biomes.
/// Compile-time-selected biome decoder for the shared bounded section traversal.
///
/// Implementations must consume exactly one biome compound payload.
pub trait SectionBiomeDecoder {
    type Section;
    const ENABLED: bool;

    /// Decodes one saved `biomes` compound payload, returning a final semantic section.
    ///
    /// # Errors
    ///
    /// Rejects malformed NBT, invalid packed palette data and unresolved biome identities.
    fn decode_section(
        &mut self,
        reader: &mut NbtReader<'_>,
        section_index: usize,
    ) -> Result<Self::Section, BiomeImportError>;
}

pub(crate) struct IgnoreBiomes;

impl SectionBiomeDecoder for IgnoreBiomes {
    type Section = ();
    const ENABLED: bool = false;

    fn decode_section(
        &mut self,
        _reader: &mut NbtReader<'_>,
        _section_index: usize,
    ) -> Result<Self::Section, BiomeImportError> {
        unreachable!("the disabled biome branch is statically removed")
    }
}

/// Reusable semantic palette and packed-word decode buffers for one imported chunk stream.
#[derive(Debug)]
pub struct BiomeDecodeScratch<B: Copy + Eq> {
    palette: Vec<B>,
    words: Vec<u64>,
    cells: Vec<B>,
}

impl<B: Copy + Eq> BiomeDecodeScratch<B> {
    #[must_use]
    pub const fn new() -> Self {
        Self {
            palette: Vec::new(),
            words: Vec::new(),
            cells: Vec::new(),
        }
    }

    fn clear(&mut self) {
        self.palette.clear();
        self.words.clear();
        self.cells.clear();
    }
}

impl<B: Copy + Eq> Default for BiomeDecodeScratch<B> {
    fn default() -> Self {
        Self::new()
    }
}

/// Statically dispatched COLD biome codec with caller-selected resolver and final storage.
#[derive(Debug)]
pub struct ExactBiomeDecoder<'a, R, B>
where
    R: BiomeStateResolver,
    B: ImportedBiomeSectionBuilder<R::Biome>,
{
    resolver: &'a R,
    builder: &'a mut B,
    scratch: &'a mut BiomeDecodeScratch<R::Biome>,
}

impl<'a, R, B> ExactBiomeDecoder<'a, R, B>
where
    R: BiomeStateResolver,
    B: ImportedBiomeSectionBuilder<R::Biome>,
{
    #[must_use]
    pub const fn new(
        resolver: &'a R,
        builder: &'a mut B,
        scratch: &'a mut BiomeDecodeScratch<R::Biome>,
    ) -> Self {
        Self {
            resolver,
            builder,
            scratch,
        }
    }
}

impl<R, B> ExactBiomeDecoder<'_, R, B>
where
    R: BiomeStateResolver,
    B: ImportedBiomeSectionBuilder<R::Biome>,
{
    fn read_palette(
        &mut self,
        reader: &mut NbtReader<'_>,
        section_index: usize,
    ) -> Result<(), BiomeImportError> {
        let header = reader.read_list_header()?;
        if header.element_type != TagType::String {
            return Err(BiomeImportError::WrongPaletteElementType {
                section_index,
                actual: header.element_type,
            });
        }
        if header.len == 0 || header.len > BIOME_CELLS {
            return Err(BiomeImportError::PaletteCardinality {
                section_index,
                actual: header.len,
            });
        }
        self.scratch.palette.reserve(header.len);
        for palette_index in 0..header.len {
            let name = reader.read_string()?;
            let biome = self
                .resolver
                .resolve(name)
                .ok_or(BiomeImportError::UnknownBiome {
                    section_index,
                    palette_index,
                })?;
            self.scratch.palette.push(biome);
        }
        Ok(())
    }

    fn read_words(
        &mut self,
        reader: &mut NbtReader<'_>,
        section_index: usize,
    ) -> Result<(), BiomeImportError> {
        let words = reader.read_long_array_len()?;
        // Hard source-section cap before reserving, independent of broader NBT limits.
        if words > BIOME_CELLS {
            return Err(BiomeImportError::PackedWordCount {
                section_index,
                expected: BIOME_CELLS,
                actual: words,
                bits: 0,
            });
        }
        self.scratch.words.reserve(words);
        for _ in 0..words {
            self.scratch
                .words
                .push(u64::from_be_bytes(reader.read_i64()?.to_be_bytes()));
        }
        Ok(())
    }
}

impl<R, B> SectionBiomeDecoder for ExactBiomeDecoder<'_, R, B>
where
    R: BiomeStateResolver,
    B: ImportedBiomeSectionBuilder<R::Biome>,
{
    type Section = B::Section;
    const ENABLED: bool = true;

    fn decode_section(
        &mut self,
        reader: &mut NbtReader<'_>,
        section_index: usize,
    ) -> Result<Self::Section, BiomeImportError> {
        self.scratch.clear();
        let mut palette_present = false;
        let mut data_present = false;
        while let Some(field) = reader.next_compound_field()? {
            match field.name {
                "palette" => {
                    require_type(
                        section_index,
                        "biomes.palette",
                        field.tag_type,
                        TagType::List,
                    )?;
                    if palette_present {
                        return Err(BiomeImportError::DuplicateField {
                            section_index,
                            field: "biomes.palette",
                        });
                    }
                    palette_present = true;
                    self.read_palette(reader, section_index)?;
                }
                "data" => {
                    require_type(
                        section_index,
                        "biomes.data",
                        field.tag_type,
                        TagType::LongArray,
                    )?;
                    if data_present {
                        return Err(BiomeImportError::DuplicateField {
                            section_index,
                            field: "biomes.data",
                        });
                    }
                    data_present = true;
                    self.read_words(reader, section_index)?;
                }
                _ => reader.skip_payload(field.tag_type)?,
            }
        }
        if !palette_present {
            return Err(BiomeImportError::MissingPalette { section_index });
        }
        let palette_entries = self.scratch.palette.len();
        if palette_entries == 1 {
            if !self.scratch.words.is_empty() {
                return Err(BiomeImportError::UniformHasData {
                    section_index,
                    words: self.scratch.words.len(),
                });
            }
            return Ok(self.builder.build_uniform(self.scratch.palette[0]));
        }
        if !data_present {
            return Err(BiomeImportError::MissingPackedData { section_index });
        }
        let bits = (usize::BITS - (palette_entries - 1).leading_zeros()) as usize;
        let cells_per_word = WORD_BITS / bits;
        let expected = BIOME_CELLS.div_ceil(cells_per_word);
        if self.scratch.words.len() != expected {
            return Err(BiomeImportError::PackedWordCount {
                section_index,
                expected,
                actual: self.scratch.words.len(),
                bits,
            });
        }
        let mask = (1_u64 << bits) - 1;
        self.scratch.cells.reserve(BIOME_CELLS);
        for cell in 0..BIOME_CELLS {
            let word = self.scratch.words[cell / cells_per_word];
            let shift = (cell % cells_per_word) * bits;
            let palette_index = usize::try_from((word >> shift) & mask)
                .map_err(|_| BiomeImportError::ArithmeticOverflow)?;
            let biome = *self.scratch.palette.get(palette_index).ok_or(
                BiomeImportError::PaletteIndexOutOfRange {
                    section_index,
                    cell,
                    palette_index,
                    palette_entries,
                },
            )?;
            self.scratch.cells.push(biome);
        }
        Ok(self.builder.build_biomes(&self.scratch.cells))
    }
}

fn require_type(
    section_index: usize,
    field: &'static str,
    actual: TagType,
    expected: TagType,
) -> Result<(), BiomeImportError> {
    if actual == expected {
        Ok(())
    } else {
        Err(BiomeImportError::WrongType {
            section_index,
            field,
            expected,
            actual,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::{
        BiomeDecodeScratch, BiomeImportError, BiomeStateResolver, ExactBiomeDecoder,
        ImportedBiomeSectionBuilder, SectionBiomeDecoder,
    };
    use crate::nbt::{NbtLimits, NbtReader, TagType};

    struct Resolver;

    impl BiomeStateResolver for Resolver {
        type Biome = u8;

        fn resolve(&self, name: &str) -> Option<Self::Biome> {
            name.strip_prefix("minecraft:biome")?
                .parse::<u8>()
                .ok()
                .filter(|&id| id < 64)
        }
    }

    struct Builder;

    impl ImportedBiomeSectionBuilder<u8> for Builder {
        type Section = Vec<u8>;

        fn build_uniform(&mut self, biome: u8) -> Self::Section {
            vec![biome; 64]
        }

        fn build_biomes(&mut self, cells: &[u8]) -> Self::Section {
            cells.to_vec()
        }
    }

    fn name(bytes: &mut Vec<u8>, value: &str) {
        let len = u16::try_from(value.len()).expect("fixture fits");
        bytes.extend_from_slice(&len.to_be_bytes());
        bytes.extend_from_slice(value.as_bytes());
    }

    fn tag(bytes: &mut Vec<u8>, ty: TagType, field: &str) {
        bytes.push(ty as u8);
        name(bytes, field);
    }

    fn palette(bytes: &mut Vec<u8>, count: usize) {
        tag(bytes, TagType::List, "palette");
        bytes.push(TagType::String as u8);
        bytes.extend_from_slice(
            &i32::try_from(count)
                .expect("fixture count fits")
                .to_be_bytes(),
        );
        for i in 0..count {
            name(bytes, &format!("minecraft:biome{i}"));
        }
    }

    fn packed_data(bytes: &mut Vec<u8>, words: &[u64]) {
        tag(bytes, TagType::LongArray, "data");
        bytes.extend_from_slice(
            &i32::try_from(words.len())
                .expect("fixture word count fits")
                .to_be_bytes(),
        );
        for &word in words {
            bytes.extend_from_slice(&word.to_be_bytes());
        }
    }

    fn words_for_palette(count: usize, index: impl Fn(usize) -> usize) -> Vec<u64> {
        let bits = (usize::BITS - (count - 1).leading_zeros()) as usize;
        let per_word = 64 / bits;
        let mut words = vec![0u64; 64usize.div_ceil(per_word)];
        for cell in 0..64 {
            words[cell / per_word] |= u64::try_from(index(cell)).expect("small palette index")
                << ((cell % per_word) * bits);
        }
        words
    }

    fn decode(bytes: &[u8]) -> Result<Vec<u8>, BiomeImportError> {
        let mut builder = Builder;
        let mut scratch = BiomeDecodeScratch::new();
        let mut decoder = ExactBiomeDecoder::new(&Resolver, &mut builder, &mut scratch);
        let mut reader = NbtReader::new(
            bytes,
            NbtLimits::new(256, 128, 128, 8).expect("valid fixture limit"),
        );
        let result = decoder.decode_section(&mut reader, 2)?;
        assert_eq!(reader.offset(), bytes.len());
        Ok(result)
    }

    #[test]
    fn uniform_saved_palette_does_not_need_a_data_array() {
        let mut bytes = Vec::new();
        palette(&mut bytes, 1);
        bytes.push(TagType::End as u8);
        assert_eq!(decode(&bytes), Ok(vec![0; 64]));
    }

    #[test]
    fn nonspanning_saved_palette_widths_decode_every_quart_cell() {
        for count in [2usize, 3, 5, 9, 17, 33, 64] {
            let mut bytes = Vec::new();
            // Saved data is legal before the palette, so the decoder must not depend on tag order.
            packed_data(
                &mut bytes,
                &words_for_palette(count, |i| (i * 17 + 3) % count),
            );
            palette(&mut bytes, count);
            bytes.push(TagType::End as u8);
            let actual = decode(&bytes).expect("all palette widths decode");
            assert_eq!(actual.len(), 64);
            for (cell, &biome) in actual.iter().enumerate() {
                assert_eq!(usize::from(biome), (cell * 17 + 3) % count);
            }
        }
    }

    #[test]
    fn invalid_saved_biomes_fail_closed_without_defaulting_to_plains() {
        let mut empty = Vec::new();
        palette(&mut empty, 0);
        empty.push(TagType::End as u8);
        assert_eq!(
            decode(&empty),
            Err(BiomeImportError::PaletteCardinality {
                section_index: 2,
                actual: 0,
            })
        );
        let mut missing_data = Vec::new();
        palette(&mut missing_data, 2);
        missing_data.push(TagType::End as u8);
        assert_eq!(
            decode(&missing_data),
            Err(BiomeImportError::MissingPackedData { section_index: 2 })
        );
        let mut duplicate = Vec::new();
        palette(&mut duplicate, 1);
        palette(&mut duplicate, 1);
        duplicate.push(TagType::End as u8);
        assert_eq!(
            decode(&duplicate),
            Err(BiomeImportError::DuplicateField {
                section_index: 2,
                field: "biomes.palette",
            })
        );
        let mut wrong_count = Vec::new();
        palette(&mut wrong_count, 3);
        packed_data(&mut wrong_count, &[0]);
        wrong_count.push(TagType::End as u8);
        assert!(matches!(
            decode(&wrong_count),
            Err(BiomeImportError::PackedWordCount {
                section_index: 2,
                bits: 2,
                expected: 2,
                actual: 1
            })
        ));
        let mut unknown = Vec::new();
        tag(&mut unknown, TagType::List, "palette");
        unknown.push(TagType::String as u8);
        unknown.extend_from_slice(&1i32.to_be_bytes());
        name(&mut unknown, "minecraft:not_a_real_biome");
        unknown.push(TagType::End as u8);
        assert_eq!(
            decode(&unknown),
            Err(BiomeImportError::UnknownBiome {
                section_index: 2,
                palette_index: 0,
            })
        );
    }

    #[test]
    fn bogus_palette_indices_and_uniform_data_are_rejected() {
        let mut bad_index = Vec::new();
        palette(&mut bad_index, 3);
        packed_data(&mut bad_index, &words_for_palette(3, |_| 3));
        bad_index.push(TagType::End as u8);
        assert_eq!(
            decode(&bad_index),
            Err(BiomeImportError::PaletteIndexOutOfRange {
                section_index: 2,
                cell: 0,
                palette_index: 3,
                palette_entries: 3,
            })
        );
        let mut uniform_data = Vec::new();
        palette(&mut uniform_data, 1);
        packed_data(&mut uniform_data, &[0]);
        uniform_data.push(TagType::End as u8);
        assert_eq!(
            decode(&uniform_data),
            Err(BiomeImportError::UniformHasData {
                section_index: 2,
                words: 1,
            })
        );
    }
}
