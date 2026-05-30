import uuid
from typing import Optional
from binance50.config.models import AppConfig
from binance50.paper.models import PaperExecutionRunRequest, PaperExecutionRunResult, PaperExecutionMode
from binance50.paper.intents import PaperIntentBridge
from binance50.paper.gateway import LocalPaperGateway
from binance50.paper.fill_simulator import PaperFillSimulator
from binance50.paper.ledger import PaperLedger
from binance50.paper.fees import compute_paper_fee_usdt
from binance50.paper.slippage import compute_slippage_bps, apply_slippage_to_fill_price, compute_slippage_cost_usdt
from binance50.paper.positions import update_position_from_fill
from binance50.paper.pnl import build_paper_pnl_report, compute_equity_curve
from binance50.paper.balances import build_balance_snapshot
from binance50.execution.models import ExecutionIntentDraft
from decimal import Decimal

class PaperExecutionRunner:
    def __init__(self, config: AppConfig):
        self.config = config
        self.intent_bridge = PaperIntentBridge()
        self.gateway = LocalPaperGateway()
        self.fill_simulator = PaperFillSimulator()
        self.ledger = PaperLedger()

    def run(self, request: PaperExecutionRunRequest, intents: list[ExecutionIntentDraft], market_data: list[dict]) -> PaperExecutionRunResult:
        result = PaperExecutionRunResult(
            request=request,
            run_id=f"paper_run_{uuid.uuid4().hex[:8]}",
            mode=PaperExecutionMode.local_paper
        )

        try:
            self.ledger.initialize(self.config.paper_execution.ledger.starting_cash_usdt, self.config)

            orders = self.build_paper_orders_from_intents(intents)
            result.paper_orders = orders

            # submit
            orders = self.submit_orders_locally(orders, market_data)

            # fills
            fills = self.simulate_fills(orders, market_data)
            result.paper_fills = fills

            # update ledger and positions
            positions = []
            position_map = {}
            for fill in fills:
                order = next((o for o in orders if o.paper_order_id == fill.paper_order_id), None)
                if not order: continue

                # simulate slippage and fees
                bps = compute_slippage_bps(order, market_data[0], self.config)
                slipped = apply_slippage_to_fill_price(order, fill.fill_price, bps, self.config)
                fill.slippage_cost_usdt = compute_slippage_cost_usdt(order, fill.fill_price, slipped, fill.fill_quantity)
                fill.fill_price = slipped
                fill.fee_usdt = compute_paper_fee_usdt(order, fill, self.config)

                events = self.ledger.apply_fill(fill, order, self.config)
                result.ledger_events.extend(events)

                pos = position_map.get(order.symbol)
                pos = update_position_from_fill(pos, fill, order, self.config)
                position_map[order.symbol] = pos

            result.positions = list(position_map.values())

            # mark to market
            prices = {m['symbol']: Decimal(str(m['close'])) for m in market_data if 'symbol' in m}
            if not prices and market_data: # fallback
                prices = {request.symbol: Decimal(str(market_data[0]['close']))}

            snapshot = self.ledger.mark_to_market(result.positions, prices, self.config)
            result.balance_snapshots.append(snapshot)

            # Pnl
            curve = compute_equity_curve(result.ledger_events, result.balance_snapshots, self.config)
            pnl_report = build_paper_pnl_report(
                result.run_id,
                self.config.paper_execution.ledger.starting_cash_usdt,
                self.ledger.current_cash,
                snapshot.equity_usdt,
                result.positions,
                fills,
                orders,
                curve,
                self.config
            )
            result.pnl_report = pnl_report.dict()

        except Exception as e:
            result.success = False
            result.error = str(e)

        return result

    def build_paper_orders_from_intents(self, intents: list[ExecutionIntentDraft]) -> list:
        return [self.intent_bridge.build_paper_order_from_execution_intent(i, self.config) for i in intents]

    def submit_orders_locally(self, orders: list, market_data: list) -> list:
        return [self.gateway.submit_paper_order(o, market_data, self.config) for o in orders]

    def simulate_fills(self, orders: list, market_data: list) -> list:
        all_fills = []
        for order in orders:
            fills = self.fill_simulator.simulate_fill(order, market_data, self.config)
            all_fills.extend(fills)
        return all_fills
