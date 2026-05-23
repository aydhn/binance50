import hashlib
import time
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.base import StrategyPluginProtocol
from binance50.strategies.candidates import deduplicate_candidates
from binance50.strategies.context import build_strategy_context
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStatus,
    StrategyRunMetadata,
    StrategyRunRequest,
    StrategyRunResult,
)
from binance50.strategies.quality import (
    assert_strategy_quality_passed,
    build_strategy_quality_report,
)
from binance50.strategies.registry import StrategyRegistry
from binance50.strategies.validators import validate_candidates, validate_strategy_input_dataframe


class StrategyEngine:
    def __init__(self, config: AppConfig, registry: StrategyRegistry, storage: Any | None = None):
        self.config = config
        self.registry = registry
        self.storage = storage

    def run(self, df: pd.DataFrame, request: StrategyRunRequest) -> StrategyRunResult:
        start_time = time.time()

        try:
            validate_strategy_input_dataframe(df, self.config)
        except Exception as e:
            from binance50.core.exceptions import StrategyInputError

            raise StrategyInputError(f"Input validation failed: {e}")

        # Filter warmup rows if needed
        if not self.config.strategies.warmup_rows_allowed and "is_warmup" in df.columns:
            df = df[~df["is_warmup"]].copy()

        if len(df) < self.config.strategies.min_rows_required:
            from binance50.core.exceptions import StrategyInputError

            raise StrategyInputError(
                f"Insufficient rows: {len(df)} < {self.config.strategies.min_rows_required}"
            )

        plugins = self.registry.list_plugins(enabled_only=True, config=self.config)
        if request.plugin_names:
            plugins = [p for p in plugins if p.name in request.plugin_names]

        if len(plugins) > self.config.strategies.max_plugins_per_run:
            from binance50.core.exceptions import StrategyConfigError

            raise StrategyConfigError(
                f"Too many plugins requested: {len(plugins)} > {self.config.strategies.max_plugins_per_run}"
            )

        all_candidates = []
        plugin_reports = {}

        input_hash = hashlib.sha256(pd.util.hash_pandas_object(df).values).hexdigest()

        for plugin in plugins:
            try:
                # Isolate context
                context = build_strategy_context(
                    config=self.config,
                    symbol=request.symbol,
                    market_scope=request.market_scope,
                    interval=request.interval,
                    plugin_name=plugin.name,
                    run_id=request.request_id,
                    correlation_id=request.correlation_id,
                    config_hash=input_hash,  # Just using input hash for determinism
                )

                cands = self.run_single_plugin(df, plugin, context)
                all_candidates.extend(cands)
                plugin_reports[plugin.name] = {"status": "success", "count": len(cands)}

            except Exception as e:
                # Isolate plugin failures
                plugin_reports[plugin.name] = {"status": "fail", "error": str(e)}

        # Deduplicate
        all_candidates = deduplicate_candidates(all_candidates)

        # Validate Bounds
        validate_candidates(all_candidates, self.config)

        # Quality Check
        quality_report = build_strategy_quality_report(all_candidates, self.config)
        try:
            assert_strategy_quality_passed(quality_report, self.config)
        except Exception as e:
            from binance50.core.exceptions import StrategyQualityError

            raise StrategyQualityError(str(e))

        active = [c for c in all_candidates if c.status == StrategyCandidateStatus.candidate]
        rejected = [c for c in all_candidates if c.status == StrategyCandidateStatus.rejected]

        # Hash output
        output_sig = f"{len(active)}_{len(rejected)}_{input_hash}"
        output_hash = hashlib.sha256(output_sig.encode()).hexdigest()

        metadata = StrategyRunMetadata(
            symbol=request.symbol,
            market_scope=request.market_scope,
            interval=request.interval,
            row_count=len(df),
            plugin_count=len(plugins),
            candidate_count=len(active),
            rejected_count=len(rejected),
            input_hash=input_hash,
            output_hash=output_hash,
            config_hash=input_hash,  # Using input hash as config hash placeholder
            generated_at_utc=int(time.time() * 1000),
            warnings=[
                f"Plugin {k} failed: {v['error']}"
                for k, v in plugin_reports.items()
                if v["status"] == "fail"
            ],
        )

        return StrategyRunResult(
            request=request,
            candidates=active,
            rejected_candidates=rejected,
            plugin_reports=plugin_reports,
            quality_report=quality_report,
            metadata=metadata,
            success=True,
        )

    def run_single_plugin(
        self, df: pd.DataFrame, plugin: StrategyPluginProtocol, context: Any
    ) -> list[SignalCandidate]:
        plugin.validate_input(df, self.config)
        return plugin.evaluate(df, context)

    def run_from_indicator_fixture(self, fixture_name: str) -> StrategyRunResult:
        # Placeholder for CLI fixture run
        pass

    def run_from_indicator_cache(self, request: StrategyRunRequest) -> StrategyRunResult:
        # Placeholder for cache run
        pass

    def run_from_warehouse(self, request: StrategyRunRequest) -> StrategyRunResult:
        pass

    def validate_input(self, df: pd.DataFrame) -> None:
        validate_strategy_input_dataframe(df, self.config)

    def build_metadata(self, result: StrategyRunResult) -> StrategyRunMetadata:
        return result.metadata

    def save_to_cache(self, result: StrategyRunResult) -> None:
        pass

    def save_to_warehouse(self, result: StrategyRunResult) -> None:
        pass
