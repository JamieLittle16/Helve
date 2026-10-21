//! Candidate stock 26.2 SQUEEZE unary stage, not yet original-JVM-qualified.
//!
//! The bound Overworld root was observed as
//! `Ap2 MIN(Mapped SQUEEZE(Marker), HolderHolder(RangeChoice))`.
//! The inner `Marker` value was not among the original 128 child operands:
//! tests below cover the candidate arithmetic and the bounded Rust compiler,
//! not finalDensity, source-law admission or production terrain generation.

use helve_world_gen::density_noise_direct_262::DirectNoiseScale262;
use helve_world_gen::density_primitives_262::DensityPrimitive262;
use helve_world_gen::seeded_registered_noise_262::{
    StockRegisteredNoiseKey262, StockWorldSeededNoiseSet262,
};
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
    StockDensityProgramError262 as ProgramError,
};

fn candidate(value: f64) -> f64 {
    let x = value.clamp(-1.0, 1.0);
    x / 2.0 - x * x * x / 24.0
}

#[test]
fn candidate_squeeze_is_clamped_and_respects_operation_order() {
    for input in [-9.0, -2.0, -1.0, -0.5, -0.125, 0.0, 0.125, 0.5, 1.0, 2.0, 9.0] {
        let program = Program::new([
            Node::Primitive(DensityPrimitive262::constant(input)),
            Node::CandidateSqueeze { input: 0 },
        ])
        .expect("valid explicitly candidate-mapped unary node");
        assert_eq!(
            program.sample_block(31, -64, 42).to_bits(),
            candidate(input).to_bits(),
            "candidate polynomial, input={input}"
        );
    }
    let positive = Program::new([
        Node::Primitive(DensityPrimitive262::constant(1.0)),
        Node::CandidateSqueeze { input: 0 },
    ])
    .expect("positive bound");
    let negative = Program::new([
        Node::Primitive(DensityPrimitive262::constant(-1.0)),
        Node::CandidateSqueeze { input: 0 },
    ])
    .expect("negative bound");
    assert_eq!(positive.sample_block(0, 0, 0).to_bits(), (11.0_f64 / 24.0).to_bits());
    assert_eq!(negative.sample_block(0, 0, 0).to_bits(), (-11.0_f64 / 24.0).to_bits());
}

#[test]
fn candidate_squeeze_rejects_forward_edges_and_disconnected_input() {
    let p = Node::Primitive(DensityPrimitive262::constant(0.5));
    assert_eq!(
        Program::new([Node::CandidateSqueeze { input: 0 }, p]).unwrap_err(),
        ProgramError::InvalidDependency { node: 0, child: 0 }
    );
    assert_eq!(
        Program::new([p, Node::CandidateSqueeze { input: 9 }]).unwrap_err(),
        ProgramError::InvalidDependency { node: 1, child: 9 }
    );
    assert_eq!(
        Program::new([p, p, Node::CandidateSqueeze { input: 0 }]).unwrap_err(),
        ProgramError::UnusedNode { node: 1 }
    );
}

#[test]
fn candidate_squeeze_can_be_shared_under_min_and_lazy_ap2_multiply() {
    let gradient =
        DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0).expect("observed gradient");
    let program = Program::new([
        Node::Primitive(gradient),
        Node::CandidateSqueeze { input: 0 },
        Node::Primitive(DensityPrimitive262::constant(0.4)),
        Node::ExplicitAp2Min { left: 1, right: 2 },
        Node::ExplicitAp2Multiply { left: 0, right: 3 },
    ])
    .expect("bounded and shared candidate stage");
    let sentinel = f64::from_bits(0x7ff8_1234_4567_89ab);
    let mut scratch = [sentinel; 5];
    assert_eq!(program.sample_with_scratch(0, 128, 0, &mut scratch).to_bits(), 0);
    assert!(scratch[1..4].iter().all(|v| v.to_bits() == sentinel.to_bits()));
    for y in [64, 127, 129, 192, 320] {
        let g = gradient.sample_block_y(y);
        let expected = g * candidate(g).min(0.4);
        assert_eq!(program.sample_block(1, y, -1).to_bits(), expected.to_bits());
    }
}

#[test]
fn candidate_squeeze_seeded_graph_plane_and_cell_are_scalar_coherent() {
    let noise_owner = StockWorldSeededNoiseSet262::new_candidate(0x0123_4567_89ab_cdef);
    let noise = noise_owner.density(
        StockRegisteredNoiseKey262::Temperature,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    );
    let program = Program::new([
        Node::RegisteredNoise(noise),
        Node::CandidateSqueeze { input: 0 },
        Node::Primitive(DensityPrimitive262::constant(0.2)),
        Node::ExplicitAp2Min { left: 1, right: 2 },
    ])
    .expect("candidate stock graph with reused existing noise kernel");
    let mut plane = [f64::NAN; 256];
    program
        .sample_plane_16x16(-16, 128, -16, &mut plane)
        .expect("bounded candidate plane");
    for dz in 0_i32..16 {
        for dx in 0_i32..16 {
            let index = usize::try_from(dz * 16 + dx).expect("bounded offset");
            assert_eq!(
                plane[index].to_bits(),
                program.sample_block(-16 + dx, 128, -16 + dz).to_bits()
            );
        }
    }
    let mut cell = vec![f64::NAN; 4096].into_boxed_slice();
    program
        .sample_cell_16x16x16(
            -16,
            120,
            -16,
            cell.as_mut().try_into().expect("fixed borrowed 4096 output"),
        )
        .expect("bounded candidate cell");
    for dy in 0_i32..16 {
        for dz in 0_i32..16 {
            for dx in 0_i32..16 {
                let index = usize::try_from((dy * 16 + dz) * 16 + dx).expect("bounded");
                assert_eq!(
                    cell[index].to_bits(),
                    program.sample_block(-16 + dx, 120 + dy, -16 + dz).to_bits()
                );
            }
        }
    }
}
