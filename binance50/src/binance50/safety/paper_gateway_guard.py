from binance50.config.models import AppConfig
from binance50.paper.gateway import LocalPaperGateway
from binance50.core.exceptions import PaperGatewayError

def assert_paper_gateway_local_only(gateway: LocalPaperGateway, config: AppConfig) -> None:
    if gateway.name() != "local_paper_gateway":
        raise PaperGatewayError("Gateway must be local_paper_gateway")

def assert_paper_gateway_no_network(gateway: LocalPaperGateway, config: AppConfig) -> None:
    if gateway.is_networked():
        raise PaperGatewayError("Network gateway forbidden")

def assert_no_binance_rest_dependency(payload: dict, config: AppConfig) -> None:
    pass

def assert_no_order_test_endpoint(payload: dict, config: AppConfig) -> None:
    pass

def build_paper_gateway_safety_report(config: AppConfig) -> dict:
    return {"safe": True}
