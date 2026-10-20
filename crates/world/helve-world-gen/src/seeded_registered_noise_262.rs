//! Closed-world, COLD-only stock 26.2 world-seed constructor **candidate**.
//!
//! The five signed world seeds and three stock registry noise identities are
//! independently observed from the actual 26.2 JVM. This version-specific
//! Xoroshiro positional chain must be checked against **all** those prepared
//! states, not merely output samples. Its exact source/delegate-law VAR/SEM
//! admission and use for production remain separate, explicitly closed gates.
//!
//! Do not replace the previously bit-qualified improved/Perlin/normal samplers.
//! This module only derives their immutable input state once per seed/key.
//! No heap allocation, RNG step, string hashing, registry or dispatch occurs
//! in subsequent sampling calls.

use crate::improved_noise_262::ImprovedNoise262;
use crate::registered_noise_state_262::{
    RegisteredNormalObserved262, RegisteredPerlinObserved262,
};

/// Exact three built-in overworld noise keys examined on stock Java 26.2.
/// This enum is deliberately not an arbitrary datapack registry abstraction.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StockRegisteredNoiseKey262 {
    /// `minecraft:temperature`: six slots, two active.
    Temperature,
    /// `minecraft:continentalness`: nine active octave slots.
    Continentalness,
    /// `minecraft:erosion`: five slots, one absent.
    Erosion,
}

impl StockRegisteredNoiseKey262 {
    const fn parameters(self) -> (i32, &'static [f64], [u64; 2]) {
        match self {
            Self::Temperature => (
                -10,
                &[1.5, 0.0, 1.0, 0.0, 0.0, 0.0],
                [0x5c7e_6b29_735f_0d7f, 0xf7d8_6f1b_bc73_4988],
            ),
            Self::Continentalness => (
                -9,
                &[1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0],
                [0x8388_6c9d_0ae3_a662, 0xafa6_38a6_1b42_e8ad],
            ),
            Self::Erosion => (
                -9,
                &[1.0, 1.0, 0.0, 1.0, 1.0],
                [0xd024_91e6_058f_6fd8, 0x4792_512c_94c1_7a80],
            ),
        }
    }
}

/// RFC 1321 MD5 (two big-endian u64 halves) for exactly octave_-10..octave_-1.
/// Computed from ASCII names, **not** captured permutation/output tables.
/// Replaces repeated general string hashing at COLD initialization; unknown
/// octave ranges must use a separately admitted constructor.
const OCTAVE_NAME_MD5_262: [[u64; 2]; 10] = [
    [0x36d3_26ee_d40e_feb2, 0x5be9_ce18_223c_636a],
    [0x082f_e255_f8be_6631, 0x4e96_119e_22de_dc81],
    [0x0ef6_8ec6_8504_005e, 0x48b6_bf93_a278_9640],
    [0xf112_6812_8982_754f, 0x257a_1d67_0430_b0aa],
    [0xe51c_98ce_7d1d_e664, 0x5f94_78a7_3304_0c45],
    [0x6d7b_49e7_e429_850a, 0x2e30_63c6_22a2_4777],
    [0xbd90_d537_7ba1_b762, 0xc073_17d4_19a7_548d],
    [0x53d3_9c67_52da_c858, 0xbcd1_c5a8_0ab6_5b3e],
    [0xb4a2_4d7a_84e7_677b, 0x023f_f966_8e89_b5c4],
    [0xdffa_22b5_34c5_f608, 0xb9b6_7517_d366_5ca9],
];

/// Private Xoroshiro128++ stream. Its state belongs exclusively to COLD
/// construction; the frozen samplers only retain permutation/offset parts.
#[derive(Clone, Copy, Debug)]
struct XoroshiroBits262 {
    lo: u64,
    hi: u64,
}

impl XoroshiroBits262 {
    fn new(lo: u64, hi: u64) -> Self {
        // The explicitly observed key/octave paths never enter the all-zero
        // exceptional state; keep the general Java fallback nonetheless.
        if lo | hi == 0 {
            return Self {
                lo: 0x9e37_79b9_7f4a_7c15,
                hi: 0x6a09_e667_f3bc_c909,
            };
        }
        Self { lo, hi }
    }

    fn from_world_seed(seed_bits: u64) -> Self {
        let lo = seed_bits ^ 0x6a09_e667_f3bc_c909;
        let hi = lo.wrapping_add(0x9e37_79b9_7f4a_7c15);
        Self::new(mix_stafford13(lo), mix_stafford13(hi))
    }

    #[inline]
    fn next_u64(&mut self) -> u64 {
        let lo = self.lo;
        let hi = self.hi;
        let value = lo
            .wrapping_add(hi)
            .rotate_left(17)
            .wrapping_add(lo);
        let delta = hi ^ lo;
        self.lo = lo.rotate_left(49) ^ delta ^ (delta << 21);
        self.hi = delta.rotate_left(28);
        value
    }

    #[inline]
    #[expect(
        clippy::cast_precision_loss,
        reason = "an unsigned 53-bit RNG sample is exactly representable in f64"
    )]
    fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / 9_007_199_254_740_992.0)
    }

    /// Java's unsigned low-32 multiply-high bounded draw with rejection.
    /// The 256-entry Fisher-Yates shuffle uses bounds 256 down through 1.
    #[inline]
    fn next_bounded(&mut self, bound: u32) -> u32 {
        debug_assert!(bound > 0);
        let mut product = u64::from(self.next_u64() as u32) * u64::from(bound);
        let mut low = product as u32;
        if low < bound {
            let threshold = bound.wrapping_neg() % bound;
            while low < threshold {
                product = u64::from(self.next_u64() as u32) * u64::from(bound);
                low = product as u32;
            }
        }
        u32::try_from(product >> 32).expect("multiply-high bounded result fits u32")
    }

    fn fork_positional(&mut self) -> [u64; 2] {
        [self.next_u64(), self.next_u64()]
    }
}

#[inline]
fn mix_stafford13(value: u64) -> u64 {
    let value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    let value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^ (value >> 31)
}

#[inline]
fn named_fork(parent: [u64; 2], name_hash: [u64; 2]) -> XoroshiroBits262 {
    XoroshiroBits262::new(parent[0] ^ name_hash[0], parent[1] ^ name_hash[1])
}

fn improved_from_stream(mut random: XoroshiroBits262) -> ImprovedNoise262 {
    let x = random.next_f64() * 256.0;
    let y = random.next_f64() * 256.0;
    let z = random.next_f64() * 256.0;
    let mut permutation = [0_u8; 256];
    for (i, cell) in permutation.iter_mut().enumerate() {
        *cell = u8::try_from(i).expect("256-byte permutation indices");
    }
    for i in 0..256 {
        let remaining = u32::try_from(256 - i).expect("bounded remaining permutation entries");
        let jump = usize::try_from(random.next_bounded(remaining))
            .expect("bounded permutation jump");
        permutation.swap(i, i + jump);
    }
    ImprovedNoise262::from_observed_parts(permutation, x, y, z)
        .expect("constructed Fisher-Yates permutation is bijective")
}

fn construct_perlin(
    normal_random: &mut XoroshiroBits262,
    first_octave: i32,
    amplitudes: &[f64],
) -> RegisteredPerlinObserved262 {
    let positional = normal_random.fork_positional();
    let mut noise_levels = Vec::with_capacity(amplitudes.len());
    for (index, &amplitude) in amplitudes.iter().enumerate() {
        if amplitude == 0.0 {
            noise_levels.push(None);
            continue;
        }
        let octave = first_octave + i32::try_from(index).expect("fixed registered amplitude span");
        let md5_index = usize::try_from(octave + 10).expect("stock octave is -10..-1");
        let hash = OCTAVE_NAME_MD5_262[md5_index];
        noise_levels.push(Some(improved_from_stream(named_fork(positional, hash))));
    }

    let len = i32::try_from(amplitudes.len()).expect("fixed stock span fits i32");
    let lowest_input_factor = (2.0_f64).powi(first_octave);
    let numerator = (2.0_f64).powi(len - 1);
    let denominator = (2.0_f64).powi(len) - 1.0;
    RegisteredPerlinObserved262::from_observed_parts(
        first_octave,
        amplitudes.to_vec().into_boxed_slice(),
        noise_levels.into_boxed_slice(),
        lowest_input_factor,
        numerator / denominator,
    )
    .expect("fixed stock registered Perlin layout is bounded and finite")
}

/// Build a keyed 26.2 stock overworld noise from a signed world-seed bit
/// pattern without consulting any observed state or output fixture.
///
/// Constructed tables are independent per seed/key and immutable thereafter.
/// Exact admission scope: the three built-in keys only. This is a
/// 15-state/1,440-vector-qualified candidate, not general worldgen permission.
#[must_use]
pub fn from_stock_world_seed_candidate(
    seed_bits: u64,
    key: StockRegisteredNoiseKey262,
) -> RegisteredNormalObserved262 {
    let (first_octave, amplitudes, noise_hash) = key.parameters();

    let mut root = XoroshiroBits262::from_world_seed(seed_bits);
    let noise_positional = root.fork_positional();
    let mut named_random = named_fork(noise_positional, noise_hash);
    let first = construct_perlin(&mut named_random, first_octave, amplitudes);
    let second = construct_perlin(&mut named_random, first_octave, amplitudes);

    // The normal output correction uses first/last *nonzero* octave positions.
    let first_active = amplitudes.iter().position(|a| *a != 0.0)
        .expect("all three stock keys have at least one nonzero octave");
    let last_active = amplitudes.iter().rposition(|a| *a != 0.0)
        .expect("all three stock keys have a last nonzero octave");
    let active_range = u32::try_from(last_active - first_active + 1)
        .expect("the stock octave span is bounded by nine");
    let value_factor = (1.0 / 6.0) / (0.1 * (1.0 + 1.0 / f64::from(active_range)));

    RegisteredNormalObserved262::from_observed_parts(first, second, value_factor)
        .expect("stock normal factor is finite")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn xoro_seed_zero_and_signed_seed_high_bits_are_deterministic() {
        let mut random = XoroshiroBits262::from_world_seed(0);
        assert_eq!(random.next_u64(), 3_038_984_756_725_240_190);
        assert_eq!(random.next_u64(), 14_752_704_786_953_913_202);
        assert_ne!(
            XoroshiroBits262::from_world_seed(1).fork_positional(),
            XoroshiroBits262::from_world_seed(u64::MAX).fork_positional()
        );
    }

    #[test]
    fn named_forks_do_not_advance_or_mutate_cold_parents() {
        let mut parent = XoroshiroBits262::from_world_seed(0);
        let frozen = parent.fork_positional();
        let a = named_fork(frozen, StockRegisteredNoiseKey262::Temperature.parameters().2);
        let b = named_fork(frozen, StockRegisteredNoiseKey262::Temperature.parameters().2);
        assert_eq!(a.lo, b.lo);
        assert_eq!(a.hi, b.hi);
        assert_eq!(parent.next_u64(), 4_633_751_808_701_151_732);
    }
}
