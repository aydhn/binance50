import re

with open("src/binance50/cli.py") as f:
    content = f.read()

import_statement = """
from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamType
from binance50.streams.subscription import build_subscription_plan
from binance50.streams.routing import build_full_stream_url
from binance50.streams.parser import parse_stream_payload
from binance50.streams.event_types import StreamSource
from binance50.streams.buffer import StreamBuffer
from binance50.streams.metrics import StreamMetricsCollector
from binance50.streams.simulator import StreamSimulator
from binance50.streams.replay import StreamReplayEngine
from binance50.streams.state import StreamStateStore
from binance50.safety.stream_guard import build_stream_safety_report, assert_real_stream_connect_allowed
from binance50.streams.reports import build_stream_health_report
from binance50.streams.models import StreamEvent
from binance50.streams.dispatcher import StreamDispatcher
from binance50.market_data.realtime_store import RealtimeMarketDataStore
"""

# Let's remove any previous bad imports
content = re.sub(r"from binance50\.core\.enums import MarketScope\n+", "", content)
content = re.sub(
    r"from binance50\.streams\.event_types import StreamType[\s\S]*?from binance50\.market_data\.realtime_store import RealtimeMarketDataStore",
    "",
    content,
)

lines = content.split("\n")
import_idx = 0
for i, line in enumerate(lines):
    if line.startswith("import") or line.startswith("from"):
        import_idx = i
lines.insert(import_idx + 1, import_statement)
content = "\n".join(lines)

with open("src/binance50/cli.py", "w") as f:
    f.write(content)
