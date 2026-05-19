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
        "config/environments.yaml",
        "config/logging.yaml",
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

    # Check Phase 3 additions
    try:
        sys.path.insert(0, str(Path("src").resolve()))
        from binance50.audit.writer import audit_event
        from binance50.config.loader import load_config
        from binance50.core.error_classifier import classify_http_status
        from binance50.logging.redaction import redact_text
        from binance50.logging.setup import setup_logging
        from binance50.safety.environment_guard import build_environment_safety_report

        config = load_config()
        print_result("Config loading", True)

        # Check default profile
        profile = config.selected_environment_profile
        has_default_profile = profile is not None
        print_result("Default profile resolves", has_default_profile)
        if not has_default_profile:
            all_passed = False

        # Check live blocked
        is_live_blocked = not profile.is_live and config.runtime.trading_mode.value != "live"
        print_result("Live trading blocked by default", is_live_blocked)
        if not is_live_blocked:
            all_passed = False

        # Check safety report works
        report = build_environment_safety_report(config)
        has_report = report is not None and "safety_status" in report
        print_result("Safety report generates", has_report)
        if not has_report:
            all_passed = False

        # Check Logging Setup
        setup_logging()
        print_result("Logging setup", True)

        # Check Audit Writer
        audit_event("app_start", "health_check", "test")
        print_result("Audit writer", True)

        # Check Redaction
        redacted = redact_text("api_key=FAKE_SECRET_KEY")
        print_result("Secret redaction", "***REDACTED***" in redacted)
        if "***REDACTED***" not in redacted:
            all_passed = False

        # Check Error Classifier
        err_cls = classify_http_status(429)
        print_result("Error classifier (429)", err_cls.__name__ == "BinanceRateLimitError")
        if err_cls.__name__ != "BinanceRateLimitError":
            all_passed = False

    except Exception as e:
        print_result("Config/Logging/Audit validation", False, f"- Error: {e}")
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
