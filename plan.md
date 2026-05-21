1. **Requirements Update**: Add `pandas` and `pyarrow` to `requirements.txt`.
2. **Config Models & Default Config**: Update `config/default.yaml` and `src/binance50/config/models.py` with the new market data configuration.
3. **Core Exceptions & Errors**: Add market data exceptions to `src/binance50/core/exceptions.py`, error codes to `error_codes.py`, and classify them in `error_classifier.py`.
4. **Market Data Domain Layer**:
   - Create `src/binance50/market_data/` directory.
   - Implement `intervals.py` for interval math and validation.
   - Implement `ohlcv_models.py` with `OHLCVBar`, `OHLCVFrameMetadata`, `OHLCVFetchPlan`, etc.
   - Implement `kline_parser.py` for DataFrame conversion.
   - Implement `fetch_plan.py` for calculating chunked requests.
   - Implement `fetcher.py` for REST/fixture loading.
   - Implement `incremental.py` for data merging and gap updates.
   - Implement `cache.py` and `store.py` for Parquet saving/loading.
   - Implement `quality.py` and `repair.py` for data validation.
   - Implement `metadata.py`, `reports.py`, `fixtures.py`, `export.py`.
5. **Safety Guard**: Implement `src/binance50/safety/market_data_guard.py`.
6. **REST Client Update**: Add `build_public_kline_request` to `src/binance50/connectors/rest_client.py`.
7. **Fixtures**: Create the required `.json` fixture files in `src/binance50/data/fixtures/`.
8. **CLI Commands**: Add all the new market data commands to `src/binance50/cli.py` and update the `doctor` command.
9. **Tests**: Implement unit tests for all new modules in `tests/`.
10. **Check Script**: Update `scripts/check_project.py` with Phase 8 checks.
11. **Docs**: Update `ARCHITECTURE.md`, `SECURITY.md`, `PHASE_PLAN.md`, and `README.md`.
12. **Pre-commit & Final Tests**: Run formatting, linting, type-checking, and pytest.
