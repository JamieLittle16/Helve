//! Source-free, JVM-raw-bit-matched Minecraft Java 26.2 density *primitive* candidates.
//!
//! Official 26.2 primitive `DensityFunction.compute` output captures match
//! these exact integer-block-Y operations for four frozen parameter profiles
//! and 640 observations. This is a bounded differential verification,
//! **not** independent source VAR/SEM admission or a complete router.
//!
//! Keep the integer block context separate from the existing floating-point
//! noise/arithmetic DAG: silently casting fractional Y to an integer would
//! create an unqualified and potentially wrong vanilla sampling context.
//! Construction occurs off the COLD hot path, and sampling allocates nothing.

/// Explicit primitive density evaluator with an integer block-position context.
///
/// Construction precomputes invariant differences, but DOES NOT replace the
/// division by an inverse multiplication: that changes raw floating-point bits.
#[derive(Clone, Copy, Debug)]
pub enum DensityPrimitive262 {
    /// Return exact input IEEE-754 bits, including negative zero.
    Constant(f64),
    /// Y-clamped linear gradient with caller-validated bounds and finite values.
    YClampedGradient {
        from_y: i32,
        from_value: f64,
        span: f64,
        delta_value: f64,
    },
}

/// Unsupported input to this deliberately narrow 26.2 primitive candidate.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DensityPrimitiveError262 {
    /// Clamped gradients require a strictly increasing integer Y interval.
    InvalidYInterval,
    /// The primitive candidate only accepts finite endpoint values/differences.
    NonFiniteValue,
    /// A 16-high COLD cell would exceed i32 block-position bounds.
    CellYOverflow,
}

impl DensityPrimitive262 {
    /// Construct an exact-bit constant density primitive.
    #[must_use]
    pub const fn constant(value: f64) -> Self {
        Self::Constant(value)
    }

    /// Construct a clamped linear Y gradient in the observed official 26.2 order.
    ///
    /// These restrictions are Helve's conservative construction policy, not
    /// a claim about all possible 26.2 factory inputs or validation rules.
    ///
    /// # Errors
    /// Rejects non-increasing integer Y bounds and non-finite endpoint values
    /// or endpoint-value differences.
    pub fn y_clamped_gradient(
        from_y: i32,
        to_y: i32,
        from_value: f64,
        to_value: f64,
    ) -> Result<Self, DensityPrimitiveError262> {
        if from_y >= to_y {
            return Err(DensityPrimitiveError262::InvalidYInterval);
        }
        let delta_value = to_value - from_value;
        if !from_value.is_finite() || !to_value.is_finite() || !delta_value.is_finite() {
            return Err(DensityPrimitiveError262::NonFiniteValue);
        }
        Ok(Self::YClampedGradient {
            from_y,
            from_value,
            span: f64::from(to_y) - f64::from(from_y),
            delta_value,
        })
    }

    /// Evaluate at the **integer block Y**, independent of X/Z or seed.
    ///
    /// The order matters for non-dyadic t: subtract, divide, clamp, then
    /// multiply and add without fusing or algebraically rearranging.
    #[must_use]
    #[inline]
    pub fn sample_block_y(&self, block_y: i32) -> f64 {
        match *self {
            Self::Constant(value) => value,
            Self::YClampedGradient {
                from_y,
                from_value,
                span,
                delta_value,
            } => {
                let progress = ((f64::from(block_y) - f64::from(from_y)) / span).clamp(0.0, 1.0);
                from_value + progress * delta_value
            }
        }
    }

    /// Fill a Z-major horizontal 16×16 plane; the primitive is X/Z invariant.
    /// No allocation, worker ownership, runtime registries or copying.
    #[inline]
    pub fn sample_plane_16x16(&self, block_y: i32, output: &mut [f64; 256]) {
        output.fill(self.sample_block_y(block_y));
    }

    /// Fill a caller-owned 16³ cell in Y/Z/X order (one evaluated Y per plane).
    ///
    /// This avoids 4096 redundant evaluations of a Y-only function.
    /// No heap allocation or secondary chunk representation is introduced.
    ///
    /// # Errors
    /// Rejects any origin whose highest sampled block Y would overflow i32.
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
