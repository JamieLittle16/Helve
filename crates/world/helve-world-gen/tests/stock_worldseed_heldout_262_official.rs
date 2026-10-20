//! Independently held-out real 26.2 stock JVM -> Rust world-seed noise parity.
//!
//! This is **not** the original 1,440-vector corpus: four different signed
//! seeds and sixteen fresh coordinates per key/profile were acquired through
//! stock VanillaRegistries -> RandomState -> DensityFunctions.Noise.compute.
//! The source-free raw IEEE-754 bits are frozen independently of this Rust
//! seed-derived constructor. No observed permutation/offset data is loaded.
//!
//! Scope is exactly three built-in registered noise keys and three scale pairs.
//! This alone does NOT independently admit RNG source laws, arbitrary registries,
//! a complete NoiseRouter, production worldgen or chunk publication.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262, from_stock_world_seed_candidate,
};

const OFFICIAL: &str = include_str!("data/stock_worldseed_heldout_576_rawbits.txt");
const SEEDS: [u64; 4] = [
    0x0123_4567_89ab_cdef,
    0x7fff_ffff_ffff_ffff,
    0x8000_0000_0000_0001,
    0xf0e1_d2c3_b4a5_9687,
];
const KEYS: [StockRegisteredNoiseKey262; 3] = [
    StockRegisteredNoiseKey262::Temperature,
    StockRegisteredNoiseKey262::Continentalness,
    StockRegisteredNoiseKey262::Erosion,
];
const PROFILES: [DirectNoiseScale262; 3] = [
    DirectNoiseScale262::Unit,
    DirectNoiseScale262::QuarterHorizontal,
    DirectNoiseScale262::QuarterHorizontalHalfVertical,
];
const POINTS: [(i32, i32, i32); 16] = [
    (0, 0, 0),
    (-1, -64, 1),
    (1, 319, -1),
    (33_554_431, -63, -33_554_432),
    (-33_554_431, 320, 33_554_431),
    (2_147_483_600, 255, -2_147_483_600),
    (-2_147_483_600, -4096, 2_147_483_600),
    (105, -65, -417),
    (-1_000_000, 2048, 1_000_000),
    (123_456, -128, -654_321),
    (-16, 0, 16),
    (15, 256, -15),
    (33_554_433, 321, -33_554_433),
    (-33_554_433, -31, 33_554_433),
    (2048, 63, -2048),
    (-2049, 64, 2049),
];

fn pinned_bits() -> Vec<u64> {
    assert!(
        OFFICIAL.is_ascii() && OFFICIAL.ends_with('\n'),
        "576-row source-free official fixture must be newline-terminated ASCII"
    );
    let lines: Vec<&str> = OFFICIAL.lines().collect();
    assert_eq!(
        lines.len(),
        576,
        "official held-out oracle must have 576 rows"
    );
    assert_eq!(lines[0], "bfded41016e4261a");
    assert_eq!(lines[287], "bfa078eb58200b97");
    assert_eq!(lines[575], "3fbe82b27db6a527");
    let mut checksum = 0_u64;
    let mut words = Vec::with_capacity(576);
    for (index, line) in lines.iter().enumerate() {
        assert_eq!(line.len(), 16, "bad held-out raw-bit width at {index}");
        assert!(
            line.bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)),
            "noncanonical held-out hex at row {index}"
        );
        let word = u64::from_str_radix(line, 16).expect("finite raw IEEE-754 word");
        assert_ne!(
            (word >> 52) & 0x7ff,
            0x7ff,
            "nonfinite held-out word {index}"
        );
        checksum = checksum.rotate_left(7) ^ word;
        words.push(word);
    }
    assert_eq!(
        checksum, 0xc445_0561_e08c_eef6,
        "source-free official held-out reference changed"
    );
    words
}

#[test]
fn all_576_unseen_stock_worldseed_density_bits_match_immutable_rust_seed_constructor() {
    let expected = pinned_bits();
    let mut compared = 0_usize;
    for (profile_index, &profile) in PROFILES.iter().enumerate() {
        for (seed_index, &seed) in SEEDS.iter().enumerate() {
            let state = StockWorldSeededNoiseSet262::new_candidate(seed);
            for (key_index, &key) in KEYS.iter().enumerate() {
                let density = state.density(key, profile);
                for (point_index, &(x, y, z)) in POINTS.iter().enumerate() {
                    let row = (((profile_index * SEEDS.len() + seed_index) * KEYS.len()
                        + key_index)
                        * POINTS.len())
                        + point_index;
                    assert_eq!(row, compared, "JVM row framing/order mismatch");
                    let actual = density.sample_block(x, y, z).to_bits();
                    assert_eq!(
                        actual, expected[row],
                        "NEW independent stock JVM held-out bit mismatch row={row} scale={profile:?} signed_seed_bits={seed:016x} key={key:?} point={point_index} xyz=({x},{y},{z}) expected={:016x} actual={actual:016x}",
                        expected[row],
                    );
                    compared += 1;
                }
            }
        }
    }
    assert_eq!(compared, 576, "not all held-out JVM answers exercised");
}

#[test]
fn new_unseen_worldseeds_derive_same_prepared_states_with_shared_or_single_key_owner() {
    for &seed in &SEEDS {
        let combined = StockWorldSeededNoiseSet262::new_candidate(seed);
        for &key in &KEYS {
            let independent = from_stock_world_seed_candidate(seed, key);
            assert!(
                combined.get(key).state_bits_equal(&independent),
                "cold one-root and independent-key constructor disagree at seed={seed:016x} key={key:?}"
            );
        }
    }
}
