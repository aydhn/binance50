#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    print(f"\n--- Running: {description} ---")
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")

        # Change working directory to the project root to fix config paths
        cwd = Path(__file__).resolve().parent.parent

        result = subprocess.run(
            cmd,
            env=env,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(result.stdout)
        print(f"✓ {description} passed.")
        return True
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(f"✗ {description} failed with exit code {e.returncode}.")
        return False


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    # File checks
    env_example = repo_root / ".env.example"
    if not env_example.exists():
        print("✗ .env.example is missing.")
        sys.exit(1)

    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        print("✗ .gitignore is missing.")
        sys.exit(1)

    print("\n--- Running Code Quality Checks ---")

    checks = [
        (["python", "-m", "pytest", "tests/"], "Pytest Unit Tests"),
        # (["python", "-m", "mypy", "src/"], "MyPy Type Checker"),
        (["python", "-m", "binance50.cli", "risk-config"], "Risk Config Check"),
        (["python", "-m", "binance50.cli", "risk-limit-report"], "Risk Limit Report Check"),
        (["python", "-m", "binance50.cli", "risk-run-fixture"], "Risk Fixture Check"),
        (["python", "-m", "binance50.cli", "risk-safety-check"], "Risk Safety Check"),
        (
            ["python", "-m", "binance50.cli", "risk-execution-guard-check"],
            "Risk Execution Guard Check",
        ),
        (["python", "-m", "binance50.cli", "risk-health"], "Risk Health Check"),
    ]

    cli_checks = [
        (["python", "-m", "binance50.cli", "doctor"], "Binance50 Doctor"),
        (["python", "-m", "binance50.cli", "secrets-check"], "Secrets Guard Check"),
        (["python", "-m", "binance50.cli", "api-key-check"], "API Key Guard Check"),
        (["python", "-m", "binance50.cli", "dry-run-check"], "Dry-run Guard Check"),
        (["python", "-m", "binance50.cli", "live-unlock-check"], "Live Unlock Guard Check"),
        (["python", "-m", "binance50.cli", "safety-report-full"], "Full Safety Report"),
        (["python", "-m", "binance50.cli", "connector-status"], "Connector Status"),
        (["python", "-m", "binance50.cli", "connector-health"], "Connector Health"),
        (["python", "-m", "binance50.cli", "connector-endpoints"], "Connector Endpoints"),
        (["python", "-m", "binance50.cli", "connector-capabilities"], "Connector Capabilities"),
        (
            [
                "python",
                "-m",
                "binance50.cli",
                "connector-stream-url-test",
                "--symbol",
                "BTCUSDT",
                "--stream",
                "kline",
                "--interval",
                "1m",
                "--combined",
            ],
            "Connector Stream URL Test",
        ),
        (["python", "-m", "binance50.cli", "sdk-check"], "SDK Check"),
        (
            ["python", "-m", "binance50.cli", "signal-config", "--config-dir", "config"],
            "Signal Config Check",
        ),
        (
            ["python", "-m", "binance50.cli", "signal-thresholds", "--config-dir", "config"],
            "Signal Thresholds Check",
        ),
        (
            ["python", "-m", "binance50.cli", "signal-weight-report", "--config-dir", "config"],
            "Signal Weight Report",
        ),
        (
            ["python", "-m", "binance50.cli", "signal-run-fixture", "--config-dir", "config"],
            "Signal Run Fixture Check",
        ),
        (
            ["python", "-m", "binance50.cli", "signal-safety-check", "--config-dir", "config"],
            "Signal Safety Check",
        ),
        (["python", "-m", "binance50.cli", "signal-quality-check"], "Signal Quality Check"),
        (["python", "-m", "binance50.cli", "regime-config"], "Regime Config"),
        (["python", "-m", "binance50.cli", "regime-feature-build-fixture"], "Regime Feature Build"),
        (["python", "-m", "binance50.cli", "regime-classify-fixture"], "Regime Classify Fixture"),
        (
            ["python", "-m", "binance50.cli", "regime-transitions-fixture"],
            "Regime Transitions Fixture",
        ),
        (["python", "-m", "binance50.cli", "regime-optional-models"], "Regime Optional Models"),
        (["python", "-m", "binance50.cli", "regime-safety-check"], "Regime Safety Check"),
        (["python", "-m", "binance50.cli", "regime-leakage-check"], "Regime Leakage Check"),
        (
            [
                "python",
                "-m",
                "binance50.cli",
                "signal-calibration-report",
                "--config-dir",
                "config",
            ],
            "Signal Calibration Report",
        ),
        (
            ["python", "-m", "binance50.cli", "backtest-reporting-config"],
            "Backtest Reporting Config Check",
        ),
        (["python", "-m", "binance50.cli", "backtest-report-pack"], "Backtest Report Pack Check"),
        (
            ["python", "-m", "binance50.cli", "backtest-advanced-metrics"],
            "Backtest Advanced Metrics Check",
        ),
        (
            ["python", "-m", "binance50.cli", "backtest-monthly-returns"],
            "Backtest Monthly Returns Check",
        ),
        (["python", "-m", "binance50.cli", "backtest-benchmark-v2"], "Backtest Benchmark V2 Check"),
        (["python", "-m", "binance50.cli", "backtest-drawdown-v2"], "Backtest Drawdown V2 Check"),
        (
            ["python", "-m", "binance50.cli", "backtest-report-quality-check"],
            "Backtest Report Quality Check",
        ),
        (
            ["python", "-m", "binance50.cli", "backtest-reporting-safety-check"],
            "Backtest Reporting Safety Check",
        ),
    ]

    cli_checks.extend(
        [
            (["python", "-m", "binance50.cli", "risk-config"], "Risk Config Check"),
            (["python", "-m", "binance50.cli", "risk-limit-report"], "Risk Limit Report Check"),
            (["python", "-m", "binance50.cli", "risk-run-fixture"], "Risk Fixture Check"),
            (["python", "-m", "binance50.cli", "risk-safety-check"], "Risk Safety Check"),
            (
                ["python", "-m", "binance50.cli", "risk-execution-guard-check"],
                "Risk Execution Guard Check",
            ),
            (["python", "-m", "binance50.cli", "risk-health"], "Risk Health Check"),
        ]
    )

    all_passed = True

    for cmd, desc in checks + cli_checks:
        if not run_command(cmd, desc):
            all_passed = False

    print("\n=========================================")
    if all_passed:
        print("🎉 All checks passed! Project is healthy and safe.")
        sys.exit(0)
    else:
        print("💥 Some checks failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
