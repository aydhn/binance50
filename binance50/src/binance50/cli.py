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
from binance50.core.exception_handler import handle_exception
from binance50.core.exceptions import ConfigError
from binance50.logging.setup import setup_logging
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
from binance50.security.live_unlock import build_live_unlock_report

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
        config = load_config()
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
def show_config() -> None:
    """Show the current configuration (with secrets redacted)."""
    try:
        config = load_config()
        console.print(Panel("Current Configuration", style="bold green"))
        config_dict = config.model_dump(mode="json")
        console.print(json.dumps(config_dict, indent=2))
    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")


@app.command()
def list_environments() -> None:
    """List all available environment profiles."""
    try:
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()

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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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
        config = load_config()
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


if __name__ == "__main__":
    app()
