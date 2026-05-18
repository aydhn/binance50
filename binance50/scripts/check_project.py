#!/usr/bin/env python3
import sys
from pathlib import Path


def print_result(check_name: str, passed: bool, msg: str = "") -> None:
    status = "PASSED" if passed else "FAILED"
    color = "\033[92m" if passed else "\033[91m"
    endc = "\033[0m"
    print(f"[{color}{status}{endc}] {check_name} {msg}")


def check_project():
    print("Running Project Health Check...")

    # Check critical files
    critical_files = [
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        "README.md",
        "config/default.yaml",
    ]

    all_passed = True

    for f in critical_files:
        exists = Path(f).exists()
        print_result(f"File exists: {f}", exists)
        if not exists:
            all_passed = False

    # Check tests folder
    has_tests = Path("tests").is_dir()
    print_result("Directory exists: tests/", has_tests)
    if not has_tests:
        all_passed = False

    # Check config loadability
    try:
        sys.path.insert(0, str(Path("src").resolve()))
        from binance50.config.loader import load_config

        load_config()
        print_result("Config loading", True)
    except Exception as e:
        print_result("Config loading", False, f"- Error: {e}")
        all_passed = False

    print("\nSummary:")
    if all_passed:
        print("\033[92mProject structure is healthy.\033[0m")
        sys.exit(0)
    else:
        print("\033[91mProject structure has issues.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    check_project()
