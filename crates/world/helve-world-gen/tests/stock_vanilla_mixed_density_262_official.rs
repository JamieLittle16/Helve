//! 1,920 real official Minecraft 26.2 mixed-stock density observations.
//!
//! The JVM oracle created stock RandomState-backed Noise density leaves and
//! reached the real DensityFunctions.add/mul delegates, not a Rust arithmetic
//! oracle. Outputs are source-free raw IEEE 754 words acquired independently.
//! Production, VAR/SEM, general router and arbitrary delegate admission CLOSED.

use helve_world_gen::density_noise_direct_262::{DirectNoiseCellError262, DirectNoiseScale262};
use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};
use helve_world_gen::stock_vanilla_mixed_density_262::{
    StockVanillaMixedDensity262, StockVanillaMixedOp262 as Op,
    StockVanillaMixedOrder262 as Order,
};

const JVM: &str = include_str!("data/stock_mixed_density_1920_rawbits.txt");
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
const POINTS: [(i32, i32, i32); 16] = [
    (0, 128, 0),
    (1, 127, -1),
    (-1, 129, 1),
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
const PROFILES: [(Op, Order); 10] = [
    (Op::Add, Order::NoiseFirst),
    (Op::Add, Order::PrimitiveFirst),
    (Op::Multiply, Order::NoiseFirst),
    (Op::Multiply, Order::PrimitiveFirst),
    (Op::Add, Order::NoiseFirst),
    (Op::Add, Order::PrimitiveFirst),
    (Op::Multiply, Order::NoiseFirst),
    (Op::Multiply, Order::PrimitiveFirst),
    (Op::Multiply, Order::NoiseFirst),
    (Op::Multiply, Order::PrimitiveFirst),
];

fn primitive(profile: usize) -> DensityPrimitive262 {
    match profile {
        0..=3 => DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0)
            .expect("independently qualified 26.2 gradient"),
        4..=7 => DensityPrimitive262::constant(-0.0),
        8..=9 => DensityPrimitive262::constant(0.5),
        _ => unreachable!("all ten stock profiles have exact parameters"),
    }
}

fn bits() -> Vec<u64> {
    assert_eq!(JVM.len(), 1920 * 17, "independent raw JVM oracle length");
    let lines: Vec<&str> = JVM.lines().collect();
    assert_eq!(lines.len(), 1920);
    assert_eq!(lines[0], "bfda6cdb9e1f1c66");
    assert_eq!(lines[384], "8000000000000000");
    assert_eq!(lines[576], "0000000000000000");
    assert_eq!(lines[1919], "3fae82b27db6a527");
    let mut checksum = 0_u64;
    let mut result = Vec::with_capacity(1920);
    for (index, line) in lines.iter().enumerate() {
        assert_eq!(line.len(), 16, "noncanonical JVM f64 width {index}");
        assert!(
            line.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)),
            "wrong original hex formatting at row {index}"
        );
        let value = u64::from_str_radix(line, 16).expect("IEEE word");
        assert_ne!((value >> 52) & 0x7ff, 0x7ff, "nonfinite official JVM row {index}");
        checksum = checksum.rotate_left(7) ^ value;
        result.push(value);
    }
    assert_eq!(checksum, 0x0000_0000_0100_0000, "mixed JVM oracle changed");
    result
}

#[test]
fn every_official_stock_mixed_noise_add_mul_output_matches_jvm_bit_for_bit() {
    let oracle = bits();
    let mut compared = 0_usize;
    for (profile_index, &(op, order)) in PROFILES.iter().enumerate() {
        for (seed_index, &seed) in SEEDS.iter().enumerate() {
            let source = StockWorldSeededNoiseSet262::new_candidate(seed);
            for (key_index, &key) in KEYS.iter().enumerate() {
                let noise = source.density(key, DirectNoiseScale262::QuarterHorizontalHalfVertical);
                let program = StockVanillaMixedDensity262::new(
                    noise, primitive(profile_index), op, order,
                );
                for (point_index, &(x, y, z)) in POINTS.iter().enumerate() {
                    let index = (((profile_index * SEEDS.len() + seed_index) * KEYS.len()
                        + key_index) * POINTS.len()) + point_index;
                    assert_eq!(index, compared, "stock JVM row order");
                    assert_eq!(
                        program.sample_block(x, y, z).to_bits(), oracle[index],
                        "OFFICIAL mixed JVM disagreement row={index} profile={profile_index} seed={seed:016x} key={key:?} point={point_index} xyz=({x},{y},{z}) expected={:016x}",
                        oracle[index],
                    );
                    compared += 1;
                }
            }
        }
    }
    assert_eq!(compared, 1920);
}

#[test]
fn seven_observed_dynamic_positive_zero_exceptions_are_not_eager_ieee() {
    let oracle = bits();
    let mut disagreements = [0_usize; 10];
    let mut positive_zero_exceptions = 0;
    for (profile_index, &(op, order)) in PROFILES.iter().enumerate() {
        for (seed_index, &seed) in SEEDS.iter().enumerate() {
            let stock = StockWorldSeededNoiseSet262::new_candidate(seed);
            for (key_index, &key) in KEYS.iter().enumerate() {
                let noise = stock.density(key, DirectNoiseScale262::QuarterHorizontalHalfVertical);
                for (point_index, &(x, y, z)) in POINTS.iter().enumerate() {
                    let value = noise.sample_block(x, y, z);
                    let gradient = primitive(profile_index).sample_block_y(y);
                    let (left, right) = if matches!(order, Order::NoiseFirst) {
                        (value, gradient)
                    } else {
                        (gradient, value)
                    };
                    let eager = match op {
                        Op::Add => left + right,
                        Op::Multiply => left * right,
                    };
                    let index = (((profile_index * SEEDS.len() + seed_index) * KEYS.len()
                        + key_index) * POINTS.len()) + point_index;
                    if eager.to_bits() != oracle[index] {
                        disagreements[profile_index] += 1;
                        assert_eq!(profile_index, 3, "only gradient-first dynamic Ap2 differs");
                        assert_eq!(y, 128);
                        assert_eq!(gradient.to_bits(), 0.0_f64.to_bits());
                        assert!(value.is_sign_negative());
                        assert_eq!(eager.to_bits(), (-0.0_f64).to_bits());
                        assert_eq!(oracle[index], 0.0_f64.to_bits());
                        positive_zero_exceptions += 1;
                    }
                }
            }
        }
    }
    assert_eq!(disagreements, [0, 0, 0, 7, 0, 0, 0, 0, 0, 0]);
    assert_eq!(positive_zero_exceptions, 7);
}

#[test]
fn coherent_mixed_planes_and_cells_match_strict_scalar_ieee_bits() {
    let stock = StockWorldSeededNoiseSet262::new_candidate(SEEDS[0]);
    let noise = stock.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    for (index, &(op, order)) in PROFILES.iter().enumerate() {
        let mixed = StockVanillaMixedDensity262::new(noise, primitive(index), op, order);
        let mut plane = [f64::NAN; 256];
        mixed.sample_plane_16x16(-16, 128, 16, &mut plane).expect("valid plane");
        for dz in 0_i32..16 {
            for dx in 0_i32..16 {
                let offset = usize::try_from(dz * 16 + dx).expect("bounded plane");
                assert_eq!(
                    plane[offset].to_bits(),
                    mixed.sample_block(-16 + dx, 128, 16 + dz).to_bits(),
                    "mixed plane mismatch profile={index} at local X/Z {dx}/{dz}"
                );
            }
        }
    }
    for &profile in &[0_usize, 3, 5, 7, 9] {
        let (op, order) = PROFILES[profile];
        let mixed = StockVanillaMixedDensity262::new(noise, primitive(profile), op, order);
        let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
        mixed.sample_cell_16x16x16(
            -16, 121, 16,
            cell.as_mut().try_into().expect("fixed 4096 cell"),
        ).expect("valid 16 high cell");
        for dy in 0_i32..16 {
            for dz in 0_i32..16 {
                for dx in 0_i32..16 {
                    let offset = usize::try_from((dy * 16 + dz) * 16 + dx)
                        .expect("bounded 4096 index");
                    assert_eq!(
                        cell[offset].to_bits(),
                        mixed.sample_block(-16 + dx, 121 + dy, 16 + dz).to_bits(),
                        "mixed cell mismatch profile={profile}, local X/Y/Z {dx}/{dy}/{dz}"
                    );
                }
            }
        }
    }
}

#[test]
fn overflow_fails_before_output_mutation_even_on_zero_shortcut_plane() {
    let stock = StockWorldSeededNoiseSet262::new_candidate(SEEDS[0]);
    let noise = stock.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    let mixed = StockVanillaMixedDensity262::new(
        noise, primitive(3), Op::Multiply, Order::PrimitiveFirst,
    );
    let sentinel = f64::from_bits(0x7ff8_12ab_0000_cdef);
    let mut plane = [sentinel; 256];
    assert_eq!(
        mixed.sample_plane_16x16(i32::MAX - 14, 128, 0, &mut plane),
        Err(DirectNoiseCellError262::BlockCoordinateOverflow)
    );
    let mut cell = vec![sentinel; 4096].into_boxed_slice();
    for &(x, y, z) in &[
        (i32::MAX - 14, 121, 0),
        (0, i32::MAX - 14, 0),
        (0, 121, i32::MAX - 14),
    ] {
        assert_eq!(
            mixed.sample_cell_16x16x16(
                x, y, z, cell.as_mut().try_into().expect("fixed test cell")
            ),
            Err(DirectNoiseCellError262::BlockCoordinateOverflow)
        );
    }
    assert!(plane.iter().all(|v| v.to_bits() == sentinel.to_bits()));
    assert!(cell.iter().all(|v| v.to_bits() == sentinel.to_bits()));
}
