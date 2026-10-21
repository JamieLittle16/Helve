//! Typed candidate 26.2 `MulOrAdd` unary constant node, tested against
//! 1,152 *existing independent real stock JVM* mixed-noise/constant outputs.
//!
//! The original stock finalDensity wrapped `MulOrAdd` has not yet had its
//! parameter/operation/child node source-bound. These tests cover the exact
//! constant-delegate output profiles, not arbitrary factory lowering,
//! interpolation/marker state or a production finalDensity evaluator.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
    StockDensityProgramError262 as Error, StockMulOrAddOp262 as Op,
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

fn constant(value: f64) -> Node<'static> {
    Node::Primitive(DensityPrimitive262::constant(value))
}

#[test]
fn fused_candidate_matches_all_1152_original_java_mul_or_add_constant_outputs() {
    let expected: Vec<_> = OFFICIAL
        .lines()
        .map(|s| u64::from_str_radix(s, 16).expect("source-free official f64"))
        .collect();
    assert_eq!(expected.len(), 1920);
    assert_eq!(expected[384], (-0.0_f64).to_bits());
    assert_eq!(expected[576], 0.0_f64.to_bits());
    let mut compared = 0;
    let mut negative_zeros = 0;
    for profile in 4_usize..10 {
        let operation = if matches!(profile, 4 | 5) {
            Op::Add
        } else {
            Op::Multiply
        };
        let argument = if profile < 8 { -0.0 } else { 0.5 };
        for (seed_index, seed) in SEEDS.iter().copied().enumerate() {
            let source = StockWorldSeededNoiseSet262::new_candidate(seed);
            for (key_index, key) in KEYS.iter().copied().enumerate() {
                let noise = source.density(key, DirectNoiseScale262::QuarterHorizontalHalfVertical);
                let program = Program::new([
                    Node::RegisteredNoise(noise),
                    Node::CandidateMulOrAdd {
                        input: 0,
                        argument,
                        operation,
                    },
                ])
                .expect("one seeded leaf plus finite constant delegate");
                for (point_index, (x, y, z)) in POINTS.iter().copied().enumerate() {
                    let row = (((profile * 4 + seed_index) * 3 + key_index) * 16) + point_index;
                    let result = program.sample_block(x, y, z).to_bits();
                    assert_eq!(
                        result, expected[row],
                        "original JVM constant delegate row={row} profile={profile} seed={seed_index} key={key_index} point={point_index}"
                    );
                    negative_zeros += usize::from(result == (-0.0_f64).to_bits());
                    compared += 1;
                }
            }
        }
    }
    assert_eq!(compared, 1152);
    assert!(
        negative_zeros > 0,
        "finite IEEE signed-zero witness must be exercised"
    );
}

#[test]
fn constant_transform_is_reachable_nested_and_skipped_under_lazy_conditions() {
    let sentinel = f64::from_bits(0x7ff8_1234_5678_9abc);
    let program = Program::new([
        constant(0.0),
        constant(-1.0),
        Node::CandidateMulOrAdd {
            input: 1,
            argument: -0.0,
            operation: Op::Multiply,
        },
        Node::ExplicitAp2Multiply { left: 0, right: 2 },
    ])
    .expect("candidate fused constant nested under lazy original Ap2");
    let mut scratch = [sentinel; 4];
    assert_eq!(
        program.sample_with_scratch(0, 0, 0, &mut scratch).to_bits(),
        0
    );
    assert!(
        scratch[1..3]
            .iter()
            .all(|v| v.to_bits() == sentinel.to_bits())
    );

    let program = Program::new([
        constant(-0.5),
        constant(-1.0),
        Node::CandidateMulOrAdd {
            input: 1,
            argument: -0.0,
            operation: Op::Multiply,
        },
        constant(3.0),
        Node::CandidateRangeChoice {
            selector: 0,
            when_in_range: 2,
            when_out_of_range: 3,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
    ])
    .expect("candidate constant nested under source-observed range selection");
    let mut scratch = [sentinel; 5];
    assert_eq!(
        program.sample_with_scratch(0, 0, 0, &mut scratch).to_bits(),
        0.0_f64.to_bits(),
    );
    assert_eq!(scratch[3].to_bits(), sentinel.to_bits());
}

#[test]
fn fused_constant_cold_validation_rejects_nonfinite_and_invalid_dependency() {
    let p = constant(0.5);
    for argument in [f64::INFINITY, f64::NEG_INFINITY, f64::NAN] {
        assert_eq!(
            Program::new([
                p,
                Node::CandidateMulOrAdd {
                    input: 0,
                    argument,
                    operation: Op::Add,
                },
            ])
            .unwrap_err(),
            Error::InvalidMulOrAddArgument { node: 1 }
        );
    }
    for input in [1, 2, usize::MAX] {
        assert_eq!(
            Program::new([
                p,
                Node::CandidateMulOrAdd {
                    input,
                    argument: -0.0,
                    operation: Op::Multiply,
                },
            ])
            .unwrap_err(),
            Error::InvalidDependency {
                node: 1,
                child: input
            }
        );
    }
}

#[test]
fn fused_constant_plane_and_cell_are_scalar_bit_coherent() {
    let source = StockWorldSeededNoiseSet262::new_candidate(SEEDS[1]);
    let noise = source.density(
        StockRegisteredNoiseKey262::Erosion,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    for operation in [Op::Add, Op::Multiply] {
        let program = Program::new([
            Node::RegisteredNoise(noise),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: -0.0,
                operation,
            },
        ])
        .expect("valid candidate");
        let mut plane = [f64::NAN; 256];
        program
            .sample_plane_16x16(-16, 128, -16, &mut plane)
            .expect("bounded plane");
        for dz in 0_i32..16 {
            for dx in 0_i32..16 {
                let i = usize::try_from(dz * 16 + dx).expect("bounded plane index");
                assert_eq!(
                    plane[i].to_bits(),
                    program.sample_block(-16 + dx, 128, -16 + dz).to_bits()
                );
            }
        }
        let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
        program
            .sample_cell_16x16x16(
                -16,
                120,
                -16,
                cell.as_mut()
                    .try_into()
                    .expect("borrowed fixed 4096 output"),
            )
            .expect("bounded cell");
        for dy in 0_i32..16 {
            for dz in 0_i32..16 {
                for dx in 0_i32..16 {
                    let i = usize::try_from((dy * 16 + dz) * 16 + dx).expect("bounded cell");
                    assert_eq!(
                        cell[i].to_bits(),
                        program.sample_block(-16 + dx, 120 + dy, -16 + dz).to_bits()
                    );
                }
            }
        }
    }
}
