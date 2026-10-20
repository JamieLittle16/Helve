//! Source-free, exact-JVM-vector-qualified *direct-seeded* 26.2 noise-density leaf.
//!
//! This borrows a caller-owned NormalNoise262 and executes the three **observed**
//! DensityFunctions$Noise.compute xz/y scaling profiles at integer block XYZ.
//! The parent noise may be constructed only by the separately qualified
//! NormalNoise262::from_direct_seed_observed_profile (or observed numeric state).
//!
//! NO RandomState, NoiseRouter, registry, world-seed or production permission is
//! inferred from this 480-vector direct-seeded observation. The COLD sampler
//! allocates nothing and never owns a chunk, world, packet or mutable cache.

use crate::perlin_normal_262::NormalNoise262;

/// Only the three scale pairs exercised in the pinned 26.2 official JVM oracle.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DirectNoiseScale262 {
    /// Horizontal and vertical scales (1, 1).
    Unit,
    /// Horizontal and vertical scales (0.25, 1).
    QuarterHorizontal,
    /// Horizontal and vertical scales (0.25, 0.5).
    QuarterHorizontalHalfVertical,
}

impl DirectNoiseScale262 {
    #[inline]
    pub(crate) const fn factors(self) -> (f64, f64) {
        match self {
            Self::Unit => (1.0, 1.0),
            Self::QuarterHorizontal => (0.25, 1.0),
            Self::QuarterHorizontalHalfVertical => (0.25, 0.5),
        }
    }
}

/// Rejected block-coordinate lattice; output remains unchanged on error.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DirectNoiseCellError262 {
    /// One of the 16 sampled integer coordinates would exceed `i32::MAX`.
    BlockCoordinateOverflow,
}

/// Immutable borrowed direct-noise density leaf, with scale selection off path.
#[derive(Clone, Copy, Debug)]
pub struct DirectNoiseDensity262<'a> {
    noise: &'a NormalNoise262,
    xz_scale: f64,
    y_scale: f64,
}

impl<'a> DirectNoiseDensity262<'a> {
    /// Borrow a retained noise sampler; never clone its octave tables per cell.
    #[must_use]
    pub const fn new(noise: &'a NormalNoise262, profile: DirectNoiseScale262) -> Self {
        let (xz_scale, y_scale) = profile.factors();
        Self {
            noise,
            xz_scale,
            y_scale,
        }
    }

    /// Evaluate the real 26.2 single-point density **candidate**, in the
    /// measured integer block -> f64 -> scale -> `NormalNoise` operation order.
    /// No unchecked i32 coordinate arithmetic, heap access or double rounding.
    #[must_use]
    #[inline]
    pub fn sample_block(&self, block_x: i32, block_y: i32, block_z: i32) -> f64 {
        self.noise.sample(
            f64::from(block_x) * self.xz_scale,
            f64::from(block_y) * self.y_scale,
            f64::from(block_z) * self.xz_scale,
        )
    }

    /// Fill a 16×16 Z-major plane without allocations; precompute horizontal
    /// scaled axes once, then use the existing exact-bit coherent noise kernel.
    ///
    /// # Errors
    /// Coordinate overflow is rejected **before any output write**.
    pub fn sample_plane_16x16(
        &self,
        origin_x: i32,
        block_y: i32,
        origin_z: i32,
        output: &mut [f64; 256],
    ) -> Result<(), DirectNoiseCellError262> {
        let (x_axis, z_axis) = self.axes_16(origin_x, origin_z)?;
        self.noise.sample_axis_grid_16x16(
            &x_axis,
            f64::from(block_y) * self.y_scale,
            &z_axis,
            output,
        );
        Ok(())
    }

    /// Fill a caller-owned 16³ Y/Z/X cell. The X/Z axes are prepared once
    /// per cell, not once per plane; the normal sampler retains its two
    /// independent octave families without transient heap allocations.
    ///
    /// # Errors
    /// All axis bounds are validated before the first output write.
    ///
    /// # Panics
    /// Only if a chunk of a fixed 4096-value array divided into sixteen
    /// 256-value planes is not exactly 256 values, which is impossible.
    pub fn sample_cell_16x16x16(
        &self,
        origin_x: i32,
        origin_y: i32,
        origin_z: i32,
        output: &mut [f64; 4096],
    ) -> Result<(), DirectNoiseCellError262> {
        origin_y
            .checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        let (x_axis, z_axis) = self.axes_16(origin_x, origin_z)?;
        for (dy, plane) in (0_i32..16).zip(output.chunks_exact_mut(256)) {
            self.noise.sample_axis_grid_16x16(
                &x_axis,
                f64::from(origin_y + dy) * self.y_scale,
                &z_axis,
                plane
                    .try_into()
                    .expect("each exact 4096/256 chunk is a 256-element plane"),
            );
        }
        Ok(())
    }

    #[inline]
    fn axes_16(
        &self,
        origin_x: i32,
        origin_z: i32,
    ) -> Result<([f64; 16], [f64; 16]), DirectNoiseCellError262> {
        origin_x
            .checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        origin_z
            .checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        let mut x_axis = [0.0_f64; 16];
        let mut z_axis = [0.0_f64; 16];
        for local in 0_u8..16 {
            let index = usize::from(local);
            x_axis[index] = f64::from(origin_x + i32::from(local)) * self.xz_scale;
            z_axis[index] = f64::from(origin_z + i32::from(local)) * self.xz_scale;
        }
        Ok((x_axis, z_axis))
    }
}
