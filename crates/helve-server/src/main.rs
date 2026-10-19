use std::env;
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Duration;

use helve_server::{
    DEFAULT_R0_BIND_ADDRESS, HELVE_STATUS_JSON, PRODUCT_NAME, R0_ADMISSION_SESSION_SHA256,
    R2bPlaytestImage, R2cColdWorldHost, R2cColdWorldPlan, ServerSessionEpoch, load_r1x_image,
    load_r2b_playtest_image, prepare_r2c_cold_world_host, serve_r0_blocking_transport,
    serve_r1a_blocking_transport, serve_r1x_blocking_transport,
    serve_r2b_playtest_blocking_transport, serve_r2b_playtest_with_r2c_cold_host,
};
use helve_target_26_2::{Target26_2R1xContext, generated};

const CONNECTION_TIMEOUT: Duration = Duration::from_secs(15);
const LOGIN_SESSION_EPOCH_PREFIX: &str = "--login-session-epoch=";
const R1X_REPLAY_IMAGE_PREFIX: &str = "--r1x-replay-image=";
const R2B_PLAYTEST_IMAGE_PREFIX: &str = "--r2b-playtest-image=";
const R2C_WORLD_PLAN_PREFIX: &str = "--r2c-world-plan=";
const R2C_HEIGHTMAP_CANDIDATE_PREFIX: &str = "--r2c-heightmap-candidate=";
const R1X_CAPTURE_SESSION_EPOCH_HEX: &str = "4d7f604f196a43b08987f0b2a27c2663";

#[derive(Debug)]
struct Options {
    bind_address: String,
    once: bool,
    login_session_epoch: Option<ServerSessionEpoch>,
    r1x_replay_image: Option<PathBuf>,
    r2b_playtest_image: Option<PathBuf>,
    r2c_world_plan: Option<PathBuf>,
    r2c_heightmap_candidate: Option<PathBuf>,
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("helve: {error}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<(), String> {
    let options = options()?;
    let r1x_context = load_selected_r1x(&options)?;
    let r2b_playtest = load_selected_r2b(&options)?;
    let r2c_world_plan = load_selected_r2c_plan(&options)?;
    // Import once at the server lifetime, not after any client reaches Play.
    // This COLD world cannot publish chunks in an ordinary build.
    let r2c_world_host = match (r2b_playtest.as_ref(), r2c_world_plan.as_ref()) {
        (Some(image), Some(plan)) => Some(
            prepare_r2c_cold_world_host(image, plan)
                .map_err(|error| format!("R2C server world rejected: {error}"))?,
        ),
        _ => None,
    };
    let listener = TcpListener::bind(&options.bind_address)
        .map_err(|error| format!("could not bind {}: {error}", options.bind_address))?;
    let local_address = listener
        .local_addr()
        .map_err(|error| format!("could not read listener address: {error}"))?;
    announce(
        local_address,
        &options,
        r1x_context.as_ref(),
        r2b_playtest.as_ref(),
    );

    loop {
        let (mut stream, peer) = listener
            .accept()
            .map_err(|error| format!("accept failed: {error}"))?;
        // Socket-option failures belong to this accepted connection, not
        // to the long-lived listener or its single resident COLD world.
        // Reuse the existing --once versus multi-connection error policy.
        if let Err(error) = configure_stream(&stream, peer) {
            report_connection("TCP setup", peer, options.once, Err::<(), _>(error))?;
            continue;
        }
        serve_connection(
            &mut stream,
            peer,
            &options,
            r1x_context.as_ref(),
            r2b_playtest.as_ref(),
            r2c_world_host.as_ref(),
        )?;
        if options.once {
            return Ok(());
        }
    }
}

fn load_selected_r1x(options: &Options) -> Result<Option<Target26_2R1xContext>, String> {
    options
        .r1x_replay_image
        .as_deref()
        .map(|path| {
            load_r1x_image(path, HELVE_STATUS_JSON).map_err(|error| {
                format!(
                    "could not load R1X replay image {}: {error}",
                    path.display()
                )
            })
        })
        .transpose()
}

fn load_selected_r2b(options: &Options) -> Result<Option<R2bPlaytestImage>, String> {
    options
        .r2b_playtest_image
        .as_deref()
        .map(|path| {
            load_r2b_playtest_image(path, HELVE_STATUS_JSON).map_err(|error| {
                format!(
                    "could not load R2B playtest image {}: {error}",
                    path.display()
                )
            })
        })
        .transpose()
}

fn load_selected_r2c_plan(options: &Options) -> Result<Option<R2cColdWorldPlan>, String> {
    options
        .r2c_world_plan
        .as_ref()
        .map(|path| {
            let plan = R2cColdWorldPlan::new(path.clone()).map_err(|error| {
                format!(
                    "R2C COLD world-plan directory {} rejected: {error:?}",
                    path.display()
                )
            })?;
            match options.r2c_heightmap_candidate.as_deref() {
                Some(candidate) => plan
                    .with_candidate_heightmap_file(candidate)
                    .map_err(|error| {
                        format!(
                            "R2C COLD heightmap candidate {} rejected: {error:?}",
                            candidate.display()
                        )
                    }),
                None => Ok(plan),
            }
        })
        .transpose()
}

fn announce(
    local_address: SocketAddr,
    options: &Options,
    r1x_context: Option<&Target26_2R1xContext>,
    r2b_playtest: Option<&R2bPlaytestImage>,
) {
    if r2b_playtest.is_some() {
        if let Some(path) = options.r2c_world_plan.as_ref() {
            println!(
                "R2C server-owned COLD plan requested for {} | selected Anvil source imported once before accept | no chunk publication | source_admitted=false",
                path.display()
            );
        }
        println!(
            "{PRODUCT_NAME} R2B playtest listening on {local_address} | Minecraft {} protocol {} | server brand {PRODUCT_NAME} | real Configuration | replay-free Play bootstrap | captured Play publication 0 | R2C world projection pending | production_admitted=false",
            generated::login_26_2::MINECRAFT_VERSION,
            generated::login_26_2::PROTOCOL_VERSION,
        );
    } else if let Some(context) = r1x_context {
        println!(
            "{PRODUCT_NAME} R1X listening on {local_address} | Minecraft {} protocol {} | server brand {PRODUCT_NAME} | Configuration admitted | experimental Play frames {} ({} body bytes) | production_admitted=false",
            generated::login_26_2::MINECRAFT_VERSION,
            generated::login_26_2::PROTOCOL_VERSION,
            context.play_frame_count(),
            context.play_body_bytes(),
        );
    } else if options.login_session_epoch.is_some() {
        println!(
            "{PRODUCT_NAME} R1A listening on {local_address} | Minecraft {} protocol {} | login contract {} | Configuration intentionally not yet admitted",
            generated::login_26_2::MINECRAFT_VERSION,
            generated::login_26_2::PROTOCOL_VERSION,
            generated::login_26_2::CONTRACT_ID,
        );
    } else {
        println!(
            "{PRODUCT_NAME} R0 listening on {local_address} | Minecraft {} protocol {} | contract {} | session {}",
            generated::MINECRAFT_VERSION,
            generated::PROTOCOL_VERSION,
            generated::CONTRACT_ID,
            R0_ADMISSION_SESSION_SHA256,
        );
    }
}

fn configure_stream(stream: &TcpStream, peer: SocketAddr) -> Result<(), String> {
    stream
        .set_read_timeout(Some(CONNECTION_TIMEOUT))
        .map_err(|error| format!("could not set read timeout for {peer}: {error}"))?;
    stream
        .set_write_timeout(Some(CONNECTION_TIMEOUT))
        .map_err(|error| format!("could not set write timeout for {peer}: {error}"))?;
    stream
        .set_nodelay(true)
        .map_err(|error| format!("could not enable TCP_NODELAY for {peer}: {error}"))
}

fn serve_connection(
    stream: &mut TcpStream,
    peer: SocketAddr,
    options: &Options,
    r1x_context: Option<&Target26_2R1xContext>,
    r2b_playtest: Option<&R2bPlaytestImage>,
    r2c_world_host: Option<&R2cColdWorldHost>,
) -> Result<(), String> {
    if let Some(image) = r2b_playtest {
        let session_epoch = options
            .login_session_epoch
            .expect("R2B playtest option normalization supplies the fixed capture epoch");
        return report_connection(
            "R2B playtest",
            peer,
            options.once,
            match r2c_world_host {
                Some(host) => {
                    serve_r2b_playtest_with_r2c_cold_host(stream, session_epoch, image, host)
                }
                None => serve_r2b_playtest_blocking_transport(stream, session_epoch, image),
            },
        );
    }
    if let Some(context) = r1x_context {
        let session_epoch = options
            .login_session_epoch
            .expect("R1X option normalization supplies the fixed capture epoch");
        return report_connection(
            "R1X",
            peer,
            options.once,
            serve_r1x_blocking_transport(stream, session_epoch, context),
        );
    }
    if let Some(session_epoch) = options.login_session_epoch {
        return report_connection(
            "R1A",
            peer,
            options.once,
            serve_r1a_blocking_transport(stream, session_epoch),
        );
    }
    report_connection(
        "R0",
        peer,
        options.once,
        serve_r0_blocking_transport(stream),
    )
}

fn report_connection<T, E>(
    route: &str,
    peer: SocketAddr,
    once: bool,
    result: Result<T, E>,
) -> Result<(), String>
where
    T: core::fmt::Debug,
    E: core::fmt::Debug,
{
    match result {
        Ok(exit) => {
            eprintln!("{route} connection {peer} completed: {exit:?}");
            Ok(())
        }
        Err(error) if !once => {
            eprintln!("{route} connection {peer} rejected: {error:?}");
            Ok(())
        }
        Err(error) => Err(format!("{route} connection {peer} failed: {error:?}")),
    }
}

fn options() -> Result<Options, String> {
    options_from(env::args().skip(1))
}

fn options_from(arguments: impl IntoIterator<Item = String>) -> Result<Options, String> {
    let mut bind_address = None;
    let mut once = false;
    let mut login_session_epoch = None;
    let mut r1x_replay_image = None;
    let mut r2b_playtest_image = None;
    let mut r2c_world_plan = None;
    let mut r2c_heightmap_candidate = None;

    for argument in arguments {
        if argument == "--once" {
            if once {
                return Err("--once may be supplied only once".to_owned());
            }
            once = true;
        } else if let Some(value) = argument.strip_prefix(LOGIN_SESSION_EPOCH_PREFIX) {
            let epoch = ServerSessionEpoch::parse_hex(value)
                .map_err(|error| format!("invalid --login-session-epoch: {error}"))?;
            if login_session_epoch.replace(epoch).is_some() {
                return Err("--login-session-epoch may be supplied only once".to_owned());
            }
        } else if let Some(value) = argument.strip_prefix(R1X_REPLAY_IMAGE_PREFIX) {
            if value.is_empty() {
                return Err("--r1x-replay-image requires a non-empty path".to_owned());
            }
            if r1x_replay_image.replace(PathBuf::from(value)).is_some() {
                return Err("--r1x-replay-image may be supplied only once".to_owned());
            }
        } else if let Some(value) = argument.strip_prefix(R2B_PLAYTEST_IMAGE_PREFIX) {
            if value.is_empty() {
                return Err("--r2b-playtest-image requires a non-empty path".to_owned());
            }
            if r2b_playtest_image.replace(PathBuf::from(value)).is_some() {
                return Err("--r2b-playtest-image may be supplied only once".to_owned());
            }
        } else if let Some(value) = argument.strip_prefix(R2C_WORLD_PLAN_PREFIX) {
            if value.is_empty() {
                return Err("--r2c-world-plan requires a non-empty path".to_owned());
            }
            if r2c_world_plan.replace(PathBuf::from(value)).is_some() {
                return Err("--r2c-world-plan may be supplied only once".to_owned());
            }
        } else if let Some(value) = argument.strip_prefix(R2C_HEIGHTMAP_CANDIDATE_PREFIX) {
            if value.is_empty() {
                return Err("--r2c-heightmap-candidate requires a non-empty file path".to_owned());
            }
            if r2c_heightmap_candidate
                .replace(PathBuf::from(value))
                .is_some()
            {
                return Err("--r2c-heightmap-candidate may be supplied only once".to_owned());
            }
        } else if argument.starts_with('-') {
            return Err(format!("unknown option {argument:?}"));
        } else if bind_address.replace(argument).is_some() {
            return Err("at most one bind address may be supplied".to_owned());
        }
    }

    if r2c_heightmap_candidate.is_some() && r2c_world_plan.is_none() {
        return Err("--r2c-heightmap-candidate requires --r2c-world-plan".to_owned());
    }

    if r2c_world_plan.is_some() && r2b_playtest_image.is_none() {
        return Err("--r2c-world-plan requires --r2b-playtest-image".to_owned());
    }

    if r1x_replay_image.is_some() && r2b_playtest_image.is_some() {
        return Err(
            "--r1x-replay-image and --r2b-playtest-image are mutually exclusive".to_owned(),
        );
    }

    if r1x_replay_image.is_some() || r2b_playtest_image.is_some() {
        let capture_epoch = ServerSessionEpoch::parse_hex(R1X_CAPTURE_SESSION_EPOCH_HEX)
            .expect("committed capture session epoch is valid");
        match login_session_epoch {
            Some(epoch) if epoch != capture_epoch => {
                return Err(format!(
                    "capture-qualified R1X/R2B development routes require --login-session-epoch={R1X_CAPTURE_SESSION_EPOCH_HEX}"
                ));
            }
            Some(_) => {}
            None => login_session_epoch = Some(capture_epoch),
        }
    }

    Ok(Options {
        bind_address: bind_address.unwrap_or_else(|| DEFAULT_R0_BIND_ADDRESS.to_owned()),
        once,
        login_session_epoch,
        r1x_replay_image,
        r2b_playtest_image,
        r2c_world_plan,
        r2c_heightmap_candidate,
    })
}

#[cfg(test)]
mod tests {
    use super::{
        DEFAULT_R0_BIND_ADDRESS, LOGIN_SESSION_EPOCH_PREFIX, PRODUCT_NAME,
        R1X_CAPTURE_SESSION_EPOCH_HEX, R1X_REPLAY_IMAGE_PREFIX, R2B_PLAYTEST_IMAGE_PREFIX,
        R2C_HEIGHTMAP_CANDIDATE_PREFIX, R2C_WORLD_PLAN_PREFIX, options, options_from,
        report_connection,
    };

    #[test]
    fn default_bind_address_remains_localhost() {
        assert_eq!(DEFAULT_R0_BIND_ADDRESS, "127.0.0.1:25565");
    }

    #[test]
    fn executable_product_name_is_helve() {
        assert_eq!(PRODUCT_NAME, "Helve");
    }

    #[test]
    fn dry_run_world_plan_requires_r2b_and_cannot_be_duplicated() {
        let args = |parts: &[&str]| {
            options_from(
                parts
                    .iter()
                    .map(|arg| (*arg).to_owned())
                    .collect::<Vec<_>>(),
            )
        };
        assert!(args(&["--r2c-world-plan=/tmp/world"]).is_err());
        assert!(args(&["--r2c-heightmap-candidate=/tmp/facts.bin"]).is_err());
        assert!(
            args(&[
                "--r2b-playtest-image=a",
                "--r2c-heightmap-candidate=/tmp/facts.bin"
            ])
            .is_err()
        );
        assert!(
            args(&[
                "--r2b-playtest-image=a",
                "--r2c-world-plan=/tmp/world",
                "--r2c-heightmap-candidate="
            ])
            .is_err()
        );
        assert!(args(&["--r1x-replay-image=a", "--r2c-world-plan=/tmp/world"]).is_err());
        assert!(args(&["--r2b-playtest-image=a", "--r2c-world-plan="]).is_err());
        assert!(
            args(&[
                "--r2b-playtest-image=a",
                "--r2c-world-plan=/tmp/world",
                "--r2c-world-plan=/tmp/other"
            ])
            .is_err()
        );
        let selected = args(&["--r2b-playtest-image=a", "--r2c-world-plan=/tmp/world"])
            .expect("a single opt-in R2B COLD plan is valid");
        assert_eq!(
            selected.r2c_world_plan.as_deref(),
            Some(std::path::Path::new("/tmp/world"))
        );
        let audited = args(&[
            "--r2b-playtest-image=a",
            "--r2c-world-plan=/tmp/world",
            "--r2c-heightmap-candidate=/tmp/facts.bin",
        ])
        .expect("candidate audit option requires the COLD world route");
        assert_eq!(
            audited.r2c_heightmap_candidate.as_deref(),
            Some(std::path::Path::new("/tmp/facts.bin"))
        );
        assert!(
            args(&[
                "--r2b-playtest-image=a",
                "--r2c-world-plan=/tmp/world",
                "--r2c-heightmap-candidate=/tmp/facts.bin",
                "--r2c-heightmap-candidate=/tmp/other.bin",
            ])
            .is_err()
        );
        assert!(
            args(&["--r2b-playtest-image=a"])
                .expect("existing R2B mode remains supported")
                .r2c_world_plan
                .is_none()
        );
    }

    #[test]
    fn accepted_socket_setup_error_is_local_unless_once() {
        let peer = "127.0.0.1:25566"
            .parse()
            .expect("fixed loopback peer is valid");
        assert!(
            report_connection("TCP setup", peer, false, Err::<(), _>("setup failed")).is_ok(),
            "a rejected socket must not terminate a multi-connection server",
        );
        assert!(
            report_connection("TCP setup", peer, true, Err::<(), _>("setup failed")).is_err(),
            "--once must still report an unsuccessful accepted connection",
        );
        assert!(
            report_connection("TCP setup", peer, false, Ok::<(), &str>(())).is_ok(),
            "successful setup is unchanged",
        );
    }

    #[test]
    fn option_parser_shape_is_kept_out_of_protocol_semantics() {
        let _ = options as fn() -> Result<super::Options, String>;
        assert_eq!(LOGIN_SESSION_EPOCH_PREFIX, "--login-session-epoch=");
        assert_eq!(R1X_REPLAY_IMAGE_PREFIX, "--r1x-replay-image=");
        assert_eq!(R2B_PLAYTEST_IMAGE_PREFIX, "--r2b-playtest-image=");
        assert_eq!(R2C_WORLD_PLAN_PREFIX, "--r2c-world-plan=");
        assert_eq!(R2C_HEIGHTMAP_CANDIDATE_PREFIX, "--r2c-heightmap-candidate=");
        assert_eq!(R1X_CAPTURE_SESSION_EPOCH_HEX.len(), 32);
    }
}
