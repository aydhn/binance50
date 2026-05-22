with open("binance50/config/default.yaml", "r") as f:
    content = f.read()

streams_config = """
streams:
  enabled: true
  market_stream_real_connect_enabled: false
  use_combined_streams: true
  default_stream_types:
    - kline
    - bookTicker
    - miniTicker
  allowed_stream_types:
    - kline
    - miniTicker
    - ticker
    - bookTicker
    - partialDepth
    - diffDepth
    - trade
    - aggTrade
    - markPrice
    - forceOrder
  default_kline_interval: 1m
  allowed_kline_intervals:
    - 1m
    - 3m
    - 5m
    - 15m
    - 30m
    - 1h
    - 2h
    - 4h
    - 6h
    - 8h
    - 12h
    - 1d
    - 3d
    - 1w
    - 1M
  max_symbols_per_stream_plan: 20
  max_streams_per_connection_spot: 1024
  max_streams_per_connection_usdm: 1024
  max_control_messages_per_second_spot: 5
  max_control_messages_per_second_usdm: 10
  buffer_max_events: 10000
  buffer_drop_policy: reject_new
  buffer_warn_threshold_pct: 80.0
  stale_event_threshold_seconds: 30
  max_event_time_skew_ms: 5000
  require_monotonic_event_time: false
  detect_duplicate_events: true
  duplicate_cache_size: 5000
  replay_enabled: true
  replay_speed_multiplier: 1.0
  realtime_store_enabled: true
  persist_realtime_snapshots: false
  lifecycle:
    max_connection_lifetime_hours: 24
    reconnect_before_disconnect_minutes: 10
    ping_timeout_seconds: 60
    pong_timeout_seconds: 600
    reconnect_backoff_initial_seconds: 1.0
    reconnect_backoff_max_seconds: 60.0
"""

if "streams:" not in content:
    with open("binance50/config/default.yaml", "w") as f:
        f.write(content.rstrip() + "\n" + streams_config)
