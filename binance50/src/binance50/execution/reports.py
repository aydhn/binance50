from typing import Any

from binance50.config.models import AppConfig
from .models import ExecutionSafetyRunResult


def build_execution_safety_summary(result: ExecutionSafetyRunResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "success": result.success,
        "error": result.error,
        "intent_count": len(result.intents),
        "safety_scans_passed": sum(1 for s in result.safety_scans if s.passed),
        "dry_runs_passed": sum(1 for d in result.dry_run_results if d.passed),
        "kill_switch_active": result.kill_switch_report.get("active", False),
        "circuit_breaker_triggered": result.circuit_breaker_report.get("breaker_triggered", False)
    }

def build_intent_table(intents: list, limit: int = 100) -> list[dict[str, Any]]:
    table = []
    for i in intents[:limit]:
        table.append({
            "intent_id": i.intent_id,
            "mode": i.mode.value,
            "status": i.status.value,
            "symbol": i.symbol,
            "side": i.side.value,
            "correlation_id": i.correlation_id
        })
    return table

def build_safety_scan_report(scans: list) -> dict[str, Any]:
    return {
        "total_scans": len(scans),
        "passed": sum(1 for s in scans if s.passed),
        "blocked": sum(1 for s in scans if s.blocked)
    }

def build_dry_run_report_view(dry_runs: list) -> dict[str, Any]:
    return {
        "total_dry_runs": len(dry_runs),
        "passed": sum(1 for d in dry_runs if d.passed)
    }

def build_boundary_report_view(result: ExecutionSafetyRunResult) -> dict[str, Any]:
    return result.boundary_report

def build_kill_switch_report_view(result: ExecutionSafetyRunResult) -> dict[str, Any]:
    return result.kill_switch_report

def build_circuit_breaker_report_view(result: ExecutionSafetyRunResult) -> dict[str, Any]:
    return result.circuit_breaker_report

def build_gateway_disabled_report(config: AppConfig) -> dict[str, Any]:
    return {
        "interface_enabled": config.execution.gateway.interface_enabled,
        "all_implementations_disabled": config.execution.gateway.all_implementations_disabled,
        "paper_gateway_enabled": config.execution.gateway.paper_gateway_enabled,
        "testnet_gateway_enabled": config.execution.gateway.testnet_gateway_enabled,
        "live_gateway_enabled": config.execution.gateway.live_gateway_enabled
    }

def build_execution_health_report(config: AppConfig) -> dict[str, Any]:
    return {
        "execution_module_enabled": config.execution.enabled,
        "default_mode": config.execution.global_.default_mode,
        "gateway_calls_allowed": config.execution.global_.allow_gateway_calls,
        "order_submission_allowed": config.execution.global_.allow_order_submission,
        "kill_switch_default_on": config.execution.kill_switch.global_kill_switch_default_on
    }
