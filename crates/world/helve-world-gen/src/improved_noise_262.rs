//! COLD, allocation-free Minecraft Java 26.2-style improved-gradient noise sampler.
//!
//! This is a precisely scoped **candidate** against source-free official JVM
//! vectors, not yet a source-admitted RNG/constructor/delegate closure or an
//! authorised full terrain/density/biome generator. Seed here is the direct
//! argument to `RandomSource.create(long)`, NOT a world-generation seed mix.
//! The exact 26.2 versioned fixture tests all 160 captured output bit patterns.

/// Frozen seed-specific offsets and permutation in inline storage.
/// No allocations, atomics, registry access, virtual calls or mutable sampling
/// state; safe to share across COLD workers after one-time construction.
#[derive(Clone, Debug)]
pub struct ImprovedNoise262 {
    permutation: [u8; 256],
    offset_x: f64,
    offset_y: f64,
    offset_z: f64,
}

const GRADIENT: [[i32; 3]; 16] = [
    [1, 1, 0],
    [-1, 1, 0],
    [1, -1, 0],
    [-1, -1, 0],
    [1, 0, 1],
    [-1, 0, 1],
    [1, 0, -1],
    [-1, 0, -1],
    [0, 1, 1],
    [0, -1, 1],
    [0, 1, -1],
    [0, -1, -1],
    [1, 1, 0],
    [0, -1, 1],
    [-1, 1, 0],
    [0, -1, -1],
];

/// The fixed-width state transition used by the candidate legacy bit RNG.
/// Seeding and bounded-int rejection consume exactly the prescribed calls;
/// no std RNG implementation or floating-point approximation is substituted.
#[derive(Debug)]
struct LegacyBits {
    state: u64,
}

impl LegacyBits {
    const MASK: u64 = (1_u64 << 48) - 1;
    const MULTIPLIER: u64 = 0x5dee_ce66d;

    fn new(seed: u64) -> Self {
        Self {
            state: (seed ^ Self::MULTIPLIER) & Self::MASK,
        }
    }

    #[inline]
    fn next_bits(&mut self, count: u32) -> u32 {
        self.state = self.state.wrapping_mul(Self::MULTIPLIER).wrapping_add(11) & Self::MASK;
        (self.state >> (48 - count)) as u32
    }

    #[inline]
    fn next_double(&mut self) -> f64 {
        let upper = u64::from(self.next_bits(26)) << 27;
        let lower = u64::from(self.next_bits(27));
        ((upper | lower) as f64) * (1.0 / 9_007_199_254_740_992.0)
    }

    #[inline]
    fn next_int(&mut self, bound: u32) -> u32 {
        debug_assert!(bound > 0);
        if bound.is_power_of_two() {
            return ((u64::from(bound) * u64::from(self.next_bits(31))) >> 31) as u32;
        }
        loop {
            let bits = self.next_bits(31);
            let value = bits % bound;
            // Reconstruct Java's signed-i32 rejection after modular addition.
            // The accepted result is identical without relying on overflow.
            if u64::from(bits - value) + u64::from(bound - 1) < (1_u64 << 31) {
                return value;
            }
        }
    }
}

#[inline]
fn java_floor(value: f64) -> i32 {
    let truncated = value as i32;
    if value < f64::from(truncated) {
        truncated.wrapping_sub(1)
    } else {
        truncated
    }
}

#[inline]
fn smoothstep(value: f64) -> f64 {
    value * value * value * (value * (value * 6.0 - 15.0) + 10.0)
}

#[inline]
fn lerp(fraction: f64, start: f64, end: f64) -> f64 {
    start + fraction * (end - start)
}

#[inline]
fn lerp3(
    x: f64,
    y: f64,
    z: f64,
    a: f64,
    b: f64,
    c: f64,
    d: f64,
    e: f64,
    f: f64,
    g: f64,
    h: f64,
) -> f64 {
    lerp(
        z,
        lerp(y, lerp(x, a, b), lerp(x, c, d)),
        lerp(y, lerp(x, e, f), lerp(x, g, h)),
    )
}

#[inline]
fn grad_dot(hash: u8, x: f64, y: f64, z: f64) -> f64 {
    let gradient = GRADIENT[usize::from(hash & 15)];
    (f64::from(gradient[0]) * x + f64::from(gradient[1]) * y) + f64::from(gradient[2]) * z
}

impl ImprovedNoise262 {
    /// Prepares one complete independent sampler using the direct bit-pattern
    /// seed given to the official `RandomSource.create(long)` probe.
    /// Allocate once per resolved seed/parameter, never once per noise sample.
    #[must_use]
    pub fn new(seed_bits: u64) -> Self {
        let mut random = LegacyBits::new(seed_bits);
        let offset_x = random.next_double() * 256.0;
        let offset_y = random.next_double() * 256.0;
        let offset_z = random.next_double() * 256.0;
        let mut permutation = [0_u8; 256];
        for (index, item) in permutation.iter_mut().enumerate() {
            *item = index as u8;
        }
        for index in 0..256_usize {
            let next = index + random.next_int((256 - index) as u32) as usize;
            permutation.swap(index, next);
        }
        Self {
            permutation,
            offset_x,
            offset_y,
            offset_z,
        }
    }

    #[inline]
    fn p(&self, index: i32) -> u8 {
        self.permutation[(index & 255) as usize]
    }

    /// Samples a 3D coordinate without allocation or mutable RNG consumption.
    /// Floating operations retain their reference evaluation order: do NOT
    /// introduce `mul_add`, fast-math or algebraic reassociation on this path.
    ///
    /// For finite inputs in the checked reference corpus, compare `to_bits()`
    /// rather than numeric equality. This alone is NOT full worldgen parity.
    #[must_use]
    pub fn sample(&self, x: f64, y: f64, z: f64) -> f64 {
        let x = x + self.offset_x;
        let y = y + self.offset_y;
        let z = z + self.offset_z;

        let ix = java_floor(x);
        let iy = java_floor(y);
        let iz = java_floor(z);
        let dx = x - f64::from(ix);
        let dy = y - f64::from(iy);
        let dz = z - f64::from(iz);

        let a = i32::from(self.p(ix));
        let b = i32::from(self.p(ix.wrapping_add(1)));
        let aa = i32::from(self.p(a.wrapping_add(iy)));
        let ab = i32::from(self.p(a.wrapping_add(iy).wrapping_add(1)));
        let ba = i32::from(self.p(b.wrapping_add(iy)));
        let bb = i32::from(self.p(b.wrapping_add(iy).wrapping_add(1)));

        let c000 = grad_dot(self.p(aa.wrapping_add(iz)), dx, dy, dz);
        let c100 = grad_dot(self.p(ba.wrapping_add(iz)), dx - 1.0, dy, dz);
        let c010 = grad_dot(self.p(ab.wrapping_add(iz)), dx, dy - 1.0, dz);
        let c110 = grad_dot(self.p(bb.wrapping_add(iz)), dx - 1.0, dy - 1.0, dz);
        let c001 = grad_dot(
            self.p(aa.wrapping_add(iz).wrapping_add(1)),
            dx,
            dy,
            dz - 1.0,
        );
        let c101 = grad_dot(
            self.p(ba.wrapping_add(iz).wrapping_add(1)),
            dx - 1.0,
            dy,
            dz - 1.0,
        );
        let c011 = grad_dot(
            self.p(ab.wrapping_add(iz).wrapping_add(1)),
            dx,
            dy - 1.0,
            dz - 1.0,
        );
        let c111 = grad_dot(
            self.p(bb.wrapping_add(iz).wrapping_add(1)),
            dx - 1.0,
            dy - 1.0,
            dz - 1.0,
        );
        lerp3(
            smoothstep(dx),
            smoothstep(dy),
            smoothstep(dz),
            c000,
            c100,
            c010,
            c110,
            c001,
            c101,
            c011,
            c111,
        )
    }

    /// Tiny immutable seed-state checksum, useful for parity reports without
    /// exposing mutable RNG state or copying the 256-byte permutation.
    #[must_use]
    pub fn permutation_checksum(&self) -> u64 {
        self.permutation
            .iter()
            .fold(0xcbf2_9ce4_8422_2325_u64, |acc, &v| {
                (acc ^ u64::from(v)).wrapping_mul(0x100_0000_01b3)
            })
    }
}

#[cfg(test)]
mod tests {
    use super::{ImprovedNoise262, LegacyBits};

    #[test]
    fn immutable_sampler_has_one_of_each_permutation_entry() {
        for seed in [0, 1, u64::MAX, 1_u64 << 63, 0x9e37_79b9_7f4a_7c15] {
            let instance = ImprovedNoise262::new(seed);
            let mut sorted = instance.permutation;
            sorted.sort_unstable();
            for (index, value) in sorted.iter().enumerate() {
                assert_eq!(*value as usize, index);
            }
            assert_eq!(
                instance.sample(0.125, -16.0, 31.5).to_bits(),
                instance.sample(0.125, -16.0, 31.5).to_bits()
            );
        }
    }

    #[test]
    fn power_of_two_and_non_power_of_two_bounded_rng_are_in_range() {
        let mut rng = LegacyBits::new(1);
        for bound in 1..=256 {
            for _ in 0..4 {
                assert!(rng.next_int(bound) < bound);
            }
        }
    }

    #[test]
    fn high_seed_bit_is_discarded_by_48_bit_legacy_initialization() {
        let a = ImprovedNoise262::new(0);
        let b = ImprovedNoise262::new(1_u64 << 63);
        assert_eq!(a.permutation, b.permutation);
        assert_eq!(a.offset_x.to_bits(), b.offset_x.to_bits());
        assert_eq!(a.offset_y.to_bits(), b.offset_y.to_bits());
        assert_eq!(a.offset_z.to_bits(), b.offset_z.to_bits());
    }
}
