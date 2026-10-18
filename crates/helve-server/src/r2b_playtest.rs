//! Stock-client development composition for the replay-free R2B boundary.
//!
//! The cold image contains source-admitted Configuration plus exactly three immutable shared R2B
//! projections. It has no captured-Play publication section. After `WorldProjectionReady`, this
//! temporary owner keeps the exact R2B driver/read scratch, claims teleport and keep-alive normally,
//! and discards currently-unowned gameplay frames only until R2C exists.

use std::convert::Infallible;
use std::fmt;
use std::fs::{self, File};
use std::io::{self, BufReader, Read, Write};
use std::net::TcpStream;
use std::path::{Path, PathBuf};

#[cfg(test)]
use crate::r2c_cold_demo_import::R2cSourceAdmission;
use crate::r2c_cold_demo_import::{
    ColdImportedView, R2cColdWorldHost, SourceAdmittedPlayPublisher,
    import_selected_cold_world_host,
};
use crate::r2c_configured_biomes::with_candidate_biomes_from_context;
use crate::r2c_play_inbound::R2cPlayInboundStep;
use std::time::{Duration, Instant};

use helve_connection_driver::{DriverError, OutboundBatch, TransactionResult};
use helve_generated::BLOCK_STATE_COUNT;
use helve_target_26_2::{
    R1xContextError, Target26_2R1xContext,
    play_liveness::PLAY_LIVENESS_POLICY,
    r2b::{
        BootstrapGameMode, BootstrapWeather, ChangeDifficultyPayload, ClockFullSyncPayload,
        ClockUpdate, CommandPermissionProfile, CommandProjectionArtifact, CommandProjectionKey,
        DefaultSpawnPayload, Difficulty26_2, FreshCommonSpawnInfo, FreshEmptyInventoryPayload,
        FreshLoginFlags, FreshLoginPayload, FreshR2bBootstrapSnapshot, HeldSlotPayload,
        InitialPlayerInfoEntry, PermissionEntityEventPayload, PermissionLevelEvent,
        PlayBootstrapImage26_2, PlayerAbilitiesPayload, PlayerAbilityFlags,
        ProjectionArtifactError, ProjectionRevision, RecipeBookSettingFlags,
        RecipeBookSettingsPayload, RecipeProjectionArtifact, RecipeProjectionKey,
        ServerDataProjection, ServerDataProjectionArtifact, ServerDataProjectionKey,
        TeleportAckResult, TeleportDestination, TickingStatePayload, TickingStepPayload,
        WorldBorderPayload,
    },
};
use helve_world_import::{
    ChunkCompression, ChunkPayloadDecoder, DeflateChunkPayloadDecoder, NbtLimits,
    require_target_26_2_level_metadata,
};

use crate::{
    R2bEntryOutcome, R2bLivenessProcess, R2bPlayError, R2bPlayInbound, R2bPlayProcess,
    R2bPlaySession, R2bServerError, ServerSessionEpoch, enter_r2b_play_blocking_transport,
};

const MAGIC: [u8; 8] = *b"CRR2B001";
const EXPECTED_PROTOCOL: u32 = 776;
const EXPECTED_CONFIGURATION_COUNT: usize = 34;
const EXPECTED_CONFIGURATION_BYTES: usize = 44_430;
const MAX_BODY_BYTES: usize = 65_536;
const HEADER_BYTES: u64 = 88;
const LENGTH_PREFIX_BYTES: u64 = 37 * 4;
const MAX_SHARED_BODY_BYTES: u64 = 3 * 65_536;
const MAX_IMAGE_BYTES: u64 = HEADER_BYTES
    + LENGTH_PREFIX_BYTES
    + EXPECTED_CONFIGURATION_BYTES as u64
    + MAX_SHARED_BODY_BYTES;
const ACTIONS_PER_SERVICE: usize = 32;
// Bounded COLD saved-world metadata only: no packet, world-cell or HOT allocation.
const MAX_R2C_LEVEL_FILE_BYTES: u64 = 4 * 1024 * 1024;
const MAX_R2C_LEVEL_NBT_BYTES: usize = 8 * 1024 * 1024;
const _: () = assert!(ACTIONS_PER_SERVICE > 0);

const EXPECTED_SOURCE_SHA256: [u8; 32] = [
    0x1e, 0x9b, 0xca, 0x3d, 0xff, 0x83, 0xcd, 0x83, 0xe7, 0x90, 0x5f, 0x88, 0x10, 0xf1, 0xec, 0x98,
    0x99, 0x36, 0x1f, 0xa2, 0xdc, 0x83, 0xfe, 0x89, 0x3b, 0xb4, 0x8b, 0xee, 0xb0, 0x4d, 0xf7, 0x50,
];
const EXPECTED_CAPTURE_SHA256: [u8; 32] = [
    0x11, 0xea, 0xd8, 0xde, 0x74, 0xdf, 0x70, 0xb4, 0x0d, 0x7f, 0xb0, 0x45, 0xff, 0x95, 0x61, 0xf0,
    0x6f, 0x6e, 0x24, 0x23, 0x87, 0x65, 0xd4, 0x14, 0x1a, 0x1d, 0x09, 0x0c, 0xab, 0x54, 0x6b, 0x57,
];

const LEVELS: [&str; 3] = [
    "minecraft:overworld",
    "minecraft:the_nether",
    "minecraft:the_end",
];
const CLOCKS: [ClockUpdate; 2] = [
    ClockUpdate {
        registry_id: 0,
        total_ticks: 5_503,
        partial_tick: 0.0,
        rate: 1.0,
    },
    ClockUpdate {
        registry_id: 1,
        total_ticks: 5_503,
        partial_tick: 0.0,
        rate: 1.0,
    },
];
const SELF: InitialPlayerInfoEntry<'static> = InitialPlayerInfoEntry {
    profile_id: [
        0x68, 0x20, 0x14, 0xfe, 0xad, 0x63, 0x36, 0x99, 0xaa, 0xda, 0x79, 0xaa, 0x08, 0xd9, 0x5b,
        0x45,
    ],
    name: "Stato16",
    game_mode: BootstrapGameMode::Survival,
    listed: true,
    latency: 0,
    list_order: 0,
    show_hat: true,
};

/// Cold-path R2B playtest-image failure.
#[derive(Debug)]
pub enum R2bPlaytestImageError {
    /// Filesystem access failed.
    Io {
        /// Stable I/O classification.
        kind: io::ErrorKind,
        /// Diagnostic detail.
        message: String,
    },
    /// Image path resolved to a symbolic link.
    Symlink,
    /// Image path was not a regular file.
    NotFile,
    /// File exceeds the maximum possible bounded playtest image.
    FileTooLarge { observed: u64, maximum: u64 },
    /// Header magic did not identify the R2B playtest format.
    Magic,
    /// Protocol differs from Minecraft Java 26.2.
    Protocol { observed: u32 },
    /// Source archive commitment differs from the pinned source archive.
    SourceCommitment,
    /// Capture commitment differs from the qualified selected capture.
    CaptureCommitment,
    /// Configuration count differs from the sealed selected route.
    ConfigurationCount { observed: usize },
    /// Configuration body-byte total differs from the selected runtime route.
    ConfigurationBytes { observed: usize },
    /// One body is empty or exceeds the finite packet-body bound.
    BodyLength { index: usize, observed: usize },
    /// Decoded Configuration aggregate differs from the header declaration.
    AggregateMismatch { declared: usize, observed: usize },
    /// Undeclared bytes remained after the fixed body sequence.
    TrailingData,
    /// Target-level Configuration validation rejected the image.
    Context(R1xContextError),
    /// One shared R2B projection carried a malformed or wrong packet identity.
    Projection(ProjectionArtifactError),
}

impl fmt::Display for R2bPlaytestImageError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io { kind, message } => {
                write!(formatter, "playtest image I/O {kind:?}: {message}")
            }
            Self::Symlink => formatter.write_str("playtest image must not be a symlink"),
            Self::NotFile => formatter.write_str("playtest image must be a regular file"),
            Self::FileTooLarge { observed, maximum } => write!(
                formatter,
                "playtest image is {observed} bytes, exceeding the {maximum}-byte bound"
            ),
            Self::Magic => formatter.write_str("playtest image magic mismatch"),
            Self::Protocol { observed } => write!(
                formatter,
                "playtest image protocol mismatch: expected {EXPECTED_PROTOCOL}, got {observed}"
            ),
            Self::SourceCommitment => {
                formatter.write_str("playtest image source commitment mismatch")
            }
            Self::CaptureCommitment => {
                formatter.write_str("playtest image capture commitment mismatch")
            }
            Self::ConfigurationCount { observed } => write!(
                formatter,
                "playtest Configuration count mismatch: expected {EXPECTED_CONFIGURATION_COUNT}, got {observed}"
            ),
            Self::ConfigurationBytes { observed } => write!(
                formatter,
                "playtest Configuration bytes mismatch: expected {EXPECTED_CONFIGURATION_BYTES}, got {observed}"
            ),
            Self::BodyLength { index, observed } => {
                write!(
                    formatter,
                    "playtest body {index} has invalid {observed}-byte length"
                )
            }
            Self::AggregateMismatch { declared, observed } => write!(
                formatter,
                "playtest Configuration aggregate mismatch: declared {declared}, decoded {observed}"
            ),
            Self::TrailingData => formatter.write_str("playtest image contains trailing data"),
            Self::Context(error) => write!(formatter, "playtest Configuration rejected: {error:?}"),
            Self::Projection(error) => {
                write!(formatter, "playtest shared projection rejected: {error:?}")
            }
        }
    }
}

impl From<R1xContextError> for R2bPlaytestImageError {
    fn from(value: R1xContextError) -> Self {
        Self::Context(value)
    }
}

impl From<ProjectionArtifactError> for R2bPlaytestImageError {
    fn from(value: ProjectionArtifactError) -> Self {
        Self::Projection(value)
    }
}

/// Process-owned replay-free inputs for the selected stock-client R2B playtest.
#[derive(Debug)]
pub struct R2bPlaytestImage {
    configuration: Target26_2R1xContext,
    bootstrap: PlayBootstrapImage26_2,
    server_data: ServerDataProjectionArtifact,
}

/// Why the temporary post-R2B playtest owner ended.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum R2bPlaytestExit {
    /// Connection ended before the explicit world-projection handoff.
    SessionClosedBeforeWorld,
    /// Peer closed before the explicit world-projection handoff.
    PeerEofBeforeWorld,
    /// Peer closed after reaching `WorldProjection`.
    LivePeerEof {
        /// Whether the initial absolute teleport was acknowledged exactly.
        teleport_acknowledged: bool,
        /// Valid keep-alive replies committed through the canonical R2B session.
        accepted_keep_alives: u64,
        /// Currently-unowned complete Play frames discarded by the temporary owner.
        discarded_world_frames: u64,
        /// Last source-compatible smoothed latency.
        latency_ms: i32,
    },
    /// Initial teleport acknowledgement was stale, wrong, duplicate, or unsolicited.
    InvalidTeleportAcknowledgement(TeleportAckResult),
    /// A keep-alive reply did not match the outstanding challenge.
    InvalidKeepAlive,
    /// One outstanding keep-alive survived through its next deadline.
    KeepAliveTimedOut,
    /// Closed-listener timeout fired unexpectedly in this development composition.
    ClosedTimedOut,
    /// Monotonic time exceeded the admitted wire domain.
    ClockInvalid,
}

/// Opt-in, **non-publishing** first world preview for one R2B development session.
/// The selected save root follows the exact official 26.2 namespaced
/// Overworld layout; optional COLD inspection never sends a Play packet.
#[derive(Clone, Debug)]
pub struct R2cColdWorldPlan {
    world: PathBuf,
    /// Immutable, explicitly selected candidate table (never source admitted).
    heightmap_candidate: Option<Box<[u8]>>,
}

#[derive(Debug)]
pub enum R2cColdWorldPlanError {
    Io {
        operation: &'static str,
        kind: io::ErrorKind,
    },
    Symlink {
        component: &'static str,
    },
    NotDirectory {
        component: &'static str,
    },
    NotFile {
        component: &'static str,
    },
    WrongHeightmapBytes {
        observed: u64,
        expected: usize,
    },
    HeightmapCandidate(String),
    /// The selected saved-world `level.dat` grew or exceeded its COLD cap.
    LevelFileTooLarge {
        observed: u64,
        maximum: u64,
    },
    /// Gzip framing/checksum or bounded NBT saved-world version was rejected.
    LevelMetadata(String),
}

impl R2cColdWorldPlan {
    /// Check the official 26.2 namespaced Overworld source directory and
    /// root save metadata before binding the network socket. The region
    /// visitor still takes a dimension directory containing `region/`;
    /// changing that generic importer's contract would duplicate work.
    /// This identity check is necessary, not the final level.dat profile or
    /// selected-pack source admission, and never authorizes publication.
    ///
    /// # Errors
    /// Fails closed on missing, nonregular or symlinked components.
    pub fn new(world: PathBuf) -> Result<Self, R2cColdWorldPlanError> {
        let dimensions = world.join("dimensions");
        let namespace = dimensions.join("minecraft");
        let overworld = namespace.join("overworld");
        let region = overworld.join("region");
        for (component, path) in [
            ("world", world.as_path()),
            ("dimensions", dimensions.as_path()),
            ("minecraft", namespace.as_path()),
            ("overworld", overworld.as_path()),
            ("region", region.as_path()),
        ] {
            let metadata =
                fs::symlink_metadata(path).map_err(|error| R2cColdWorldPlanError::Io {
                    operation: component,
                    kind: error.kind(),
                })?;
            if metadata.file_type().is_symlink() {
                return Err(R2cColdWorldPlanError::Symlink { component });
            }
            if !metadata.is_dir() {
                return Err(R2cColdWorldPlanError::NotDirectory { component });
            }
        }
        let level = world.join("level.dat");
        let metadata = fs::symlink_metadata(&level).map_err(|error| R2cColdWorldPlanError::Io {
            operation: "level.dat",
            kind: error.kind(),
        })?;
        if metadata.file_type().is_symlink() {
            return Err(R2cColdWorldPlanError::Symlink {
                component: "level.dat",
            });
        }
        if !metadata.is_file() {
            return Err(R2cColdWorldPlanError::NotFile {
                component: "level.dat",
            });
        }
        if metadata.len() > MAX_R2C_LEVEL_FILE_BYTES {
            return Err(R2cColdWorldPlanError::LevelFileTooLarge {
                observed: metadata.len(),
                maximum: MAX_R2C_LEVEL_FILE_BYTES,
            });
        }
        // The metadata length can race with a write: limit the actual read
        // independently. Never trust a file-size precheck to cap allocation.
        let initial_capacity = usize::try_from(metadata.len()).map_err(|_| {
            R2cColdWorldPlanError::LevelFileTooLarge {
                observed: metadata.len(),
                maximum: MAX_R2C_LEVEL_FILE_BYTES,
            }
        })?;
        let mut compressed = Vec::new();
        compressed
            .try_reserve_exact(initial_capacity)
            .map_err(|_| {
                R2cColdWorldPlanError::LevelMetadata("bounded level.dat allocation failed".into())
            })?;
        File::open(&level)
            .map_err(|error| R2cColdWorldPlanError::Io {
                operation: "level.dat",
                kind: error.kind(),
            })?
            .take(MAX_R2C_LEVEL_FILE_BYTES + 1)
            .read_to_end(&mut compressed)
            .map_err(|error| R2cColdWorldPlanError::Io {
                operation: "level.dat",
                kind: error.kind(),
            })?;
        let observed = u64::try_from(compressed.len()).map_err(|_| {
            R2cColdWorldPlanError::LevelFileTooLarge {
                observed: u64::MAX,
                maximum: MAX_R2C_LEVEL_FILE_BYTES,
            }
        })?;
        if observed > MAX_R2C_LEVEL_FILE_BYTES {
            return Err(R2cColdWorldPlanError::LevelFileTooLarge {
                observed,
                maximum: MAX_R2C_LEVEL_FILE_BYTES,
            });
        }
        let mut decoder = DeflateChunkPayloadDecoder::new();
        let source = decoder
            .decode(ChunkCompression::Gzip, &compressed, MAX_R2C_LEVEL_NBT_BYTES)
            .map_err(|error| {
                R2cColdWorldPlanError::LevelMetadata(format!(
                    "bounded gzip level.dat rejected: {error:?}"
                ))
            })?;
        let limits = NbtLimits::new(4096, 32768, 32768, 64).map_err(|error| {
            R2cColdWorldPlanError::LevelMetadata(format!("level.dat NBT limits invalid: {error:?}"))
        })?;
        require_target_26_2_level_metadata(source, limits).map_err(|error| {
            R2cColdWorldPlanError::LevelMetadata(format!(
                "26.2 Data.DataVersion rejected: {error:?}"
            ))
        })?;
        Ok(Self {
            world,
            heightmap_candidate: None,
        })
    }

    #[must_use]
    pub fn world(&self) -> &Path {
        &self.world
    }

    /// The generic Anvil visitor expects the selected dimension root,
    /// whereas the CLI selects a complete official 26.2 save root.
    #[must_use]
    pub(crate) fn overworld_source_root(&self) -> PathBuf {
        self.world.join("dimensions/minecraft/overworld")
    }

    /// Load and validate a separate source-unadmitted 26.2 heightmap state
    /// table before opening the network listener. Own it once per selected
    /// development profile, rather than per connection or chunk.
    ///
    /// # Errors
    /// Rejects missing, symlinked, wrong-sized, independently inconsistent
    /// or non-official-census candidate bytes. The frozen 16-bin census is
    /// only a COLD corruption check, not client/source/SEM admission.
    pub fn with_candidate_heightmap_file(
        mut self,
        candidate_path: &Path,
    ) -> Result<Self, R2cColdWorldPlanError> {
        let metadata =
            fs::symlink_metadata(candidate_path).map_err(|error| R2cColdWorldPlanError::Io {
                operation: "heightmap",
                kind: error.kind(),
            })?;
        if metadata.file_type().is_symlink() {
            return Err(R2cColdWorldPlanError::Symlink {
                component: "heightmap",
            });
        }
        if !metadata.is_file() {
            return Err(R2cColdWorldPlanError::NotFile {
                component: "heightmap",
            });
        }
        if metadata.len() != BLOCK_STATE_COUNT as u64 {
            return Err(R2cColdWorldPlanError::WrongHeightmapBytes {
                observed: metadata.len(),
                expected: BLOCK_STATE_COUNT,
            });
        }
        // Fixed-size read, plus one trailing byte check if the file changed
        // after metadata preflight. No unbounded filesystem allocation.
        let mut bytes = vec![0_u8; BLOCK_STATE_COUNT].into_boxed_slice();
        let mut reader = File::open(candidate_path).map_err(|error| R2cColdWorldPlanError::Io {
            operation: "heightmap",
            kind: error.kind(),
        })?;
        reader
            .read_exact(&mut bytes)
            .map_err(|error| R2cColdWorldPlanError::Io {
                operation: "heightmap",
                kind: error.kind(),
            })?;
        let mut extra = [0_u8; 1];
        if reader
            .read(&mut extra)
            .map_err(|error| R2cColdWorldPlanError::Io {
                operation: "heightmap",
                kind: error.kind(),
            })?
            != 0
        {
            return Err(R2cColdWorldPlanError::WrongHeightmapBytes {
                observed: BLOCK_STATE_COUNT as u64 + 1,
                expected: BLOCK_STATE_COUNT,
            });
        }
        crate::r2c_heightmap_facts::CandidateHeightmapFacts::from_official_oracle_bytes(&bytes)
            .map_err(|error| R2cColdWorldPlanError::HeightmapCandidate(format!("{error:?}")))?;
        self.heightmap_candidate = Some(bytes);
        Ok(self)
    }

    #[must_use]
    pub(crate) fn candidate_heightmap_bytes(&self) -> Option<&[u8]> {
        self.heightmap_candidate.as_deref()
    }
}

/// Failure from the temporary R2B playtest outer owner.
#[derive(Debug)]
pub enum R2bPlaytestError {
    /// Canonical replay-free R2B entry failed.
    Entry(R2bServerError),
    /// Canonical continuing-Play control processing failed.
    Play(R2bPlayError),
    /// Direct same-driver discard/read accounting failed.
    Driver(DriverError<Infallible>),
    /// Transport I/O failed.
    Io {
        /// Read/write operation.
        operation: &'static str,
        /// Stable I/O classification.
        kind: io::ErrorKind,
        /// Diagnostic detail.
        message: String,
    },
    /// EOF arrived with an incomplete framed Play packet buffered.
    TruncatedEof { buffered_ingress: usize },
    /// An impossible incomplete frame followed an R2B `Unclaimed` classification.
    DiscardInvariant,
    /// Opt-in world preview could not be bound to the actual outstanding teleport.
    WorldPlan { reason: String },
    /// Transactional R2C ingress failure in the explicit saved-world mode.
    WorldInbound { reason: String },
    /// Explicit source-admitted chunk publication failed without changing world truth.
    WorldPublish { reason: String },
    /// A diagnostic counter overflowed.
    AccountingOverflow,
}

impl From<R2bServerError> for R2bPlaytestError {
    fn from(value: R2bServerError) -> Self {
        Self::Entry(value)
    }
}

impl From<R2bPlayError> for R2bPlaytestError {
    fn from(value: R2bPlayError) -> Self {
        Self::Play(value)
    }
}

/// Loads the compact replay-free R2B playtest image.
///
/// The fixed body sequence is Configuration, update-recipes, commands, server-data. There is no
/// captured-Play publication section.
///
/// # Errors
///
/// Rejects wrong format/commitments/bounds/trailing data, invalid Configuration, or malformed shared
/// projection packet identities.
pub fn load_r2b_playtest_image(
    path: &Path,
    status_json: &str,
) -> Result<R2bPlaytestImage, R2bPlaytestImageError> {
    let metadata = fs::symlink_metadata(path).map_err(|error| image_io_error(&error))?;
    if metadata.file_type().is_symlink() {
        return Err(R2bPlaytestImageError::Symlink);
    }
    if !metadata.is_file() {
        return Err(R2bPlaytestImageError::NotFile);
    }
    if metadata.len() > MAX_IMAGE_BYTES {
        return Err(R2bPlaytestImageError::FileTooLarge {
            observed: metadata.len(),
            maximum: MAX_IMAGE_BYTES,
        });
    }
    let file = File::open(path).map_err(|error| image_io_error(&error))?;
    decode_image(&mut BufReader::new(file), status_json)
}

fn decode_image<R: Read>(
    reader: &mut R,
    status_json: &str,
) -> Result<R2bPlaytestImage, R2bPlaytestImageError> {
    if read_array::<8, _>(reader)? != MAGIC {
        return Err(R2bPlaytestImageError::Magic);
    }
    let protocol = read_u32(reader)?;
    if protocol != EXPECTED_PROTOCOL {
        return Err(R2bPlaytestImageError::Protocol { observed: protocol });
    }
    if read_array::<32, _>(reader)? != EXPECTED_SOURCE_SHA256 {
        return Err(R2bPlaytestImageError::SourceCommitment);
    }
    if read_array::<32, _>(reader)? != EXPECTED_CAPTURE_SHA256 {
        return Err(R2bPlaytestImageError::CaptureCommitment);
    }

    let configuration_count = usize_from_u32(read_u32(reader)?)?;
    let configuration_bytes = usize_from_u64(read_u64(reader)?)?;
    if configuration_count != EXPECTED_CONFIGURATION_COUNT {
        return Err(R2bPlaytestImageError::ConfigurationCount {
            observed: configuration_count,
        });
    }
    if configuration_bytes != EXPECTED_CONFIGURATION_BYTES {
        return Err(R2bPlaytestImageError::ConfigurationBytes {
            observed: configuration_bytes,
        });
    }

    let mut configuration = Vec::with_capacity(configuration_count);
    let mut observed_configuration_bytes = 0_usize;
    for index in 0..configuration_count {
        let body = read_body(reader, index)?;
        observed_configuration_bytes = observed_configuration_bytes.checked_add(body.len()).ok_or(
            R2bPlaytestImageError::AggregateMismatch {
                declared: configuration_bytes,
                observed: usize::MAX,
            },
        )?;
        configuration.push(body);
    }
    if observed_configuration_bytes != configuration_bytes {
        return Err(R2bPlaytestImageError::AggregateMismatch {
            declared: configuration_bytes,
            observed: observed_configuration_bytes,
        });
    }

    let recipes = read_body(reader, EXPECTED_CONFIGURATION_COUNT)?;
    let commands = read_body(reader, EXPECTED_CONFIGURATION_COUNT + 1)?;
    let server_data = read_body(reader, EXPECTED_CONFIGURATION_COUNT + 2)?;
    let mut trailing = [0_u8; 1];
    if reader
        .read(&mut trailing)
        .map_err(|error| image_io_error(&error))?
        != 0
    {
        return Err(R2bPlaytestImageError::TrailingData);
    }

    let configuration = Target26_2R1xContext::new(status_json.into(), configuration, Vec::new())?;
    debug_assert_eq!(configuration.play_frame_count(), 0);
    let bootstrap = PlayBootstrapImage26_2::new(
        CommandProjectionArtifact::new(command_key(), commands)?,
        RecipeProjectionArtifact::new(recipe_key(), recipes)?,
    );
    let server_data = ServerDataProjectionArtifact::new(status_key(), server_data)?;
    Ok(R2bPlaytestImage {
        configuration,
        bootstrap,
        server_data,
    })
}

/// Drives one stock-client connection through real Configuration, replay-free R2B and the temporary
/// post-`WorldProjection` owner.
///
/// # Errors
///
/// Returns canonical R2B entry/control failures, same-driver accounting failures, transport I/O
/// failures, truncated EOF, or impossible discard-state failures.
pub fn serve_r2b_playtest_blocking_transport(
    transport: &mut TcpStream,
    session_epoch: ServerSessionEpoch,
    image: &R2bPlaytestImage,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    serve_r2b_playtest_with_optional_r2c_plan(
        transport,
        session_epoch,
        image,
        None,
        None,
        WorldPublicationMode::NoChunks,
    )
}

/// Construct the server-lifetime source-backed world before accepting a
/// client. It is strictly non-publishing until independent 26.2 VAR/SEM
/// admission; no session driver or socket participates in source import.
///
/// # Errors
/// Fail closed on unsupported save, candidate biome order, initial teleport,
/// source receipt, or optional official-heightmap candidate.
pub fn prepare_r2c_cold_world_host(
    image: &R2bPlaytestImage,
    plan: &R2cColdWorldPlan,
) -> Result<R2cColdWorldHost, String> {
    let count = with_candidate_biomes_from_context(&image.configuration, |registry| registry.len())
        .map_err(|error| format!("selected Configuration biome names rejected: {error:?}"))?;
    if count != 66 {
        return Err(format!(
            "selected Configuration expected 66 biome names, got {count}"
        ));
    }
    let teleport = selected_snapshot(&image.server_data).teleport;
    let host = import_selected_cold_world_host(
        &image.configuration,
        &plan.overworld_source_root(),
        (teleport.x, teleport.y, teleport.z),
    )?;
    eprintln!(
        "R2C server-owned COLD import | root={} | resident_chunks={} | verified_source_receipts={} | world_read=true | chunk_sent=false | source_admitted=false",
        plan.world().display(),
        host.chunks(),
        host.receipts(),
    );
    if let Some(table) = plan.candidate_heightmap_bytes() {
        let audit = host.audit_candidate_bodies(table)?;
        eprintln!(
            "R2C server-owned COLD audit | chunks={} | total_body_bytes={} | maximum_body_bytes={} | packet_queued=false | source_admitted=false",
            audit.chunks, audit.total_body_bytes, audit.maximum_body_bytes
        );
    }
    Ok(host)
}

/// Borrow an already imported server-owned world for one retained R2B
/// Play session. Only the ACK/quota cursor is per client; source chunks
/// and source receipts keep their original server lifetime.
///
/// # Errors
/// Propagates the existing session, teleport or transport failures.
pub fn serve_r2b_playtest_with_r2c_cold_host(
    transport: &mut TcpStream,
    session_epoch: ServerSessionEpoch,
    image: &R2bPlaytestImage,
    host: &R2cColdWorldHost,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    serve_r2b_playtest_with_optional_r2c_plan(
        transport,
        session_epoch,
        image,
        None,
        Some(host),
        WorldPublicationMode::NoChunks,
    )
}

/// Retains the *same* R2B Play owner, with an explicitly selected COLD
/// nonpublishing pregenerated-world request for later R2C source admission.
/// This route must not be used to infer that a client can see a world.
///
/// # Errors
/// Returns normal R2B I/O/control errors, or a typed fail-closed teleport plan error.
pub fn serve_r2b_playtest_with_r2c_cold_plan(
    transport: &mut TcpStream,
    session_epoch: ServerSessionEpoch,
    image: &R2bPlaytestImage,
    plan: &R2cColdWorldPlan,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    serve_r2b_playtest_with_optional_r2c_plan(
        transport,
        session_epoch,
        image,
        Some(plan),
        None,
        WorldPublicationMode::NoChunks,
    )
}

/// Every product caller supplies `NoChunks`. The only positive variant
/// exists in Rust's test build, where it remains an unadmitted visual
/// diagnostic rather than an R2C source/VAR/SEM acceptance decision.
#[derive(Clone, Copy)]
enum WorldPublicationMode {
    NoChunks,
    #[cfg(test)]
    UnadmittedStockClientDiagnostic,
}

/// Bind only the opted-in test-only 25-source-chunk neighborhood to the
/// existing COLD importer. Neither mode changes production publication.
fn import_cold_world_for_demo(
    session: &R2bPlaySession,
    context: &Target26_2R1xContext,
    world: &Path,
    publication_mode: WorldPublicationMode,
) -> Result<ColdImportedView, String> {
    #[cfg(test)]
    if matches!(
        publication_mode,
        WorldPublicationMode::UnadmittedStockClientDiagnostic
    ) && let Some(value) = std::env::var_os("HELVE_R2C_DIAGNOSTIC_RENDER_HALO")
    {
        if value != "1" {
            return Err("render-halo diagnostic flag must be exactly 1".to_owned());
        }
        return crate::r2c_cold_demo_import::import_selected_cold_world_with_render_halo(
            session, context, world,
        );
    }
    let _ = publication_mode;
    crate::r2c_cold_demo_import::import_selected_cold_world(session, context, world)
}

#[expect(
    clippy::redundant_closure_for_method_calls,
    reason = "this callback borrows a registry with a closure-local lifetime; the method item fails the required FnOnce generality"
)]
fn serve_r2b_playtest_with_optional_r2c_plan(
    transport: &mut TcpStream,
    session_epoch: ServerSessionEpoch,
    image: &R2bPlaytestImage,
    plan: Option<&R2cColdWorldPlan>,
    host: Option<&R2cColdWorldHost>,
    publication_mode: WorldPublicationMode,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    if plan.is_some() || host.is_some() {
        // Reuse the already-tested borrowed Configuration bridge exactly
        // once, before any pre-Play or Play bytes are emitted. This is a
        // source-unadmitted *consistency check* only, never numeric-ID
        // authority for chunk publication.
        let count =
            with_candidate_biomes_from_context(&image.configuration, |registry| registry.len())
                .map_err(|error| R2bPlaytestError::WorldPlan {
                    reason: format!("selected Configuration biome names rejected: {error:?}"),
                })?;
        if count != 66 {
            return Err(R2bPlaytestError::WorldPlan {
                reason: format!("selected Configuration expected 66 biome names, got {count}"),
            });
        }
    }
    let outcome = enter_r2b_play_blocking_transport(
        transport,
        session_epoch,
        &image.configuration,
        &image.bootstrap,
        selected_snapshot(&image.server_data),
    )?;
    let mut session = match outcome {
        R2bEntryOutcome::SessionClosed => return Ok(R2bPlaytestExit::SessionClosedBeforeWorld),
        R2bEntryOutcome::PeerEof => return Ok(R2bPlaytestExit::PeerEofBeforeWorld),
        R2bEntryOutcome::WorldProjectionReady(session) => session,
    };

    // The opt-in development route now imports *actual* saved chunks into
    // exactly one retained semantic dimension. The opaque imported owner and
    // its receipts live through the original R2B Play service loop; they
    // cannot emit Play chunks until separate client/source VAR/SEM admission.
    // Without the flag, the original R2B behavior remains byte-identical.
    let mut cold_view = if let Some(host) = host {
        Some(
            host.attach(&session)
                .map_err(|reason| R2bPlaytestError::WorldPlan { reason })?,
        )
    } else if let Some(plan) = plan {
        let overworld = plan.overworld_source_root();
        let imported = import_cold_world_for_demo(
            &session,
            &image.configuration,
            &overworld,
            publication_mode,
        )
        .map_err(|reason| R2bPlaytestError::WorldPlan { reason })?;
        eprintln!(
            "R2C COLD import | root={} | resident_chunks={} | verified_source_receipts={} | world_read=true | chunk_sent=false | source_admitted=false",
            plan.world().display(),
            imported.chunks(),
            imported.receipts(),
        );
        if let Some(table) = plan.candidate_heightmap_bytes() {
            let audit = imported
                .audit_candidate_bodies(table)
                .map_err(|reason| R2bPlaytestError::WorldPlan { reason })?;
            eprintln!(
                "R2C COLD candidate audit | chunks={} | total_body_bytes={} | maximum_body_bytes={} | packet_queued=false | biome_heightmap_wire_admitted=false",
                audit.chunks, audit.total_body_bytes, audit.maximum_body_bytes
            );
        }
        Some(imported)
    } else {
        None
    };

    eprintln!(
        "R2B WorldProjectionReady | captured_play_publication=0 | pending_teleport={:?} | R2C_world_projection_pending=true",
        session
            .teleport_transaction()
            .awaiting()
            .map(|pending| pending.id)
    );
    // Only the `cargo test --lib` diagnostic build can produce a positive
    // witness. This deliberately exercises the *existing* real socket,
    // importer and publisher, but is neither a production switch nor a
    // source-admitted R2C client demonstration.
    #[cfg(test)]
    if matches!(
        publication_mode,
        WorldPublicationMode::UnadmittedStockClientDiagnostic
    ) {
        return serve_unadmitted_stock_client_test(transport, &mut session, &mut cold_view, plan);
    }
    // Admission is intentionally uninhabited in product builds. This path
    // keeps the original R2B client behavior unchanged until source VAR/SEM
    // promotes the exact 26.2 source/known-pack/heightmap/Play contract.
    let _ = publication_mode;
    serve_world_projection_wait(transport, &mut session, cold_view.as_mut(), None)
}

/// Strictly test-build-only real-client probe using the original R2B
/// session, resident source receipts and existing receipt-bound publisher.
/// Product builds cannot call or construct this admission path.
#[cfg(test)]
fn serve_unadmitted_stock_client_test(
    transport: &mut TcpStream,
    session: &mut R2bPlaySession,
    cold_view: &mut Option<ColdImportedView>,
    plan: Option<&R2cColdWorldPlan>,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    let table = plan
        .and_then(R2cColdWorldPlan::candidate_heightmap_bytes)
        .ok_or_else(|| R2bPlaytestError::WorldPlan {
            reason:
                "diagnostic live R2C requires an explicitly selected official heightmap candidate"
                    .to_owned(),
        })?;
    let world = cold_view
        .as_mut()
        .ok_or_else(|| R2bPlaytestError::WorldPlan {
            reason: "diagnostic live R2C requires a verified imported saved world".to_owned(),
        })?;
    // Both the receipt audit above and the publisher's own facts/limit
    // validation must pass before the first chunk enters the driver.
    let admission = R2cSourceAdmission;
    let mut publisher = SourceAdmittedPlayPublisher::new(session, table, 0, &admission)
        .map_err(|reason| R2bPlaytestError::WorldPublish { reason })?;
    eprintln!(
        "R2C TEST-ONLY LIVE DIAGNOSTIC | chunks={} | source_receipts={} | stock_client_observation_required=true | source_admitted_for_live_r2c=false | production_admitted=false",
        world.chunks(),
        world.receipts(),
    );
    let exit =
        serve_world_projection_wait(transport, session, Some(&mut *world), Some(&mut publisher))?;
    if matches!(exit, R2bPlaytestExit::LivePeerEof { .. }) {
        let (sent, expected, unacknowledged) = world.diagnostic_batch_progress();
        if sent != expected || unacknowledged != 0 {
            return Err(R2bPlaytestError::WorldPublish {
                reason: format!(
                    "diagnostic chunk batch incomplete at peer EOF: published={sent}/{expected}, pending_ACKs={unacknowledged}"
                ),
            });
        }
        eprintln!(
            "R2C TEST-ONLY CHUNK BATCH ACK PASS | published_chunks={sent} | source_receipts={expected} | unacknowledged_batches=0 | visual rendering remains MANUAL"
        );
    }
    Ok(exit)
}

/// One event on the original R2B driver; the optional world owner can
/// additionally claim a source-bound batch ACK without moving frame bytes.
enum WorldPlayIngress {
    Incomplete,
    Control(R2bPlayInbound),
    ChunkBatchAcknowledged,
    Unclaimed { packet_id: i32 },
}

fn process_one_world_play_ingress(
    session: &mut R2bPlaySession,
    cold_view: Option<&mut ColdImportedView>,
    now_ms: u64,
) -> Result<WorldPlayIngress, R2bPlaytestError> {
    if let Some(world) = cold_view {
        return match world
            .process_one_play_inbound(session, now_ms)
            .map_err(|error| R2bPlaytestError::WorldInbound {
                reason: format!("{error:?}"),
            })? {
            R2cPlayInboundStep::Incomplete => Ok(WorldPlayIngress::Incomplete),
            R2cPlayInboundStep::Control(event) => Ok(WorldPlayIngress::Control(event)),
            R2cPlayInboundStep::ChunkBatchAcknowledged { .. } => {
                Ok(WorldPlayIngress::ChunkBatchAcknowledged)
            }
            R2cPlayInboundStep::Unclaimed { packet_id } => {
                Ok(WorldPlayIngress::Unclaimed { packet_id })
            }
        };
    }
    match session.process_one_play_control(now_ms)? {
        R2bPlayProcess::Incomplete => Ok(WorldPlayIngress::Incomplete),
        R2bPlayProcess::Committed(event) => Ok(WorldPlayIngress::Control(event)),
        R2bPlayProcess::Unclaimed { packet_id } => Ok(WorldPlayIngress::Unclaimed { packet_id }),
    }
}

pub(crate) fn serve_world_projection_wait(
    transport: &mut TcpStream,
    session: &mut R2bPlaySession,
    mut cold_view: Option<&mut ColdImportedView>,
    mut publisher: Option<&mut SourceAdmittedPlayPublisher<'_>>,
) -> Result<R2bPlaytestExit, R2bPlaytestError> {
    let origin = Instant::now();
    let mut teleport_acknowledged = false;
    let mut accepted_keep_alives = 0_u64;
    let mut discarded_world_frames = 0_u64;

    loop {
        let Some(now_ms) = elapsed_millis(origin) else {
            return Ok(R2bPlaytestExit::ClockInvalid);
        };
        for _ in 0..ACTIONS_PER_SERVICE {
            match process_one_world_play_ingress(session, cold_view.as_deref_mut(), now_ms)? {
                WorldPlayIngress::Incomplete => break,
                WorldPlayIngress::Control(R2bPlayInbound::TeleportAcknowledgement(result)) => {
                    if result != TeleportAckResult::Accepted {
                        return Ok(R2bPlaytestExit::InvalidTeleportAcknowledgement(result));
                    }
                    teleport_acknowledged = true;
                }
                WorldPlayIngress::Control(R2bPlayInbound::KeepAliveAccepted { .. }) => {
                    accepted_keep_alives = accepted_keep_alives
                        .checked_add(1)
                        .ok_or(R2bPlaytestError::AccountingOverflow)?;
                }
                WorldPlayIngress::Control(R2bPlayInbound::KeepAliveRejected { .. }) => {
                    return Ok(R2bPlaytestExit::InvalidKeepAlive);
                }
                WorldPlayIngress::ChunkBatchAcknowledged => {
                    // No finished batch is ever queued until source admission;
                    // this becomes reachable only after the real sender is
                    // independently admitted. The existing batch state has
                    // already transactionally consumed the ACK.
                }
                WorldPlayIngress::Unclaimed { packet_id } => {
                    // This route is an intentionally incomplete gameplay handler.
                    // Expose the exact serverbound packet IDs observed during the
                    // COLD-only stock-client experiment, without another parser,
                    // packet copy or production HOT-path trace.
                    #[cfg(test)]
                    if publisher.is_some() && discarded_world_frames < 16 {
                        trace_unclaimed(packet_id, now_ms);
                    }
                    let _ = packet_id;
                    discard_one_complete_play_frame(session)?;
                    discarded_world_frames = discarded_world_frames
                        .checked_add(1)
                        .ok_or(R2bPlaytestError::AccountingOverflow)?;
                }
            }
        }

        write_play_once(transport, session)?;
        let Some(now_ms) = elapsed_millis(origin) else {
            return Ok(R2bPlaytestExit::ClockInvalid);
        };
        match session.service_play_liveness(now_ms)? {
            R2bLivenessProcess::Idle => {}
            R2bLivenessProcess::ChallengeQueued { .. } => write_play_once(transport, session)?,
            R2bLivenessProcess::KeepAliveTimedOut => {
                return Ok(R2bPlaytestExit::KeepAliveTimedOut);
            }
            R2bLivenessProcess::ClosedTimedOut => return Ok(R2bPlaytestExit::ClosedTimedOut),
        }

        // Control ingress and liveness have already had first priority.
        // Only a separately admitted publisher may enter this branch; it
        // uses the exact same connection driver and source receipt owner.
        if let (Some(world), Some(sender)) = (cold_view.as_deref_mut(), publisher.as_deref_mut()) {
            let Some(send_now_ms) = elapsed_millis(origin) else {
                return Ok(R2bPlaytestExit::ClockInvalid);
            };
            service_admitted_play_publication(transport, session, world, sender, send_now_ms)?;
        }

        let Some(now_ms) = elapsed_millis(origin) else {
            return Ok(R2bPlaytestExit::ClockInvalid);
        };
        let liveness_deadline_ms = session.liveness.next_deadline_ms(PLAY_LIVENESS_POLICY);
        let deadline_ms = match (publisher.as_deref(), cold_view.as_deref()) {
            (Some(sender), Some(world)) => {
                sender.next_wake_deadline_ms(world, liveness_deadline_ms)
            }
            _ => liveness_deadline_ms,
        };
        let wait_ms = deadline_ms.saturating_sub(now_ms).max(1);
        transport
            .set_read_timeout(Some(Duration::from_millis(wait_ms)))
            .map_err(|error| transport_error("read-timeout", &error))?;

        match transport.read(&mut session.read_scratch) {
            Ok(0) => {
                if session.driver.buffered_ingress() != 0 {
                    return Err(R2bPlaytestError::TruncatedEof {
                        buffered_ingress: session.driver.buffered_ingress(),
                    });
                }
                return Ok(R2bPlaytestExit::LivePeerEof {
                    teleport_acknowledged,
                    accepted_keep_alives,
                    discarded_world_frames,
                    latency_ms: session.latency_ms(),
                });
            }
            Ok(read) => session
                .driver
                .ingest::<Infallible>(&session.read_scratch[..read])
                .map_err(R2bPlaytestError::Driver)?,
            Err(error)
                if matches!(
                    error.kind(),
                    io::ErrorKind::WouldBlock
                        | io::ErrorKind::TimedOut
                        | io::ErrorKind::Interrupted
                ) => {}
            Err(error) => return Err(transport_error("read", &error)),
        }
    }
}

/// A single bounded publication opportunity following Play control and
/// liveness. Keep the driver and socket in their original R2B owner.
fn service_admitted_play_publication(
    transport: &mut TcpStream,
    session: &mut R2bPlaySession,
    world: &mut ColdImportedView,
    sender: &mut SourceAdmittedPlayPublisher<'_>,
    now_ms: u64,
) -> Result<(), R2bPlaytestError> {
    let queued =
        sender
            .service(session, world, now_ms)
            .map_err(|error| R2bPlaytestError::WorldPublish {
                reason: format!("{error:?}"),
            })?;
    if queued != 0 {
        write_play_once(transport, session)?;
    }
    Ok(())
}

#[derive(Clone, Copy, Debug)]
struct DiscardedPlayFrame;

impl OutboundBatch for DiscardedPlayFrame {
    type Body = [u8; 0];

    fn outbound_frames(&self) -> &[Self::Body] {
        &[]
    }
}

#[cfg(test)]
fn trace_unclaimed(packet_id: i32, now_ms: u64) {
    eprintln!(
        "R2C TEST-ONLY unclaimed Play inbound | packet_id={packet_id} | elapsed_ms={now_ms} | action=discard_in_diagnostic_only"
    );
}

fn discard_one_complete_play_frame(session: &mut R2bPlaySession) -> Result<(), R2bPlaytestError> {
    match session
        .driver
        .process_one_transactional::<Infallible, DiscardedPlayFrame, _>(|_| Ok(DiscardedPlayFrame))
        .map_err(R2bPlaytestError::Driver)?
    {
        TransactionResult::Committed(_) => Ok(()),
        TransactionResult::Incomplete => Err(R2bPlaytestError::DiscardInvariant),
    }
}

fn write_play_once(
    transport: &mut TcpStream,
    session: &mut R2bPlaySession,
) -> Result<(), R2bPlaytestError> {
    let pending = session.driver.pending_egress().len();
    if pending == 0 {
        return Ok(());
    }
    let result = {
        let bytes = session.driver.pending_egress();
        transport.write(bytes)
    };
    match result {
        Ok(0) => Err(R2bPlaytestError::Io {
            operation: "write",
            kind: io::ErrorKind::WriteZero,
            message: format!("zero-byte write with {pending} bytes pending"),
        }),
        Ok(written) => session
            .driver
            .consume_written::<Infallible>(written)
            .map_err(R2bPlaytestError::Driver),
        Err(error) => Err(transport_error("write", &error)),
    }
}

fn selected_snapshot(status: &ServerDataProjectionArtifact) -> FreshR2bBootstrapSnapshot<'_> {
    FreshR2bBootstrapSnapshot {
        command_key: command_key(),
        recipe_key: recipe_key(),
        login: FreshLoginPayload {
            player_id: 270,
            flags: FreshLoginFlags::SHOW_DEATH_SCREEN,
            levels: &LEVELS,
            max_players: 20,
            chunk_radius: 10,
            simulation_distance: 10,
            spawn: FreshCommonSpawnInfo {
                dimension_type_registry_id: 0,
                dimension: "minecraft:overworld",
                seed: 0x1439_77a8_ee42_e04a,
                game_mode: BootstrapGameMode::Survival,
                previous_game_mode: None,
                is_debug: false,
                is_flat: false,
                portal_cooldown: 0,
                sea_level: 63,
            },
        },
        difficulty: ChangeDifficultyPayload {
            difficulty: Difficulty26_2::Easy,
            locked: false,
        },
        abilities: PlayerAbilitiesPayload {
            flags: PlayerAbilityFlags::NONE,
            flying_speed: 0.05,
            walking_speed: 0.1,
        },
        held_slot: HeldSlotPayload(0),
        permission_event: PermissionEntityEventPayload {
            entity_id: 270,
            event: PermissionLevelEvent::All,
        },
        recipe_settings: RecipeBookSettingsPayload {
            flags: RecipeBookSettingFlags::NONE,
        },
        teleport: TeleportDestination {
            x: 10.390_952_126_751_907,
            y: 84.0,
            z: -5.815_159_807_324_014,
            yaw: f32::from_bits(0xc2ee_3335),
            pitch: f32::from_bits(0x4190_0001),
        },
        server_data: Some(ServerDataProjection {
            artifact: status,
            requested: status_key(),
        }),
        existing_players: &[],
        joining_player: SELF,
        border: WorldBorderPayload {
            center_x: 0.0,
            center_z: 0.0,
            old_size: 59_999_968.0,
            new_size: 59_999_968.0,
            lerp_time: 0,
            absolute_max_size: 29_999_984,
            warning_blocks: 5,
            warning_time: 300,
        },
        clock: ClockFullSyncPayload {
            game_time: 5_503,
            updates: &CLOCKS,
        },
        spawn: DefaultSpawnPayload {
            dimension: "minecraft:overworld",
            x: 0,
            y: 90,
            z: 0,
            yaw: 0.0,
            pitch: 0.0,
        },
        weather: BootstrapWeather::Clear,
        ticking_state: TickingStatePayload {
            tick_rate: 20.0,
            is_frozen: false,
        },
        ticking_step: TickingStepPayload(0),
        inventory: FreshEmptyInventoryPayload {
            container_id: 0,
            state_id: 1,
            slot_count: 46,
        },
    }
}

const fn revision(byte: u8) -> ProjectionRevision {
    ProjectionRevision::new([byte; 32])
}

const fn command_key() -> CommandProjectionKey {
    CommandProjectionKey::new(
        revision(1),
        revision(2),
        revision(3),
        revision(4),
        CommandPermissionProfile::DefaultNonOperator,
    )
}

const fn recipe_key() -> RecipeProjectionKey {
    RecipeProjectionKey::new(revision(5), revision(6), revision(7), revision(8))
}

const fn status_key() -> ServerDataProjectionKey {
    ServerDataProjectionKey::new(revision(9), revision(10))
}

fn read_body<R: Read>(reader: &mut R, index: usize) -> Result<Box<[u8]>, R2bPlaytestImageError> {
    let length = usize_from_u32(read_u32(reader)?)?;
    if length == 0 || length > MAX_BODY_BYTES {
        return Err(R2bPlaytestImageError::BodyLength {
            index,
            observed: length,
        });
    }
    let mut body = vec![0_u8; length].into_boxed_slice();
    reader
        .read_exact(&mut body)
        .map_err(|error| image_io_error(&error))?;
    Ok(body)
}

fn read_u32<R: Read>(reader: &mut R) -> Result<u32, R2bPlaytestImageError> {
    Ok(u32::from_le_bytes(read_array(reader)?))
}

fn read_u64<R: Read>(reader: &mut R) -> Result<u64, R2bPlaytestImageError> {
    Ok(u64::from_le_bytes(read_array(reader)?))
}

fn read_array<const N: usize, R: Read>(reader: &mut R) -> Result<[u8; N], R2bPlaytestImageError> {
    let mut value = [0_u8; N];
    reader
        .read_exact(&mut value)
        .map_err(|error| image_io_error(&error))?;
    Ok(value)
}

fn usize_from_u32(value: u32) -> Result<usize, R2bPlaytestImageError> {
    usize::try_from(value).map_err(|_| R2bPlaytestImageError::BodyLength {
        index: usize::MAX,
        observed: usize::MAX,
    })
}

fn usize_from_u64(value: u64) -> Result<usize, R2bPlaytestImageError> {
    usize::try_from(value).map_err(|_| R2bPlaytestImageError::ConfigurationBytes {
        observed: usize::MAX,
    })
}

fn image_io_error(error: &io::Error) -> R2bPlaytestImageError {
    R2bPlaytestImageError::Io {
        kind: error.kind(),
        message: error.to_string(),
    }
}

fn transport_error(operation: &'static str, error: &io::Error) -> R2bPlaytestError {
    R2bPlaytestError::Io {
        operation,
        kind: error.kind(),
        message: error.to_string(),
    }
}

fn elapsed_millis(origin: Instant) -> Option<u64> {
    u64::try_from(origin.elapsed().as_millis()).ok()
}

#[cfg(test)]
mod r2c_cold_plan_tests {
    use std::fs;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    use super::{R2cColdWorldPlan, R2cColdWorldPlanError};

    static NEXT: AtomicU64 = AtomicU64::new(0);
    // Synthetic, checksum-correct gzip NBT: empty root, one Data compound,
    // one DataVersion Int, and both TAG_End terminators.
    const VALID_LEVEL_DAT_GZIP: [u8; 47] = [
        0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe3, 0x62, 0x60, 0xe0, 0x62,
        0x60, 0x71, 0x49, 0x2c, 0x49, 0x64, 0x66, 0xe0, 0x06, 0x51, 0x61, 0xa9, 0x45, 0xc5, 0x99,
        0xf9, 0x79, 0x0c, 0x0c, 0xc2, 0xea, 0x0c, 0x0c, 0x00, 0x73, 0xd9, 0x0f, 0xb5, 0x1e, 0x00,
        0x00, 0x00,
    ];
    const OLD_LEVEL_DAT_GZIP: [u8; 47] = [
        0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe3, 0x62, 0x60, 0xe0, 0x62,
        0x60, 0x71, 0x49, 0x2c, 0x49, 0x64, 0x66, 0xe0, 0x06, 0x51, 0x61, 0xa9, 0x45, 0xc5, 0x99,
        0xf9, 0x79, 0x0c, 0x0c, 0xc2, 0x6a, 0x0c, 0x0c, 0x00, 0x44, 0xb3, 0xcd, 0xb4, 0x1e, 0x00,
        0x00, 0x00,
    ];

    fn official_overworld_directory(root: &std::path::Path) -> PathBuf {
        let path = root.join("dimensions/minecraft/overworld");
        fs::create_dir_all(&path).unwrap();
        // This test covers bounded path identity only, not level.dat NBT
        // admission. The full saved profile remains separately gated.
        fs::write(root.join("level.dat"), VALID_LEVEL_DAT_GZIP).unwrap();
        path
    }

    struct ScratchWorld(PathBuf);

    impl ScratchWorld {
        fn new() -> Self {
            let number = NEXT.fetch_add(1, Ordering::Relaxed);
            let root = std::env::temp_dir().join(format!(
                "helve-r2c-world-plan-{}-{number}",
                std::process::id()
            ));
            fs::create_dir(&root).expect("fresh temporary root");
            Self(root)
        }
    }

    impl Drop for ScratchWorld {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn cold_world_root_is_explicit_and_requires_region_directory() {
        let dir = ScratchWorld::new();
        // A legacy world/region path is not the real 26.2 Overworld.
        fs::create_dir(dir.0.join("region")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::Io {
                operation: "dimensions",
                ..
            })
        ));
        let overworld = official_overworld_directory(&dir.0);
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::Io {
                operation: "region",
                ..
            })
        ));
        fs::create_dir(overworld.join("region")).unwrap();
        let selection = R2cColdWorldPlan::new(dir.0.clone()).unwrap();
        assert_eq!(selection.world(), dir.0.as_path());
        assert_eq!(selection.overworld_source_root(), overworld);
        assert_eq!(fs::read_dir(overworld.join("region")).unwrap().count(), 0);
    }

    #[test]
    fn invalid_world_components_are_rejected_before_network_listen() {
        let dir = ScratchWorld::new();
        let overworld = official_overworld_directory(&dir.0);
        fs::write(overworld.join("region"), b"not a region directory").unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::NotDirectory {
                component: "region"
            })
        ));
        fs::remove_file(overworld.join("region")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.join("missing")),
            Err(R2cColdWorldPlanError::Io {
                operation: "world",
                ..
            })
        ));
    }

    #[test]
    fn opt_in_dense_candidate_is_bounded_and_never_promoted_to_admission() {
        use helve_generated::{BLOCK_STATE_COUNT, STATE_MUTATION_FLAGS};

        let world = ScratchWorld::new();
        let overworld = official_overworld_directory(&world.0);
        fs::create_dir(overworld.join("region")).unwrap();
        let facts_path = world.0.join("facts.bin");
        let valid: Vec<u8> = STATE_MUTATION_FLAGS
            .iter()
            .map(|&flags| (flags & 1) | ((flags & 2) << 1))
            .collect();
        assert_eq!(valid.len(), BLOCK_STATE_COUNT);
        fs::write(&facts_path, &valid).unwrap();
        // This table is coherent with independent non-air/fluid bits, but
        // deliberately lacks the actual official motion/leaves census.
        // The product's COLD candidate file path must reject it.
        assert!(matches!(
            R2cColdWorldPlan::new(world.0.clone())
                .unwrap()
                .with_candidate_heightmap_file(&facts_path),
            Err(R2cColdWorldPlanError::HeightmapCandidate(_))
        ));

        fs::write(&facts_path, &valid[..valid.len() - 1]).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(world.0.clone())
                .unwrap()
                .with_candidate_heightmap_file(&facts_path),
            Err(R2cColdWorldPlanError::WrongHeightmapBytes { .. })
        ));
        // The dedicated Java 25 workflow supplies the exact pinned runtime
        // facts. Unlike a coherent synthetic table, they must pass the
        // product's real pre-listener file admission path.
        if let Some(official) = std::env::var_os("HELVE_R2C_HEIGHTMAP_CANDIDATE") {
            let admitted = R2cColdWorldPlan::new(world.0.clone())
                .unwrap()
                .with_candidate_heightmap_file(std::path::Path::new(&official))
                .expect("actual official runtime table passes frozen COLD census");
            assert_eq!(
                admitted.candidate_heightmap_bytes().unwrap().len(),
                BLOCK_STATE_COUNT
            );
        }
        let mut wrong = valid;
        wrong[0] = 0x80;
        fs::write(&facts_path, &wrong).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(world.0.clone())
                .unwrap()
                .with_candidate_heightmap_file(&facts_path),
            Err(R2cColdWorldPlanError::HeightmapCandidate(_))
        ));
    }

    #[test]
    fn missing_or_nonregular_level_dat_cannot_pass_cold_save_root_preflight() {
        let dir = ScratchWorld::new();
        let overworld = official_overworld_directory(&dir.0);
        fs::create_dir(overworld.join("region")).unwrap();
        fs::remove_file(dir.0.join("level.dat")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::Io {
                operation: "level.dat",
                ..
            })
        ));
        fs::create_dir(dir.0.join("level.dat")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::NotFile {
                component: "level.dat"
            })
        ));
    }

    #[test]
    fn saved_root_rejects_old_corrupt_and_oversized_level_metadata() {
        let dir = ScratchWorld::new();
        let overworld = official_overworld_directory(&dir.0);
        fs::create_dir(overworld.join("region")).unwrap();
        R2cColdWorldPlan::new(dir.0.clone()).expect("pinned gzip NBT version 4903");

        let path = dir.0.join("level.dat");
        fs::write(&path, OLD_LEVEL_DAT_GZIP).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::LevelMetadata(_))
        ));
        let mut corrupted = VALID_LEVEL_DAT_GZIP;
        corrupted[40] ^= 0x01;
        fs::write(&path, corrupted).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::LevelMetadata(_))
        ));
        // Deliberately larger than the COLD cap. The production path rejects
        // from metadata without allocating for untrusted source bytes.
        let too_large = vec![0_u8; usize::try_from(super::MAX_R2C_LEVEL_FILE_BYTES + 1).unwrap()];
        fs::write(&path, too_large).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::LevelFileTooLarge { .. })
        ));
    }

    #[cfg(unix)]
    #[test]
    fn symlinked_world_or_region_is_not_treated_as_admitted_source() {
        use std::os::unix::fs::symlink;
        let dir = ScratchWorld::new();
        let overworld = official_overworld_directory(&dir.0);
        fs::create_dir(dir.0.join("actual-region")).unwrap();
        symlink(dir.0.join("actual-region"), overworld.join("region")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.clone()),
            Err(R2cColdWorldPlanError::Symlink {
                component: "region"
            })
        ));
        symlink(&dir.0, dir.0.join("world-link")).unwrap();
        assert!(matches!(
            R2cColdWorldPlan::new(dir.0.join("world-link")),
            Err(R2cColdWorldPlanError::Symlink { component: "world" })
        ));
    }
}

#[cfg(test)]
mod r2c_stock_client_diagnostic {
    use std::env;
    use std::io;
    use std::net::{TcpListener, TcpStream};
    use std::path::PathBuf;
    use std::thread;
    use std::time::{Duration, Instant};

    use super::{
        R2bPlaytestExit, R2cColdWorldPlan, WorldPublicationMode, load_r2b_playtest_image,
        serve_r2b_playtest_with_optional_r2c_plan,
    };
    use crate::{HELVE_STATUS_JSON, ServerSessionEpoch};

    const MAX_PREPLAY_CONNECTIONS: usize = 8;
    const MAX_LISTEN_TIME: Duration = Duration::from_mins(3);
    const ACCEPT_POLL: Duration = Duration::from_millis(25);
    const SOCKET_TIMEOUT: Duration = Duration::from_secs(15);

    fn required(name: &str) -> String {
        env::var(name).unwrap_or_else(|_| {
            panic!("test-only R2C diagnostic requires {name}; see R2C_STOCK_CLIENT_DEMO_RUNBOOK")
        })
    }

    /// A status probe or other pre-Play termination cannot prove world
    /// projection. Do not treat it as a test failure or as a chunk success:
    /// the next accepted socket must independently reach `WorldProjection`.
    fn is_preplay_only(exit: R2bPlaytestExit) -> bool {
        matches!(
            exit,
            R2bPlaytestExit::SessionClosedBeforeWorld | R2bPlaytestExit::PeerEofBeforeWorld
        )
    }

    #[test]
    fn status_only_or_preworld_eof_is_not_r2c_completion() {
        assert!(is_preplay_only(R2bPlaytestExit::SessionClosedBeforeWorld));
        assert!(is_preplay_only(R2bPlaytestExit::PeerEofBeforeWorld));
        assert!(!is_preplay_only(R2bPlaytestExit::KeepAliveTimedOut));
        assert!(!is_preplay_only(R2bPlaytestExit::LivePeerEof {
            teleport_acknowledged: true,
            accepted_keep_alives: 1,
            discarded_world_frames: 0,
            latency_ms: 0,
        }));
    }

    /// Only this COLD ignored test owns the listener. It is bounded both in
    /// number of status/preplay probes and wall-clock admission time; there
    /// is still only one R2B/Play driver per accepted physical connection.
    fn next_client(listener: &TcpListener, deadline: Instant) -> TcpStream {
        loop {
            match listener.accept() {
                Ok((socket, peer)) => {
                    eprintln!("R2C diagnostic incoming peer={peer}");
                    socket.set_nodelay(true).expect("one TCP peer");
                    socket
                        .set_read_timeout(Some(SOCKET_TIMEOUT))
                        .expect("bounded initial handshake timeout");
                    socket
                        .set_write_timeout(Some(SOCKET_TIMEOUT))
                        .expect("bounded write timeout");
                    return socket;
                }
                Err(error) if error.kind() == io::ErrorKind::WouldBlock => {
                    assert!(
                        Instant::now() < deadline,
                        "R2C diagnostic listener timed out without a completed Play connection; try Direct Connection on the selected 26.2 offline profile"
                    );
                    thread::sleep(ACCEPT_POLL);
                }
                Err(error) => panic!("R2C localhost accept failed: {error}"),
            }
        }
    }

    fn assert_live_completion(exit: R2bPlaytestExit) {
        match exit {
            R2bPlaytestExit::LivePeerEof {
                teleport_acknowledged: true,
                accepted_keep_alives,
                discarded_world_frames,
                ..
            } => {
                if accepted_keep_alives == 0 {
                    eprintln!(
                        "R2C DIAGNOSTIC PARTIAL WIRE RESULT | chunk batch and teleport ACK confirmed | unclaimed gameplay frames={discarded_world_frames} | peer closed before a keep-alive response | no visual success or complete liveness proof"
                    );
                    panic!(
                        "client disconnected after completed chunk batch but before keep-alive; inspect PrismLauncher minecraft/logs/latest.log for client-side protocol decoder exception. Keep-alive is not proven faulty by early EOF."
                    );
                }
                eprintln!(
                    "R2C DIAGNOSTIC WIRE PASS | teleport ACK=accepted | keep-alives={accepted_keep_alives} | unclaimed gameplay frames={discarded_world_frames} | visual terrain observation is MANUAL | not production-admitted"
                );
            }
            other => panic!(
                "client reached a nonpassing post-handshake exit: {other:?}; capture client/latest.log"
            ),
        }
    }

    /// Human-operated localhost-only experiment, never ordinary CI or a
    /// release binary. The actual chunk publisher remains cfg(test)-only;
    /// pre-Play status connections are not silently called successful joins.
    #[test]
    #[ignore = "requires real stock Java 26.2 client, selected 26.2 save and source-free R2B image; UNADMITTED diagnostic only"]
    fn manual_stock_client_receives_real_anvil_chunks() {
        assert_eq!(
            required("HELVE_R2C_DIAGNOSTIC_CONFIRM"),
            "UNADMITTED_LOCAL_ONLY",
            "must explicitly accept unadmitted test-only client experiment"
        );
        let epoch = ServerSessionEpoch::parse_hex(&required("HELVE_R2C_DIAGNOSTIC_EPOCH"))
            .expect("capture-qualified offline R2B session epoch");
        let image = load_r2b_playtest_image(
            &PathBuf::from(required("HELVE_R2C_DIAGNOSTIC_R2B_IMAGE")),
            HELVE_STATUS_JSON,
        )
        .expect("exact source/capture-committed R2B playtest image");
        let plan = R2cColdWorldPlan::new(PathBuf::from(required("HELVE_R2C_DIAGNOSTIC_WORLD")))
            .expect("bounded real 26.2 saved-world root")
            .with_candidate_heightmap_file(&PathBuf::from(required(
                "HELVE_R2C_HEIGHTMAP_CANDIDATE",
            )))
            .expect("exact pinned, bounded 32,366-state official-runtime candidate");
        let port = env::var("HELVE_R2C_DIAGNOSTIC_PORT")
            .map_or_else(|_| Ok(25565_u16), |text| text.parse::<u16>())
            .expect("valid numeric loopback listener port");
        let listener = TcpListener::bind(("127.0.0.1", port))
            .expect("local demo listener; close any server occupying the port");
        listener
            .set_nonblocking(true)
            .expect("bounded test-only accept polling");
        let deadline = Instant::now() + MAX_LISTEN_TIME;
        eprintln!(
            "R2C TEST-ONLY diagnostic listening on {} | connect Java 26.2 via Direct Connection | pre-Play probes tolerated, but only completed chunk batch and liveness can PASS | production_admitted=false",
            listener.local_addr().expect("bound address")
        );
        for attempt in 1..=MAX_PREPLAY_CONNECTIONS {
            let mut socket = next_client(&listener, deadline);
            let outcome = serve_r2b_playtest_with_optional_r2c_plan(
                &mut socket,
                epoch,
                &image,
                Some(&plan),
                None,
                WorldPublicationMode::UnadmittedStockClientDiagnostic,
            )
            .unwrap_or_else(|error| {
                panic!("R2C diagnostic connection {attempt} failed: {error:?}")
            });
            eprintln!("R2C diagnostic connection {attempt} ended: {outcome:?}");
            if is_preplay_only(outcome) {
                eprintln!(
                    "R2C diagnostic pre-Play-only connection {attempt}/{MAX_PREPLAY_CONNECTIONS}; no chunks sent. Awaiting real Login/Configuration/Play on a NEW connection. If Minecraft shows a failed join, retry Direct Connection and keep its latest.log."
                );
                continue;
            }
            assert_live_completion(outcome);
            return;
        }
        panic!(
            "R2C diagnostic exhausted {MAX_PREPLAY_CONNECTIONS} pre-Play connections without reaching Play; examine client latest.log and selected offline name Stato16"
        );
    }
}
