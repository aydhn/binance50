import pytest
from binance50.execution.disabled_gateways import (
    DisabledLiveGateway,
    DisabledTestnetGateway,
    DisabledTestOrderGateway
)
from binance50.core.exceptions import ExecutionGatewayDisabledError

def test_disabled_gateways():
    for gw_class in [DisabledLiveGateway, DisabledTestnetGateway, DisabledTestOrderGateway]:
        gw = gw_class()
        assert not gw.is_enabled()
        with pytest.raises(ExecutionGatewayDisabledError):
            gw.submit_intent(None)
