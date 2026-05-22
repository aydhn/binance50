import json

data = []
t = 1672531140000
for i in range(120):
    data.append({
        "open_time": t + (i * 60000),
        "open": 16500.0 + i,
        "high": 16520.0 + i,
        "low": 16490.0 + i,
        "close": 16510.0 + i,
        "volume": 100.5,
        "close_time": t + (i * 60000) + 59999,
        "quote_asset_volume": 1650000.0,
        "number_of_trades": 100,
        "taker_buy_base_asset_volume": 50.25,
        "taker_buy_quote_asset_volume": 825000.0,
        "is_closed": True
    })

with open("src/binance50/data/fixtures/ohlcv/ohlcv_spot_btcusdt_1m_sample.json", "w") as f:
    json.dump(data, f)
