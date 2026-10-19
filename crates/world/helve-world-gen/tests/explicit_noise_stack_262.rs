//! Source-neutral, raw-bit differential tests for prepared axes and
//! explicit ordered octave composition. These mechanisms do not purport
//! to implement target 26.2 `PerlinNoise`/`NormalNoise` source rules.

use helve_world_gen::explicit_noise_stack_262::{ExplicitNoiseLayer262, ExplicitNoiseStack262};
use helve_world_gen::improved_noise_262::ImprovedNoise262;

fn check_axis_grid(
    sampler: &ImprovedNoise262,
    x_axis: &[f64; 16],
    y: f64,
    z_axis: &[f64; 16],
) {
    let mut output = [f64::NAN; 256];
    sampler.sample_axis_grid_16x16(x_axis, y, z_axis, &mut output);
    for (iz, &z) in z_axis.iter().enumerate() {
        for (ix, &x) in x_axis.iter().enumerate() {
            assert_eq!(
                output[iz * 16 + ix].to_bits(),
                sampler.sample(x, y, z).to_bits(),
                "prepared axis [{ix}, {iz}] at ({x}, {y}, {z})"
            );
        }
    }
}

#[test]
fn arbitrary_axes_match_scalar_bits_including_repetition_and_negative_zero() {
    let irregular_x = [
        0.0, -0.0, -16.0, -15.999, 15.0, 16.0, 31.125, -31.125,
        0.0, 0.125, -0.125, 1024.25, -1024.25,
        1_048_576.0, -1_048_576.0, 1_073_741_824.0,
    ];
    let irregular_z = [
        -0.0, 0.0, -16.0, -16.0, -17.0, 17.0, 0.75, -0.75,
        31.5, -31.5, 0.000_000_000_000_000_2,
        -0.000_000_000_000_000_2, 128.25, -128.25,
        -1_073_741_824.0, 1_073_741_824.0,
    ];
    for seed in [0, 1, u64::MAX, 1_u64 << 63, 0x9e37_79b9_7f4a_7c15] {
        let sampler = ImprovedNoise262::new(seed);
        for y in [0.0, -0.0, -64.0, 319.875, -63.875, 0.125] {
            check_axis_grid(&sampler, &irregular_x, y, &irregular_z);
        }
    }
}

fn four_layer_stack(seed: u64) -> ExplicitNoiseStack262<4> {
    ExplicitNoiseStack262::new([
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed), 1.0, 0.5),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(1)), 0.5, -0.25),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(2)), 2.0, 0.125),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(3)), 0.75, 0.375),
    ])
}

fn check_stack<const N: usize>(
    stack: &ExplicitNoiseStack262<N>,
    origin_x: f64,
    y: f64,
    origin_z: f64,
) {
    let mut output = [f64::NAN; 256];
    stack.sample_plane_16x16(origin_x, y, origin_z, &mut output);
    for iz in 0_u8..16 {
        for ix in 0_u8..16 {
            let x = origin_x + f64::from(ix);
            let z = origin_z + f64::from(iz);
            let expected = stack.sample(x, y, z).to_bits();
            let result = output[usize::from(iz) * 16 + usize::from(ix)].to_bits();
            assert_eq!(
                result, expected,
                "explicit stack {N} layers: origin=({origin_x},{y},{origin_z}), cell ({ix},{iz})"
            );
        }
    }
}

#[test]
fn frequency_scaled_four_octave_stack_matches_scalar_on_every_cell() {
    let origins = [
        (0.0, 0.0, 0.0), (-0.0, -0.0, -0.0),
        (-16.0, -64.0, -16.0), (-17.0, -63.5, 15.0),
        (15.0, 319.0, -17.0), (31.125, -63.875, -31.125),
        (-31.125, 319.875, 31.125), (1_048_576.0, 256.0, -1_048_576.0),
        (-1_073_741_824.0, 319.0, 1_073_741_824.0),
    ];
    for seed in [0, 1, u64::MAX, 1_u64 << 63, 0x9e37_79b9_7f4a_7c15] {
        let stack = four_layer_stack(seed);
        assert_eq!(stack.len(), 4);
        assert!(!stack.is_empty());
        for (x, y, z) in origins {
            check_stack(&stack, x, y, z);
        }
    }
}

#[test]
fn empty_stack_is_positive_zero_and_zero_weights_are_not_skipped() {
    let empty = ExplicitNoiseStack262::<0>::new([]);
    assert_eq!(empty.sample(-0.0, 0.0, -16.0).to_bits(), 0);
    assert!(empty.is_empty());
    let mut output = [f64::NAN; 256];
    empty.sample_plane_16x16(-0.0, 0.0, -16.0, &mut output);
    assert!(output.iter().all(|value| value.to_bits() == 0));

    let zero_weight = ExplicitNoiseStack262::new([
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(1), 0.75, 0.0),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(2), -0.5, -0.0),
    ]);
    check_stack(&zero_weight, -15.125, 319.875, -16.25);
    let lone = ExplicitNoiseStack262::new([
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(42), 0.75, 1.0),
    ]);
    check_stack(&lone, 0.125, -64.375, -31.125);
}

#[test]
fn layers_can_be_evaluated_on_independent_workers() {
    let stack = four_layer_stack(0x9e37_79b9_7f4a_7c15);
    let baseline = stack.sample(-16.125, -63.875, 15.125).to_bits();
    std::thread::scope(|scope| {
        for _ in 0..4 {
            let borrowed = &stack;
            scope.spawn(move || {
                for _ in 0..12 {
                    assert_eq!(borrowed.sample(-16.125, -63.875, 15.125).to_bits(), baseline);
                    check_stack(borrowed, -16.125, -63.875, 15.125);
                }
            });
        }
    });
}
