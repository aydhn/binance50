import re

with open('binance50/src/binance50/cli.py', 'r') as f:
    content = f.read()

# Replace spot_kline_btcusdt_1m_closed.json with stream_events_btcusdt.json in streams check as an example if that exists. Let's see what's in data/fixtures/streams.
