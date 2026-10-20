//! Exactly 480 official Java 26.2 DensityFunctions$Noise.compute raw-bit vectors.
//! The oracle directly seeded NormalNoise via RandomSource.create(long), NOT
//! RandomState/NoiseRouter. Production and source VAR/SEM admission remain closed.

use helve_world_gen::density_noise_direct_262::{
    DirectNoiseCellError262, DirectNoiseDensity262, DirectNoiseScale262,
};
use helve_world_gen::perlin_normal_262::NormalNoise262;

const GOLDEN: &str = include_str!("data/density_noise_direct_26_2_rawbits.txt");
const SEEDS: [u64; 5] = [0, 1, u64::MAX, 0x8000_0000_0000_0000, 0x9e37_79b9_7f4a_7c15];
const SCALES: [DirectNoiseScale262; 3] = [
    DirectNoiseScale262::Unit,
    DirectNoiseScale262::QuarterHorizontal,
    DirectNoiseScale262::QuarterHorizontalHalfVertical,
];
const Y: [i32; 32] = [
    -4096, -65, -64, -63, -31, -30, -29, -1, 0, 1, 15, 16, 17, 18, 63, 64, 127, 128, 255, 256, 318,
    319, 320, 321, 1024, -1024, -384, -320, 319, -64, 17, 320,
];

fn position(index: usize) -> (i32, i32, i32) {
    let i = i32::try_from(index).expect("only 32 positions");
    let x = (if i % 2 == 0 { 33_554_432 } else { -33_554_432 }) + 13 * i;
    let z = (if i % 3 == 0 { 17 * i } else { -17 * i }) - 16;
    (x, Y[index], z)
}

#[test]
fn all_480_direct_seeded_official_noise_density_bits_match_exactly() {
    assert!(GOLDEN.contains("e2107c7b874aacda195cab980c55cba2e0110f0974b4efebdf2a34fd480c3bd5"));
    assert!(GOLDEN.contains("bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe"));
    let lines: Vec<_> = GOLDEN
        .lines()
        .filter(|line| !line.starts_with('#'))
        .collect();
    assert_eq!(lines.len(), SCALES.len() * SEEDS.len());
    for (scale_index, scale) in SCALES.iter().enumerate() {
        for (seed_index, seed) in SEEDS.iter().enumerate() {
            let source_line = lines[scale_index * SEEDS.len() + seed_index];
            assert_eq!(source_line.len(), 32 * 16);
            assert!(source_line.bytes().all(|b| b.is_ascii_hexdigit()));
            let noise = NormalNoise262::from_direct_seed_observed_profile(*seed);
            let density = DirectNoiseDensity262::new(&noise, *scale);
            for j in 0..32 {
                let start = j * 16;
                let expected = u64::from_str_radix(&source_line[start..start + 16], 16)
                    .expect("frozen 64-bit hex");
                let (x, y, z) = position(j);
                let actual = density.sample_block(x, y, z).to_bits();
                assert_eq!(
                    actual, expected,
                    "official density profile {scale_index}, seed {seed_index}, index {j}, xyz ({x},{y},{z})"
                );
            }
        }
    }
}

#[test]
fn source_observed_legacy_seed_truncation_preserves_48_bit_collision() {
    let zero = NormalNoise262::from_direct_seed_observed_profile(0);
    let high_bit = NormalNoise262::from_direct_seed_observed_profile(0x8000_0000_0000_0000);
    assert!(zero.state_bits_equal(&high_bit));
    for scale in SCALES {
        assert_eq!(
            DirectNoiseDensity262::new(&zero, scale)
                .sample_block(33_554_432, -4096, -16)
                .to_bits(),
            DirectNoiseDensity262::new(&high_bit, scale)
                .sample_block(33_554_432, -4096, -16)
                .to_bits()
        );
    }
}

#[test]
fn planes_and_cells_reuse_borrowed_noise_and_match_scalar_exact_bits() {
    let noise = NormalNoise262::from_direct_seed_observed_profile(1);
    for scale in SCALES {
        let density = DirectNoiseDensity262::new(&noise, scale);
        let mut plane = [f64::NAN; 256];
        density
            .sample_plane_16x16(33_554_432, 128, -127, &mut plane)
            .unwrap();
        for (z, row) in plane.chunks_exact(16).enumerate() {
            for (x, observed) in row.iter().enumerate() {
                let actual = density.sample_block(
                    33_554_432 + i32::try_from(x).unwrap(),
                    128,
                    -127 + i32::try_from(z).unwrap(),
                );
                assert_eq!(observed.to_bits(), actual.to_bits());
            }
        }

        let mut cell = [f64::NAN; 4096];
        density
            .sample_cell_16x16x16(-33_554_432, -64, 33_554_432, &mut cell)
            .unwrap();
        for (local_y, y_plane) in cell.chunks_exact(256).enumerate() {
            for (local_z, row) in y_plane.chunks_exact(16).enumerate() {
                for (local_x, value) in row.iter().enumerate() {
                    let actual = density.sample_block(
                        -33_554_432 + i32::try_from(local_x).unwrap(),
                        -64 + i32::try_from(local_y).unwrap(),
                        33_554_432 + i32::try_from(local_z).unwrap(),
                    );
                    assert_eq!(value.to_bits(), actual.to_bits());
                }
            }
        }
    }
}

#[test]
fn overflow_in_any_axis_rejected_before_mutating_outputs() {
    let noise = NormalNoise262::from_direct_seed_observed_profile(0);
    let density = DirectNoiseDensity262::new(&noise, DirectNoiseScale262::QuarterHorizontal);
    let mut plane = [f64::NAN; 256];
    assert_eq!(
        density.sample_plane_16x16(i32::MAX - 14, 0, 0, &mut plane),
        Err(DirectNoiseCellError262::BlockCoordinateOverflow)
    );
    assert!(plane.iter().all(|v| v.is_nan()));
    assert_eq!(
        density.sample_plane_16x16(0, 0, i32::MAX - 14, &mut plane),
        Err(DirectNoiseCellError262::BlockCoordinateOverflow)
    );
    assert!(plane.iter().all(|v| v.is_nan()));
    let mut cell = [f64::NAN; 4096];
    for (x, y, z) in [
        (i32::MAX - 14, 0, 0),
        (0, i32::MAX - 14, 0),
        (0, 0, i32::MAX - 14),
    ] {
        assert_eq!(
            density.sample_cell_16x16x16(x, y, z, &mut cell),
            Err(DirectNoiseCellError262::BlockCoordinateOverflow)
        );
        assert!(cell.iter().all(|v| v.is_nan()));
    }
}
