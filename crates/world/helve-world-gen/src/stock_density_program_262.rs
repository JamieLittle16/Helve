//! COLD-validated, allocation-free mixed-density expression **substrate**.
//!
//! Its leaves are the existing independently bit-qualified stock registered
//! world-seed noise and integer-block-Y constant/clamped-gradient primitives.
//! Its explicit arithmetic nodes are *eager IEEE operations*, NOT independently
//! qualified vanilla DensityFunctions / NoiseRouter. A separate typed leaf
//! delegates to the existing 1,920-JVM-vector-qualified stock mixed evaluator.
//! Another typed leaf reuses the 1,280-vector-qualified two-primitive composition.
//! Both preserve the observed 26.2 Ap2 +0 and MulOrAdd signed-zero behaviour.
//! An explicit Ap2-multiply DAG node additionally demand-evaluates its right
//! child, preserving that observed early return even across nested subgraphs.
//! The first-level stock finalDensity root is now independently observed as
//! Ap2 MIN(Mapped SQUEEZE(Marker), HolderHolder(RangeChoice)) across four seeds.
//! An explicit MIN node can combine independently evaluated finite operands.
//! The real SQUEEZE mapping is now bit-confirmed on 128 original JVM Marker
//! input/output pairs, and RangeChoice's actual [-1_000_000, 0) branch
//! selection matches 128 independent seeded observations. The candidate
//! nodes remain explicitly source-law unadmitted; actual inner graph children,
//! marker interpolation lifecycle and complete finalDensity remain open.
//! Factory selection and arbitrary graph shapes remain unqualified.
//! No production authority.
//!
//! A maximum of 32 immutable nodes and fixed per-worker scratch bound hot-path
//! work. A single noise leaf or noise with one Y-only primitive gets an exact
//! coherent plane/cell path. Everything else uses ordered per-block evaluation.

use crate::density_composition_262::DensityComposition262;
use crate::density_noise_direct_262::DirectNoiseCellError262;
use crate::density_primitives_262::DensityPrimitive262;
use crate::registered_noise_state_262::RegisteredNoiseDensityObserved262;
use crate::stock_vanilla_mixed_density_262::StockVanillaMixedDensity262;

/// Source-observed 26.2 `MulOrAdd` constant operator category.
///
/// The 1,920 independently captured mixed delegate outputs support
/// adding or multiplying a registered noise by a constant, including
/// ordinary IEEE signed zero (unlike explicit `Ap2` multiplication).
/// This does NOT determine the operation or coefficient in the actual
/// `finalDensity` `MulOrAdd` subtree.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StockMulOrAddOp262 {
    /// Finite sampled inner input plus a constant.
    Add,
    /// Finite sampled inner input multiplied by a constant.
    Multiply,
}

impl StockMulOrAddOp262 {
    #[inline]
    fn apply(self, input: f64, argument: f64) -> f64 {
        match self {
            Self::Add => input + argument,
            Self::Multiply => input * argument,
        }
    }
}

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
    /// One exact 26.2 observed stock Noise/primitive delegate.
    ///
    /// This node calls the existing qualified mixed evaluator. It is NOT an
    /// authorization to compile arbitrary vanilla factory/marker graph nodes.
    ObservedMixed(StockVanillaMixedDensity262<'a>),
    /// One exact observed 26.2 pair of Y-only density primitives.
    ///
    /// Retains the independently JVM-bit-qualified `Ap2` (+0 short-circuit)
    /// versus `MulOrAdd` (signed-zero IEEE multiplication) delegate choice.
    /// This does not source-admit arbitrary upstream factory graphs.
    ObservedPrimitiveComposition(DensityComposition262),
    /// Explicit eager IEEE-754 addition in operand order.
    Add { left: usize, right: usize },
    /// Caller-explicit Ap2 ADD on the actual 26.2 finalDensity outside branch.
    ///
    /// 128 original JVM operands/outputs support ordinary, ordered IEEE
    /// addition. This is only a typed finite SinglePointContext candidate:
    /// arbitrary factory rewrites, nonfinite laws and NoiseChunk cache
    /// lifecycle remain unreviewed.
    ExplicitAp2Add { left: usize, right: usize },
    /// Explicit eager IEEE-754 multiplication; **not** vanilla Ap2 short-circuit.
    Multiply { left: usize, right: usize },
    /// Caller-explicit observed Ap2 multiply candidate, demand-evaluated on
    /// the right only when the left is not positive zero. It must not be
    /// inferred from an arbitrary upstream vanilla graph or factory.
    ExplicitAp2Multiply { left: usize, right: usize },
    /// Caller-explicit 26.2 Ap2 MIN operation on two density dependencies.
    ///
    /// Verified only on finite, non-zero child-value combinations by 128
    /// original JVM `SinglePointContext` `finalDensity` root observations,
    /// including four right-child wins. Does NOT implement the `Mapped`/
    /// `HolderHolder` subgraphs or `NoiseChunk` marker/cache lifetimes.
    /// NaN and signed-zero Java-branch behaviour remain unreviewed.
    ExplicitAp2Min { left: usize, right: usize },
    /// Experimental unary transform for the observed stock
    /// `Mapped(type=SQUEEZE, input=Marker)` branch.
    ///
    /// Its formula is a **candidate** until separately matched against
    /// genuine original JVM Marker-input/Mapped-output pairs and reviewed
    /// against the pinned 26.2 mapping source body. This does not admit the
    /// marker's `NoiseChunk` cache, interpolation, or complete `finalDensity`.
    CandidateSqueeze { input: usize },
    /// Source-observed `RangeChoice` selector with lazy branch evaluation.
    ///
    /// The stock 26.2 `finalDensity` bound [-1,000,000, 0) selects
    /// constant 64.0 versus its `Ap2` alternative in 47/81 actual JVM
    /// `SinglePointContext` observations. This remains a candidate until
    /// its original source-law and `NoiseChunk` marker lifecycle are admitted.
    /// Candidate fused `MulOrAdd` arithmetic with a single density child.
    ///
    /// The operator has 1,152 independent original stock mixed-delegate
    /// output comparisons. The actual `finalDensity` instance is now
    /// observed as MUL(0x3fe47ae147ae147b, Marker) with 128/128 exact
    /// original-JVM `SinglePointContext` input/output bit matches.
    /// This does not source-review its wrapped Marker or NoiseChunk lifecycle.
    /// No arbitrary vanilla factory admission.
    CandidateMulOrAdd {
        /// The one upstream density dependency.
        input: usize,
        /// Signed, finite constant (including negative zero).
        argument: f64,
        /// Add or ordinary IEEE multiplication, not `Ap2` +0 skipping.
        operation: StockMulOrAddOp262,
    },
    CandidateRangeChoice {
        /// Density input used only to choose the branch.
        selector: usize,
        /// Evaluated only when the selector is >= min and < max.
        when_in_range: usize,
        /// Evaluated only when the selector is outside the range.
        when_out_of_range: usize,
        /// Inclusive lower bound, verified finite at COLD construction.
        min_inclusive: f64,
        /// Exclusive upper bound, verified finite at COLD construction.
        max_exclusive: f64,
    },
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
    /// Range bounds must be finite and strictly increasing.
    InvalidRangeBounds { node: usize },
    /// The fused `MulOrAdd` constant is not a finite JVM-observed parameter.
    InvalidMulOrAddArgument { node: usize },
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

/// Stock 26.2 SQUEEZE mapping candidate: 128/128 original JVM bit matches.
///
/// The original 26.2 `Mapped` source operation ordering is still unreviewed;
/// bit parity in four seeded `SinglePointContext` frames alone does not
/// authorize using this transform as a stock `NoiseChunk` implementation.
/// Keep the observed arithmetic order, without FMA or simplification.
#[inline]
fn candidate_squeeze(value: f64) -> f64 {
    let clamped = value.clamp(-1.0, 1.0);
    clamped / 2.0 - clamped * clamped * clamped / 24.0
}

/// Preselected specializations. No expensive tree shape matching per sample.
#[derive(Clone, Copy, Debug)]
enum SamplingPlan262<'a> {
    Generic,
    OnlyPrimitive(DensityPrimitive262),
    OnlyNoise(RegisteredNoiseDensityObserved262<'a>),
    OnlyObservedMixed(StockVanillaMixedDensity262<'a>),
    OnlyObservedPrimitiveComposition(DensityComposition262),
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
    contains_demand_nodes: bool,
}

impl<'a, const N: usize> StockDensityProgram262<'a, N> {
    /// Validate strictly backward unary and binary edges once at COLD construction.
    fn validate_edges(
        nodes: &[StockDensityNode262<'a>; N],
    ) -> Result<(), StockDensityProgramError262> {
        for (index, node) in nodes.iter().enumerate() {
            match *node {
                StockDensityNode262::Add { left, right }
                | StockDensityNode262::ExplicitAp2Add { left, right }
                | StockDensityNode262::Multiply { left, right }
                | StockDensityNode262::ExplicitAp2Multiply { left, right }
                | StockDensityNode262::ExplicitAp2Min { left, right } => {
                    for child in [left, right] {
                        if child >= index {
                            return Err(StockDensityProgramError262::InvalidDependency {
                                node: index,
                                child,
                            });
                        }
                    }
                }
                StockDensityNode262::CandidateSqueeze { input } if input >= index => {
                    return Err(StockDensityProgramError262::InvalidDependency {
                        node: index,
                        child: input,
                    });
                }
                StockDensityNode262::CandidateMulOrAdd {
                    input, argument, ..
                } => {
                    if !argument.is_finite() {
                        return Err(StockDensityProgramError262::InvalidMulOrAddArgument {
                            node: index,
                        });
                    }
                    if input >= index {
                        return Err(StockDensityProgramError262::InvalidDependency {
                            node: index,
                            child: input,
                        });
                    }
                }
                StockDensityNode262::CandidateRangeChoice {
                    selector,
                    when_in_range,
                    when_out_of_range,
                    min_inclusive,
                    max_exclusive,
                } => {
                    if !min_inclusive.is_finite()
                        || !max_exclusive.is_finite()
                        || min_inclusive >= max_exclusive
                    {
                        return Err(StockDensityProgramError262::InvalidRangeBounds {
                            node: index,
                        });
                    }
                    for child in [selector, when_in_range, when_out_of_range] {
                        if child >= index {
                            return Err(StockDensityProgramError262::InvalidDependency {
                                node: index,
                                child,
                            });
                        }
                    }
                }
                _ => {}
            }
        }
        Ok(())
    }

    #[inline]
    fn requires_demand_evaluation(nodes: &[StockDensityNode262<'a>; N]) -> bool {
        nodes.iter().any(|node| {
            matches!(
                node,
                StockDensityNode262::ExplicitAp2Multiply { .. }
                    | StockDensityNode262::CandidateRangeChoice { .. }
            )
        })
    }

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

        Self::validate_edges(&nodes)?;

        let mut reachable = [false; N];
        reachable[N - 1] = true;
        for index in (0..N).rev() {
            if !reachable[index] {
                continue;
            }
            match nodes[index] {
                StockDensityNode262::Add { left, right }
                | StockDensityNode262::ExplicitAp2Add { left, right }
                | StockDensityNode262::Multiply { left, right }
                | StockDensityNode262::ExplicitAp2Multiply { left, right }
                | StockDensityNode262::ExplicitAp2Min { left, right } => {
                    reachable[left] = true;
                    reachable[right] = true;
                }
                StockDensityNode262::CandidateSqueeze { input }
                | StockDensityNode262::CandidateMulOrAdd { input, .. } => {
                    reachable[input] = true;
                }
                StockDensityNode262::CandidateRangeChoice {
                    selector,
                    when_in_range,
                    when_out_of_range,
                    ..
                } => {
                    reachable[selector] = true;
                    reachable[when_in_range] = true;
                    reachable[when_out_of_range] = true;
                }
                _ => {}
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
                StockDensityNode262::ObservedMixed(mixed) => {
                    SamplingPlan262::OnlyObservedMixed(mixed)
                }
                StockDensityNode262::ObservedPrimitiveComposition(composed) => {
                    SamplingPlan262::OnlyObservedPrimitiveComposition(composed)
                }
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
        let contains_demand_nodes = Self::requires_demand_evaluation(&nodes);
        Ok(Self {
            nodes,
            plan,
            contains_demand_nodes,
        })
    }

    /// Evaluate a block using caller-owned, fixed-bounded scratch.
    ///
    /// Eager programs overwrite all N slots. Explicit Ap2 programs compute
    /// only demanded nodes and do not overwrite skipped subtree slots; only
    /// the returned output is guaranteed meaningful. This does not authorize
    /// arbitrary vanilla factory/delegate graph shapes.
    #[must_use]
    #[inline]
    pub fn sample_with_scratch(
        &self,
        block_x: i32,
        block_y: i32,
        block_z: i32,
        scratch: &mut [f64; N],
    ) -> f64 {
        if self.contains_demand_nodes {
            let mut computed = [false; N];
            return self.evaluate_demand(
                N - 1,
                (block_x, block_y, block_z),
                scratch,
                &mut computed,
            );
        }
        for (index, node) in self.nodes.iter().enumerate() {
            scratch[index] = match *node {
                StockDensityNode262::Primitive(primitive) => primitive.sample_block_y(block_y),
                StockDensityNode262::RegisteredNoise(noise) => {
                    noise.sample_block(block_x, block_y, block_z)
                }
                StockDensityNode262::ObservedMixed(mixed) => {
                    mixed.sample_block(block_x, block_y, block_z)
                }
                StockDensityNode262::ObservedPrimitiveComposition(composed) => {
                    composed.sample_block_y(block_y)
                }
                StockDensityNode262::Add { left, right }
                | StockDensityNode262::ExplicitAp2Add { left, right } => {
                    scratch[left] + scratch[right]
                }
                StockDensityNode262::Multiply { left, right } => scratch[left] * scratch[right],
                StockDensityNode262::ExplicitAp2Min { left, right } => {
                    scratch[left].min(scratch[right])
                }
                StockDensityNode262::CandidateSqueeze { input } => {
                    candidate_squeeze(scratch[input])
                }
                StockDensityNode262::CandidateMulOrAdd {
                    input,
                    argument,
                    operation,
                } => operation.apply(scratch[input], argument),
                StockDensityNode262::ExplicitAp2Multiply { .. }
                | StockDensityNode262::CandidateRangeChoice { .. } => {
                    unreachable!("COLD program selects demand evaluation for conditional nodes")
                }
            };
        }
        scratch[N - 1]
    }

    /// Evaluate one demanded child once per sample. COLD validation
    /// guarantees backward edges and a maximum nesting depth of 32.
    /// Siblings reached from two parents share the same computed value.
    /// No heap allocation, dynamic registry or world owner is involved.
    fn evaluate_demand(
        &self,
        index: usize,
        block: (i32, i32, i32),
        scratch: &mut [f64; N],
        computed: &mut [bool; N],
    ) -> f64 {
        if computed[index] {
            return scratch[index];
        }
        let value = match self.nodes[index] {
            StockDensityNode262::Primitive(primitive) => primitive.sample_block_y(block.1),
            StockDensityNode262::RegisteredNoise(noise) => {
                noise.sample_block(block.0, block.1, block.2)
            }
            StockDensityNode262::ObservedMixed(mixed) => {
                mixed.sample_block(block.0, block.1, block.2)
            }
            StockDensityNode262::ObservedPrimitiveComposition(composed) => {
                composed.sample_block_y(block.1)
            }
            StockDensityNode262::Add { left, right }
            | StockDensityNode262::ExplicitAp2Add { left, right } => {
                let a = self.evaluate_demand(left, block, scratch, computed);
                let b = self.evaluate_demand(right, block, scratch, computed);
                a + b
            }
            StockDensityNode262::Multiply { left, right } => {
                let a = self.evaluate_demand(left, block, scratch, computed);
                let b = self.evaluate_demand(right, block, scratch, computed);
                a * b
            }
            StockDensityNode262::ExplicitAp2Min { left, right } => {
                let first = self.evaluate_demand(left, block, scratch, computed);
                let second = self.evaluate_demand(right, block, scratch, computed);
                first.min(second)
            }
            StockDensityNode262::CandidateSqueeze { input } => {
                candidate_squeeze(self.evaluate_demand(input, block, scratch, computed))
            }
            StockDensityNode262::CandidateMulOrAdd {
                input,
                argument,
                operation,
            } => operation.apply(
                self.evaluate_demand(input, block, scratch, computed),
                argument,
            ),
            StockDensityNode262::CandidateRangeChoice {
                selector,
                when_in_range,
                when_out_of_range,
                min_inclusive,
                max_exclusive,
            } => {
                let key = self.evaluate_demand(selector, block, scratch, computed);
                let branch = if key >= min_inclusive && key < max_exclusive {
                    when_in_range
                } else {
                    when_out_of_range
                };
                self.evaluate_demand(branch, block, scratch, computed)
            }
            StockDensityNode262::ExplicitAp2Multiply { left, right } => {
                let first = self.evaluate_demand(left, block, scratch, computed);
                if first.to_bits() == 0.0_f64.to_bits() {
                    0.0
                } else {
                    first * self.evaluate_demand(right, block, scratch, computed)
                }
            }
        };
        scratch[index] = value;
        computed[index] = true;
        value
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
            SamplingPlan262::OnlyObservedMixed(mixed) => {
                mixed.sample_plane_16x16(origin_x, y, origin_z, output)?;
            }
            SamplingPlan262::OnlyObservedPrimitiveComposition(composed) => {
                composed.sample_plane_16x16(y, output);
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
            SamplingPlan262::OnlyObservedMixed(mixed) => {
                mixed.sample_cell_16x16x16(x, y, z, output)?;
            }
            SamplingPlan262::OnlyObservedPrimitiveComposition(composed) => {
                composed
                    .sample_cell_16x16x16(y, output)
                    .map_err(|_| DirectNoiseCellError262::BlockCoordinateOverflow)?;
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
