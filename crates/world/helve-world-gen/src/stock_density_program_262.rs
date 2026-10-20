//! COLD-validated, allocation-free mixed-density expression **substrate**.
//!
//! Its leaves are the existing independently bit-qualified stock registered
//! world-seed noise and integer-block-Y constant/clamped-gradient primitives.
//! Its arithmetic nodes are deliberately *explicit eager IEEE operations*:
//! mixing stock noise with primitives or composing arbitrary graph shapes is
//! NOT independently qualified as vanilla DensityFunctions / NoiseRouter.
//! In particular, the official 26.2 Ap2 multiply early-positive-zero rule
//! may differ from generic eager multiplication. No production authority.
//!
//! A maximum of 32 immutable nodes and fixed per-worker scratch bound hot-path
//! work. A single noise leaf or noise with one Y-only primitive gets an exact
//! coherent plane/cell path. Everything else uses ordered per-block evaluation.

use crate::density_noise_direct_262::DirectNoiseCellError262;
use crate::density_primitives_262::DensityPrimitive262;
use crate::registered_noise_state_262::RegisteredNoiseDensityObserved262;

/// One entry in a caller-constructed, index-validated COLD expression graph.
///
/// All dependencies must point strictly backwards; the final node is the
/// result. No implicit cache, source-router translation or node rewriting.
#[derive(Clone, Copy, Debug)]
pub enum StockDensityNode262<'a> {
    /// Integer-block-Y primitive from the independently observed 26.2 leaf.
    Primitive(DensityPrimitive262),
    /// Borrow one immutable, seed-derived, already bit-qualified normal noise.
    RegisteredNoise(RegisteredNoiseDensityObserved262<'a>),
    /// Explicit eager IEEE-754 addition in operand order.
    Add { left: usize, right: usize },
    /// Explicit eager IEEE-754 multiplication; **not** vanilla Ap2 short-circuit.
    Multiply { left: usize, right: usize },
}

/// COLD program validation errors; no runtime evaluation is attempted.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StockDensityProgramError262 {
    /// A program requires a final output node.
    Empty,
    /// More than 32 operations would exceed the bounded worker scratch.
    TooManyNodes,
    /// A dependency points forward or to itself, or outside the graph.
    InvalidDependency { node: usize, child: usize },
    /// A disconnected node would cause unnecessary work on the hot path.
    UnusedNode { node: usize },
}

#[derive(Clone, Copy, Debug)]
enum Arithmetic262 {
    Add,
    Multiply,
}

impl Arithmetic262 {
    #[inline]
    fn apply(self, left: f64, right: f64) -> f64 {
        match self {
            Self::Add => left + right,
            Self::Multiply => left * right,
        }
    }
}

/// Preselected specializations. No expensive tree shape matching per sample.
#[derive(Clone, Copy, Debug)]
enum SamplingPlan262<'a> {
    Generic,
    OnlyPrimitive(DensityPrimitive262),
    OnlyNoise(RegisteredNoiseDensityObserved262<'a>),
    NoiseAndPrimitive {
        noise: RegisteredNoiseDensityObserved262<'a>,
        primitive: DensityPrimitive262,
        operation: Arithmetic262,
        noise_is_left: bool,
    },
}

/// Immutable prepared DAG. `N` is checked against 32 at construction.
///
/// There is no world owner, registry, thread-local state or per-sample
/// allocation. Graph ownership and sample-output buffers stay with the caller.
#[derive(Clone, Debug)]
pub struct StockDensityProgram262<'a, const N: usize> {
    nodes: [StockDensityNode262<'a>; N],
    plan: SamplingPlan262<'a>,
}

impl<'a, const N: usize> StockDensityProgram262<'a, N> {
    /// Validate dependencies, dead nodes and a bounded scratch footprint once.
    ///
    /// # Errors
    /// Rejects empty/oversized programs, invalid dependency indices and
    /// disconnected nodes, before any density sampling.
    pub fn new(nodes: [StockDensityNode262<'a>; N]) -> Result<Self, StockDensityProgramError262> {
        if N == 0 {
            return Err(StockDensityProgramError262::Empty);
        }
        if N > 32 {
            return Err(StockDensityProgramError262::TooManyNodes);
        }

        for (index, node) in nodes.iter().enumerate() {
            if let StockDensityNode262::Add { left, right }
            | StockDensityNode262::Multiply { left, right } = node
            {
                for &child in &[*left, *right] {
                    if child >= index {
                        return Err(StockDensityProgramError262::InvalidDependency {
                            node: index,
                            child,
                        });
                    }
                }
            }
        }

        let mut reachable = [false; N];
        reachable[N - 1] = true;
        for index in (0..N).rev() {
            if !reachable[index] {
                continue;
            }
            if let StockDensityNode262::Add { left, right }
            | StockDensityNode262::Multiply { left, right } = nodes[index]
            {
                reachable[left] = true;
                reachable[right] = true;
            }
        }
        for (index, &used) in reachable.iter().enumerate() {
            if !used {
                return Err(StockDensityProgramError262::UnusedNode { node: index });
            }
        }

        let plan = if N == 1 {
            match nodes[0] {
                StockDensityNode262::Primitive(p) => SamplingPlan262::OnlyPrimitive(p),
                StockDensityNode262::RegisteredNoise(n) => SamplingPlan262::OnlyNoise(n),
                _ => SamplingPlan262::Generic,
            }
        } else if N == 3 {
            let operation = match nodes[2] {
                StockDensityNode262::Add { left: 0, right: 1 } => Some(Arithmetic262::Add),
                StockDensityNode262::Multiply { left: 0, right: 1 } => {
                    Some(Arithmetic262::Multiply)
                }
                _ => None,
            };
            match (operation, nodes[0], nodes[1]) {
                (
                    Some(operation),
                    StockDensityNode262::RegisteredNoise(noise),
                    StockDensityNode262::Primitive(primitive),
                ) => SamplingPlan262::NoiseAndPrimitive {
                    noise,
                    primitive,
                    operation,
                    noise_is_left: true,
                },
                (
                    Some(operation),
                    StockDensityNode262::Primitive(primitive),
                    StockDensityNode262::RegisteredNoise(noise),
                ) => SamplingPlan262::NoiseAndPrimitive {
                    noise,
                    primitive,
                    operation,
                    noise_is_left: false,
                },
                _ => SamplingPlan262::Generic,
            }
        } else {
            SamplingPlan262::Generic
        };
        Ok(Self { nodes, plan })
    }

    /// Evaluate a block with fixed, fully overwritten per-worker scratch.
    ///
    /// This is **explicit eager IEEE arithmetic**, NOT a claim of the
    /// unreviewed vanilla mixed `DensityFunctions` factory/delegate rules.
    #[must_use]
    #[inline]
    pub fn sample_with_scratch(
        &self,
        block_x: i32,
        block_y: i32,
        block_z: i32,
        scratch: &mut [f64; N],
    ) -> f64 {
        for (index, node) in self.nodes.iter().enumerate() {
            scratch[index] = match *node {
                StockDensityNode262::Primitive(primitive) => primitive.sample_block_y(block_y),
                StockDensityNode262::RegisteredNoise(noise) => {
                    noise.sample_block(block_x, block_y, block_z)
                }
                StockDensityNode262::Add { left, right } => scratch[left] + scratch[right],
                StockDensityNode262::Multiply { left, right } => scratch[left] * scratch[right],
            };
        }
        scratch[N - 1]
    }

    /// Scalar convenience form, with all scratch allocated on the stack.
    #[must_use]
    #[inline]
    pub fn sample_block(&self, x: i32, y: i32, z: i32) -> f64 {
        let mut scratch = [0.0_f64; N];
        self.sample_with_scratch(x, y, z, &mut scratch)
    }

    #[inline]
    fn validate_horizontal(x: i32, z: i32) -> Result<(), DirectNoiseCellError262> {
        x.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        z.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;
        Ok(())
    }

    #[inline]
    fn combine(output: &mut [f64], invariant: f64, operation: Arithmetic262, noise_is_left: bool) {
        if noise_is_left {
            for value in output {
                *value = operation.apply(*value, invariant);
            }
        } else {
            for value in output {
                *value = operation.apply(invariant, *value);
            }
        }
    }

    /// Write a caller-owned coherent Z/X plane at one integer Y.
    ///
    /// A single noise or a noise/primitive blend samples all 256 positions
    /// using the existing bit-qualified octave-axis implementation, then
    /// applies a single Y-only primitive value. General mixed DAGs use
    /// the fixed node scratch and original scalar operand order.
    ///
    /// # Errors
    /// All horizontal overflow is rejected before the first output write.
    ///
    /// # Panics
    /// Only if a fixed 16×16 pixel index does not fit into `usize`, which
    /// is impossible because both local axes are bounded by 0..16.
    pub fn sample_plane_16x16(
        &self,
        origin_x: i32,
        y: i32,
        origin_z: i32,
        output: &mut [f64; 256],
    ) -> Result<(), DirectNoiseCellError262> {
        Self::validate_horizontal(origin_x, origin_z)?;
        match self.plan {
            SamplingPlan262::OnlyPrimitive(primitive) => {
                output.fill(primitive.sample_block_y(y));
            }
            SamplingPlan262::OnlyNoise(noise) => {
                noise.sample_plane_16x16(origin_x, y, origin_z, output)?;
            }
            SamplingPlan262::NoiseAndPrimitive {
                noise,
                primitive,
                operation,
                noise_is_left,
            } => {
                noise.sample_plane_16x16(origin_x, y, origin_z, output)?;
                Self::combine(
                    output,
                    primitive.sample_block_y(y),
                    operation,
                    noise_is_left,
                );
            }
            SamplingPlan262::Generic => {
                let mut scratch = [0.0_f64; N];
                for dz in 0_i32..16 {
                    for dx in 0_i32..16 {
                        let index =
                            usize::try_from(dz * 16 + dx).expect("16x16 pixel index is bounded");
                        output[index] =
                            self.sample_with_scratch(origin_x + dx, y, origin_z + dz, &mut scratch);
                    }
                }
            }
        }
        Ok(())
    }

    /// Write one caller-owned 16³ cell in Y/Z/X order.
    ///
    /// For the fast noise/gradient case, fill the *entire* cell through the
    /// existing noise kernel (reusing 16-wide horizontal axes) and perform
    /// exactly 16 Y-only primitive evaluations, one per plane. This avoids
    /// 4096 gradient recomputations, without reordering floating arithmetic.
    ///
    /// # Errors
    /// Rejects X, Y or Z integer overflow atomically, before any output write.
    ///
    /// # Panics
    /// Only if the fixed 4096-element output unexpectedly fails to divide
    /// into sixteen exact 256-element planes.
    pub fn sample_cell_16x16x16(
        &self,
        x: i32,
        y: i32,
        z: i32,
        output: &mut [f64; 4096],
    ) -> Result<(), DirectNoiseCellError262> {
        Self::validate_horizontal(x, z)?;
        y.checked_add(15)
            .ok_or(DirectNoiseCellError262::BlockCoordinateOverflow)?;

        match self.plan {
            SamplingPlan262::OnlyNoise(noise) => {
                noise.sample_cell_16x16x16(x, y, z, output)?;
            }
            SamplingPlan262::NoiseAndPrimitive {
                noise,
                primitive,
                operation,
                noise_is_left,
            } => {
                noise.sample_cell_16x16x16(x, y, z, output)?;
                for (dy, plane) in (0_i32..16).zip(output.chunks_exact_mut(256)) {
                    Self::combine(
                        plane,
                        primitive.sample_block_y(y + dy),
                        operation,
                        noise_is_left,
                    );
                }
            }
            _ => {
                for (dy, plane) in (0_i32..16).zip(output.chunks_exact_mut(256)) {
                    self.sample_plane_16x16(
                        x,
                        y + dy,
                        z,
                        plane.try_into().expect("fixed 4096 / 256 cell plane"),
                    )?;
                }
            }
        }
        Ok(())
    }
}
