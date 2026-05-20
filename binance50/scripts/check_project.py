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
        (["python", "-m", "ruff", "check", "."], "Ruff Linter"),
        (["python", "-m", "black", "--check", "."], "Black Formatter"),
        (["python", "-m", "mypy", "src"], "MyPy Type Checker"),
    ]

    cli_checks = [
        (["python", "-m", "binance50.cli", "doctor"], "Binance50 Doctor"),
        (["python", "-m", "binance50.cli", "secrets-check"], "Secrets Guard Check"),
        (["python", "-m", "binance50.cli", "api-key-check"], "API Key Guard Check"),
        (["python", "-m", "binance50.cli", "dry-run-check"], "Dry-run Guard Check"),
        (["python", "-m", "binance50.cli", "live-unlock-check"], "Live Unlock Guard Check"),
        (["python", "-m", "binance50.cli", "safety-report-full"], "Full Safety Report"),
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
