import hashlib
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionIdempotencyError

from .models import ExecutionIntentDraft


def build_correlation_id(source_run_id: str, source_candidate_id: str, config: AppConfig) -> str:
    # Ensure correlation ID is deterministic for tracing
    return f"corr_{source_run_id}_{source_candidate_id}"


def build_idempotency_key(
    source_run_id: str,
    source_candidate_id: str,
    symbol: str,
    side: str,
    mode: str,
    open_time: str,
    config: AppConfig
) -> str:
    comp = [source_run_id, source_candidate_id, symbol, side, mode, str(open_time)]
    raw = "|".join(comp)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"idk_{h[:16]}"


def validate_idempotency_key(key: str, config: AppConfig) -> None:
    if config.execution.idempotency.idempotency_key_required and not key:
        raise ExecutionIdempotencyError("Idempotency key is required but missing.")
    if not key.startswith("idk_"):
        raise ExecutionIdempotencyError(f"Idempotency key format invalid: {key}")


def validate_correlation_id(correlation_id: str, config: AppConfig) -> None:
    if config.execution.idempotency.correlation_id_required and not correlation_id:
        raise ExecutionIdempotencyError("Correlation ID is required but missing.")
    if not correlation_id.startswith("corr_"):
        raise ExecutionIdempotencyError(f"Correlation ID format invalid: {correlation_id}")


def build_idempotency_report(intents: list[ExecutionIntentDraft]) -> dict[str, Any]:
    keys = [i.idempotency_key for i in intents]
    unique_keys = set(keys)
    duplicates = len(keys) - len(unique_keys)
    return {
        "total_intents": len(keys),
        "unique_idempotency_keys": len(unique_keys),
        "duplicates": duplicates
    }
