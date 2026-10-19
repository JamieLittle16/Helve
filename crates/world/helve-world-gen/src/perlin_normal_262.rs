//! Source-free **observed-state** Minecraft Java 26.2 Perlin/Normal sampler.
//!
//! Four explicit octave slots, weights and Java float operations are driven by
//! the independently supplied official-runtime state snapshots. This module
//! intentionally does NOT claim the full seed-to-constructor algorithm:
//! `from_observed_parts` requires the actual octave permutations and offsets.
//! Source/VAR/SEM admission and normal terrain publication remain closed.

use crate::improved_noise_262::ImprovedNoise262;

/// Exactly the four octave slots in the explicitly pinned fixture profile.
/// A zero-amplitude absent octave stays absent, rather than consuming RNG.
pub const OBSERVED_OCTAVES_262: usize = 4;

/// The modulus used by the evaluated source-candidate coordinate wrapping
/// rule. The official output corpus contains large coordinates that reject
/// an otherwise equivalent implementation without this operation.
const WRAP_PERIOD: f64 = 33_554_432.0;

/// `NormalNoise`'s second Perlin family samples a slightly expanded position.
/// The number is an evaluated output-matching candidate, not an independent
/// declaration that every target-version constructor has this scaling.
const NORMAL_SECOND_INPUT_MULTIPLIER: f64 = 1.018_126_888_217_522_7;

/// Implements the Java-style rounded-floor rule used by the candidate wrap.
/// Nonfinite / far-out-of-range arguments are **not** admitted by this stage:
/// corpus qualification currently covers only finite 26.2 reference points.
#[inline]
#[expect(
    clippy::cast_possible_truncation,
    clippy::cast_precision_loss,
    reason = "the candidate Java long floor deliberately truncates the f64"
)]
fn wrap_coordinate(x: f64) -> f64 {
    let scaled = x / WRAP_PERIOD + 0.5;
    let integer = scaled as i64;
    let rounded = if scaled < integer as f64 {
        integer.wrapping_sub(1)
    } else {
        integer
    };
    x - (rounded as f64) * WRAP_PERIOD
}

/// A frozen Perlin family instance from its full **observed** JVM state.
///
/// Exactly four octave slots, an explicit four-entry amplitude vector, and
/// two JVM-observed scalar factors. This is a genuine multi-octave sampler
/// evaluator, not a constructed `RandomSource.create(seed)` clone.
#[derive(Clone, Debug)]
pub struct PerlinNoise262 {
    first_octave: i32,
    amplitudes: [f64; OBSERVED_OCTAVES_262],
    octaves: [Option<ImprovedNoise262>; OBSERVED_OCTAVES_262],
    lowest_freq_input_factor: f64,
    lowest_freq_value_factor: f64,
}

impl PerlinNoise262 {
    /// Construct from checked source-free numeric observations.
    ///
    /// The owner of these values must have independently bound them to an
    /// official 26.2 runtime and exact sampling profile. This constructor
    /// does *not* infer the permutations from a raw world or random seed.
    #[must_use]
    pub const fn from_observed_parts(
        first_octave: i32,
        amplitudes: [f64; OBSERVED_OCTAVES_262],
        octaves: [Option<ImprovedNoise262>; OBSERVED_OCTAVES_262],
        lowest_freq_input_factor: f64,
        lowest_freq_value_factor: f64,
    ) -> Self {
        Self {
            first_octave,
            amplitudes,
            octaves,
            lowest_freq_input_factor,
            lowest_freq_value_factor,
        }
    }

    /// The first source-observed octave position; informational for this
    /// four-slot state-backed evaluator, not a seed-construction recipe.
    #[must_use]
    pub const fn first_octave(&self) -> i32 {
        self.first_octave
    }

    /// Evaluate the observed 3D Perlin profile in strict Java operation order.
    /// The inactive octave contributes nothing, but advances both frequency
    /// multipliers. No reassociation, fast math, or FMA is permitted.
    #[must_use]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let mut total = 0.0_f64;
        let mut input_factor = self.lowest_freq_input_factor;
        let mut value_factor = self.lowest_freq_value_factor;
        for (index, octave) in self.octaves.iter().enumerate() {
            if let Some(noise) = octave {
                let value = noise.sample(
                    wrap_coordinate(x * input_factor),
                    wrap_coordinate(y * input_factor),
                    wrap_coordinate(z * input_factor),
                );
                total += self.amplitudes[index] * value * value_factor;
            }
            input_factor *= 2.0;
            value_factor /= 2.0;
        }
        total
    }

    /// Sample every product of 16 caller-provided X and Z coordinates,
    /// maintaining independent scalar input multiplication and wrap order.
    /// Writes Z-major results with only fixed-size stack scratch.
    pub fn sample_axis_grid_16x16(
        &self,
        x_axis: &[f64; 16],
        y: f64,
        z_axis: &[f64; 16],
        output: &mut [f64; 256],
    ) {
        output.fill(0.0);
        let mut input_factor = self.lowest_freq_input_factor;
        let mut value_factor = self.lowest_freq_value_factor;
        let mut scaled_x = [0.0_f64; 16];
        let mut scaled_z = [0.0_f64; 16];
        let mut contributions = [0.0_f64; 256];

        for (index, octave) in self.octaves.iter().enumerate() {
            if let Some(noise) = octave {
                for axis in 0..16 {
                    scaled_x[axis] = wrap_coordinate(x_axis[axis] * input_factor);
                    scaled_z[axis] = wrap_coordinate(z_axis[axis] * input_factor);
                }
                noise.sample_axis_grid_16x16(
                    &scaled_x,
                    wrap_coordinate(y * input_factor),
                    &scaled_z,
                    &mut contributions,
                );
                for (out, sample) in output.iter_mut().zip(contributions.iter().copied()) {
                    *out += self.amplitudes[index] * sample * value_factor;
                }
            }
            input_factor *= 2.0;
            value_factor /= 2.0;
        }
    }

    /// Evaluate 256 consecutive X/Z positions with the exact per-position
    /// scalar coordinate arithmetic, without constructing temporary chunks.
    pub fn sample_plane_16x16(
        &self,
        origin_x: f64,
        y: f64,
        origin_z: f64,
        output: &mut [f64; 256],
    ) {
        let mut x_axis = [0.0_f64; 16];
        let mut z_axis = [0.0_f64; 16];
        for local in 0_u8..16 {
            x_axis[usize::from(local)] = origin_x + f64::from(local);
            z_axis[usize::from(local)] = origin_z + f64::from(local);
        }
        self.sample_axis_grid_16x16(&x_axis, y, &z_axis, output);
    }
}

/// Two distinct, source-observed Perlin instances with the measured normal
/// value multiplier. The second input-coordinate scaling is deliberately
/// applied independently to each axis, preserving Java rounding.
#[derive(Clone, Debug)]
pub struct NormalNoise262 {
    first: PerlinNoise262,
    second: PerlinNoise262,
    value_factor: f64,
}

impl NormalNoise262 {
    /// Accept the two complete observed Perlin instances; never share one
    /// sampler's permutation table in place of the second.
    #[must_use]
    pub const fn from_observed_parts(
        first: PerlinNoise262,
        second: PerlinNoise262,
        value_factor: f64,
    ) -> Self {
        Self {
            first,
            second,
            value_factor,
        }
    }

    /// Evaluate the observed normal-noise candidate in exact ordered sums.
    #[must_use]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let first_value = self.first.sample(x, y, z);
        let second_value = self.second.sample(
            x * NORMAL_SECOND_INPUT_MULTIPLIER,
            y * NORMAL_SECOND_INPUT_MULTIPLIER,
            z * NORMAL_SECOND_INPUT_MULTIPLIER,
        );
        (first_value + second_value) * self.value_factor
    }

    /// Return 256 coherent normal-noise samples, using each branch's exact
    /// prepared-axis Perlin implementation and a caller-owned output buffer.
    pub fn sample_plane_16x16(
        &self,
        origin_x: f64,
        y: f64,
        origin_z: f64,
        output: &mut [f64; 256],
    ) {
        let mut x_axis = [0.0_f64; 16];
        let mut z_axis = [0.0_f64; 16];
        for local in 0_u8..16 {
            x_axis[usize::from(local)] = origin_x + f64::from(local);
            z_axis[usize::from(local)] = origin_z + f64::from(local);
        }
        self.first
            .sample_axis_grid_16x16(&x_axis, y, &z_axis, output);
        for value in &mut x_axis {
            *value *= NORMAL_SECOND_INPUT_MULTIPLIER;
        }
        for value in &mut z_axis {
            *value *= NORMAL_SECOND_INPUT_MULTIPLIER;
        }
        let mut secondary = [0.0_f64; 256];
        self.second.sample_axis_grid_16x16(
            &x_axis,
            y * NORMAL_SECOND_INPUT_MULTIPLIER,
            &z_axis,
            &mut secondary,
        );
        for (primary, followup) in output.iter_mut().zip(secondary.iter().copied()) {
            *primary = (*primary + followup) * self.value_factor;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::wrap_coordinate;

    #[test]
    fn finite_wrap_is_periodic_at_exact_modulus() {
        assert_eq!(wrap_coordinate(0.0).to_bits(), 0.0_f64.to_bits());
        assert_eq!(wrap_coordinate(33_554_432.0).to_bits(), 0.0_f64.to_bits());
        assert_eq!(wrap_coordinate(-33_554_432.0).to_bits(), 0.0_f64.to_bits());
    }
}
