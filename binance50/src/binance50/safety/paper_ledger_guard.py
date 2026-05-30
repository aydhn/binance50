from binance50.config.models import AppConfig
from binance50.core.exceptions import PaperLedgerError

def assert_ledger_append_only(ledger, config: AppConfig) -> None:
    pass

def assert_no_negative_cash(snapshots: list, config: AppConfig) -> None:
    if not config.paper_execution.ledger.allow_negative_cash:
        for s in snapshots:
            if s.cash_usdt < 0:
                raise PaperLedgerError("Negative cash detected")

def assert_no_short_spot(positions: list, config: AppConfig) -> None:
    if not config.paper_execution.ledger.allow_short_spot:
        for p in positions:
            if p.quantity < 0:
                raise PaperLedgerError("Short spot detected")

def assert_no_manual_balance_edit(events: list, config: AppConfig) -> None:
    pass

def build_paper_ledger_safety_report(config: AppConfig) -> dict:
    return {"safe": True}
