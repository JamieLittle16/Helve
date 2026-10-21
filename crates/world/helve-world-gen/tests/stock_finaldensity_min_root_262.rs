//! Exact stock 26.2 finite Ap2 MIN *root operator* evidence.
//!
//! This test compiles the MIN operation over the two frozen, original JVM
//! child values at each of 128 real Overworld `SinglePointContext` coordinates.
//! It does NOT implement or recompute either child subtree in Rust. Full
//! `finalDensity` / `NoiseChunk` numerical parity and production remain OPEN.

use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
};

const ORIGINAL: &str = include_str!("data/stock_finaldensity_min_root_128_rawbits.tsv");
const FINAL: &str = include_str!(
    "../../../../vanilla/reports/worldgen-26_2-stock-final-density-singlepoint-128-bits.txt"
);

fn word(raw: &str) -> u64 {
    assert_eq!(raw.len(), 16, "16 original raw hexadecimal digits");
    u64::from_str_radix(raw, 16).expect("original source-free IEEE-754 f64")
}

#[test]
fn compiled_explicit_ap2_min_matches_all_128_original_java_root_words() {
    let expected: Vec<_> = FINAL.lines().map(word).collect();
    assert_eq!(expected.len(), 128);
    let mut count = 0;
    let mut right_wins = 0;
    for (index, row) in ORIGINAL.lines().enumerate() {
        let fields: Vec<_> = row.split('\t').collect();
        assert_eq!(fields.len(), 3);
        let a = f64::from_bits(word(fields[0]));
        let b = f64::from_bits(word(fields[1]));
        let java = word(fields[2]);
        assert!(a.is_finite() && b.is_finite());
        assert_ne!(a.to_bits() & 0x7fff_ffff_ffff_ffff, 0, "observed nonzero left");
        assert_ne!(b.to_bits() & 0x7fff_ffff_ffff_ffff, 0, "observed nonzero right");
        assert_eq!(
            java, expected[index],
            "must preserve independent 128-word fixture"
        );

        let program = Program::new([
            Node::Primitive(DensityPrimitive262::constant(a)),
            Node::Primitive(DensityPrimitive262::constant(b)),
            Node::ExplicitAp2Min { left: 0, right: 1 },
        ])
        .expect("bounded compiled observed MIN subtree");
        assert_eq!(
            program.sample_block(0, 64, 0).to_bits(),
            java,
            "compiled original stock Ap2 MIN at sample {index}"
        );
        if b < a {
            right_wins += 1;
        }
        count += 1;
    }
    assert_eq!(count, 128);
    assert_eq!(
        right_wins, 4,
        "HolderHolder RangeChoice cannot be discarded"
    );
}

#[test]
fn min_node_is_reachable_and_compatible_with_lazy_ap2_multiply() {
    let left = DensityPrimitive262::constant(2.0);
    let right = DensityPrimitive262::constant(1.0);
    let gradient = DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0)
        .expect("observed gradient law");
    let program = Program::new([
        Node::Primitive(left),
        Node::Primitive(right),
        Node::ExplicitAp2Min { left: 0, right: 1 },
        Node::Primitive(gradient),
        Node::ExplicitAp2Multiply { left: 3, right: 2 },
    ])
    .expect("bounded typed min nested under lazy multiply");

    let sentinel = f64::from_bits(0x7ff8_1234_5678_9abc);
    let mut scratch = [sentinel; 5];
    assert_eq!(
        program
            .sample_with_scratch(0, 128, 0, &mut scratch)
            .to_bits(),
        0
    );
    for slot in &scratch[..3] {
        assert_eq!(
            slot.to_bits(),
            sentinel.to_bits(),
            "lazy +0 skips MIN subtree"
        );
    }
    assert_eq!(scratch[3].to_bits(), 0.0_f64.to_bits());
    assert_eq!(scratch[4].to_bits(), 0.0_f64.to_bits());

    let mut scratch = [sentinel; 5];
    let result = program.sample_with_scratch(0, 127, 0, &mut scratch);
    assert_eq!(scratch[2].to_bits(), 1.0_f64.to_bits());
    assert_eq!(result.to_bits(), gradient.sample_block_y(127).to_bits());
}

#[test]
fn explicit_min_batch_paths_equal_scalar_results_without_heap_in_evaluator() {
    let gradient =
        DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0).expect("observed Y gradient");
    let program = Program::new([
        Node::Primitive(gradient),
        Node::Primitive(DensityPrimitive262::constant(0.1)),
        Node::ExplicitAp2Min { left: 0, right: 1 },
    ])
    .expect("two leaves MIN root");
    let mut plane = [f64::NAN; 256];
    program
        .sample_plane_16x16(-16, 127, -16, &mut plane)
        .expect("bounded plane");
    let scalar = program.sample_block(-16, 127, -16).to_bits();
    assert!(plane.iter().all(|v| v.to_bits() == scalar));
    let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
    program
        .sample_cell_16x16x16(
            -16,
            120,
            -16,
            cell.as_mut().try_into().expect("fixed owned cell buffer"),
        )
        .expect("bounded cell");
    for (dy, plane) in cell.chunks_exact(256).enumerate() {
        let y = 120 + i32::try_from(dy).expect("bounded Y");
        let expected = program.sample_block(-16, y, -16).to_bits();
        assert!(plane.iter().all(|v| v.to_bits() == expected));
    }
}
