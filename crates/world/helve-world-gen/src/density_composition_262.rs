//! Observed official Minecraft Java 26.2 two-primitive density composition.
//!
//! Only the frozen eight factory profiles and their integer block-Y contexts
//! have independent JVM output evidence (1,280 raw-bit observations).
//! These operations are NOT a complete source-reviewed DensityFunctions API,
//! a world-seed-backed NoiseRouter, or a production-admitted chunk generator.
//!
//! Do not reuse generic floating-coordinate DensityKernel262 arithmetic here.
//! The official nonconstant multiplication has an observed +0 exception that
//! differs from IEEE multiplication at Y=128; constant-factor multiplication
//! in the same capture instead retains IEEE signed-zero multiplication.

use crate::density_primitives_262::{DensityPrimitive262, DensityPrimitiveError262};

/// Source-free JVM-output-qualified *candidate* composition of exactly two
/// immutable density primitives, evaluated at integer Minecraft block Y.
///
/// Both addition and multiplication have source-locked JVM-observed shape
/// distinctions: `Ap2.compute` handles two nonconstant primitives;
/// `MulOrAdd` reaches `PureTransformer.compute` with a constant operand.
/// Those identities were observed via official reflection and Atlas
/// fingerprints, NOT independently source-reviewed or production-admitted.
#[derive(Clone, Copy, Debug)]
pub enum DensityComposition262 {
    /// Official `DensityFunctions$Ap2.compute` path: two nonconstant leaves.
    AddFunctions {
        left: DensityPrimitive262,
        right: DensityPrimitive262,
    },
    /// Official `DensityFunctions$MulOrAdd` path, reached through
    /// `PureTransformer.compute` for a constant-factor addition.
    AddWithConstant {
        left: DensityPrimitive262,
        right: DensityPrimitive262,
    },
    /// Observed `MulOrAdd` constant-factor composition; preserves signed zeros.
    MultiplyWithConstant {
        left: DensityPrimitive262,
        right: DensityPrimitive262,
    },
    /// Observed `Ap2.compute` nonconstant pair: return positive zero for a +0 left
    /// operand before evaluating the second operand.
    MultiplyFunctions {
        left: DensityPrimitive262,
        right: DensityPrimitive262,
    },
}

impl DensityComposition262 {
    /// Construct a source-free qualified candidate for a two-primitive add.
    #[must_use]
    pub const fn add(left: DensityPrimitive262, right: DensityPrimitive262) -> Self {
        // The official 26.2 JVM class capture (2026-10-20) distinguishes
        // Ap2 from MulOrAdd/PureTransformer even for addition. Select
        // once at construction, not inside the sampling hot path.
        if matches!(left, DensityPrimitive262::Constant(_))
            || matches!(right, DensityPrimitive262::Constant(_))
        {
            Self::AddWithConstant { left, right }
        } else {
            Self::AddFunctions { left, right }
        }
    }

    /// Select the observed 26.2 multiplication behavior by primitive shape.
    ///
    /// This is intentionally **not** the blanket rule of the older generic
    /// eager DAG: the official JVM distinguishes multiplying two gradients
    /// from multiplying a gradient by a signed-zero constant.
    #[must_use]
    pub const fn multiply(left: DensityPrimitive262, right: DensityPrimitive262) -> Self {
        if matches!(left, DensityPrimitive262::Constant(_))
            || matches!(right, DensityPrimitive262::Constant(_))
        {
            Self::MultiplyWithConstant { left, right }
        } else {
            Self::MultiplyFunctions { left, right }
        }
    }

    /// Scalar evaluation with explicit left-operand-first arithmetic.
    /// No allocation, virtual call, registry or world-owner dependency.
    #[must_use]
    #[inline]
    pub fn sample_block_y(&self, block_y: i32) -> f64 {
        match *self {
            Self::AddFunctions { left, right } | Self::AddWithConstant { left, right } => {
                left.sample_block_y(block_y) + right.sample_block_y(block_y)
            }
            Self::MultiplyWithConstant { left, right } => {
                left.sample_block_y(block_y) * right.sample_block_y(block_y)
            }
            Self::MultiplyFunctions { left, right } => {
                let first = left.sample_block_y(block_y);
                // Measured in the official two-gradient profile at Y=128:
                // +0 * negative is +0, NOT the IEEE -0. Only the observed
                // positive-zero input shape is specialised. Negative-zero
                // dynamic inputs, nonfinite inputs and arbitrary composed
                // graphs have not been source-reviewed or qualified.
                if first.to_bits() == 0.0_f64.to_bits() {
                    return 0.0;
                }
                first * right.sample_block_y(block_y)
            }
        }
    }

    /// Fill a caller-owned 16×16 horizontal plane with just one evaluation.
    #[inline]
    pub fn sample_plane_16x16(&self, block_y: i32, output: &mut [f64; 256]) {
        output.fill(self.sample_block_y(block_y));
    }

    /// Fill a caller-owned 16³ Y/Z/X cell using just 16 Y evaluations.
    ///
    /// # Errors
    /// Returns an error *before writing* if the highest block Y overflows.
    pub fn sample_cell_16x16x16(
        &self,
        origin_y: i32,
        output: &mut [f64; 4096],
    ) -> Result<(), DensityPrimitiveError262> {
        origin_y
            .checked_add(15)
            .ok_or(DensityPrimitiveError262::CellYOverflow)?;
        for (local_y, plane) in (0_i32..16).zip(output.chunks_exact_mut(256)) {
            plane.fill(self.sample_block_y(origin_y + local_y));
        }
        Ok(())
    }
}
