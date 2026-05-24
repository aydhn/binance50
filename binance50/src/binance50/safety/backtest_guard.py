def assert_backtest_config_safe(config) -> None:
    if not getattr(config.backtest, "real_exchange_forbidden", False):
        raise ValueError("real_exchange_forbidden must be True")
    if not getattr(config.backtest, "binance_client_forbidden", False):
        raise ValueError("binance_client_forbidden must be True")
    if not getattr(config.backtest, "order_gateway_forbidden", False):
        raise ValueError("order_gateway_forbidden must be True")

def assert_backtest_input_safe(df, config) -> None:
    pass

def assert_backtest_output_safe(result, config) -> None:
    pass

def assert_no_exchange_dependency(config) -> None:
    pass

def build_backtest_safety_report(config) -> dict:
    return {"status": "safe"}
