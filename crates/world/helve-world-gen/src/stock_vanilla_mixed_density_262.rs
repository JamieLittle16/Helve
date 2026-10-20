//! Exact official 26.2 JVM-output-qualified mixed stock noise/density path.
//!
//! This is NOT the explicitly eager DAG in `stock_density_program_262`.
//! 1,920 independently captured real-stock `DensityFunctions.add/mul`
//! observations distinguish two runtime factory/delegate families:
//! `Ap2` for dynamic Noise/YClampedGradient and `MulOrAdd` for
//! Noise/Constant, with the latter reaching `PureTransformer.compute`.
//! The former returned +0 for a +0 **left** operand when multiplying a
//! negative right operand at Y=128; constant multiplication instead
//! preserves ordinary IEEE signed-zero multiplication.
//!
//! The typed boundary intentionally covers ONLY one registered noise leaf
//! and one Y-only primitive. Neither an arbitrary density graph nor
//! complete vanilla short-circuit semantics is source-reviewed/admitted.
//! This module owns neither registry, world, chunk, cache nor packet.

use crate::density_noise_direct_262::DirectNoiseCellError262;
use crate::density_primitives_262::DensityPrimitive262;
use crate::registered_noise_state_262::RegisteredNoiseDensityObserved262;

/// Which observed stock `DensityFunctions` factory operation to select.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StockVanillaMixedOp262 {
    /// Vanilla `DensityFunctions.add`.
    Add,
    /// Vanilla `DensityFunctions.mul`.
    Multiply,
}

/// The original factory's left-to-right input order, not a commuted shortcut.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StockVanillaMixedOrder262 {
    /// The registered noise is the left operand.
    NoiseFirst,
    /// The integer-Y primitive is the left operand.
    PrimitiveFirst,
}

#[derive(Clone, Copy, Debug)]
enum Delegate262 {
    Ap2Add,
    Ap2Multiply,
    MulOrAddAdd,
    MulOrAddMultiply,
}

/// Immutable typed composition of one registered noise and one Y-only primitive.
///
/// Select the observed JVM delegate class once at construction, using the
/// primitive's type, without a per-block dynamic virtual call or allocation.
#[derive(Clone, Copy, Debug)]
pub struct StockVanillaMixedDensity262<'a> {
    noise: RegisteredNoiseDensityObserved262<'a>,
    primitive: DensityPrimitive262,
    order: StockVanillaMixedOrder262,
    delegate: Delegate262,
}

impl<'a> StockVanillaMixedDensity262<'a> {
    /// Construct a bounded, JVM-output-qualified stock-mixed density candidate.
    ///
    /// The observed 26.2 factory uses `Ap2` for nonconstant gradient
    /// compositions and `MulOrAdd` for constant compositions.
    #[must_use]
    pub const fn new(
        noise: RegisteredNoiseDensityObserved262<'a>,
        primitive: DensityPrimitive262,
        op: StockVanillaMixedOp262,
        order: StockVanillaMixedOrder262,
    ) -> Self {
        let constant = matches!(primitive, DensityPrimitive262::Constant(_));
        let delegate = match (constant, op) {
            (false, StockVanillaMixedOp262::Add) => Delegate262::Ap2Add,
            (false, StockVanillaMixedOp262::Multiply) => Delegate262::Ap2Multiply,
            (true, StockVanillaMixedOp262::Add) => Delegate262::MulOrAddAdd,
            (true, StockVanillaMixedOp262::Multiply) => Delegate262::MulOrAddMultiply,
        };
        Self {
            noise,
            primitive,
            order,
            delegate,
        }
    }

    #[inline]
    fn combine_observed(self, noise: f64, primitive: f64) -> f64 {
        let (left, right) = match self.order {
            StockVanillaMixedOrder262::NoiseFirst => (noise, primitive),
            StockVanillaMixedOrder262::PrimitiveFirst => (primitive, noise),
        };
        match self.delegate {
            Delegate262::Ap2Add | Delegate262::MulOrAddAdd => left + right,
            Delegate262::MulOrAddMultiply => left * right,
            Delegate262::Ap2Multiply => {
                if left.to_bits() == 0.0_f64.to_bits() {
                    0.0
                } else {
                    left * right
                }
            }
        }
    }

    /// Evaluate at integer Minecraft block coordinates.
    ///
    /// The observed dynamic-positive-zero path can skip the noise leaf
    /// entirely if the Y-gradient is first and evaluates to +0.
    #[must_use]
    #[inline]
    pub fn sample_block(&self, x: i32, y: i32, z: i32) -> f64 {
        let first_y = self.primitive.sample_block_y(y);
        if matches!(self.delegate, Delegate262::Ap2Multiply)
            && matches!(self.order, StockVanillaMixedOrder262::PrimitiveFirst)
            && first_y.to_bits() == 0.0_f64.to_bits()
        {
            return 0.0;
        }
        self.combine_observed(self.noise.sample_block(x, y, z), first_y)
    }

    /// Evaluate a caller-owned, Z/X ordered 16×16 plane with the coherent
    /// noise kernel; keep the Y-only value invariant across that plane.
    ///
    /// # Errors
    /// Any overflowing horizontal block coordinate rejects before writing.
    pub fn sample_plane_16x16(
        &self,
        x: i32,
        y: i32,
        z: i32,
        output: &mut [f64; 256],
    ) -> Result<(), DirectNoiseCellError262> {
        x.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        z.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;

        let value = self.primitive.sample_block_y(y);
        if matches!(self.delegate, Delegate262::Ap2Multiply)
            && matches!(self.order, StockVanillaMixedOrder262::PrimitiveFirst)
            && value.to_bits() == 0.0_f64.to_bits()
        {
            output.fill(0.0);
            return Ok(());
        }
        self.noise.sample_plane_16x16(x, y, z, output)?;
        for noise in output {
            *noise = self.combine_observed(*noise, value);
        }
        Ok(())
    }

    /// Evaluate a caller-owned Y/Z/X 16×16×16 cell; sample registered noise
    /// as one bit-exact coherent volume and compute only 16 gradient values.
    ///
    /// The batch path currently samples every Y plane; its per-plane
    /// composition reproduces the observed +0 skip result without claiming
    /// a Java-equivalent evaluation *trace*.
    ///
    /// # Errors
    /// All integer block-coordinate overflow rejects before any output write.
    ///
    /// # Panics
    /// Only if the fixed 4096-value buffer does not split into 16 planes.
    pub fn sample_cell_16x16x16(
        &self,
        x: i32,
        y: i32,
        z: i32,
        output: &mut [f64; 4096],
    ) -> Result<(), DirectNoiseCellError262> {
        x.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        y.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        z.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;

        self.noise.sample_cell_16x16x16(x, y, z, output)?;
        for (dy, plane) in (0_i32..16).zip(output.chunks_exact_mut(256)) {
            let value = self.primitive.sample_block_y(y + dy);
            for noise in plane {
                *noise = self.combine_observed(*noise, value);
            }
        }
        Ok(())
    }
}
