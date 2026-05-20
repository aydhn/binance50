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

## Phase 4: Safety Layer Architecture

In Phase 4, the system was hardened with an extensive Safety Layer ensuring live-trading logic cannot be circumvented accidentally.

### Credential Guard
Manages API keys and Telegram tokens using `SecretStr` exclusively. Config loads are actively evaluated and intercepted before exposure. Redaction rules apply not just to simple fields but perform deep inspection over mappings.

### API Permission Guard
Implements an **offline validation model**. Before connecting to Binance, the application validates the `.env` metadata describing the permissions of the local API key against the declared requirements of the chosen `EnvironmentProfile`.

### Dry-Run Guard
Enforces restrictions globally when running in non-live modes. If dry-run is enabled, any activation of the order gateway causes an immediate crash (`DryRunViolationError`), guaranteeing simulated actions never reach real execution pathways.

### Live Unlock Guard
A fail-safe specifically for Live environments. It scans memory specifically for exact match confirmation strings ("I_UNDERSTAND_REAL_MONEY_RISK", etc.). The application blocks initialization if any character deviates.

### Effective Trading Mode
A computed concept derived from combining `runtime.trading_mode` and Phase 4 locks (like `force_paper_mode`). While runtime mode declares intention, **Effective Trading Mode** determines actual permission levels inside the guard architecture.

### Order Path Disabled Model
`disable_all_orders` is an absolute kill-switch acting universally across all domains. Even if specific `supports_order_placement` variables are technically true inside testnet matrices, this global toggle fundamentally amputates the functionality at a structural level.

## Connector Layer (Phase 5)

### Connector Architecture
The Binance connector layer acts as the bridge between the core trading engine and the external exchange endpoints. It is designed to be completely modular and environment-aware, preventing accidental mainnet calls during paper trading.

### Adapter Pattern
We utilize an adapter pattern via `ExchangeAdapterProtocol`. This encapsulates environment specifics (Spot vs USDⓈ-M Futures) and returns correctly configured REST and WebSocket clients for the selected network. Supported adapters include `binance:spot`, `binance:usdm_futures`, and a placeholder for `binance:coinm_futures`.

### Client Factory
The `client_factory` is the sole entry point for acquiring connection objects. It automatically consults the safety guards, reads the connection policies, and outputs a `ConnectorBundle`.

### Disabled & Mock Clients
To ensure "secure by default" behavior, the client factory produces a `DisabledExchangeAdapter` if the `connection_enabled` flag is false. This prevents any external network requests. A `MockExchangeAdapter` can be created if `mock_enabled` is true, which supports testing the connector lifecycle without real network I/O.

### Endpoint Resolver & REST/WS Separation
`endpoint_resolver` dynamically fetches the correct base URLs (e.g., testnet vs mainnet, routed vs raw) depending on the active `EnvironmentProfile`. REST and WebSocket clients are distinctly modeled (e.g., `RestConnectorProtocol` and `WebSocketConnectorProtocol`).

### Stream URL Builders
Stream routing varies heavily across Binance's ecosystem. Spot typically uses combined stream payloads (`/stream?streams=x/y`), while USDⓈ-M uses routed endpoints (`/public`, `/market`, `/private`). The client and `stream_names` helper generate safe, properly formatted strings for these contexts.

### Phase 5 Constraints
- **Real Network Blocked:** Actual HTTP and WebSocket requests are strictly unimplemented and intercepted in this phase to harden the structural safety before moving to live execution.
- **Order Gateway:** The `OrderGatewayProtocol` acts only as an interface right now, defaulting to a `DisabledOrderGateway` that denies all order submissions. This guarantees zero chance of capital loss until full live integration is completed.

## Network Safety (Phase 6)
- **Rate Limit Architecture**: Contains an in-memory tracker, header parser, and cooldown manager to evaluate `429` and `418` responses and proactively rate limit based on endpoint weights.
- **Circuit Breaker**: Evaluates repeated connection errors and breaks circuits preventing downstream flood.
- **Clock Sync**: Ensures local time vs. Binance server time difference doesn't exceed `max_allowed_clock_drift_ms` to avoid `recvWindow` rejection.
- **WebSocket Limits**: Evaluates and asserts stream count constraints and incoming message rate boundaries.
- **Real Network Disabled**: Default `False` since all interactions in Phase 6 act as pure simulations.
