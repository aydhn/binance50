# Phase 18 Report

## Oluşturulan/güncellenen dosyalar
- `src/binance50/config/default.yaml` and `src/binance50/config/models.py`: Updated to include backtest configuration structures.
- `src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py`: Added backtest specific exceptions.
- `src/binance50/storage/schemas.py`, `importers.py`: Added storage models for backtest datasets.
- `src/binance50/backtest/`: Created new module directory and the required files: `models.py`, `data_loader.py`, `events.py`, `runner.py`, `broker.py`, `fills.py`, `portfolio.py`, `positions.py`, `equity.py`, `trades.py`, `metrics.py`, `drawdown.py`, `benchmark.py`, `timeline.py`, `validators.py`, `quality.py`, `reports.py`, `cache.py`, `export.py`, `datasets.py`, `reproducibility.py`.
- `src/binance50/safety/`: Added `backtest_guard.py`, `backtest_leakage_guard.py`, `backtest_execution_guard.py`.
- `tests/`: Added unit test files for all the components above.
- `src/binance50/cli.py`: Registered backtest commands.
- `scripts/check_project.py`: Updated with backtest check commands.
- `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/PHASE_PLAN.md`, `README.md`: Updated with architecture details, security guardrails, phase progress, and CLI commands.

## Backtest config kararları
- Backtesting is heavily restricted to simulation via event-driven engine (`real_exchange_forbidden = True`).
- No testnet, live order, or signed request actions are allowed in the configuration.
- Fill parameters disable same bar fills, preventing execution assumption without a subsequent candle.

## Data loader kararları
- Uses local data loaders (from fixtures or warehouse) and ensures OHLCV input matches quality expectations (e.g., gap rejection, row thresholds).
- Network or real exchange connections are disconnected.

## Event-driven runner mimarisi
- Built a deterministic step-by-step runner processing each historical bar sequentially.
- Emits events via `BacktestEventBus` at various lifecycle points (e.g., `run_started`, `bar_opened`, `strategy_evaluated`, `simulated_fill_created`).

## Decision/fill zamanlama kararları
- Requires closed candles for indicator evaluations and signal scoring.
- Enforces a `next_bar_open` filling simulation so that execution cannot front-run decision logic (same bar fills raise exceptions).

## Simulated broker ve portfolio
- Simulated broker tracks margin constraints (none allowed), starting cash (defaults to 1000 USDT) and handles deterministic `BacktestFill` outputs.
- Portfolio aggregates current cash, unrealized and realized PnL, taking positions mark-to-market.

## Fill/fee/slippage modeli
- Taker/maker fees modeled via BPS format (e.g., 10 bps default).
- Slippage acts punitively against the simulated entry/exit prices based on configurable BPS metrics.

## Position lifecycle
- Position states strictly cycle from `open` to `closed` according to filled simulation orders. Max holding bars triggers and end of test closures handle exits automatically.

## Equity curve
- Evaluates per period and records portfolio values into `BacktestEquityPoint` records making it simple to visualize backtest drawdowns and growth.

## Trade journal
- Groups entries and exits into simulated `BacktestTrade` records showing gross/net pnl, fee impact, slippage cost, and reasons for closing.

## Drawdown ve metrikler
- Implemented core mathematical summaries in `metrics.py` covering Return, Win Rate, Expectancy, Profit Factor. Drawdown runs a sequential max metric and extracts discrete events.

## Benchmark placeholder
- Setup standard Buy-and-Hold model without fees or slippage for pure market return alignment comparisons.

## Reproducibility kararları
- Inputs are uniquely hashed with config settings to verify deterministic outcomes on exact configurations and inputs.

## Backtest quality kontrolleri
- Reports analyze the outputs to warn against missing explanations, unexpected duplicate fills, negative cash constraints or empty curves.

## Backtest safety guard
- Verifies that configs don't accidentally enable connection strings, active testnet environments, or true live exchange parameters.

## Backtest leakage guard
- Asserts that lookahead indicators or same-bar alignments did not mistakenly leak future information into the decision-making step.

## Backtest execution guard
- Guarantees the output objects (simulated trades/fills) do not contain attributes representing actual execution parameters (`order_id`, `signature`, API keys).

## Storage/cache entegrasyonu
- Prepared storage schema integration to allow data warehouses to store equity points and trade outcomes as discrete valid datasets. Outputs hashes are verified against cached runs.

## CLI komutları
- Added over a dozen commands representing cache wiping, health checks, execution guards, metrics, and quality queries. E.g. `backtest-run-fixture`.

## Test sonuçları
- All 19 added backtest unit tests passed successfully and cli command integrations successfully execute the stubbed configurations.

## Bilinen sınırlamalar
- No actual order dispatching possible.
- `run_from_warehouse` and indicator computations inside the runner are functionally stubbed pending deep warehouse integrations in Phase 19+.

## Phase 19’a hazırlık
- Phase 19 focuses on deep dive metrics (Sharpe, Sortino) and multi-symbol multi-strategy comparative reporting.

