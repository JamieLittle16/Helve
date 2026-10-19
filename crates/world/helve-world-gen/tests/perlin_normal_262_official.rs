//! Real 26.2 JVM-observed constructor states + independently captured 320
//! Perlin/Normal raw-bit outputs. Neither the in-Rust constructor RNG law
//! nor arbitrary 26.2 density routing is admitted by these tests.

use helve_world_gen::improved_noise_262::{ImprovedNoise262, ObservedNoiseStateError};
use helve_world_gen::perlin_normal_262::{NormalNoise262, PerlinNoise262};

const STATES: &str = include_str!("data/perlin_normal_26_2_observed_state.tsv");
const VECTORS: &str = include_str!("data/perlin_normal_26_2_rawbits.tsv");

const SEEDS: [&str; 5] = [
    "0x0000000000000000",
    "0x0000000000000001",
    "0xffffffffffffffff",
    "0x8000000000000000",
    "0x9e3779b97f4a7c15",
];

fn parse_hex_bits(hex: &str) -> f64 {
    let hex = hex.strip_prefix("0x").unwrap_or(hex);
    assert_eq!(hex.len(), 16, "exact 64-bit JVM floating representation");
    f64::from_bits(u64::from_str_radix(hex, 16).expect("16 valid hex digits"))
}

fn decode_permutation(hex: &str) -> [u8; 256] {
    assert_eq!(hex.len(), 512, "exact 256-byte JVM permutation");
    let mut result = [0_u8; 256];
    for (index, entry) in result.iter_mut().enumerate() {
        *entry = u8::from_str_radix(&hex[index * 2..index * 2 + 2], 16)
            .expect("byte-exact source-free permutation");
    }
    result
}

fn observed_perlin(seed: &str, branch: &str) -> PerlinNoise262 {
    let mut config = None;
    let mut octaves: [Option<ImprovedNoise262>; 4] = std::array::from_fn(|_| None);
    let mut occupied = [false; 4];
    for row in STATES
        .lines()
        .filter(|line| !line.starts_with('#') && !line.is_empty())
    {
        let cells: Vec<_> = row.split_whitespace().collect();
        if cells.len() < 4 || cells[1] != seed || cells[2] != branch {
            continue;
        }
        match cells[0] {
            "C" => {
                assert_eq!(cells.len(), 11);
                assert!(config.is_none(), "duplicate root state");
                let first_octave = cells[3].parse::<i32>().expect("octave position");
                let input_factor = parse_hex_bits(cells[4]);
                let value_factor = parse_hex_bits(cells[5]);
                let _max_value = parse_hex_bits(cells[6]);
                let amplitudes = [
                    parse_hex_bits(cells[7]),
                    parse_hex_bits(cells[8]),
                    parse_hex_bits(cells[9]),
                    parse_hex_bits(cells[10]),
                ];
                config = Some((first_octave, amplitudes, input_factor, value_factor));
            }
            "O" => {
                assert_eq!(cells.len(), 8);
                let slot = cells[3].parse::<usize>().expect("octave slot index");
                assert!(
                    slot < 4 && !occupied[slot],
                    "duplicated/invalid octave slot"
                );
                occupied[slot] = true;
                if cells[4] == "NULL" {
                    assert_eq!(cells[5..], ["-", "-", "-"]);
                } else {
                    let sampler = ImprovedNoise262::from_observed_parts(
                        decode_permutation(cells[4]),
                        parse_hex_bits(cells[5]),
                        parse_hex_bits(cells[6]),
                        parse_hex_bits(cells[7]),
                    )
                    .expect("official octave must be an unsigned permutation bijection");
                    octaves[slot] = Some(sampler);
                }
            }
            _ => panic!("unexpected constructor-state record"),
        }
    }
    assert!(occupied.iter().all(|&is_present| is_present));
    let (first, amplitudes, input_factor, value_factor) =
        config.expect("official source-free configuration row");
    assert_eq!(first, -3);
    assert!(octaves[1].is_none());
    PerlinNoise262::from_observed_parts(first, amplitudes, octaves, input_factor, value_factor)
}

fn observed_normal(seed: &str) -> NormalNoise262 {
    let mut normal_factor = None;
    for row in STATES.lines().filter(|line| line.starts_with("N ")) {
        let cells: Vec<_> = row.split_whitespace().collect();
        assert_eq!(cells.len(), 3);
        if cells[1] == seed {
            assert!(normal_factor.is_none());
            normal_factor = Some(parse_hex_bits(cells[2]));
        }
    }
    NormalNoise262::from_observed_parts(
        observed_perlin(seed, "F"),
        observed_perlin(seed, "S"),
        normal_factor.expect("captured normal scaling factor"),
    )
}

#[test]
fn exactly_320_official_26_2_perlin_and_normal_results_match_raw_bits() {
    let lines: Vec<_> = VECTORS
        .lines()
        .filter(|line| !line.starts_with('#') && !line.is_empty())
        .collect();
    assert_eq!(lines.len(), 160, "no missing / duplicated official points");
    for (seed_index, seed) in SEEDS.iter().enumerate() {
        let perlin = observed_perlin(seed, "P");
        let normal = observed_normal(seed);
        assert_eq!(perlin.first_octave(), -3);
        for (position, line) in lines[seed_index * 32..(seed_index + 1) * 32]
            .iter()
            .enumerate()
        {
            let fields: Vec<_> = line.split_whitespace().collect();
            assert_eq!(fields.len(), 6);
            assert_eq!(fields[0], *seed, "official source vector seed ordering");
            let x = parse_hex_bits(fields[1]);
            let y = parse_hex_bits(fields[2]);
            let z = parse_hex_bits(fields[3]);
            let expected_perlin = parse_hex_bits(fields[4]).to_bits();
            let expected_normal = parse_hex_bits(fields[5]).to_bits();
            let actual_perlin = perlin.sample(x, y, z).to_bits();
            let actual_normal = normal.sample(x, y, z).to_bits();
            assert_eq!(
                actual_perlin, expected_perlin,
                "Perlin JVM seed {seed}, vector {position}, ({x},{y},{z})"
            );
            assert_eq!(
                actual_normal, expected_normal,
                "Normal JVM seed {seed}, vector {position}, ({x},{y},{z})"
            );
        }
    }
}

#[test]
fn direct_seed_constructors_match_all_five_complete_official_states_and_320_outputs() {
    // Two independent paths: (1) derive each octave from the direct seed,
    // (2) decode complete read-only JVM-observed permutations/offset bits.
    // Both must produce the same four-slot masks, amplitude/frequency factors
    // and both distinct NormalNoise branches, not merely matching samples.
    let lines: Vec<_> = VECTORS
        .lines()
        .filter(|line| !line.starts_with('#') && !line.is_empty())
        .collect();
    assert_eq!(lines.len(), SEEDS.len() * 32);

    for (seed_index, &seed) in SEEDS.iter().enumerate() {
        let seed_bits = u64::from_str_radix(seed.trim_start_matches("0x"), 16)
            .expect("pinned direct-seed bits");
        let perlin = PerlinNoise262::from_direct_seed_observed_profile(seed_bits);
        let normal = NormalNoise262::from_direct_seed_observed_profile(seed_bits);
        assert!(
            perlin.state_bits_equal(&observed_perlin(seed, "P")),
            "direct seed {seed} mismatches complete Perlin JVM constructor state"
        );
        assert!(
            normal.state_bits_equal(&observed_normal(seed)),
            "direct seed {seed} mismatches complete Normal JVM constructor state"
        );
        for (position, line) in lines[seed_index * 32..(seed_index + 1) * 32]
            .iter()
            .enumerate()
        {
            let fields: Vec<_> = line.split_whitespace().collect();
            assert_eq!(fields.len(), 6);
            assert_eq!(fields[0], seed);
            let (x, y, z) = (
                parse_hex_bits(fields[1]),
                parse_hex_bits(fields[2]),
                parse_hex_bits(fields[3]),
            );
            assert_eq!(
                perlin.sample(x, y, z).to_bits(),
                parse_hex_bits(fields[4]).to_bits(),
                "seed-derived Perlin {seed}, sample {position}"
            );
            assert_eq!(
                normal.sample(x, y, z).to_bits(),
                parse_hex_bits(fields[5]).to_bits(),
                "seed-derived Normal {seed}, sample {position}"
            );
        }
    }
}

#[test]
fn profile_seed_constructors_preserve_legacy_48_bit_seed_truncation() {
    // Java RandomSource.create(long) in the pinned profile is a 48-bit
    // legacy seed, unlike an arbitrary worldgen seed or Xoroshiro stream.
    let base = NormalNoise262::from_direct_seed_observed_profile(0);
    let upper_bit = NormalNoise262::from_direct_seed_observed_profile(1_u64 << 63);
    assert!(base.state_bits_equal(&upper_bit));
    assert!(!base.state_bits_equal(&NormalNoise262::from_direct_seed_observed_profile(1)));
}

#[test]
fn source_observed_normal_first_branch_equals_independent_perlin_state() {
    // The recorded constructor state confirms that Normal's first branch
    // uses exactly the independently captured Perlin factory output for all
    // five direct factory seeds, not an inferred RNG clone.
    for seed in SEEDS {
        let stand_alone = observed_perlin(seed, "P");
        let inside_normal = observed_perlin(seed, "F");
        for (x, y, z) in [
            (0.0, 0.0, 0.0),
            (-16.0, -63.875, -16.0),
            (33_554_432.125, 0.125, -33_554_432.125),
        ] {
            assert_eq!(
                stand_alone.sample(x, y, z).to_bits(),
                inside_normal.sample(x, y, z).to_bits(),
                "identical official constructor state, seed {seed}"
            );
        }
    }
}

#[test]
fn coherent_perlin_and_normal_planes_preserve_every_scalar_result_bit() {
    let origins = [
        (0.0, 0.0, 0.0),
        (-16.0, -64.0, -16.0),
        (-31.125, 319.875, 31.125),
        (33_554_432.25, -63.875, -33_554_432.25),
    ];
    for seed in SEEDS {
        let perlin = observed_perlin(seed, "P");
        let normal = observed_normal(seed);
        for (x, y, z) in origins {
            let mut p = [0.0_f64; 256];
            let mut n = [0.0_f64; 256];
            perlin.sample_plane_16x16(x, y, z, &mut p);
            normal.sample_plane_16x16(x, y, z, &mut n);
            for local_z in 0_u8..16 {
                for local_x in 0_u8..16 {
                    let coordinate_x = x + f64::from(local_x);
                    let coordinate_z = z + f64::from(local_z);
                    let index = usize::from(local_z) * 16 + usize::from(local_x);
                    assert_eq!(
                        p[index].to_bits(),
                        perlin.sample(coordinate_x, y, coordinate_z).to_bits(),
                        "Perlin grid seed {seed} at ({coordinate_x}, {y}, {coordinate_z})"
                    );
                    assert_eq!(
                        n[index].to_bits(),
                        normal.sample(coordinate_x, y, coordinate_z).to_bits(),
                        "Normal grid seed {seed} at ({coordinate_x}, {y}, {coordinate_z})"
                    );
                }
            }
        }
    }
}

#[test]
fn invalid_observed_permutation_is_refused() {
    let result = ImprovedNoise262::from_observed_parts([0; 256], 0.0, 0.0, 0.0);
    assert!(matches!(
        result,
        Err(ObservedNoiseStateError::InvalidPermutation)
    ));
}

#[test]
fn observed_sampler_reads_are_deterministic_across_cold_workers() {
    let normal = observed_normal(SEEDS[0]);
    let expected = normal.sample(-16.125, -63.875, 15.125).to_bits();
    std::thread::scope(|scope| {
        for _ in 0..4 {
            let shared = &normal;
            scope.spawn(move || {
                for _ in 0..100 {
                    assert_eq!(shared.sample(-16.125, -63.875, 15.125).to_bits(), expected);
                }
            });
        }
    });
}
