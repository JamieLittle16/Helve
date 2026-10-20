//! Exact-bit official 26.2 stock registry world-seed **observed-state replay**.
//!
//! Unlike the direct-seeded four-slot profile, these 15 complete numerical
//! states were independently prepared by the pinned official stock JVM via
//! `RandomState` and three registered noise keys. The Rust implementation loads
//! those states into the EXISTING immutable Improved/Perlin/Normal evaluators.
//!
//! The test must not be described as a Rust world-seed RNG constructor. It
//! qualifies the stock-shaped *sampling* path, not seed -> prepared state,
//! independent VAR/SEM review, `NoiseRouter`, or production world generation.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::improved_noise_262::ImprovedNoise262;
use helve_world_gen::registered_noise_state_262::{
    RegisteredNoiseDensityObserved262, RegisteredNormalObserved262, RegisteredPerlinObserved262,
};

use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, from_stock_world_seed_candidate,
};

const STATES: &str = include_str!("data/stock_registered_observed_state_26_2.txt");
const ORACLE: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../../vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt"
));
const SEEDS: [u64; 5] = [0, 1, u64::MAX, 0x8000_0000_0000_0000, 0x9e37_79b9_7f4a_7c15];
const KEYS: [&str; 3] = ["TEMPERATURE", "CONTINENTALNESS", "EROSION"];
const SCALES: [DirectNoiseScale262; 3] = [
    DirectNoiseScale262::Unit,
    DirectNoiseScale262::QuarterHorizontal,
    DirectNoiseScale262::QuarterHorizontalHalfVertical,
];
const Y: [i32; 32] = [
    -4096, -65, -64, -63, -31, -30, -29, -1, 0, 1, 15, 16, 17, 18, 63, 64, 127, 128, 255, 256, 318,
    319, 320, 321, 1024, -1024, -384, -320, 319, -64, 17, 320,
];

fn hex_bits(s: &str) -> u64 {
    assert_eq!(s.len(), 16, "expected exactly sixteen raw IEEE hex digits");
    u64::from_str_radix(s, 16).expect("source-free bit encoding")
}

fn next_record<'a>(lines: &mut impl Iterator<Item = &'a str>) -> &'a str {
    lines
        .next()
        .expect("complete official registered-state fixture")
}

fn read_branch<'a>(lines: &mut impl Iterator<Item = &'a str>) -> RegisteredPerlinObserved262 {
    let raw = next_record(lines);
    let mut fields = raw.split_whitespace();
    assert_eq!(fields.next(), Some("B"));
    let first_octave = fields
        .next()
        .expect("Perlin first octave")
        .parse::<i32>()
        .expect("signed Java octave");
    let input_factor = f64::from_bits(hex_bits(fields.next().expect("Perlin input factor")));
    let value_factor = f64::from_bits(hex_bits(fields.next().expect("Perlin value factor")));
    let amplitudes: Vec<f64> = fields
        .next()
        .expect("registered amplitudes")
        .split(',')
        .map(|raw| f64::from_bits(hex_bits(raw)))
        .collect();
    assert!(fields.next().is_none(), "unrecognised Perlin fixture data");

    let mut octaves = Vec::with_capacity(amplitudes.len());
    for &amplitude in &amplitudes {
        let raw = next_record(lines);
        let mut slot = raw.split_whitespace();
        assert_eq!(slot.next(), Some("O"));
        let next = slot.next().expect("octave presence or permutation");
        if next == "-" {
            assert_eq!(amplitude.to_bits(), 0, "missing octave has nonzero weight");
            assert!(slot.next().is_none());
            octaves.push(None);
            continue;
        }
        assert_ne!(amplitude.to_bits(), 0, "active octave has zero weight");
        assert_eq!(next.len(), 512, "a permutation is exactly 256 bytes");
        let mut permutation = [0_u8; 256];
        for (index, byte) in permutation.iter_mut().enumerate() {
            *byte = u8::from_str_radix(&next[2 * index..2 * index + 2], 16)
                .expect("hex permutation byte");
        }
        let x = f64::from_bits(hex_bits(slot.next().expect("x offset")));
        let y = f64::from_bits(hex_bits(slot.next().expect("y offset")));
        let z = f64::from_bits(hex_bits(slot.next().expect("z offset")));
        assert!(
            slot.next().is_none(),
            "unrecognised improved-noise fixture data"
        );
        octaves.push(Some(
            ImprovedNoise262::from_observed_parts(permutation, x, y, z)
                .expect("stock permutation is a complete bijection"),
        ));
    }
    RegisteredPerlinObserved262::from_observed_parts(
        first_octave,
        amplitudes.into_boxed_slice(),
        octaves.into_boxed_slice(),
        input_factor,
        value_factor,
    )
    .expect("bounded complete stock Perlin state")
}

fn load_stock_observed_states() -> Vec<RegisteredNormalObserved262> {
    let mut lines = STATES
        .lines()
        .filter(|line| !line.is_empty() && !line.starts_with('#'));
    let mut states = Vec::with_capacity(15);
    for &seed in &SEEDS {
        for &key in &KEYS {
            let raw = next_record(&mut lines);
            let mut fields = raw.split_whitespace();
            assert_eq!(fields.next(), Some("N"));
            assert_eq!(hex_bits(fields.next().expect("world-seed bits")), seed);
            assert_eq!(fields.next(), Some(key));
            let first_octave = fields
                .next()
                .expect("registered first octave")
                .parse::<i32>()
                .expect("signed octave");
            let factor = f64::from_bits(hex_bits(fields.next().expect("normal value factor")));
            assert!(fields.next().is_none(), "unexpected normal header fields");
            let first = read_branch(&mut lines);
            let second = read_branch(&mut lines);
            assert_eq!(first.first_octave(), first_octave);
            assert_eq!(second.first_octave(), first_octave);
            assert_eq!(first.octave_count(), second.octave_count());
            assert_eq!(
                first.octave_count(),
                match key {
                    "TEMPERATURE" => 6,
                    "CONTINENTALNESS" => 9,
                    "EROSION" => 5,
                    _ => unreachable!("three stock keys"),
                }
            );
            assert_eq!(next_record(&mut lines), "E");
            states.push(
                RegisteredNormalObserved262::from_observed_parts(first, second, factor)
                    .expect("finite stock normal value factor"),
            );
        }
    }
    assert!(
        lines.next().is_none(),
        "unrecognised trailing stock fixture records"
    );
    assert_eq!(states.len(), 15);
    states
}

fn block_xyz(index: usize) -> (i32, i32, i32) {
    let i = i32::try_from(index).expect("exactly 32 reference positions");
    let x = (if i % 2 == 0 { 33_554_432 } else { -33_554_432 }) + 13 * i;
    let z = (if i % 3 == 0 { 17 * i } else { -17 * i }) - 16;
    (x, Y[index], z)
}

#[test]
fn all_1440_stock_worldseed_bits_match_existing_rust_sampler_from_observed_state() {
    let observed = load_stock_observed_states();
    let oracle: Vec<&str> = ORACLE.lines().collect();
    assert_eq!(
        oracle.len(),
        1440,
        "existing independent JVM oracle is immutable"
    );
    assert_eq!(oracle[0], "3fe642a30a35f266");
    assert_eq!(oracle[480], "bfb1cb44d1eacac0");
    assert_eq!(oracle[1439], "3fc3cbbb372a1759");

    for (profile, &scale) in SCALES.iter().enumerate() {
        for (seed_index, &seed) in SEEDS.iter().enumerate() {
            for (key_index, &key) in KEYS.iter().enumerate() {
                let state = &observed[seed_index * KEYS.len() + key_index];
                let density = RegisteredNoiseDensityObserved262::new(state, scale);
                for index in 0..32 {
                    let (x, y, z) = block_xyz(index);
                    let row = (((profile * SEEDS.len() + seed_index) * KEYS.len() + key_index)
                        * 32)
                        + index;
                    let expected = hex_bits(oracle[row]);
                    let actual = density.sample_block(x, y, z).to_bits();
                    assert_eq!(
                        actual, expected,
                        "stock observed-state replay bit mismatch at profile={profile} seed_bits={seed:016x} key={key} point={index} xyz=({x},{y},{z}) row={row}"
                    );
                }
            }
        }
    }
}

#[test]
fn observed_stock_states_are_seed_dependent_and_nontruncated() {
    let states = load_stock_observed_states();
    for key_index in 0..KEYS.len() {
        for seed_index in 0..SEEDS.len() {
            let i = seed_index * KEYS.len() + key_index;
            let next = ((seed_index + 1) % SEEDS.len()) * KEYS.len() + key_index;
            assert!(
                !states[i].state_bits_equal(&states[next]),
                "distinct signed stock worldseeds cannot alias observed state"
            );
        }
    }
}

#[test]
fn all_15_seed_derived_stock_sampler_states_match_complete_official_snapshots() {
    let actual = load_stock_observed_states();
    let keys = [
        StockRegisteredNoiseKey262::Temperature,
        StockRegisteredNoiseKey262::Continentalness,
        StockRegisteredNoiseKey262::Erosion,
    ];
    for (seed_index, seed) in SEEDS.iter().enumerate() {
        for (key_index, key) in keys.iter().enumerate() {
            let derived = from_stock_world_seed_candidate(*seed, *key);
            let slot = seed_index * KEYS.len() + key_index;
            assert!(
                derived.state_bits_equal(&actual[slot]),
                "full prepared-state mismatch at signed seed_bits={seed:016x}, stock key={}",
                KEYS[key_index],
            );
        }
    }
}

#[test]
fn all_1440_stock_worldseed_bits_match_rust_seed_derived_constructor() {
    let keys = [
        StockRegisteredNoiseKey262::Temperature,
        StockRegisteredNoiseKey262::Continentalness,
        StockRegisteredNoiseKey262::Erosion,
    ];
    let generated: Vec<_> = SEEDS
        .iter()
        .flat_map(|seed| {
            keys.iter()
                .map(move |key| from_stock_world_seed_candidate(*seed, *key))
        })
        .collect();
    let oracle: Vec<&str> = ORACLE.lines().collect();
    assert_eq!(oracle.len(), 1440);

    for (profile, &scale) in SCALES.iter().enumerate() {
        for (seed_index, &seed) in SEEDS.iter().enumerate() {
            for (key_index, &key) in KEYS.iter().enumerate() {
                let state = &generated[seed_index * KEYS.len() + key_index];
                let density = RegisteredNoiseDensityObserved262::new(state, scale);
                for point in 0..32 {
                    let (x, y, z) = block_xyz(point);
                    let row = (((profile * SEEDS.len() + seed_index) * KEYS.len()
                        + key_index) * 32) + point;
                    let expected = hex_bits(oracle[row]);
                    assert_eq!(
                        density.sample_block(x, y, z).to_bits(),
                        expected,
                        "seed-derived 26.2 stock density mismatch profile={profile} seed={seed:016x} key={key} point={point} xyz=({x},{y},{z})",
                    );
                }
            }
        }
    }
}
