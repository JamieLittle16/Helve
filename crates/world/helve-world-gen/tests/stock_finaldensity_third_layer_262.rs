//! New actual 26.2 third-layer original-JVM inputs: 128 finite contexts.
//!
//! Only per-sample `SinglePointContext` Marker delegation is established.
//! No native `NoiseChunk` lifecycle, all-input source law, or production authority.
//! Four unexpanded upstream inputs are JVM-injected into one bounded Rust DAG.

use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program, StockMulOrAddOp262 as Op,
};

const THIRD: &str = include_str!("data/stock_finaldensity_third_layer_new_128_rawbits.tsv");
const SECOND: &str = include_str!("data/stock_finaldensity_second_layer_new_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const FIRST_MULTIPLIER: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const OUTSIDE_MULTIPLIER: f64 = f64::from_bits(0x3ff8_0000_0000_0000);
const NESTED_LOW: f64 = f64::from_bits(0xc04e_0000_0000_0000);
const NESTED_HIGH: f64 = f64::from_bits(0x4074_1000_0000_0000);

fn bits(word: &str) -> u64 {
    assert_eq!(word.len(), 16);
    u64::from_str_radix(word, 16).expect("source-free original-JVM IEEE f64 word")
}

fn constant(word: u64) -> Node<'static> {
    Node::Primitive(DensityPrimitive262::constant(f64::from_bits(word)))
}

fn actual_partially_lowered_graph(
    left_marker: u64,
    selector: u64,
    in_value: u64,
    out_value: u64,
    outside_marker: u64,
    mul_input: u64,
) -> Program<'static, 14> {
    // Actual graph operators, not an assumed vanilla formula. Four
    // unexpanded primitive/spline operands stay JVM-supplied leaves.
    Program::new([
        constant(left_marker), // 0: BlendDensity's wrapped MulOrAdd output
        Node::CandidateMulOrAdd {
            // 1: observed MUL 0.64
            input: 0,
            argument: FIRST_MULTIPLIER,
            operation: Op::Multiply,
        },
        Node::CandidateSqueeze { input: 1 }, // 2
        constant(selector),                  // 3: nested HolderHolder output
        constant(in_value),                  // 4: original Noise result
        constant(out_value),                 // 5: original Constant(-1)
        Node::CandidateRangeChoice {
            // 6: nested [-60,321)
            selector: 3,
            when_in_range: 4,
            when_out_of_range: 5,
            min_inclusive: NESTED_LOW,
            max_exclusive: NESTED_HIGH,
        },
        constant(outside_marker), // 7: outside Interpolated RangeChoice
        constant(mul_input),      // 8: outside MulOrAdd's child Ap2
        Node::CandidateMulOrAdd {
            // 9: observed MUL 1.5
            input: 8,
            argument: OUTSIDE_MULTIPLIER,
            operation: Op::Multiply,
        },
        Node::ExplicitAp2Add { left: 7, right: 9 }, // 10
        constant(64.0_f64.to_bits()),               // 11: outer in-range
        Node::CandidateRangeChoice {
            // 12: outer [-1_000_000,0)
            selector: 6,
            when_in_range: 11,
            when_out_of_range: 10,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
        Node::ExplicitAp2Min { left: 2, right: 12 }, // 13
    ])
    .expect("one immutable 14-node backwards-only actual partial graph")
}

#[test]
fn original_third_layer_nested_range_and_mul_128_bit_exact_plus_root_composition() {
    let third: Vec<_> = THIRD.lines().collect();
    let second: Vec<_> = SECOND.lines().collect();
    let root: Vec<_> = ROOT.lines().collect();
    assert_eq!((third.len(), second.len(), root.len()), (128, 128, 128));
    let mut in_count = 0;
    let mut out_count = 0;
    let mut count = 0;
    for (i, ((tr, sr), rr)) in third.iter().zip(&second).zip(&root).enumerate() {
        let new: Vec<u64> = tr.split('\t').map(bits).collect();
        let prev: Vec<u64> = sr.split('\t').map(bits).collect();
        let original: Vec<u64> = rr.split('\t').map(bits).collect();
        let [
            left_marker,
            selector,
            in_value,
            out_value,
            outside_marker,
            mul_input,
        ] = <[u64; 6]>::try_from(new).expect("six new words");
        let [old_left, old_nested, old_marker, old_mul] =
            <[u64; 4]>::try_from(prev).expect("four frozen second-layer words");
        let [_, _, old_root] = <[u64; 3]>::try_from(original).expect("three frozen root words");
        assert_eq!(left_marker, old_left, "BlendDensity single-point {i}");
        assert_eq!(outside_marker, old_marker, "Interpolated single-point {i}");
        assert_eq!(out_value, (-1.0_f64).to_bits());
        let choice_in = (NESTED_LOW..NESTED_HIGH).contains(&f64::from_bits(selector));
        assert_eq!(
            if choice_in { in_value } else { out_value },
            old_nested,
            "nested {i}"
        );
        in_count += usize::from(choice_in);
        out_count += usize::from(!choice_in);

        let nested = Program::new([
            constant(selector),
            constant(in_value),
            constant(out_value),
            Node::CandidateRangeChoice {
                selector: 0,
                when_in_range: 1,
                when_out_of_range: 2,
                min_inclusive: NESTED_LOW,
                max_exclusive: NESTED_HIGH,
            },
        ])
        .expect("bounded actual nested selector");
        assert_eq!(
            nested.sample_block(0, 64, 0).to_bits(),
            old_nested,
            "choice {i}"
        );

        // Independent MUL check prevents outer lazy branch masking this node.
        let mul = Program::new([
            constant(mul_input),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: OUTSIDE_MULTIPLIER,
                operation: Op::Multiply,
            },
        ])
        .expect("bounded observed outside MUL");
        assert_eq!(
            mul.sample_block(0, 64, 0).to_bits(),
            old_mul,
            "MUL(1.5) {i}"
        );

        let graph = actual_partially_lowered_graph(
            left_marker,
            selector,
            in_value,
            out_value,
            outside_marker,
            mul_input,
        );
        assert_eq!(
            graph.sample_block(0, 64, 0).to_bits(),
            old_root,
            "source-bound partial finalDensity {i}"
        );
        count += 1;
    }
    assert_eq!((count, in_count, out_count), (128, 108, 20));
}
