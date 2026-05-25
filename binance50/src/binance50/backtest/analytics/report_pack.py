import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from binance50.backtest.analytics.advanced_metrics import compute_advanced_metrics
from binance50.backtest.analytics.benchmark_v2 import compute_benchmark_v2
from binance50.backtest.analytics.cost_analysis import analyze_costs
from binance50.backtest.analytics.drawdown_v2 import build_drawdown_v2_report
from binance50.backtest.analytics.periodic_returns import compute_periodic_returns
from binance50.backtest.analytics.regime_breakdown import analyze_performance_by_regime
from binance50.backtest.analytics.report_models import BacktestReportPack
from binance50.backtest.analytics.rolling_metrics import compute_rolling_metrics
from binance50.backtest.analytics.signal_breakdown import (
    analyze_performance_by_direction,
    analyze_performance_by_risk_score,
    analyze_performance_by_signal_score,
    analyze_performance_by_strategy_plugin,
)
from binance50.backtest.analytics.trade_distribution import analyze_trade_distribution
from binance50.config.models import AppConfig


class BacktestReportPackBuilder:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def build(self, result: Any) -> BacktestReportPack:
        pack = BacktestReportPack(
            report_id=f"rep_{result.run_id}",
            run_id=result.run_id,
            generated_at_utc=datetime.now(UTC),
        )

        cfg = self.config.backtest_reporting.report_pack

        if cfg.include_summary:
            pack.summary = self.build_summary_section(result)

        if cfg.include_metrics:
            pack.advanced_metrics = self.build_metrics_section(result)

        if cfg.include_rolling_metrics:
            pack.rolling_metrics = self.build_rolling_section(result)

        if cfg.include_periodic_returns:
            pack.periodic_returns = self.build_periodic_returns_section(result)

        if cfg.include_benchmark:
            pack.benchmark = self.build_benchmark_section(result)

        if cfg.include_drawdowns:
            pack.drawdowns = self.build_drawdown_section(result)

        if cfg.include_trade_distribution:
            pack.trade_distribution = self.build_trade_distribution_section(result)

        if cfg.include_breakdowns:
            pack.breakdowns = self.build_breakdowns_section(result)

        if cfg.include_cost_analysis:
            pack.cost_analysis = self.build_cost_section(result)

        if cfg.include_disclaimer:
            pack.disclaimer = self.build_disclaimer_section()

        if self.config.backtest_reporting.require_input_hash:
            pack.input_hash = getattr(result, "input_hash", "missing")

        if self.config.backtest_reporting.require_config_hash:
            pack.config_hash = getattr(result, "config_hash", "missing")

        pack.report_hash = self.compute_report_hash(pack)

        if cfg.include_quality:
            from binance50.backtest.quality_v2 import build_backtest_report_quality

            pack.quality = build_backtest_report_quality(pack, self.config)

        return pack

    def build_summary_section(self, result: Any) -> dict[str, Any]:
        return {
            "strategy": getattr(result, "strategy_name", "unknown"),
            "symbols": getattr(result, "symbols", []),
            "start_time": getattr(result, "start_time", None),
            "end_time": getattr(result, "end_time", None),
            "initial_capital": getattr(result, "initial_capital", 0.0),
        }

    def build_metrics_section(self, result: Any) -> Any:
        return compute_advanced_metrics(result, self.config)

    def build_rolling_section(self, result: Any) -> list[Any]:
        return compute_rolling_metrics(result, self.config)

    def build_periodic_returns_section(self, result: Any) -> list[Any]:
        return compute_periodic_returns(result, self.config)

    def build_benchmark_section(self, result: Any) -> Any:
        return compute_benchmark_v2(result, self.config)

    def build_drawdown_section(self, result: Any) -> dict[str, Any]:
        return build_drawdown_v2_report(result, self.config)

    def build_trade_distribution_section(self, result: Any) -> dict[str, Any]:
        trades = getattr(result, "trades", [])
        return analyze_trade_distribution(trades, self.config)

    def build_breakdowns_section(self, result: Any) -> dict[str, Any]:
        trades = getattr(result, "trades", [])
        equity = getattr(result, "equity_curve", None)
        regimes = getattr(result, "regimes", None)

        return {
            "by_regime": (
                analyze_performance_by_regime(trades, equity, regimes, self.config)
                if regimes is not None
                else {}
            ),
            "by_signal_score": analyze_performance_by_signal_score(trades, self.config),
            "by_risk_score": analyze_performance_by_risk_score(trades, self.config),
            "by_strategy_plugin": analyze_performance_by_strategy_plugin(trades, self.config),
            "by_direction": analyze_performance_by_direction(trades, self.config),
        }

    def build_cost_section(self, result: Any) -> dict[str, Any]:
        return analyze_costs(result, self.config)

    def build_quality_section(self, result: Any) -> Any:
        return None

    def build_disclaimer_section(self) -> str:
        return (
            "DISCLAIMER: This backtest report is a simulation and does not represent "
            "real execution or "
            "guaranteed future performance. "
            "It is not financial advice. Past performance is not indicative of future results. "
            "Fee and slippage models are assumed. Low trade counts may indicate overfitting."
        )

    def compute_report_hash(self, pack: BacktestReportPack) -> str:
        data = {
            "run_id": pack.run_id,
            "input_hash": pack.input_hash,
            "config_hash": pack.config_hash,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
