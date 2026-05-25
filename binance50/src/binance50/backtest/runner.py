from .models import BacktestRunRequest, BacktestRunResult, BacktestRunStatus


class BacktestRunner:
    def __init__(
        self,
        config,
        data_loader=None,
        indicator_engine_v1=None,
        indicator_engine_v2=None,
        strategy_engine=None,
        signal_engine=None,
        regime_classifier=None,
        risk_engine=None,
        simulated_broker=None,
        portfolio=None,
        event_bus=None,
        storage=None,
    ):
        self.config = config
        self.data_loader = data_loader
        self.indicator_engine_v1 = indicator_engine_v1
        self.indicator_engine_v2 = indicator_engine_v2
        self.strategy_engine = strategy_engine
        self.signal_engine = signal_engine
        self.regime_classifier = regime_classifier
        self.risk_engine = risk_engine
        self.simulated_broker = simulated_broker
        self.portfolio = portfolio
        self.event_bus = event_bus
        self.storage = storage

    def run(self, request: BacktestRunRequest) -> BacktestRunResult:
        # Stub
        return BacktestRunResult(
            request=request,
            run_id="stub",
            status=BacktestRunStatus.completed,
            events=[],
            fills=[],
            positions=[],
            trades=[],
            equity_curve=[],
            success=True,
        )

    def run_from_fixture(
        self, fixture_name: str, symbol: str, market_scope: str, interval: str
    ) -> BacktestRunResult:
        request = BacktestRunRequest(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            input_ohlcv_dataset_name="fixture",
            strategy_profile="default",
            request_id="stub_request",
            correlation_id="stub_correlation",
        )
        return self.run(request)

    def run_from_warehouse(
        self,
        symbol: str,
        market_scope: str,
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> BacktestRunResult:
        request = BacktestRunRequest(
            symbol=symbol,
            market_scope=market_scope,
            interval=interval,
            input_ohlcv_dataset_name="warehouse",
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            strategy_profile="default",
            request_id="stub_request",
            correlation_id="stub_correlation",
        )
        return self.run(request)

    def process_bar(self, index, current_bar, next_bar, context):
        pass

    def compute_pipeline_until_risk(self, historical_slice, current_bar):
        pass

    def handle_risk_assessments(self, risk_assessments, current_bar, next_bar):
        pass

    def handle_exits(self, current_bar, next_bar):
        pass

    def update_equity(self, current_bar):
        pass

    def finalize_run(self, last_bar):
        pass

    def build_metadata(self, result):
        pass

    def save_to_cache(self, result):
        pass

    def save_to_warehouse(self, result):
        pass
