//! Eighth-layer bounded source-observed partial 26.2 stock Java `finalDensity`.
//!
//! Seven genuinely new original-JVM child operands per point; all previous
//! sixth/third outputs and the original MIN-root fixture remain separate.
//! Actual deeper left `MulOrAdd` and both distinct Marker `RangeChoice`
//! branches are lowered. The two original `HolderHolder` selectors independently
//! agree with the existing Rust gradient on 128 finite samples; this is NOT
//! an all-input alias or stock `NoiseChunk` lifecycle claim.
//!
//! Original seventh 30-node regression is retained; new 32-node candidate stays within the hard bound.
//! Deeper left Ap2 operands are independently source-owned, but the right `MulOrAdd` and actual `Noise` remain JVM-fed.

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
    Primitive::y_clamped_gradient(-64, -40, 0.0, 1.0).expect("actual left-gradient original record")
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
        9 => constant(third[2]),  // original nested Noise output
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
        24 => Node::ExplicitAp2Max {
            left: 20,
            right: 23,
        },
        25 => Node::CandidateMulOrAdd {
            input: 24,
            argument: 1.5,
            operation: Op::Multiply,
        },
        26 => Node::ExplicitAp2Add {
            left: 17,
            right: 25,
        },
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
        assert_eq!(
            deep.sample_block(0, y, 0).to_bits(),
            sixth[0],
            "deep ADD {i}"
        );

        for (input, zero, original) in [(new[2], new[3], sixth[2]), (new[5], new[6], sixth[3])] {
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
            assert_eq!(
                choice.sample_block(0, y, 0).to_bits(),
                original,
                "choice {i}"
            );
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

const EIGHTH: &str = include_str!("data/stock_finaldensity_eighth_layer_new_128_rawbits.tsv");

fn eighth_samples() -> Vec<([u64; 2], Receipt)> {
    let rows: Vec<_> = EIGHTH.lines().collect();
    let prior = samples();
    assert_eq!(rows.len(), 128);
    rows.into_iter()
        .zip(prior)
        .map(|(line, frozen)| {
            let eighth: [u64; 2] = words(line)
                .try_into()
                .expect("two NEW eighth source-owned operand words");
            (eighth, frozen)
        })
        .collect()
}

/// The genuine deeper Ap2 operation is MUL and was independently measured on
/// both source-owned operands, including four positive-zero short circuits.
/// This does not source-qualify the right child `MulOrAdd` or the source law for
/// arbitrary Ap2 instances. Exact two finite operands are still JVM-injected.
fn eighth_partial_program(
    eighth: [u64; 2],
    new: [u64; 7],
    sixth: [u64; 4],
    third: [u64; 6],
) -> Program<'static, 32> {
    Program::new(std::array::from_fn(|i| match i {
        0 => Node::Primitive(left_gradient()),
        1 => constant(eighth[0]), // genuine new left YClampedGradient output (record not yet inspected)
        2 => constant(eighth[1]), // genuine new right MulOrAdd output (source operator still unknown)
        3 => Node::ExplicitAp2Multiply { left: 1, right: 2 },
        4 => Node::CandidateMulOrAdd {
            input: 3,
            argument: LEFT_DEEP_ADD,
            operation: Op::Add,
        },
        5 => Node::CandidateMulOrAdd {
            input: 4,
            argument: LEFT_INNER_ADD,
            operation: Op::Add,
        },
        6 => Node::ExplicitAp2Multiply { left: 0, right: 5 },
        7 => Node::CandidateMulOrAdd {
            input: 6,
            argument: LEFT_OUTER_ADD,
            operation: Op::Add,
        },
        8 => Node::CandidateMulOrAdd {
            input: 7,
            argument: FIRST_MUL,
            operation: Op::Multiply,
        },
        9 => Node::CandidateSqueeze { input: 8 },
        10 | 14 => Node::Primitive(outside_gradient()),
        11 => constant(third[2]), // original nested Noise output
        12 => constant(third[3]), // genuine Constant(-1) output
        13 => Node::CandidateRangeChoice {
            selector: 10,
            when_in_range: 11,
            when_out_of_range: 12,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        15 => constant(sixth[1]), // outside inner original Noise output
        16 => Node::CandidateMulOrAdd {
            input: 15,
            argument: OUTSIDE_INNER_MUL,
            operation: Op::Multiply,
        },
        17 => Node::CandidateMulOrAdd {
            input: 16,
            argument: OUTSIDE_OUTER_ADD,
            operation: Op::Add,
        },
        18 => constant(0.0_f64.to_bits()), // both actual out-of-range Constant(0)
        19 => Node::CandidateRangeChoice {
            selector: 14,
            when_in_range: 17,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        20 => constant(new[2]), // first actual Marker RangeChoice Noise
        21 => Node::CandidateRangeChoice {
            selector: 14,
            when_in_range: 20,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        22 => Node::CandidateAbs { input: 21 },
        23 => constant(new[5]), // second actual Marker RangeChoice Noise
        24 => Node::CandidateRangeChoice {
            selector: 14,
            when_in_range: 23,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        25 => Node::CandidateAbs { input: 24 },
        26 => Node::ExplicitAp2Max {
            left: 22,
            right: 25,
        },
        27 => Node::CandidateMulOrAdd {
            input: 26,
            argument: 1.5,
            operation: Op::Multiply,
        },
        28 => Node::ExplicitAp2Add {
            left: 19,
            right: 27,
        },
        29 => constant(64.0_f64.to_bits()),
        30 => Node::CandidateRangeChoice {
            selector: 13,
            when_in_range: 29,
            when_out_of_range: 28,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
        31 => Node::ExplicitAp2Min { left: 9, right: 30 },
        _ => unreachable!("fixed 32-node original eighth partial graph"),
    }))
    .expect("one cold-validated 32-node backward-only eighth graph")
}

#[test]
fn eighth_ap2_matches_original_positive_zero_and_all_128_deep_outputs() {
    let mut ordinary_ieee_mismatches = 0;
    let mut positive_zero_cases = 0;
    for (i, (eighth, (seventh, _, _, _))) in eighth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        let deep = Program::new([
            constant(eighth[0]),
            constant(eighth[1]),
            Node::ExplicitAp2Multiply { left: 0, right: 1 },
        ])
        .expect("real eighth Ap2 MUL finite original children");
        assert_eq!(
            deep.sample_block(0, y, 0).to_bits(),
            seventh[0],
            "original signed-zero-aware eighth Ap2 MUL row {i}"
        );
        let ordinary = f64::from_bits(eighth[0]) * f64::from_bits(eighth[1]);
        if ordinary.to_bits() != seventh[0] {
            ordinary_ieee_mismatches += 1;
            assert_eq!(
                eighth[0],
                0.0_f64.to_bits(),
                "only +zero can differ row {i}"
            );
            assert_eq!(ordinary.to_bits(), (-0.0_f64).to_bits());
            assert_eq!(seventh[0], 0.0_f64.to_bits());
            positive_zero_cases += 1;
            assert_eq!(y, 320);
        }
    }
    assert_eq!(ordinary_ieee_mismatches, 4);
    assert_eq!(positive_zero_cases, 4);
}

#[test]
fn thirty_two_node_source_observed_eighth_finaldensity_min_matches_stock_original() {
    for (i, (eighth, (new, sixth, third, root))) in eighth_samples().into_iter().enumerate() {
        let graph = eighth_partial_program(eighth, new, sixth, third);
        assert_eq!(
            graph.sample_block(0, BLOCK_Y[i % 32], 0).to_bits(),
            root,
            "original stock eighth 32-node partial finalDensity MIN row {i}"
        );
    }
}


const NINTH: &str = include_str!("data/stock_finaldensity_ninth_layer_new_128_rawbits.tsv");
const NINTH_RIGHT_ADD: f64 = f64::from_bits(0x3fb4_0000_0000_0000);

fn ninth_left_gradient() -> Primitive {
    Primitive::y_clamped_gradient(240, 256, 1.0, 0.0)
        .expect("actual source-owned deep left gradient record")
}

fn ninth_samples() -> Vec<(u64, [u64; 2], Receipt)> {
    let rows: Vec<_> = NINTH.lines().collect();
    assert_eq!(rows.len(), 128, "only 128 new original RangeChoice child bits");
    rows.into_iter()
        .zip(eighth_samples())
        .map(|(line, (eighth, prior))| {
            let inputs: [u64; 1] = words(line).try_into().expect("one NEW ninth child word");
            (inputs[0], eighth, prior)
        })
        .collect()
}

/// The two distinct Java `HolderHolder` targets were each independently
/// reflected as the exact same `YClampedGradient` record with parameters
/// (-4064, 4062, -4064, 4062). Reusing their pure native numerical
/// value is a finite sample-test simplification, NOT Java object identity
/// or all-input holder forwarding qualification. This saves one DAG node,
/// permitting the actual deep ADD with a new child under the 32-node ceiling.
fn ninth_partial_program(
    new_child: u64,
    new: [u64; 7],
    sixth: [u64; 4],
    third: [u64; 6],
) -> Program<'static, 32> {
    Program::new(std::array::from_fn(|i| match i {
        0 => Node::Primitive(left_gradient()),
        1 => Node::Primitive(ninth_left_gradient()), // genuine real Y-gradient record from ninth JVM
        2 => constant(new_child), // only genuine ninth new RangeChoice child output
        3 => Node::CandidateMulOrAdd {
            input: 2,
            argument: NINTH_RIGHT_ADD,
            operation: Op::Add,
        },
        4 => Node::ExplicitAp2Multiply { left: 1, right: 3 },
        5 => Node::CandidateMulOrAdd {
            input: 4,
            argument: LEFT_DEEP_ADD,
            operation: Op::Add,
        },
        6 => Node::CandidateMulOrAdd {
            input: 5,
            argument: LEFT_INNER_ADD,
            operation: Op::Add,
        },
        7 => Node::ExplicitAp2Multiply { left: 0, right: 6 },
        8 => Node::CandidateMulOrAdd {
            input: 7,
            argument: LEFT_OUTER_ADD,
            operation: Op::Add,
        },
        9 => Node::CandidateMulOrAdd {
            input: 8,
            argument: FIRST_MUL,
            operation: Op::Multiply,
        },
        10 => Node::CandidateSqueeze { input: 9 },
        11 => Node::Primitive(outside_gradient()),
        12 => constant(third[2]), // original nested Noise output
        13 => constant(third[3]), // genuine Constant(-1) output
        14 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 12,
            when_out_of_range: 13,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        15 => constant(sixth[1]), // outside inner original Noise output
        16 => Node::CandidateMulOrAdd {
            input: 15,
            argument: OUTSIDE_INNER_MUL,
            operation: Op::Multiply,
        },
        17 => Node::CandidateMulOrAdd {
            input: 16,
            argument: OUTSIDE_OUTER_ADD,
            operation: Op::Add,
        },
        18 => constant(0.0_f64.to_bits()), // both actual out-of-range Constant(0)
        19 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 17,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        20 => constant(new[2]), // first actual Marker RangeChoice Noise
        21 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 20,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        22 => Node::CandidateAbs { input: 21 },
        23 => constant(new[5]), // second actual Marker RangeChoice Noise
        24 => Node::CandidateRangeChoice {
            selector: 11,
            when_in_range: 23,
            when_out_of_range: 18,
            min_inclusive: -60.0,
            max_exclusive: 321.0,
        },
        25 => Node::CandidateAbs { input: 24 },
        26 => Node::ExplicitAp2Max {
            left: 22,
            right: 25,
        },
        27 => Node::CandidateMulOrAdd {
            input: 26,
            argument: 1.5,
            operation: Op::Multiply,
        },
        28 => Node::ExplicitAp2Add {
            left: 19,
            right: 27,
        },
        29 => constant(64.0_f64.to_bits()),
        30 => Node::CandidateRangeChoice {
            selector: 14,
            when_in_range: 29,
            when_out_of_range: 28,
            min_inclusive: -1_000_000.0,
            max_exclusive: 0.0,
        },
        31 => Node::ExplicitAp2Min { left: 10, right: 30 },
        _ => unreachable!("fixed 32-node source-observed ninth partial graph"),
    }))
    .expect("one cold-validated 32-node backward-only ninth graph")
}


#[test]
fn ninth_source_owned_left_gradient_and_actual_right_add_match_128_old_parents() {
    let mut checks = 0;
    for (i, (child, eighth, (seventh, _, _, _))) in ninth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_eq!(
            ninth_left_gradient().sample_block_y(y).to_bits(),
            eighth[0],
            "original ninth gradient Y record at point {i}"
        );
        let right = Program::new([
            constant(child),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: NINTH_RIGHT_ADD,
                operation: Op::Add,
            },
        ])
        .expect("original Java ninth deep right MulOrAdd ADD(+0.078125)");
        assert_eq!(
            right.sample_block(0, y, 0).to_bits(),
            eighth[1],
            "actual original ninth right child ADD at point {i}"
        );
        let deep = Program::new([
            Node::Primitive(ninth_left_gradient()),
            constant(child),
            Node::CandidateMulOrAdd {
                input: 1,
                argument: NINTH_RIGHT_ADD,
                operation: Op::Add,
            },
            Node::ExplicitAp2Multiply { left: 0, right: 2 },
        ])
        .expect("real ninth extended deep Ap2 MUL with positive-zero short circuit");
        assert_eq!(
            deep.sample_block(0, y, 0).to_bits(),
            seventh[0],
            "original ninth deep Ap2 at point {i}"
        );
        checks += 1;
    }
    assert_eq!(checks, 128);
}

#[test]
fn ninth_flat_32node_actual_gradient_add_and_shared_selectors_match_original_min() {
    for (i, (child, _, (new, sixth, third, root))) in ninth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_eq!(new[1], sample_shared_selector(y), "original first selector {i}");
        assert_eq!(new[4], sample_shared_selector(y), "original second selector {i}");
        let graph = ninth_partial_program(child, new, sixth, third);
        assert_eq!(
            graph.sample_block(0, y, 0).to_bits(),
            root,
            "actual original 26.2 ninth bounded 32-node finalDensity MIN point {i}"
        );
    }
}
