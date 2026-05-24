def assert_no_real_order_object(payload) -> None:
    pass

def assert_no_exchange_order_identifiers(payload) -> None:
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k in ("order_id", "client_order_id", "exchange_order_id", "orderId", "clientOrderId"):
                from binance50.core.exceptions import BacktestOrderIdentifierDetectedError
                raise BacktestOrderIdentifierDetectedError(f"Found forbidden key: {k}")
            if isinstance(v, (dict, list)):
                assert_no_exchange_order_identifiers(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_exchange_order_identifiers(item)

def assert_no_signed_request_payload(payload) -> None:
    pass

def assert_no_api_credentials(payload) -> None:
    pass

def assert_no_order_gateway_reference(payload) -> None:
    pass

def build_backtest_execution_guard_report(config) -> dict:
    return {"status": "execution_guarded"}
