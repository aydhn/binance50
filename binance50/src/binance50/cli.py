import logging
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binance50.audit.writer import audit_event
from binance50.config.loader import load_config
from binance50.core.exception_handler import handle_exception
from binance50.core.exceptions import BinanceRateLimitError, ConfigError
from binance50.logging.setup import setup_logging
from binance50.safety.environment_guard import (
    build_environment_safety_report,
    validate_environment_matrix,
)
from binance50.safety.secrets_guard import (
    check_for_leaked_secrets,
    verify_no_secrets_in_example_env,
)

app = typer.Typer(help="binance50 CLI tool")
console = Console()


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
        verify_no_secrets_in_example_env()
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

    # Check Audit Writer
    try:
        audit_event("app_start", "cli", "doctor", message="Doctor check")
        table.add_row("Audit Writer", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Audit Writer", f"[red]Failed: {str(e)}[/red]")

    # Check Exception Handler & Redaction
    try:
        handle_exception(ConfigError("Fake key=12345 secret=XYZ"), component="cli", action="doctor")
        table.add_row("Exception Handler", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Exception Handler", f"[red]Failed: {str(e)}[/red]")

    console.print(table)


@app.command()
def show_config() -> None:
    """Show the current configuration (with secrets redacted)."""
    try:
        config = load_config()
        console.print(Panel("Current Configuration", style="bold green"))

        import json

        config_dict = config.model_dump()
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
        # Avoid passing raw string through model
        for p_name, p_config in config.environment_matrix.profiles.items():
            if p_name.value == profile:
                p = p_config
                break
        else:
            console.print(f"[red]Profile '{profile}' not found in environment matrix.[/red]")
            sys.exit(1)

    console.print(Panel(f"Environment Profile: {p.profile_name.value}", style="bold cyan"))

    import json

    p_dict = p.model_dump()
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
    import json

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

        # 1. Secrets guard
        warnings = check_for_leaked_secrets()
        if warnings:
            for w in warnings:
                console.print(f"[yellow]{w}[/yellow]")
        else:
            console.print("[green]✓ Secrets Guard passed[/green]")

        # 2. Environment Matrix Guard (includes mode and live guards)
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
def log_test() -> None:
    """Test logging output and redaction capabilities."""
    setup_logging()
    logger = logging.getLogger("binance50.cli")

    console.print("[yellow]Running Log Test...[/yellow]")
    logger.info("This is a normal info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    # Fake secret test
    logger.info(
        "Testing redaction: api_key=FAKE_TEST_SECRET_SHOULD_BE_REDACTED_1234567890 and secret=ANOTHER_FAKE_SECRET_THAT_IS_LONG_ENOUGH"
    )
    logger.info(
        "Testing JSON redaction: {'telegram_bot_token': '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'}"
    )

    console.print("[green]Log test complete. Check your console and logs/binance50.log.[/green]")


@app.command()
def audit_test() -> None:
    """Test audit log writing."""
    setup_logging()
    console.print("[yellow]Running Audit Test...[/yellow]")

    audit_event(
        "app_start",
        "cli",
        "audit_test",
        message="This is a test audit event",
        metadata={"test_api_key": "FAKE_SECRET_THAT_SHOULD_BE_REDACTED"},
    )

    console.print("[green]Audit test complete. Check logs/binance50_audit.jsonl.[/green]")


@app.command()
def error_test() -> None:
    """Test error handling and classification."""
    setup_logging()
    logger = logging.getLogger("binance50.cli")
    console.print("[yellow]Running Error Test...[/yellow]")

    try:
        raise BinanceRateLimitError(
            "Too many requests from this IP", metadata={"endpoint": "/api/v3/order"}
        )
    except Exception as e:
        handle_exception(e, component="cli", action="error_test", logger=logger)

    try:
        raise ConfigError("Invalid configuration for api_secret=FAKE_SECRET_SHOULD_BE_REDACTED")
    except Exception as e:
        handle_exception(e, component="cli", action="error_test", logger=logger)

    console.print(
        "[green]Error test complete. Exceptions were caught and handled safely. Check console and error logs.[/green]"
    )


if __name__ == "__main__":
    app()
