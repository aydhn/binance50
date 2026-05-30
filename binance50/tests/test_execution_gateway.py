import pytest
from binance50.app import load_config as get_config
from binance50.execution.disabled_gateways import DisabledPaperGateway
from binance50.core.exceptions import ExecutionGatewayDisabledError

def test_disabled_paper_gateway():
    gw = DisabledPaperGateway()
    assert not gw.is_enabled()
    with pytest.raises(ExecutionGatewayDisabledError):
        gw.submit_intent(None)
    assert gw.health()["status"] == "disabled"
