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
        result = subprocess.run(
            cmd,
            env=env,
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
        # (["python", "-m", "mypy", "src"], "MyPy Type Checker"),
    ]

    cli_checks = [
        (["python", "-m", "binance50.cli", "indicator-config"], "Indicator Config"),
        (["python", "-m", "binance50.cli", "indicator-backends"], "Indicator Backends"),
        (["python", "-m", "binance50.cli", "indicator-list"], "Indicator List"),
        (["python", "-m", "binance50.cli", "indicator-quality-check"], "Indicator Quality Check"),
        (["python", "-m", "binance50.cli", "indicator-safety-check"], "Indicator Safety Check"),
        (["python", "-m", "binance50.cli", "indicator-health"], "Indicator Health"),
        (["python", "-m", "binance50.cli", "universe-config"], "Universe Config Check"),
        (
            ["python", "-m", "binance50.cli", "universe-fixture-select", "--scope", "spot"],
            "Universe Fixture Select Spot",
        ),
        (
            ["python", "-m", "binance50.cli", "universe-fixture-select", "--scope", "usdm_futures"],
            "Universe Fixture Select USDM",
        ),
        (
            ["python", "-m", "binance50.cli", "universe-explain", "BTCUSDT"],
            "Universe Explain Check",
        ),
        (["python", "-m", "binance50.cli", "universe-safety-check"], "Universe Safety Check"),
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
        (["python", "-m", "binance50.cli", "stream-config"], "Stream Config Check"),
        (
            [
                "python",
                "-m",
                "binance50.cli",
                "stream-plan",
                "--symbols",
                "BTCUSDT,ETHUSDT",
                "--scope",
                "spot",
                "--types",
                "kline,bookTicker",
                "--interval",
                "1m",
            ],
            "Stream Plan Check",
        ),
        (
            [
                "python",
                "-m",
                "binance50.cli",
                "stream-url-test",
                "--symbols",
                "BTCUSDT",
                "--scope",
                "spot",
                "--types",
                "kline",
                "--interval",
                "1m",
            ],
            "Stream URL Test Check",
        ),
        (
            [
                "python",
                "-m",
                "binance50.cli",
                "stream-fixture-parse",
                "--fixture",
                "spot_kline_btcusdt_1m_closed.json",
                "--scope",
                "spot",
            ],
            "Stream Fixture Parse Check",
        ),
        (["python", "-m", "binance50.cli", "stream-simulate"], "Stream Simulate Check"),
        (["python", "-m", "binance50.cli", "stream-buffer-test"], "Stream Buffer Test Check"),
        (
            ["python", "-m", "binance50.cli", "stream-replay-fixtures"],
            "Stream Replay Fixtures Check",
        ),
        (["python", "-m", "binance50.cli", "stream-state-report"], "Stream State Report Check"),
        (["python", "-m", "binance50.cli", "stream-safety-check"], "Stream Safety Check"),
        (["python", "-m", "binance50.cli", "stream-health"], "Stream Health Check"),
        (["python", "-m", "binance50.cli", "strategy-config"], "Strategy Config Check"),
        (["python", "-m", "binance50.cli", "strategy-list"], "Strategy List Check"),
        (
            ["python", "-m", "binance50.cli", "strategy-plugin-health"],
            "Strategy Plugin Health Check",
        ),
        (["python", "-m", "binance50.cli", "strategy-run-fixture"], "Strategy Run Fixture Check"),
        (
            ["python", "-m", "binance50.cli", "strategy-candidates-preview"],
            "Strategy Candidate Preview Check",
        ),
        (["python", "-m", "binance50.cli", "strategy-quality-check"], "Strategy Quality Check"),
        (["python", "-m", "binance50.cli", "strategy-cache-list"], "Strategy Cache List Check"),
        (["python", "-m", "binance50.cli", "strategy-safety-check"], "Strategy Safety Check"),
        (["python", "-m", "binance50.cli", "strategy-health"], "Strategy Health Check"),
    ]

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
