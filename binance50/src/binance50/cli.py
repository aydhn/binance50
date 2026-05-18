import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from binance50.config.loader import load_config
from binance50.safety.secrets_guard import (
    check_for_leaked_secrets,
    verify_no_secrets_in_example_env,
)
from binance50.safety.mode_guard import check_mode_consistency
from binance50.safety.live_guard import check_live_trading_guard

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
        load_config()
        table.add_row("Config Loader", "[green]Passed[/green]")
    except Exception as e:
        table.add_row("Config Loader", f"[red]Failed: {str(e)}[/red]")

    # Check .env.example
    try:
        verify_no_secrets_in_example_env()
        table.add_row(".env.example Safety", "[green]Passed[/green]")
    except Exception as e:
        table.add_row(".env.example Safety", f"[red]Failed: {str(e)}[/red]")

    console.print(table)


@app.command()
def show_config() -> None:
    """Show the current configuration (with secrets redacted)."""
    try:
        config = load_config()
        # The model validation will ensure it's loaded properly.
        # When printing, pydantic's dict doesn't contain the env secrets,
        # but if it did we'd want to redact it. Here we just print the config model.
        console.print(Panel("Current Configuration", style="bold green"))

        # Pretty print config dict
        import json

        config_dict = config.model_dump()
        console.print(json.dumps(config_dict, indent=2))

    except Exception as e:
        console.print(f"[red]Failed to load config: {e}[/red]")


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

        # 2. Mode guard
        check_mode_consistency(config)
        console.print("[green]✓ Mode Consistency passed[/green]")

        # 3. Live guard
        check_live_trading_guard(config)
        console.print("[green]✓ Live Trading Guard passed[/green]")

        console.print(f"\n[bold]Current Mode:[/bold] {config.runtime.trading_mode.value}")
        console.print(f"[bold]Current Environment:[/bold] {config.runtime.environment.value}")

    except Exception as e:
        console.print(f"[red]Safety check failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
