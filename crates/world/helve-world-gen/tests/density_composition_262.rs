//! 1,280 independently observed official 26.2 composed density raw-bit vectors.
//! This is bounded JVM-output parity, NOT a complete `DensityFunctions` source
//! review or production authorization.

use helve_world_gen::density_composition_262::DensityComposition262;
use helve_world_gen::density_primitives_262::{DensityPrimitive262, DensityPrimitiveError262};

const OFFICIAL: &str = include_str!("data/density_composed_26_2_rawbits.tsv");
const DELEGATES: &str = include_str!("data/density_delegate_26_2_observed.tsv");
const SEEDS: [&str; 5] = [
    "0x0000000000000000",
    "0x0000000000000001",
    "0xffffffffffffffff",
    "0x8000000000000000",
    "0x9e3779b97f4a7c15",
];
const PROFILES: [&str; 8] = [
    "add_gradients",
    "mul_gradients",
    "add_zero_left",
    "add_zero_right",
    "mul_zero_left",
    "mul_zero_right",
    "add_self",
    "mul_half",
];
const Y_LEVELS: [i32; 32] = [
    -4096, -65, -64, -63, -31, -30, -29, -1, 0, 1, 15, 16, 17, 18, 63, 64, 127, 128, 255, 256, 318,
    319, 320, 321, 1024, -1024, -384, -320, 319, -64, 17, 320,
];

fn bits(raw: &str) -> u64 {
    let hex = raw.strip_prefix("0x").expect("official raw IEEE prefix");
    assert_eq!(hex.len(), 16);
    u64::from_str_radix(hex, 16).expect("exact official u64 raw bits")
}

fn primitive(profile: &str) -> DensityPrimitive262 {
    match profile {
        "gradient_world_height" => {
            DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0).unwrap()
        }
        "gradient_reverse" => DensityPrimitive262::y_clamped_gradient(-30, 17, 0.5, -0.75).unwrap(),
        "constant_negative_zero" => DensityPrimitive262::constant(-0.0),
        "constant_fraction" => DensityPrimitive262::constant(0.5),
        _ => panic!("unrecognised official leaf {profile}"),
    }
}

fn program(profile: &str) -> DensityComposition262 {
    let world = primitive("gradient_world_height");
    let reverse = primitive("gradient_reverse");
    let zero = primitive("constant_negative_zero");
    let half = primitive("constant_fraction");
    match profile {
        "add_gradients" => DensityComposition262::add(world, reverse),
        "mul_gradients" => DensityComposition262::multiply(world, reverse),
        "add_zero_left" => DensityComposition262::add(zero, world),
        "add_zero_right" => DensityComposition262::add(world, zero),
        "mul_zero_left" => DensityComposition262::multiply(zero, world),
        "mul_zero_right" => DensityComposition262::multiply(world, zero),
        "add_self" => DensityComposition262::add(world, world),
        "mul_half" => DensityComposition262::multiply(world, half),
        _ => panic!("unrecognised official composition profile {profile}"),
    }
}

#[test]
fn all_1280_exact_official_density_composition_bits_match() {
    assert!(OFFICIAL.contains(
        "Original JSON SHA256: a303cc90269cf273cb5d65ed470fe118263468708c59897f89399e7fa1adff20"
    ));
    assert!(OFFICIAL.contains(
        "Factory add body SHA256: aff60df9dc11f0e52d061660cf39684dfd671e214ab185174a293ce96ddebe58"
    ));
    assert!(OFFICIAL.contains(
        "Factory mul body SHA256: c5d5aaa53f8650d9068362c193487625eeeb057633eaafb0142651a4cc29d7f1"
    ));
    let mut row_count = 0;
    for line in OFFICIAL
        .lines()
        .filter(|line| !line.is_empty() && !line.starts_with('#'))
    {
        let fields: Vec<_> = line.split_whitespace().collect();
        assert_eq!(fields.len(), 6, "official row {row_count}");
        let profile_idx = row_count / 160;
        let seed_idx = (row_count / 32) % 5;
        let coordinate_idx = row_count % 32;
        assert_eq!(fields[0], PROFILES[profile_idx]);
        assert_eq!(fields[1], SEEDS[seed_idx]);
        let x = fields[2].parse::<i32>().unwrap();
        let y = fields[3].parse::<i32>().unwrap();
        let z = fields[4].parse::<i32>().unwrap();
        let index = i32::try_from(coordinate_idx).unwrap();
        let expected_x = (if index % 2 == 0 {
            33_554_432
        } else {
            -33_554_432
        }) + index * 13;
        let expected_z = (if index % 3 == 0 {
            index * 17
        } else {
            -index * 17
        }) - 16;
        assert_eq!(
            (x, y, z),
            (expected_x, Y_LEVELS[coordinate_idx], expected_z)
        );
        let actual = program(fields[0]).sample_block_y(y).to_bits();
        let expected = bits(fields[5]);
        assert_eq!(
            actual, expected,
            "official row {row_count} profile {} at ({x},{y},{z}) seed {}",
            fields[0], fields[1]
        );
        row_count += 1;
    }
    assert_eq!(row_count, 1280);
}

#[test]
fn multiplication_distinguishes_two_dynamic_leaves_from_signed_zero_constant() {
    let two_functions = program("mul_gradients");
    let constant_first = program("mul_zero_left");
    let constant_second = program("mul_zero_right");
    let half = program("mul_half");
    let world = primitive("gradient_world_height");
    let reverse = primitive("gradient_reverse");

    assert_eq!(world.sample_block_y(128).to_bits(), 0.0_f64.to_bits());
    assert_eq!(reverse.sample_block_y(128).to_bits(), (-0.75_f64).to_bits());
    // Standard IEEE +0 × negative produces -0; the official 26.2
    // factory's two-function case instead produces +0.
    assert_eq!((0.0_f64 * -0.75_f64).to_bits(), (-0.0_f64).to_bits());
    assert_eq!(
        two_functions.sample_block_y(128).to_bits(),
        0.0_f64.to_bits()
    );
    assert_eq!(
        constant_first.sample_block_y(128).to_bits(),
        (-0.0_f64).to_bits()
    );
    assert_eq!(
        constant_second.sample_block_y(128).to_bits(),
        (-0.0_f64).to_bits()
    );
    assert_eq!(half.sample_block_y(128).to_bits(), 0.0_f64.to_bits());
    assert_eq!(
        constant_first.sample_block_y(-64).to_bits(),
        0.0_f64.to_bits()
    );
    assert_eq!(
        constant_second.sample_block_y(320).to_bits(),
        (-0.0_f64).to_bits()
    );
}

#[test]
fn horizontal_planes_and_cells_reuse_single_y_value_without_allocations() {
    for profile in PROFILES {
        let evaluator = program(profile);
        let mut plane = [f64::NAN; 256];
        evaluator.sample_plane_16x16(128, &mut plane);
        assert!(
            plane
                .iter()
                .all(|v| v.to_bits() == evaluator.sample_block_y(128).to_bits())
        );

        let mut values = vec![f64::NAN; 4096];
        let cell: &mut [f64; 4096] = values.as_mut_slice().try_into().unwrap();
        evaluator.sample_cell_16x16x16(120, cell).unwrap();
        for (local_y, slice) in values.chunks_exact(256).enumerate() {
            let y = 120 + i32::try_from(local_y).unwrap();
            let expected = evaluator.sample_block_y(y).to_bits();
            assert!(slice.iter().all(|v| v.to_bits() == expected));
        }
    }
}

#[test]
fn overflow_rejected_before_mutating_cell() {
    let program = program("mul_gradients");
    let mut buffer = vec![f64::NAN; 4096];
    let cell: &mut [f64; 4096] = buffer.as_mut_slice().try_into().unwrap();
    assert_eq!(
        program.sample_cell_16x16x16(i32::MAX - 14, cell),
        Err(DensityPrimitiveError262::CellYOverflow)
    );
    assert!(cell.iter().all(|v| v.is_nan()));
    assert_eq!(program.sample_cell_16x16x16(i32::MAX - 15, cell), Ok(()));
}

#[test]
fn all_official_factory_runtime_delegate_classes_are_statically_selected() {
    // Independent official-JVM reflection plus private Atlas fingerprints.
    // This asserts the source-free *shape* identity; it does not source-admit
    // the reached implementation's exact branch predicates.
    assert!(DELEGATES.contains(
        "frontier JSON bytes: 104689; SHA-256: 2b97fea7676ba68d563a1ef97b350ded934998f3359588b22884e9ecf992d578"
    ));
    let implementation_root = "net.minecraft.world.level.levelgen.DensityFunctions$";
    let ap2_body = "54d44e99cae188665438eda580ab0a76204c0c486b80edb603f32fa4375b3e48";
    let pure_body = "80087cd337e4ac54a98884a9c47579f4573740fc983f033ed2243e579515a6dd";
    let mut count = 0;
    for line in DELEGATES
        .lines()
        .filter(|line| !line.is_empty() && !line.starts_with('#'))
    {
        let fields: Vec<_> = line.split_whitespace().collect();
        assert_eq!(fields.len(), 4);
        assert_eq!(fields[0], PROFILES[count]);
        let instance = program(fields[0]);
        let (expected_type, expected_compute, expected_hash) = match instance {
            DensityComposition262::AddFunctions { left, right } => {
                assert!(!matches!(left, DensityPrimitive262::Constant(_)));
                assert!(!matches!(right, DensityPrimitive262::Constant(_)));
                ("Ap2", "Ap2", ap2_body)
            }
            DensityComposition262::MultiplyFunctions { left, right } => {
                assert!(!matches!(left, DensityPrimitive262::Constant(_)));
                assert!(!matches!(right, DensityPrimitive262::Constant(_)));
                ("Ap2", "Ap2", ap2_body)
            }
            DensityComposition262::AddWithConstant { left, right }
            | DensityComposition262::MultiplyWithConstant { left, right } => {
                assert!(
                    matches!(left, DensityPrimitive262::Constant(_))
                        || matches!(right, DensityPrimitive262::Constant(_))
                );
                ("MulOrAdd", "PureTransformer", pure_body)
            }
        };
        assert_eq!(fields[1], format!("{implementation_root}{expected_type}"));
        assert_eq!(fields[2], format!("{implementation_root}{expected_compute}"));
        assert_eq!(fields[3], expected_hash);
        count += 1;
    }
    assert_eq!(count, PROFILES.len());
}
