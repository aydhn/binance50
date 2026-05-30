## Execution Safety Abstraction (Phase 28)

This pull request implements the Phase 28 execution safety abstraction layer for the binance50 project.

### Core Architecture
- Creates internal `ExecutionIntentDraft` model, structurally separated from real order representations.
- Establishes sandbox mode constraints where execution is explicitly forbidden and drafts cannot be sent to exchanges.
- Defines Execution Boundaries preventing direct flows from portfolio allocation into executable orders.

### Local Safety Enforcements
- Built local `BinanceFilterValidationConfig` to mock and check tick sizes, notional, and rounding rules via local fixtures without network requests.
- Integrated a comprehensive Payload Scanner that actively rejects payloads containing `api_key`, `secret`, `signature`, exchange identifiers (`orderId`, `clientOrderId`), and live endpoint references.
- Instantiated empty local Exchange Gateway skeletons configured to instantly reject executions.

### Execution Safeguards
- Configured a default-ON Global Kill Switch blocking intent promotions or downstream order executions.
- Embedded a Circuit Breaker capable of blocking runs emitting excessive errors or unsupported modes.
- Added 15+ dedicated Phase 28 Safety exceptions and Error Codes along with the respective routing logic.
- Complete CLI commands and health checks mapping Phase 28 metrics successfully via the `doctor` command.
- Verified entirely via `scripts/check_project.py` and 20+ execution specific unit tests ensuring zero actual exchange requests.
