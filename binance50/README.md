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
