//! Immutable, bounded **observed-state** normal noise for arbitrary octave spans.
//!
//! This is a COLD numeric-state replay substrate for authentic stock-registered
//! 26.2 NoiseParameters and prepared NormalNoise state. It does NOT derive a
//! sampler from a world seed, guess registry parameters or admit a production
//! generator. The only cross-runtime numeric assertion here uses the separately
//! pinned direct-seeded four-slot profile until a source-owned stock receipt is
//! available. VAR, SEM, NoiseRouter and chunk publication remain closed.
//!
//! The boxed amplitudes/octave states are built once and never allocated,
//! copied or mutated during scalar sampling. The same qualified scalar
//! arithmetic is used by the existing four-slot direct family.

use crate::density_noise_direct_262::DirectNoiseScale262;
use crate::improved_noise_262::ImprovedNoise262;
use crate::perlin_normal_262::{NORMAL_SECOND_INPUT_MULTIPLIER, sample_perlin_parts};

/// Upper bound for one prepared stock 26.2 Perlin amplitude/octave span.
/// A future reviewed source binding may narrow this limit, never bypass it.
pub const MAX_REGISTERED_OCTAVES_262: usize = 64;

/// Malformed observed numeric input is never repaired or padded.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum RegisteredNoiseStateError262 {
    /// No octaves or more than the deliberately bounded maximum.
    InvalidOctaveCount,
    /// Amplitudes and `ImprovedNoise` slots disagree.
    OctaveLengthMismatch,
    /// The signed first octave and final octave cannot both fit Java i32.
    OctaveIndexOverflow,
    /// An observed amplitude or factor is not a finite IEEE-754 value.
    NonFiniteNumericState,
}

/// Cold-owned, fixed-after-setup Perlin numeric state.
///
/// Separate from the registered key identity and world-seed RNG construction:
/// numeric replay alone is NOT a general constructor law.
#[derive(Clone, Debug)]
pub struct RegisteredPerlinObserved262 {
    first_octave: i32,
    amplitudes: Box<[f64]>,
    octaves: Box<[Option<ImprovedNoise262>]>,
    lowest_freq_input_factor: f64,
    lowest_freq_value_factor: f64,
}

impl RegisteredPerlinObserved262 {
    /// Load complete bounded, source-free numeric state, without truncation.
    ///
    /// This is a cold construction, not hot-path registry access.
    ///
    /// # Errors
    /// Rejects empty/oversized/mismatched octave arrays, arithmetic overflow,
    /// or any nonfinite amplitude/frequency/value factor.
    pub fn from_observed_parts(
        first_octave: i32,
        amplitudes: Box<[f64]>,
        octaves: Box<[Option<ImprovedNoise262>]>,
        lowest_freq_input_factor: f64,
        lowest_freq_value_factor: f64,
    ) -> Result<Self, RegisteredNoiseStateError262> {
        let count = amplitudes.len();
        if count == 0 || count > MAX_REGISTERED_OCTAVES_262 {
            return Err(RegisteredNoiseStateError262::InvalidOctaveCount);
        }
        if count != octaves.len() {
            return Err(RegisteredNoiseStateError262::OctaveLengthMismatch);
        }
        let maximum_index = i32::try_from(count - 1)
            .map_err(|_| RegisteredNoiseStateError262::InvalidOctaveCount)?;
        first_octave
            .checked_add(maximum_index)
            .ok_or(RegisteredNoiseStateError262::OctaveIndexOverflow)?;
        if !lowest_freq_input_factor.is_finite()
            || !lowest_freq_value_factor.is_finite()
            || amplitudes.iter().any(|a| !a.is_finite())
        {
            return Err(RegisteredNoiseStateError262::NonFiniteNumericState);
        }
        Ok(Self {
            first_octave,
            amplitudes,
            octaves,
            lowest_freq_input_factor,
            lowest_freq_value_factor,
        })
    }

    /// Signed Java first octave from the observed state.
    #[must_use]
    pub const fn first_octave(&self) -> i32 {
        self.first_octave
    }

    /// Number of received slots, including deliberately absent octaves.
    #[must_use]
    pub fn octave_count(&self) -> usize {
        self.amplitudes.len()
    }

    /// Compare full numeric state (including IEEE sign bits of zeros).
    #[must_use]
    pub fn state_bits_equal(&self, other: &Self) -> bool {
        self.first_octave == other.first_octave
            && self.amplitudes.len() == other.amplitudes.len()
            && self
                .amplitudes
                .iter()
                .zip(other.amplitudes.iter())
                .all(|(a, b)| a.to_bits() == b.to_bits())
            && self
                .octaves
                .iter()
                .zip(other.octaves.iter())
                .all(|(a, b)| match (a, b) {
                    (None, None) => true,
                    (Some(a), Some(b)) => a.state_bits_equal(b),
                    _ => false,
                })
            && self.lowest_freq_input_factor.to_bits() == other.lowest_freq_input_factor.to_bits()
            && self.lowest_freq_value_factor.to_bits() == other.lowest_freq_value_factor.to_bits()
    }

    /// Numeric sampling shares the previously bit-qualified Perlin loop.
    /// This does not itself establish the registered seed constructor.
    #[must_use]
    #[inline]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        sample_perlin_parts(
            &self.amplitudes,
            &self.octaves,
            self.lowest_freq_input_factor,
            self.lowest_freq_value_factor,
            [x, y, z],
        )
    }
}

/// The two *distinct* immutable Perlin branches of an observed `NormalNoise`.
#[derive(Clone, Debug)]
pub struct RegisteredNormalObserved262 {
    first: RegisteredPerlinObserved262,
    second: RegisteredPerlinObserved262,
    value_factor: f64,
}

impl RegisteredNormalObserved262 {
    /// Retain two complete independently prepared branches, no RNG sharing.
    ///
    /// # Errors
    /// Returns a nonfinite-state error for an invalid observed normal factor.
    pub fn from_observed_parts(
        first: RegisteredPerlinObserved262,
        second: RegisteredPerlinObserved262,
        value_factor: f64,
    ) -> Result<Self, RegisteredNoiseStateError262> {
        if !value_factor.is_finite() {
            return Err(RegisteredNoiseStateError262::NonFiniteNumericState);
        }
        Ok(Self {
            first,
            second,
            value_factor,
        })
    }

    /// Verify all retained sampler state, including signed floating-point zeros.
    #[must_use]
    pub fn state_bits_equal(&self, other: &Self) -> bool {
        self.first.state_bits_equal(&other.first)
            && self.second.state_bits_equal(&other.second)
            && self.value_factor.to_bits() == other.value_factor.to_bits()
    }

    /// Exact ordered normal sampling from two separately retained Perlin states.
    #[must_use]
    #[inline]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let first_value = self.first.sample(x, y, z);
        let second_value = self.second.sample(
            x * NORMAL_SECOND_INPUT_MULTIPLIER,
            y * NORMAL_SECOND_INPUT_MULTIPLIER,
            z * NORMAL_SECOND_INPUT_MULTIPLIER,
        );
        (first_value + second_value) * self.value_factor
    }
}

/// Borrowed, scale-prepared scalar density leaf for observed stock-shaped state.
/// Construct it once per profile/key, not once per block.
#[derive(Clone, Copy, Debug)]
pub struct RegisteredNoiseDensityObserved262<'a> {
    noise: &'a RegisteredNormalObserved262,
    xz_scale: f64,
    y_scale: f64,
}

impl<'a> RegisteredNoiseDensityObserved262<'a> {
    /// One constant-time borrow; scale lookup moves out of the sampling loop.
    #[must_use]
    pub const fn new(noise: &'a RegisteredNormalObserved262, scale: DirectNoiseScale262) -> Self {
        let (xz_scale, y_scale) = scale.factors();
        Self {
            noise,
            xz_scale,
            y_scale,
        }
    }

    /// Integer block coordinate -> double -> scale -> normal sampler.
    #[must_use]
    #[inline]
    pub fn sample_block(&self, x: i32, y: i32, z: i32) -> f64 {
        self.noise.sample(
            f64::from(x) * self.xz_scale,
            f64::from(y) * self.y_scale,
            f64::from(z) * self.xz_scale,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::improved_noise_262::LegacyBits;

    const GOLDEN: &str = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/tests/data/density_noise_direct_26_2_rawbits.txt"
    ));
    const SEEDS: [u64; 5] = [0, 1, u64::MAX, 0x8000_0000_0000_0000, 0x9e37_79b9_7f4a_7c15];
    const SCALES: [DirectNoiseScale262; 3] = [
        DirectNoiseScale262::Unit,
        DirectNoiseScale262::QuarterHorizontal,
        DirectNoiseScale262::QuarterHorizontalHalfVertical,
    ];
    const Y: [i32; 32] = [
        -4096, -65, -64, -63, -31, -30, -29, -1, 0, 1, 15, 16, 17, 18, 63, 64, 127, 128, 255, 256,
        318, 319, 320, 321, 1024, -1024, -384, -320, 319, -64, 17, 320,
    ];

    fn perlin(factory: u64) -> RegisteredPerlinObserved262 {
        let mut slots = Vec::with_capacity(4);
        for i in 0_i32..4 {
            slots.push(if i == 1 {
                None
            } else {
                Some(ImprovedNoise262::from_legacy_positional_octave(
                    factory,
                    -3 + i,
                ))
            });
        }
        RegisteredPerlinObserved262::from_observed_parts(
            -3,
            vec![1.0, 0.0, 0.5, 1.0].into_boxed_slice(),
            slots.into_boxed_slice(),
            f64::from_bits(0x3fc0_0000_0000_0000),
            f64::from_bits(0x3fe1_1111_1111_1111),
        )
        .expect("independently observed direct seed layout")
    }

    fn normal(seed: u64) -> RegisteredNormalObserved262 {
        let mut rng = LegacyBits::new(seed);
        let first = perlin(rng.next_long());
        let second = perlin(rng.next_long());
        RegisteredNormalObserved262::from_observed_parts(
            first,
            second,
            f64::from_bits(0x3ff5_5555_5555_5555),
        )
        .expect("finite direct observed NormalNoise factor")
    }

    fn position(j: usize) -> (i32, i32, i32) {
        let i = i32::try_from(j).expect("32 samples");
        let x = (if i % 2 == 0 { 33_554_432 } else { -33_554_432 }) + 13 * i;
        let z = (if i % 3 == 0 { 17 * i } else { -17 * i }) - 16;
        (x, Y[j], z)
    }

    #[test]
    fn all_480_independent_direct_seed_bits_match_through_bounded_observed_state() {
        let lines: Vec<_> = GOLDEN
            .lines()
            .filter(|line| !line.starts_with('#'))
            .collect();
        assert_eq!(lines.len(), 15);
        for (scale_index, scale) in SCALES.iter().enumerate() {
            for (seed_index, seed) in SEEDS.iter().enumerate() {
                let noise = normal(*seed);
                let density = RegisteredNoiseDensityObserved262::new(&noise, *scale);
                let source = lines[scale_index * 5 + seed_index];
                assert_eq!(source.len(), 512);
                for j in 0..32 {
                    let expected = u64::from_str_radix(&source[j * 16..(j + 1) * 16], 16)
                        .expect("frozen 64-bit hex");
                    let (x, y, z) = position(j);
                    assert_eq!(
                        density.sample_block(x, y, z).to_bits(),
                        expected,
                        "observed dynamic state scale={scale_index} seed={seed_index} point={j}"
                    );
                }
            }
        }
    }

    #[test]
    fn bound_validation_is_lossless_and_never_pads_or_truncates() {
        let none = || Vec::<Option<ImprovedNoise262>>::new().into_boxed_slice();
        assert!(matches!(
            RegisteredPerlinObserved262::from_observed_parts(
                0,
                Vec::new().into_boxed_slice(),
                none(),
                1.0,
                1.0
            ),
            Err(RegisteredNoiseStateError262::InvalidOctaveCount)
        ));
        assert!(matches!(
            RegisteredPerlinObserved262::from_observed_parts(
                0,
                vec![0.0; 65].into_boxed_slice(),
                vec![None; 65].into_boxed_slice(),
                1.0,
                1.0
            ),
            Err(RegisteredNoiseStateError262::InvalidOctaveCount)
        ));
        assert!(matches!(
            RegisteredPerlinObserved262::from_observed_parts(
                0,
                vec![0.0; 2].into_boxed_slice(),
                vec![None; 1].into_boxed_slice(),
                1.0,
                1.0
            ),
            Err(RegisteredNoiseStateError262::OctaveLengthMismatch)
        ));
        assert!(matches!(
            RegisteredPerlinObserved262::from_observed_parts(
                i32::MAX,
                vec![0.0; 2].into_boxed_slice(),
                vec![None; 2].into_boxed_slice(),
                1.0,
                1.0
            ),
            Err(RegisteredNoiseStateError262::OctaveIndexOverflow)
        ));
        assert!(matches!(
            RegisteredPerlinObserved262::from_observed_parts(
                0,
                vec![f64::NAN].into_boxed_slice(),
                vec![None].into_boxed_slice(),
                1.0,
                1.0
            ),
            Err(RegisteredNoiseStateError262::NonFiniteNumericState)
        ));
        assert!(matches!(
            RegisteredNormalObserved262::from_observed_parts(perlin(1), perlin(2), f64::INFINITY),
            Err(RegisteredNoiseStateError262::NonFiniteNumericState)
        ));
        let a = normal(1);
        assert!(a.state_bits_equal(&normal(1)));
        assert!(!a.state_bits_equal(&normal(2)));
    }

    #[test]
    fn wide_sparse_observed_state_is_retained_without_four_slot_truncation() {
        let noise = RegisteredPerlinObserved262::from_observed_parts(
            -8,
            vec![1.0, 0.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0].into_boxed_slice(),
            vec![
                Some(ImprovedNoise262::new(1)),
                None,
                None,
                None,
                Some(ImprovedNoise262::new(2)),
                None,
                Some(ImprovedNoise262::new(3)),
                None,
            ]
            .into_boxed_slice(),
            0.003_906_25,
            0.5,
        )
        .expect("valid eight-slot observation");
        assert_eq!(noise.first_octave(), -8);
        assert_eq!(noise.octave_count(), 8);
        assert!(noise.sample(1.0, 2.0, 3.0).is_finite());
        assert!(noise.state_bits_equal(&noise.clone()));
    }
}
