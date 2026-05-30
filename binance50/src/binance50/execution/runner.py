import uuid
from typing import Any

from binance50.config.models import AppConfig
from .audit import build_execution_audit_timeline, emit_execution_audit_event
from .boundaries import build_execution_boundary_report
from .circuit_breaker import build_circuit_breaker_report, check_max_intents_per_run
from .dry_run import ExecutionDryRunValidator
from .intents import ExecutionIntentBuilder
from .kill_switch import build_kill_switch_report
from .models import ExecutionSafetyRunRequest, ExecutionSafetyRunResult
from .quality import build_execution_quality_report
from .reproducibility import build_execution_reproducibility_report


class ExecutionSafetyRunner:
    def __init__(self, config: AppConfig):
        self.config = config
        self.intent_builder = ExecutionIntentBuilder()
        self.dry_run_validator = ExecutionDryRunValidator(config)

    def run(self, request: ExecutionSafetyRunRequest, source_items: list[dict] = None) -> ExecutionSafetyRunResult:
        run_id = f"exec_run_{uuid.uuid4().hex}"

        # 1. Load source result (Mocking for now, normally loads from storage)
        if source_items is None:
            source_items = [{"symbol": request.symbol, "side": "buy", "hypothetical_notional_usdt": 1000.0}]

        # 2. Build intents
        intents = [self.intent_builder.build_sandbox_intent_draft(item, self.config) for item in source_items]

        # 3. Circuit breaker check
        try:
            check_max_intents_per_run(intents, self.config)
        except Exception as e:
            return self._build_failed_result(request, run_id, str(e))

        # 4. Safety Scans and Dry Runs
        scans = []
        dry_runs = []
        for intent in intents:
            # mock payload
            payload = {"symbol": intent.symbol, "side": intent.side.value}
            scans.append(self.dry_run_validator.run_payload_safety_validation(intent, payload))
            dry_runs.append(self.dry_run_validator.run_dry_validation(intent, payload))

        # 5. Build Reports
        b_report = build_execution_boundary_report({}, self.config)
        k_report = build_kill_switch_report(self.config)
        c_report = build_circuit_breaker_report(intents, scans, self.config)

        result = ExecutionSafetyRunResult(
            request=request,
            run_id=run_id,
            intents=intents,
            safety_scans=scans,
            dry_run_results=dry_runs,
            boundary_report=b_report,
            kill_switch_report=k_report.__dict__,
            circuit_breaker_report=c_report.__dict__,
            quality_report={},
            reproducibility_report={},
            metadata={},
            success=True,
            error=None
        )

        result.quality_report = build_execution_quality_report(result, self.config).__dict__
        result.reproducibility_report = build_execution_reproducibility_report(result, self.config)

        # Audit event
        emit_execution_audit_event(run_id, "N/A", "execution_safety_run_completed", "info", "Run completed successfully", {})

        return result

    def _build_failed_result(self, request: ExecutionSafetyRunRequest, run_id: str, error: str) -> ExecutionSafetyRunResult:
        return ExecutionSafetyRunResult(
            request=request,
            run_id=run_id,
            intents=[],
            safety_scans=[],
            dry_run_results=[],
            boundary_report={},
            kill_switch_report={},
            circuit_breaker_report={},
            quality_report={},
            reproducibility_report={},
            metadata={},
            success=False,
            error=error
        )
