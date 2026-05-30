from binance50.app import load_config as get_config
from binance50.execution.quality import build_execution_quality_report, assert_execution_quality_passed
from binance50.execution.models import ExecutionSafetyRunResult, ExecutionSafetyRunRequest

def test_execution_quality_passed():
    config = get_config()
    req = ExecutionSafetyRunRequest("BTC", "spot", "1m", "run1", "req1", "corr1")
    result = ExecutionSafetyRunResult(
        request=req, run_id="1", intents=[], safety_scans=[], dry_run_results=[],
        boundary_report={}, kill_switch_report={}, circuit_breaker_report={},
        quality_report={}, reproducibility_report={}, metadata={}, success=True, error=None
    )
    report = build_execution_quality_report(result, config)
    assert report.status == "passed"
    assert_execution_quality_passed(report, config)
