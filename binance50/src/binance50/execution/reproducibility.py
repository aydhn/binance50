import hashlib
from typing import Any

from binance50.config.models import AppConfig
from .models import ExecutionDryRunResult, ExecutionIntentDraft, ExecutionSafetyRunResult, ExecutionSafetyScan


def _sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def compute_execution_input_hash(source_result: Any, config: AppConfig) -> str:
    return _sha256_hash(str(source_result))


def compute_intent_hash(intent: ExecutionIntentDraft) -> str:
    # Hash deterministic parts
    raw = f"{intent.intent_id}|{intent.mode}|{intent.symbol}|{intent.side}|{intent.correlation_id}"
    return _sha256_hash(raw)


def compute_safety_scan_hash(scan: ExecutionSafetyScan) -> str:
    raw = f"{scan.safety_scan_id}|{scan.intent_id}|{scan.passed}|{scan.blocked}"
    return _sha256_hash(raw)


def compute_dry_run_hash(dry_run: ExecutionDryRunResult) -> str:
    raw = f"{dry_run.dry_run_id}|{dry_run.intent_id}|{dry_run.passed}"
    return _sha256_hash(raw)


def compute_execution_config_hash(config: AppConfig) -> str:
    # A simple hash of the execution config
    return _sha256_hash(str(config.execution.model_dump()))


def compute_execution_output_hash(result: ExecutionSafetyRunResult) -> str:
    raw = f"{result.run_id}|{result.success}|{len(result.intents)}|{result.error}"
    return _sha256_hash(raw)


def build_execution_reproducibility_report(result: ExecutionSafetyRunResult, config: AppConfig) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "config_hash": compute_execution_config_hash(config),
        "output_hash": compute_execution_output_hash(result),
        "intents_hashes": [compute_intent_hash(i) for i in result.intents],
        "scans_hashes": [compute_safety_scan_hash(s) for s in result.safety_scans],
        "dry_runs_hashes": [compute_dry_run_hash(d) for d in result.dry_run_results]
    }
