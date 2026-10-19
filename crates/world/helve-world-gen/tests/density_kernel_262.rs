//! Source-free density-kernel tests: retained direct-seed 26.2 noise
//! samplers remain exact. These are NOT official density-router vectors.

use helve_world_gen::density_kernel_262::{
    DensityKernel262, DensityKernelError262, DensityNode262,
};
use helve_world_gen::perlin_normal_262::{NormalNoise262, PerlinNoise262};

const OFFICIAL_NOISE: &str = include_str!("data/perlin_normal_26_2_rawbits.tsv");
const SEEDS: [&str; 5] = [
    "0x0000000000000000",
    "0x0000000000000001",
    "0xffffffffffffffff",
    "0x8000000000000000",
    "0x9e3779b97f4a7c15",
];

fn bits(s: &str) -> u64 {
    u64::from_str_radix(s.strip_prefix("0x").expect("official bits prefix"), 16)
        .expect("16 exact hex digits")
}

#[test]
fn unmodified_noise_leaf_preserves_all_320_official_perlin_normal_bits() {
    // This is noise-LEAF parity, not a Minecraft density-router oracle.
    let lines: Vec<_> = OFFICIAL_NOISE
        .lines()
        .filter(|s| !s.starts_with('#') && !s.is_empty())
        .collect();
    assert_eq!(lines.len(), 160);
    for (seed_index, seed) in SEEDS.iter().enumerate() {
        let perlin = PerlinNoise262::from_direct_seed_observed_profile(bits(seed));
        let normal = NormalNoise262::from_direct_seed_observed_profile(bits(seed));
        let perlin_leaf = DensityKernel262::new([DensityNode262::Perlin(&perlin)]).unwrap();
        let normal_leaf = DensityKernel262::new([DensityNode262::Normal(&normal)]).unwrap();
        let mut perlin_scratch = [0.0];
        let mut normal_scratch = [0.0];
        for (sample, line) in lines[seed_index * 32..(seed_index + 1) * 32]
            .iter()
            .enumerate()
        {
            let fields: Vec<_> = line.split_whitespace().collect();
            assert_eq!(fields.len(), 6);
            assert_eq!(fields[0], *seed);
            let (x, y, z) = (
                f64::from_bits(bits(fields[1])),
                f64::from_bits(bits(fields[2])),
                f64::from_bits(bits(fields[3])),
            );
            assert_eq!(
                perlin_leaf.sample_with_scratch(x, y, z, &mut perlin_scratch).to_bits(),
                bits(fields[4]),
                "Perlin density leaf, seed {seed}, row {sample}"
            );
            assert_eq!(
                normal_leaf.sample_with_scratch(x, y, z, &mut normal_scratch).to_bits(),
                bits(fields[5]),
                "Normal density leaf, seed {seed}, row {sample}"
            );
        }
    }
}

#[test]
fn ordered_arithmetic_reuses_prior_values_and_preserves_ieee_bits() {
    let normal = NormalNoise262::from_direct_seed_observed_profile(42);
    let graph = DensityKernel262::new([
        DensityNode262::Normal(&normal),
        DensityNode262::Constant(0.5),
        DensityNode262::Add { left: 0, right: 1 },
        DensityNode262::Y,
        DensityNode262::Multiply { left: 2, right: 3 },
    ])
    .unwrap();
    let mut scratch = [f64::NAN; 5];
    for (x, y, z) in [
        (-16.125, -63.875, 31.5),
        (0.0, 0.0, 0.0),
        (0.5, -0.0, -0.5),
        (33_554_432.125, 63.875, -33_554_432.125),
    ] {
        let expected = (normal.sample(x, y, z) + 0.5) * y;
        assert_eq!(
            graph.sample_with_scratch(x, y, z, &mut scratch).to_bits(),
            expected.to_bits()
        );
        assert_eq!(graph.sample(x, y, z).to_bits(), expected.to_bits());
    }
}

#[test]
fn bounded_dag_rejects_invalid_edges_empty_graph_and_dead_work() {
    assert!(matches!(
        DensityKernel262::new([]),
        Err(DensityKernelError262::Empty)
    ));
    assert!(matches!(
        DensityKernel262::new([DensityNode262::Add { left: 0, right: 0 }]),
        Err(DensityKernelError262::InvalidDependency { node: 0, child: 0 })
    ));
    assert!(matches!(
        DensityKernel262::new([
            DensityNode262::Constant(1.0),
            DensityNode262::Add { left: 0, right: 2 },
            DensityNode262::Y,
        ]),
        Err(DensityKernelError262::InvalidDependency { node: 1, child: 2 })
    ));
    assert!(matches!(
        DensityKernel262::new([
            DensityNode262::Constant(1.0),
            DensityNode262::Constant(2.0),
        ]),
        Err(DensityKernelError262::UnusedNode { node: 0 })
    ));
    let shared = DensityKernel262::new([
        DensityNode262::Constant(0.5),
        DensityNode262::Add { left: 0, right: 0 },
    ])
    .unwrap();
    assert_eq!(shared.sample(1.0, 2.0, 3.0).to_bits(), 1.0_f64.to_bits());
    for special in [0.0_f64, -0.0_f64, f64::MIN_POSITIVE, f64::MAX] {
        let single = DensityKernel262::new([DensityNode262::Constant(special)]).unwrap();
        assert_eq!(single.sample(0.0, 0.0, 0.0).to_bits(), special.to_bits());
        let mut output = [0.0; 256];
        single.sample_plane_16x16(-16.0, 4.0, 0.0, &mut output);
        assert!(output.iter().all(|v| v.to_bits() == special.to_bits()));
    }
}

#[test]
fn coherent_plane_and_y_z_x_cell_match_scalar_at_signed_boundaries() {
    let normal = NormalNoise262::from_direct_seed_observed_profile(u64::MAX);
    let single = DensityKernel262::new([DensityNode262::Normal(&normal)]).unwrap();
    let perlin = PerlinNoise262::from_direct_seed_observed_profile(42);
    let perlin_leaf = DensityKernel262::new([DensityNode262::Perlin(&perlin)]).unwrap();
    let compound = DensityKernel262::new([
        DensityNode262::Normal(&normal),
        DensityNode262::Y,
        DensityNode262::Add { left: 0, right: 1 },
    ])
    .unwrap();

    for (x0, y, z0) in [
        (-16.125, -63.875, -16.25),
        (33_554_432.25, 31.125, -33_554_432.25),
    ] {
        for graph in [&single, &perlin_leaf] {
            let mut plane = [0.0; 256];
            graph.sample_plane_16x16(x0, y, z0, &mut plane);
            for lz in 0_u8..16 {
                for lx in 0_u8..16 {
                    let index = usize::from(lz) * 16 + usize::from(lx);
                    assert_eq!(
                        plane[index].to_bits(),
                        graph.sample(x0 + f64::from(lx), y, z0 + f64::from(lz)).to_bits()
                    );
                }
            }
        }
    }

    let mut cell = [0.0; 4096];
    compound.sample_cell_16x16x16(-16.125, -64.25, 31.5, &mut cell);
    for iy in 0_u8..16 {
        for iz in 0_u8..16 {
            for ix in 0_u8..16 {
                let index =
                    usize::from(iy) * 256 + usize::from(iz) * 16 + usize::from(ix);
                let x = -16.125 + f64::from(ix);
                let y = -64.25 + f64::from(iy);
                let z = 31.5 + f64::from(iz);
                assert_eq!(
                    cell[index].to_bits(),
                    compound.sample(x, y, z).to_bits(),
                    "Y/Z/X density cell order at local ({ix}, {iy}, {iz})"
                );
            }
        }
    }
}

#[test]
fn independent_worker_scratch_never_changes_immutable_program_results() {
    let perlin = PerlinNoise262::from_direct_seed_observed_profile(42);
    let graph = DensityKernel262::new([
        DensityNode262::Perlin(&perlin),
        DensityNode262::X,
        DensityNode262::Multiply { left: 0, right: 1 },
    ])
    .unwrap();
    let expected = graph.sample(-8.125, 0.5, 31.125).to_bits();
    std::thread::scope(|scope| {
        for _ in 0..4 {
            let shared = &graph;
            scope.spawn(move || {
                let mut scratch = [0.0; 3];
                for _ in 0..100 {
                    assert_eq!(
                        shared.sample_with_scratch(-8.125, 0.5, 31.125, &mut scratch).to_bits(),
                        expected
                    );
                }
            });
        }
    });
}
