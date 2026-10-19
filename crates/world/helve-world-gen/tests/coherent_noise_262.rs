//! Differential qualification for the coherent 16×16 noise plane: exact
//! scalar `f64::to_bits()` at all 256 positions, not approximate equality.
//! Keeps the captured 160 official JVM vector points as extra first-cell
//! anchors without claiming full worldgen source/VAR/SEM admission.

use std::collections::BTreeMap;

use helve_world_gen::improved_noise_262::ImprovedNoise262;

fn hex64(value: &str) -> u64 {
    u64::from_str_radix(
        value.strip_prefix("0x").expect("raw oracle has hex prefix"),
        16,
    )
    .expect("raw oracle has exactly 64-bit hex")
}

fn verify_plane(sampler: &ImprovedNoise262, origin_x: f64, y: f64, origin_z: f64) -> u64 {
    let mut output = [f64::NAN; 256];
    sampler.sample_plane_16x16(origin_x, y, origin_z, &mut output);
    let mut checksum = 0_u64;
    for local_z in 0_u8..16 {
        for local_x in 0_u8..16 {
            let expected = sampler
                .sample(
                    origin_x + f64::from(local_x),
                    y,
                    origin_z + f64::from(local_z),
                )
                .to_bits();
            let actual = output[usize::from(local_z) * 16 + usize::from(local_x)].to_bits();
            assert_eq!(
                actual, expected,
                "x={origin_x} y={y} z={origin_z} local_x={local_x} local_z={local_z} actual={actual:#018x} expected={expected:#018x}",
            );
            checksum = checksum.rotate_left(5) ^ actual;
        }
    }
    checksum
}

#[test]
fn coherent_planes_match_scalar_on_negative_boundaries_fractional_and_large_origins() {
    const SEEDS: [u64; 5] = [0, 1, u64::MAX, 1 << 63, 0x9e37_79b9_7f4a_7c15];
    const ORIGINS: [(f64, f64, f64); 18] = [
        (0.0, 0.0, 0.0),
        (-0.0, -0.0, -0.0),
        (-16.0, -64.0, -16.0),
        (-17.0, -63.5, 15.0),
        (15.0, 319.0, -17.0),
        (16.0, -64.0, 16.0),
        (-31.125, 319.875, 31.125),
        (0.125, -64.375, 0.25),
        (31.125, -63.875, -31.125),
        (-128.5, -64.5, 256.75),
        (1.000_000_000_000_000_2, -1.000_000_000_000_000_2, -7.0),
        (1_048_576.0, 256.0, -1_048_576.0),
        (-1_048_576.0, 0.0, 1_048_576.0),
        (1_073_741_824.0, -64.0, -1_073_741_824.0),
        (-1_073_741_824.0, 319.0, 1_073_741_824.0),
        (0.000_000_000_000_000_2, -0.000_000_000_000_000_2, 7.0),
        (-4_096.000_001, 318.0, -0.25),
        (4_095.999_999, -63.0, 0.25),
    ];
    for seed in SEEDS {
        let sampler = ImprovedNoise262::new(seed);
        let mut checksum = 0_u64;
        for (x, y, z) in ORIGINS {
            checksum ^= verify_plane(&sampler, x, y, z);
        }
        assert_ne!(checksum, 0, "degenerate all-zero sample checksum");
    }
}

#[test]
fn every_official_noise_vector_is_the_first_point_of_an_exact_scalar_plane() {
    let mut samplers = BTreeMap::<u64, ImprovedNoise262>::new();
    let mut count = 0_usize;
    let oracle = include_str!("data/improved_noise_26_2_rawbits.tsv");
    for row in oracle
        .lines()
        .filter(|line| !line.starts_with('#') && !line.is_empty())
    {
        let cells: Vec<_> = row.split_whitespace().collect();
        assert_eq!(cells.len(), 5, "malformed oracle input");
        let seed = hex64(cells[0]);
        let x = f64::from_bits(hex64(cells[1]));
        let y = f64::from_bits(hex64(cells[2]));
        let z = f64::from_bits(hex64(cells[3]));
        let expected = hex64(cells[4]);
        let sampler = samplers
            .entry(seed)
            .or_insert_with(|| ImprovedNoise262::new(seed));
        let mut out = [0.0; 256];
        sampler.sample_plane_16x16(x, y, z, &mut out);
        assert_eq!(
            out[0].to_bits(),
            expected,
            "official raw bits: {seed:#018x} {cells:?}"
        );
        for local_z in 0_u8..16 {
            for local_x in 0_u8..16 {
                let scalar = sampler.sample(x + f64::from(local_x), y, z + f64::from(local_z));
                assert_eq!(
                    out[usize::from(local_z) * 16 + usize::from(local_x)].to_bits(),
                    scalar.to_bits()
                );
            }
        }
        count += 1;
    }
    assert_eq!(
        count, 160,
        "complete official noise corpus must be exercised"
    );
    assert_eq!(samplers.len(), 5, "five official seed identities");
}

#[test]
fn plane_reads_are_deterministic_across_workers() {
    let instance = ImprovedNoise262::new(0x9e37_79b9_7f4a_7c15);
    let expected = verify_plane(&instance, -16.125, -63.875, 15.125);
    std::thread::scope(|scope| {
        for _ in 0..4 {
            let sampler = &instance;
            scope.spawn(move || {
                for _ in 0..12 {
                    assert_eq!(verify_plane(sampler, -16.125, -63.875, 15.125), expected);
                }
            });
        }
    });
}
