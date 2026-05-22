from pathlib import Path

file_path = Path("README.md")
content = file_path.read_text()

readme_add = """
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
"""

if "## Indicator Engine" not in content:
    content += "\n" + readme_add

file_path.write_text(content)
print("Patched README.md")
