//! Mixed noise/gradient construction is an internal eager arithmetic
//! *candidate*, not an independently qualified stock DensityFunctions router.
//! Only the raw registered-noise leaf is independently stock-JVM qualified.

use helve_world_gen::density_noise_direct_262::{DirectNoiseCellError262, DirectNoiseScale262};
use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
    StockDensityProgramError262 as ProgramError,
};

const HELD_OUT: &str = include_str!("data/stock_worldseed_heldout_576_rawbits.txt");
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
    (0, 0, 0), (-1, -64, 1), (1, 319, -1),
    (33_554_431, -63, -33_554_432), (-33_554_431, 320, 33_554_431),
    (2_147_483_600, 255, -2_147_483_600),
    (-2_147_483_600, -4096, 2_147_483_600),
    (105, -65, -417), (-1_000_000, 2048, 1_000_000),
    (123_456, -128, -654_321), (-16, 0, 16),
    (15, 256, -15), (33_554_433, 321, -33_554_433),
    (-33_554_433, -31, 33_554_433), (2048, 63, -2048),
    (-2049, 64, 2049),
];

fn gradient() -> DensityPrimitive262 {
    DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0)
        .expect("pinned official 26.2 primitive profile")
}

fn blended<'a>(
    noise: helve_world_gen::registered_noise_state_262::RegisteredNoiseDensityObserved262<'a>,
    gradient: DensityPrimitive262,
    add: bool,
    noise_left: bool,
) -> Program<'a, 3> {
    let (first, second) = if noise_left {
        (Node::RegisteredNoise(noise), Node::Primitive(gradient))
    } else {
        (Node::Primitive(gradient), Node::RegisteredNoise(noise))
    };
    let final_node = if add {
        Node::Add { left: 0, right: 1 }
    } else {
        Node::Multiply { left: 0, right: 1 }
    };
    Program::new([first, second, final_node]).expect("all three nodes used, and DAG valid")
}

#[test]
fn all_576_independently_observed_jvm_bits_survive_single_noise_program() {
    let lines: Vec<_> = HELD_OUT.lines().collect();
    assert_eq!(lines.len(), 576);
    let mut count = 0_usize;
    for (profile_index, profile) in PROFILES.iter().enumerate() {
        for (seed_index, seed) in SEEDS.iter().enumerate() {
            let set = StockWorldSeededNoiseSet262::new_candidate(*seed);
            for (key_index, key) in KEYS.iter().enumerate() {
                let program = Program::new([Node::RegisteredNoise(set.density(*key, *profile))])
                    .expect("single registered leaf is valid");
                for (point_index, &(x, y, z)) in POINTS.iter().enumerate() {
                    let index = (((profile_index * SEEDS.len() + seed_index) * KEYS.len()
                        + key_index) * POINTS.len()) + point_index;
                    assert_eq!(index, count, "source-free JVM row order must stay fixed");
                    let expected = u64::from_str_radix(lines[index], 16).expect("JVM raw bits");
                    assert_eq!(
                        program.sample_block(x, y, z).to_bits(),
                        expected,
                        "registered leaf through program changed raw JVM parity at row={index}"
                    );
                    count += 1;
                }
            }
        }
    }
    assert_eq!(count, 576);
}

#[test]
fn mixed_noise_y_gradient_specialized_planes_are_bit_exact_to_scalar() {
    for &seed in &SEEDS[..2] {
        let set = StockWorldSeededNoiseSet262::new_candidate(seed);
        for &key in &KEYS {
            for &profile in &PROFILES[..2] {
                let noise = set.density(key, profile);
                let primitive = gradient();
                for add in [true, false] {
                    for noise_left in [true, false] {
                        let program = blended(noise, primitive, add, noise_left);
                        let mut output = [f64::NAN; 256];
                        program.sample_plane_16x16(-33_554_431, -31, 14, &mut output)
                            .expect("checked horizontal 16x16 plane");
                        let invariant = primitive.sample_block_y(-31);
                        for dz in 0_i32..16 {
                            for dx in 0_i32..16 {
                                let index = usize::try_from(dz * 16 + dx).expect("plane index");
                                let sample = noise.sample_block(-33_554_431 + dx, -31, 14 + dz);
                                let reference = match (add, noise_left) {
                                    (true, true) => sample + invariant,
                                    (true, false) => invariant + sample,
                                    (false, true) => sample * invariant,
                                    (false, false) => invariant * sample,
                                };
                                assert_eq!(
                                    output[index].to_bits(), reference.to_bits(),
                                    "mixed candidate mismatch seed={seed:016x} key={key:?} scale={profile:?} add={add} noise_left={noise_left} local=({dx},{dz})"
                                );
                                assert_eq!(
                                    output[index].to_bits(),
                                    program.sample_block(-33_554_431 + dx, -31, 14 + dz).to_bits()
                                );
                            }
                        }
                    }
                }
            }
        }
    }
}

#[test]
fn specialized_mixed_3d_cell_preserves_ieee_bits_and_operand_order() {
    let set = StockWorldSeededNoiseSet262::new_candidate(SEEDS[2]);
    let noise = set.density(
        StockRegisteredNoiseKey262::Continentalness,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    let invariant = gradient();
    let origin = (33_554_415_i32, -68_i32, -33_554_433_i32);
    for add in [true, false] {
        for noise_left in [true, false] {
            let program = blended(noise, invariant, add, noise_left);
            let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
            program.sample_cell_16x16x16(
                origin.0, origin.1, origin.2,
                cell.as_mut().try_into().expect("fixed 4096 test cells"),
            ).expect("valid 16-high cell");
            for dy in 0_i32..16 {
                for dz in 0_i32..16 {
                    for dx in 0_i32..16 {
                        let index = usize::try_from((dy * 16 + dz) * 16 + dx)
                            .expect("16^3 index");
                        let point = (origin.0 + dx, origin.1 + dy, origin.2 + dz);
                        assert_eq!(
                            cell[index].to_bits(),
                            program.sample_block(point.0, point.1, point.2).to_bits(),
                            "specialized cell not scalar-bit-exact at index={index}, add={add}, noise_left={noise_left}"
                        );
                    }
                }
            }
        }
    }
}

#[test]
fn nested_multi_noise_graph_reuses_dependencies_and_matches_explicit_reference() {
    let set = StockWorldSeededNoiseSet262::new_candidate(SEEDS[3]);
    let temperature = set.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::Unit,
    );
    let erosion = set.density(
        StockRegisteredNoiseKey262::Erosion,
        DirectNoiseScale262::QuarterHorizontal,
    );
    // Explicit eager arithmetic only. The official mixed composition factory
    // and its correct short-circuit paths are NOT asserted here.
    let program = Program::new([
        Node::RegisteredNoise(temperature),
        Node::Primitive(gradient()),
        Node::Multiply { left: 0, right: 1 },
        Node::RegisteredNoise(erosion),
        Node::Add { left: 2, right: 3 },
    ]).expect("complete backward-indexed expression");
    for &(x, y, z) in &POINTS {
        let expected = (temperature.sample_block(x, y, z)
            * gradient().sample_block_y(y)) + erosion.sample_block(x, y, z);
        let mut scratch = [f64::NAN; 5];
        assert_eq!(program.sample_block(x, y, z).to_bits(), expected.to_bits());
        assert_eq!(
            program.sample_with_scratch(x, y, z, &mut scratch).to_bits(),
            expected.to_bits()
        );
    }
    let mut plane = [f64::NAN; 256];
    program.sample_plane_16x16(-16, -64, 16, &mut plane).expect("valid plane");
    for dz in 0_i32..16 {
        for dx in 0_i32..16 {
            let index = usize::try_from(dz * 16 + dx).expect("plane index");
            assert_eq!(
                plane[index].to_bits(),
                program.sample_block(-16 + dx, -64, 16 + dz).to_bits()
            );
        }
    }
}

#[test]
fn cold_validation_rejects_cycles_dead_nodes_oversized_and_empty_programs() {
    let empty = Program::new([]);
    assert!(matches!(empty, Err(ProgramError::Empty)));

    let invalid = Program::new([
        Node::Primitive(DensityPrimitive262::constant(1.0)),
        Node::Add { left: 0, right: 1 },
    ]);
    assert!(matches!(invalid, Err(ProgramError::InvalidDependency { node: 1, child: 1 })));

    let unused = Program::new([
        Node::Primitive(DensityPrimitive262::constant(1.0)),
        Node::Primitive(DensityPrimitive262::constant(2.0)),
    ]);
    assert!(matches!(unused, Err(ProgramError::UnusedNode { node: 0 })));

    let too_many = Program::new([Node::Primitive(DensityPrimitive262::constant(1.0)); 33]);
    assert!(matches!(too_many, Err(ProgramError::TooManyNodes)));
}

#[test]
fn every_invalid_cell_coordinate_rejects_atomically_before_output_writes() {
    let set = StockWorldSeededNoiseSet262::new_candidate(SEEDS[0]);
    let program = blended(
        set.density(StockRegisteredNoiseKey262::Temperature, DirectNoiseScale262::Unit),
        gradient(), false, true,
    );
    let sentinel = f64::from_bits(0x7ff8_00ab_cdef_1234);
    let mut plane = [sentinel; 256];
    let mut cell = vec![sentinel; 4096].into_boxed_slice();
    assert_eq!(
        program.sample_plane_16x16(i32::MAX - 14, 0, 0, &mut plane),
        Err(DirectNoiseCellError262::BlockCoordinateOverflow)
    );
    for (x, y, z) in [
        (i32::MAX - 14, 0, 0),
        (0, i32::MAX - 14, 0),
        (0, 0, i32::MAX - 14),
    ] {
        assert_eq!(
            program.sample_cell_16x16x16(
                x, y, z,
                cell.as_mut().try_into().expect("fixed test cell")
            ),
            Err(DirectNoiseCellError262::BlockCoordinateOverflow)
        );
    }
    assert!(plane.iter().all(|v| v.to_bits() == sentinel.to_bits()));
    assert!(cell.iter().all(|v| v.to_bits() == sentinel.to_bits()));
}

#[test]
fn signed_zero_constant_multiplication_is_eager_and_not_claimed_as_stock_ap2() {
    let set = StockWorldSeededNoiseSet262::new_candidate(0);
    let noise = set.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::Unit,
    );
    let program = blended(noise, DensityPrimitive262::constant(-0.0), false, true);
    let (x, y, z) = POINTS[0];
    let expected = noise.sample_block(x, y, z) * -0.0;
    assert_eq!(program.sample_block(x, y, z).to_bits(), expected.to_bits());
    let mut plane = [f64::NAN; 256];
    program.sample_plane_16x16(0, 0, 0, &mut plane).expect("valid plane");
    for dz in 0_i32..16 {
        for dx in 0_i32..16 {
            let index = usize::try_from(dz * 16 + dx).expect("plane index");
            assert_eq!(plane[index].to_bits(), program.sample_block(dx, y, dz).to_bits());
        }
    }
}
