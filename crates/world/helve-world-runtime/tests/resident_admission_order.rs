use helve_types::{ChunkGeneration, ChunkPos, DimensionId, DimensionTypeId};
use helve_world_reference::DirectBlockSection;
use helve_world_runtime::{DimensionInstance, DimensionRuntimeProfile, LoadChunkError};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum State {
    Air,
}

fn profile() -> DimensionRuntimeProfile {
    DimensionRuntimeProfile::new(DimensionTypeId(1), 0, 32, true)
        .expect("two-section regression profile")
}

fn sections(count: usize) -> Vec<DirectBlockSection<State>> {
    (0..count)
        .map(|_| DirectBlockSection::filled_without_facts(State::Air))
        .collect()
}

#[test]
fn duplicate_admission_preempts_payload_validation_without_consuming_generation() {
    let profile = profile();
    let mut dimension = DimensionInstance::new(DimensionId(1), profile);
    let first_position = ChunkPos { x: 0, z: 0 };

    let first = dimension
        .load_chunk(first_position, sections(profile.section_count()))
        .expect("first valid chunk becomes resident");
    assert_eq!(first.generation, ChunkGeneration(1));

    // The replacement payload is deliberately malformed for this dimension. The lifecycle contract
    // probes residency first, so duplicate identity must win over payload validation and the build
    // path must never run.
    assert_eq!(
        dimension.load_chunk(first_position, sections(1)),
        Err(LoadChunkError::AlreadyResident { handle: first })
    );

    let second_position = ChunkPos { x: 1, z: 0 };
    let second = dimension
        .load_chunk(second_position, sections(profile.section_count()))
        .expect("next vacant chunk becomes resident");
    assert_eq!(
        second.generation,
        ChunkGeneration(2),
        "rejected duplicate must not consume a generation"
    );
}
