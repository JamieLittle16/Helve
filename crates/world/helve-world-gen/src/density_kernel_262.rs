//! Production-disconnected, source-free density-field calculation substrate.
//!
//! This deliberately implements ONLY an explicit eager straight-line
//! arithmetic/noise DAG chosen by the caller. It is NOT Minecraft 26.2
//! `DensityFunctions`, `NoiseRouter`, `RandomState`, terrain or admission.
//! In particular, vanilla short-circuiting, interpolation, caches,
//! registries, aquifers and branch-specific operation order are unreviewed.
//!
//! Nodes are immutable and borrow the existing immutable Perlin/Normal
//! samplers; the caller owns fixed-size per-worker scratch and output.
//! No heap allocation, virtual calls or state mutation occurs per sample.

use crate::perlin_normal_262::{NormalNoise262, PerlinNoise262};

/// A narrowly scoped, explicitly ordered arithmetic/noise expression.
/// Both arithmetic operands are already computed before the node executes.
/// Do not infer source-version vanilla min/max, lazy evaluation or other
/// `DensityFunctions` semantics from these generic operations.
#[derive(Clone, Copy, Debug)]
pub enum DensityNode262<'a> {
    /// The raw IEEE-754 value is preserved, including signed zero.
    Constant(f64),
    /// The caller-provided X coordinate, unchanged.
    X,
    /// The caller-provided Y coordinate, unchanged.
    Y,
    /// The caller-provided Z coordinate, unchanged.
    Z,
    /// Evaluate one retained seeded or externally observed Perlin sampler.
    Perlin(&'a PerlinNoise262),
    /// Evaluate one retained seeded or externally observed Normal sampler.
    Normal(&'a NormalNoise262),
    /// Strict left-operand then right-operand floating-point addition.
    Add { left: usize, right: usize },
    /// Strict left-operand then right-operand floating-point multiplication.
    Multiply { left: usize, right: usize },
}

/// Malformed explicit program: rejection happens once, before COLD sampling.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DensityKernelError262 {
    /// A graph must have a final output node.
    Empty,
    /// All children must precede their consumer in the fixed node array.
    InvalidDependency { node: usize, child: usize },
    /// Dead graph nodes would cause unnecessary evaluation every sample.
    UnusedNode { node: usize },
}

/// Immutable, statically sized, fully validated COLD density program.
///
/// The output is the **last** node. Repeated references to a node reuse its
/// result per coordinate. This does not reuse values across coordinates,
/// which would be unsound without independent source/cache review.
#[derive(Clone, Debug)]
pub struct DensityKernel262<'a, const N: usize> {
    nodes: [DensityNode262<'a>; N],
}

impl<'a, const N: usize> DensityKernel262<'a, N> {
    /// Validate the complete dependency graph once, outside sampling.
    /// No allocations, identifiers, registries or dynamic node dispatch.
    ///
    /// # Errors
    /// Rejects empty programs, cycles/forward edges, and unreachable nodes.
    pub fn new(nodes: [DensityNode262<'a>; N]) -> Result<Self, DensityKernelError262> {
        if N == 0 {
            return Err(DensityKernelError262::Empty);
        }
        for (node, operation) in nodes.iter().enumerate() {
            match operation {
                DensityNode262::Add { left, right } | DensityNode262::Multiply { left, right } => {
                    if *left >= node {
                        return Err(DensityKernelError262::InvalidDependency {
                            node,
                            child: *left,
                        });
                    }
                    if *right >= node {
                        return Err(DensityKernelError262::InvalidDependency {
                            node,
                            child: *right,
                        });
                    }
                }
                _ => {}
            }
        }

        // Reverse traversal is sufficient: edges always point to earlier
        // nodes. Every marked predecessor will be encountered later.
        let mut reachable = [false; N];
        reachable[N - 1] = true;
        for index in (0..N).rev() {
            if !reachable[index] {
                continue;
            }
            match nodes[index] {
                DensityNode262::Add { left, right } | DensityNode262::Multiply { left, right } => {
                    reachable[left] = true;
                    reachable[right] = true;
                }
                _ => {}
            }
        }
        for (node, &used) in reachable.iter().enumerate() {
            if !used {
                return Err(DensityKernelError262::UnusedNode { node });
            }
        }
        Ok(Self { nodes })
    }

    /// Evaluate a scalar using caller-owned, reusable per-worker scratch.
    /// All N slots are overwritten in dependency order before being read.
    /// Sampling never allocates and never touches an authoritative world.
    #[must_use]
    #[inline]
    pub fn sample_with_scratch(&self, x: f64, y: f64, z: f64, scratch: &mut [f64; N]) -> f64 {
        for (index, node) in self.nodes.iter().enumerate() {
            scratch[index] = match *node {
                DensityNode262::Constant(value) => value,
                DensityNode262::X => x,
                DensityNode262::Y => y,
                DensityNode262::Z => z,
                DensityNode262::Perlin(noise) => noise.sample(x, y, z),
                DensityNode262::Normal(noise) => noise.sample(x, y, z),
                DensityNode262::Add { left, right } => scratch[left] + scratch[right],
                DensityNode262::Multiply { left, right } => scratch[left] * scratch[right],
            };
        }
        scratch[N - 1]
    }

    /// Convenient scalar entry; the scratch is fixed-size stack storage.
    #[must_use]
    #[inline]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let mut scratch = [0.0; N];
        self.sample_with_scratch(x, y, z, &mut scratch)
    }

    /// Exact Z-major 16×16 plane. Single-node Perlin/Normal programs
    /// delegate to the already bit-qualified coherent batching kernel.
    /// Generic graphs retain per-coordinate operation order and reuse
    /// fixed-size scratch across all 256 positions.
    pub fn sample_plane_16x16(
        &self,
        origin_x: f64,
        y: f64,
        origin_z: f64,
        output: &mut [f64; 256],
    ) {
        if N == 1 {
            match self.nodes[0] {
                DensityNode262::Constant(value) => {
                    output.fill(value);
                    return;
                }
                DensityNode262::Y => {
                    output.fill(y);
                    return;
                }
                DensityNode262::Perlin(noise) => {
                    noise.sample_plane_16x16(origin_x, y, origin_z, output);
                    return;
                }
                DensityNode262::Normal(noise) => {
                    noise.sample_plane_16x16(origin_x, y, origin_z, output);
                    return;
                }
                _ => {}
            }
        }
        let mut scratch = [0.0; N];
        for local_z in 0_u8..16 {
            let z = origin_z + f64::from(local_z);
            for local_x in 0_u8..16 {
                let x = origin_x + f64::from(local_x);
                output[usize::from(local_z) * 16 + usize::from(local_x)] =
                    self.sample_with_scratch(x, y, z, &mut scratch);
            }
        }
    }

    /// 4096 density values in **Y/Z/X** cell order. Caller owns both
    /// output and temporary scratch; there is no extra volume copy.
    /// The single-noise plane fast path is reused for every Y slice.
    pub fn sample_cell_16x16x16(
        &self,
        origin_x: f64,
        origin_y: f64,
        origin_z: f64,
        output: &mut [f64; 4096],
    ) {
        for (local_y, plane) in output.chunks_exact_mut(256).enumerate() {
            let plane: &mut [f64; 256] = plane
                .try_into()
                .expect("each exact chunk of 4096/256 is a 256-element plane");
            let y = origin_y + f64::from(u8::try_from(local_y).expect("16 Y levels fit u8"));
            self.sample_plane_16x16(origin_x, y, origin_z, plane);
        }
    }
}
