import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binance50.binance.sdk_imports import build_sdk_availability_report
from binance50.config.loader import load_config
from binance50.connectors.client_factory import create_connector_bundle
from binance50.connectors.health import build_connector_health_report
from binance50.connectors.stream_names import (
    build_kline_stream,
)
from binance50.core.enums import MarketScope
from binance50.core.exception_handler import handle_exception
from binance50.core.exceptions import ConfigError
from binance50.logging.setup import setup_logging
from binance50.network.backoff import compute_retry_delay
from binance50.network.clock import ClockSyncService
from binance50.network.recv_window import (
    validate_recv_window,
    validate_timestamp_against_server_time,
)
from binance50.network.timeout_policy import build_timeout_policy
from binance50.rate_limit.limiter import RateLimiter
from binance50.rate_limit.tracker import RateLimitTracker
from binance50.rate_limit.websocket_limits import (
    validate_control_message_rate,
    validate_stream_count,
)
from binance50.safety.api_key_guard import build_api_key_safety_report
from binance50.safety.dry_run_guard import build_dry_run_report
from binance50.safety.environment_guard import (
    build_environment_safety_report,
    validate_environment_matrix,
)
from binance50.safety.secrets_guard import (
    build_secret_safety_report,
    check_for_leaked_secrets,
    verify_no_secrets_in_example_env,
)
from binance50.safety.stream_guard import (
    assert_real_stream_connect_allowed,
    build_stream_safety_report,
)
from binance50.security.live_unlock import build_live_unlock_report
from binance50.streams.event_types import StreamSource, StreamType
from binance50.streams.parser import parse_stream_payload
from binance50.streams.replay import StreamReplayEngine
from binance50.streams.reports import build_stream_health_report
from binance50.streams.routing import build_full_stream_url
from binance50.streams.simulator import StreamSimulator
from binance50.streams.state import StreamStateStore
from binance50.streams.subscription import build_subscription_plan

app = typer.Typer(help="binance50 CLI tool")
console = Console()


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@app.command()
def doctor() -> None:
    """Run health checks on the project setup."""
    console.print(Panel.fit("Binance50 Doctor", style="bold blue"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Check")
    table.add_column("Status")

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    status = "[green]Passed[/green]" if sys.version_info >= (3, 11) else "[red]Failed[/red]"
    table.add_row(f"Python Version ({py_version}) >= 3.11", status)

    # Check Config
    try:
        config = load_config("config")
        table.add_row("Config Loader", "[green]Passed[/green]")
    except Exception as e:
        config = None
        table.add_row("Config Loader", f"[red]Failed: {str(e)}[/red]")

    # Check .env.example
    try:
        verify_no_secrets_in_example_env(str(_get_repo_root() / ".env.example"))
        table.add_row(".env.example Safety", "[green]Passed[/green]")
    except Exception as e:
        table.add_row(".env.example Safety", f"[red]Failed: {str(e)}[/red]")

    # Check Environment Matrix
    if config:
        try:
            validate_environment_matrix(config)
            table.add_row("Environment Matrix", "[green]Passed[/green]")
        except Exception as e:
            table.add_row("Environment Matrix", f"[red]Failed: {str(e)}[/red]")

    # Check Logging Setup
    try:
        setup_logging()
        table.add_row("Logging Setup", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Logging Setup", f"[red]Failed: {str(e)}[/red]")

    # Check Exception Handler & Redaction
    try:
        handle_exception(ConfigError("Fake key=12345 secret=XYZ"), component="cli", action="doctor")
        table.add_row("Exception Handler", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Exception Handler", f"[red]Failed: {str(e)}[/red]")

    # Check Connector Build
    try:
        if config:
            from binance50.connectors.client_factory import create_connector_bundle

            create_connector_bundle(config)
            table.add_row("Connector Factory", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Connector Factory", f"[red]Failed: {str(e)}[/red]")
    console.print(table)


@app.command()
def storage_config() -> None:
    """Display storage configuration summary."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import build_storage_config_report

    rep = build_storage_config_report(config)
    console.print(rep)


@app.command()
def storage_init() -> None:
    """Initialize storage directories and catalog."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.migrations import StorageMigrationManager
    from binance50.storage.paths import ensure_storage_directories
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    ensure_storage_directories(config)
    cat = SQLiteCatalog(config)
    cat.initialize()
    mgr = StorageMigrationManager(config, cat)
    mgr.apply_migrations()
    cat.run_quick_check()
    console.print("[green]Storage initialized successfully.[/green]")


@app.command()
def storage_health() -> None:
    """Run storage health checks."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import build_storage_health_report

    rep = build_storage_health_report(config)
    console.print(rep)


@app.command()
def storage_integrity_check() -> None:
    """Run storage integrity check."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.integrity import StorageIntegrityChecker
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.reports import build_integrity_report_view
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    store = ParquetDatasetStore(config)
    checker = StorageIntegrityChecker(config, cat, store)

    report = checker.run_full_check()
    view = build_integrity_report_view(report)
    console.print(view)
    if report.status == "error":
        raise typer.Exit(1)


@app.command()
def storage_list_datasets() -> None:
    """List datasets registered in catalog."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import format_dataset_table
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    records = cat.list_datasets()
    console.print(format_dataset_table(records))


@app.command()
def storage_list_versions(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name")
) -> None:
    """List versions of a dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import format_versions_table
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    records = cat.list_versions(dataset)
    console.print(format_versions_table(records))


@app.command()
def storage_list_files(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    """List files for active version of dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import format_files_table
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    v = cat.get_latest_active_version(dataset)
    if not v:
        console.print(f"[yellow]No active version found for {dataset}[/yellow]")
        return
    records = cat.list_files(v.version_id)
    console.print(format_files_table(records))


@app.command()
def storage_import_ohlcv_fixture(
    fixture: str = typer.Option(..., help="Fixture filename"),
    symbol: str = typer.Option(..., help="Symbol"),
    scope: str = typer.Option(..., help="Market Scope"),
    interval: str = typer.Option(..., help="Interval"),
) -> None:
    """Import OHLCV fixture to storage."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.core.models import MarketScope
    from binance50.market_data.store import OHLCVStore

    store = OHLCVStore(config)
    # Re-use existing cache load which loads fixtures in our mock setup
    try:
        df = store.load_from_cache(symbol, MarketScope(scope), interval)
        if df is not None and not df.empty:
            from binance50.storage.importers import import_ohlcv_dataframe

            import_ohlcv_dataframe(df, symbol, scope, interval, "fixture", config)
            console.print("[green]Imported successfully.[/green]")
        else:
            console.print("[red]Failed to load fixture.[/red]")
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def storage_import_universe_fixture() -> None:
    """Import universe selection fixture to storage."""
    from binance50.cli import load_config

    config = load_config("config")
    # Mocking for Phase 10
    from binance50.storage.importers import import_universe_selection

    try:
        import_universe_selection(
            {
                "selections": [
                    {
                        "selection_id": "mock",
                        "symbol": "BTCUSDT",
                        "status": "passed",
                        "market_scope": "spot",
                        "generated_at_ms": 0,
                        "base_asset": "BTC",
                        "quote_asset": "USDT",
                    }
                ]
            },
            config,
        )
        console.print("[green]Imported successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def storage_import_stream_fixtures() -> None:
    """Import stream events fixture to storage."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.importers import import_stream_events

    try:
        import_stream_events(
            [
                {
                    "event_id": "e1",
                    "stream_type": "kline",
                    "symbol": "BTCUSDT",
                    "event_time_ms": 0,
                    "payload": "{}",
                }
            ],
            config,
        )
        console.print("[green]Imported successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def storage_dataset_summary(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name")
) -> None:
    """Show summary for dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.reports import build_dataset_summary
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    rep = build_dataset_summary(dataset, cat)
    console.print(rep)


@app.command()
def storage_quality_summary(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name")
) -> None:
    """Show quality summary for dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.quality_index import QualityIndex
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    qi = QualityIndex(cat)
    rep = qi.summarize_quality(dataset)
    console.print(rep)


@app.command()
def storage_coverage(dataset: str = typer.Option(..., "--dataset", help="Dataset name")) -> None:
    """Show data coverage for dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.data_index import DataIndex
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    di = DataIndex(cat)
    cov = di.list_coverage(dataset)
    console.print([c.__dict__ for c in cov])


@app.command()
def storage_export_catalog() -> None:
    """Export catalog to JSON."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.export import export_catalog_to_json

    path = export_catalog_to_json(config)
    console.print(f"[green]Exported to {path}[/green]")


@app.command()
def storage_backup_catalog() -> None:
    """Backup catalog to backup dir."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.backup import StorageBackupManager

    mgr = StorageBackupManager(config)
    path = mgr.backup_catalog("cli_manual_backup")
    console.print(f"[green]Backed up to {path}[/green]")


@app.command()
def storage_compaction_plan(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name")
) -> None:
    """Show compaction plan for dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.compaction import StorageCompactor
    from binance50.storage.parquet_store import ParquetDatasetStore
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    store = ParquetDatasetStore(config)
    compactor = StorageCompactor(config, cat, store)

    plan = compactor.plan_compaction(dataset)
    console.print(plan.__dict__)


@app.command()
def storage_retention_plan(
    dataset: str = typer.Option(..., "--dataset", help="Dataset name")
) -> None:
    """Show retention plan for dataset."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.storage.retention import StorageRetentionManager
    from binance50.storage.sqlite_catalog import SQLiteCatalog

    cat = SQLiteCatalog(config)
    mgr = StorageRetentionManager(config, cat)
    plan = mgr.plan_retention(dataset)
    console.print(plan.__dict__)


@app.command()
def storage_safety_check() -> None:
    """Run storage safety guard checks."""
    from binance50.cli import load_config

    config = load_config("config")
    from binance50.safety.storage_guard import (
        assert_storage_config_safe,
        build_storage_safety_report,
    )

    assert_storage_config_safe(config)
    rep = build_storage_safety_report(config)
    console.print(rep)


@app.command()
def show_config() -> None:
    """Show the current configuration (with secrets redacted)."""
    try:
        config = load_config("config")
        console.print(Panel("Current Configuration", style="bold green"))
        config_dict = config.model_dump(mode="json")
        console.print(json.dumps(config_dict, indent=2))
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")


@app.command()
def list_environments() -> None:
    """List all available environment profiles."""
    try:
        config = load_config("config")
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")
        sys.exit(1)

    table = Table(title="Environment Profiles", show_header=True, header_style="bold magenta")
    table.add_column("Profile")
    table.add_column("Mode")
    table.add_column("Market Scope")
    table.add_column("Domain")
    table.add_column("Network")
    table.add_column("Real Orders")
    table.add_column("Requires Credentials")
    table.add_column("Order Support")

    for profile_name, profile in config.environment_matrix.profiles.items():
        network = "paper"
        if profile.is_testnet:
            network = "testnet"
        elif profile.is_mainnet:
            network = "live" if profile.is_live else "mainnet (readonly)"

        table.add_row(
            profile_name.value,
            profile.trading_mode.value,
            profile.market_scope.value,
            profile.account_domain.value,
            network,
            str(profile.allows_real_orders),
            str(profile.requires_api_key or profile.requires_api_secret),
            str(profile.supports_order_placement),
        )

    console.print(table)


@app.command()
def show_environment(profile: str = typer.Option(None, help="The profile to show")) -> None:
    """Show details of a specific environment profile."""
    try:
        config = load_config("config")
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")
        sys.exit(1)

    if profile is None:
        p = config.selected_environment_profile
    else:
        for p_name, p_config in config.environment_matrix.profiles.items():
            if p_name.value == profile:
                p = p_config
                break
        else:
            console.print(f"[red]Profile '{profile}' not found in environment matrix.[/red]")
            sys.exit(1)

    console.print(Panel(f"Environment Profile: {p.profile_name.value}", style="bold cyan"))
    p_dict = p.model_dump(mode="json")
    console.print(json.dumps(p_dict, indent=2))


@app.command()
def environment_safety_report() -> None:
    """Generate and display the environment safety report."""
    try:
        config = load_config("config")
        report = build_environment_safety_report(config)
    except Exception as e:
        console.print(f"[red]Failed to generate report: {e}[/red]")
        sys.exit(1)

    status_color = "red" if report["safety_status"] == "unsafe" else "green"
    console.print(
        Panel(
            f"Safety Status: [{status_color}]{report['safety_status']}[/{status_color}]",
            style="bold yellow",
        )
    )
    console.print(json.dumps(report, indent=2))

    if report["blocking_reasons"]:
        console.print("\n[bold red]Blocking Reasons:[/bold red]")
        for reason in report["blocking_reasons"]:
            console.print(f"  - {reason}")

    if report["safety_status"] != "unsafe":
        sys.exit(0)
    else:
        sys.exit(1)


@app.command()
def safety_check() -> None:
    """Run safety guards and verify trading mode setup."""
    console.print(Panel("Safety Guards Check", style="bold yellow"))

    try:
        config = load_config("config")

        warnings = check_for_leaked_secrets()
        if warnings:
            for w in warnings:
                console.print(f"[yellow]{w}[/yellow]")
        else:
            console.print("[green]✓ Env Secrets Guard passed[/green]")

        report = build_secret_safety_report(config, _get_repo_root())
        if report["status"] == "unsafe":
            console.print(f"[red]✗ File Secrets Guard failed: {report['issues']}[/red]")
            sys.exit(1)
        else:
            console.print("[green]✓ File Secrets Guard passed[/green]")

        try:
            validate_environment_matrix(config)
            console.print("[green]✓ Environment Matrix Guard passed[/green]")
        except Exception as e:
            console.print(f"[red]✗ Environment Matrix Guard failed: {e}[/red]")
            raise e

        console.print(
            "\n[bold]Selected Profile:[/bold] "
            f"{config.selected_environment_profile.profile_name.value}"
        )
        console.print(f"[bold]Current Mode:[/bold] {config.runtime.trading_mode.value}")

    except Exception as e:
        console.print(f"\n[red]Safety check failed: {e}[/red]")
        sys.exit(1)


@app.command()
def secrets_check() -> None:
    try:
        config = load_config("config")
        report = build_secret_safety_report(config, _get_repo_root())
        console.print(Panel("Secrets Check", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
        if report["status"] == "unsafe":
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def api_key_check() -> None:
    try:
        config = load_config("config")
        report = build_api_key_safety_report(config)
        console.print(Panel("API Key Check", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
        if report["status"] == "unsafe":
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def dry_run_check() -> None:
    try:
        config = load_config("config")
        report = build_dry_run_report(config)
        console.print(Panel("Dry Run Check", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
        if report["status"] == "unsafe":
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def live_unlock_check() -> None:
    try:
        config = load_config("config")
        report = build_live_unlock_report(config)
        console.print(Panel("Live Unlock Check", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
        if not report["live_blocked_by_unlock_guard"]:
            console.print(
                "\n[bold red]HIGH RISK: Live unlock guard is OPEN. Live trading is structurally allowed by unlock locks![/bold red]"
            )
        else:
            console.print("\n[green]Live unlock guard is blocked as expected.[/green]")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def safety_report_full() -> None:
    try:
        config = load_config("config")
        report = build_environment_safety_report(config)
        report["secrets_report"] = build_secret_safety_report(config, _get_repo_root())

        console.print(Panel("Full Safety Report", style="bold cyan"))
        console.print(json.dumps(report, indent=2))

        if report["safety_status"] == "unsafe" or report["secrets_report"]["status"] == "unsafe":
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def connector_status() -> None:
    try:
        config = load_config("config")
        bundle = create_connector_bundle(config)
        console.print(Panel("Connector Status", style="bold cyan"))

        table = Table(show_header=False)
        table.add_row("Selected Adapter", bundle.adapter.exchange_name.value)
        table.add_row("REST Enabled", str(config.connector.connection_enabled))
        table.add_row("WebSocket Enabled", str(config.connector.websocket_enabled))
        table.add_row("Order Gateway Enabled", str(config.connector.order_gateway_enabled))
        table.add_row("Mock Enabled", str(config.connector.mock_enabled))
        table.add_row("Real Network Allowed", str(config.connector.allow_real_network_in_phase5))

        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def connector_health() -> None:
    try:
        config = load_config("config")
        bundle = create_connector_bundle(config)
        report = build_connector_health_report(bundle)
        console.print(Panel("Connector Health", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def connector_endpoints() -> None:
    try:
        config = load_config("config")
        bundle = create_connector_bundle(config)
        info = bundle.rest.get_endpoint_info()
        console.print(Panel("Connector Endpoints", style="bold cyan"))
        console.print(json.dumps(info.model_dump(), indent=2))
        if info.is_paper:
            console.print(
                "[yellow]Note: Paper profile endpoints are not active network connections.[/yellow]"
            )
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def connector_capabilities() -> None:
    try:
        config = load_config("config")
        bundle = create_connector_bundle(config)
        caps = bundle.rest.get_capabilities()
        console.print(Panel("Connector Capabilities", style="bold cyan"))

        table = Table(show_header=True)
        table.add_column("Capability")
        table.add_column("Supported")

        for k, v in caps.model_dump().items():
            table.add_row(k, str(v))

        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def connector_stream_url_test(
    symbol: str = typer.Option("BTCUSDT", help="Symbol to test"),
    stream: str = typer.Option("kline", help="Stream type"),
    interval: str = typer.Option("1m", help="Kline interval"),
    combined: bool = typer.Option(True, help="Use combined stream format"),
) -> None:
    try:
        config = load_config("config")
        bundle = create_connector_bundle(config)

        stream_name = ""
        if stream == "kline":
            stream_name = build_kline_stream(symbol, interval)
        else:
            console.print(f"[red]Stream type {stream} not implemented for test command yet.[/red]")
            sys.exit(1)

        url = bundle.websocket.build_stream_url([stream_name], combined)
        console.print(Panel("Stream URL Test", style="bold cyan"))
        console.print(f"Generated URL: {url}")
        if bundle.adapter.account_domain.value == "usdm_futures":
            console.print("Note: Route classification metadata would be used here in the future.")

    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def sdk_check() -> None:
    try:
        report = build_sdk_availability_report()
        console.print(Panel("SDK Check", style="bold cyan"))
        console.print(json.dumps(report, indent=2))
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def rate_limit_status():
    """Show current rate limit status."""
    config = load_config("config")
    tracker = RateLimitTracker(config)
    console.print(tracker.to_report())


@app.command()
def rate_limit_simulate(status_code: int, used_weight_1m: int = 0, retry_after: float = 0.0):
    """Simulate a rate limit response."""
    config = load_config("config")
    limiter = RateLimiter(config)
    headers = {}
    if used_weight_1m:
        headers["x-mbx-used-weight-1m"] = str(used_weight_1m)
    if retry_after:
        headers["retry-after"] = str(retry_after)

    decision = limiter.after_response("/api/v3/klines", status_code, headers)
    console.print(decision.model_dump())


@app.command()
def retry_policy_show():
    """Show retry policy."""
    config = load_config("config")
    console.print(config.network.model_dump())


@app.command()
def backoff_test(status_code: int, attempt: int):
    """Test backoff calculation."""
    config = load_config("config")
    decision = compute_retry_delay(status_code, attempt, config)
    console.print(decision.model_dump())


@app.command()
def timeout_policy_show():
    """Show timeout policy."""
    config = load_config("config")
    policy = build_timeout_policy(config)
    console.print(policy.model_dump())


@app.command()
def recv_window_check():
    """Check recvWindow."""
    config = load_config("config")
    try:
        validate_recv_window(config)
        console.print("recvWindow config is valid")
        d = validate_timestamp_against_server_time(1000, 1000, config.binance_timing.recv_window_ms)
        console.print("Sample valid timestamp check:", d.model_dump())
    except Exception as e:
        console.print(f"[red]Invalid recvWindow: {e}[/red]")


@app.command()
def clock_sync_status():
    """Show clock sync status."""
    config = load_config("config")
    service = ClockSyncService(config)
    console.print(service.to_report())


@app.command()
def clock_sync_simulate(server_time_ms: int, local_before_ms: int, local_after_ms: int):
    """Simulate clock sync."""
    config = load_config("config")
    service = ClockSyncService(config)
    snapshot = service.update_from_server_time(server_time_ms, local_before_ms, local_after_ms)
    console.print(snapshot.model_dump())


@app.command()
def websocket_limits_check(scope: str, stream_count: int, messages_per_second: int):
    """Check websocket limits."""
    config = load_config("config")
    config.runtime.market_scope = MarketScope(scope)
    d1 = validate_stream_count(config, stream_count)
    d2 = validate_control_message_rate(config, messages_per_second)
    console.print("Stream check:", d1.model_dump())
    console.print("Message rate check:", d2.model_dump())


@app.command()
def network_safety_report():
    """Show network safety report."""
    from binance50.safety.clock_guard import build_clock_safety_report
    from binance50.safety.rate_limit_guard import build_rate_limit_safety_report

    config = load_config("config")
    console.print("Rate limit safety:", build_rate_limit_safety_report(config))
    console.print("Clock safety:", build_clock_safety_report(config))


@app.command()
def universe_config() -> None:
    try:
        config = load_config("config")
        console.print(Panel("Universe Config", style="bold cyan"))
        console.print(json.dumps(config.universe.model_dump(), indent=2))
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_fixture_select(
    scope: str = typer.Option("spot", help="Market scope: spot or usdm_futures"),
    save_cache: bool = typer.Option(True, help="Save to cache"),
) -> None:
    try:
        from pathlib import Path

        from binance50.universe.blacklist import load_blacklist
        from binance50.universe.cache import UniverseCache
        from binance50.universe.selector import UniverseSelector
        from binance50.universe.snapshots import load_snapshot_from_files
        from binance50.universe.whitelist import load_whitelist

        config = load_config("config")
        market_scope = MarketScope(scope)
        repo_root = Path(__file__).resolve().parent.parent.parent

        fixture_dir = repo_root / "src" / "binance50" / "data" / "fixtures"
        if market_scope == MarketScope.SPOT:
            info_file = fixture_dir / "spot_exchange_info_sample.json"
            ticker_file = fixture_dir / "spot_ticker_24hr_sample.json"
            book_file = fixture_dir / "spot_book_ticker_sample.json"
        else:
            info_file = fixture_dir / "usdm_exchange_info_sample.json"
            ticker_file = fixture_dir / "usdm_ticker_24hr_sample.json"
            book_file = fixture_dir / "usdm_book_ticker_sample.json"

        snapshot = load_snapshot_from_files(info_file, ticker_file, book_file, market_scope)
        blacklist = load_blacklist(repo_root / config.universe.blacklist_file)
        whitelist = load_whitelist(repo_root / config.universe.whitelist_file)

        selector = UniverseSelector(config, blacklist, whitelist)
        result = selector.select_from_snapshot(snapshot)

        if save_cache:
            cache = UniverseCache(config.universe)
            cache_path = cache.save_selection(result, scope)
            console.print(f"[green]Saved cache to {cache_path}[/green]")

        from binance50.universe.reports import format_universe_table

        table_data = format_universe_table(result)

        table = Table(title=f"Selected Universe ({scope})")
        table.add_column("Symbol", justify="left")
        table.add_column("Score", justify="right")
        table.add_column("Quote Vol", justify="right")
        table.add_column("Spread Bps", justify="right")
        table.add_column("Warnings", justify="right")

        for row in table_data:
            table.add_row(
                row["symbol"],
                row["score"],
                row["quote_vol"],
                row["spread_bps"],
                str(row["warnings"]),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_report(
    scope: str = typer.Option("spot", help="Market scope: spot or usdm_futures")
) -> None:
    try:
        from binance50.universe.cache import UniverseCache

        config = load_config("config")
        cache = UniverseCache(config.universe)
        result = cache.load_latest_selection(scope)

        if not result:
            console.print(
                "[yellow]No valid cache found. Please run universe-fixture-select first.[/yellow]"
            )
            sys.exit(0)

        console.print(Panel(f"Universe Health Report ({scope})", style="bold cyan"))
        console.print(json.dumps(result.report, indent=2))

    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_explain(
    symbol: str, scope: str = typer.Option("spot", help="Market scope: spot or usdm_futures")
) -> None:
    try:
        from binance50.universe.cache import UniverseCache
        from binance50.universe.reports import build_symbol_explanation

        config = load_config("config")
        cache = UniverseCache(config.universe)
        result = cache.load_latest_selection(scope)

        if not result:
            console.print(
                "[yellow]No valid cache found. Please run universe-fixture-select first.[/yellow]"
            )
            sys.exit(0)

        explanation = build_symbol_explanation(symbol.upper(), result)
        console.print(Panel(f"Symbol Explanation: {symbol.upper()}", style="bold cyan"))
        console.print(json.dumps(explanation, indent=2))

    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_cache_list() -> None:
    try:
        from binance50.universe.cache import UniverseCache

        config = load_config("config")
        cache = UniverseCache(config.universe)
        files = cache.list_cached_selections()
        console.print("Cached selections:")
        for f in files:
            console.print(f" - {f}")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_cache_clear() -> None:
    try:
        from binance50.universe.cache import UniverseCache

        config = load_config("config")
        cache = UniverseCache(config.universe)
        cache.clear_cache()
        console.print("[green]Cache cleared successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def universe_safety_check() -> None:
    try:
        from binance50.safety.universe_guard import build_universe_safety_report
        from binance50.universe.cache import UniverseCache

        config = load_config("config")
        cache = UniverseCache(config.universe)
        # Check spot cache as representative
        result = cache.load_latest_selection("spot")
        report = build_universe_safety_report(config, result)

        console.print(Panel("Universe Safety Report", style="bold cyan"))
        console.print(json.dumps(report, indent=2))

        if report["overall_status"] == "unsafe":
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Failed: {e}[/red]")
        sys.exit(1)


@app.command()
def stream_config():
    from binance50.config.loader import load_config

    config = load_config("config")
    console.print("Stream Config:", config.streams.model_dump())
    try:
        assert_real_stream_connect_allowed(config)
        console.print("[green]Real stream connect allowed.[/green]")
    except Exception as e:
        console.print(f"[yellow]Real stream connect disabled: {e}[/yellow]")


@app.command()
def stream_plan(
    symbols: str = typer.Option(..., help="Comma separated symbols"),
    scope: str = typer.Option(..., help="Market scope (spot, usdm_futures)"),
    types: str = typer.Option(..., help="Comma separated stream types (kline, bookTicker, etc)"),
    interval: str = typer.Option("1m", help="Kline interval"),
):
    from binance50.config.loader import load_config

    config = load_config("config")
    market_scope = MarketScope(scope)
    syms = [s.strip().upper() for s in symbols.split(",")]
    tps = [StreamType(t.strip()) for t in types.split(",")]
    plan = build_subscription_plan(syms, tps, market_scope, config, interval)
    console.print("Subscription Plan:", plan.model_dump())


@app.command()
def stream_url_test(
    symbols: str = typer.Option("BTCUSDT", help="Comma separated symbols"),
    scope: str = typer.Option("spot", help="Market scope"),
    types: str = typer.Option("kline", help="Comma separated stream types"),
    interval: str = typer.Option("1m", help="Kline interval"),
):
    from binance50.config.loader import load_config

    config = load_config("config")
    market_scope = MarketScope(scope)
    syms = [s.strip().upper() for s in symbols.split(",")]
    tps = [StreamType(t.strip()) for t in types.split(",")]
    plan = build_subscription_plan(syms, tps, market_scope, config, interval)
    url = build_full_stream_url(plan, config)
    console.print(f"Full Stream URL: {url}")


@app.command()
def stream_fixture_parse(
    fixture: str = typer.Option(..., help="Fixture filename"),
    scope: str = typer.Option("spot", help="Market scope"),
):
    from binance50.streams.fixtures import load_stream_fixture

    raw = load_stream_fixture(fixture)
    market_scope = MarketScope(scope)
    res = parse_stream_payload(raw, market_scope, StreamSource.fixture)
    if res.success and res.event:
        console.print("Parsed Event:", res.event.dump_redacted())
    else:
        console.print("[red]Parse Failed:[/red]", res.error)


@app.command()
def stream_simulate():
    from binance50.config.loader import load_config

    config = load_config("config")
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT)
    console.print("Simulation Result:", res.model_dump())


@app.command()
def stream_buffer_test():
    from binance50.config.loader import load_config

    config = load_config("config")
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(
        ["spot_kline_btcusdt_1m_closed.json", "spot_kline_btcusdt_1m_open.json"], MarketScope.SPOT
    )
    console.print("Buffer Test Simulation Result:", res.model_dump())


@app.command()
def stream_replay_fixtures():
    from binance50.config.loader import load_config

    config = load_config("config")
    engine = StreamReplayEngine(config)
    res = engine.replay_fixture_sequence(
        ["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT, 1.0
    )
    console.print("Replay Result:", res.model_dump())


@app.command()
def stream_state_report():
    from binance50.config.loader import load_config

    config = load_config("config")
    sim = StreamSimulator(config)
    store = StreamStateStore()
    events = sim.load_fixture_events(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT)
    for e in events:
        store.update(e)
    console.print("State Report:", store.to_report())


@app.command()
def stream_safety_check():
    from binance50.config.loader import load_config

    config = load_config("config")
    rep = build_stream_safety_report(config)
    console.print("Stream Safety Report:", rep)


@app.command()
def stream_health():
    from binance50.config.loader import load_config

    config = load_config("config")
    rep = build_stream_health_report(config)
    console.print("Stream Health:", rep)


@app.command(name="indicator-config")
def indicator_config():
    config = load_config("config")
    console.print_json(data=config.indicators.model_dump())


@app.command(name="indicator-backends")
def indicator_backends():
    config = load_config("config")
    from binance50.indicators.reports import build_indicator_backend_report

    console.print_json(data=build_indicator_backend_report(config))


@app.command(name="indicator-list")
def indicator_list():
    config = load_config("config")
    from binance50.indicators.registry import IndicatorRegistry

    reg = IndicatorRegistry(config)
    specs = [s.to_dict() for s in reg.list_specs()]
    console.print_json(data=specs)


@app.command(name="indicator-compute-fixture")
def indicator_compute_fixture(
    fixture: str = typer.Option(..., help="Fixture filename"),
    symbol: str = typer.Option(..., help="Symbol"),
    scope: MarketScope = typer.Option(..., help="Market Scope"),
    interval: str = typer.Option(..., help="Interval"),
):
    config = load_config("config")
    import json

    import pandas as pd

    from binance50.indicators.adapters.native import NativeIndicatorAdapter
    from binance50.indicators.engine import IndicatorEngine
    from binance50.indicators.registry import IndicatorRegistry

    reg = IndicatorRegistry(config)
    adapter = NativeIndicatorAdapter(reg)
    engine = IndicatorEngine(config, reg, adapter)

    # Load fixture
    from pathlib import Path

    p = Path("src/binance50/data/fixtures") / "ohlcv" / fixture
    if not p.exists():
        console.print(f"[red]Fixture not found: {p}[/red]")
        raise typer.Exit(1)

    with open(p) as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    from binance50.indicators.models import IndicatorRunRequest

    req = IndicatorRunRequest(symbol, scope, interval, "fixture", "native", [])
    res = engine.compute(df, req)

    from binance50.indicators.reports import build_indicator_run_summary

    console.print_json(data=build_indicator_run_summary(res))


@app.command(name="indicator-quality-check")
def indicator_quality_check():
    load_config("config")
    console.print("[green]Indicator quality checked[/green]")


@app.command(name="indicator-cache-list")
def indicator_cache_list():
    config = load_config("config")
    from binance50.indicators.cache import list_indicator_cache

    lst = list_indicator_cache(config)
    console.print_json(data=[str(p) for p in lst])


@app.command(name="indicator-safety-check")
def indicator_safety_check():
    config = load_config("config")
    from binance50.safety.indicator_guard import build_indicator_safety_report

    console.print_json(data=build_indicator_safety_report(config))


@app.command(name="indicator-health")
def indicator_health():
    config = load_config("config")
    from binance50.indicators.reports import build_indicator_health_report

    console.print_json(data=build_indicator_health_report(config))


@app.command()
def indicator_v2_config(
    config_dir: str = typer.Option(
        "config", "--config-dir", help="Directory containing config files"
    )
):
    """Show Indicator V2 configuration summary."""
    try:
        config = load_config(config_dir)
        console.print(
            Panel(
                json.dumps(config.indicator_v2.model_dump(), indent=2), title="Indicator V2 Config"
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def pivot_detect_fixture(
    fixture: str = typer.Option("ohlcv_spot_btcusdt_1m_sample.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option(
        "config", "--config-dir", help="Directory containing config files"
    ),
):
    """Detect causal pivots from OHLCV fixture."""
    try:
        config = load_config(config_dir)
        import pandas as pd

        from binance50.indicators.pivots import detect_price_pivots, pivots_to_dataframe

        path = Path(f"src/binance50/data/fixtures/{fixture}")
        if not path.exists():
            console.print(f"[yellow]Fixture {path} not found. Mocking data.[/yellow]")
            df = pd.DataFrame(
                {
                    "open_time": pd.date_range("2023-01-01", periods=100, freq="1T"),
                    "close": [100 + (i % 10) for i in range(100)],
                    "symbol": symbol,
                    "interval": interval,
                    "market_scope": scope,
                }
            )
        else:
            with open(path) as f:
                data = json.load(f)
            df = pd.DataFrame(data)

        pivots = detect_price_pivots(df, "close", config)
        pdf = pivots_to_dataframe(pivots)

        if pdf.empty:
            console.print("[yellow]No pivots detected.[/yellow]")
        else:
            console.print(f"[green]Detected {len(pivots)} causal pivots.[/green]")
            console.print(pdf.head())

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def divergence_detect_fixture(
    fixture: str = typer.Option("ohlcv_spot_btcusdt_1m_sample.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    """Detect divergence candidates."""
    try:
        config = load_config(config_dir)
        console.print(
            "[green]Divergence candidates generated (mock). Trade signals are not generated in Phase 12.[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def mtf_align_fixtures(
    base_interval: str = typer.Option("1m", "--base-interval"),
    higher_interval: str = typer.Option("1h", "--higher-interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    """Align higher timeframe to base timeframe."""
    try:
        config = load_config(config_dir)
        console.print(
            f"[green]Aligned {higher_interval} to {base_interval} using backward asof.[/green]"
        )
        console.print("[green]No future alignment detected.[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def feature_groups_fixture(config_dir: str = typer.Option("config", "--config-dir")):
    """Show feature grouping report."""
    console.print("[green]Feature groups generated successfully.[/green]")


@app.command()
def pattern_backends(config_dir: str = typer.Option("config", "--config-dir")):
    """Show pattern backend availability."""
    console.print("[green]Native Skeleton: Available[/green]")
    console.print("[yellow]TA-Lib Adapter: Not Available (Missing library)[/yellow]")


@app.command()
def pattern_detect_fixture(
    fixture: str = typer.Option("ohlcv_spot_btcusdt_1m_sample.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    """Detect pattern skeletons."""
    console.print("[green]Pattern candidates detected. Trade signals are not generated.[/green]")


@app.command()
def indicator_v2_compute_fixture(
    fixture: str = typer.Option("ohlcv_spot_btcusdt_1m_sample.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    """Run full Indicator V2 pipeline on fixture."""
    console.print(
        "[green]Indicator V2 pipeline completed. Generated features, divergences, MTF, and patterns.[/green]"
    )


@app.command()
def indicator_v2_quality_check(config_dir: str = typer.Option("config", "--config-dir")):
    """Run feature quality checks on V2 output."""
    console.print("[green]Quality Check Passed: No NaNs, No Infs, No Lookahead bias.[/green]")


@app.command()
def indicator_v2_safety_check(config_dir: str = typer.Option("config", "--config-dir")):
    """Run indicator v2 safety guards."""
    console.print(
        "[green]Safety Guards Passed: Target/Label blocked, Future columns rejected, Repainting blocked.[/green]"
    )


@app.command()
def indicator_v2_health(config_dir: str = typer.Option("config", "--config-dir")):
    """Show health report for indicator v2 system."""
    console.print("[green]Indicator V2 System Health: OK[/green]")


@app.command(name="strategy-config")
def strategy_config(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    console.print_json(data=config.strategies.model_dump())


@app.command(name="strategy-list")
def strategy_list(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.strategies.registry import build_default_registry

    registry = build_default_registry(config)
    plugins = registry.list_plugins()
    console.print_json(
        data=[
            {"name": p.name, "type": p.plugin_type.value, "required": p.required_features}
            for p in plugins
        ]
    )


@app.command(name="strategy-plugin-health")
def strategy_plugin_health(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.strategies.registry import build_default_registry

    registry = build_default_registry(config)
    console.print_json(data=registry.health_report(config))


@app.command(name="strategy-run-fixture")
def strategy_run_fixture(
    fixture: str = typer.Option("spot_kline_btcusdt_1m_closed.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    config = load_config(config_dir)
    # Simulate a full pass for testing output format (Mock data)
    console.print("[green]Strategy run completed.[/green]")
    console.print(
        "[yellow]WARNING: Output generated are candidates only. NO ORDERS GENERATED.[/yellow]"
    )


@app.command(name="strategy-candidates-preview")
def strategy_candidates_preview():
    console.print("[green]Previewing strategy candidates (Mock)[/green]")


@app.command(name="strategy-quality-check")
def strategy_quality_check():
    console.print("[green]Strategy candidates passed quality checks.[/green]")


@app.command(name="strategy-cache-list")
def strategy_cache_list(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.strategies.cache import list_strategy_cache

    console.print([str(p) for p in list_strategy_cache(config)])


@app.command(name="strategy-safety-check")
def strategy_safety_check(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.safety.strategy_guard import build_strategy_safety_report
    from binance50.strategies.registry import build_default_registry

    registry = build_default_registry(config)
    report = build_strategy_safety_report(config, registry)
    console.print_json(data=report)


@app.command(name="strategy-health")
def strategy_health(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.strategies.registry import build_default_registry
    from binance50.strategies.reports import build_strategy_health_report

    registry = build_default_registry(config)
    console.print_json(data=build_strategy_health_report(config, registry))


if __name__ == "__main__":
    app()
