import pytest
from decimal import Decimal
from binance50.config.models import AppConfig
from binance50.paper.models import PaperOrder, PaperOrderSide, PaperOrderType, PaperOrderStatus
from binance50.paper.intents import PaperIntentBridge
from binance50.paper.gateway import LocalPaperGateway
from binance50.paper.fill_simulator import PaperFillSimulator
from binance50.paper.lifecycle import transition_paper_order
from binance50.core.exceptions import PaperIntentError, PaperLifecycleError, PaperFillSimulationError

@pytest.fixture
def base_config():
    return AppConfig()

def test_paper_intent_bridge_rejects_live(base_config):
    bridge = PaperIntentBridge()
    class MockIntent:
        intent_mode = type("Mode", (), {"value": "live_candidate"})()
        source_trace = "trace"

    with pytest.raises(PaperIntentError, match="Live/testnet intent rejected"):
        bridge.validate_execution_intent_for_paper(MockIntent(), base_config)

def test_paper_lifecycle_transitions(base_config):
    order = PaperOrder(
        paper_order_id="paper_123",
        source_intent_id="intent_123",
        source_run_id="run_123",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        side=PaperOrderSide.buy,
        order_type=PaperOrderType.market,
        requested_notional_usdt=Decimal("10.0"),
        requested_quantity=Decimal("0.001"),
        created_open_time="2024-01-01T00:00:00Z",
        correlation_id="corr_123",
        idempotency_key="idem_123",
        source_trace="trace",
        explanation="expl"
    )

    order = transition_paper_order(order, PaperOrderStatus.paper_submitted_local, base_config)
    assert order.status == PaperOrderStatus.paper_submitted_local

    with pytest.raises(PaperLifecycleError):
        transition_paper_order(order, PaperOrderStatus.paper_draft, base_config)

def test_local_paper_gateway_no_network(base_config):
    gateway = LocalPaperGateway()
    assert not gateway.is_networked()
    assert gateway.name() == "local_paper_gateway"

def test_fill_simulator_market_order(base_config):
    simulator = PaperFillSimulator()
    order = PaperOrder(
        paper_order_id="paper_123",
        source_intent_id="intent_123",
        source_run_id="run_123",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        side=PaperOrderSide.buy,
        order_type=PaperOrderType.market,
        requested_notional_usdt=Decimal("10.0"),
        requested_quantity=Decimal("0.001"),
        created_open_time="2024-01-01T00:00:00Z",
        correlation_id="corr_123",
        idempotency_key="idem_123",
        source_trace="trace",
        explanation="expl"
    )
    order.status = PaperOrderStatus.paper_accepted_local

    market_data = [{"open_time": "2024-01-01T00:01:00Z", "open": 50000.0, "close": 50100.0}]
    fills = simulator.simulate_fill(order, market_data, base_config)

    assert len(fills) == 1
    assert fills[0].fill_price == Decimal("50000.0") # next_bar_open
    assert order.status == PaperOrderStatus.paper_filled_local
