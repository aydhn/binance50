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

## Market Universe Selection (Phase 7)
The market universe selection layer is responsible for determining which symbols the trading bot is allowed to consider. This involves:
- **Symbol metadata model:** Standardized models representing symbol characteristics, trading status, base/quote assets.
- **Binance filters model:** Models for order size rules like `PRICE_FILTER`, `LOT_SIZE`, and `MIN_NOTIONAL`.
- **Liquidity model:** Evaluation of 24h volume and trade count to ensure sufficient market depth.
- **Spread model:** Analysis of order book bid/ask metrics to avoid illiquid or wide-spread assets.
- **Scoring model:** Weighted ranking system based on liquidity, spread, filter quality, stability, and configured preferences.
- **Blacklist/whitelist policy:** YAML-based rules enforcing exclusion of specific symbols/patterns or prioritizing certain ones.
- **Universe cache:** JSON-based local caching of universe results to reduce parsing overhead and maintain a stable list over short periods.
- **Universe explainability:** Detailed rejection reasons or acceptance scores mapped clearly to symbols to allow auditing of universe construction.
- **Phase 7 Network Separation:** In this phase, true REST/WS calls are not made. The logic depends on comprehensive offline fixture snapshots in order to decouple complex domain validation from external network volatility, guaranteeing structural robustness first.

## OHLCV Market Data Layer (Phase 8)

The OHLCV Market Data Layer is responsible for fetching, parsing, caching, repairing, and incrementally updating kline (candlestick) data for spot and futures markets.

### Kline Parser
Converts raw lists of values (as returned by Binance endpoints or fixtures) into rich `OHLCVBar` domain models and `pandas.DataFrame` structures for analysis and processing. Ensures basic logical consistency (high >= low, volume >= 0) immediately upon parsing.

### Fetch Plan Architecture
Due to limitations like `spot_max_limit` (1000) and `usdm_max_limit` (1500), large data ranges must be split into logical chunks. The `fetch_plan.py` module creates an `OHLCVFetchPlan` consisting of multiple `OHLCVFetchChunk` requests to manage API calls safely without overlapping boundaries unnecessarily.

### Incremental Update Strategy
Updates use `existing_df` (if any cache is loaded) to calculate the `last_complete` candle. Utilizing a user-defined `overlap_candles_on_update`, the next fetch time is padded backwards safely to account for minor revisions on recent candles, ensuring structural integrity without requiring a full re-fetch. Incomplete last candles are typically dropped during caching based on configuration to avoid polluting historical data sets.

### Cache/Store Architecture
Cache partitions data locally by scope, symbol, and interval, primarily saving data to fast, compressed `parquet` files. Alongside data, `OHLCVFrameMetadata` is saved in JSON, maintaining the row count, generation timestamps, gap statuses, and content hashes.

### Metadata Model
Every dataframe includes a metadata model specifying data ranges, the source of data (e.g. `FIXTURE`, `BINANCE_SPOT_REST`), and a quality report status, allowing consuming systems (indicators, backtesters) to understand dataset lineage and integrity.

### Data Quality Checks
Crucial for backtesting leakage prevention. Checks run to detect duplicate timestamps, out-of-order rows, missing expected ranges (gaps), and price or volume inconsistencies (e.g., negative volume or zero closes).

### Repair Strategy
Repair mechanisms can safely drop duplicate observations based on chronological occurrence or correct minor sorting issues. Detected gaps generate gap-fill fetch plans rather than interpolating fake data.

### Fixture/Mock Testing
By default, the real network is completely disabled in Phase 8. Offline JSON fixtures replicate raw Binance payload structures. Testing revolves around loading and asserting these fixtures accurately without any live rate limits.

### Why is real network disabled in Phase 8?
To prevent accidental test script executions consuming API rate limits and because stream buffers, real network pipelines, and final execution guards are yet to be completely wired in Phase 9 and beyond. Phase 8 strictly focuses on the internal modeling and local state generation of historical market data.

## WebSocket Market Stream Layer
- **Stream Subscription Plan**: Generates stream paths and payload models offline.
- **Stream Parser**: Deserializes raw string payloads into strongly-typed Pydantic event models.
- **Stream Buffer**: Implements max capacity and drop policies (e.g., `reject_new`) for event queues.
- **Stream Simulator/Replay**: Loads offline JSON fixtures, executes pipeline steps sequentially, validating parsing and buffer handling without actual network.
- **Lifecycle**: Tracks reconnection timers, ping/pong delays offline.

**Why Phase 9 lacks real WS connections**: We must first ensure we can robustly model, digest, test, limit-check, and safeguard streams entirely offline to prevent rate-limit bans or stale data processing bugs in production.

## Indicator Engine (Phase 11)
- **Indicator Engine Architecture**: Decoupled engine processing OHLCV data to generate technical indicators via an extensible registry.
- **Native Backend**: Pandas/Numpy-based native calculation path serving as the robust default without heavy dependencies.
- **Optional Backend Adapters**: Protocol-based adapters permitting integration of libraries like TA-Lib or pandas-ta gracefully.
- **Indicator Registry**: Centralized repository of specifications, mapping configuration parameters to computing functions.
- **Warmup/Lookback Model**: Explicit handling of required history rows (warmup period) to ensure indicator outputs are valid and not skewed by insufficient data.
- **Indicator Metadata Model**: Detailed generation tracking including lookback boundaries and output validity windows.
- **Indicator Quality Checks**: Validation routines that check for structural issues such as all-NaNs, infinity, constant values, or outliers.
- **Lookahead-bias Prevention**: Strict barriers rejecting columns with future labels to ensure indicator execution relies strictly on past and present data.
- **Warehouse Integration**: Generated indicator outputs alongside their configurations and metadata can be written directly to the localized data warehouse.
- **Why no strategy signals in Phase 11?**: The goal of this phase is isolating the deterministic computation of metrics. Evaluation and trading signals belong in the forthcoming strategy and scoring engines to maintain the single-responsibility principle.

## Phase 12: Indicator Engine V2

The Indicator Engine V2 builds upon the V1 base and adds higher-level abstractions like Divergence Candidate generation, Multi-timeframe (MTF) alignment, Pattern Skeletons, and Feature Groupings.

- **Causal Pivot Detection**: Pivots are determined exclusively using backward-looking windows. There is no future leakage.
- **Divergence Candidate Model**: Emits signals based on price vs indicator movements. These are *candidates*, not direct trade signals.
- **Multi-timeframe Alignment**: Implements strictly backward (`asof`) alignment. Forward/nearest matching is disabled.
- **Feature Grouping & Metadata Registry**: Maintains provenance and statistics for all generated columns.
- **Lookahead-safe feature pipeline**: Preempts the possibility of target/label leakage in the features layer.
- **No Trade Signals in Phase 12**: Signals, backtesting, and ML are explicitly excluded from this phase to focus on stable structural feature engineering.

## Strategy Engine (Phase 13)
The Strategy Engine orchestrates trading ideas over market and indicator data.

### Strategy Plugin Architecture
Strategies are implemented as dynamically loaded plugins adhering to the `StrategyPluginProtocol`. They operate in strict isolation, preventing a single failure from halting the execution pipeline.

### Rule DSL
A declarative domain-specific language (DSL) is provided (`RuleBlock` and `RuleCondition`) to enable the rapid assembly of evaluation criteria, simplifying the creation of deterministic bounds mapping features to decisions.

### SignalCandidate Model
Strategies exclusively emit `SignalCandidate` objects. This model explicitly lacks execution intent elements like order types, pricing, or quantities. This decoupling forces strategies to suggest market opinions independently of execution capabilities.

### Built-in Strategy Plugins
Phase 13 establishes basic skeletons:
- Trend Following
- Mean Reversion
- Momentum Continuation
- Volatility Breakout
- Volume Confirmation
- Divergence Candidate
- Multi-timeframe Confirmation
- Pattern Candidate
- Composite Skeleton (defers final decisions until scoring phase)

### Explanations and Decision Traceability
The `StrategyExplanation` model provides rigorous traceability, documenting exactly which feature conditions passed or failed when generating a candidate, fulfilling strict algorithmic explainability mandates.

### Why No Execution in Phase 13?
To adhere to the "Secure by Default" and "Test Driven" principles, execution structures are withheld. Phase 13 merely provides deterministic data classification. Actual trades wait for execution gating and risk engines.

## Signal Scoring Engine (Phase 14)

The **Signal Scoring Engine** translates the output of the Strategy Engine (Phase 13) into unified, explainable, and normalized signal scores. Crucially, the outcome of this phase is *still not an order*.

### Core Components
- **Normalization:** Converts unconstrained candidate confidences to a 0-100 scale based on dynamic criteria.
- **Component Scoring:** Each signal's final score is a weighted aggregation of multiple factors:
    - Base confidence
    - Plugin-specific base weights
    - Multi-timeframe and divergence confirmation
    - Freshness and bar age decay
    - Data quality
- **Confluence Engine:** Groups candidates by bar time and symbol. Signals confirmed by multiple distinct plugins receive confluence bonuses, which are strictly capped to prevent unbounded optimism.
- **Conflict Detection:** Detects opposite-direction candidates (e.g., Bullish and Bearish on the exact same bar). Conflicts do not delete signals; they apply an explicate, capped penalty and flag the signal as conflicted.
- **Freshness/Expiry:** Uses the original `open_time` against current system time or `expiry_bars` to decay older signals linearly or step-wise, ensuring stale signals don't act as current triggers.
- **Calibration Placeholder:** Emits offline placeholder metrics for Brier Score, Expected Calibration Error, and Reliability Bins. Genuine live calibration requires actual realized labels (which depend on a backtesting or live simulation engine).
- **Threshold Classification:** Maps the continuous score into discrete intents (e.g., `research_candidate`, `risk_review_candidate`).

### Why No Execution in Phase 14?
In adherence to the strict isolation principles of binance50, Phase 14 remains intentionally decoupled from order creation or risk sizing. A high-scoring signal (`>90`) signifies strong confluence and system confidence, but executing that signal depends on subsequent risk engines, capital availability, active position limits, and execution routers. Therefore, ScoredSignalCandidates strictly avoid actionable language (like "buy" or "sell") and execution fields (like `quantity`, `leverage`).


## Phase 15: Market Regime Classification
- **Market regime classification architecture:** A decoupled layer providing context (trend, range, volatility) independent of execution.
- **Regime feature engineering:** Extracting structural cues using strictly backward-looking moving calculations and z-scores.
- **Rule-based regime classifier:** Deterministic categorization prioritizing simplicity and transparency over opaque ML optimization.
- **Regime smoothing:** Removing high-frequency noise using majority vote bounded to historical trailing data.
- **Transition detection:** Tracking points of stability shifts.
- **Stability scoring:** Grading the chronological reliability of regimes.
- **Optional GMM/HMM adapters:** Forward-looking skeleton definitions utilizing sklearn and hmmlearn if accessible.
- **Regime quality checks:** Integrity boundaries demanding explicit explanations and banning unlabeled segments.
- **Rejim bilgisinin signal/risk katmanına bağlam olarak aktarımı:** Passing contextual outputs to downstream processes metadata safely.
- **Neden Phase 15’te trading yok?:** Regime classification creates market context—it does not inherently signify an entry or exit point setup.

## Risk Engine v1 (Phase 16)
The risk engine v1 is a non-execution risk evaluation layer. It acts as an intermediary between signal/regime generation and order execution.

- **RiskAssessment**: The core model representing a risk evaluation. It is intentionally designed to NOT contain execution parameters like order quantities or specific order prices.
- **RiskComponent and RiskBreakdown**: Individual risk factors (volatility, liquidity, filters) are evaluated into RiskComponents and aggregated into a RiskBreakdown to explain the risk decision.
- **Signal + Regime Context Integration**: Regime context is used to penalize volatile/transitional regimes or grant bonuses to calm ones, allowing the risk engine to reject candidates that conflict with current market contexts.
- **Symbol Filter & Notional Risk**: Simulates symbol filter rules (e.g. MIN_NOTIONAL) using offline metadata without making API calls.
- **Volatility & Liquidity Risk**: Penalizes wide spreads and low quote volumes or depths based on predefined config thresholds.
- **Futures Leverage Placeholder**: Contains placeholder logic to ensure that leverage is estimated safely without making live `/fapi/v1/leverage` calls.
- **Exposure & Drawdown Placeholder**: Tracks mock exposure counts and limits correlations between concurrent candidates.
- **Frequency/Rate Model**: Places ceilings on how frequently candidates can be generated or approved per symbol and globally.

**No Execution Guarantee**: Phase 16 intentionally avoids generating real orders, position sizing, entry/exit prices, or interacting with live APIs. Risk assessments have intents such as `risk_review`, `future_backtest_candidate`, and `paper_review_candidate`, but never `live_trade`.

## Phase 17: Paper Trading Engine v1
The Paper trading engine simulates risk-approved candidates without executing real orders. It operates strictly locally using simulated constructs.
- **Paper Account Model**: Maintains simulated cash and equity balances without querying Binance.
- **Paper Ledger**: An append-only structure that records all simulation events including candidate evaluation, fills, and position lifecycle.
- **Paper Fill Simulation**: By default, simulates fills based on the open price of the bar following the signal.
- **Paper Position State**: Manages open and closed simulated positions. Supports checking margin and opposing signal constraints.
- **Paper Portfolio Snapshots**: Periodically captures mark-to-market snapshots reflecting current local equity and unrealized PnL.
- **Paper PnL v1**: Simplistic PnL calculations factoring in estimated slippage and fees.
- **Paper Journal**: Logs every closed paper trade along with an explanation linking the source signal and risk regime context.
- **Risk Assessment Integration**: The engine solely accepts RiskAssessment payloads that have the status `approved_for_paper_review` or similar, ignoring rejected signals.
- **Why no real exchange?**: Phase 17 focuses entirely on a sandboxed validation of sequential execution without financial risk or network variability.
## Phase 18: Backtest engine v1
- **Event-driven historical loop**: Deterministic bar-by-bar processing.
- **Decision time vs fill time**: Signals at close, fills at next open.
- **Simulated broker & Fill/fee/slippage model**: Estimates execution costs realistically without actual trading.
- **Position lifecycle**: Maintains open/closed states strictly mapped to simulated fills.
- **Equity curve & Trade journal**: Standardizes reporting logic.
- **Drawdown metrics & Benchmark placeholder**: Comparative performance.
- **Reproducibility model**: Input/output hashes for verified simulation.
- **No real exchange**: Protects from live execution during backtest phases.

## Backtest Reporting v2 architecture

The `Backtest Reporting v2` layer is an advanced analytical layer that ingests the raw, deterministic execution results (from Phase 18) and outputs highly detailed, reproducible, and explainable reporting packs. It operates strictly as an offline observer; it cannot execute trades or influence the simulation state. Its purpose is to answer the question: "How well did this strategy perform contextually?"

### Advanced metrics engine

Provides a robust calculation suite for key risk-adjusted metrics such as CAGR, Annualized Volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Omega Ratio, Tail Ratio, Value at Risk (VaR), and Conditional Value at Risk (CVaR). All metrics natively handle `NaN/inf` edge cases and enforce minimum observation counts.

### Rolling metrics

Evaluates the stability of the strategy over time by computing metrics (like rolling Sharpe, volatility, and return) on shifting windows (e.g., 20, 50, 100 periods). The implementation actively blocks centered windows (`center=True`) to prevent lookahead bias.

### Periodic returns

Resamples the equity curve to generate calendar-based performance summaries, including daily, weekly, monthly, quarterly, and yearly returns. Includes helpers to generate classic monthly return matrices and calendar heatmaps.

### Benchmark v2

A dedicated comparison engine that overlays strategy performance against a benchmark (typically buy-and-hold). It aligns the datetime indices to ensure fair comparisons and computes tracking error and information ratio.

### Drawdown analytics v2

Maps the historical underwater curve to pinpoint the exact depth, duration, and recovery period of all negative equity excursions.

### Trade distribution

Analyzes the characteristics of simulated trades. Generates win/loss distributions, PnL percentiles, consecutive streak counts, and groups returns into histograms for distributional analysis.

### Regime/signal breakdowns

Provides deep contextual analysis by grouping trade outcomes based on metadata. Includes breakdowns by pre-trade market regime (bull, bear, range, etc.), by Signal Score and Risk Score tiers, and by the specific generating Strategy Plugin.

### Cost/exposure analysis

Isolates the impact of simulated trading friction by calculating gross vs. net PnL, total slippage, total fees, and percentage cost drag. Additionally estimates capital turnover and time in the market.

### Report pack generator

The `BacktestReportPackBuilder` acts as a facade, coordinating the individual analytic engines and assembling their outputs into a single, cohesive `BacktestReportPack` model. This pack includes immutable hashes of the inputs and config to guarantee deterministic reporting.

### Optional analytics adapters

Provides skeleton adapters to interface with powerful third-party quantitative libraries (`empyrical` and `quantstats`). These are strictly optional and fallback gracefully to native Python metrics if the libraries are not installed or configured.

### Neden Phase 19'da optimizer yok?

In Phase 19, the focus is entirely on correctly interpreting and reporting the results of a single deterministic backtest run. Introducing an optimizer here would distract from the core goal of establishing stable, mathematically sound evaluation primitives (Sharpe, Drawdown, Hash verification). Once the reporting primitives are rock-solid, Phase 20 will introduce the optimizer, utilizing these exact reports as the fitness scoring mechanism for parameter grids and walk-forward evaluations.

## Optimizer v1 Architecture

The optimizer is designed to find robust strategy parameters using exhaustive (grid) or random search, while remaining completely disconnected from live execution pathways.

- **Search Space Model**: Defines the bounds and distributions of parameters. Execution and live-trading related parameters are strictly rejected from the search space.
- **Grid Search**: Evaluates all combinations of parameters deterministically.
- **Random Search**: Evaluates a random set of parameters, heavily reliant on deterministic seeds.
- **Objective Scoring**: A composite scoring model incorporating return, drawdown, Sharpe, trade count, cost drag, and parameter complexity. Total return is never the sole metric.
- **Time-Series Train/Validation/Test Split**: Enforces chronological evaluation and prevents future leakage using strict `train < validation < test` boundaries.
- **Trial Runner**: Orchestrates the parameter application and backtest run per split.
- **Overfit Guard**: Checks the performance gap between train and validation sets, penalizing or rejecting parameters that only perform well in-sample.
- **Robustness Analysis**: Calculates the stability of a given parameter set by looking at nearby parameters to avoid fragile optimums.
- **Walk-Forward Skeleton**: Prepares the definitions for walk-forward windows without running the full heavy compute cycle (deferred to Phase 21).
- **Optional Optuna Adapter**: Allows extending search methods using Optuna when available, without creating a hard dependency on it.
- **Why no live/paper in Phase 20?**: The optimizer is strictly an offline research tool. Allowing it to interact with execution models creates severe risks of unapproved, auto-generated orders.

## Walk-forward Validation Architecture
- **Rolling window model**: Evaluates fixed size windows progressively.
- **Expanding window model**: Trains on a steadily growing dataset while testing out-of-sample.
- **Anchored expanding model**: Always starts from an anchored first bar.
- **Optimizer bridge**: Bridges validation configurations via parameter optimization routines.
- **OOS evaluation**: Separate out-of-sample testing isolated from model training.
- **OOS equity stitching**: Joins output capital over different windows.
- **Parameter drift analysis**: Analyzes whether parameter ranges drift significantly.
- **Validation-to-OOS degradation**: Tracks score drop-offs from validation to OOS.
- **Walk-forward stability**: Computes aggregated run metrics across multiple tested windows.
- **Regime robustness analysis**: Protects against over-exposure in single trends.
- **Walk-forward leakage guards**: Ensures no nearest fill, forward-fill or future hints are fed to models.
- **Neden Phase 21'de execution yok?**: Phase 21 focuses solely on robust statistical generation instead of active order triggering.

## ML Ensemble and Blending Sandbox (Phase 25)
- ML ensemble and blending sandbox architecture
- Input loaders
- Time-safe alignment
- Static weight engine
- Probability blending
- Rule-based signal blending
- Calibration-aware weighting
- Regime/risk context blending
- Disagreement analysis
- Diversity analysis
- Sandbox blended candidates
- Integration contract
- Soft voting skeleton
- Stacking skeleton
- No production write in Phase 25.

## Portfolio Candidate Selection Sandbox (Phase 26)
- **Candidate input loader**: Loads signals, risk context, ML blended candidates, and regime data into unified CandidateInputs.
- **Candidate normalization**: Normalizes heterogeneous scores and probabilities to a common 0-100 scale.
- **Eligibility and deduplication**: Filters stale candidates, drops blocked ones, and resolves duplicates.
- **Correlation matrix builder**: Estimates Pearson/Spearman pair correlation of symbol returns.
- **Similarity analysis**: Analyzes cosine similarity of candidate score feature vectors.
- **Hypothetical exposure model**: Computes aggregate candidate exposure percentage relative to simulated equity.
- **Concentration analysis**: Checks symbol density, directional biases, and regime overlaps.
- **Diversification scoring**: Rewards candidate selections that blend uncorrelated strategies or signals.
- **Risk budget placeholder**: Demonstrates risk consumption.
- **Ranking engine**: Weights scores and applies penalties.
- **Optional constrained optimizer skeleton**: Provides Scipy optimization logic structure, but restricts output to sandbox-only.
- **Sandbox selected candidates**: The final product is a non-executable list of portfolio candidate selections, which must never be confused with live execution commands or position sizing.


## Portfolio Construction Sandbox Architecture
The portfolio construction sandbox layer is responsible for creating hypothetical allocations from selected candidates. It includes:
- **Selected candidate loader:** Validates and loads inputs.
- **Returns and covariance matrix:** Calculates historical data necessary for risk assessment.
- **Volatility estimation:** Handles scaling based on historical behavior.
- **Equal weight baseline & Inverse volatility allocation:** Deterministic rule-based allocation methods.
- **Volatility targeting skeleton & Risk parity skeleton:** Optimization methods that stop short of executing real trades.
- **Risk contribution analysis:** Computes the marginal and component risk of each candidate.
- **Constraint checker:** Verifies adherence to predefined limits.
- **Optional SciPy SLSQP & PyPortfolioOpt adapters:** Used solely for research purposes without triggering live orders.

Production allocation is strictly forbidden in Phase 27 to maintain absolute separation between research projections and execution realities.

## Execution Safety Abstraction (Phase 28)
- Execution safety abstraction architecture provides local safety validations.
- Order intent vs exchange order ayrımı: `ExecutionIntentDraft` is purely internal and not actionable on the exchange.
- Sandbox/paper/testnet/live mode separation: only `sandbox` is enabled, all execution is blocked.
- Disabled gateway architecture: local interfaces exist but implementations throw errors.
- Binance filter validation skeleton ensures formats, max-notionals, and rounding using cached datasets.
- Payload safety scanner checks for credential, order IDs, and real-order fields, preventing submission.
- Intent lifecycle state machine allows transitions internally but rejects exchange states.
- Idempotency/correlation id design ensures traceability of decisions.
- Kill-switch and circuit breaker act as fail-safes.
- Intent promotion policy rejects moving intents to testnet or live.
- Neden Phase 28’de order submission yok? It's essential to build the entire safety boundary before attempting network communication.

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
