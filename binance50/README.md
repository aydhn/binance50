# Binance50

A secure, multi-environment algorithmic trading system for Binance.

## Security First Approach

Binance50 is designed with security as its primary concern:
- **Default Paper/Dry-Run Mode**: The system strictly operates in safe simulation mode by default.
- **Never Share Secrets**: You can copy `.env.example` to `.env` but **never** add real secrets to the template or commit `.env` to Git.
- **Multi-Lock Live Trading**: Activating live trading requires multiple conscious steps and environment variable overrides to unlock the order gateway. A single flag is not enough to accidentally spend live capital.

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/binance50.git
    cd binance50
    ```

2.  **Create your local environment configuration:**
    ```bash
    cp .env.example .env
    ```
    *Ensure you only input actual secrets into `.env` and never into `.env.example`.*

3.  **Run Health & Safety Checks (Crucial before starting):**
    ```bash
    python -m binance50.cli doctor
    python -m binance50.cli secrets-check
    python -m binance50.cli dry-run-check
    python -m binance50.cli live-unlock-check
    python -m binance50.cli safety-report-full
    ```

4.  **Explore the Configuration:**
    ```bash
    python -m binance50.cli show-config
    python -m binance50.cli list-environments
    python -m binance50.cli show-environment
    ```

## Documentation
- [Phase Plan](docs/PHASE_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security Guidelines](docs/SECURITY.md)


## Connector Commands (Phase 5)

The connector layer is completely disabled by default and lacks real network implementations in this phase. Live trading is still strictly impossible.

Explore the connector status and capabilities using the CLI:
```bash
python -m binance50.cli connector-status
python -m binance50.cli connector-health
python -m binance50.cli connector-endpoints
python -m binance50.cli connector-capabilities
python -m binance50.cli connector-stream-url-test --symbol BTCUSDT --stream kline --interval 1m --combined true
python -m binance50.cli sdk-check
```

## Network Safety (Phase 6)
- **Status:** Real network calls remain strictly disabled (`real_network_enabled: false`).
- Implemented **Rate Limit Models** tracking weights and limits dynamically without true traffic via simulated mock requests.
- Validated **Clock Sync & Recv Window** models preventing latency and sequence abuse.
- Set restrictions for `418` hard bans, cooldown responses, and circuit breaking mechanics natively integrated across the execution stack.
- To view statuses, use commands like:
  - `python -m binance50.cli rate-limit-status`
  - `python -m binance50.cli rate-limit-simulate --status-code 429`
  - `python -m binance50.cli rate-limit-simulate --status-code 418`
  - `python -m binance50.cli recv-window-check`
  - `python -m binance50.cli clock-sync-status`
  - `python -m binance50.cli websocket-limits-check spot 10 1`
  - `python -m binance50.cli network-safety-report`

### Universe Selection
The universe selection feature identifies safe, tradable pairs based on strict filtering criteria:
- **Elimination:** It aggressively filters out pairs that have low liquidity, high spread, or belong to risky categories (like stablecoin pairs or leveraged tokens).
- **Rule Verification:** It verifies Binance filters (like `MIN_NOTIONAL`, `LOT_SIZE`) to ensure the bot can actually construct valid orders for the symbol.
- **Testing:** Can be tested completely offline utilizing pre-captured JSON fixtures.

Commands:
```bash
python -m binance50.cli universe-config
python -m binance50.cli universe-fixture-select --scope spot
python -m binance50.cli universe-fixture-select --scope usdm_futures
python -m binance50.cli universe-explain BTCUSDT
python -m binance50.cli universe-safety-check
```

## Market Data (Phase 8)
The OHLCV Market Data Layer safely processes historical kline (candlestick) data for analytical use.

- **Real Fetch Disabled**: Default settings prohibit real network requests. You must manually unlock the fetch flags to reach Binance.
- **Fixtures & Mocks**: You can test the entire pipeline safely using local JSON fixtures.
- **Cache & Incremental**: Data is persisted in fast Parquet files. Incremental logic guarantees only missing ranges are updated, safely managing minor overlaps and rejecting incomplete current candles.
- **Quality Checks**: Critical data anomalies (gaps, duplicates, unordered bars, negative volumes) are surfaced immediately to prevent backtest leaks.

Commands:
```bash
python -m binance50.cli market-data-config
python -m binance50.cli ohlcv-fixture-load --symbol BTCUSDT --scope spot --interval 1m --fixture ohlcv_spot_btcusdt_1m_sample.json
python -m binance50.cli ohlcv-quality-check --symbol BTCUSDT --scope spot --interval 1m --fixture ohlcv_spot_btcusdt_1m_sample.json
python -m binance50.cli ohlcv-fetch-plan --symbol BTCUSDT --scope spot --interval 1m --days 7
python -m binance50.cli ohlcv-cache-save-fixture --symbol BTCUSDT --scope spot --interval 1m --fixture ohlcv_spot_btcusdt_1m_sample.json
python -m binance50.cli ohlcv-cache-load --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli ohlcv-incremental-plan --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli market-data-safety-check
python -m binance50.cli market-data-health
```

## WebSocket Market Stream Layer
Phase 9 provides robust offline simulation and structural preparation for real-time WebSocket market data. Real websocket connections are intentionally disabled by default.
Test commands include:
- `python -m binance50.cli stream-simulate`
- `python -m binance50.cli stream-buffer-test`


## Indicator Engine (Phase 11)

The Indicator Engine is designed to securely and deterministically compute technical indicators (Trend, Momentum, Volatility, Volume, and Transforms) across OHLCV datasets. It is responsible for bridging the gap between raw market data and quantitative feature sets suitable for strategies and machine learning.

**Key Features:**
- **Native Backend as Default**: It employs a pure pandas/numpy implementation by default. This eliminates complex dependencies like TA-Lib on platforms like Windows while retaining high performance and perfect determinism.
- **Optional Adapters**: Adapters for TA-Lib and pandas-ta are defined. They are not strictly required, enforcing graceful degradation if uninstalled.
- **Lookahead Bias Prevention**: The engine explicitly blocks the ingestion and creation of future-peeking columns (e.g., labels, targets, future returns). This mathematically guarantees that current calculations strictly rely on present and historical data.
- **Warmup Row Management**: Indicator accuracy requires an initial lookback period. The engine identifies and flags "warmup" periods to prevent strategies from trusting incomplete initial indicator values.
- **Fixture Testing**: Can be run entirely offline against deterministic JSON fixtures for testing.

**Commands:**
- `python -m binance50.cli indicator-config`
- `python -m binance50.cli indicator-backends`
- `python -m binance50.cli indicator-list`
- `python -m binance50.cli indicator-compute-fixture --fixture spot_kline_btcusdt_1m_closed.json --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli indicator-quality-check`
- `python -m binance50.cli indicator-safety-check`
- `python -m binance50.cli indicator-health`

### Indicator V2 Features
- **Divergence Candidate**: Identifies possible market divergences based on strictly backward pivots. They do not constitute actionable trade signals on their own.
- **Causal Pivots**: Local extremes generated without lookahead bias.
- **Multi-Timeframe Alignment**: Robust mechanism strictly aligning completed higher-timeframe candles to current ones.
- **Feature Grouping**: Tagging mechanism categorizing indicators (trend, momentum, volume, etc.).

**CLI Commands:**
- `python -m binance50.cli indicator-v2-config`
- `python -m binance50.cli pivot-detect-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli divergence-detect-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli mtf-align-fixtures --base-interval 1m --higher-interval 1h`
- `python -m binance50.cli pattern-backends`
- `python -m binance50.cli indicator-v2-compute-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli indicator-v2-safety-check`
- `python -m binance50.cli indicator-v2-health`

## Strategy Engine (Phase 13)
The Strategy engine applies structured, declarative rules across computed indicators to generate `SignalCandidate` models.

**Key Safety Principles:**
- **No Orders:** Output candidates are explicitly denied the vocabulary or parameters to execute trades.
- **Rule Determinism:** Uses `RuleBlock` logic arrays ensuring the inputs mathematically correspond to specific candidates.
- **Auditable Explanations:** Every emitted candidate is packaged with a `StrategyExplanation`, explicitly listing exactly which features passed or failed thresholds.

Commands:
```bash
python -m binance50.cli strategy-config
python -m binance50.cli strategy-list
python -m binance50.cli strategy-plugin-health
python -m binance50.cli strategy-run-fixture --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli strategy-quality-check
python -m binance50.cli strategy-safety-check
python -m binance50.cli strategy-health
```

## Signal Scoring Engine (Phase 14)
The Signal Scoring engine normalizes the output of our isolated strategy plugins into comprehensive, reliable `ScoredSignalCandidate` objects.

- **What it does:** It processes directional signal candidates, groups them for confluence (multiple plugins confirming the same intent), detects conflicts, handles staleness/freshness based on bar age, and yields a single mathematically-grounded score bounded between 0 and 100.
- **Not an order:** A `ScoredSignalCandidate` explicitly forbids actionable order properties (like leverage, quantity, exact entry price) or execution language (like "buy now"). This ensures safety boundaries aren't leaked.
- **Confluence and Conflict:** The system dynamically rewards diverse plugins agreeing on the same bar, while levying strict penalties against conflicting inputs on identical bars.
- **Calibration:** Live predictive calibration is considered invalid without realized labels. Actual ML/Calibration relies purely on placeholder frameworks in this phase until a risk engine or backtester can assign outcome labels.

**Commands to run:**
- `python -m binance50.cli signal-config`
- `python -m binance50.cli signal-thresholds`
- `python -m binance50.cli signal-weight-report`
- `python -m binance50.cli signal-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli signal-confluence-report`
- `python -m binance50.cli signal-conflict-report`
- `python -m binance50.cli signal-calibration-report`
- `python -m binance50.cli signal-safety-check`
- `python -m binance50.cli signal-health`


## Regime Classification (Phase 15)
- **Rejim sınıflandırma ne yapar?**: It evaluates structural market contexts independently from immediate trade execution metrics.
- **Hangi rejimler var?**: `trend_up`, `trend_down`, `range_bound`, `volatile`, `calm`, `transition`, and `unknown`.
- **Rejim neden emir değildir?**: Context identification ensures system environments correctly process risk instead of directly issuing trade signals.
- **Rule-based classifier neden ana yol?**: Rule-based methodologies offer deterministic predictability entirely avoiding hidden biases.
- **GMM/HMM neden opsiyonel?**: Complex models carry forward-fitting execution risks safely contained within isolated optionally-toggled interfaces.
- **Lookahead/leakage nasıl engellenir?**: Strict dataset tracking limits feature sets dropping unclosed candles, blocking full-dataset scalers, and targeting center=False rolling features entirely.

### Regime CLI Commands
```bash
python -m binance50.cli regime-config
python -m binance50.cli regime-feature-build-fixture --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli regime-classify-fixture --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli regime-transitions-fixture
python -m binance50.cli regime-optional-models
python -m binance50.cli regime-safety-check
python -m binance50.cli regime-leakage-check
python -m binance50.cli regime-health
```

## Risk Engine v1
The risk engine evaluates scored signals and regime context to produce safe, non-executable risk assessments.
- **What it does**: It evaluates multiple risk dimensions including volatility, liquidity, data quality, and strategy conflicts. It applies pre-configured limitations on exposures, candidates per hour, and loss drawdowns.
- **RiskAssessment is not an order**: A `RiskAssessment` represents a decision (e.g. `approved_for_paper_review`, `rejected_by_risk`) but strictly omits execution parameters (quantities, prices).
- **Hypothetical Notional**: Uses a simulated account equity config variable to generate hypothetical notional risk percent values without executing trades.
- **Futures Leverage**: Acts purely as a placeholder estimation (no live API modifications).
- **Real Balance Blocked**: API calls fetching actual live balances are strictly disabled by the config safety guards.

### CLI Commands
- `python -m binance50.cli risk-config`
- `python -m binance50.cli risk-limit-report`
- `python -m binance50.cli risk-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli risk-quality-check`
- `python -m binance50.cli risk-safety-check`
- `python -m binance50.cli risk-execution-guard-check`
- `python -m binance50.cli risk-health`

### Paper Trading
The Paper engine safely evaluates risk-approved candidates, maintaining a locally simulated account to estimate PnL and trade journaling.
It operates without making real orders, meaning it utilizes 0 network requests, no signatures, and zero actual capital.

**Usage:**
- `python -m binance50.cli paper-config`
- `python -m binance50.cli paper-account-init`
- `python -m binance50.cli paper-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli paper-ledger-report`
- `python -m binance50.cli paper-pnl-report`
- `python -m binance50.cli paper-quality-check`
- `python -m binance50.cli paper-safety-check`
- `python -m binance50.cli paper-execution-guard-check`
- `python -m binance50.cli paper-health`

## Backtesting (Phase 18)
The deterministic event-driven backtest engine loads OHLCV data, processes signals, manages simulated positions, and tracks an equity curve.
It uses strict next-bar fills and prevents lookahead leakage.
Commands:
- `python -m binance50.cli backtest-config`
- `python -m binance50.cli backtest-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli backtest-summary`

## Backtest Reporting v2

The `binance50` backtesting suite utilizes a deterministic reporting layer (v2) designed to produce institutional-grade analytics while strictly preventing lookahead bias and enforcing reality-check quality guards.

### Backtest report pack nedir?
A Report Pack is a consolidated, immutable structure containing the summary, advanced metrics, benchmark comparisons, drawdown details, and contextual breakdowns for a single backtest run. It binds the output to the exact configuration and input data hashes that generated it.

### Advanced metrics nasıl okunur?
Metrics like CAGR, Volatility, Sharpe, and Sortino provide a snapshot of risk-adjusted returns. The system sanitizes outputs (e.g. dividing by zero volatility returns `None`) to prevent misinterpretation of broken data.

### Sharpe/Sortino/Calmar neden tek başına yeterli değildir?
While these ratios quantify risk-adjusted returns, they assume normal distributions and fail to capture path dependency. A strategy with a high Sharpe ratio but only 3 total trades is likely overfit or lucky, which is why the reporting engine issues "low trade count" warnings. Furthermore, metrics alone do not explain *where* the performance came from (hence the need for Regime and Signal Breakdowns).

### Monthly returns nasıl üretilir?
The equity curve is resampled at month-end boundaries to calculate period-over-period percentage returns. This is often formatted into a classic Calendar Heatmap table to quickly spot seasonality or prolonged slumps.

### Benchmark karşılaştırması nasıl yorumlanır?
The benchmark engine aligns the strategy's returns directly against a passive buy-and-hold strategy covering the exact same date range. It highlights whether active trading actually generated "Alpha" (excess return) or simply tracked the market while racking up fees.

### Drawdown v2 ne gösterir?
It calculates the magnitude, duration, and recovery time of every peak-to-trough drop in equity. The `underwater curve` provides a continuous view of how far the strategy was from its all-time high at any given moment.

### Düşük trade count neden risklidir?
Statistical significance requires a sufficient sample size. If a backtest yields a 100% win rate across only 4 trades, the result is practically meaningless. The reporting guards actively flag backtests that fall below the minimum observation thresholds.

### Komutlar:
- `python -m binance50.cli backtest-reporting-config`
- `python -m binance50.cli backtest-report-pack`
- `python -m binance50.cli backtest-advanced-metrics`
- `python -m binance50.cli backtest-monthly-returns`
- `python -m binance50.cli backtest-benchmark-v2`
- `python -m binance50.cli backtest-drawdown-v2`
- `python -m binance50.cli backtest-report-quality-check`
- `python -m binance50.cli backtest-reporting-safety-check`
- `python -m binance50.cli backtest-reporting-health`

## Optimizer (Phase 20)
The Optimizer is an offline research tool that systematically explores parameter combinations to find robust configurations for the strategy engine.

- **What does the optimizer do?** It generates different parameter sets and evaluates them against historical data using the Backtest engine.
- **Why doesn't it generate orders?** Optimization is pure research. Automatically mapping optimized parameters to live execution creates extreme financial risk.
- **Grid vs Random Search**: Grid search evaluates every combination in the parameter space exhaustively. Random search evaluates a specified number of randomly sampled combinations deterministically.
- **Objective function**: It evaluates performance using a weighted combination of Total Return, Sharpe, Drawdown, Trade Count, and Cost Drag.
- **Train/Validation/Test**: The data is split chronologically. The optimizer fits to the Train set, selects the best using the Validation set, and the Test set is kept untouched for final reporting.
- **Overfit Guard**: Rejects or penalizes parameter sets where performance drops significantly between the Train and Validation sets.
- **Robustness Score**: Measures how stable the performance is if the parameters are slightly perturbed, avoiding fragile optimums.
- **Optuna**: Supported as an optional adapter for advanced search algorithms (e.g., TPE) but not required for base operation.

### Optimizer Commands
```bash
python -m binance50.cli optimizer-config
python -m binance50.cli optimizer-search-space
python -m binance50.cli optimizer-split-report
python -m binance50.cli optimizer-run-grid-fixture --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli optimizer-trials-report
python -m binance50.cli optimizer-best-trial
python -m binance50.cli optimizer-overfit-report
python -m binance50.cli optimizer-robustness-report
python -m binance50.cli optimizer-walk-forward-plan
python -m binance50.cli optimizer-safety-check
python -m binance50.cli optimizer-leakage-check
python -m binance50.cli optimizer-health
```

## Walk-forward Validation
- **Walk-forward validation nedir?**: Model optimization spanning simulated progressive timelines.
- **Rolling ve expanding window farkı nedir?**: Rolling uses a constant train window; Expanding stretches back to an anchor.
- **OOS neden selection için kullanılamaz?**: Modifies test bounds ensuring models aren't tested over optimized goals.
- **Parameter drift nasıl okunur?**: Changes spanning multiple periods.
- **Validation-to-OOS degradation ne gösterir?**: Drops in metric value.
- **Stitched OOS equity nedir?**: Accumulated returns merged across windows.
- **Rejim kırılganlığı neden önemlidir?**: Overfitting onto bull markets exposes risks in bears.
- **Komutlar**:
  - `python -m binance50.cli walkforward-config`
  - `python -m binance50.cli walkforward-window-plan`
  - `python -m binance50.cli walkforward-split-report`
  - `python -m binance50.cli walkforward-run-fixture --symbol BTCUSDT --scope spot --interval 1m`
  - `python -m binance50.cli walkforward-oos-report`
  - `python -m binance50.cli walkforward-parameter-drift`
  - `python -m binance50.cli walkforward-degradation-report`
  - `python -m binance50.cli walkforward-stability-report`
  - `python -m binance50.cli walkforward-robustness-report`
  - `python -m binance50.cli walkforward-safety-check`
  - `python -m binance50.cli walkforward-leakage-check`
  - `python -m binance50.cli walkforward-health`

## ML Blending Sandbox
- ML blending sandbox ne yapar? Offline araştırma için model ve rule signal birleştirir.
- Blended score neden gerçek sinyal değildir? Production write yasaktır.
- Weighted probability blend nasıl çalışır? Config'den statik ağırlıklar.
- Komutlar:
  - `python -m binance50.cli ml-blending-config`
  - `python -m binance50.cli ml-blending-inputs`
  - `python -m binance50.cli ml-run-blending-fixture --symbol BTCUSDT --scope spot --interval 1m`

## Portfolio Candidate Selection Sandbox
The Portfolio Candidate Selection Sandbox evaluates isolated single-symbol signals, risk contexts, and ML probability blended candidates in aggregate to construct a holistic candidate ranking. By introducing correlation constraints, diversification logic, and hypothetical exposure monitoring, the system identifies the most optimal multi-asset composition.

Key constraints:
- This is purely hypothetical and offline.
- It does **not** construct production position sizing.
- Sandbox candidates are explicitly blocked from executing against live / paper / execution endpoints.

Commands available:
```bash
python -m binance50.cli portfolio-sandbox-config
python -m binance50.cli portfolio-candidate-inputs
python -m binance50.cli portfolio-run-selection-fixture --symbol BTCUSDT --scope spot --interval 1m
python -m binance50.cli portfolio-selected-candidates
python -m binance50.cli portfolio-correlation-report
python -m binance50.cli portfolio-exposure-report
python -m binance50.cli portfolio-concentration-report
python -m binance50.cli portfolio-diversification-report
python -m binance50.cli portfolio-safety-check
python -m binance50.cli portfolio-sandbox-health
```


## Portfolio Construction Sandbox
The Portfolio Construction layer generates hypothetical allocation structures from selected candidates. It supports:
- **Equal Weight and Inverse Volatility:** Deterministic rule-based distributions.
- **Volatility Targeting and Risk Parity:** Skeletons for advanced optimization approaches.

**Note:** All outputs are strictly hypothetical. No quantities, leverages, or real orders are produced.

### Commands
- `python -m binance50.cli portfolio-construction-config`
- `python -m binance50.cli portfolio-run-construction-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli portfolio-allocation-table`
- `python -m binance50.cli portfolio-method-comparison`
- `python -m binance50.cli portfolio-covariance-report`
- `python -m binance50.cli portfolio-volatility-report`
- `python -m binance50.cli portfolio-risk-contribution-report`
- `python -m binance50.cli portfolio-allocation-safety-check`
- `python -m binance50.cli portfolio-construction-health`

## Execution Safety Abstraction (Phase 28)
Execution safety abstraction ne yapar? It validates intents before they ever leave the strategy and enforces rules against direct allocation-to-order flow.
ExecutionIntentDraft neden gerçek emir değildir? It holds internal simulation details and lacks exchange IDs.
Sandbox/paper/testnet/live ayrımı nasıl korunur? Hardcoded mode configs ensure we operate purely offline in P28.
Gateway neden disabled? Prevent accidental network calls.
Kill-switch ne işe yarar? Default on, prevents gateway submissions.
Payload scanner neyi yakalar? API keys, listen keys, signatures, and exchange IDs.
Binance filter validation neden local skeleton? We do not rely on live networks to check tick sizes or limits.

Komutlar:
- `python -m binance50.cli execution-config`
- `python -m binance50.cli execution-modes`
- `python -m binance50.cli execution-run-safety-fixture --symbol BTCUSDT --scope spot --interval 1m`
- `python -m binance50.cli execution-intents`
- `python -m binance50.cli execution-safety-scans`
- `python -m binance50.cli execution-dry-run-report`
- `python -m binance50.cli execution-gateway-report`
- `python -m binance50.cli execution-kill-switch-report`
- `python -m binance50.cli credential-safety-check`
- `python -m binance50.cli execution-health`
