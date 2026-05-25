from typing import Any

import pandas as pd

from binance50.walkforward.models import WalkForwardWindow, WalkForwardWindowResult


def walkforward_windows_to_dataframe(windows: list[WalkForwardWindow]) -> pd.DataFrame:
    return pd.DataFrame([w.model_dump() for w in windows])


def walkforward_window_results_to_dataframe(results: list[WalkForwardWindowResult]) -> pd.DataFrame:
    # Handle serialization appropriately for dataframe structures
    data = []
    for r in results:
        dump = r.model_dump(exclude={"oos_backtest_result", "optimizer_result"})
        data.append(dump)
    return pd.DataFrame(data)


def walkforward_oos_equity_to_dataframe(result: Any) -> pd.DataFrame:
    return getattr(result, "stitched_oos_equity", pd.DataFrame())


def walkforward_parameter_drift_to_dataframe(result: Any) -> pd.DataFrame:
    return pd.DataFrame()


def walkforward_degradation_to_dataframe(result: Any) -> pd.DataFrame:
    return pd.DataFrame()


def walkforward_quality_to_dataframe(report: Any) -> pd.DataFrame:
    return pd.DataFrame()
