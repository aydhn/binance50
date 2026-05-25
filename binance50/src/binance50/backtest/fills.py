import uuid

from .models import BacktestFill


def simulate_backtest_open_fill(risk_assessment: dict, next_bar: dict, config) -> BacktestFill:
    # Stub implementation
    side = risk_assessment.get("side", "buy")
    price = choose_backtest_fill_price(
        next_bar, config.backtest.timing.fill_model, side, True, config
    )
    simulated_price, slippage_bps = apply_backtest_slippage(price, side, True, config)
    notional = risk_assessment.get("notional", config.backtest.sizing.fixed_notional_usdt)
    quantity = notional / simulated_price
    fee = estimate_backtest_fee(notional, config)

    return BacktestFill(
        fill_id=str(uuid.uuid4()),
        run_id=risk_assessment.get("run_id", "test_run"),
        symbol=risk_assessment.get("symbol", "UNKNOWN"),
        side=side,
        simulated_price=simulated_price,
        simulated_quantity=quantity,
        simulated_notional_usdt=notional,
        simulated_fee_usdt=fee,
        simulated_slippage_bps=slippage_bps,
        fill_time=next_bar["open_time"],
        source_risk_assessment_id=risk_assessment.get("risk_assessment_id"),
    )


def simulate_backtest_close_fill(position, next_bar: dict, reason: str, config) -> BacktestFill:
    # Stub implementation
    close_side = "sell" if position.side == "buy" else "buy"
    price = choose_backtest_fill_price(
        next_bar, config.backtest.timing.fill_model, close_side, False, config
    )
    simulated_price, slippage_bps = apply_backtest_slippage(price, close_side, False, config)
    notional = position.simulated_quantity * simulated_price
    fee = estimate_backtest_fee(notional, config)

    return BacktestFill(
        fill_id=str(uuid.uuid4()),
        run_id=position.run_id,
        symbol=position.symbol,
        side=close_side,
        simulated_price=simulated_price,
        simulated_quantity=position.simulated_quantity,
        simulated_notional_usdt=notional,
        simulated_fee_usdt=fee,
        simulated_slippage_bps=slippage_bps,
        fill_time=next_bar["open_time"],
    )


def choose_backtest_fill_price(
    bar: dict, fill_model: str, side: str, is_open: bool, config
) -> float:
    return bar.get("open", 0.0)


def apply_backtest_slippage(
    price: float, side: str, is_open: bool, config, context=None
) -> tuple[float, float]:
    slippage_bps = config.backtest.slippage.default_slippage_bps
    if not config.backtest.slippage.enabled:
        return price, 0.0

    slippage_amount = price * (slippage_bps / 10000.0)
    if (side == "buy" and is_open) or (side == "sell" and not is_open):
        simulated_price = price + slippage_amount
    else:
        simulated_price = price - slippage_amount

    return simulated_price, slippage_bps


def estimate_backtest_fee(notional_usdt: float, config) -> float:
    if not config.backtest.fees.enabled:
        return 0.0
    fee_bps = config.backtest.fees.taker_fee_bps
    return notional_usdt * (fee_bps / 10000.0)


def validate_backtest_fill(fill: BacktestFill, config) -> None:
    pass
