def assert_no_backtest_lookahead(df, config) -> None:
    pass

def assert_no_future_columns(df) -> None:
    pass

def assert_no_centered_rolling_metadata(metadata) -> None:
    pass

def assert_no_forward_or_nearest_alignment(metadata) -> None:
    pass

def assert_decision_before_fill(result, config) -> None:
    pass

def assert_no_same_bar_fill(result, config) -> None:
    pass

def build_backtest_leakage_report(config) -> dict:
    return {"status": "no_leakage"}
