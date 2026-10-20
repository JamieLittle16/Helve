//! Bit-preserving 26.2 registered noise plane/cell integration qualification.
//!
//! Original JVM stock-worldseed outputs remain the independent oracle; other
//! coherent positions are compared against the ALREADY independently matched
//! scalar Rust constructor path. No production/world/chunk authority is granted.

use helve_world_gen::density_noise_direct_262::{DirectNoiseCellError262, DirectNoiseScale262};
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};

const KEYS: [StockRegisteredNoiseKey262; 3] = [
    StockRegisteredNoiseKey262::Temperature,
    StockRegisteredNoiseKey262::Continentalness,
    StockRegisteredNoiseKey262::Erosion,
];
const SEEDS: [u64; 5] = [0, 1, u64::MAX, 0x8000_0000_0000_0000, 0x9e37_79b9_7f4a_7c15];
const SCALES: [DirectNoiseScale262; 3] = [
    DirectNoiseScale262::Unit,
    DirectNoiseScale262::QuarterHorizontal,
    DirectNoiseScale262::QuarterHorizontalHalfVertical,
];
const ORACLE: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../../vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt"
));

fn hex_bits(value: &str) -> u64 {
    assert_eq!(value.len(), 16);
    u64::from_str_radix(value, 16).expect("pinned official raw IEEE-754 bits")
}

#[test]
fn plane_first_pixel_matches_pinned_stock_jvm_and_entire_plane_matches_scalar() {
    let bits: Vec<&str> = ORACLE.lines().collect();
    assert_eq!(bits.len(), 1440);
    // Two genuine corpus points, one at each opposite edge of the 2^25 wrap.
    let anchors = [
        (0_usize, 33_554_432_i32, -4096_i32, -16_i32),
        (31_usize, -33_554_029_i32, 320_i32, -543_i32),
    ];
    for (seed_index, seed) in SEEDS.iter().enumerate() {
        let set = StockWorldSeededNoiseSet262::new_candidate(*seed);
        for (key_index, key) in KEYS.iter().enumerate() {
            for (scale_index, scale) in SCALES.iter().enumerate() {
                let density = set.density(*key, *scale);
                for &(point, x, y, z) in &anchors {
                    let mut out = [f64::NAN; 256];
                    density
                        .sample_plane_16x16(x, y, z, &mut out)
                        .expect("bounded coherent grid");
                    let row = (((scale_index * SEEDS.len() + seed_index) * KEYS.len() + key_index)
                        * 32)
                        + point;
                    assert_eq!(
                        out[0].to_bits(),
                        hex_bits(bits[row]),
                        "official first-pixel mismatch scale={scale_index} seed={seed_index} key={key_index} point={point}"
                    );
                    for dz in 0_i32..16 {
                        for dx in 0_i32..16 {
                            let expected = density.sample_block(x + dx, y, z + dz).to_bits();
                            let i = usize::try_from(dz * 16 + dx).expect("bounded grid index");
                            assert_eq!(
                                out[i].to_bits(),
                                expected,
                                "coherent plane differs from scalar at seed={seed:016x} key={key_index} scale={scale_index} pixel=({dx},{dz})"
                            );
                        }
                    }
                }
            }
        }
    }
}

#[test]
fn full_3d_cells_are_bit_identical_to_scalar_under_signed_seed_and_scales() {
    let seeds = [0_u64, 0x8000_0000_0000_0000];
    let scales = [
        DirectNoiseScale262::Unit,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    ];
    let (origin_x, origin_y, origin_z) = (-33_554_431_i32, -64_i32, 15_i32);
    for &seed in &seeds {
        let set = StockWorldSeededNoiseSet262::new_candidate(seed);
        for &key in &KEYS {
            for &scale in &scales {
                let density = set.density(key, scale);
                let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
                density
                    .sample_cell_16x16x16(
                        origin_x,
                        origin_y,
                        origin_z,
                        cell.as_mut().try_into().expect("exactly 4096 cells"),
                    )
                    .expect("signed valid block cell");
                for dy in 0_i32..16 {
                    for dz in 0_i32..16 {
                        for dx in 0_i32..16 {
                            let i = usize::try_from((dy * 16 + dz) * 16 + dx)
                                .expect("bounded Y/Z/X cell index");
                            let expected =
                                density.sample_block(origin_x + dx, origin_y + dy, origin_z + dz);
                            assert_eq!(
                                cell[i].to_bits(),
                                expected.to_bits(),
                                "cell/scalar mismatch seed={seed:016x} key={key:?} scale={scale:?} local=({dx},{dy},{dz})"
                            );
                        }
                    }
                }
            }
        }
    }
}

#[test]
fn rejecting_block_overflow_does_not_partially_write_plane_or_cell() {
    let set = StockWorldSeededNoiseSet262::new_candidate(u64::MAX);
    let density = set.density(
        StockRegisteredNoiseKey262::Continentalness,
        DirectNoiseScale262::QuarterHorizontal,
    );
    let sentinel = f64::from_bits(0x7ff8_0bad_cafe_0001);
    let mut plane = [sentinel; 256];
    let mut cell = vec![sentinel; 4096].into_boxed_slice();

    for (x, z) in [(i32::MAX - 14, 0), (0, i32::MAX - 14)] {
        assert_eq!(
            density.sample_plane_16x16(x, 0, z, &mut plane),
            Err(DirectNoiseCellError262::BlockCoordinateOverflow)
        );
    }
    for (x, y, z) in [
        (i32::MAX - 14, -64, 0),
        (0, i32::MAX - 14, 0),
        (0, -64, i32::MAX - 14),
    ] {
        assert_eq!(
            density.sample_cell_16x16x16(
                x,
                y,
                z,
                cell.as_mut().try_into().expect("exactly 4096 cells")
            ),
            Err(DirectNoiseCellError262::BlockCoordinateOverflow)
        );
    }
    assert!(plane.iter().all(|n| n.to_bits() == sentinel.to_bits()));
    assert!(cell.iter().all(|n| n.to_bits() == sentinel.to_bits()));

    // Boundary inclusive remains valid: 15 positive increments reach MAX.
    density
        .sample_plane_16x16(i32::MAX - 15, -64, i32::MAX - 15, &mut plane)
        .expect("inclusive maximum block coordinate is valid");
    assert!(plane.iter().all(|n| n.is_finite()));
}

#[test]
fn stock_world_seeded_noise_set_is_immutable_and_safe_across_worker_threads() {
    let state = StockWorldSeededNoiseSet262::new_candidate(0x9e37_79b9_7f4a_7c15);
    let expected = {
        let mut plane = [0.0_f64; 256];
        state
            .density(
                StockRegisteredNoiseKey262::Erosion,
                DirectNoiseScale262::Unit,
            )
            .sample_plane_16x16(-16, 319, -16, &mut plane)
            .expect("valid plane");
        plane.map(f64::to_bits)
    };
    std::thread::scope(|scope| {
        for _ in 0..4 {
            let state = &state;
            let expected = &expected;
            scope.spawn(move || {
                let mut plane = [0.0_f64; 256];
                for _ in 0..3 {
                    state
                        .density(
                            StockRegisteredNoiseKey262::Erosion,
                            DirectNoiseScale262::Unit,
                        )
                        .sample_plane_16x16(-16, 319, -16, &mut plane)
                        .expect("valid plane");
                    assert_eq!(plane.map(f64::to_bits), *expected);
                }
            });
        }
    });
}
