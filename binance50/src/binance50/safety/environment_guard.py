from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import SafetyError
from binance50.safety.api_key_guard import build_api_key_safety_report
from binance50.safety.dry_run_guard import build_dry_run_report
from binance50.safety.live_guard import build_live_guard_report
from binance50.safety.mode_guard import build_mode_guard_report
from binance50.security.live_unlock import build_live_unlock_report


def validate_environment_matrix(config: AppConfig) -> None:
    """
    High level validation that delegates to specialized guards.
    Throws SafetyError if any hard constraint fails.
    """
    # 1. Check mode consistency
    mode_report = build_mode_guard_report(config)
    if mode_report["status"] == "unsafe":
        raise SafetyError(f"Mode validation failed: {mode_report['issues'][0]}")

    # 2. Check API key consistency
    api_key_report = build_api_key_safety_report(config)
    if api_key_report["status"] == "unsafe":
        raise SafetyError(f"API key validation failed: {api_key_report['issues'][0]}")

    # 3. Check dry run and order path
    dry_run_report = build_dry_run_report(config)
    if dry_run_report["status"] == "unsafe":
        raise SafetyError(f"Dry run validation failed: {dry_run_report['issues'][0]}")

    # 4. Check live trading constraints
    # We only throw error for live trading blocks if we are actually TRYING to trade live
    if config.runtime.trading_mode == "live":
        live_report = build_live_guard_report(config)
        if live_report["live_trading_blocked"]:
            raise SafetyError(f"Live trading blocked: {live_report['blocking_reasons'][0]}")


def build_environment_safety_report(config: AppConfig) -> dict[str, Any]:
    """
    Build a comprehensive safety report combining all guards.
    """
    mode_report = build_mode_guard_report(config)
    live_report = build_live_guard_report(config)
    api_key_report = build_api_key_safety_report(config)
    dry_run_report = build_dry_run_report(config)
    unlock_report = build_live_unlock_report(config)

    # Collect blocking reasons specifically for live trading
    blocking_reasons = []
    blocking_reasons.extend(live_report["blocking_reasons"])

    # Collect generic warnings and issues
    warnings = []
    warnings.extend(mode_report["issues"])
    warnings.extend(api_key_report["issues"])
    warnings.extend(dry_run_report["issues"])

    status = "unsafe" if warnings else "safe"

    creds = config.credentials.binance

    report = {
        "safety_status": status,
        "selected_profile": config.selected_environment_profile.profile_name.value,
        "runtime_mode": config.runtime.trading_mode.value,
        "dry_run": config.safety.dry_run,
        "force_paper_mode": config.safety.force_paper_mode,
        "disable_all_orders": config.safety.disable_all_orders,
        "allow_testnet_orders": config.safety.allow_testnet_orders,
        "allow_demo_orders": config.safety.allow_demo_orders,
        "allow_live_orders": config.safety.allow_live_orders,
        "effective_trading_mode": dry_run_report["effective_trading_mode"],
        "credentials_present": api_key_report["credentials_present"],
        "credential_pair_complete": api_key_report["credential_pair_complete"],
        "api_permissions": api_key_report["permissions"],
        "ip_restricted": creds.ip_restricted,
        "order_path_status": "enabled" if config.connector.order_gateway_enabled else "disabled",
        "real_order_impossible": dry_run_report["real_orders_impossible"],
        "live_trading_blocked": live_report["live_trading_blocked"],
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "unlock_status": unlock_report,
    }

    return report
