//! Fourth-layer stock 26.2 original-JVM partial finalDensity graph (128 points).
//!
//! All seven new child leaves come from the source-free fourth-layer capture,
//! never generated from a guessed vanilla formula. The independently frozen
//! third-layer and MIN root fixtures are *outputs* that must be reproduced.
//! No source law, `NoiseChunk` interpolation, or production admission.

use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program, StockMulOrAddOp262 as Op,
};

const FOURTH: &str = include_str!("data/stock_finaldensity_fourth_layer_new_128_rawbits.tsv");
const THIRD: &str = include_str!("data/stock_finaldensity_third_layer_new_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");

const LEFT_ADD: f64 = f64::from_bits(0x3fbe_0000_0000_0000);
const MUL_FIRST: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const MUL_OUTSIDE: f64 = 1.5;
const LOW: f64 = -60.0;
const HIGH: f64 = 321.0;
const OUTER_LOW: f64 = -1_000_000.0;
const OUTER_HIGH: f64 = 0.0;

type FixtureRow = ([u64; 7], [u64; 6], u64);

fn words(line: &str) -> Vec<u64> {
    line.split('\t')
        .map(|v| {
            assert_eq!(v.len(), 16);
            u64::from_str_radix(v, 16).expect("original binary64 word")
        })
        .collect()
}

fn all_rows() -> Vec<FixtureRow> {
    let first: Vec<_> = FOURTH.lines().collect();
    let previous: Vec<_> = THIRD.lines().collect();
    let roots: Vec<_> = ROOT.lines().collect();
    assert_eq!((first.len(), previous.len(), roots.len()), (128, 128, 128));
    first
        .iter()
        .zip(previous)
        .zip(roots)
        .map(|((a, b), root)| {
            let f = words(a).try_into().expect("seven new inputs");
            let t = words(b)
                .try_into()
                .expect("six frozen third-layer operands");
            let original: [u64; 3] = words(root).try_into().expect("three root words");
            (f, t, original[2])
        })
        .collect()
}

fn constant(word: u64) -> Node<'static> {
    Node::Primitive(DensityPrimitive262::constant(f64::from_bits(word)))
}

/// Reconstructed exact *observed* operator topology, no graph compiler.
fn partial_graph(f: [u64; 7], t: [u64; 6]) -> Program<'static, 20> {
    let [
        left_ap2,
        inner_y,
        outside_y,
        outside_in,
        outside_out,
        max_left,
        max_right,
    ] = f;
    Program::new([
        constant(left_ap2), // 0: unexpanded left Ap2
        Node::CandidateMulOrAdd {
            input: 0,
            argument: LEFT_ADD,
            operation: Op::Add,
        }, // 1: actual BlendDensity wrapped ADD 0.1171875
        Node::CandidateMulOrAdd {
            input: 1,
            argument: MUL_FIRST,
            operation: Op::Multiply,
        }, // 2: observed MUL 0.64
        Node::CandidateSqueeze { input: 2 }, // 3: observed SQUEEZE
        constant(inner_y),  // 4: nested YClampedGradient, JVM-injected
        constant(t[2]),     // 5: earlier source-observed nested Noise
        constant(t[3]),     // 6: earlier Constant(-1)
        Node::CandidateRangeChoice {
            selector: 4,
            when_in_range: 5,
            when_out_of_range: 6,
            min_inclusive: LOW,
            max_exclusive: HIGH,
        }, // 7
        constant(outside_y), // 8: separate outside HolderHolder (no shared identity claim)
        constant(outside_in), // 9: not yet descended MulOrAdd
        constant(outside_out), // 10: actual Constant(+0)
        Node::CandidateRangeChoice {
            selector: 8,
            when_in_range: 9,
            when_out_of_range: 10,
            min_inclusive: LOW,
            max_exclusive: HIGH,
        }, // 11
        constant(max_left), // 12: first Mapped child
        constant(max_right), // 13: second Mapped child
        Node::ExplicitAp2Max {
            left: 12,
            right: 13,
        }, // 14: original right Ap2 MAX
        Node::CandidateMulOrAdd {
            input: 14,
            argument: MUL_OUTSIDE,
            operation: Op::Multiply,
        }, // 15: observed MUL 1.5
        Node::ExplicitAp2Add {
            left: 11,
            right: 15,
        }, // 16: observed outside ADD
        constant(64.0_f64.to_bits()), // 17: outer in-range
        Node::CandidateRangeChoice {
            selector: 7,
            when_in_range: 17,
            when_out_of_range: 16,
            min_inclusive: OUTER_LOW,
            max_exclusive: OUTER_HIGH,
        }, // 18
        Node::ExplicitAp2Min { left: 3, right: 18 }, // 19: actual original finalDensity root
    ])
    .expect("one bounded, cold-validated 20-node original partial graph")
}

#[test]
fn actual_fourth_layer_independently_checks_all_parent_operands() {
    let mut branches = [0_usize; 2];
    let mut max_winners = [0_usize; 3];
    for (index, (f, t, _)) in all_rows().into_iter().enumerate() {
        let [ap2, y, selector, inside, outside, left, right] = f;
        let add = Program::new([
            constant(ap2),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: LEFT_ADD,
                operation: Op::Add,
            },
        ])
        .expect("actual left additive operator");
        assert_eq!(add.sample_block(0, 0, 0).to_bits(), t[0], "ADD {index}");
        assert_eq!(y, t[1], "nested holder {index}");
        assert_eq!(outside, 0_f64.to_bits(), "outside constant {index}");
        let range = Program::new([
            constant(selector),
            constant(inside),
            constant(outside),
            Node::CandidateRangeChoice {
                selector: 0,
                when_in_range: 1,
                when_out_of_range: 2,
                min_inclusive: LOW,
                max_exclusive: HIGH,
            },
        ])
        .expect("actual outside selector");
        assert_eq!(range.sample_block(0, 0, 0).to_bits(), t[4], "range {index}");
        branches[usize::from(!(LOW..HIGH).contains(&f64::from_bits(selector)))] += 1;
        let max = Program::new([
            constant(left),
            constant(right),
            Node::ExplicitAp2Max { left: 0, right: 1 },
        ])
        .expect("actual MAX operands");
        assert_eq!(max.sample_block(0, 0, 0).to_bits(), t[5], "MAX {index}");
        let lhs = f64::from_bits(left);
        let rhs = f64::from_bits(right);
        max_winners[if lhs > rhs {
            0
        } else if lhs < rhs {
            1
        } else {
            2
        }] += 1;
    }
    assert_eq!(branches, [108, 20]);
    assert_eq!(max_winners, [44, 64, 20]);
}

#[test]
fn actual_fourth_layer_20_node_partial_finaldensity_matches_frozen_original_root() {
    for (index, (f, t, expected)) in all_rows().into_iter().enumerate() {
        let graph = partial_graph(f, t);
        assert_eq!(
            graph.sample_block(0, 0, 0).to_bits(),
            expected,
            "actual original fourth-layer lowerings at {index}"
        );
    }
}
