import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioCorrelationError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioCorrelationReport(BaseModel):
    run_id: str
    method: str
    lookback_bars: int
    min_periods: int
    symbols: list[str]
    correlation_matrix: dict | None = None
    high_correlation_pairs: list[dict] = Field(default_factory=list)
    blocked_correlation_pairs: list[dict] = Field(default_factory=list)
    missing_correlation_symbols: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def build_returns_matrix(
    ohlcv_by_symbol: dict[str, pd.DataFrame], config: AppConfig
) -> pd.DataFrame:
    c_config = config.portfolio_sandbox.correlation
    if not c_config.use_returns:
        raise PortfolioCorrelationError(
            "Using non-returns for correlation is currently not fully supported."
        )

    returns_dict = {}
    for symbol, df in ohlcv_by_symbol.items():
        if df is None or df.empty:
            continue
        col = c_config.return_column
        if col not in df.columns:
            continue

        # Validate future columns
        if c_config.reject_future_columns:
            if any(c in df.columns for c in ["target", "future", "label"]):
                raise PortfolioCorrelationError(f"Future columns detected in {symbol} data")

        # Take the last lookback_bars
        subset = df.tail(c_config.lookback_bars).copy()
        subset["return"] = subset[col].pct_change()
        returns_dict[symbol] = subset["return"]

    if not returns_dict:
        return pd.DataFrame()

    return pd.DataFrame(returns_dict)


def compute_correlation_matrix(returns_df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if returns_df.empty:
        return pd.DataFrame()

    c_config = config.portfolio_sandbox.correlation

    # Compute correlation
    corr_matrix = returns_df.corr(method=c_config.method, min_periods=c_config.min_periods)

    # Validation
    if c_config.reject_forward_returns:
        # A simple check: if the index implies future dates... (mock logic here)
        pass

    return corr_matrix


def compute_candidate_pair_correlations(
    candidates: list[PortfolioCandidateInput], corr_matrix: pd.DataFrame
) -> dict:
    pairs = {}
    symbols = list(set([c.symbol for c in candidates]))
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            s1, s2 = symbols[i], symbols[j]
            if s1 in corr_matrix.columns and s2 in corr_matrix.columns:
                pairs[f"{s1}-{s2}"] = float(corr_matrix.loc[s1, s2])
    return pairs


def detect_high_correlation_pairs(
    candidates: list[PortfolioCandidateInput], corr_matrix: pd.DataFrame, config: AppConfig
) -> list[dict]:
    high_corr = []
    c_config = config.portfolio_sandbox.correlation
    pairs = compute_candidate_pair_correlations(candidates, corr_matrix)

    for pair, corr in pairs.items():
        if pd.isna(corr):
            continue
        if abs(corr) >= c_config.max_abs_pair_correlation_warning:
            s1, s2 = pair.split("-")
            high_corr.append(
                {
                    "symbol_1": s1,
                    "symbol_2": s2,
                    "correlation": corr,
                    "blocked": abs(corr) >= c_config.max_abs_pair_correlation_block,
                }
            )
    return high_corr


def validate_correlation_inputs(market_data: dict, config: AppConfig) -> None:
    # Dummy validation logic
    if not market_data and config.portfolio_sandbox.correlation.enabled:
        pass  # Handle based on policy


def build_correlation_report(
    candidates: list[PortfolioCandidateInput], market_data: dict, config: AppConfig
) -> PortfolioCorrelationReport:
    c_config = config.portfolio_sandbox.correlation
    report = PortfolioCorrelationReport(
        run_id="unknown",
        method=c_config.method,
        lookback_bars=c_config.lookback_bars,
        min_periods=c_config.min_periods,
        symbols=list(set([c.symbol for c in candidates])),
    )

    if not c_config.enabled:
        return report

    validate_correlation_inputs(market_data, config)
    returns_df = build_returns_matrix(market_data, config)
    corr_matrix = compute_correlation_matrix(returns_df, config)

    # Store matrix compactly
    if not corr_matrix.empty:
        # report.correlation_matrix = corr_matrix.to_dict() # Deferred to JSON export usually

        high_corr_pairs = detect_high_correlation_pairs(candidates, corr_matrix, config)
        report.high_correlation_pairs = [p for p in high_corr_pairs if not p["blocked"]]
        report.blocked_correlation_pairs = [p for p in high_corr_pairs if p["blocked"]]

        # Check missing
        for sym in report.symbols:
            if sym not in corr_matrix.columns or corr_matrix[sym].isna().all():
                report.missing_correlation_symbols.append(sym)

    return report
