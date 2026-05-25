import pandas as pd

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult


def stitch_oos_equity(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> pd.DataFrame:
    wf_config = config.walkforward

    # Sort windows by start time to stitch sequentially
    sorted_results = sorted(
        window_results.values(), key=lambda r: r.window_id
    )  # Simplify sorting by ID

    equities = []
    for res in sorted_results:
        if res.oos_backtest_result and hasattr(res.oos_backtest_result, "equity_curve"):
            eq = res.oos_backtest_result.equity_curve
            # Add metadata columns if needed
            eq["window_id"] = res.window_id
            equities.append(eq)

    if not equities:
        return pd.DataFrame()

    if wf_config.oos.reset_capital_each_window and not wf_config.oos.compound_oos_equity:
        stitched_df = reset_capital_stitch(equities, config)
    elif wf_config.oos.compound_oos_equity:
        stitched_df = compound_oos_equity(equities, config)
    else:
        # Default simple concat
        stitched_df = pd.concat(equities)

    validate_stitched_equity(stitched_df, config)
    return stitched_df


def normalize_window_equity(
    equity_curve: pd.DataFrame, starting_cash: float, config: AppConfig
) -> pd.DataFrame:
    df = equity_curve.copy()
    if len(df) == 0:
        return df

    initial_val = df["equity"].iloc[0]
    if initial_val > 0:
        df["equity"] = (df["equity"] / initial_val) * starting_cash
    return df


def compound_oos_equity(windows_equity: list[pd.DataFrame], config: AppConfig) -> pd.DataFrame:
    # A continuous equity curve where the end of one window is the start of the next
    if not windows_equity:
        return pd.DataFrame()

    result_df = windows_equity[0].copy()
    current_cash = result_df["equity"].iloc[-1]

    for eq_df in windows_equity[1:]:
        normalized_df = normalize_window_equity(eq_df, current_cash, config)
        result_df = pd.concat([result_df, normalized_df])
        current_cash = result_df["equity"].iloc[-1]

    return result_df


def reset_capital_stitch(windows_equity: list[pd.DataFrame], config: AppConfig) -> pd.DataFrame:
    # Each window starts from starting_cash_usdt, absolute PnLs are summed
    if not windows_equity:
        return pd.DataFrame()

    starting_cash = config.walkforward.oos.starting_cash_usdt
    result_df = pd.DataFrame()
    cumulative_pnl = 0.0

    for eq_df in windows_equity:
        df = eq_df.copy()
        if len(df) == 0:
            continue

        initial_val = df["equity"].iloc[0]
        # Calculate PnL for each step relative to start of window
        df["pnl"] = df["equity"] - initial_val

        # Add to absolute starting cash + cumulative previous PnL
        df["stitched_equity"] = starting_cash + cumulative_pnl + df["pnl"]
        cumulative_pnl += df["pnl"].iloc[-1]

        result_df = pd.concat([result_df, df])

    return result_df


def validate_stitched_equity(equity_df: pd.DataFrame, config: AppConfig) -> None:
    # Check for NaNs
    if equity_df.isnull().any().any():
        raise ValueError("Stitched equity contains NaN values")


def build_stitched_equity_report(equity_df: pd.DataFrame) -> dict:
    if equity_df.empty:
        return {}

    equity_col = "stitched_equity" if "stitched_equity" in equity_df.columns else "equity"

    return {
        "start_equity": equity_df[equity_col].iloc[0],
        "end_equity": equity_df[equity_col].iloc[-1],
        "total_return_pct": (equity_df[equity_col].iloc[-1] / equity_df[equity_col].iloc[0] - 1)
        * 100,
        "data_points": len(equity_df),
    }
