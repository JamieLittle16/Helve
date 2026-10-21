//! 128 independently captured stock 26.2 SQUEEZE/RangeChoice observations.
//!
//! This tests *real* inner original JVM operand words in the bounded Rust DAG.
//! It still injects source-derived Marker and RangeChoice child values rather
//! than computing their underlying MulOrAdd / Ap2 / NoiseChunk graphs.
//! Source-law review, cache/interpolation semantics and production stay OPEN.

use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
    StockDensityProgramError262 as ProgramError,
};

const INNER: &str = include_str!("data/stock_finaldensity_inner_128_rawbits.tsv");
const ROOT: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const MIN: f64 = -1_000_000.0;
const MAX: f64 = 0.0;

fn bits(hex: &str) -> u64 {
    assert_eq!(hex.len(), 16, "source-frozen IEEE f64 needs 16 hex digits");
    u64::from_str_radix(hex, 16).expect("source-free original Java f64 word")
}

fn constant(value: f64) -> Node<'static> {
    Node::Primitive(DensityPrimitive262::constant(value))
}

#[test]
fn stock_squeeze_128_exact_jvm_marker_to_mapped_bits() {
    let mut count = 0;
    let mut clamped = 0;
    for (index, row) in INNER.lines().enumerate() {
        let cols: Vec<_> = row.split('\t').collect();
        assert_eq!(cols.len(), 7);
        assert_eq!(cols[0], cols[1], "single-point Interpolated Marker delegates");
        let marker = f64::from_bits(bits(cols[0]));
        if !(-1.0..=1.0).contains(&marker) {
            clamped += 1;
        }
        let program = Program::new([
            constant(marker),
            Node::CandidateSqueeze { input: 0 },
        ])
        .expect("one stock marker input and a typed SQUEEZE candidate");
        assert_eq!(
            program.sample_block(0, 64, 0).to_bits(),
            bits(cols[2]),
            "original four-seed Minecraft 26.2 Mapped output {index}"
        );
        count += 1;
    }
    assert_eq!(count, 128);
    assert!(clamped > 0, "stock evidence covers clamped SQUEEZE inputs");
}

#[test]
fn stock_range_choice_128_exact_jvm_selector_branch_and_min_root_bits() {
    let root_rows: Vec<_> = ROOT.lines().collect();
    assert_eq!(root_rows.len(), 128);
    let mut count = 0;
    let mut in_count = 0;
    let mut out_count = 0;
    let mut holder_wins = 0;
    for (index, row) in INNER.lines().enumerate() {
        let cols: Vec<_> = row.split('\t').collect();
        assert_eq!(cols.len(), 7);
        let marker = f64::from_bits(bits(cols[0]));
        let selector = f64::from_bits(bits(cols[3]));
        let when_in = f64::from_bits(bits(cols[4]));
        let when_out = f64::from_bits(bits(cols[5]));
        let holder = bits(cols[6]);
        let range_in = selector >= MIN && selector < MAX;
        assert_eq!(when_in.to_bits(), 64.0_f64.to_bits());
        assert_eq!(
            if range_in {
                when_in.to_bits()
            } else {
                when_out.to_bits()
            },
            holder,
            "original 26.2 RangeChoice branch {index}"
        );
        if range_in {
            in_count += 1;
        } else {
            out_count += 1;
        }
        let expected_root: Vec<_> = root_rows[index].split('\t').collect();
        assert_eq!(expected_root.len(), 3);
        assert_eq!(bits(cols[2]), bits(expected_root[0]));
        assert_eq!(holder, bits(expected_root[1]));

        // The candidate transform computes the genuine Mapped child from
        // the real Marker input, not from the saved Mapped output.
        // RangeChoice's *three* leaf values remain JVM-provided here.
        let program = Program::new([
            constant(marker),
            Node::CandidateSqueeze { input: 0 },
            constant(selector),
            constant(when_in),
            constant(when_out),
            Node::CandidateRangeChoice {
                selector: 2,
                when_in_range: 3,
                when_out_of_range: 4,
                min_inclusive: MIN,
                max_exclusive: MAX,
            },
            Node::ExplicitAp2Min { left: 1, right: 5 },
        ])
        .expect("bounded 26.2 finalDensity first two levels");
        assert_eq!(
            program.sample_block(0, 64, 0).to_bits(),
            bits(expected_root[2]),
            "source-free original stock finalDensity result {index}"
        );
        if f64::from_bits(holder) < f64::from_bits(bits(cols[2])) {
            holder_wins += 1;
        }
        count += 1;
    }
    assert_eq!(count, 128);
    assert_eq!(in_count, 47);
    assert_eq!(out_count, 81);
    assert_eq!(holder_wins, 4);
}

#[test]
fn range_choice_skips_inactive_dependency_and_memoizes_selected_branch() {
    const SENTINEL: u64 = 0x7ff8_1234_5678_9abc;
    for (selector, selected, skipped) in [(-0.5, 64.0, 2), (0.5, 3.0, 1)] {
        let program = Program::new([
            constant(selector),
            constant(64.0),
            constant(3.0),
            Node::CandidateRangeChoice {
                selector: 0,
                when_in_range: 1,
                when_out_of_range: 2,
                min_inclusive: MIN,
                max_exclusive: MAX,
            },
        ])
        .expect("valid explicitly selected branch");
        let mut scratch = [f64::from_bits(SENTINEL); 4];
        assert_eq!(
            program.sample_with_scratch(0, 64, 0, &mut scratch).to_bits(),
            selected.to_bits()
        );
        assert_eq!(
            scratch[skipped].to_bits(),
            SENTINEL,
            "must not evaluate unselected RangeChoice branch"
        );
    }

    let program = Program::new([
        constant(0.0),
        constant(0.5),
        constant(64.0),
        constant(3.0),
        Node::CandidateRangeChoice {
            selector: 1,
            when_in_range: 2,
            when_out_of_range: 3,
            min_inclusive: MIN,
            max_exclusive: MAX,
        },
        Node::ExplicitAp2Multiply { left: 0, right: 4 },
    ])
    .expect("nested conditional subgraph");
    let mut scratch = [f64::from_bits(SENTINEL); 6];
    assert_eq!(program.sample_with_scratch(0, 64, 0, &mut scratch).to_bits(), 0);
    assert!(scratch[1..5].iter().all(|value| value.to_bits() == SENTINEL));
}

#[test]
fn range_choice_cold_validator_rejects_forward_edges_and_invalid_bounds() {
    let p = constant(1.0);
    assert_eq!(
        Program::new([
            p,
            p,
            p,
            Node::CandidateRangeChoice {
                selector: 3,
                when_in_range: 1,
                when_out_of_range: 2,
                min_inclusive: MIN,
                max_exclusive: MAX,
            },
        ])
        .unwrap_err(),
        ProgramError::InvalidDependency { node: 3, child: 3 }
    );
    assert_eq!(
        Program::new([
            p,
            p,
            p,
            Node::CandidateRangeChoice {
                selector: 0,
                when_in_range: 1,
                when_out_of_range: 9,
                min_inclusive: MIN,
                max_exclusive: MAX,
            },
        ])
        .unwrap_err(),
        ProgramError::InvalidDependency { node: 3, child: 9 }
    );
    for (min_inclusive, max_exclusive) in [
        (1.0, 1.0),
        (2.0, 1.0),
        (f64::NAN, 1.0),
        (0.0, f64::INFINITY),
        (f64::NEG_INFINITY, 0.0),
    ] {
        assert_eq!(
            Program::new([
                p,
                p,
                p,
                Node::CandidateRangeChoice {
                    selector: 0,
                    when_in_range: 1,
                    when_out_of_range: 2,
                    min_inclusive,
                    max_exclusive,
                },
            ])
            .unwrap_err(),
            ProgramError::InvalidRangeBounds { node: 3 }
        );
    }
}

#[test]
fn range_choice_boundary_is_inclusive_low_and_exclusive_high() {
    const BELOW_ZERO: f64 = f64::from_bits(0x8000_0000_0000_0001);
    for (selector, expected) in [
        (MIN, 64.0),
        (MIN - 1.0, 3.0),
        (BELOW_ZERO, 64.0),
        (0.0, 3.0),
        (-0.0, 3.0),
        (1.0, 3.0),
    ] {
        let program = Program::new([
            constant(selector),
            constant(64.0),
            constant(3.0),
            Node::CandidateRangeChoice {
                selector: 0,
                when_in_range: 1,
                when_out_of_range: 2,
                min_inclusive: MIN,
                max_exclusive: MAX,
            },
        ])
        .expect("valid finite range candidate");
        assert_eq!(
            program.sample_block(0, 0, 0).to_bits(),
            expected.to_bits()
        );
    }
}
