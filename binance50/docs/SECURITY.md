# Security Guidelines

## Core Principles
1. **Never log secrets.** API keys, passwords, tokens, and chat IDs must be masked (`***`) before hitting console or files.
2. **Live trading is disabled by default.** Multi-layer confirmation is required to activate live trading.
3. **API Keys belong in `.env`.** Never commit secrets or default them in YAML files.
4. **Testnet and Paper Trading first.** Never start testing on live markets.
5. **Dry-Run guards are mandatory.** The Live Execution Gateway cannot be bypassed.
6. **No manual intervention required.** Once running, the system makes safe decisions; but initiating live mode is a conscious, manual choice by the user.

## Live Execution Guidelines

*   **Mainnet Readonly Model**: The safest way to interact with mainnet data is through a readonly profile (`spot_mainnet_readonly` or `usdm_futures_mainnet_readonly`). These profiles explicitly disallow the `order_gateway_enabled` flag, preventing any real orders from being submitted while allowing ingestion of live market data.
*   **Testnet/Demo Order Safety**: Testnet environments require their own explicit profiles. A testnet profile cannot be used to submit orders if the trading mode is inadvertently set to `live`. Testnet environments must be strictly segregated from mainnet environments.
*   **Live Unlock Procedure**: Live trading requires multiple confirmations. You must explicitly configure `enable_live_trading` and `confirm_live_trading` in your `default.yaml` (or via environment variables).
*   **Environment Variable Lock**: In addition to configuration files, live trading requires the environment variable `BINANCE50_LIVE_UNLOCK` to be set to precisely `"I_UNDERSTAND_REAL_MONEY_RISK"`. This prevents accidental deployment scripts from activating live trading.
*   **Default Paper Mode Policy**: The system always defaults to `local_paper_spot`. You must explicitly override the profile to connect to testnet or live.
*   **Connector Disabled by Default Policy**: The global connection switch (`connection_enabled`) defaults to `false`. No outbound connections to Binance are made unless explicitly enabled, ensuring that the system is safe to start and inspect offline.

## Secret Redaction Policy
- Passwords, API Keys, Secrets, Tokens, and Chat IDs are never written to disk or console.
- Recursive redaction is applied to dictionaries, lists, and strings.
- Patterns matching Binance keys (64 char alnum) or Telegram tokens are aggressively masked.
- If a secret leak is detected during safety checks, a `SecretLeakError` is raised.

## Logging Prohibitions
- Raw HTTP Authorization headers.
- Full payload dumps containing keys.
- Exception tracebacks that inadvertently capture local variables containing secrets (handled via string-level redaction on traceback text).

## Audit Trail Boundaries
- Audit logs contain decision logic and state transitions but never raw financial credentials or PII.
- It is mandatory to have a functioning audit trail before live trading is unlocked.

## Error Handling Security
- **429 (Rate Limit)**: Triggers an automatic circuit breaker or backoff, audited as `rate_limit_warning`.
- **418 (IP Ban)**: Triggers an immediate halt (`BinanceIpBanError`), requires manual intervention.
- **5XX (Unknown Execution Status)**: Treated critically. We assume the order state is unknown and halt trading to prevent duplicate orders or unintended exposure.

## Phase 4 Security Enhancements

### `.env` and `.env.example` Policy
- **Never commit `.env` to the repository.** `.gitignore` strictly protects `.env` and `.env.*`.
- **No real secrets in `.env.example`.** The example template must leave sensitive variables blank. Long, secret-like strings in `.env.example` will trigger a `SecretLeakError`.

### Secret Redaction Guarantee
- The application guarantees that secret values (e.g., API keys, telegram tokens) are aggressively redacted before hitting any output mechanism.
- Dumps, logs, exceptions, and safety reports will consistently mask secrets with `***redacted***` or similar, ensuring absolute protection against accidental leakage.

### API Key Permission Policy
- The project implements an **offline permission model**. Binance API credentials metadata (e.g., `BINANCE_API_PERMISSION_SPOT_TRADE`) is provided by the user in `.env`.
- The `api_key_guard` evaluates this metadata against the selected `EnvironmentProfile`. Read-only profiles strictly block trading permissions. Live profiles dynamically verify the corresponding market permission (spot vs. futures).

### Readonly Profile Security
- `spot_mainnet_readonly` and `usdm_futures_mainnet_readonly` are strictly for ingesting live market data without the ability to place orders.
- If these profiles are used alongside an enabled `order_gateway`, or if they declare trade-enabled API credentials, the system blocks execution.

### Dry-Run Mode
- **Dry-run is enabled by default (`BINANCE50_DRY_RUN=true`).**
- When dry-run is active, the order gateway is strictly blocked, preventing simulated environments from accidentally sending real orders.

### Force Paper Mode
- **Force paper mode is enabled by default (`BINANCE50_FORCE_PAPER_MODE=true`).**
- This globally overrides the trading mode to `paper`. Changing the runtime environment to `live` or `testnet` is impossible while this flag remains active.

### Disable All Orders Flag
- **Disable all orders is enabled by default (`BINANCE50_DISABLE_ALL_ORDERS=true`).**
- Serves as the ultimate kill-switch. When true, the order path is universally disabled, regardless of dry-run or force-paper mode states.

### Live Unlock Phrase
- Live trading is guarded by a manual phrase confirmation (`BINANCE50_LIVE_UNLOCK`). The exact text must be provided (e.g., `"I_UNDERSTAND_REAL_MONEY_RISK"`). If it does not strictly match, live trading is blocked.

### Live Risk Acknowledgement
- Mainnet confirmation involves a secondary lock (`BINANCE50_LIVE_RISK_ACK`). The user must supply the exact acknowledgment phrase (e.g., `"I_ACCEPT_FULL_RESPONSIBILITY"`) to confirm the risk.

### Mainnet/Live Transition Checklist
- Disable `BINANCE50_DRY_RUN`, `BINANCE50_FORCE_PAPER_MODE`, and `BINANCE50_DISABLE_ALL_ORDERS`.
- Set `BINANCE50_ENABLE_LIVE_TRADING` and `BINANCE50_CONFIRM_LIVE_TRADING` to `true`.
- Supply exact phrases for `BINANCE50_LIVE_UNLOCK` and `BINANCE50_LIVE_RISK_ACK`.
- Enable connector and order gateway explicitly (`BINANCE50_CONNECTION_ENABLED`, `BINANCE50_ORDER_GATEWAY_ENABLED`).
- Configure exact Live Mainnet profile in `environments.yaml` and `.env`.
- Supply valid, strictly-scoped API credentials.

### Why not a single flag for live trading?
- A single flag (like `IS_LIVE=true`) is too easy to flip accidentally, especially via bulk environment variable loads or quick testing.
- Requiring distinct, explicit flags alongside long, complex strings guarantees the user has consciously decided to deploy live capital.

## Connector Security

### Default Disabled State
All connections are strictly disabled by default. If `connection_enabled` is false, only the disabled client variant is instantiated, enforcing an air-gapped simulation environment.

### Phase 5 Explicit Network Block
In Phase 5, real network implementations are absent from the clients. `allow_real_network_in_phase5` defaults to false and will trigger a safety error if flipped to true, ensuring we build structural safety before implementing live I/O.

### Order Gateway Constraints
The order gateway defaults to `DisabledOrderGateway`. Attempts to execute an order in Phase 5 will explicitly throw an `OrderPathDisabledError`.

### Credentials Policy
`user_data_stream_enabled` cannot be true unless appropriate API keys and secrets are present in the configuration.

### Logging & Auditing
All connector factory events (enabled, mock, disabled) are strictly audited. API responses, headers, and signatures (once implemented) are redacted in log dumps.

### Official SDK Recommendations
We detect and warn against unofficial packages like `python-binance`. The environment relies natively on explicit `websockets` and `httpx` abstractions, allowing adoption of the official `binance-connector-python` seamlessly in later phases.

### Connection Resilience & Routing
WebSocket reconnections (e.g., Binance's 24-hour limit) and routed endpoint logic (USDM public/market/private) are accounted for at the metadata level to guide implementation and guardrails when fully active in subsequent phases.

## Network Safety and Rate Limit Policies (Phase 6)
- **429 Handling**: Triggers a backoff limit based on `Retry-After` header or falls back to `cooldown_on_429_seconds`. Hard stops incoming requests until cooled down.
- **418 Handling**: IP Auto-ban triggers an unrecoverable (manual intervention) hard-stop across all network systems via `cooldown_on_418_max_seconds`.
- **recvWindow and Time Drift**: Prevents requests if local clock drifts further than Binance bounds. Rejects timestamp manipulations preventing timing attacks.
- **WebSocket Budgets**: Connection policies block stream creations beyond official Binance limits (1024 spot, 200 usdm) and 5/10 message limits per second per connection.
- **5XX Handling**: Safely evaluates retry bounds and gracefully delegates execution resolution to upcoming Phase capabilities.

## Symbol Selection Security (Phase 7)
The universe selection limits the operational space of the bot to safe, known bounds:
- **Low Liquidity Risk:** Symbols with low 24h quote volume or trade counts are categorically excluded to prevent slippage traps.
- **Wide Spread Risk:** Enforces max spread basis points (bps) to prevent trades on illiquid books.
- **Notional and Lot Size Risk:** Verifies that minimum trade requirements (`minNotional`) are not unsafely high and `stepSize`/`tickSize` fit acceptable granularities.
- **Stablecoin Pair Default Exclusion:** Disallows trading USD/USDT style stable-pairs by default to prevent stuck capital in stationary markets.
- **Leveraged Token Default Exclusion:** By default, patterns like "UP", "DOWN", "BULL", "BEAR" are rejected to avoid compounding decay products.
- **Blacklist Priority:** The blacklist is absolute. A symbol matched on the blacklist is rejected, even if present on the whitelist.
- **Whitelist Non-Auto-Acceptance:** Whitelist presence provides a score preference boost but does not bypass critical liquidity, spread, or status filters.
- **Selection is Not Execution:** Inclusion in the universe does not equal an order execution decision. The universe simply defines the candidate pool for the trading strategy.

## Market Data Safety (Phase 8)

### Public Market Data Security Boundaries
Market data fetching operates completely strictly on public endpoints (`/api/v3/klines`, `/fapi/v1/klines`). No API keys or signatures are ever injected into these queries.

### Real Fetch Guard
In Phase 8, `real_fetch_enabled` defaults to `false`. The `assert_market_data_config_safe` check ensures that the initial environment runs safely without emitting real HTTP requests, returning mock or fixture data instead.

### Rate Limit Compliance
Fetch chunks are dynamically created not to exceed exact API endpoint limits (e.g., 1000 for Spot). Each planned chunk estimates request weights compatible with the Phase 6 rate limit budgets.

### Cache Path Safety
`assert_cache_path_safe` guarantees that dynamic symbols or intervals cannot exploit path traversal (e.g. `../../etc/passwd`) by enforcing cache resolutions within the specific configured root project data directory.

### Incomplete Candle Risk
Caching incomplete (currently open) candles leads to severe predictive leaks and distorted indicators in offline usage. Configuration like `exclude_incomplete_last_candle` strictly eliminates this risk by dropping unclosed candles before committing to parquet stores.

### Duplicate/Gap/Out-of-Order Risk
A corrupt market data series (e.g. overlapping records or chronological gaps) ruins backtest reality. All loaded cache and network payloads pass through `validate_ohlcv_dataframe` to surface these issues explicitly before consumption.

### Cache Metadata and Secrets
`OHLCVFrameMetadata` captures data hashes, lengths, and intervals—it explicitly drops all raw API strings and avoids storing API tokens or environments, keeping cache files portable and non-sensitive.

## WebSocket Limits & Safety
- Limit tracking ensures no more than 1024 streams per spot connection.
- Stream connections are strictly blocked by `stream_guard` if `market_stream_real_connect_enabled` is false.
- User Data Streams and Private Routes are completely locked out in Phase 9.

## Indicator Security & Safety (Phase 11)
- **Lookahead Bias Risk**: The engine is guarded against calculating values that incorporate future knowledge, a critical risk in algorithmic trading testing.
- **Future/Target/Label Column Ban**: Input constraints explicitly reject any columns implicitly suggesting target prices or forward returns (`future_return`, `label`, etc.).
- **Warmup Rows Risk**: The system ensures metrics outputted early in a dataset that haven't consumed sufficient historical data points are clearly marked or omitted, preventing false confidence in strategy layers.
- **Incomplete Candle Risk**: Options are strictly provided to drop incomplete candles to ensure indicator consistency across boundaries.
- **Optional Dependency Security**: Third-party indicator libraries (TA-Lib, pandas-ta) are loaded securely and their absence gracefully managed rather than crashing the runtime.
- **Indicator Output != Trade Signal**: Indicator values are strictly mathematical features and are structurally prohibited from issuing live execution commands.
- **Indicator Cache Path Security**: Storage mechanisms apply path sanitization to prevent traversal attacks when defining or loading cached metrics.

## Indicator V2 Feature Security
- **Divergence repainting risk**: Blocked via strict configuration. Centered rolling windows are prohibited.
- **Causal pivot principle**: Pivots only observe past data to confirm themselves.
- **MTF future leakage risk**: Eliminated by ensuring `higher_close_time <= base_open_time`.
- **Target/Future column ban**: Prevents "next_close" or "future_return" columns from polluting the feature registry.
- **Pattern Candidates != Signals**: Skeletons deliberately output strengths/confidences rather than execute paths to ensure separation of concern.

## Strategy Plugin Security & Safety (Phase 13)

### Output is NOT an Order
Strategies are forcefully sandboxed away from the connector lifecycle. `SignalCandidate` outputs contain no parameters for execution sizing, entry limits, or risk locks.

### Actionable Language Guard
The `signal_candidate_guard` explicitly parses explanation strings to guarantee that "actionable" directives (e.g. "BUY NOW", "EXECUTE LONG") are rejected, ensuring candidate outputs remain strictly conversational suggestions to the scoring engine.

### Execution Object Detection
The configuration asserts the complete omission of execution keywords across all output dictionaries, ensuring no `order_id` or equivalent execution intent accidentally seeps through payloads.

### Plugin Isolation
`StrategyEngine` restricts plugin evaluation into sandbox `try-except` blocks. Rogue plugins that raise faults or attempt to circumvent restrictions are halted silently and logged via warning mechanisms rather than bringing down the runtime.

## Signal Scoring Security & Safety (Phase 14)

Phase 14's signal scoring engine acts as a critical safety boundary between abstract strategy concepts and the eventual risk/execution layers. It guarantees that signals are purely informational, strictly normalized, and safe to evaluate.

- **Scored Signal is Not an Order:** A `ScoredSignalCandidate` is strictly a draft intent. It is never guaranteed to be executed.
- **Execution Threshold Deferred:** There are no configuration thresholds in this phase that automatically trigger a trade.
- **Risk Engine Required:** Phase 14 configuration actively enforces `risk_engine_required_before_execution=True` to prevent circumvention.
- **Order-like Language Guard:** Signal explanations are stringently parsed against a blacklist of actionable verbs ("buy now", "sell now", "execute", "long aç") to prevent misinterpretation by logs, dashboards, or NLP parsers.
- **Execution Field Blacklist:** The payloads produced by Phase 14 are systematically blocked from carrying any order-centric fields such as `order_id`, `quantity`, `leverage`, `stop_loss`, or `take_profit`.
- **Conflict Penalty & Safety:** Signals displaying high internal conflict (e.g. both bullish and bearish indicators on the same bar) are aggressively penalized to ensure ambiguity results in low scores, preventing reckless entries.
- **Single Plugin High Score Warning:** A high score generated by only one plugin lacking external confluence triggers safety warnings.
- **Financial Guarantees:** A signal with a 100/100 score represents mathematical confluence, not financial certainty. Calibration is solely for continuous model improvement, not a promise of yield.


## Phase 15: Regime Security Guardrails
- **Rejim sınıfı emir değildir:** Classifications reflect market context mapping, explicitly banning explicit orders or trading execution actions.
- **Regime leakage riskleri:** Classifications must purely rely on structurally completed and explicitly backward-looking information without forward returns.
- **Centered rolling yasağı:** Data leakage blocks prevent utilizing any pandas standard centered rolling mechanics.
- **Scaler full dataset fit yasağı:** ML boundaries strictly map training splits and prevent cross-dataset standardization leaks.
- **Optional model train split zorunluluğu:** Experimental models explicitly require chronological train splits.
- **Higher timeframe closed candle ilkesi:** Multi-timeframe structures rely on completely closed states.
- **Rejim flip/chop riskleri:** Overtrading is punished with stability grading boundaries reflecting high chop metrics safely.
- **Rejim confidence finansal garanti değildir:** Confidence maps mathematical alignments, completely detached from execution safety guarantees.
