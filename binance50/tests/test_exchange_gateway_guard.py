import pytest
from binance50.app import load_config as get_config
from binance50.core.exceptions import ExecutionGatewayDisabledError
from binance50.safety.exchange_gateway_guard import assert_all_gateways_disabled

def test_all_gateways_disabled():
    config = get_config()
    assert_all_gateways_disabled(config)

    config.execution.gateway.paper_gateway_enabled = True
    with pytest.raises(ExecutionGatewayDisabledError):
        assert_all_gateways_disabled(config)
