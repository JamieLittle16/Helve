//! Fifth-layer stock Java 26.2 finite single-point partial \`finalDensity\`.
//!
//! Six genuinely new source-owned child values; independent fourth, third and
//! root original JVM fixtures remain separate equality anchors. The nested
//! Y-gradient's observed record fields now exercise an existing Rust primitive.
//! The *outside* holder has not had its own bounds inspected and remains an
//! original-JVM leaf. No \`NoiseChunk\`, source-law or production authority.

use helve_world_gen::density_primitives_262::DensityPrimitive262 as Primitive;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program, StockMulOrAddOp262 as Op,
};

const FIFTH: &str = include_str!("data/stock_finaldensity_fifth_layer_new_128_rawbits.tsv");
const FOURTH: &str = include_str!("data/stock_finaldensity_fourth_layer_new_128_rawbits.tsv");
const THIRD: &str = include_str!("data/stock_finaldensity_third_layer_new_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const ADD_LEFT: f64 = f64::from_bits(0x3fbe_0000_0000_0000);
const ADD_OUTSIDE: f64 = f64::from_bits(0xbfb3_3333_3333_3334);
const MUL_FIRST: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const BLOCK_Y: [i32; 32] = [
    -64, 0, 63, 64, 65, 128, 192, 255,
    320, -63, -1, 64, 64, 63, 65, 127,
    128, 64, 128, 128, 255, 0, 64, 65,
    73, 96, 96, 128, -63, 255, -4096, -65,
];

type Receipt = ([u64; 6], [u64; 7], [u64; 6], u64);

fn words(line: &str) -> Vec<u64> {
    line.split('\t')
        .map(|word| {
            assert_eq!(word.len(), 16);
            u64::from_str_radix(word, 16).expect("exact original-JVM IEEE word")
        })
        .collect()
}

fn samples() -> Vec<Receipt> {
    let a: Vec<_> = FIFTH.lines().collect();
    let b: Vec<_> = FOURTH.lines().collect();
    let c: Vec<_> = THIRD.lines().collect();
    let root: Vec<_> = ROOT.lines().collect();
    assert_eq!((a.len(), b.len(), c.len(), root.len()), (128, 128, 128, 128));
    a.iter()
        .zip(&b)
        .zip(&c)
        .zip(&root)
        .map(|(((new, fourth), third), root)| {
            let new = words(new).try_into().expect("six genuine fifth-layer words");
            let fourth = words(fourth).try_into().expect("seven fourth-layer words");
            let third = words(third).try_into().expect("six third-layer words");
            let roots: [u64; 3] = words(root).try_into().expect("three frozen root words");
            (new, fourth, third, roots[2])
        })
        .collect()
}

fn constant(bits: u64) -> Node<'static> {
    Node::Primitive(Primitive::constant(f64::from_bits(bits)))
}

fn nested_gradient() -> Primitive {
    Primitive::y_clamped_gradient(-4064, 4062, -4064.0, 4062.0)
        .expect("genuine original fifth-layer nested gradient record")
}

/// Explicitly observed operator topology; still has stock-JVM input leaves.
/// 25 nodes, backwards-only, no hot-path heap allocations or dynamic lookup.
fn partial_program(new: [u64; 6], third: [u64; 6]) -> Program<'static, 25> {
    Program::new(std::array::from_fn(|i| match i {
        0 => constant(new[0]),  // left Ap2's real Y-gradient, bounds still unknown
        1 => constant(new[1]),  // left Ap2's inner MulOrAdd
        2 => Node::ExplicitAp2Multiply { left: 0, right: 1 },
        3 => Node::CandidateMulOrAdd { input: 2, argument: ADD_LEFT, operation: Op::Add },
        4 => Node::CandidateMulOrAdd { input: 3, argument: MUL_FIRST, operation: Op::Multiply },
        5 => Node::CandidateSqueeze { input: 4 },
        6 => Node::Primitive(nested_gradient()), // actual source-owned nested gradient record
        7 => constant(third[2]), // original nested Noise output, NOT native yet
        8 => constant(third[3]), // original Constant(-1)
        9 => Node::CandidateRangeChoice {
            selector: 6, when_in_range: 7, when_out_of_range: 8,
            min_inclusive: -60.0, max_exclusive: 321.0,
        },
        10 => constant(new[2]), // outside holder gradient, UNKNOWN own endpoints
        11 => constant(new[3]), // outside MulOrAdd's inner MulOrAdd output
        12 => Node::CandidateMulOrAdd { input: 11, argument: ADD_OUTSIDE, operation: Op::Add },
        13 => constant(0.0_f64.to_bits()), // outside Constant(+0)
        14 => Node::CandidateRangeChoice {
            selector: 10, when_in_range: 12, when_out_of_range: 13,
            min_inclusive: -60.0, max_exclusive: 321.0,
        },
        15 => constant(new[4]), // first ABS's inner Marker (unexpanded)
        16 => Node::CandidateAbs { input: 15 },
        17 => constant(new[5]), // second ABS's inner Marker (unexpanded)
        18 => Node::CandidateAbs { input: 17 },
        19 => Node::ExplicitAp2Max { left: 16, right: 18 },
        20 => Node::CandidateMulOrAdd { input: 19, argument: 1.5, operation: Op::Multiply },
        21 => Node::ExplicitAp2Add { left: 14, right: 20 },
        22 => constant(64.0_f64.to_bits()),
        23 => Node::CandidateRangeChoice {
            selector: 9, when_in_range: 22, when_out_of_range: 21,
            min_inclusive: -1_000_000.0, max_exclusive: 0.0,
        },
        24 => Node::ExplicitAp2Min { left: 5, right: 23 },
        _ => unreachable!("statically 25-node original partial density DAG"),
    }))
    .expect("one cold-validated backward-only 25-node fifth-layer graph")
}

#[test]
fn exact_original_fifth_child_operations_even_if_parent_is_lazy() {
    let gradient = nested_gradient();
    let mut gradient_matches = 0;
    let mut abs_matches = 0;
    let mut outside_add_matches = 0;
    let mut left_mul_matches = 0;
    for (i, (new, fourth, _, _)) in samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_eq!(gradient.sample_block_y(y).to_bits(), fourth[1], "gradient {i}");
        gradient_matches += 1;
        assert_eq!(new[2], fourth[2], "outside holder forwarding {i}");
        let left_mul = Program::new([
            constant(new[0]),
            constant(new[1]),
            Node::ExplicitAp2Multiply { left: 0, right: 1 },
        ]).expect("original left Ap2 MUL");
        assert_eq!(left_mul.sample_block(0, y, 0).to_bits(), fourth[0], "MUL {i}");
        left_mul_matches += 1;
        let outside_add = Program::new([
            constant(new[3]),
            Node::CandidateMulOrAdd { input: 0, argument: ADD_OUTSIDE, operation: Op::Add },
        ]).expect("actual outside ADD(-0.075)");
        assert_eq!(outside_add.sample_block(0, y, 0).to_bits(), fourth[3], "ADD {i}");
        outside_add_matches += 1;
        for (input, expected) in [(new[4], fourth[5]), (new[5], fourth[6])] {
            let mapped = Program::new([constant(input), Node::CandidateAbs { input: 0 }])
                .expect("genuine original ABS mapped child");
            assert_eq!(mapped.sample_block(0, y, 0).to_bits(), expected, "ABS {i}");
            abs_matches += 1;
        }
    }
    assert_eq!((gradient_matches, left_mul_matches, outside_add_matches), (128, 128, 128));
    assert_eq!(abs_matches, 256);
}

#[test]
fn twenty_five_node_source_observed_partial_graph_matches_128_frozen_root_words() {
    for (i, (new, _fourth, third, original)) in samples().into_iter().enumerate() {
        let graph = partial_program(new, third);
        assert_eq!(
            graph.sample_block(0, BLOCK_Y[i % 32], 0).to_bits(),
            original,
            "source-observed fifth-layer partial original finalDensity {i}"
        );
    }
}
