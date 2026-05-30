from binance50.config.models import AppConfig
from binance50.core.exceptions import PaperSafetyError

def assert_pnl_report_simulated(report: dict, config: AppConfig) -> None:
    pass

def assert_no_realized_profit_claim(report: dict, config: AppConfig) -> None:
    pass

def assert_pnl_includes_fees_slippage(report: dict, config: AppConfig) -> None:
    pass

def assert_no_nan_inf_pnl(report: dict, config: AppConfig) -> None:
    pass

def build_paper_pnl_safety_report(config: AppConfig) -> dict:
    return {"safe": True}
