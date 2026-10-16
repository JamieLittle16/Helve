//! COLD candidate bridge: dense official 26.2 heightmap oracle bytes to
//! the retained source-independent three-map heightmap reference projector.
//!
//! This adapter is **not** a source-admission certificate. An official runtime
//! probe alone cannot authorize a stock-client-visible world; the separate
//! Heightmap VAR/SEM source gate must still qualify all four predicates.
//! Deliberately no publication call site is installed in the live server.
//!
//! The existing Helve block-state identity is vanilla-global-ID ordered.
//! Every candidate byte must match the *independently qualified* non-air and
//! counted-fluid bits already embedded in generated state data. The other
//! two bits can only be independently certified through the source gate.
//! No HOT mutation, second world owner, copied fact array or registry lookup.

use helve_generated::{BLOCK_STATE_COUNT, BlockStateId, STATE_MUTATION_FLAGS};
use helve_world_chunk::{HeightmapStateFacts, HeightmapStateProperties};

const NON_AIR: u8 = 0b0001;
const MOTION: u8 = 0b0010;
const FLUID: u8 = 0b0100;
const LEAVES: u8 = 0b1000;

/// Strict source-identity, table-layout, and independent flag-check errors.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum HeightmapCandidateError {
    /// The oracle and generated 26.2 block-state universe are not identical.
    WrongCount { actual: usize, expected: usize },
    /// A record attempts to introduce unassigned bits.
    ReservedBits { state: usize, flags: u8 },
    /// The oracle non-air result contradicts the qualified state facts.
    NonAirMismatch { state: usize },
    /// The oracle raw-fluid result contradicts qualified counted-fluid facts.
    FluidMismatch { state: usize },
    /// An air state cannot block motion or belong to the leaves block class.
    ImpossibleAirProperties { state: usize, flags: u8 },
}

/// Stack-only borrow of one complete immutable official runtime candidate.
///
/// The byte-owner remains caller-owned; no `Vec`, map, closure, or
/// self-referential table is retained. Validation scans the 32,366-byte
/// candidate once at the COLD world-import boundary; each subsequent
/// state lookup is one dense bounds-proven read.
///
/// Successful validation proves target identity **consistency only**,
/// not the independent source/SEM admission of `blocksMotion()` or
/// `LeavesBlock` semantics.
///
/// # Errors
///
/// Rejects incomplete, corrupted, non-target, and internally inconsistent
/// candidate bytes before any world publication work is attempted.
#[derive(Clone, Copy, Debug)]
pub(crate) struct CandidateHeightmapFacts<'a> {
    flags: &'a [u8],
}

impl<'a> CandidateHeightmapFacts<'a> {
    pub(crate) fn from_oracle_bytes(flags: &'a [u8]) -> Result<Self, HeightmapCandidateError> {
        if flags.len() != BLOCK_STATE_COUNT {
            return Err(HeightmapCandidateError::WrongCount {
                actual: flags.len(),
                expected: BLOCK_STATE_COUNT,
            });
        }
        for (state, (&observed, &generated)) in
            flags.iter().zip(STATE_MUTATION_FLAGS.iter()).enumerate()
        {
            if observed & !(NON_AIR | MOTION | FLUID | LEAVES) != 0 {
                return Err(HeightmapCandidateError::ReservedBits {
                    state,
                    flags: observed,
                });
            }
            if (observed & NON_AIR != 0) != (generated & 1 != 0) {
                return Err(HeightmapCandidateError::NonAirMismatch { state });
            }
            // The generated mutation table's second bit means:
            // !isAir() && !getFluidState().isEmpty(). All official air
            // states have empty fluid and are independently checked below.
            if (observed & FLUID != 0) != (generated & 2 != 0) {
                return Err(HeightmapCandidateError::FluidMismatch { state });
            }
            if observed & NON_AIR == 0 && observed & (MOTION | LEAVES) != 0 {
                return Err(HeightmapCandidateError::ImpossibleAirProperties {
                    state,
                    flags: observed,
                });
            }
        }
        Ok(Self { flags })
    }
}

impl HeightmapStateFacts<BlockStateId> for CandidateHeightmapFacts<'_> {
    #[inline]
    fn properties(&self, state: BlockStateId) -> HeightmapStateProperties {
        let flags = self.flags[state.as_usize()];
        HeightmapStateProperties::new(
            flags & NON_AIR != 0,
            flags & MOTION != 0,
            flags & FLUID != 0,
            flags & LEAVES != 0,
        )
    }
}

#[cfg(test)]
mod tests {
    use helve_generated::{AIR, GeneratedStateFacts};
    use helve_types::{ChunkGeneration, ChunkPos};
    use helve_world_chunk::{
        ClientHeightmapKind, ClientHeightmaps, HeightmapStateFacts, LiveChunkCore,
    };
    use helve_world_contract::{BlockSection, SectionBlockPos};
    use helve_world_reference::DirectBlockSection;

    use super::{
        BLOCK_STATE_COUNT, BlockStateId, CandidateHeightmapFacts, FLUID, HeightmapCandidateError,
        LEAVES, MOTION, NON_AIR, STATE_MUTATION_FLAGS,
    };

    fn consistent_synthetic_oracle() -> Vec<u8> {
        // NOT an official runtime oracle. Reuses only existing admitted bits;
        // extra motion/leaves bits are intentionally absent in these tests.
        STATE_MUTATION_FLAGS
            .iter()
            .map(|&facts| (facts & 1) | ((facts & 2) << 1))
            .collect()
    }

    #[test]
    fn exact_universe_and_existing_independent_flags_fail_closed() {
        let mut candidate = consistent_synthetic_oracle();
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate[..candidate.len() - 1])
                .unwrap_err(),
            HeightmapCandidateError::WrongCount {
                actual: BLOCK_STATE_COUNT - 1,
                expected: BLOCK_STATE_COUNT,
            }
        );
        candidate[0] = 0x80;
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate).unwrap_err(),
            HeightmapCandidateError::ReservedBits {
                state: 0,
                flags: 0x80,
            }
        );
        candidate[0] = NON_AIR;
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate).unwrap_err(),
            HeightmapCandidateError::NonAirMismatch { state: 0 }
        );
        candidate[0] = FLUID;
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate).unwrap_err(),
            HeightmapCandidateError::FluidMismatch { state: 0 }
        );
        candidate[0] = MOTION;
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate).unwrap_err(),
            HeightmapCandidateError::ImpossibleAirProperties {
                state: 0,
                flags: MOTION,
            }
        );
        candidate[0] = LEAVES;
        assert_eq!(
            CandidateHeightmapFacts::from_oracle_bytes(&candidate).unwrap_err(),
            HeightmapCandidateError::ImpossibleAirProperties {
                state: 0,
                flags: LEAVES,
            }
        );
    }

    #[test]
    fn borrowed_dense_table_is_pointer_stable_and_reuses_existing_state_ids() {
        let flags = consistent_synthetic_oracle();
        let ptr = flags.as_ptr();
        let facts = CandidateHeightmapFacts::from_oracle_bytes(&flags).unwrap();
        assert_eq!(ptr, flags.as_ptr());
        for id in [0_u32, 1, 2, 123, 32_365] {
            let state = BlockStateId::new(id).unwrap();
            let observed = facts.properties(state);
            let original = STATE_MUTATION_FLAGS[state.as_usize()];
            assert_eq!(observed.non_air(), original & 1 != 0);
            assert_eq!(observed.fluid_non_empty(), original & 2 != 0);
        }
        assert!(!facts.properties(AIR).non_air());
    }

    #[test]
    fn official_runtime_candidate_feeds_real_source_heightmap_reference() {
        // This is exercised with all *actual* oracle bytes only by the
        // dedicated R2C Official Heightmap Facts workflow. Ordinary Rust CI
        // still runs the hermetic rejection tests above.
        let Some(path) = std::env::var_os("HELVE_R2C_HEIGHTMAP_CANDIDATE") else {
            return;
        };
        let bytes = std::fs::read(path).expect("official oracle candidate is present");
        let facts = CandidateHeightmapFacts::from_oracle_bytes(&bytes)
            .expect("official heightmap facts must match qualified mutation facts");

        // Select the necessary behavioural cases *by their oracle results*.
        // No block names, hand-picked vanilla IDs, or approximations.
        let selected_leaf = bytes
            .iter()
            .position(|&f| f & (NON_AIR | MOTION | LEAVES) == (NON_AIR | MOTION | LEAVES))
            .expect("source runtime has motion-blocking leaf states");
        let selected_ground = bytes
            .iter()
            .position(|&f| f & (NON_AIR | MOTION | LEAVES) == (NON_AIR | MOTION))
            .expect("source runtime has non-leaf motion-blocking states");
        let leaf = BlockStateId::new(u32::try_from(selected_leaf).unwrap()).unwrap();
        let ground = BlockStateId::new(u32::try_from(selected_ground).unwrap()).unwrap();

        let generated = GeneratedStateFacts;
        let mut lower = DirectBlockSection::filled(AIR, &generated);
        let mut upper = DirectBlockSection::filled(AIR, &generated);
        lower.replace(SectionBlockPos::new(1, 2, 3).unwrap(), ground, &generated);
        upper.replace(SectionBlockPos::new(1, 13, 3).unwrap(), leaf, &generated);

        let core = LiveChunkCore::new(
            ChunkPos { x: 0, z: 0 },
            ChunkGeneration(1),
            -1,
            vec![lower, upper],
        )
        .expect("two-section coherent source chunk");
        let heights = ClientHeightmaps::derive(&core, &facts);
        let column = 1 + 16 * 3;
        assert_eq!(
            heights.relative_heights(ClientHeightmapKind::WorldSurface)[column],
            30
        );
        assert_eq!(
            heights.relative_heights(ClientHeightmapKind::MotionBlocking)[column],
            30
        );
        assert_eq!(
            heights.relative_heights(ClientHeightmapKind::MotionBlockingNoLeaves)[column],
            3
        );
    }
}
