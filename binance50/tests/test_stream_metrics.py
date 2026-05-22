from binance50.streams.metrics import StreamMetricsCollector
from binance50.streams.models import StreamParseResult


def test_stream_metrics():
    coll = StreamMetricsCollector()
    res = StreamParseResult(success=False, error="test")
    coll.record_parse_result(res)

    snap = coll.snapshot()
    assert snap.total_events == 1
    assert snap.invalid_events == 1
    assert snap.parsed_events == 0
