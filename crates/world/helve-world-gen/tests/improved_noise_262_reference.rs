//! Bit-for-bit acceptance against the 160 source-free JVM captures supplied
//! for the pinned Minecraft Java 26.2 ImprovedNoise three-coordinate overload.
//! Fixture preserves the archive/runtime/body identities and originating JSON
//! SHA-256. Passing does NOT substitute for independent source/VAR/SEM closure.

use std::collections::BTreeMap;

use helve_world_gen::improved_noise_262::ImprovedNoise262;

const ORACLE: &str = include_str!("data/improved_noise_26_2_rawbits.tsv");

fn hex64(value: &str) -> u64 {
    u64::from_str_radix(
        value
            .strip_prefix("0x")
            .expect("oracle must contain 0x prefix"),
        16,
    )
    .expect("oracle has exactly 64-bit hexadecimal input/output")
}

#[test]
fn all_160_pinned_official_jvm_samples_are_bit_exact() {
    let mut samplers = BTreeMap::<u64, ImprovedNoise262>::new();
    let mut samples = 0_usize;
    for (line_number, line) in ORACLE.lines().enumerate() {
        if line.starts_with('#') || line.is_empty() {
            continue;
        }
        let values: Vec<_> = line.split_whitespace().collect();
        assert_eq!(values.len(), 5, "fixture row {} malformed", line_number + 1);
        let seed = hex64(values[0]);
        let x = f64::from_bits(hex64(values[1]));
        let y = f64::from_bits(hex64(values[2]));
        let z = f64::from_bits(hex64(values[3]));
        let expected = hex64(values[4]);
        let sampler = samplers
            .entry(seed)
            .or_insert_with(|| ImprovedNoise262::new(seed));
        let actual = sampler.sample(x, y, z).to_bits();
        assert_eq!(
            actual,
            expected,
            "source-free 26.2 oracle mismatch: line {}, seed {seed:#018x}, x {:#018x}, y {:#018x}, z {:#018x}, actual {actual:#018x}, expected {expected:#018x}",
            line_number + 1,
            x.to_bits(),
            y.to_bits(),
            z.to_bits()
        );
        samples += 1;
    }
    assert_eq!(samples, 160, "the complete frozen oracle must be checked");
    assert_eq!(samplers.len(), 5, "exactly five distinct official seeds");
}

#[test]
fn seed_setup_is_deterministic_and_sampling_is_read_only() {
    for seed in [0_u64, 1, u64::MAX, 1_u64 << 63, 0x9e37_79b9_7f4a_7c15] {
        let a = ImprovedNoise262::new(seed);
        let b = ImprovedNoise262::new(seed);
        assert_eq!(a.permutation_checksum(), b.permutation_checksum());
        let p = (1024.125, -63.875, -4096.375);
        let baseline = a.sample(p.0, p.1, p.2).to_bits();
        for _ in 0..100 {
            assert_eq!(a.sample(p.0, p.1, p.2).to_bits(), baseline);
        }
        assert_eq!(b.sample(p.0, p.1, p.2).to_bits(), baseline);
    }
}

#[test]
fn independent_cold_workers_do_not_share_mutable_rng_state() {
    let samplers: Vec<_> = [0, 1, u64::MAX, 0x9e37_79b9_7f4a_7c15]
        .into_iter()
        .map(ImprovedNoise262::new)
        .collect();
    std::thread::scope(|scope| {
        for sampler in &samplers {
            scope.spawn(move || {
                let baseline = sampler.sample(-31.125, 319.875, 31.125).to_bits();
                for i in 0..1_000 {
                    let offset = f64::from(i);
                    let _ = sampler.sample(offset / 4.0, 0.25, -offset / 8.0);
                    assert_eq!(sampler.sample(-31.125, 319.875, 31.125).to_bits(), baseline);
                }
            });
        }
    });
}
