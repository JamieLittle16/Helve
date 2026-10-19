//! All 640 source-free official 26.2 integer-context DensityFunction.compute
//! raw-bit outputs, never inferred from a Rust float expected value.
//! This does NOT qualify arbitrary router nodes, random state or chunk publication.

use helve_world_gen::density_primitives_262::{
    DensityPrimitive262, DensityPrimitiveError262,
};

const OFFICIAL: &str = include_str!("data/density_primitive_26_2_rawbits.tsv");
const SEEDS: [&str; 5] = [
    "0x0000000000000000",
    "0x0000000000000001",
    "0xffffffffffffffff",
    "0x8000000000000000",
    "0x9e3779b97f4a7c15",
];
const PROFILES: [&str; 4] = [
    "constant_negative_zero",
    "constant_fraction",
    "gradient_world_height",
    "gradient_reverse",
];
const Y_LEVELS: [i32; 32] = [
    -4096, -65, -64, -63, -31, -30, -29, -1, 0, 1, 15, 16, 17, 18, 63, 64, 127, 128, 255,
    256, 318, 319, 320, 321, 1024, -1024, -384, -320, 319, -64, 17, 320,
];

fn raw_bits(hex: &str) -> u64 {
    let digits = hex.strip_prefix("0x").expect("official 0x bits prefix");
    assert_eq!(digits.len(), 16);
    u64::from_str_radix(digits, 16).expect("official exactly 64 raw bits")
}

fn primitive(profile: &str) -> DensityPrimitive262 {
    match profile {
        "constant_negative_zero" => DensityPrimitive262::constant(f64::from_bits(0x8000_0000_0000_0000)),
        "constant_fraction" => DensityPrimitive262::constant(0.5),
        "gradient_world_height" => DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0)
            .expect("observed official profile has valid bounds"),
        "gradient_reverse" => DensityPrimitive262::y_clamped_gradient(-30, 17, 0.5, -0.75)
            .expect("observed official profile has valid bounds"),
        _ => panic!("unknown official density profile {profile}"),
    }
}

#[test]
fn all_640_pinned_official_density_compute_raw_bits_match() {
    assert!(OFFICIAL.contains("Original complete official capture JSON SHA256: b1ee06e998b19ede5a283af2757e192dbb75fb6b761b55fa0d6a8a5f1e2297bc"));
    assert!(OFFICIAL.contains("Target 26.2 protocol 776 data version 4903"));
    let mut count = 0;
    for line in OFFICIAL.lines().filter(|line| !line.starts_with('#') && !line.is_empty()) {
        let fields: Vec<_> = line.split_whitespace().collect();
        assert_eq!(fields.len(), 6, "row {count}");
        let (profile_idx, seed_idx, position_idx) = (count / 160, (count / 32) % 5, count % 32);
        assert_eq!(fields[0], PROFILES[profile_idx]);
        assert_eq!(fields[1], SEEDS[seed_idx]);
        let block_x = fields[2].parse::<i32>().expect("official block X");
        let block_y = fields[3].parse::<i32>().expect("official block Y");
        let block_z = fields[4].parse::<i32>().expect("official block Z");
        let pos = i32::try_from(position_idx).expect("32 positions");
        assert_eq!(block_x, if pos % 2 == 0 { 33_554_432 } else { -33_554_432 } + pos * 13);
        assert_eq!(block_y, Y_LEVELS[position_idx]);
        assert_eq!(block_z, if pos % 3 == 0 { pos * 17 } else { -pos * 17 } - 16);
        let expected = raw_bits(fields[5]);
        let actual = primitive(fields[0]).sample_block_y(block_y).to_bits();
        assert_eq!(
            actual, expected,
            "official raw-bit mismatch row {count}: profile {}, seed {}, X/Y/Z {block_x}/{block_y}/{block_z}",
            fields[0], fields[1]
        );
        count += 1;
    }
    assert_eq!(count, 640, "four official profiles × five seed labels × 32 positions");
}

#[test]
fn preserves_raw_signed_zero_and_distinguishes_non_equivalent_lerp_order() {
    let negative_zero = DensityPrimitive262::constant(-0.0);
    for block_y in [i32::MIN, -64, 0, 128, 320, i32::MAX] {
        assert_eq!(negative_zero.sample_block_y(block_y).to_bits(), (-0.0_f64).to_bits());
    }
    let height = DensityPrimitive262::y_clamped_gradient(-64, 320, -1.0, 1.0).unwrap();
    assert_eq!(height.sample_block_y(-64).to_bits(), (-1.0_f64).to_bits());
    assert_eq!(height.sample_block_y(320).to_bits(), 1.0_f64.to_bits());
    assert_eq!(height.sample_block_y(128).to_bits(), 0.0_f64.to_bits());
    // The two algebraically equivalent lerps can disagree by 1 ULP.
    assert_eq!(height.sample_block_y(-63).to_bits(), 0xbfef_d555_5555_5555);
    assert_ne!(height.sample_block_y(-63).to_bits(), 0xbfef_d555_5555_5556);
    let reverse = DensityPrimitive262::y_clamped_gradient(-30, 17, 0.5, -0.75).unwrap();
    assert_eq!(reverse.sample_block_y(-29).to_bits(), 0x3fde_4c41_5c98_82b9);
    assert_eq!(reverse.sample_block_y(-1).to_bits(), 0xbfd1_5c98_82b9_3106);
}

#[test]
fn y_only_coherent_planes_and_cells_reuse_one_sample_per_vertical_level() {
    for profile in PROFILES {
        let density = primitive(profile);
        let mut horizontal = [f64::NAN; 256];
        density.sample_plane_16x16(-29, &mut horizontal);
        assert!(horizontal.iter().all(|v| v.to_bits() == density.sample_block_y(-29).to_bits()));

        // Keep the 32-KiB test buffer off the test thread stack.
        let mut output = vec![f64::NAN; 4096];
        let cell: &mut [f64; 4096] = output.as_mut_slice().try_into().expect("fixed cell");
        density.sample_cell_16x16x16(-38, cell).unwrap();
        for (y, plane) in output.chunks_exact(256).enumerate() {
            let world_y = -38 + i32::try_from(y).unwrap();
            assert!(plane.iter().all(|v| v.to_bits() == density.sample_block_y(world_y).to_bits()));
        }
    }
}

#[test]
fn invalid_construction_and_out_of_range_cells_fail_before_writing() {
    assert!(matches!(
        DensityPrimitive262::y_clamped_gradient(2, 2, 0.0, 1.0),
        Err(DensityPrimitiveError262::InvalidYInterval)
    ));
    assert!(matches!(
        DensityPrimitive262::y_clamped_gradient(2, 1, 0.0, 1.0),
        Err(DensityPrimitiveError262::InvalidYInterval)
    ));
    assert!(matches!(
        DensityPrimitive262::y_clamped_gradient(0, 1, f64::NAN, 0.0),
        Err(DensityPrimitiveError262::NonFiniteValue)
    ));
    assert!(matches!(
        DensityPrimitive262::y_clamped_gradient(0, 1, -f64::MAX, f64::MAX),
        Err(DensityPrimitiveError262::NonFiniteValue)
    ));
    let flat = DensityPrimitive262::constant(1.25);
    let mut output = vec![0.0; 4096];
    let cell: &mut [f64; 4096] = output.as_mut_slice().try_into().unwrap();
    assert_eq!(
        flat.sample_cell_16x16x16(i32::MAX - 14, cell),
        Err(DensityPrimitiveError262::CellYOverflow)
    );
    assert!(cell.iter().all(|x| x.to_bits() == 0.0_f64.to_bits()));
    flat.sample_cell_16x16x16(i32::MAX - 15, cell).unwrap();
    assert!(cell.iter().all(|x| x.to_bits() == 1.25_f64.to_bits()));
}
