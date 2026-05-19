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

## Environment Matrix

To safely manage trading environments, we utilize a strict Environment Matrix. This decouples the trading logic from the underlying execution context and ensures that dangerous actions are difficult to perform accidentally.

*   **Paper/Testnet/Live Separation**: By explicitly separating paper, testnet, and live modes, the system knows exactly what the intention is. Paper mode uses local simulation, testnet connects to Binance's simulated endpoints, and live connects to the real market.
*   **Read-Only Mainnet**: We offer profiles that connect to the mainnet for real-time market data but explicitly disallow any order placement. This is ideal for paper trading against real order books without any risk of executing a trade.
*   **Live Order Gateway Flag**: Even if a profile supports live trading, the order gateway must be explicitly enabled via a separate configuration flag (`order_gateway_enabled`). This adds an extra layer of protection.
*   **Endpoint Configuration**: Endpoints (REST and WebSocket URLs) are tied directly to the selected environment profile in the configuration (`environments.yaml`). The code never hardcodes endpoints during execution, making the system extensible and easily testable.
*   **Connector Separation**: In Phase 2, the actual connection logic is mocked/disabled by default. This ensures that the environment setup is completely solid before we introduce live network requests in later phases.

## Logging Architecture
The logging architecture uses standard Python `logging` with specialized formatters and filters.
- **SafeConsoleFormatter**: For human-readable console output.
- **SafeJsonFormatter**: For structured JSON logging to files, enabling easy integration with log aggregators.
- **Filters**: `RedactionFilter` (masks secrets), `CorrelationIdFilter` (adds request tracking), `RuntimeContextFilter` (adds environment and mode info).

## Audit Trail Architecture
The audit trail is a separate, structured logging path designed for security and compliance.
- Written to `logs/binance50_audit.jsonl` exclusively in JSON Lines format.
- Uses the `AuditEvent` dataclass to ensure consistent schema.
- Tracks critical state changes, errors, and safety checks.
- Features automatic metadata redaction before serialization.

## Error Taxonomy & Binance Classification
The application uses a deep hierarchy rooted in `Binance50Error`.
- **General Errors**: ConfigError, SafetyError, SecretLeakError.
- **Binance API Errors**: Specific classes for rate limits (429 -> `BinanceRateLimitError`), IP bans (418 -> `BinanceIpBanError`), execution status unknowns (5XX -> `BinanceUnknownExecutionStatusError`).
- The `error_classifier` maps HTTP statuses and Binance error codes to these specific Python classes.
- *Note: In Phase 3, no actual API calls are made. This architecture is established in preparation for the connector implementation in Phase 4.*

## Correlation ID Lifecycle
- Created at the start of a logical operation (e.g., app init, scheduled job run).
- Stored using `contextvars` to flow through all async and sync calls seamlessly.
- Included automatically in both application and audit logs.

## Runtime Context Propagation
- Similar to Correlation ID, the active environment profile, trading mode, and market scope are stored in `contextvars`.
- This ensures every log and audit event is permanently tagged with the context it ran under, preventing confusion when reviewing logs from mixed environments.
