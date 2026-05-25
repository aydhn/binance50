from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AdvancedMetricsReport(BaseModel):
    model_config = ConfigDict(extra="allow")
    run_id: str
    total_return_pct: float | None = None
    cagr_pct: float | None = None
    annualized_volatility_pct: float | None = None
    sharpe_ratio: float | None = None
    sortino_ratio: float | None = None
    calmar_ratio: float | None = None
    omega_ratio: float | None = None
    tail_ratio: float | None = None
    var_pct: float | None = None
    cvar_pct: float | None = None
    skew: float | None = None
    kurtosis: float | None = None
    profit_factor: float | None = None
    expectancy_usdt: float | None = None
    payoff_ratio: float | None = None
    recovery_factor: float | None = None
    ulcer_index: float | None = None
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


class RollingMetricsReport(BaseModel):
    model_config = ConfigDict(extra="allow")
    run_id: str
    window: int
    metric_name: str
    points: list[dict[str, Any]] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


class PeriodicReturnReport(BaseModel):
    model_config = ConfigDict(extra="allow")
    run_id: str
    frequency: str
    returns_table: list[dict[str, Any]] = []
    best_period: dict[str, Any] | None = None
    worst_period: dict[str, Any] | None = None
    positive_period_ratio: float | None = None
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


class BenchmarkComparisonReport(BaseModel):
    model_config = ConfigDict(extra="allow")
    run_id: str
    benchmark_label: str
    strategy_total_return_pct: float | None = None
    benchmark_total_return_pct: float | None = None
    excess_return_pct: float | None = None
    tracking_error_pct: float | None = None
    information_ratio: float | None = None
    alpha_placeholder: float | None = None
    beta_placeholder: float | None = None
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


class BacktestReportPack(BaseModel):
    model_config = ConfigDict(extra="allow")
    report_id: str
    run_id: str
    summary: dict[str, Any] = {}
    advanced_metrics: AdvancedMetricsReport | None = None
    rolling_metrics: list[RollingMetricsReport] = []
    periodic_returns: list[PeriodicReturnReport] = []
    benchmark: BenchmarkComparisonReport | None = None
    drawdowns: dict[str, Any] = {}
    trade_distribution: dict[str, Any] = {}
    breakdowns: dict[str, Any] = {}
    cost_analysis: dict[str, Any] = {}
    quality: Any = None
    disclaimer: str = ""
    input_hash: str = ""
    config_hash: str = ""
    report_hash: str = ""
    generated_at_utc: datetime | str = ""
    warnings: list[str] = []
