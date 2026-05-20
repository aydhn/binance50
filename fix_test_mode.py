from pathlib import Path

content = Path("binance50/tests/test_mode_guard.py").read_text()
content = content.replace(
'''def test_readonly_profile_with_order_gateway(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_readonly")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "true")

    config = load_config()

    with pytest.raises(SafetyError) as exc_info:
        validate_mode_consistency(config)
    assert "is readonly but order_gateway is enabled" in str(exc_info.value)''',
'''def test_readonly_profile_with_order_gateway(monkeypatch):
    monkeypatch.setenv("BINANCE50_ENVIRONMENT_PROFILE", "spot_mainnet_readonly")
    monkeypatch.setenv("BINANCE50_ORDER_GATEWAY_ENABLED", "true")
    monkeypatch.setenv("BINANCE50_CONNECTION_ENABLED", "true")
    # For Phase 4 we need to disable the overall order blocks to even load the config
    monkeypatch.setenv("BINANCE50_DISABLE_ALL_ORDERS", "false")

    config = load_config()

    with pytest.raises(SafetyError) as exc_info:
        validate_mode_consistency(config)
    assert "is readonly but order_gateway is enabled" in str(exc_info.value)'''
)
Path("binance50/tests/test_mode_guard.py").write_text(content)
