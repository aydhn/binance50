from binance50.execution.audit import emit_execution_audit_event, build_execution_audit_timeline

def test_audit_event():
    event = emit_execution_audit_event("run1", "intent1", "test_event", "info", "test", {})
    assert event.event_id.startswith("audit_")
    timeline = build_execution_audit_timeline([event])
    assert len(timeline) == 1
    assert "created_at_utc" in timeline[0]
