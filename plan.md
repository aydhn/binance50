1. **Config and Exceptions Setup**
   - We already patched `AppConfig` and models (`config/models.py`), default config (`config/default.yaml`), exceptions (`core/exceptions.py`), error codes (`core/error_codes.py`), and error classifier (`core/error_classifier.py`).

2. **Domain Models (`indicators/models.py`)**
   - Create enums `IndicatorGroup`, `IndicatorBackend`, `IndicatorOutputStatus`, `IndicatorWarmupStatus`.
   - Create models `IndicatorSpec`, `IndicatorRunRequest`, `IndicatorRunResult`, `IndicatorFrameMetadata`, `IndicatorColumnMetadata`.
   - Add `to_dict(redacted=True)` methods.

3. **Context Module (`indicators/context.py`)**
   - Create `IndicatorContext` class and helper functions to build it and convert to metadata.

4. **Validation Module (`indicators/validators.py`)**
   - Create input/output validation functions (`validate_ohlcv_input`, `validate_required_columns`, etc.).
   - Reject lookahead columns (`future_return`, `target`, `label`, `next_close`, `forward`).

5. **Warmup/Lookback Module (`indicators/warmup.py`)**
   - Functions to estimate lookback, mark warmup rows, summarize, and assert sufficient history.

6. **Transform Helpers (`indicators/transforms.py`)**
   - Implement `typical_price`, `median_price`, `weighted_close`, `hl_range`, `oc_change`, `true_range`, `returns`, `log_returns`, `rolling_zscore`, etc.

7. **Native Indicators - Trend (`indicators/trend.py`)**
   - Implement native SMA, EMA, WMA, DEMA, TEMA, MACD, ADX, AROON.

8. **Native Indicators - Momentum (`indicators/momentum.py`)**
   - Implement native RSI, Stochastic, Stoch RSI, ROC, Momentum, CCI, Williams %R.

9. **Native Indicators - Volatility (`indicators/volatility.py`)**
   - Implement native ATR, NATR, Bollinger Bands, Keltner Channels, Donchian Channels, Rolling STD, Realized Volatility.

10. **Native Indicators - Volume (`indicators/volume.py`)**
    - Implement native OBV, Volume SMA, Volume EMA, VWAP, MFI, CMF, ADL.

11. **Registry (`indicators/registry.py`)**
    - `IndicatorRegistry` class to manage specs, validate params, and build defaults.

12. **Adapters (`indicators/adapters/`)**
    - `base.py`: Define `IndicatorBackendAdapter` protocol.
    - `native.py`: Implement `NativeIndicatorAdapter`.
    - `talib_adapter.py`: Optional adapter for TA-Lib.
    - `pandas_ta_adapter.py`: Optional adapter for pandas-ta.

13. **Indicator Quality (`indicators/quality.py`)**
    - Models and functions to check for all NaN, high NaN ratio, infs, constant columns, extreme values.

14. **Indicator Cache (`indicators/cache.py`)**
    - Parquet/JSON cache for indicators.

15. **Indicator Exports & Reports (`indicators/export.py`, `indicators/reports.py`)**
    - Report generation and data exporting helpers.

16. **Indicator Engine (`indicators/engine.py`)**
    - Main orchestration class `IndicatorEngine`.

17. **Features (`features/basic_returns.py`)**
    - Basic past returns for future feature store.

18. **Safety Guard (`safety/indicator_guard.py`)**
    - Guards against lookahead bias, invalid configuration, and missing backends.

19. **Storage Schema & Imports (`storage/schemas.py`, `storage/importers.py`)**
    - Update `schemas.py` to add `DatasetKind.INDICATORS` and the dynamic schema.
    - Add `import_indicator_result` to `importers.py`.

20. **CLI and Doctor (`cli.py`, `scripts/check_project.py`)**
    - Add indicator CLI commands.
    - Add indicator checks to `doctor` command and `check_project.py`.

21. **Tests**
    - Write tests for models, registry, warmup, transforms, trend, momentum, volatility, volume, engine, adapters, quality, cache, guard, cli.

22. **Documentation**
    - Update `ARCHITECTURE.md`, `SECURITY.md`, `PHASE_PLAN.md`, `README.md`.

23. **Pre-commit Steps**
    - Verify with tests, format, lint, type check.
