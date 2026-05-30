from decimal import Decimal
from binance50.execution.notional import compute_notional

def test_compute_notional():
    assert compute_notional(Decimal("10.0"), Decimal("2.0")) == Decimal("20.0")
    assert compute_notional(None, Decimal("2.0")) is None
