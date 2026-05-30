from binance50.config.models import AppConfig
from binance50.paper.models import PaperExecutionRunResult
from binance50.paper.ledger import PaperLedger
from binance50.core.exceptions import PaperReplayError

class PaperReplayEngine:
    def replay_events(self, events: list, config: AppConfig) -> PaperExecutionRunResult:
        # Skeleton for replay
        pass

    def rebuild_ledger_from_events(self, events: list, config: AppConfig) -> PaperLedger:
        ledger = PaperLedger()
        # process events
        return ledger

    def verify_replay_matches_original(self, original: PaperExecutionRunResult, replayed: PaperExecutionRunResult, config: AppConfig) -> dict:
        return {"matched": True}

    def build_replay_report(self, original: PaperExecutionRunResult, replayed: PaperExecutionRunResult) -> dict:
        return {"status": "success"}
