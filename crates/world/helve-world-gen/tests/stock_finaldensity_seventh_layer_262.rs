//! Seventh-layer source-observed partial 26.2 stock Java `finalDensity`.
//!
//! Seven genuinely new original-JVM child operands per point; all previous
//! sixth/third outputs and the original MIN-root fixture remain separate.
//! Actual deeper left `MulOrAdd` and both distinct Marker `RangeChoice`
//! branches are lowered. The two original HolderHolder selectors independently
//! agree with the existing Rust gradient on 128 finite samples; this is NOT
//! an all-input alias or stock `NoiseChunk` lifecycle claim.
//!
//! 30 cold-validated immutable nodes, backward only and within the <=32 cap.
//! The remaining noise and left Ap2 outputs remain stock-JVM injected.

use helve_world_gen::density_primitives_262::DensityPrimitive262 as Primitive;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program, StockMulOrAddOp262 as Op,
};

const SEVENTH: &str = include_str!("data/stock_finaldensity_seventh_layer_new_128_rawbits.tsv");
const SIXTH: &str = include_str!("data/stock_finaldensity_sixth_layer_new_128_rawbits.tsv");
const THIRD: &str = include_str!("data/stock_finaldensity_third_layer_new_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const LEFT_DEEP_ADD: f64 = f64::from_bits(0xbfb4_0000_0000_0000);
const LEFT_INNER_ADD: f64 = f64::from_bits(0xbfbe_0000_0000_0000);
const LEFT_OUTER_ADD: f64 = f64::from_bits(0x3fbe_0000_0000_0000);
const OUTSIDE_INNER_MUL: f64 = f64::from_bits(0xbf99_9999_9999_999a);
const OUTSIDE_OUTER_ADD: f64 = f64::from_bits(0xbfb3_3333_3333_3334);
const FIRST_MUL: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const BLOCK_Y: [i32; 32] = [
    -64, 0, 63, 64, 65, 128, 192, 255, 320, -63, -1, 64, 64, 63, 65, 127, 128, 64, 128, 128, 255,
    0, 64, 65, 73, 96, 96, 128, -63, 255, -4096, -65,
];

type Receipt = ([u64; 7], [u64; 4], [u64; 6], u64);

fn words(line: &str) -> Vec<u64> {
    line.split('\t')
        .map(|word| {
            assert_eq!(word.len(), 16);
            u64::from_str_radix(word, 16).expect("exact original-JVM IEEE word")
        })
        .collect()
}

fn samples() -> Vec<Receipt> {
    let a: Vec<_> = SEVENTH.lines().collect();
    let b: Vec<_> = SIXTH.lines().collect();
    let c: Vec<_> = THIRD.lines().collect();
    let d: Vec<_> = ROOT.lines().collect();
    assert_eq!((a.len(), b.len(), c.len(), d.len()), (128, 128, 128, 128));
    a.iter()
        .zip(&b)
        .zip(&c)
        .zip(&d)
        .map(|(((new, sixth), third), root)| {
            let new = words(new).try_into().expect("seven NEW child IEEE words");
            let sixth = words(sixth).try_into().expect("four OLD sixth words");
            let third = words(third).try_into().expect("six OLD third words");
            let root: [u64; 3] = words(root).try_into().expect("old MIN root words");
            (new, sixth, third, root[2])
        })
        .collect()
}

fn constant(bits: u64) -> Node<'static> {
    Node::Primitive(Primitive::constant(f64::from_bits(bits)))
}

fn left_gradient() -> Primitive {
    Primitive::y_clamped_gradient(-64, -40, 0.0, 1.0)
        .expect("actual left-gradient original record")
}

fn outside_gradient() -> Primitive {
    Primitive::y_clamped_gradient(-4064, 4062, -4064.0, 4062.0)
        .expect("actual existing two gradient record parameters")
}

/// Actual two original Java `HolderHolder` selectors separately yield this
/// exact gradient's bits on every one of the 128 pinned `SinglePointContext`
/// samples. Sharing it below is a finite-fixture reduction, not Java aliasing.
fn sample_shared_selector(y: i32) -> u64 {
    outside_gradient().sample_block_y(y).to_bits()
}

/// 30 fixed nodes. Only independently unresolved deeper `Ap2` and three
/// stock registry noise outputs are injected as original-JVM IEEE constants.
fn partial_program(new: [u64; 7], sixth: [u64; 4], third: [u64; 6]) -> Program<'static, 30> {
    Program::new(std::array::from_fn(|i| match i {
        0 => Node::Primitive(left_gradient()),
        1 => constant(new[0]), // actual deeper left Ap2 output remains unresolved
        2 => Node::CandidateMulOrAdd {
            input: 1,
            argument: LEFT_DEEP_ADD,
            operation: Op::Add,
        },
        3 => Node::CandidateMulOrAdd {
            input: 2,
            argument: LEFT_INNER_ADD,
            operation: Op::Add,
        },
        4 => Node::ExplicitAp2Multiply { left: 0, right: 3 },
        5 => Node::CandidateMulOrAdd {
            input: 4,
            argument: LEFT_OUTER_ADD,
            operation: Op::Add,
        },
        6 => Node::CandidateMulOrAdd {
            input: 5,
            argument: FIRST_MUL,
            operation: Op::Multiply,
        },
        7 => Node::CandidateSqueeze { input: 6 },
        8 | 12 => Node::Primitive(outside_gradient()),
        9 => constant(third[2]), // original nested Noise output
        10 => constant(third[3]), // genuine Constant(-1) output
        11 => Node::CandidateRangeChoice {
            selector: 8,
            when_in_range: 9,
            when_out_of_range: 10,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        13 => constant(sixth[1]), // outside inner original Noise output
        14 => Node::CandidateMulOrAdd {
            input: 13,
            argument: OUTSIDE_INNER_MUL,
            operation: Op::Multiply,
        },
        15 => Node::CandidateMulOrAdd {
            input: 14,
            argument: OUTSIDE_OUTER_ADD,
            operation: Op::Add,
        },
        16 => constant(0.0_f64.to_bits()), // both actual out-of-range Constant(0)
        17 => Node::CandidateRangeChoice {
            selector: 12,
            when_in_range: 15,
            when_out_of_range: 16,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        18 => constant(new[2]), // first actual Marker RangeChoice Noise
        19 => Node::CandidateRangeChoice {
            selector: 12,
            when_in_range: 18,
            when_out_of_range: 16,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        20 => Node::CandidateAbs { input: 19 },
        21 => constant(new[5]), // second actual Marker RangeChoice Noise
        22 => Node::CandidateRangeChoice {
            selector: 12,
            when_in_range: 21,
            when_out_of_range: 16,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        23 => Node::CandidateAbs { input: 22 },
        24 => Node::ExplicitAp2Max { left: 20, right: 23 },
        25 => Node::CandidateMulOrAdd { input: 24, argument: 1.5, operation: Op::Multiply },
        26 => Node::ExplicitAp2Add { left: 17, right: 25 },
        27 => constant(64.0_f64.to_bits()),
        28 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 27,
            when_out_of_range: 26,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
        29 => Node::ExplicitAp2Min { left: 7, right: 28 },
        _ => unreachable!("fixed 30-node original partial graph"),
    }))
    .expect("one cold-validated 30-node backward-only seventh graph")
}

#[test]
fn exact_original_deep_add_and_independent_two_marker_choices() {
    let mut checks = 0;
    for (i, (new, sixth, _, _)) in samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        let sel = sample_shared_selector(y);
        assert_eq!(new[1], sel, "first genuine HolderHolder selector {i}");
        assert_eq!(new[4], sel, "second genuine HolderHolder selector {i}");
        assert_eq!(new[3], 0.0_f64.to_bits(), "first actual Constant zero {i}");
        assert_eq!(new[6], 0.0_f64.to_bits(), "second actual Constant zero {i}");

        let deep = Program::new([
            constant(new[0]),
            Node::CandidateMulOrAdd {
            input: 0,
            argument: LEFT_DEEP_ADD,
            operation: Op::Add,
        },
        ])
        .expect("real original seventh ADD(-0.078125)");
        assert_eq!(deep.sample_block(0, y, 0).to_bits(), sixth[0], "deep ADD {i}");

        for (input, zero, original) in [
            (new[2], new[3], sixth[2]),
            (new[5], new[6], sixth[3]),
        ] {
            let choice = Program::new([
                Node::Primitive(outside_gradient()),
                constant(input),
                constant(zero),
                Node::CandidateRangeChoice {
                    selector: 0,
                    when_in_range: 1,
                    when_out_of_range: 2,
                    min_inclusive: -60.0,
                    max_exclusive: 321.0,
                },
            ])
            .expect("separately source-observed actual seventh RangeChoice");
            assert_eq!(choice.sample_block(0, y, 0).to_bits(), original, "choice {i}");
        }
        checks += 1;
    }
    assert_eq!(checks, 128);
}

#[test]
fn thirty_node_source_observed_partial_finaldensity_matches_original_128_min_root() {
    for (i, (new, sixth, third, root)) in samples().into_iter().enumerate() {
        let graph = partial_program(new, sixth, third);
        assert_eq!(
            graph.sample_block(0, BLOCK_Y[i % 32], 0).to_bits(),
            root,
            "original-JVM seventh-layer partial finalDensity {i}"
        );
    }
}
