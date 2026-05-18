# binance50

A secure, disciplined, Python-based cryptocurrency algorithmic trading bot designed exclusively for Binance.

## Purpose
This project aims to build a realistic, low/medium frequency trading system that works in typical home environments (like a standard Windows PC with wired internet). It is not High-Frequency Trading (HFT). The focus is on finding a limited number of high-quality trading opportunities with strict risk management.

**Key Design Choices:**
- **Binance-only:** Specialized for Binance spot/futures.
- **Python-only:** Developed purely in Python, without relying on dashboards, HTML/web scraping, or browser automation.
- **No Paid APIs:** Zero budget operations. No Twitter API, no OpenAI API, no paid data services.
- **Secure by Default:** Live trading is strictly disabled by default. The progression is always: Backtest → Paper Trading → Testnet/Demo → Live Trading.
- **Telegram Notifications:** Operational updates and alerts will be sent via Telegram.
- **Audit & Discipline:** No black boxes. Every critical action is logged safely.

## Quickstart

1. Set up the virtual environment:
   `python -m venv .venv`

2. Activate the virtual environment:
   - On Windows: `.venv\Scripts\activate`
   - On macOS/Linux: `source .venv/bin/activate`

3. Install dependencies:
   `pip install -r requirements.txt`
   `pip install -r requirements-dev.txt`

4. Run the project doctor to verify the setup:
   `python -m binance50.cli doctor`

5. Run tests:
   `pytest`
