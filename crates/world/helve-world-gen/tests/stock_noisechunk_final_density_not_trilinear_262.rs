//! Negative control from the genuine 768-bit stock 26.2 NoiseChunk capture.
//!
//! A `finalDensity` value is **not** generally the trilinear interpolation of
//! its eight observed final-output corner values. The real density graph,
//! wrappers, and per-cell evaluator must be implemented; interpolating a
//! post-processed final field from just the corner samples is insufficient.
//!
//! The source-free numeric fixture is a reference, not a Rust finalDensity
//! implementation or any permission to generate production terrain.

const REFERENCE: &str = include_str!(
    "../../../../vanilla/reports/worldgen-26_2-stock-noisechunk-adjacent-768-bits.txt"
);

fn read_bits() -> Vec<u64> {
    let bits: Vec<u64> = REFERENCE
        .lines()
        .map(|raw| u64::from_str_radix(raw, 16).expect("fixed original 26.2 IEEE bits"))
        .collect();
    assert_eq!(
        bits.len(),
        768,
        "four seeds, two chunks, 96 positions per chunk"
    );
    bits
}

// Stock candidate fixture ordering from the source-free adjacent tool:
// seed -> chunk -> X cell -> Z cell -> Y cell descending (17,16,15) ->
// local Y (7,0) -> local X (0,3) -> local Z (0,3).
fn index(
    seed: usize,
    chunk: usize,
    cx: usize,
    cz: usize,
    cy: usize,
    ly: usize,
    lx: usize,
    lz: usize,
) -> usize {
    assert!(seed < 4 && chunk < 2 && cx < 2 && cz < 2);
    assert!(cy < 3 && ly < 2 && lx < 2 && lz < 2);
    (seed * 2 + chunk) * 96 + (((((cx * 2 + cz) * 3 + cy) * 2 + ly) * 2 + lx) * 2 + lz)
}

fn value(
    bits: &[u64],
    seed: usize,
    chunk: usize,
    cx: usize,
    cz: usize,
    cy: usize,
    ly: usize,
    lx: usize,
    lz: usize,
) -> f64 {
    f64::from_bits(bits[index(seed, chunk, cx, cz, cy, ly, lx, lz)])
}

#[inline]
fn lerp(t: f64, a: f64, b: f64) -> f64 {
    a + t * (b - a)
}

#[test]
fn real_noisechunk_final_output_is_not_plain_trilinear_corners() {
    let bits = read_bits();
    let mut largest_difference = 0.0_f64;
    let mut verified = 0_usize;
    for seed in 0..4 {
        for chunk in 0..2 {
            // Bottom eight geometric cube corners are at X/Z = origin or
            // origin+4, Y=64. Top corners are Y=72. All are independently
            // observed as local offset zero in neighboring source cells.
            let mut y_lerped = [[0.0_f64; 2]; 2];
            for (ix, row) in y_lerped.iter_mut().enumerate() {
                for (iz, out) in row.iter_mut().enumerate() {
                    let bottom = value(&bits, seed, chunk, ix, iz, 1, 1, 0, 0);
                    let top = value(&bits, seed, chunk, ix, iz, 0, 1, 0, 0);
                    *out = lerp(7.0 / 8.0, bottom, top);
                }
            }
            let z0 = lerp(3.0 / 4.0, y_lerped[0][0], y_lerped[1][0]);
            let z1 = lerp(3.0 / 4.0, y_lerped[0][1], y_lerped[1][1]);
            let naive = lerp(3.0 / 4.0, z0, z1);
            // Actual stock output at (origin+3,71,origin+3): cell
            // X0/Z0/Y16, upper local Y7, upper local X3 and Z3.
            let actual = value(&bits, seed, chunk, 0, 0, 1, 0, 1, 1);
            let difference = (actual - naive).abs();
            assert!(
                difference > 1e-5,
                "stock finalDensity should not silently become a naive trilinear final-output field"
            );
            largest_difference = largest_difference.max(difference);
            verified += 1;
        }
    }
    assert_eq!(verified, 8);
    // At least one genuine 26.2 stock observation differs materially.
    assert!(
        largest_difference > 0.01,
        "a generic final-output interpolator is not the 26.2 stock density graph"
    );
}
