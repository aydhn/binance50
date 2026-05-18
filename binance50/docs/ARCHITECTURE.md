# Architecture

The system is designed with multiple decoupled engines and layers. This allows swapping implementations and simplifies testing.

## Planned Layers

1. **Config & Environment Layer**
   Loads and validates YAML and ENV settings safely.
2. **Binance Connector Layer**
   Handles authenticated requests, WebSockets, rate limiting.
3. **Market Data Layer**
   Fetches and processes OHLCV and order book data.
4. **Local Data Store Layer**
   Caches historical data locally (CSV/Parquet) for backtesting.
5. **Indicator & Feature Engine**
   Computes technical indicators and ML features.
6. **Strategy Plugin Engine**
   Loads and executes trading logic dynamically.
7. **Regime Detection Engine**
   Identifies market regimes (trend, range, volatility).
8. **Signal Scoring Engine**
   Aggregates strategy signals and calculates confidence scores.
9. **Risk Engine**
   Validates orders against risk parameters (drawdown, position size).
10. **Portfolio/Exposure Manager**
    Tracks current asset allocation.
11. **Backtest Engine**
    Simulates trading over historical data with realistic assumptions.
12. **Benchmark Engine**
    Compares strategy performance against buy-and-hold baselines.
13. **Optimizer/Walk-Forward Engine**
    Finds optimal parameters avoiding overfitting.
14. **ML Engine**
    Generates predictive features and models.
15. **Paper Trading Engine**
    Simulates trading on live data without real orders.
16. **Testnet/Demo Execution Engine**
    Executes trades on Binance Testnet.
17. **Live Execution Gateway**
    The final layer for mainnet trading.
18. **Telegram Communication Layer**
    Sends updates and receives commands.
19. **Scheduler/Watchdog**
    Orchestrates execution and ensures system health.
20. **Reports/Audit/Journal Layer**
    Maintains a detailed ledger of all decisions.
21. **Tests and Validation Layer**
    Ensures code quality and correctness.
