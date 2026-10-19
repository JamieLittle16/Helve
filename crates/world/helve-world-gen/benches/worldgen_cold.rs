//! Source-free COLD worldgen cost accounting. Not a Minecraft 26.2 noise
//! benchmark: `SteppedSurface` is deliberately NOT the vanilla noise router.

use std::convert::Infallible;
use std::env;
use std::fmt::Write as _;
use std::fs;
use std::hint::black_box;
use std::time::Instant;

use helve_benchmark_support::collect_hardware_metadata;
use helve_types::{ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
use helve_world_contract::{
    BIOME_SECTION_CELLS, BLOCK_SECTION_CELLS, BlockStateFacts, SectionBiomePos, SectionStateFacts,
};
use helve_world_gen::{GeneratedSectionBuilder, SectionSamples, SteppedSurface, SurfacePalette};
use helve_world_reference::{DirectBiomeSection, DirectBlockSection};
use helve_world_runtime::{DimensionRuntimeProfile, SemanticDimensionInstance};

type World = SemanticDimensionInstance<u8, DirectBlockSection<u8>, u8, DirectBiomeSection<u8>>;

#[derive(Clone, Copy, Debug)]
struct Facts;

impl BlockStateFacts<u8> for Facts {
    #[inline]
    fn facts(&self, state: u8) -> SectionStateFacts {
        SectionStateFacts::new(state != 0, false, false, false)
    }
}

#[derive(Default)]
struct ReferenceBuilder;

impl GeneratedSectionBuilder<u8, u8> for ReferenceBuilder {
    type Blocks = DirectBlockSection<u8>;
    type Biomes = DirectBiomeSection<u8>;
    type Error = Infallible;

    fn blocks(
        &mut self,
        samples: SectionSamples<'_, u8, BLOCK_SECTION_CELLS>,
    ) -> Result<Self::Blocks, Self::Error> {
        Ok(match samples {
            SectionSamples::Uniform(state) => DirectBlockSection::filled(state, &Facts),
            SectionSamples::Dense(cells) => DirectBlockSection::from_decoded_cells(cells, &Facts),
        })
    }

    fn biomes(
        &mut self,
        samples: SectionSamples<'_, u8, BIOME_SECTION_CELLS>,
    ) -> Result<Self::Biomes, Self::Error> {
        Ok(match samples {
            SectionSamples::Uniform(id) => DirectBiomeSection::filled(id),
            SectionSamples::Dense(cells) => {
                let mut section = DirectBiomeSection::filled(cells[0]);
                section.fill_with(|x, y, z| {
                    cells[SectionBiomePos::new(x, y, z)
                        .expect("quart coordinates are bounded")
                        .index()]
                });
                section
            }
        })
    }
}

const PALETTE: SurfacePalette<u8, u8> = SurfacePalette {
    air: 0,
    solid: 1,
    biome: 2,
};

#[derive(Clone, Copy)]
enum Case {
    Sampler,
    Construct,
    Admit,
}

impl Case {
    const fn name(self) -> &'static str {
        match self {
            Self::Sampler => "256_column_samples",
            Self::Construct => "sample_and_construct_sections",
            Self::Admit => "sample_construct_and_resident_install",
        }
    }

    const fn index(self) -> usize {
        match self {
            Self::Sampler => 0,
            Self::Construct => 1,
            Self::Admit => 2,
        }
    }
}

#[derive(Debug)]
struct Config {
    chunks: usize,
    warmup: usize,
    rounds: usize,
    output: Option<String>,
}

fn config() -> Result<Config, String> {
    let mut cfg = Config {
        chunks: 32,
        warmup: 3,
        rounds: 15,
        output: None,
    };
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        let value = args.next().ok_or(format!("missing value for {arg}"))?;
        match arg.as_str() {
            "--chunks" => cfg.chunks = value.parse().map_err(|_| "invalid --chunks")?,
            "--warmup" => cfg.warmup = value.parse().map_err(|_| "invalid --warmup")?,
            "--rounds" => cfg.rounds = value.parse().map_err(|_| "invalid --rounds")?,
            "--output" => cfg.output = Some(value),
            _ => return Err(format!("unknown argument: {arg}")),
        }
    }
    if !(1..=4096).contains(&cfg.chunks) || !(1..=100).contains(&cfg.rounds) || cfg.warmup > 20 {
        return Err("requires 1..=4096 chunks, 1..=100 rounds, <=20 warmups".into());
    }
    Ok(cfg)
}

fn position(i: usize) -> ChunkPos {
    ChunkPos {
        x: i32::try_from(i % 64).expect("bounded chunk x") - 32,
        z: i32::try_from(i / 64).expect("bounded chunk z") - 32,
    }
}

fn profile() -> DimensionRuntimeProfile {
    DimensionRuntimeProfile::new(DimensionTypeId(1), -64, 384, true)
        .expect("bounded Overworld-like lattice")
}

fn perform(case: Case, cfg: &Config, record: &mut Vec<u128>) -> Result<(), String> {
    let rule = SteppedSurface::new(0x0ace_cafe_cafe_9e13, -8, 29);
    let profile = profile();
    let mut builder = ReferenceBuilder;
    let mut world = World::with_chunk_capacity(DimensionId(1), profile, cfg.chunks);
    for index in 0..cfg.chunks {
        let pos = position(index);
        let start = Instant::now();
        match case {
            Case::Sampler => {
                let mut sum = 0_i64;
                for z in 0..16 {
                    for x in 0..16 {
                        let world_x = i64::from(pos.x) * 16 + x;
                        let world_z = i64::from(pos.z) * 16 + z;
                        sum = sum.wrapping_add(rule.surface_y(world_x, world_z));
                    }
                }
                black_box(sum);
            }
            Case::Construct => {
                let chunk = rule
                    .generate_chunk(pos, ChunkGeneration(1), profile, PALETTE, &mut builder)
                    .map_err(|e| format!("construct failed: {e:?}"))?;
                black_box(chunk.block_masks().non_air_bits());
                black_box(chunk);
            }
            Case::Admit => {
                let handle = world
                    .admit_chunk(pos, |generation, p| {
                        rule.generate_chunk(pos, generation, p, PALETTE, &mut builder)
                    })
                    .map_err(|e| format!("admission failed: {e:?}"))?;
                black_box(world.resolve_chunk(handle).map_err(|e| format!("{e:?}"))?);
            }
        }
        record.push(start.elapsed().as_nanos());
    }
    black_box(world.resident_chunk_count());
    Ok(())
}

#[derive(Debug)]
struct Stats {
    n: usize,
    p50_ns: u128,
    p95_ns: u128,
    p99_ns: u128,
    max_ns: u128,
    total_ns: u128,
}

fn stats(mut samples: Vec<u128>) -> Result<Stats, String> {
    if samples.is_empty() {
        return Err("cannot summarize zero benchmark samples".to_owned());
    }
    let total_ns = samples.iter().sum();
    samples.sort_unstable();
    let percentile = |p: usize| samples[(samples.len() * p).div_ceil(100) - 1];
    Ok(Stats {
        n: samples.len(),
        p50_ns: percentile(50),
        p95_ns: percentile(95),
        p99_ns: percentile(99),
        max_ns: samples[samples.len() - 1],
        total_ns,
    })
}

fn main() -> Result<(), String> {
    let cfg = config()?;
    let mut measured = [Vec::<u128>::new(), Vec::<u128>::new(), Vec::<u128>::new()];
    for i in 0..(cfg.warmup + cfg.rounds) {
        // Balanced rotation mitigates (but does not eliminate) thermal and
        // frequency-order bias. A cold resident directory is made per case.
        let order = [Case::Sampler, Case::Construct, Case::Admit];
        for j in 0..3 {
            let case = order[(i + j) % 3];
            let mut times = Vec::with_capacity(cfg.chunks);
            perform(case, &cfg, &mut times)?;
            if i >= cfg.warmup {
                measured[case.index()].extend(times);
            }
        }
    }
    let hardware = collect_hardware_metadata()?;
    let summaries = [
        stats(std::mem::take(&mut measured[0]))?,
        stats(std::mem::take(&mut measured[1]))?,
        stats(std::mem::take(&mut measured[2]))?,
    ];
    let mut json = format!(
        "{{\"schema\":1,\"type\":\"NON_VANILLA_STEPPED_SURFACE_BASELINE\",\
        \"strict_minecraft_26_2_parity\":false,\
        \"worldgen_noise_26_2_measured\":false,\
        \"sections\":24,\"min_y\":-64,\"chunks_per_round\":{},\
        \"warmup_rounds\":{},\"measured_rounds\":{},\"units\":\"ns\",\
        \"provenance\":{},\"cases\":[",
        cfg.chunks,
        cfg.warmup,
        cfg.rounds,
        hardware.to_json()
    );
    for (i, summary) in summaries.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        write!(
            &mut json,
            "{{\"name\":\"{}\",\"samples\":{},\"p50_ns\":{},\
            \"p95_ns\":{},\"p99_ns\":{},\"max_ns\":{},\
            \"total_sample_ns\":{}}}",
            [Case::Sampler, Case::Construct, Case::Admit][i].name(),
            summary.n,
            summary.p50_ns,
            summary.p95_ns,
            summary.p99_ns,
            summary.max_ns,
            summary.total_ns
        )
        .expect("writing to String cannot fail");
    }
    json.push_str("]}");
    if let Some(path) = &cfg.output {
        fs::write(path, format!("{json}\n")).map_err(|e| format!("write {path}: {e}"))?;
    } else {
        println!("{json}");
    }
    Ok(())
}
