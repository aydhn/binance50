from dataclasses import dataclass
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionCircuitBreakerError

from .models import ExecutionIntentDraft, ExecutionSafetyScan


@dataclass
class ExecutionCircuitBreakerReport:
    max_intents_per_run: int
    max_intents_per_symbol: int
    intent_count: int
    intents_by_symbol: dict[str, int]
    safety_error_count: int
    breaker_triggered: bool
    reasons: list[str]
    metadata: dict[str, Any]


def check_max_intents_per_run(intents: list[ExecutionIntentDraft], config: AppConfig) -> None:
    max_count = config.execution.circuit_breaker.max_intents_per_run
    if len(intents) > max_count:
        raise ExecutionCircuitBreakerError(f"Max intents per run exceeded: {len(intents)} > {max_count}")


def check_max_intents_per_symbol(intents: list[ExecutionIntentDraft], config: AppConfig) -> None:
    counts: dict[str, int] = {}
    for intent in intents:
        counts[intent.symbol] = counts.get(intent.symbol, 0) + 1

    max_count = config.execution.circuit_breaker.max_intents_per_symbol
    for sym, count in counts.items():
        if count > max_count:
            raise ExecutionCircuitBreakerError(f"Max intents per symbol exceeded for {sym}: {count} > {max_count}")


def check_safety_error_threshold(scans: list[ExecutionSafetyScan], config: AppConfig) -> None:
    error_count = sum(1 for s in scans if not s.passed)
    max_err = config.execution.circuit_breaker.max_rejected_intents_warning
    if error_count > max_err and config.execution.circuit_breaker.block_on_safety_error:
        raise ExecutionCircuitBreakerError(f"Too many safety errors: {error_count} > {max_err}")


def build_circuit_breaker_report(intents: list[ExecutionIntentDraft], scans: list[ExecutionSafetyScan], config: AppConfig) -> ExecutionCircuitBreakerReport:
    counts: dict[str, int] = {}
    for intent in intents:
        counts[intent.symbol] = counts.get(intent.symbol, 0) + 1

    err_count = sum(1 for s in scans if not s.passed)

    reasons = []
    max_run = config.execution.circuit_breaker.max_intents_per_run
    if len(intents) > max_run:
        reasons.append(f"intents > {max_run}")

    max_sym = config.execution.circuit_breaker.max_intents_per_symbol
    for s, c in counts.items():
        if c > max_sym:
            reasons.append(f"symbol {s} > {max_sym}")

    max_err = config.execution.circuit_breaker.max_rejected_intents_warning
    if err_count > max_err and config.execution.circuit_breaker.block_on_safety_error:
        reasons.append(f"safety errors > {max_err}")

    return ExecutionCircuitBreakerReport(
        max_intents_per_run=max_run,
        max_intents_per_symbol=max_sym,
        intent_count=len(intents),
        intents_by_symbol=counts,
        safety_error_count=err_count,
        breaker_triggered=len(reasons) > 0,
        reasons=reasons,
        metadata={}
    )


def assert_circuit_breaker_not_triggered(report: ExecutionCircuitBreakerReport, config: AppConfig) -> None:
    if report.breaker_triggered:
        raise ExecutionCircuitBreakerError(f"Circuit breaker triggered: {report.reasons}")
