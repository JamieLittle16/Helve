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
    assert_eq!(
        rows.len(),
        128,
        "only 128 new original RangeChoice child bits"
    );
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
// Construct only the source-observed right-hand candidates in cold graph setup.
fn ninth_right_branch_node(i: usize, new: [u64; 7], sixth: [u64; 4]) -> Node<'static> {
    match i {
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
        31 => Node::ExplicitAp2Min {
            left: 10,
            right: 30,
        },
        _ => unreachable!("ninth bounded right-hand graph node"),
    }
}

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
        _ => ninth_right_branch_node(i, new, sixth),
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
        assert_eq!(
            new[1],
            sample_shared_selector(y),
            "original first selector {i}"
        );
        assert_eq!(
            new[4],
            sample_shared_selector(y),
            "original second selector {i}"
        );
        let graph = ninth_partial_program(child, new, sixth, third);
        assert_eq!(
            graph.sample_block(0, y, 0).to_bits(),
            root,
            "actual original 26.2 ninth bounded 32-node finalDensity MIN point {i}"
        );
    }
}

const TENTH: &str = include_str!("data/stock_finaldensity_tenth_layer_new_128_rawbits.tsv");
const TENTH_MIN: f64 = f64::from_bits(0xc12e_8480_0000_0000); // actual -1_000_000.0
const TENTH_MAX: f64 = f64::from_bits(0x3ff9_0000_0000_0000); // actual +1.5625

/// Three NEW actual original Java tenth child observations per seeded
/// coordinate. The original ninth `RangeChoice` output is *not* duplicated
/// here: it remains an independently frozen parent from `ninth_samples`.
fn tenth_samples() -> Vec<([u64; 3], u64, [u64; 2], Receipt)> {
    let rows: Vec<_> = TENTH.lines().collect();
    assert_eq!(rows.len(), 128);
    rows.into_iter()
        .zip(ninth_samples())
        .map(|(line, (ninth, eighth, old))| {
            let children: [u64; 3] = words(line)
                .try_into()
                .expect("three source-owned tenth selector/Ap2 branch words");
            (children, ninth, eighth, old)
        })
        .collect()
}

/// The actually reflected original tenth branch records are Marker,
/// Ap2 and Ap2, in that order; their compute results are *three separate*
/// injected original-JVM values. This four-node cold-validated local stage
/// samples the observed `RangeChoice` independently of its fixed 32-node
/// ninth parent and without growing either graph's HOT scratch capacity.
/// Neither Java Marker lifecycle nor either Ap2 source law is inferred.
fn tenth_choice_stage(children: [u64; 3]) -> Program<'static, 4> {
    Program::new([
        constant(children[0]),
        constant(children[1]),
        constant(children[2]),
        Node::CandidateRangeChoice {
            selector: 0,
            when_in_range: 1,
            when_out_of_range: 2,
            min_inclusive: TENTH_MIN,
            max_exclusive: TENTH_MAX,
        },
    ])
    .expect("source-observed original tenth RangeChoice bounded four-node stage")
}

#[test]
fn tenth_true_selector_and_both_independent_ap2_branches_match_128_ninth_parents() {
    let mut inside = 0;
    let mut outside = 0;
    let mut non_alias_inside = 0;
    for (i, (children, old_ninth, _, _)) in tenth_samples().into_iter().enumerate() {
        let selector = f64::from_bits(children[0]);
        let expected = if (TENTH_MIN..TENTH_MAX).contains(&selector) {
            inside += 1;
            if children[0] != children[1] {
                non_alias_inside += 1;
            }
            children[1]
        } else {
            outside += 1;
            children[2]
        };
        assert_eq!(
            expected, old_ninth,
            "genuine original tenth selected child {i}"
        );
        assert_eq!(
            tenth_choice_stage(children)
                .sample_block(0, BLOCK_Y[i % 32], 0)
                .to_bits(),
            old_ninth,
            "original tenth actual Marker-selector RangeChoice row {i}"
        );
    }
    assert_eq!((inside, outside, non_alias_inside), (68, 60, 1));
}

#[test]
fn tenth_composed_four_plus_thirty_two_nodes_match_stock_original_128_min_root() {
    for (i, (children, old_ninth, _, (new, sixth, third, root))) in
        tenth_samples().into_iter().enumerate()
    {
        let y = BLOCK_Y[i % 32];
        let original_choice = tenth_choice_stage(children).sample_block(0, y, 0);
        assert_eq!(
            original_choice.to_bits(),
            old_ninth,
            "source-free tenth original parent boundary {i}"
        );
        // Stage output is an explicit per-sample IEEE word. Only the
        // test fixture can supply its unresolved original density children.
        let final_density = ninth_partial_program(original_choice.to_bits(), new, sixth, third);
        assert_eq!(
            final_density.sample_block(0, y, 0).to_bits(),
            root,
            "original tenth staged 4+32 stock finalDensity MIN point {i}"
        );
    }
}

const ELEVENTH: &str = include_str!("data/stock_finaldensity_eleventh_layer_new_128_rawbits.tsv");

/// Five genuine new direct original Java child words. The three old tenth
/// `Marker`/`Ap2` parent values come only from the independently frozen tenth
/// source fixture. No previous parent or stock MIN-root bits are recopied.
type EleventhReceipt = ([u64; 5], [u64; 3], u64, [u64; 2], Receipt);

fn eleventh_samples() -> Vec<EleventhReceipt> {
    let rows: Vec<_> = ELEVENTH.lines().collect();
    assert_eq!(rows.len(), 128, "only 640 new eleventh JVM child words");
    rows.into_iter()
        .zip(tenth_samples())
        .map(|(line, (old_tenth, ninth, eighth, receipt))| {
            let child: [u64; 5] = words(line)
                .try_into()
                .expect("five source-observed eleventh original child words");
            (child, old_tenth, ninth, eighth, receipt)
        })
        .collect()
}

/// Bounded independently source-observed `Ap2(MIN)` candidate. Actual Java
/// children are a `Marker` and a `MulOrAdd`; both remain original-JVM fed here.
/// This tests ONLY finite `SinglePointContext` arithmetic against the tenth
/// original parent, not generalized Java operator semantics or `NoiseChunk`.
fn eleventh_min_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        constant(left),
        constant(right),
        Node::ExplicitAp2Min { left: 0, right: 1 },
    ])
    .expect("cold-validated genuine eleventh three-node MIN branch candidate")
}

/// Genuine separately observed out-of-range `Ap2(MAX)` operands: an `Ap2`
/// and a `RangeChoice`. Preserve the rare right-wins row; never flatten
/// the second operand into a constant or guess object identity.
fn eleventh_max_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        constant(left),
        constant(right),
        Node::ExplicitAp2Max { left: 0, right: 1 },
    ])
    .expect("cold-validated genuine eleventh three-node MAX branch candidate")
}

#[test]
fn eleventh_actual_marker_min_and_max_parity_against_old_tenth_ieee_parents() {
    let mut min_left = 0;
    let mut min_right = 0;
    let mut max_left = 0;
    let mut max_right = 0;
    let mut nonconstant_out_right = 0;
    for (i, (new, old, _, _, _)) in eleventh_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        // Original CacheOnce Marker wraps HolderHolder. Identical IEEE samples
        // establish no identity, caching, interpolation or lifecycle law.
        assert_eq!(new[0], old[0], "actual Marker child/parent row {i}");
        let min = eleventh_min_stage(new[1], new[2]).sample_block(0, y, 0);
        let max = eleventh_max_stage(new[3], new[4]).sample_block(0, y, 0);
        assert_eq!(min.to_bits(), old[1], "original MIN Ap2 parent row {i}");
        assert_eq!(max.to_bits(), old[2], "original MAX Ap2 parent row {i}");
        min_left += usize::from(min.to_bits() == new[1]);
        min_right += usize::from(min.to_bits() == new[2] && new[1] != new[2]);
        max_left += usize::from(max.to_bits() == new[3]);
        max_right += usize::from(max.to_bits() == new[4] && new[3] != new[4]);
        nonconstant_out_right += usize::from(new[4] != TENTH_MIN.to_bits());
        if i == 110 {
            assert_eq!(new[3], 0x3fde_51af_db79_aeec);
            assert_eq!(new[4], 0x3fdf_8360_6ba0_8263);
            assert_eq!(max.to_bits(), new[4], "rare original MAX right-wins");
        }
    }
    assert_eq!(
        (
            min_left,
            min_right,
            max_left,
            max_right,
            nonconstant_out_right
        ),
        (68, 60, 127, 1, 3)
    );
}

#[test]
fn eleventh_staged_min_max_then_tenth_choice_then_ninth_root_matches_128_originals() {
    let mut choice_inside = 0;
    let mut choice_outside = 0;
    let mut selector_not_selected_inner = 0;
    for (i, (children, tenth, original_choice, _, (new, sixth, third, root))) in
        eleventh_samples().into_iter().enumerate()
    {
        let y = BLOCK_Y[i % 32];
        assert_eq!(children[0], tenth[0], "original Marker parent boundary {i}");
        let actual_in = eleventh_min_stage(children[1], children[2])
            .sample_block(0, y, 0)
            .to_bits();
        let actual_out = eleventh_max_stage(children[3], children[4])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!([children[0], actual_in, actual_out], tenth);
        let selector = f64::from_bits(children[0]);
        if (TENTH_MIN..TENTH_MAX).contains(&selector) {
            choice_inside += 1;
            selector_not_selected_inner += usize::from(children[0] != actual_in);
        } else {
            choice_outside += 1;
        }
        let choice = tenth_choice_stage([children[0], actual_in, actual_out])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(choice, original_choice, "original ninth old parent row {i}");
        // The preexisting ninth fixed 32-node partial graph and frozen stock
        // root remain untouched. Per-stage scratch: 3, 3, 4, 32 nodes.
        let root_candidate = ninth_partial_program(choice, new, sixth, third);
        assert_eq!(
            root_candidate.sample_block(0, y, 0).to_bits(),
            root,
            "original eleventh staged native candidate stock MIN root row {i}"
        );
    }
    assert_eq!(
        (choice_inside, choice_outside, selector_not_selected_inner),
        (68, 60, 1)
    );
}

const TWELFTH: &str =
    include_str!("data/stock_finaldensity_twelfth_outleft_ap2_children_128_rawbits.tsv");

/// Exactly TWO new original JVM operands for the genuine out-of-range
/// eleventh MAX left Ap2(MIN). Its old numerical parent belongs ONLY to
/// `eleventh_samples()`. Earlier selector, root and parent fixtures remain
/// independently frozen. Test-only finite single-point candidate parity.
type TwelfthReceipt = ([u64; 2], EleventhReceipt);

fn twelfth_samples() -> Vec<TwelfthReceipt> {
    let rows: Vec<_> = TWELFTH.lines().collect();
    assert_eq!(
        rows.len(),
        128,
        "only 256 source-owned twelfth operand words"
    );
    rows.into_iter()
        .zip(eleventh_samples())
        .map(|(line, earlier)| {
            let child: [u64; 2] = words(line)
                .try_into()
                .expect("exactly two genuinely new original twelfth Ap2 child words");
            (child, earlier)
        })
        .collect()
}

/// Native explicit Ap2(MIN) supplied with its actual independently
/// computed stock-JVM Ap2 children. The original source owner observed:
/// Ap2(MIN) with two distinct class-recorded Ap2 child nodes.
/// This does not assert any arbitrary-input Java special-case, short circuit,
/// `NoiseChunk` caching, object identity or production admission.
fn twelfth_outleft_min_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        constant(left),
        constant(right),
        Node::ExplicitAp2Min { left: 0, right: 1 },
    ])
    .expect("source-observed twelfth MIN three-node stage, cold validated")
}

#[test]
fn twelfth_source_owned_outleft_ap2_min_has_three_real_right_wins_and_128_old_parent_matches() {
    let mut left_wins = 0;
    let mut right_wins = 0;
    let mut right_indices = Vec::new();
    for (i, (new, (eleventh, _, _, _, _))) in twelfth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_ne!(
            new[0], new[1],
            "twelfth original MIN tie unqualified at {i}"
        );
        let min = twelfth_outleft_min_stage(new[0], new[1]).sample_block(0, y, 0);
        assert_eq!(
            min.to_bits(),
            eleventh[3],
            "actual original twelfth out-left MIN => immutable eleventh parent row {i}"
        );
        if min.to_bits() == new[0] {
            left_wins += 1;
        } else {
            assert_eq!(min.to_bits(), new[1], "right must be an actual operand");
            right_wins += 1;
            right_indices.push(i);
        }
    }
    assert_eq!((left_wins, right_wins), (125, 3));
    assert_eq!(right_indices, vec![21, 97, 106]);
}

#[test]
fn twelfth_staged_min_then_max_then_tenth_choice_then_ninth_root_matches_128_originals() {
    let mut actual_tenth_inside = 0;
    let mut actual_tenth_outside = 0;
    let mut actual_root_parity = 0;
    for (
        i,
        (twelfth, (eleventh, tenth, old_ninth_choice, _, (ninth_new, sixth, third, stock_root))),
    ) in twelfth_samples().into_iter().enumerate()
    {
        let y = BLOCK_Y[i % 32];
        let native_outleft = twelfth_outleft_min_stage(twelfth[0], twelfth[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_outleft, eleventh[3],
            "new twelfth MIN/eleventh MAX input boundary row {i}"
        );
        let native_in = eleventh_min_stage(eleventh[1], eleventh[2])
            .sample_block(0, y, 0)
            .to_bits();
        let native_out = eleventh_max_stage(native_outleft, eleventh[4])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            [eleventh[0], native_in, native_out],
            tenth,
            "independent stock tenth Marker / both Ap2 parents row {i}"
        );
        assert_eq!(eleventh[0], tenth[0], "Marker finite forwarding row {i}");
        if (TENTH_MIN..TENTH_MAX).contains(&f64::from_bits(eleventh[0])) {
            actual_tenth_inside += 1;
        } else {
            actual_tenth_outside += 1;
        }
        let choice = tenth_choice_stage([eleventh[0], native_in, native_out])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            choice, old_ninth_choice,
            "independent original ninth parent row {i}"
        );
        let actual_root = ninth_partial_program(choice, ninth_new, sixth, third)
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            actual_root, stock_root,
            "genuine original 26.2 finalDensity MIN root after twelfth staged native {i}"
        );
        actual_root_parity += 1;
    }
    assert_eq!((actual_tenth_inside, actual_tenth_outside), (68, 60));
    assert_eq!(actual_root_parity, 128);
    // Each separate cold-validated HOT evaluation uses at most 32 nodes:
    // 3 (twelfth Ap2), 3+3 (eleventh branches), 4 (tenth), 32 (ninth).
    // Never merge these into an unbounded or production-authorized graph.
}

const THIRTEENTH: &str =
    include_str!("data/stock_finaldensity_thirteenth_selected_left_ap2_children_128_rawbits.tsv");

// Exactly two genuinely NEW original JVM words from the actual thirteenth
// Ap2(MIN): left child Ap2, right child HolderHolder. Parent values are
// loaded ONLY from the original prior twelfth new-only fixture.
type ThirteenthReceipt = ([u64; 2], TwelfthReceipt);

fn thirteenth_samples() -> Vec<ThirteenthReceipt> {
    let rows: Vec<_> = THIRTEENTH.lines().collect();
    assert_eq!(rows.len(), 128, "only 256 genuine new thirteenth words");
    rows.into_iter()
        .zip(twelfth_samples())
        .map(|(line, older)| {
            let children: [u64; 2] = words(line)
                .try_into()
                .expect("two new original Java thirteenth Ap2 operands");
            (children, older)
        })
        .collect()
}

// Real source-owner enum MIN and two actual runtime child classes. Genuine
// 128x2 Java operand words are JVM-fed; no all-input law, HolderHolder
// lifecycle or stock NoiseChunk admission is inferred from this sample.
fn thirteenth_left_ap2_min_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        constant(left),
        constant(right),
        Node::ExplicitAp2Min { left: 0, right: 1 },
    ])
    .expect("source-observed original thirteenth three-node MIN stage")
}

#[test]
fn thirteenth_actual_ap2_and_holderholder_min_match_128_immutable_twelfth_parents() {
    let mut left_wins = 0;
    let mut right_wins = 0;
    let mut left_indices = Vec::new();
    for (i, (child, (twelfth, _))) in thirteenth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_ne!(
            child[0], child[1],
            "source-owner thirteenth MIN tie not source-admitted at {i}"
        );
        let reconstructed = thirteenth_left_ap2_min_stage(child[0], child[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            reconstructed, twelfth[0],
            "independent original twelfth left Ap2 parent mismatch row {i}"
        );
        if reconstructed == child[0] {
            left_wins += 1;
            left_indices.push(i);
        } else {
            assert_eq!(reconstructed, child[1]);
            right_wins += 1;
        }
    }
    assert_eq!((left_wins, right_wins), (12, 116));
    assert_eq!(
        left_indices,
        vec![0, 1, 9, 10, 11, 12, 31, 32, 41, 53, 62, 117]
    );
}

#[test]
fn thirteenth_staged_min_through_twelfth_eleventh_tenth_ninth_matches_original_root() {
    let mut root_selected_thirteenth_left = 0;
    let mut root_selected_thirteenth_right = 0;
    let mut root_selected_right_indices = Vec::new();
    let mut parity = 0;
    for (
        i,
        (child, (twelfth, (eleventh, tenth, old_ninth, _, (ninth_new, sixth, third, stock_root)))),
    ) in thirteenth_samples().into_iter().enumerate()
    {
        let y = BLOCK_Y[i % 32];

        // Thirteenth MIN is locally a 3-node pure native candidate.
        let native_left = thirteenth_left_ap2_min_stage(child[0], child[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_left, twelfth[0],
            "new thirteenth to old twelfth parent boundary row {i}"
        );
        // Twelfth MIN must consume the *calculated* thirteenth result,
        // not a new copy of its previous original-JVM parent fixture.
        let native_twelfth = twelfth_outleft_min_stage(native_left, twelfth[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_twelfth, eleventh[3],
            "thirteenth=>twelfth=>old eleventh MAX-left boundary row {i}"
        );

        let in_branch = eleventh_min_stage(eleventh[1], eleventh[2])
            .sample_block(0, y, 0)
            .to_bits();
        let out_branch = eleventh_max_stage(native_twelfth, eleventh[4])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            [eleventh[0], in_branch, out_branch],
            tenth,
            "independent original tenth three old source-observed parents row {i}"
        );
        let choice = tenth_choice_stage([eleventh[0], in_branch, out_branch])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            choice, old_ninth,
            "independent original ninth RangeChoice parent row {i}"
        );
        let root = ninth_partial_program(choice, ninth_new, sixth, third)
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            root, stock_root,
            "original stock finalDensity MIN 128-bit root row {i}"
        );
        parity += 1;

        // Counts derive from the actual independently frozen ROOT operands,
        // not solely from local MIN child selections.
        let root_words: [u64; 3] = words(ROOT.lines().nth(i).expect("128 stock roots"))
            .try_into()
            .expect("two actual original root operands plus final root");
        assert_eq!(root_words[2], stock_root);
        let root_left = f64::from_bits(root_words[0]) < f64::from_bits(root_words[1]);
        let selected_tenth_outside = !(TENTH_MIN..TENTH_MAX).contains(&f64::from_bits(tenth[0]));
        let selected_eleventh_left = f64::from_bits(eleventh[3]) > f64::from_bits(eleventh[4]);
        let selected_twelfth_left = f64::from_bits(twelfth[0]) < f64::from_bits(twelfth[1]);
        if root_left && selected_tenth_outside && selected_eleventh_left && selected_twelfth_left {
            if native_left == child[0] {
                root_selected_thirteenth_left += 1;
            } else {
                assert_eq!(native_left, child[1]);
                root_selected_thirteenth_right += 1;
                root_selected_right_indices.push(i);
            }
        }
    }
    assert_eq!(parity, 128);
    assert_eq!(
        (
            root_selected_thirteenth_left,
            root_selected_thirteenth_right
        ),
        (12, 43)
    );
    assert_eq!(root_selected_right_indices.len(), 43);
    // The HOT scratch never grows beyond the existing ninth 32-node bound.
    // Separate cold-validated stages: 3, 3, 3, 3, 4, 32. No new production
    // graph, scheduler, runtime cache, or source law is admitted.
}

const SIXTEENTH: &str =
    include_str!("data/stock_finaldensity_sixteenth_cacheonce_ap2_children_128_rawbits.tsv");

// Exactly 2 new genuine original JVM numeric operands for the actually observed
// thirteenth RIGHT Holder$Direct -> Marker(CacheOnce) -> Ap2(MIN) ancestry.
// 14th/15th old wrapped parent values are NEVER duplicated as fixtures.
// Existing independent thirteenth RIGHT column remains the old Ap2 parent.
type SixteenthReceipt = ([u64; 2], ThirteenthReceipt);

fn sixteenth_samples() -> Vec<SixteenthReceipt> {
    let source_lines: Vec<_> = SIXTEENTH.lines().collect();
    assert_eq!(
        source_lines.len(),
        128,
        "only 256 genuine new original 16th IEEE operands"
    );
    source_lines
        .into_iter()
        .zip(thirteenth_samples())
        .map(|(line, old)| {
            let new: [u64; 2] = words(line)
                .try_into()
                .expect("exactly two original stock 26.2 16th Ap2 operands");
            (new, old)
        })
        .collect()
}

// 3-node, cold-validated HOT standalone MIN. The actual original source
// type enum is MIN and both child classes are Ap2. Each numeric input is
// independently source-owned, not computed by production seeded worldgen.
fn sixteenth_cacheonce_wrapped_min_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        constant(left),
        constant(right),
        Node::ExplicitAp2Min { left: 0, right: 1 },
    ])
    .expect("genuine sixteenth original MIN, separate cold 3-node stage")
}

#[test]
fn sixteenth_source_owned_ap2_min_matches_frozen_thirteenth_right_parent_128() {
    let mut wins_left = 0;
    let mut wins_right = 0;
    for (i, (children, (thirteenth, _))) in sixteenth_samples().into_iter().enumerate() {
        let y = BLOCK_Y[i % 32];
        assert_ne!(
            children[0], children[1],
            "original sixteenth unreviewed equal MIN operands at row {i}"
        );
        let native = sixteenth_cacheonce_wrapped_min_stage(children[0], children[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native, thirteenth[1],
            "independent thirteenth RIGHT Holder/CacheOnce/Ap2 output row {i}"
        );
        if native == children[0] {
            wins_left += 1;
        } else {
            assert_eq!(native, children[1]);
            wins_right += 1;
        }
    }
    assert_eq!((wins_left, wins_right), (57, 71));
}

#[test]
fn sixteenth_native_ap2_through_thirteenth_twelfth_eleventh_tenth_ninth_matches_128_roots() {
    let mut root_parity = 0;
    let mut sixteen_right_selected = 0;
    let mut sixteen_left_selected = 0;
    for (
        i,
        (
            new_sixteenth,
            (
                thirteenth,
                (
                    twelfth,
                    (eleventh, tenth, old_ninth_choice, _, (ninth_new, sixth, third, stock_root)),
                ),
            ),
        ),
    ) in sixteenth_samples().into_iter().enumerate()
    {
        let y = BLOCK_Y[i % 32];
        let new_right = sixteenth_cacheonce_wrapped_min_stage(new_sixteenth[0], new_sixteenth[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            new_right, thirteenth[1],
            "new 16th -> old 13th RIGHT row {i}"
        );

        // Feed actual newly calculated sixteenth Ap2 parent into the earlier
        // independently source-owned test-only thirteenth MIN stage.
        let native_thirteenth = thirteenth_left_ap2_min_stage(thirteenth[0], new_right)
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_thirteenth, twelfth[0],
            "13th MIN -> old 12th LEFT {i}"
        );

        let native_twelfth = twelfth_outleft_min_stage(native_thirteenth, twelfth[1])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_twelfth, eleventh[3],
            "12th MIN -> old 11th MAX-left {i}"
        );

        let native_inside = eleventh_min_stage(eleventh[1], eleventh[2])
            .sample_block(0, y, 0)
            .to_bits();
        let native_outside = eleventh_max_stage(native_twelfth, eleventh[4])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!([eleventh[0], native_inside, native_outside], tenth);

        let native_choice = tenth_choice_stage([eleventh[0], native_inside, native_outside])
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_choice, old_ninth_choice,
            "tenth choice => ninth parent row {i}"
        );

        let native_root = ninth_partial_program(native_choice, ninth_new, sixth, third)
            .sample_block(0, y, 0)
            .to_bits();
        assert_eq!(
            native_root, stock_root,
            "original JVM root after native 16th stage row {i}"
        );
        root_parity += 1;

        // Actual source-bounded root selection only; no all-input branch law.
        let root_words: [u64; 3] = words(ROOT.lines().nth(i).expect("128 original roots"))
            .try_into()
            .expect("two original root operands + original final result");
        let root_selects_left = f64::from_bits(root_words[0]) < f64::from_bits(root_words[1]);
        let tenth_outside = !(TENTH_MIN..TENTH_MAX).contains(&f64::from_bits(tenth[0]));
        let eleventh_out_left = f64::from_bits(eleventh[3]) > f64::from_bits(eleventh[4]);
        let twelfth_left = f64::from_bits(twelfth[0]) < f64::from_bits(twelfth[1]);
        let thirteenth_right = f64::from_bits(thirteenth[1]) < f64::from_bits(thirteenth[0]);
        if root_selects_left
            && tenth_outside
            && eleventh_out_left
            && twelfth_left
            && thirteenth_right
        {
            if new_right == new_sixteenth[0] {
                sixteen_left_selected += 1;
            } else {
                assert_eq!(new_right, new_sixteenth[1]);
                sixteen_right_selected += 1;
            }
        }
    }
    assert_eq!(root_parity, 128);
    assert_eq!(sixteen_left_selected + sixteen_right_selected, 43);
    // Separate 16th/13th/12th/11th/10th/9th evaluations: 3,3,3,3,4,32.
    // No HOT capacity change, no streaming cache, no NoiseChunk lifecycle law.
}
