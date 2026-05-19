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
