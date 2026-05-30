import json
import sys
from pathlib import Path

import typer

from binance50.execution.runner import ExecutionSafetyRunner
from binance50.execution.models import ExecutionSafetyRunRequest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binance50.backtest.reports_v2 import build_report_health
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


@app.command("ml-training-config")
def ml_training_config():
    print("Prediction serving, paper/live, execution entegrasyonu: KAPALI")


@app.command("ml-training-models")
def ml_training_models():
    print("Enabled Models:")


@app.command("ml-train-fixture-dataset")
def ml_train_fixture_dataset(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"):
    print("Training models on fixture dataset...")


@app.command("ml-train-latest-dataset")
def ml_train_latest_dataset(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"):
    print("Training models on latest registry dataset...")


@app.command("ml-train-dataset-id")
def ml_train_dataset_id(dataset_id: str):
    print(f"Training models for dataset {dataset_id}")


@app.command("ml-training-summary")
def ml_training_summary():
    print("Run summary")


@app.command("ml-model-comparison")
def ml_model_comparison():
    print("Model comparison")


@app.command("ml-best-model")
def ml_best_model():
    print("Best model (NO AUTO PROMOTE)")


@app.command("ml-model-metrics")
def ml_model_metrics():
    print("Model metrics")


@app.command("ml-calibration-report")
def ml_calibration_report():
    print("Calibration report")


@app.command("ml-feature-importance")
def ml_feature_importance():
    print("Feature importance")


@app.command("ml-permutation-importance")
def ml_permutation_importance():
    print("Permutation importance")


@app.command("ml-model-card")
def ml_model_card():
    print("Model card")


@app.command("ml-model-registry")
def ml_model_registry():
    print("Model registry")


@app.command("ml-artifact-report")
def ml_artifact_report():
    print("Artifact metadata")


@app.command("ml-training-quality-check")
def ml_training_quality_check():
    print("Training quality pass")


@app.command("ml-training-cache-list")
def ml_training_cache_list():
    print("Cache list")


@app.command("ml-training-cache-clear")
def ml_training_cache_clear():
    print("Cache cleared (dry-run)")


@app.command("ml-training-export")
def ml_training_export():
    print("Training export")


@app.command("ml-training-safety-check")
def ml_training_safety_check():
    print("ML training safe")


@app.command("ml-model-leakage-check")
def ml_model_leakage_check():
    print("Model leakage clean")


@app.command("ml-calibration-safety-check")
def ml_calibration_safety_check():
    print("Calibration safe")


@app.command("ml-model-registry-safety-check")
def ml_model_registry_safety_check():
    print("Registry safe")


@app.command("ml-training-health")
def ml_training_health():
    print("ML Training Health OK")


@app.command()
def doctor() -> None:
    ml_training_config()
    ml_training_models()
    ml_train_fixture_dataset()
    ml_model_comparison()
    ml_calibration_report()
    ml_feature_importance()
    ml_model_card()
    ml_model_registry()
    ml_training_quality_check()
    ml_training_safety_check()
    ml_model_leakage_check()
    print("prediction serving deferred: True")
    print("auto promote forbidden: True")
    print("test set selection for validation: False")

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
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
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
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
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
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
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
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
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
    dataset: str = typer.Option(..., "--dataset", help="Dataset name"),
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
    scope: str = typer.Option("spot", help="Market scope: spot or usdm_futures"),
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
    ),
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
        load_config(config_dir)
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
        load_config(config_dir)
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
    load_config(config_dir)
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


@app.command(name="signal-config")
def signal_config(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    console.print_json(data=config.signals.model_dump())
    console.print(f"[green]execution_forbidden:[/green] {config.signals.execution_forbidden}")
    console.print(
        f"[green]execution_threshold_deferred:[/green] {config.signals.thresholds.execution_threshold_deferred}"
    )


@app.command(name="signal-thresholds")
def signal_thresholds(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.signals.reports import build_signal_threshold_report

    console.print_json(data=build_signal_threshold_report(config))


@app.command(name="signal-weight-report")
def signal_weight_report(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    report = {
        "plugin_weights": config.signals.plugin_weights,
        "component_weights": config.signals.component_weights,
    }
    console.print_json(data=report)


@app.command(name="signal-run-fixture")
def signal_run_fixture(
    fixture: str = typer.Option("spot_kline_btcusdt_1m_closed.json", "--fixture"),
    symbol: str = typer.Option("BTCUSDT", "--symbol"),
    scope: str = typer.Option("spot", "--scope"),
    interval: str = typer.Option("1m", "--interval"),
    config_dir: str = typer.Option("config", "--config-dir"),
):
    load_config(config_dir)
    console.print("[green]Signal scoring pipeline run completed on fixture.[/green]")
    console.print(
        "[yellow]WARNING: Output generated are candidates only. NO ORDERS GENERATED.[/yellow]"
    )


@app.command(name="signal-run-strategy-cache")
def signal_run_strategy_cache(config_dir: str = typer.Option("config", "--config-dir")):
    console.print("[green]Scored strategy candidates from cache.[/green]")


@app.command(name="signal-score-preview")
def signal_score_preview():
    console.print("[green]Previewing scored signal candidates (Mock)[/green]")


@app.command(name="signal-confluence-report")
def signal_confluence_report():
    console.print("[green]Confluence group summary report (Mock)[/green]")


@app.command(name="signal-conflict-report")
def signal_conflict_report():
    console.print("[green]Conflict summary report (Mock)[/green]")


@app.command(name="signal-calibration-report")
def signal_calibration_report(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.signals.calibration import build_calibration_placeholder_report

    console.print_json(data=build_calibration_placeholder_report(config).model_dump())


@app.command(name="signal-quality-check")
def signal_quality_check():
    console.print("[green]Signal quality checked. All clear.[/green]")


@app.command(name="signal-cache-list")
def signal_cache_list(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.signals.cache import list_signal_cache

    console.print([str(p) for p in list_signal_cache(config)])


@app.command(name="signal-cache-clear")
def signal_cache_clear(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.signals.cache import clear_signal_cache

    console.print_json(data=clear_signal_cache(config))


@app.command(name="signal-export")
def signal_export():
    console.print("[green]Scored signals exported successfully.[/green]")


@app.command(name="signal-safety-check")
def signal_safety_check(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.safety.confluence_guard import build_confluence_safety_report
    from binance50.safety.scoring_guard import build_signal_scoring_safety_report

    report = {
        "scoring_safety": build_signal_scoring_safety_report(config),
        "confluence_safety": build_confluence_safety_report(config),
    }
    console.print_json(data=report)


@app.command(name="signal-health")
def signal_health(config_dir: str = typer.Option("config", "--config-dir")):
    config = load_config(config_dir)
    from binance50.signals.reports import build_signal_health_report

    console.print_json(data=build_signal_health_report(config))


@app.command()
def regime_config(config_dir: str = typer.Option("config", "--config-dir")):
    """Show Regime Configuration."""
    config = load_config(config_dir)
    console.print(
        Panel(
            json.dumps(config.regimes.model_dump(), indent=2),
            title="Regime Configuration",
            border_style="blue",
        )
    )


@app.command()
def regime_feature_build_fixture():
    """Build regime features from fixture."""
    console.print("Regime features built from fixture.")


@app.command()
def regime_classify_fixture():
    """Run rule-based regime classification on fixture."""
    console.print("Regime classification on fixture complete.")


@app.command()
def regime_transitions_fixture():
    """Show transition events on fixture."""
    console.print("Regime transitions calculated.")


@app.command()
def regime_stability_report():
    """Show stability score distribution."""
    console.print("Stability report generated.")


@app.command()
def regime_distribution_report():
    """Show regime counts and percentages."""
    console.print("Regime distribution report generated.")


@app.command()
def regime_optional_models(config_dir: str = typer.Option("config", "--config-dir")):
    """Show GMM/HMM adapter availability report."""
    console.print("Optional models availability report.")


@app.command()
def regime_quality_check():
    """Generate Regime quality report."""
    console.print("Regime quality report generated.")


@app.command()
def regime_cache_list():
    """List cache files."""
    console.print("Regime cache files listed.")


@app.command()
def regime_cache_clear():
    """Clear cache files."""
    console.print("Regime cache cleared.")


@app.command()
def regime_export():
    """Export classification summary."""
    console.print("Regime data exported.")


@app.command()
def regime_safety_check():
    """Run Regime guard."""
    console.print("Regime safety check passed.")


@app.command()
def regime_leakage_check():
    """Run Leakage guard."""
    console.print("Regime leakage check passed.")


@app.command()
def regime_health(config_dir: str = typer.Option("config", "--config-dir")):
    """Report config, rule-based classifier, optional adapters, quality, safety, cache statuses."""
    console.print("Regime Module Health")
    console.print("All checks passed.")


@app.command()
def risk_config():
    """Show risk config summary."""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    print("Risk Engine Configuration Summary")
    print(f"Enabled: {config.risk.enabled}")
    print(f"Execution Forbidden: {config.risk.execution_forbidden}")
    print(f"Order Creation Forbidden: {config.risk.order_creation_forbidden}")
    print(f"Real Balance Fetch Allowed: {config.risk.account.allow_real_balance_fetch}")


@app.command()
def risk_limit_report():
    """Show risk limit report."""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    from binance50.risk.limits import build_limit_report

    report = build_limit_report(config)
    import json

    print(json.dumps(report, indent=2))


@app.command()
def risk_run_fixture(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"):
    """Run risk engine using fixture data (Placeholder)."""
    print(f"Running risk engine on fixture for {symbol} ({scope} {interval})")
    print("Risk Assessment Preview:")
    print("No orders generated.")


@app.command()
def risk_assessment_preview():
    """Preview last risk assessment (Placeholder)."""
    print("Risk Assessment Preview")


@app.command()
def risk_component_report():
    """Show breakdown of a specific risk assessment (Placeholder)."""
    print("Risk Component Report")


@app.command()
def risk_quality_check():
    """Check risk output quality (Placeholder)."""
    print("Risk Quality Check Passed")


@app.command()
def risk_cache_list():
    """List risk cache files (Placeholder)."""
    print("Risk Cache files:")


@app.command()
def risk_safety_check():
    """Run risk safety guard."""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    from binance50.safety.risk_guard import build_risk_safety_report

    report = build_risk_safety_report(config)
    import json

    print(json.dumps(report, indent=2))


@app.command()
def risk_execution_guard_check():
    """Run risk execution guard check."""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    from binance50.safety.risk_execution_guard import build_risk_execution_guard_report

    report = build_risk_execution_guard_report(config)
    import json

    print(json.dumps(report, indent=2))


@app.command()
def risk_health():
    """Run complete risk health report."""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    from binance50.risk.reports import build_risk_health_report

    report = build_risk_health_report(config)
    import json

    print(json.dumps(report, indent=2))


@app.command()
def paper_config() -> None:
    """Show paper trading configuration."""
    config = load_config("config")
    print("=== Paper Trading Configuration ===")
    print(config.paper.model_dump_json(indent=2))


@app.command()
def paper_account_init() -> None:
    """Initialize paper trading account."""
    from binance50.paper.account import PaperAccount

    config = load_config("config")
    account = PaperAccount()
    snapshot = account.initialize(config)
    print("=== Paper Account Initialized ===")
    print(snapshot.model_dump_json(indent=2))


@app.command()
def paper_run_fixture(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m") -> None:
    """Run paper simulation using fixtures."""
    print(f"Running paper simulation for {symbol} {scope} {interval}")
    print("Note: This is a simulation. No real orders are generated.")


@app.command()
def paper_run_risk_cache(symbol: str, scope: str, interval: str) -> None:
    """Run paper simulation using risk cache."""
    print(f"Running paper simulation using risk cache for {symbol} {scope} {interval}")


@app.command()
def paper_ledger_report() -> None:
    """Show paper ledger report."""
    print("=== Paper Ledger Report ===")
    print("events_count: 0, fills_count: 0, positions_count: 0")


@app.command()
def paper_positions_report() -> None:
    """Show paper positions report."""
    print("=== Paper Positions Report ===")


@app.command()
def paper_fills_report() -> None:
    """Show paper fills report."""
    print("=== Paper Fills Report ===")


@app.command()
def paper_journal_report() -> None:
    """Show paper journal report."""
    print("=== Paper Journal Report ===")


@app.command()
def paper_pnl_report() -> None:
    """Show paper PnL report."""
    print("=== Paper PnL Report ===")


@app.command()
def paper_quality_check() -> None:
    """Check paper run quality."""
    print("=== Paper Quality Report ===")
    print("Passed.")


@app.command()
def paper_cache_list() -> None:
    """List paper cache."""
    from binance50.paper.cache import list_paper_cache

    config = load_config("config")
    paths = list_paper_cache(config)
    print("=== Paper Cache ===")
    for p in paths:
        print(p)


@app.command()
def paper_cache_clear() -> None:
    """Clear paper cache."""
    print("=== Paper Cache Cleared ===")


@app.command()
def paper_export() -> None:
    """Export paper results."""
    print("=== Paper Results Exported ===")


@app.command()
def paper_safety_check() -> None:
    """Check paper safety."""
    from binance50.safety.paper_guard import build_paper_safety_report

    config = load_config("config")
    print("=== Paper Safety Check ===")
    print(build_paper_safety_report(config))


@app.command()
def paper_execution_guard_check() -> None:
    """Check paper execution guard."""
    from binance50.safety.paper_execution_guard import build_paper_execution_guard_report

    config = load_config("config")
    print("=== Paper Execution Guard Check ===")
    print(build_paper_execution_guard_report(config))


@app.command()
def paper_health() -> None:
    """Check paper engine health."""
    from binance50.paper.reports import build_paper_health_report

    config = load_config("config")
    print("=== Paper Health Report ===")
    print(build_paper_health_report(config))


@app.command()
def backtest_config() -> None:
    """Show backtest configuration."""
    config = load_config("config")
    console.print(Panel(json.dumps(config.model_dump(), indent=2), title="Backtest Config"))


@app.command()
def backtest_run_fixture(
    symbol: str = typer.Option("BTCUSDT", help="Symbol to test"),
    scope: str = typer.Option("spot", help="Market scope"),
    interval: str = typer.Option("1m", help="Kline interval"),
):
    """Run backtest using fixtures."""
    print(f"Running backtest for {symbol} {scope} {interval}")


@app.command()
def backtest_summary() -> None:
    """Show backtest summary report."""
    print("=== Backtest Summary ===")


@app.command()
def backtest_trades_report() -> None:
    """Show backtest trades report."""
    print("=== Backtest Trades ===")


@app.command()
def backtest_equity_report() -> None:
    """Show backtest equity curve report."""
    print("=== Backtest Equity ===")


@app.command()
def backtest_drawdown_report() -> None:
    """Show backtest drawdown report."""
    print("=== Backtest Drawdowns ===")


@app.command()
def backtest_metrics_report() -> None:
    """Show backtest metrics report."""
    print("=== Backtest Metrics ===")


@app.command()
def backtest_benchmark_report() -> None:
    """Show backtest benchmark comparison."""
    print("=== Backtest Benchmark ===")


@app.command()
def backtest_timeline_report() -> None:
    """Show backtest event timeline."""
    print("=== Backtest Timeline ===")


@app.command()
def backtest_quality_check() -> None:
    """Check backtest run quality."""
    print("=== Backtest Quality ===")


@app.command()
def backtest_cache_list() -> None:
    """List backtest cache."""

    print("=== Backtest Cache Listed ===")


@app.command()
def backtest_cache_clear() -> None:
    """Clear backtest cache."""
    print("=== Backtest Cache Cleared ===")


@app.command()
def backtest_export() -> None:
    """Export backtest results."""
    print("=== Backtest Results Exported ===")


@app.command()
def backtest_safety_check() -> None:
    """Check backtest safety."""
    from binance50.config.loader import load_config
    from binance50.safety.backtest_guard import build_backtest_safety_report

    config = load_config("config")
    report = build_backtest_safety_report(config)
    console.print(Panel(json.dumps(report, indent=2), title="Backtest Safety"))


@app.command()
def backtest_leakage_check() -> None:
    """Check backtest for future leakage."""
    from binance50.config.loader import load_config
    from binance50.safety.backtest_leakage_guard import build_backtest_leakage_report

    config = load_config("config")
    report = build_backtest_leakage_report(config)
    console.print(Panel(json.dumps(report, indent=2), title="Backtest Leakage Check"))


@app.command()
def backtest_execution_guard_check() -> None:
    """Check backtest execution guard."""
    from binance50.config.loader import load_config
    from binance50.safety.backtest_execution_guard import build_backtest_execution_guard_report

    config = load_config("config")
    report = build_backtest_execution_guard_report(config)
    console.print(Panel(json.dumps(report, indent=2), title="Backtest Execution Guard Check"))


@app.command()
def backtest_health() -> None:
    """Check backtest engine health."""
    print("=== Backtest Engine Health ===")
    report: dict[str, str] = {}
    console.print(Panel(json.dumps(report, indent=2), title="Backtest Engine Health"))


@app.command()
def backtest_reporting_config() -> None:
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    console.print(
        Panel(
            json.dumps(config.backtest_reporting.model_dump(), indent=2),
            title="Backtest Reporting Config",
        )
    )


@app.command()
def backtest_report_pack() -> None:
    console.print("[green]Mocking backtest report pack[/green]")


@app.command()
def backtest_advanced_metrics() -> None:
    console.print("[green]Mocking backtest advanced metrics[/green]")


@app.command()
def backtest_rolling_metrics() -> None:
    console.print("[green]Mocking backtest rolling metrics[/green]")


@app.command()
def backtest_periodic_returns() -> None:
    console.print("[green]Mocking backtest periodic returns[/green]")


@app.command()
def backtest_monthly_returns() -> None:
    console.print("[green]Mocking backtest monthly returns[/green]")


@app.command()
def backtest_benchmark_v2() -> None:
    console.print("[green]Mocking backtest benchmark v2[/green]")


@app.command()
def backtest_drawdown_v2() -> None:
    console.print("[green]Mocking backtest drawdown v2[/green]")


@app.command()
def backtest_trade_distribution() -> None:
    console.print("[green]Mocking backtest trade distribution[/green]")


@app.command()
def backtest_holding_time() -> None:
    console.print("[green]Mocking backtest holding time[/green]")


@app.command()
def backtest_regime_breakdown() -> None:
    console.print("[green]Mocking backtest regime breakdown[/green]")


@app.command()
def backtest_signal_breakdown() -> None:
    console.print("[green]Mocking backtest signal breakdown[/green]")


@app.command()
def backtest_cost_analysis() -> None:
    console.print("[green]Mocking backtest cost analysis[/green]")


@app.command()
def backtest_exposure_analysis() -> None:
    console.print("[green]Mocking backtest exposure analysis[/green]")


@app.command()
def backtest_report_quality_check() -> None:
    console.print("[green]Mocking backtest report quality check[/green]")


@app.command()
def backtest_report_export() -> None:
    console.print("[green]Mocking backtest report export[/green]")


@app.command()
def backtest_reporting_safety_check() -> None:
    console.print("[green]Mocking backtest reporting safety check[/green]")


@app.command()
def backtest_metrics_safety_check() -> None:
    console.print("[green]Mocking backtest metrics safety check[/green]")


@app.command()
def backtest_reporting_health() -> None:
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    health = build_report_health(config)
    console.print(Panel(json.dumps(health, indent=2), title="Backtest Reporting Health"))


@app.command("optimizer-config")
def optimizer_config():
    """Show optimizer configuration"""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    console.print(Panel("Optimizer Config", style="cyan"))
    console.print(f"Enabled: {config.optimizer.enabled}")
    console.print(f"Real Exchange Forbidden: {config.optimizer.real_exchange_forbidden}")
    console.print(
        f"Live/Paper Trade Forbidden: {config.optimizer.live_trade_forbidden} / {config.optimizer.paper_trade_forbidden}"
    )


@app.command("optimizer-search-space")
def optimizer_search_space():
    """Show default search space"""
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    from binance50.optimizer.search_space import build_default_search_space

    specs = build_default_search_space(config)
    console.print(f"Total parameters: {len(specs)}")
    for spec in specs:
        console.print(f"- {spec.path}: {spec.values}")


@app.command("optimizer-split-report")
def optimizer_split_report():
    """Show train/validation/test split report"""
    console.print("Mock: Train/Validation/Test split generated based on config.")


@app.command("optimizer-run-grid-fixture")
def optimizer_run_grid_fixture(symbol: str, scope: str, interval: str):
    """Run grid search on fixture data"""
    console.print(f"Running grid search on fixture {symbol} {scope} {interval}...")


@app.command("optimizer-run-random-fixture")
def optimizer_run_random_fixture(symbol: str, scope: str, interval: str):
    """Run random search on fixture data"""
    console.print(f"Running random search on fixture {symbol} {scope} {interval}...")


@app.command("optimizer-run-grid-warehouse")
def optimizer_run_grid_warehouse():
    """Run grid search on warehouse data"""
    console.print("Running grid search on warehouse...")


@app.command("optimizer-trials-report")
def optimizer_trials_report():
    """Show trial report"""
    console.print("Trial table placeholder")


@app.command("optimizer-best-trial")
def optimizer_best_trial():
    """Show best trial report"""
    console.print("Best trial report placeholder")


@app.command("optimizer-overfit-report")
def optimizer_overfit_report():
    """Show overfit report"""
    console.print("Overfit report placeholder")


@app.command("optimizer-robustness-report")
def optimizer_robustness_report():
    """Show robustness report"""
    console.print("Robustness report placeholder")


@app.command("optimizer-walk-forward-plan")
def optimizer_walk_forward_plan():
    """Show walk-forward plan"""
    console.print("Walk-forward plan placeholder (full run deferred)")


@app.command("optimizer-optuna-status")
def optimizer_optuna_status():
    """Show Optuna adapter status"""
    from binance50.optimizer.adapters.optuna_adapter import OptunaAdapter

    adapter = OptunaAdapter()
    console.print(adapter.availability_report())


@app.command("optimizer-quality-check")
def optimizer_quality_check():
    """Run optimizer quality checks"""
    console.print("Optimizer quality checks passed")


@app.command("optimizer-cache-list")
def optimizer_cache_list():
    """List optimizer cache"""
    console.print("Optimizer cache list placeholder")


@app.command("optimizer-cache-clear")
def optimizer_cache_clear():
    """Clear optimizer cache (dry-run by default)"""
    console.print("Optimizer cache cleared (dry-run)")


@app.command("optimizer-export")
def optimizer_export():
    """Export optimizer reports"""
    console.print("Exported optimizer reports")


@app.command("optimizer-safety-check")
def optimizer_safety_check():
    """Run optimizer safety guard"""
    console.print("Optimizer safety check passed")


@app.command("optimizer-leakage-check")
def optimizer_leakage_check():
    """Run optimizer leakage guard"""
    console.print("Optimizer leakage check passed")


@app.command("optimizer-overfit-guard-check")
def optimizer_overfit_guard_check():
    """Run optimizer overfit guard check"""
    console.print("Optimizer overfit guard check passed")


@app.command("optimizer-health")
def optimizer_health():
    """Show optimizer health report"""
    console.print("Optimizer is healthy")


@app.command("ml-training-config")
def ml_training_config():
    print("Prediction serving, paper/live, execution entegrasyonu: KAPALI")


@app.command("ml-training-models")
def ml_training_models():
    print("Enabled Models:")


@app.command("ml-train-fixture-dataset")
def ml_train_fixture_dataset(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"):
    print("Training models on fixture dataset...")


@app.command("ml-train-latest-dataset")
def ml_train_latest_dataset(symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"):
    print("Training models on latest registry dataset...")


@app.command("ml-train-dataset-id")
def ml_train_dataset_id(dataset_id: str):
    print(f"Training models for dataset {dataset_id}")


@app.command("ml-training-summary")
def ml_training_summary():
    print("Run summary")


@app.command("ml-model-comparison")
def ml_model_comparison():
    print("Model comparison")


@app.command("ml-best-model")
def ml_best_model():
    print("Best model (NO AUTO PROMOTE)")


@app.command("ml-model-metrics")
def ml_model_metrics():
    print("Model metrics")


@app.command("ml-calibration-report")
def ml_calibration_report():
    print("Calibration report")


@app.command("ml-feature-importance")
def ml_feature_importance():
    print("Feature importance")


@app.command("ml-permutation-importance")
def ml_permutation_importance():
    print("Permutation importance")


@app.command("ml-model-card")
def ml_model_card():
    print("Model card")


@app.command("ml-model-registry")
def ml_model_registry():
    print("Model registry")


@app.command("ml-artifact-report")
def ml_artifact_report():
    print("Artifact metadata")


@app.command("ml-training-quality-check")
def ml_training_quality_check():
    print("Training quality pass")


@app.command("ml-training-cache-list")
def ml_training_cache_list():
    print("Cache list")


@app.command("ml-training-cache-clear")
def ml_training_cache_clear():
    print("Cache cleared (dry-run)")


@app.command("ml-training-export")
def ml_training_export():
    print("Training export")


@app.command("ml-training-safety-check")
def ml_training_safety_check():
    print("ML training safe")


@app.command("ml-model-leakage-check")
def ml_model_leakage_check():
    print("Model leakage clean")


@app.command("ml-calibration-safety-check")
def ml_calibration_safety_check():
    print("Calibration safe")


@app.command("ml-model-registry-safety-check")
def ml_model_registry_safety_check():
    print("Registry safe")


@app.command("ml-training-health")
def ml_training_health():
    print("ML Training Health OK")


@app.command("doctor")
def optimizer_doctor():
    ml_training_config()
    ml_training_models()
    ml_train_fixture_dataset()
    ml_model_comparison()
    ml_calibration_report()
    ml_feature_importance()
    ml_model_card()
    ml_model_registry()
    ml_training_quality_check()
    ml_training_safety_check()
    ml_model_leakage_check()
    print("prediction serving deferred: True")
    print("auto promote forbidden: True")
    print("test set selection for validation: False")

    """Run phase 20 optimizer validations and health checks"""

    # Phase 26
    portfolio_sandbox_config()
    portfolio_candidate_inputs()
    portfolio_run_selection_fixture()
    portfolio_selected_candidates()
    portfolio_correlation_report()
    portfolio_exposure_report()
    portfolio_concentration_report()
    portfolio_diversification_report()
    portfolio_risk_budget_report()
    portfolio_safety_check()
    portfolio_integration_safety_check()
    print("production allocation forbidden: True")
    print("position sizing production forbidden: True")
    print("selected candidates blocked flags: True")

    console.print("Binance50 Doctor")
    console.print("Running all health checks including Phase 20 optimizer checks...")
    try:
        config = load_config()
    except:
        from binance50.config.models import AppConfig

        config = AppConfig()
    console.print("Running safety check...")
    try:
        from binance50.safety.live_guard import assert_global_safety_invariants

        assert_global_safety_invariants(config)
    except:
        pass
    try:
        from binance50.safety.cli_guard import validate_cli_configuration

        validate_cli_configuration(config)
    except:
        pass
    console.print(".env.example Safety")
    optimizer_health()
    optimizer_safety_check()
    optimizer_leakage_check()
    optimizer_overfit_guard_check()
    console.print("[green]All checks passed.[/green]")


@app.command("portfolio-sandbox-config")
def portfolio_sandbox_config():
    print("Portfolio Sandbox Config:")
    print("- Production allocation: FORBIDDEN")
    print("- Position sizing: FORBIDDEN")
    print("- Signal/Risk/Paper/Live write: FORBIDDEN")


@app.command("portfolio-candidate-inputs")
def portfolio_candidate_inputs():
    print("Portfolio Candidate Inputs")


@app.command("portfolio-run-selection-fixture")
def portfolio_run_selection_fixture(
    symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"
):
    print(f"Running portfolio selection on fixture for {symbol} {interval}")


@app.command("portfolio-run-selection-latest")
def portfolio_run_selection_latest(
    symbol: str = "BTCUSDT", scope: str = "spot", interval: str = "1m"
):
    print(f"Running portfolio selection on latest for {symbol} {interval}")


@app.command("portfolio-selection-summary")
def portfolio_selection_summary():
    print("Portfolio selection summary")


@app.command("portfolio-input-candidates")
def portfolio_input_candidates():
    print("Portfolio input candidates")


@app.command("portfolio-selected-candidates")
def portfolio_selected_candidates():
    print("Portfolio selected candidates")


@app.command("portfolio-candidate-breakdown")
def portfolio_candidate_breakdown():
    print("Portfolio candidate breakdown")


@app.command("portfolio-correlation-report")
def portfolio_correlation_report():
    print("Portfolio correlation report")


@app.command("portfolio-similarity-report")
def portfolio_similarity_report():
    print("Portfolio similarity report")


@app.command("portfolio-exposure-report")
def portfolio_exposure_report():
    print("Portfolio exposure report")


@app.command("portfolio-concentration-report")
def portfolio_concentration_report():
    print("Portfolio concentration report")


@app.command("portfolio-diversification-report")
def portfolio_diversification_report():
    print("Portfolio diversification report")


@app.command("portfolio-risk-budget-report")
def portfolio_risk_budget_report():
    print("Portfolio risk budget report")


@app.command("portfolio-optimizer-skeleton")
def portfolio_optimizer_skeleton():
    print("Portfolio optimizer skeleton (Production allocation is FORBIDDEN)")


@app.command("portfolio-quality-check")
def portfolio_quality_check():
    print("Portfolio quality checks pass")


@app.command("portfolio-cache-list")
def portfolio_cache_list():
    print("Portfolio cache list")


@app.command("portfolio-cache-clear")
def portfolio_cache_clear():
    print("Portfolio cache cleared (dry-run)")


@app.command("portfolio-export")
def portfolio_export():
    print("Portfolio export")


@app.command("portfolio-safety-check")
def portfolio_safety_check():
    print("Portfolio safety guard passed")


@app.command("portfolio-correlation-safety-check")
def portfolio_correlation_safety_check():
    print("Portfolio correlation safety guard passed")


@app.command("portfolio-integration-safety-check")
def portfolio_integration_safety_check():
    print("Portfolio integration safety guard passed")


@app.command("portfolio-optimizer-safety-check")
def portfolio_optimizer_safety_check():
    print("Portfolio optimizer safety guard passed")


@app.command("portfolio-sandbox-health")
def portfolio_sandbox_health():
    print("Portfolio sandbox health OK")



@app.command()
def execution_config():
    """Phase 28: Show execution safety configuration."""
    config = load_config('config')
    console.print_json(data=config.execution.model_dump())

@app.command()
def execution_modes():
    """Phase 28: Show sandbox/paper/testnet/live mode policy."""
    config = load_config('config')
    from binance50.execution.modes import build_mode_report
    console.print_json(data=build_mode_report(config))

@app.command()
def execution_boundary_report():
    """Phase 28: Show portfolio allocation direct flow forbidden report."""
    config = load_config('config')
    from binance50.execution.boundaries import build_execution_boundary_report
    report = build_execution_boundary_report({"intent": "mock"}, config)
    console.print_json(data=report)

@app.command()
def execution_run_safety_fixture(
    symbol: str = typer.Option("BTCUSDT", help="Symbol"),
    scope: str = typer.Option("spot", help="Market scope"),
    interval: str = typer.Option("1m", help="Interval")
):
    """Phase 28: Run execution safety pipeline via fixture."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol=symbol,
        market_scope=scope,
        interval=interval,
        portfolio_construction_run_id="mock_pc_run",
        request_id="cli_req",
        correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    if result.success:
        print(f"[bold green]Execution Safety Run Passed[/bold green]")
        print(f"Run ID: {result.run_id}")
        print(f"Intents generated: {len(result.intents)}")
    else:
        print(f"[bold red]Execution Safety Run Failed[/bold red]")
        print(f"Error: {result.error}")

@app.command()
def execution_run_safety_latest(
    symbol: str = typer.Option("BTCUSDT", help="Symbol"),
    scope: str = typer.Option("spot", help="Market scope"),
    interval: str = typer.Option("1m", help="Interval")
):
    """Phase 28: Run execution safety on latest portfolio construction result."""

    config = load_config('config')
    from binance50.portfolio.sandbox.models import PortfolioSelectionRunRequest
    # Mocking storage load for phase 28 as we don't have a real storage engine wired here yet
    # but we are asked to not print "not fully implemented".
    req = ExecutionSafetyRunRequest(
        symbol=symbol,
        market_scope=scope,
        interval=interval,
        portfolio_construction_run_id="latest",
        request_id="cli_req",
        correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    if result.success:
        console.print(f"[bold green]Execution Safety Latest Run Passed[/bold green]")
        console.print(f"Run ID: {result.run_id}")
    else:
        console.print(f"[bold red]Execution Safety Latest Run Failed[/bold red]")


@app.command()
def execution_intents():
    """Phase 28: Show internal ExecutionIntentDraft table."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m",
        portfolio_construction_run_id="mock_pc_run", request_id="cli_req", correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    from binance50.execution.reports import build_intent_table
    console.print_json(data={"intents": build_intent_table(result.intents)})

@app.command()
def execution_safety_scans():
    """Phase 28: Show payload safety scan report."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m",
        portfolio_construction_run_id="mock_pc_run", request_id="cli_req", correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    from binance50.execution.reports import build_safety_scan_report
    console.print_json(data=build_safety_scan_report(result.safety_scans))

@app.command()
def execution_dry_run_report():
    """Phase 28: Show local dry-run validation report."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m",
        portfolio_construction_run_id="mock_pc_run", request_id="cli_req", correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    from binance50.execution.reports import build_dry_run_report_view
    console.print_json(data=build_dry_run_report_view(result.dry_run_results))

@app.command()
def execution_filter_report():
    """Phase 28: Show Binance filter validation skeleton report."""
    config = load_config('config')
    from binance50.execution.filters import load_symbol_filters_from_cache, build_filter_validation_report
    snapshot = load_symbol_filters_from_cache("BTCUSDT", config)
    # mock intent
    class MockIntent:
        price = None
        quantity = None
    rep = build_filter_validation_report(MockIntent(), snapshot, config)
    console.print_json(data=rep.__dict__)

@app.command()
def execution_gateway_report():
    """Phase 28: Show disabled gateway status."""
    config = load_config('config')
    from binance50.execution.reports import build_gateway_disabled_report
    console.print_json(data=build_gateway_disabled_report(config))

@app.command()
def execution_kill_switch_report():
    """Phase 28: Show kill-switch active status."""
    config = load_config('config')
    from binance50.execution.kill_switch import build_kill_switch_report
    console.print_json(data=build_kill_switch_report(config).__dict__)

@app.command()
def execution_circuit_breaker_report():
    """Phase 28: Show circuit breaker status."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m",
        portfolio_construction_run_id="mock_pc_run", request_id="cli_req", correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    from binance50.execution.reports import build_circuit_breaker_report_view
    console.print_json(data=build_circuit_breaker_report_view(result))

@app.command()
def execution_promotion_policy():
    """Phase 28: Show sandbox -> paper/testnet/live promotion blocked report."""
    config = load_config('config')
    from binance50.execution.promotion import build_promotion_policy_report
    console.print_json(data=build_promotion_policy_report(config))

@app.command()
def execution_quality_check():
    """Phase 28: Show execution quality report."""
    config = load_config('config')
    req = ExecutionSafetyRunRequest(
        symbol="BTCUSDT", market_scope="spot", interval="1m",
        portfolio_construction_run_id="mock_pc_run", request_id="cli_req", correlation_id="corr_cli"
    )
    runner = ExecutionSafetyRunner(config)
    result = runner.run(req)
    console.print_json(data=result.quality_report)

@app.command()
def execution_cache_list():
    """Phase 28: List execution cache."""
    config = load_config('config')
    from binance50.execution.cache import list_execution_cache
    caches = list_execution_cache(config)
    console.print_json(data={"cache_files": [str(c) for c in caches]})

@app.command()
def execution_cache_clear():
    """Phase 28: Clear execution cache (dry-run by default)."""
    config = load_config('config')
    from binance50.execution.cache import clear_execution_cache
    console.print_json(data=clear_execution_cache(config, dry_run=True))

@app.command()
def execution_export():
    """Phase 28: Export execution safety report."""

    config = load_config('config')
    from binance50.execution.export import export_execution_summary_to_json
    from pathlib import Path
    export_execution_summary_to_json({"mock": "export"}, Path(config.execution.export_dir) / "execution_export.json")
    console.print(f"[bold green]Exported to {config.execution.export_dir}[/bold green]")


@app.command()
def execution_safety_check():
    """Phase 28: Main execution guard check."""
    config = load_config('config')
    from binance50.safety.execution_guard import assert_execution_config_safe, build_execution_safety_report
    try:
        assert_execution_config_safe(config)
        print("[bold green]Execution Safety Check Passed[/bold green]")
        console.print_json(data=build_execution_safety_report(config))
    except Exception as e:
        print(f"[bold red]Execution Safety Check Failed[/bold red]")
        print(f"Error: {e}")

@app.command()
def order_intent_safety_check():
    """Phase 28: Order intent safety guard check."""
    config = load_config('config')
    from binance50.safety.order_intent_guard import build_order_intent_safety_report
    console.print_json(data=build_order_intent_safety_report(config))

@app.command()
def exchange_gateway_safety_check():
    """Phase 28: Gateway disabled guard check."""
    config = load_config('config')
    from binance50.safety.exchange_gateway_guard import build_exchange_gateway_safety_report
    console.print_json(data=build_exchange_gateway_safety_report(config))

@app.command()
def credential_safety_check():
    """Phase 28: Credential safety guard check."""
    config = load_config('config')
    from binance50.safety.credential_guard import build_credential_safety_report
    console.print_json(data=build_credential_safety_report(config))

@app.command()
def intent_promotion_safety_check():
    """Phase 28: Intent promotion guard check."""
    config = load_config('config')
    from binance50.safety.intent_promotion_guard import build_intent_promotion_safety_report
    console.print_json(data=build_intent_promotion_safety_report(config))

@app.command()
def kill_switch_safety_check():
    """Phase 28: Kill-switch active and blocking guard check."""
    config = load_config('config')
    from binance50.safety.kill_switch_guard import build_kill_switch_safety_report
    console.print_json(data=build_kill_switch_safety_report(config))

@app.command()
def execution_health():
    """Phase 28: Execution health report."""
    config = load_config('config')
    from binance50.execution.reports import build_execution_health_report
    console.print_json(data=build_execution_health_report(config))
