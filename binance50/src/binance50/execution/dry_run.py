import uuid
from datetime import datetime, timezone

from binance50.config.models import AppConfig

from .boundaries import build_execution_boundary_report
from .filters import build_filter_validation_report, load_symbol_filters_from_cache
from .models import ExecutionDryRunResult, ExecutionIntentDraft
from .notional import build_notional_report
from .payloads import scan_payload_for_forbidden_fields
from .rounding import build_rounding_report


class ExecutionDryRunValidator:
    def __init__(self, config: AppConfig):
        self.config = config

    def run_dry_validation(self, intent: ExecutionIntentDraft, payload: dict) -> ExecutionDryRunResult:
        # Dry-run validation is purely local and does not touch the network
        f_rep = self.run_filter_validation(intent)
        r_rep = self.run_rounding_validation(intent)
        n_rep = self.run_notional_validation(intent)
        p_rep = self.run_payload_safety_validation(intent, payload)
        b_rep = self.run_boundary_validation(intent, payload)

        passed = (
            f_rep.validation_passed
            and n_rep.passed
            and p_rep.passed
            and b_rep.get("passed", False)
        )

        warnings = f_rep.warnings + r_rep.warnings + n_rep.warnings + b_rep.get("violations", [])

        return ExecutionDryRunResult(
            dry_run_id=f"dry_{uuid.uuid4().hex}",
            intent_id=intent.intent_id,
            passed=passed,
            filter_validation_report=f_rep.__dict__,
            notional_validation_report=n_rep.__dict__,
            rounding_report=r_rep.__dict__,
            payload_safety_report=p_rep.__dict__,
            boundary_report=b_rep,
            warnings=warnings,
            metadata={},
            generated_at_utc=datetime.now(timezone.utc)
        )

    def run_filter_validation(self, intent: ExecutionIntentDraft):
        snapshot = load_symbol_filters_from_cache(intent.symbol, self.config)
        return build_filter_validation_report(intent, snapshot, self.config)

    def run_rounding_validation(self, intent: ExecutionIntentDraft):
        snapshot = load_symbol_filters_from_cache(intent.symbol, self.config)
        return build_rounding_report(intent, snapshot, self.config)

    def run_notional_validation(self, intent: ExecutionIntentDraft):
        snapshot = load_symbol_filters_from_cache(intent.symbol, self.config)
        return build_notional_report(intent, snapshot, self.config)

    def run_payload_safety_validation(self, intent: ExecutionIntentDraft, payload: dict):
        scan = scan_payload_for_forbidden_fields(payload, intent.intent_id, self.config)
        return scan

    def run_boundary_validation(self, intent: ExecutionIntentDraft, payload: dict):
        return build_execution_boundary_report(payload, self.config)

    def build_dry_run_report(self, result: ExecutionDryRunResult) -> dict:
        data = result.__dict__.copy()
        data["generated_at_utc"] = data["generated_at_utc"].isoformat()
        return data
