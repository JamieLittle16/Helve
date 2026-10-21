//! Genuine second-layer 26.2 finalDensity input words from the original JVM.
//!
//! These tests compute MulOrAdd MUL(0.64), the outer Ap2 ADD, SQUEEZE,
//! RangeChoice, and final MIN *inside one fixed 10-node immutable Rust DAG*.
//! The four remaining child inputs are original-JVM-provided leaves, not
//! independently computed world-seeded noise/spline/Marker graph values.
//! Interpolated Marker identity is valid only for the observed
//! SinglePointContext. This is NOT native end-to-end finalDensity or
//! original NoiseChunk lifecycle/source-law admission.

use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
    StockDensityProgramError262 as Error, StockMulOrAddOp262 as Op,
};

const SECOND: &str = include_str!("data/stock_finaldensity_second_layer_new_128_rawbits.tsv");
const INNER: &str = include_str!("data/stock_finaldensity_inner_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const ARGUMENT: f64 = f64::from_bits(0x3fe4_7ae1_47ae_147b);
const MIN: f64 = -1_000_000.0;

fn bits(hex: &str) -> u64 {
    assert_eq!(hex.len(), 16);
    u64::from_str_radix(hex, 16).expect("source-free JVM f64 word")
}

fn constant(bits: u64) -> Node<'static> {
    Node::Primitive(DensityPrimitive262::constant(f64::from_bits(bits)))
}

#[test]
fn actual_128_second_layer_inputs_reconstruct_both_operators_and_nested_min() {
    let second: Vec<_> = SECOND.lines().collect();
    let inner: Vec<_> = INNER.lines().collect();
    let root: Vec<_> = ROOT.lines().collect();
    assert_eq!(second.len(), 128);
    assert_eq!(inner.len(), 128);
    assert_eq!(root.len(), 128);

    let mut mul_matches = 0;
    let mut add_matches = 0;
    let mut marker_matches = 0;
    let mut root_matches = 0;
    let mut in_range = 0;
    let mut right_wins = 0;
    for (i, ((new_row, inner_row), root_row)) in second
        .iter()
        .zip(&inner)
        .zip(&root)
        .enumerate()
    {
        let new: Vec<_> = new_row.split('\t').map(bits).collect();
        let old: Vec<_> = inner_row.split('\t').map(bits).collect();
        let first: Vec<_> = root_row.split('\t').map(bits).collect();
        assert_eq!(new.len(), 4);
        assert_eq!(old.len(), 7);
        assert_eq!(first.len(), 3);
        let [mul_input, selector_input, out_left, out_right] =
            <[u64; 4]>::try_from(new).expect("four real second-layer operands");
        let [marker, wrapped, mapped, selector, _inside, outside, holder] =
            <[u64; 7]>::try_from(old).expect("seven frozen inner words");
        let [old_mapped, old_holder, old_root] =
            <[u64; 3]>::try_from(first).expect("three frozen root words");

        // Exact independent observations: SinglePointContext Interpolated
        // Markers delegate to their underlying input (not true in general
        // for NoiseChunk interpolation/cache timeline).
        assert_eq!(selector_input, selector, "selector Marker input {i}");
        assert_eq!(marker, wrapped, "left Marker delegation {i}");
        marker_matches += 1;

        // Force both previously unseen operators to be computed and
        // compared independently of the selected RangeChoice/MIN branch.
        let mul = Program::new([
            constant(mul_input),
            Node::CandidateMulOrAdd {
                input: 0,
                argument: ARGUMENT,
                operation: Op::Multiply,
            },
        ])
        .expect("typed actual configured 26.2 MulOrAdd candidate");
        assert_eq!(mul.sample_block(0, 64, 0).to_bits(), wrapped, "MUL {i}");
        mul_matches += 1;

        let add = Program::new([
            constant(out_left),
            constant(out_right),
            Node::ExplicitAp2Add { left: 0, right: 1 },
        ])
        .expect("typed actual outside Ap2 ADD candidate");
        assert_eq!(add.sample_block(0, 64, 0).to_bits(), outside, "ADD {i}");
        add_matches += 1;

        let graph = Program::new([
            constant(mul_input), // 0: upstream Marker result, not its graph
            Node::CandidateMulOrAdd { // 1: observed MUL operation/argument
                input: 0,
                argument: ARGUMENT,
                operation: Op::Multiply,
            },
            Node::CandidateSqueeze { input: 1 }, // 2: Mapped
            constant(selector_input), // 3: Interpolated Marker result
            constant(out_left),       // 4: outside Ap2 Marker result
            constant(out_right),      // 5: outside Ap2 MulOrAdd result
            Node::ExplicitAp2Add { left: 4, right: 5 }, // 6
            constant(64.0_f64.to_bits()), // 7: in-range Constant
            Node::CandidateRangeChoice { // 8: HolderHolder target
                selector: 3,
                when_in_range: 7,
                when_out_of_range: 6,
                min_inclusive: MIN,
                max_exclusive: 0.0,
            },
            Node::ExplicitAp2Min { left: 2, right: 8 }, // 9
        ])
        .expect("one cold-validated 10-node, backwards-only source-bounded DAG");

        let mut scratch = [f64::NAN; 10];
        assert_eq!(
            graph.sample_with_scratch(0, 64, 0, &mut scratch).to_bits(),
            old_root,
            "actual partially lowered source-bound finalDensity {i}"
        );
        assert_eq!(mapped, old_mapped, "frozen root left {i}");
        assert_eq!(holder, old_holder, "frozen root right {i}");
        assert_eq!(ARGUMENT.to_bits(), 0x3fe4_7ae1_47ae_147b);
        if (MIN..0.0).contains(&f64::from_bits(selector_input)) {
            in_range += 1;
        }
        if f64::from_bits(old_holder) < f64::from_bits(old_mapped) {
            right_wins += 1;
        }
        root_matches += 1;
    }
    assert_eq!((mul_matches, add_matches, marker_matches, root_matches), (128, 128, 128, 128));
    assert_eq!(in_range, 47);
    assert_eq!(right_wins, 4);
}

#[test]
fn explicit_ap2_add_is_cold_validated_and_branch_lazy() {
    let one = constant(1.0_f64.to_bits());
    for child in [2, 3, usize::MAX] {
        assert_eq!(
            Program::new([one, one, Node::ExplicitAp2Add { left: 0, right: child }])
                .unwrap_err(),
            Error::InvalidDependency { node: 2, child },
        );
    }
    let program = Program::new([
        constant(0.5_f64.to_bits()),
        constant(64.0_f64.to_bits()),
        constant((-0.0_f64).to_bits()),
        constant(3.0_f64.to_bits()),
        Node::ExplicitAp2Add { left: 2, right: 3 },
        Node::CandidateRangeChoice {
            selector: 0,
            when_in_range: 1,
            when_out_of_range: 4,
            min_inclusive: MIN,
            max_exclusive: 0.0,
        },
    ])
    .expect("conditional prevents evaluation of outside ADD");
    let sentinel = f64::from_bits(0x7ff8_1234_5678_9abc);
    let mut scratch = [sentinel; 6];
    assert_eq!(
        program.sample_with_scratch(0, 0, 0, &mut scratch).to_bits(),
        3.0_f64.to_bits(),
    );
    assert_eq!(scratch[1].to_bits(), sentinel.to_bits());
    assert_eq!(scratch[4].to_bits(), 3.0_f64.to_bits());
}
