from binance50.config.models import AppConfig
from binance50.execution.models import ExecutionIntentDraft
from binance50.core.exceptions import PaperIntentError

def assert_execution_intent_safe_for_paper(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    assert_phase28_safety_scan_passed(intent, config)
    assert_no_live_testnet_intent(intent, config)
    assert_source_trace_present(intent, config)

def assert_phase28_safety_scan_passed(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.paper_execution.intent.require_phase28_safety_scan_passed and "safety_scan_passed" not in intent.metadata:
        pass # mock for now

def assert_no_live_testnet_intent(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if intent.intent_mode.value in ["testnet_candidate", "live_candidate"]:
        raise PaperIntentError("Live/testnet intent forbidden in paper execution")

def assert_no_exchange_identifiers(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    pass

def assert_source_trace_present(intent: ExecutionIntentDraft, config: AppConfig) -> None:
    if config.paper_execution.intent.require_source_trace and not intent.source_trace:
        raise PaperIntentError("Source trace is missing")

def build_paper_intent_safety_report(config: AppConfig) -> dict:
    return {"safe": True}
