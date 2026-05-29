from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioReturnsError


def build_price_matrix(market_data_by_symbol: dict[str, pd.DataFrame], config: AppConfig) -> pd.DataFrame:
    if not market_data_by_symbol:
        return pd.DataFrame()
    prices = {}
    return_source = config.portfolio_construction.market_data.return_source
    for symbol, df in market_data_by_symbol.items():
        if df.empty or return_source not in df.columns:
            if config.portfolio_construction.market_data.allow_missing_symbol_returns: continue
            elif config.portfolio_construction.market_data.missing_returns_policy == "reject": raise PortfolioReturnsError(f"Missing '{return_source}' column in market data for {symbol}")
        if 'timestamp' in df.columns: s = df.set_index('timestamp')[return_source]
        elif 'open_time' in df.columns: s = df.set_index('open_time')[return_source]
        else: s = df[return_source]
        prices[symbol] = s
    if not prices: return pd.DataFrame()
    price_df = pd.DataFrame(prices).ffill().dropna()
    return price_df

def compute_returns_matrix(price_matrix: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if price_matrix.empty: return pd.DataFrame()
    if config.portfolio_construction.market_data.reject_future_columns:
        for col in price_matrix.columns:
            if "future" in str(col).lower() or "forward" in str(col).lower(): raise PortfolioReturnsError(f"Future-looking column '{col}' rejected.")
    returns_df = price_matrix.pct_change().dropna()
    return returns_df

def validate_returns_matrix(returns_df: pd.DataFrame, config: AppConfig) -> None:
    if returns_df.empty: raise PortfolioReturnsError("Returns matrix is empty.")
    if config.portfolio_construction.quality.reject_forward_returns and not returns_df.index.is_monotonic_increasing:
        raise PortfolioReturnsError("Returns index is not monotonic increasing, potential forward returns.")

def align_returns_to_candidates(returns_df: pd.DataFrame, candidates: list[Any], config: AppConfig) -> pd.DataFrame:
    if returns_df.empty: return returns_df
    candidate_symbols = [c.get("symbol") if isinstance(c, dict) else getattr(c, "symbol", None) for c in candidates]
    candidate_symbols = [s for s in candidate_symbols if s]
    available_symbols = [s for s in candidate_symbols if s in returns_df.columns]
    if not available_symbols and candidate_symbols: raise PortfolioReturnsError("None of the candidate symbols exist in the returns matrix.")
    return returns_df[available_symbols]

def build_returns_report(returns_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "symbols": list(returns_df.columns),
        "periods": len(returns_df),
        "start_time": str(returns_df.index[0]) if not returns_df.empty else None,
        "end_time": str(returns_df.index[-1]) if not returns_df.empty else None,
        "contains_nans": bool(returns_df.isna().any().any()),
    }
