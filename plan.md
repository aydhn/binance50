1. **Config Update**:
   - Update `config/default.yaml` with `streams` block.
   - Update `src/binance50/config/models.py` to add `StreamLifecycleConfig`, `StreamsConfig` and add it to `AppConfig`.
2. **Exceptions & Errors**:
   - Update `src/binance50/core/error_codes.py` with Phase 9 stream codes.
   - Update `src/binance50/core/exceptions.py` with Phase 9 stream exceptions.
   - Update `src/binance50/core/error_classifier.py` for stream exceptions.
3. **Stream Layer Definition**:
   - `src/binance50/streams/event_types.py`: `StreamType`, `StreamEventStatus`, `StreamSource`, `StreamRoute` enums.
   - `src/binance50/streams/models.py`: `StreamEvent`, `KlineStreamEvent`, `BookTickerStreamEvent`, etc.
   - `src/binance50/streams/stream_names.py`: Extend `src/binance50/connectors/stream_names.py` and move it or wrap it. (The prompt suggests moving or expanding it here).
   - `src/binance50/streams/subscription.py`: `StreamSubscription`, `StreamSubscriptionPlan`, and builder functions.
   - `src/binance50/streams/parser.py`: Payload parsers to specific event models.
   - `src/binance50/streams/validators.py`: Event validation functions (stale, out_of_order, etc).
   - `src/binance50/streams/buffer.py`: `StreamBuffer` class.
   - `src/binance50/streams/dispatcher.py`: `StreamDispatcher` class.
   - `src/binance50/streams/state.py`: `SymbolStreamState` and `StreamStateStore`.
   - `src/binance50/streams/metrics.py`: `StreamMetricsCollector` and snapshot model.
   - `src/binance50/streams/simulator.py`: `StreamSimulator`.
   - `src/binance50/streams/replay.py`: `StreamReplayEngine`.
   - `src/binance50/streams/routing.py`: Route resolving functions.
   - `src/binance50/streams/lifecycle.py`: Connection lifecycle tracking.
   - `src/binance50/streams/reports.py`: Report builder functions.
   - `src/binance50/streams/fixtures.py`: Helper functions for loading test JSONs.
4. **Safety & Connectors**:
   - `src/binance50/safety/stream_guard.py`: Guard blocking actual connection.
   - `src/binance50/connectors/websocket_client.py`: Integrate with subscription plan.
   - `src/binance50/connectors/stream_connection.py`: Manager skeleton.
5. **Realtime Store**:
   - `src/binance50/market_data/realtime_store.py`: `RealtimeMarketDataStore`.
6. **Fixtures**: Create the listed json files in `src/binance50/data/fixtures/streams/`.
7. **CLI Commands**: Add new stream commands to `src/binance50/cli.py`.
8. **Checks & Tests**:
   - Add new tests in `tests/test_stream_*.py` and `tests/test_realtime_store.py`.
   - Update `scripts/check_project.py` to include new CLI commands and tests.
9. **Docs**: Update `ARCHITECTURE.md`, `SECURITY.md`, `PHASE_PLAN.md` and `README.md`.
10. **Pre-commit**: Format, lint, type-check, and test.
