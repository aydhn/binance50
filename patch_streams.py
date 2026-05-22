import re

with open('binance50/src/binance50/streams/replay.py', 'r') as f:
    content = f.read()

methods_to_add = """
def save_replay_events_to_warehouse(events: list, config: Any) -> Any:
    if not config.storage.enabled:
        return None
    from binance50.storage.importers import import_stream_events
    return import_stream_events(events, config)
"""

content = content + "\n" + methods_to_add

with open('binance50/src/binance50/streams/replay.py', 'w') as f:
    f.write(content)
