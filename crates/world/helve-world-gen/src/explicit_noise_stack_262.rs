//! Explicit, immutable multi-layer 26.2 candidate noise *mechanism*.
//!
//! This is **not** Minecraft's `PerlinNoise`, `NormalNoise` or
//! `DensityFunctions` contract. Their target-version seeding, octave
//! placement, input wrapping, weight factors and evaluation order still
//! require independent official 26.2 source review and output oracles.
//!
//! Rather, this type allows an explicitly specified sequence of weighted,
//! frequency-scaled `ImprovedNoise262` instances to reuse the exact-bit
//! 16×16 product-grid mechanism without allocating or using global caches.

use crate::improved_noise_262::ImprovedNoise262;

/// One explicitly configured candidate noise layer; no implicit seed
/// mixing, amplitude normalisation or target-version octave assumptions.
#[derive(Debug, Clone)]
pub struct ExplicitNoiseLayer262 {
    pub sampler: ImprovedNoise262,
    pub frequency: f64,
    pub weight: f64,
}

impl ExplicitNoiseLayer262 {
    /// Creates an explicit term without silently deriving octave parameters.
    #[must_use]
    pub const fn new(sampler: ImprovedNoise262, frequency: f64, weight: f64) -> Self {
        Self {
            sampler,
            frequency,
            weight,
        }
    }
}

/// Fixed-size, caller-ordered stack with no heap allocations or per-sample
/// mutability. `N=0` produces positive zero and is tested explicitly.
///
/// The evaluation contract is defined by `sample()`, not an assertion that
/// a particular Mojang octave construction uses these rules.
#[derive(Debug, Clone)]
pub struct ExplicitNoiseStack262<const N: usize> {
    layers: [ExplicitNoiseLayer262; N],
}

impl<const N: usize> ExplicitNoiseStack262<N> {
    /// Preserves the supplied order and all explicit frequencies/weights.
    #[must_use]
    pub const fn new(layers: [ExplicitNoiseLayer262; N]) -> Self {
        Self { layers }
    }

    /// Evaluate each term in order: independent coordinate scaling,
    /// scalar noise, multiplication by weight, then accumulation.
    ///
    /// No reassociation, zero-weight shortcut, fast math or FMA is permitted
    /// because each can change raw IEEE-754 output bits.
    #[must_use]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let mut sum = 0.0_f64;
        for layer in &self.layers {
            let sample = layer.sampler.sample(
                x * layer.frequency,
                y * layer.frequency,
                z * layer.frequency,
            );
            sum += sample * layer.weight;
        }
        sum
    }

    /// Evaluate the identical ordered stack on a 16×16 X/Z plane. The input
    /// to each scalar layer would be `(origin_x + local_x) * frequency`,
    /// **not** `origin_x * frequency + local_x * frequency`, because those
    /// two expressions can round differently.
    ///
    /// A single caller-supplied 256-element output is used as the
    /// accumulator. All temporary axes and contributions live on the stack.
    /// The result is bit-identical to calling `sample()` at each position.
    pub fn sample_plane_16x16(
        &self,
        origin_x: f64,
        y: f64,
        origin_z: f64,
        output: &mut [f64; 256],
    ) {
        output.fill(0.0);
        let mut x_axis = [0.0_f64; 16];
        let mut z_axis = [0.0_f64; 16];
        let mut contributions = [0.0_f64; 256];
        for layer in &self.layers {
            for offset in 0_u8..16 {
                let index = usize::from(offset);
                x_axis[index] = (origin_x + f64::from(offset)) * layer.frequency;
                z_axis[index] = (origin_z + f64::from(offset)) * layer.frequency;
            }
            layer.sampler.sample_axis_grid_16x16(
                &x_axis,
                y * layer.frequency,
                &z_axis,
                &mut contributions,
            );
            for (value, contribution) in output.iter_mut().zip(contributions.iter().copied()) {
                *value += contribution * layer.weight;
            }
        }
    }

    /// Number of compile-time fixed noise layers.
    #[must_use]
    pub const fn len(&self) -> usize {
        N
    }

    /// Whether there are no layers.
    #[must_use]
    pub const fn is_empty(&self) -> bool {
        N == 0
    }
}
