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
