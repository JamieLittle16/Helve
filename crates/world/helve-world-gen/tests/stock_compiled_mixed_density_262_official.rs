//! Compiled borrowed density program executes stock 26.2 mixed delegates.
//!
//! The 1,920 original JVM observations were captured independently of Rust.
//! Each test evaluates real seeded Rust noise + Y primitive + observed
//! `Ap2`/`MulOrAdd` semantics; it never merely replays fixture output.
//! Arbitrary graph composition, marker/cache and full finalDensity are OPEN.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
};
use helve_world_gen::stock_vanilla_mixed_density_262::{
    StockVanillaMixedDensity262, StockVanillaMixedOp262 as Op, StockVanillaMixedOrder262 as Order,
};

const OFFICIAL: &str = include_str!("data/stock_mixed_density_1920_rawbits.txt");
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
            .expect("original stock Y-gradient"),
        4..=7 => DensityPrimitive262::constant(-0.0),
        8..=9 => DensityPrimitive262::constant(0.5),
        _ => unreachable!("ten official stock factory profiles"),
    }
}

#[test]
fn compiled_mixed_leaf_computes_all_1920_official_java_words() {
    let words: Vec<_> = OFFICIAL
        .lines()
        .map(|v| u64::from_str_radix(v, 16).expect("frozen official 26.2 raw word"))
        .collect();
    assert_eq!(words.len(), 1920);
    assert_eq!(words[0], 0xbfda_6cdb_9e1f_1c66);
    assert_eq!(words[384], (-0.0_f64).to_bits());
    assert_eq!(words[576], 0.0_f64.to_bits());
    let mut checked = 0_usize;
    for (profile, &(op, order)) in PROFILES.iter().enumerate() {
        for (seed_idx, &seed) in SEEDS.iter().enumerate() {
            let world = StockWorldSeededNoiseSet262::new_candidate(seed);
            for (key_idx, &key) in KEYS.iter().enumerate() {
                let noise = world.density(key, DirectNoiseScale262::QuarterHorizontalHalfVertical);
                let leaf = StockVanillaMixedDensity262::new(noise, primitive(profile), op, order);
                let program = Program::new([Node::ObservedMixed(leaf)])
                    .expect("one prepared observed-delegate leaf");
                for (point_idx, &(x, y, z)) in POINTS.iter().enumerate() {
                    let row = (((profile * 4 + seed_idx) * 3 + key_idx) * 16) + point_idx;
                    assert_eq!(row, checked);
                    let actual = program.sample_block(x, y, z).to_bits();
                    assert_eq!(
                        actual, words[row],
                        "compiled original 26.2 factory mismatch at profile {profile}, seed {seed_idx}, key {key_idx}, point {point_idx}"
                    );
                    checked += 1;
                }
            }
        }
    }
    assert_eq!(checked, 1920);
}

#[test]
fn compiled_leaf_preserves_positive_zero_ap2_and_signed_zero_mul_or_add() {
    let world = StockWorldSeededNoiseSet262::new_candidate(SEEDS[0]);
    let noise = world.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    let dynamic =
        StockVanillaMixedDensity262::new(noise, primitive(3), Op::Multiply, Order::PrimitiveFirst);
    let constant =
        StockVanillaMixedDensity262::new(noise, primitive(7), Op::Multiply, Order::PrimitiveFirst);
    let dynamic_program = Program::new([Node::ObservedMixed(dynamic)]).expect("observed Ap2");
    let constant_program =
        Program::new([Node::ObservedMixed(constant)]).expect("observed MulOrAdd");
    // The source-verified one-node wrapper must not flatten both
    // original stock delegates into an eager multiply.
    for &(x, y, z) in &POINTS {
        assert_eq!(
            dynamic_program.sample_block(x, y, z).to_bits(),
            dynamic.sample_block(x, y, z).to_bits()
        );
        assert_eq!(
            constant_program.sample_block(x, y, z).to_bits(),
            constant.sample_block(x, y, z).to_bits()
        );
    }
    assert_eq!(dynamic_program.sample_block(0, 128, 0).to_bits(), 0);
}

#[test]
fn compiled_single_mixed_leaf_plane_and_cell_keep_exact_scalar_order() {
    let world = StockWorldSeededNoiseSet262::new_candidate(SEEDS[1]);
    let noise = world.density(
        StockRegisteredNoiseKey262::Erosion,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    for &profile in &[0_usize, 3, 5, 7, 9] {
        let (op, order) = PROFILES[profile];
        let leaf = StockVanillaMixedDensity262::new(noise, primitive(profile), op, order);
        let program = Program::new([Node::ObservedMixed(leaf)]).expect("one mixed leaf");
        let mut plane = [f64::NAN; 256];
        program
            .sample_plane_16x16(-16, 128, -16, &mut plane)
            .expect("bounded plane");
        for dz in 0_i32..16 {
            for dx in 0_i32..16 {
                let row = usize::try_from(dz * 16 + dx).expect("bounded XZ row");
                assert_eq!(
                    plane[row].to_bits(),
                    program.sample_block(-16 + dx, 128, -16 + dz).to_bits()
                );
            }
        }
        // Test-owned heap storage avoids a 32 KiB stack array; the
        // compiled evaluator still receives an ordinary borrowed buffer.
        let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
        program
            .sample_cell_16x16x16(
                -16,
                121,
                -16,
                cell.as_mut()
                    .try_into()
                    .expect("fixed 4096-value test cell"),
            )
            .expect("bounded volume");
        for dy in 0_i32..16 {
            for dz in 0_i32..16 {
                for dx in 0_i32..16 {
                    let row = usize::try_from((dy * 16 + dz) * 16 + dx).expect("bounded voxel");
                    assert_eq!(
                        cell[row].to_bits(),
                        program.sample_block(-16 + dx, 121 + dy, -16 + dz).to_bits()
                    );
                }
            }
        }
    }
}

#[test]
fn compiled_explicit_eager_outer_arithmetic_reuses_observed_mixed_subtree() {
    let world = StockWorldSeededNoiseSet262::new_candidate(SEEDS[2]);
    let noise = world.density(
        StockRegisteredNoiseKey262::Continentalness,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    let mixed =
        StockVanillaMixedDensity262::new(noise, primitive(3), Op::Multiply, Order::PrimitiveFirst);
    let extra = DensityPrimitive262::constant(-0.0);
    let program = Program::new([
        Node::ObservedMixed(mixed),
        Node::Primitive(extra),
        Node::Add { left: 0, right: 1 },
    ])
    .expect("bounded explicit expression");
    for &(x, y, z) in &POINTS {
        let expected = mixed.sample_block(x, y, z) + extra.sample_block_y(y);
        assert_eq!(program.sample_block(x, y, z).to_bits(), expected.to_bits());
    }
    // This multi-node arithmetic is explicit/eager, not claimed as a
    // source-reviewed general Minecraft 26.2 DensityFunctions factory graph.
}
