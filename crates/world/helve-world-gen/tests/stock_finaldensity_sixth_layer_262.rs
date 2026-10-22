//! Sixth-layer source-observed partial 26.2 stock Java \`finalDensity\`.
//!
//! Four **new** original-JVM child operands per point, six immutable fifth-layer
//! parent output anchors, and the frozen original MIN-root observations.
//! Both separately reviewed \`YClampedGradient\` record parameters are now
//! native Rust primitives; two actual \`MulOrAdd\` operations are native nodes.
//! Original-JVM values are still required for deeper noise and both
//! \`Interpolated\` Marker-wrapped \`RangeChoice\` subgraphs; this is *not*
//! stock \`NoiseChunk\` lifecycle, all-input or production qualification.

use helve_world_gen::density_primitives_262::DensityPrimitive262 as Primitive;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program, StockMulOrAddOp262 as Op,
};

const SIXTH: &str = include_str!("data/stock_finaldensity_sixth_layer_new_128_rawbits.tsv");
const FIFTH: &str = include_str!("data/stock_finaldensity_fifth_layer_new_128_rawbits.tsv");
const THIRD: &str = include_str!("data/stock_finaldensity_third_layer_new_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const LEFT_INNER_ADD: f64 = f64::from_bits(0xbfbe_0000_0000_0000);
const LEFT_OUTER_ADD: f64 = f64::from_bits(0x3fbe_0000_0000_0000);
const OUTSIDE_INNER_MUL: f64 = f64::from_bits(0xbf99_9999_9999_999a);
const OUTSIDE_OUTER_ADD: f64 = f64::from_bits(0xbfb3_3333_3333_3334);
const FIRST_MUL: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const BLOCK_Y: [i32; 32] = [
    -64, 0, 63, 64, 65, 128, 192, 255, 320, -63, -1, 64, 64, 63, 65, 127, 128, 64, 128, 128, 255,
    0, 64, 65, 73, 96, 96, 128, -63, 255, -4096, -65,
];

type Receipt = ([u64; 4], [u64; 6], [u64; 6], u64);

fn words(line: &str) -> Vec<u64> {
    line.split('\t')
        .map(|word| {
            assert_eq!(word.len(), 16);
            u64::from_str_radix(word, 16).expect("exact original-JVM IEEE-754 word")
        })
        .collect()
}

fn samples() -> Vec<Receipt> {
    let sixth: Vec<_> = SIXTH.lines().collect();
    let fifth: Vec<_> = FIFTH.lines().collect();
    let third: Vec<_> = THIRD.lines().collect();
    let root: Vec<_> = ROOT.lines().collect();
    assert_eq!(
        (sixth.len(), fifth.len(), third.len(), root.len()),
        (128, 128, 128, 128)
    );
    sixth
        .iter()
        .zip(&fifth)
        .zip(&third)
        .zip(&root)
        .map(|(((s, f), t), r)| {
            let s = words(s).try_into().expect("four NEW source-owned words");
            let f = words(f).try_into().expect("six immutable fifth-layer words");
            let t = words(t).try_into().expect("six immutable third-layer words");
            let root: [u64; 3] = words(r).try_into().expect("three immutable root words");
            (s, f, t, root[2])
        })
        .collect()
}

fn constant(bits: u64) -> Node<'static> {
    Node::Primitive(Primitive::constant(f64::from_bits(bits)))
}

fn left_gradient() -> Primitive {
    Primitive::y_clamped_gradient(-64, -40, 0.0, 1.0)
        .expect("actual sixth-layer left gradient record")
}

fn outside_gradient() -> Primitive {
    Primitive::y_clamped_gradient(-4064, 4062, -4064.0, 4062.0)
        .expect("independent actual sixth-layer outside Holder gradient record")
}

/// 27 cold-validated nodes. Unknown deeper noise and marker RangeChoice
/// values are separately original-JVM-injected; no sampled hot-path heap.
fn partial_program(sixth: [u64; 4], third: [u64; 6]) -> Program<'static, 27> {
    Program::new(std::array::from_fn(|i| match i {
        0 => Node::Primitive(left_gradient()),
        1 => constant(sixth[0]), // real left inner MulOrAdd's unexpanded child
        2 => Node::CandidateMulOrAdd {
            input: 1,
            argument: LEFT_INNER_ADD,
            operation: Op::Add,
        },
        3 => Node::ExplicitAp2Multiply { left: 0, right: 2 },
        4 => Node::CandidateMulOrAdd {
            input: 3,
            argument: LEFT_OUTER_ADD,
            operation: Op::Add,
        },
        5 => Node::CandidateMulOrAdd {
            input: 4,
            argument: FIRST_MUL,
            operation: Op::Multiply,
        },
        6 => Node::CandidateSqueeze { input: 5 },
        7 => Node::Primitive(outside_gradient()), // nested selector's matching record
        8 => constant(third[2]), // nested original Noise, not yet native
        9 => constant(third[3]), // original Constant(-1), independently frozen
        10 => Node::CandidateRangeChoice {
            selector: 7,
            when_in_range: 8,
            when_out_of_range: 9,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        11 => Node::Primitive(outside_gradient()), // independently reflected real record
        12 => constant(sixth[1]), // actual outside inner Noise output; unseeded here
        13 => Node::CandidateMulOrAdd {
            input: 12,
            argument: OUTSIDE_INNER_MUL,
            operation: Op::Multiply,
        },
        14 => Node::CandidateMulOrAdd {
            input: 13,
            argument: OUTSIDE_OUTER_ADD,
            operation: Op::Add,
        },
        15 => constant(0.0_f64.to_bits()),
        16 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 14,
            when_out_of_range: 15,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        17 => constant(sixth[2]), // first Interpolated Marker child RangeChoice
        18 => Node::CandidateAbs { input: 17 }, // Marker forwards only in SinglePointContext
        19 => constant(sixth[3]), // second Interpolated Marker child RangeChoice
        20 => Node::CandidateAbs { input: 19 },
        21 => Node::ExplicitAp2Max {
            left: 18,
            right: 20,
        },
        22 => Node::CandidateMulOrAdd {
            input: 21,
            argument: 1.5,
            operation: Op::Multiply,
        },
        23 => Node::ExplicitAp2Add {
            left: 16,
            right: 22,
        },
        24 => constant(64.0_f64.to_bits()),
        25 => Node::CandidateRangeChoice {
            selector: 10,
            when_in_range: 24,
            when_out_of_range: 23,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
        26 => Node::ExplicitAp2Min { left: 6, right: 25 },
        _ => unreachable!("fixed 27-node original partial graph"),
    }))
    .expect("fixed finite backward-only source-observed sixth-layer graph")
}

#[test]
fn exact_sixth_layer_two_new_gradients_and_nested_arithmetic() {
    let mut checked = 0;
    for (i, (new, fifth, _, _)) in samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_eq!(
            left_gradient().sample_block_y(y).to_bits(),
            fifth[0],
            "left gradient row {i}"
        );
        assert_eq!(
            outside_gradient().sample_block_y(y).to_bits(),
            fifth[2],
            "outside Holder gradient row {i}"
        );
        let left = Program::new([
            constant(new[0]),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: LEFT_INNER_ADD,
                operation: Op::Add,
            },
        ])
        .expect("actual source-backed inner left addition");
        let outside = Program::new([
            constant(new[1]),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: OUTSIDE_INNER_MUL,
                operation: Op::Multiply,
            },
        ])
        .expect("actual source-backed outside inner multiplication");
        assert_eq!(left.sample_block(0, y, 0).to_bits(), fifth[1], "left ADD {i}");
        assert_eq!(
            outside.sample_block(0, y, 0).to_bits(),
            fifth[3],
            "outside MUL {i}"
        );
        assert_eq!(new[2], fifth[4], "left Interpolated marker forwarding {i}");
        assert_eq!(new[3], fifth[5], "right Interpolated marker forwarding {i}");
        checked += 1;
    }
    assert_eq!(checked, 128);
}

#[test]
fn twenty_seven_node_partial_rust_graph_matches_128_original_stock_root_words() {
    for (i, (new, _, third, root)) in samples().into_iter().enumerate() {
        let graph = partial_program(new, third);
        assert_eq!(
            graph.sample_block(0, BLOCK_Y[i % 32], 0).to_bits(),
            root,
            "original-JVM finalDensity MIN root row {i}"
        );
    }
}
