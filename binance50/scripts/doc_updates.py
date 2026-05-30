with open("binance50/README.md", "a") as f:
    f.write("""
## Paper Execution Bridge

The paper execution bridge allows for local simulation of paper orders based on `ExecutionIntentDraft`s. It safely isolates the paper run from the real exchange API, simulating fills, slippage, fees, and keeping an append-only ledger for PnL calculation. No real order payloads are exported.

Commands:
- `python -m binance50.cli paper-config`
- `python -m binance50.cli paper-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli paper-orders`
- `python -m binance50.cli paper-fills`
- `python -m binance50.cli paper-ledger`
- `python -m binance50.cli paper-pnl-report`
- `python -m binance50.cli paper-safety-check`
- `python -m binance50.cli paper-health`
""")

with open("binance50/docs/ARCHITECTURE.md", "a") as f:
    f.write("""
## Paper Execution Bridge v1
The Paper Execution bridge safely translates a `ExecutionIntentDraft` to a `PaperOrder`.
- **Local paper gateway:** Does not connect to any network. Simulates transition to accepted state.
- **Fill simulator:** Generates fills using next-bar execution rules to prevent lookahead bias.
- **Fee/slippage simulator:** Applies hypothetical slippage and fixed fees.
- **Append-only paper ledger:** Tracks cash and asset deltas.
- **Balance and position ledger:** MTM evaluation of equity.
- **Paper PnL engine:** Calculates realized/unrealized PnL.
- **Replay engine:** Evaluates determinism.

Note: Testnet and live order execution are strictly disabled in Phase 29.
""")

with open("binance50/docs/SECURITY.md", "a") as f:
    f.write("""
## Paper Execution Security
- Paper order is not a real order.
- Paper fill is not a real fill.
- Paper PnL is not real profit/loss.
- API keys, signed requests, Binance REST, WebSocket, and `/api/v3/order/test` are strictly forbidden.
- Same-bar fill is forbidden to prevent lookahead bias.
- Negative cash and short spot positions are rejected.
- The paper gateway is strictly local-only.
- Paper exports are not exchange-ready payloads.
""")

with open("binance50/docs/PHASE_PLAN.md", "r") as f:
    content = f.read()

import re
content = re.sub(r"- Phase 29:.*", "- Phase 29: Paper execution bridge v1; ExecutionIntentDraft’tan local-only PaperOrder lifecycle simülasyonuna geçiş, next-bar fill simulator, fee/slippage, append-only ledger, balance/position/PnL, local paper events, replay ve paper safety guard altyapısını kurar; Binance REST/testnet/live/signed request kapalı kalır.", content)
content = re.sub(r"- Phase 30:.*", "- Phase 30: Phase 30’da Telegram notification v1 kurulacak; paper execution, PnL, risk ve sistem health olayları Telegram’a güvenli, rate-limited ve secrets-redacted şekilde gönderilecek.", content)

with open("binance50/docs/PHASE_PLAN.md", "w") as f:
    f.write(content)
