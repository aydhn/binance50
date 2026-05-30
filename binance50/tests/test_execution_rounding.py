from decimal import Decimal
from binance50.execution.rounding import floor_to_tick, floor_to_step

def test_floor_to_tick():
    assert floor_to_tick(Decimal("100.125"), Decimal("0.01")) == Decimal("100.12")
    assert floor_to_tick(Decimal("100.125"), Decimal("0.1")) == Decimal("100.10")

def test_floor_to_step():
    assert floor_to_step(Decimal("1.2345"), Decimal("0.01")) == Decimal("1.23")
