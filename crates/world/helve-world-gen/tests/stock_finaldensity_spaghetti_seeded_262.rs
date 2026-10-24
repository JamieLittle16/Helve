//! Genuine 26.2 `finalDensity` `spaghetti_3d_thickness` Noise leaf:
//! independently seed-derived Rust sampler versus original JVM 128 raw words.
//! The old words are borrowed from the *unchanged* 21st source-only fixture,
//! not replayed as constructor input and not duplicated in a new fixture.
//! Scoped to four fixed signed world seeds, unit axes and `SinglePointContext`.
//! No general all-input source law, `NoiseChunk` lifecycle, VAR/SEM or production.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262, from_stock_world_seed_candidate,
};

const ORIGINAL_NOISE: &str =
    include_str!("data/stock_finaldensity_twenty_first_actual_noise_leaf_128_rawbits.tsv");

const SEEDS: [u64; 4] = [
    0x0123_4567_89ab_cdef,
    0x7fff_ffff_ffff_ffff,
    0x8000_0000_0000_0001,
    0xf0e1_d2c3_b4a5_9687,
];
const KEY: StockRegisteredNoiseKey262 = StockRegisteredNoiseKey262::Spaghetti3DThickness;
const POINTS: [(i32, i32, i32); 32] = [
    (0, -64, 0),
    (0, 0, 0),
    (0, 63, 0),
    (0, 64, 0),
    (0, 65, 0),
    (0, 128, 0),
    (0, 192, 0),
    (0, 255, 0),
    (0, 320, 0),
    (1, -63, -1),
    (-1, -1, 1),
    (15, 64, 15),
    (16, 64, 16),
    (-16, 63, -16),
    (-17, 65, -17),
    (31, 127, -31),
    (32, 128, -32),
    (128, 64, 128),
    (128, 128, 128),
    (-128, 128, -128),
    (256, 255, -256),
    (-256, 0, 256),
    (1024, 64, -1024),
    (-1025, 65, 1025),
    (123_456, 73, -654_321),
    (1_000_000, 96, 1_000_000),
    (-1_000_000, 96, -1_000_000),
    (33_554_431, 128, -33_554_432),
    (-33_554_431, -63, 33_554_431),
    (2_147_483_600, 255, -2_147_483_600),
    (-2_147_483_600, -4096, 2_147_483_600),
    (0, -65, 0),
];

fn old_original_ieee_words() -> Vec<u64> {
    assert!(ORIGINAL_NOISE.is_ascii() && ORIGINAL_NOISE.ends_with('\n'));
    let lines: Vec<_> = ORIGINAL_NOISE.lines().collect();
    assert_eq!(lines.len(), 128, "only 4 seeds x 32 actual old leaf words");
    let mut words = Vec::with_capacity(128);
    let mut checksum = 0_u64;
    for (index, line) in lines.iter().enumerate() {
        assert_eq!(
            line.len(),
            16,
            "source-only fixture word {index} not exact 64-bit"
        );
        assert!(
            line.bytes()
                .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
        );
        let word = u64::from_str_radix(line, 16).expect("canonical source-only numeric");
        assert!(
            f64::from_bits(word).is_finite(),
            "nonfinite old Noise output {index}"
        );
        checksum = checksum.rotate_left(7) ^ word;
        words.push(word);
    }
    assert_eq!(
        checksum, 0x1054_b79a_effb_8e6e,
        "old original Noise fixture changed"
    );
    assert_eq!(words[0], 0x3fe4_8f11_c0c8_841c);
    assert_eq!(words[127], 0xbfe6_42d5_a54d_5628);
    words
}

#[test]
fn real_spaghetti_noise_seeded_native_matches_all_128_old_stock_jvm_leaf_words() {
    let expected = old_original_ieee_words();
    let mut checked = 0;
    for (seed_index, &seed) in SEEDS.iter().enumerate() {
        let native = StockWorldSeededNoiseSet262::new_candidate(seed);
        let density = native.density(KEY, DirectNoiseScale262::Unit);
        for (point_index, &(x, y, z)) in POINTS.iter().enumerate() {
            let row = seed_index * POINTS.len() + point_index;
            assert_eq!(row, checked);
            let actual = density.sample_block(x, y, z).to_bits();
            assert_eq!(
                actual, expected[row],
                "original finalDensity spaghetti Noise parity seed={seed:016x}                  row={row} XYZ=({x},{y},{z}) original={:016x} native={actual:016x}",
                expected[row],
            );
            checked += 1;
        }
    }
    assert_eq!(checked, 128, "all four actual original JVM seeds consumed");
}

#[test]
fn independent_cold_constructor_matches_four_key_combined_world_owner_state() {
    for &seed in &SEEDS {
        let owner = StockWorldSeededNoiseSet262::new_candidate(seed);
        let independently_derived = from_stock_world_seed_candidate(seed, KEY);
        assert!(
            owner.get(KEY).state_bits_equal(&independently_derived),
            "spaghetti single-key and full four-key cold states moved at {seed:016x}"
        );
    }
}
