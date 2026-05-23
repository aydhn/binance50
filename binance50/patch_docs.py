with open("docs/ARCHITECTURE.md", "a") as f:
    f.write("\n## WebSocket Market Stream Layer\n")
    f.write("- **Stream Subscription Plan**: Generates stream paths and payload models offline.\n")
    f.write(
        "- **Stream Parser**: Deserializes raw string payloads into strongly-typed Pydantic event models.\n"
    )
    f.write(
        "- **Stream Buffer**: Implements max capacity and drop policies (e.g., `reject_new`) for event queues.\n"
    )
    f.write(
        "- **Stream Simulator/Replay**: Loads offline JSON fixtures, executes pipeline steps sequentially, validating parsing and buffer handling without actual network.\n"
    )
    f.write("- **Lifecycle**: Tracks reconnection timers, ping/pong delays offline.\n")
    f.write(
        "\n**Why Phase 9 lacks real WS connections**: We must first ensure we can robustly model, digest, test, limit-check, and safeguard streams entirely offline to prevent rate-limit bans or stale data processing bugs in production.\n"
    )

with open("docs/SECURITY.md", "a") as f:
    f.write("\n## WebSocket Limits & Safety\n")
    f.write("- Limit tracking ensures no more than 1024 streams per spot connection.\n")
    f.write(
        "- Stream connections are strictly blocked by `stream_guard` if `market_stream_real_connect_enabled` is false.\n"
    )
    f.write("- User Data Streams and Private Routes are completely locked out in Phase 9.\n")

with open("docs/PHASE_PLAN.md") as f:
    content = f.read()

content = content.replace(
    "- Phase 9: [Pending] WebSocket market stream models, parsers, plan, buffer, dispatcher, offline simulator.",
    "- Phase 9: [Completed] WebSocket market stream hattı; kline/ticker/bookTicker/depth/trade stream modelleri, subscription plan, buffer, parser, simulator ve realtime store ile kurulur.",
)

if "Phase 10:" not in content:
    content += "\n- Phase 10: [Pending] Lokal veri ambarı, parquet/sqlite partition yönetimi, veri katalogu ve veri kalite indeksleri kurulacak.\n"

with open("docs/PHASE_PLAN.md", "w") as f:
    f.write(content)

with open("README.md", "a") as f:
    f.write("\n## WebSocket Market Stream Layer\n")
    f.write(
        "Phase 9 provides robust offline simulation and structural preparation for real-time WebSocket market data. Real websocket connections are intentionally disabled by default.\n"
    )
    f.write("Test commands include:\n")
    f.write("- `python -m binance50.cli stream-simulate`\n")
    f.write("- `python -m binance50.cli stream-buffer-test`\n")
