//! Candidate `ImprovedNoise` cost probe: immutable seed initialization,
//! coherent 3D chunk-grid sampling and unrelated/scattered coordinates.
//!
//! This measures only the isolated 26.2 3D noise kernel, NOT noise routers,
//! full chunk generation, lighting or network-visible chunk latency.

use std::env;
use std::fmt::Write as _;
use std::fs;
use std::hint::black_box;
use std::time::Instant;

use helve_benchmark_support::collect_hardware_metadata;
use helve_world_gen::explicit_noise_stack_262::{ExplicitNoiseLayer262, ExplicitNoiseStack262};
use helve_world_gen::improved_noise_262::ImprovedNoise262;

#[derive(Clone, Copy)]
enum Case {
    Init,
    Coherent,
    CoherentReused,
    Scattered,
    StackScalar,
    StackBatched,
}

impl Case {
    const fn index(self) -> usize {
        match self {
            Self::Init => 0,
            Self::Coherent => 1,
            Self::CoherentReused => 2,
            Self::Scattered => 3,
            Self::StackScalar => 4,
            Self::StackBatched => 5,
        }
    }

    const fn name(self) -> &'static str {
        match self {
            Self::Init => "immutable_seed_setup",
            Self::Coherent => "coherent_grid_scalar",
            Self::CoherentReused => "coherent_grid_reused",
            Self::Scattered => "scattered_scalar",
            Self::StackScalar => "explicit_4layer_scalar",
            Self::StackBatched => "explicit_4layer_batched",
        }
    }
}

struct Config {
    points: usize,
    warmup: usize,
    rounds: usize,
    output: Option<String>,
}

fn args() -> Result<Config, String> {
    let mut cfg = Config {
        points: 4096,
        warmup: 5,
        rounds: 40,
        output: None,
    };
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        if arg == "--bench" {
            continue;
        }
        let value = args
            .next()
            .ok_or_else(|| format!("missing value for {arg}"))?;
        match arg.as_str() {
            "--points" => cfg.points = value.parse().map_err(|_| "invalid --points")?,
            "--warmup" => cfg.warmup = value.parse().map_err(|_| "invalid --warmup")?,
            "--rounds" => cfg.rounds = value.parse().map_err(|_| "invalid --rounds")?,
            "--output" => cfg.output = Some(value),
            _ => return Err(format!("unknown argument: {arg}")),
        }
    }
    if !(256..=262_144).contains(&cfg.points)
        || !cfg.points.is_multiple_of(256)
        || cfg.rounds == 0
        || cfg.rounds > 1000
        || cfg.warmup > 100
    {
        return Err(
            "requires 256..262144 points divisible by 256, 1..1000 rounds and <=100 warmups".into(),
        );
    }
    Ok(cfg)
}

fn run(case: Case, n: usize, generation: usize) -> (u128, u64, usize) {
    let seed = 0x9e37_79b9_7f4a_7c15_u64;
    let baseline = ImprovedNoise262::new(seed);
    let stack = ExplicitNoiseStack262::new([
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed), 1.0, 0.5),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(1)), 0.5, -0.25),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(2)), 2.0, 0.125),
        ExplicitNoiseLayer262::new(ImprovedNoise262::new(seed.wrapping_add(3)), 0.75, 0.375),
    ]);
    let start = Instant::now();
    let mut checksum = 0_u64;
    let evaluations = match case {
        Case::Init => {
            let instances = n.div_ceil(256);
            for i in 0..instances {
                let sampler =
                    ImprovedNoise262::new(seed.wrapping_add((generation * instances + i) as u64));
                checksum = checksum.rotate_left(7) ^ sampler.permutation_checksum();
                black_box(sampler);
            }
            instances
        }
        Case::Coherent | Case::CoherentReused => {
            let mut samples = [0_f64; 256];
            for tile in 0..n / 256 {
                let origin_x = 0.125;
                let origin_z = 0.25;
                let y = f64::from(u8::try_from(tile & 31).expect("5-bit tile height")) - 64.375;
                if matches!(case, Case::CoherentReused) {
                    baseline.sample_plane_16x16(origin_x, y, origin_z, &mut samples);
                } else {
                    for z in 0_u8..16 {
                        for x in 0_u8..16 {
                            samples[usize::from(z) * 16 + usize::from(x)] = baseline.sample(
                                origin_x + f64::from(x),
                                y,
                                origin_z + f64::from(z),
                            );
                        }
                    }
                }
                for &sample in &samples {
                    checksum = checksum.rotate_left(7) ^ sample.to_bits();
                }
            }
            n
        }
        Case::StackScalar | Case::StackBatched => {
            let mut samples = [0.0_f64; 256];
            for tile in 0..n / 256 {
                let origin_x = 0.125;
                let origin_z = 0.25;
                let y = f64::from(u8::try_from(tile & 31).expect("5-bit tile height")) - 64.375;
                if matches!(case, Case::StackBatched) {
                    stack.sample_plane_16x16(origin_x, y, origin_z, &mut samples);
                } else {
                    for iz in 0_u8..16 {
                        for ix in 0_u8..16 {
                            samples[usize::from(iz) * 16 + usize::from(ix)] =
                                stack.sample(origin_x + f64::from(ix), y, origin_z + f64::from(iz));
                        }
                    }
                }
                for &sample in &samples {
                    checksum = checksum.rotate_left(7) ^ sample.to_bits();
                }
            }
            n
        }
        Case::Scattered => {
            for i in 0..n {
                let hashed = (i as u64)
                    .wrapping_mul(0x9e37_79b9_7f4a_7c15)
                    .wrapping_add((generation as u64).wrapping_mul(0xbf58_476d_1ce4_e5b9));
                let x = f64::from((hashed & 4095) as u16) - 2048.125;
                let y = f64::from(((hashed >> 12) & 255) as u16) - 64.375;
                let z = f64::from(((hashed >> 20) & 4095) as u16) - 2048.875;
                checksum = checksum.rotate_left(7) ^ baseline.sample(x, y, z).to_bits();
            }
            n
        }
    };
    let elapsed = start.elapsed().as_nanos();
    black_box(checksum);
    (elapsed, checksum, evaluations)
}

struct Summary {
    count: usize,
    units: usize,
    total: u128,
    p50: u128,
    p95: u128,
    p99: u128,
    max: u128,
    checksum: u64,
}

fn summarize(mut observations: Vec<u128>, per_round: usize, checksum: u64) -> Summary {
    observations.sort_unstable();
    let index = |percent: usize| (observations.len() * percent).div_ceil(100) - 1;
    Summary {
        count: observations.len(),
        units: per_round,
        total: observations.iter().sum(),
        p50: observations[index(50)],
        p95: observations[index(95)],
        p99: observations[index(99)],
        max: observations[observations.len() - 1],
        checksum,
    }
}

fn main() -> Result<(), String> {
    let cfg = args()?;
    let mut timings: [Vec<u128>; 6] = std::array::from_fn(|_| Vec::new());
    let mut sums = [0_u64; 6];
    let mut evaluation_counts = [0_usize; 6];
    let cases = [
        Case::Init,
        Case::Coherent,
        Case::CoherentReused,
        Case::Scattered,
        Case::StackScalar,
        Case::StackBatched,
    ];
    for round in 0..cfg.warmup + cfg.rounds {
        // Rotate which case goes first to reduce systematic thermal bias.
        for j in 0..cases.len() {
            let case = cases[(round + j) % cases.len()];
            let (ns, digest, evaluations) = run(case, cfg.points, round);
            if round >= cfg.warmup {
                let i = case.index();
                timings[i].push(ns);
                sums[i] = sums[i].rotate_left(7) ^ digest;
                evaluation_counts[i] = evaluations;
            }
        }
    }
    // Same points, same tile order, same arithmetic, same per-element bit
    // checksum. Any mismatch invalidates the benchmark, regardless of time.
    if sums[Case::Coherent.index()] != sums[Case::CoherentReused.index()] {
        return Err("cached coherent plane differs from scalar output bits".into());
    }
    if sums[Case::StackScalar.index()] != sums[Case::StackBatched.index()] {
        return Err("batched explicit octave stack differs from scalar output bits".into());
    }
    let metadata = collect_hardware_metadata()?;
    let mut json = format!(
        "{{\"schema\":1,\"benchmark\":\"improved-noise-26_2-candidate\",        \"target_stage\":\"improved_noise\",        \"official_26_2_sample_vectors_tested_in_separate_ci\":160,        \"full_worldgen_source_admitted\":false,        \"full_chunk_latency_measured\":false,        \"strict_floating_point\":true,        \"points_per_round\":{},\"warmup_rounds\":{},        \"measured_rounds\":{},\"timing_units\":\"ns_per_batch\",        \"provenance\":{},\"cases\":[",
        cfg.points,
        cfg.warmup,
        cfg.rounds,
        metadata.to_json()
    );
    for (i, case) in cases.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        let summary = summarize(
            std::mem::take(&mut timings[i]),
            evaluation_counts[i],
            sums[i],
        );
        write!(
            &mut json,
            "{{\"name\":\"{}\",\"batches\":{},\"evaluations_per_batch\":{},            \"p50_ns\":{},\"p95_ns\":{},\"p99_ns\":{},            \"max_ns\":{},\"total_sample_ns\":{},\"checksum\":{}}}",
            case.name(),
            summary.count,
            summary.units,
            summary.p50,
            summary.p95,
            summary.p99,
            summary.max,
            summary.total,
            summary.checksum
        )
        .expect("writing to String cannot fail");
    }
    json.push_str("]}");
    if let Some(path) = &cfg.output {
        fs::write(path, format!("{json}\n"))
            .map_err(|error| format!("failed writing {path}: {error}"))?;
    } else {
        println!("{json}");
    }
    Ok(())
}
