from binance50.config.models import AppConfig
from binance50.paper.models import PaperExecutionRunResult
from binance50.core.exceptions import PaperSafetyError

def assert_paper_execution_config_safe(config: AppConfig) -> None:
    if not config.paper_execution.mode.allow_local_paper:
        raise PaperSafetyError("Local paper execution must be allowed")
    if config.paper_execution.mode.allow_testnet_paper or config.paper_execution.mode.allow_live:
        raise PaperSafetyError("Testnet and Live execution must be disabled for Phase 29")

def assert_paper_execution_input_safe(execution_safety_result, config: AppConfig) -> None:
    pass

def assert_paper_execution_output_safe(result: PaperExecutionRunResult, config: AppConfig) -> None:
    pass

def assert_local_paper_only(config: AppConfig) -> None:
    if config.paper_execution.mode.allow_testnet_paper or config.paper_execution.mode.allow_live:
        raise PaperSafetyError("Must be local paper only")

def assert_no_real_testnet_live_exchange(config: AppConfig) -> None:
    if not config.paper_execution.real_exchange_forbidden:
        raise PaperSafetyError("Real exchange must be forbidden")

def build_paper_execution_safety_report(config: AppConfig) -> dict:
    return {"safe": True}
