import datetime
import hashlib
import json

from binance50.config.models import AppConfig
from binance50.signals.confluence import ConfluenceEngine
from binance50.signals.models import SignalScoringMetadata, SignalScoringRequest, SignalScoringResult
from binance50.signals.quality import build_signal_quality_report
from binance50.signals.scoring import SignalScoringEngine
from binance50.strategies.models import SignalCandidate, StrategyRunResult


class SignalEngine:
    def __init__(self, config: AppConfig, storage=None):
        self.config = config
        self.confluence_engine = ConfluenceEngine(config)
        self.scoring_engine = SignalScoringEngine(config, confluence_engine=self.confluence_engine)
        self.storage = storage

        class MockAudit:
            def log(self, *args, **kwargs): pass
        self.audit = MockAudit()

    def validate_input(self, candidates: list[SignalCandidate]) -> None:
        """Validate the input candidates."""
        from binance50.signals.validators import validate_signal_candidates
        validate_signal_candidates(candidates, self.config)

    def _generate_hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def build_metadata(self, request: SignalScoringRequest, scored: list, rejected: list, groups: list, config_hash: str) -> SignalScoringMetadata:
        input_data = "".join([c.source_candidate_id for c in scored + rejected])
        output_data = "".join([c.scored_signal_id for c in scored])

        return SignalScoringMetadata(
            symbol=request.symbol,
            market_scope=request.market_scope,
            interval=request.interval,
            input_candidate_count=len(scored) + len(rejected),
            scored_candidate_count=len(scored),
            rejected_candidate_count=len(rejected),
            confluence_group_count=len(groups),
            conflict_count=sum(1 for s in scored if s.conflicted),
            input_hash=self._generate_hash(input_data),
            output_hash=self._generate_hash(output_data),
            config_hash=config_hash,
            generated_at_utc=int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
        )

    def run(self, candidates: list[SignalCandidate], request: SignalScoringRequest) -> SignalScoringResult:
        try:
            self.audit.log("signal_scoring_started", {"request_id": request.request_id})

            self.validate_input(candidates)

            scored_results = self.scoring_engine.score_candidates(candidates)

            scored = [s for s in scored_results if s.status != "rejected"]
            rejected = [s for s in scored_results if s.status == "rejected"]

            confluence_groups = self.confluence_engine.build_confluence_groups(candidates, self.config)

            quality_report = build_signal_quality_report(scored, self.config)

            from binance50.signals.quality import assert_signal_quality_passed
            assert_signal_quality_passed(quality_report, self.config)

            config_hash = self._generate_hash(json.dumps(self.config.signals.model_dump(), sort_keys=True))
            metadata = self.build_metadata(request, scored, rejected, confluence_groups, config_hash)

            result = SignalScoringResult(
                request=request,
                scored_candidates=scored,
                rejected_candidates=rejected,
                confluence_groups=confluence_groups,
                quality_report=quality_report,
                metadata=metadata,
                success=True
            )

            self.audit.log("signal_scoring_completed", {"scored_count": len(scored)})

            if self.config.signals.cache_enabled:
                self.save_to_cache(result)

            return result

        except Exception as e:
            self.audit.log("signal_scoring_failed", {"error": str(e)}, severity="error")

            return SignalScoringResult(
                request=request,
                metadata=SignalScoringMetadata(
                    symbol=request.symbol, market_scope=request.market_scope, interval=request.interval,
                    input_candidate_count=len(candidates), scored_candidate_count=0, rejected_candidate_count=len(candidates),
                    confluence_group_count=0, conflict_count=0, input_hash="", output_hash="", config_hash="",
                    generated_at_utc=int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
                ),
                success=False,
                error=str(e)
            )

    def run_from_strategy_result(self, strategy_result: StrategyRunResult) -> SignalScoringResult:
        req = SignalScoringRequest(
            symbol=strategy_result.request.symbol,
            market_scope=strategy_result.request.market_scope,
            interval=strategy_result.request.interval,
            candidate_dataset_name=self.config.strategies.output_dataset_name,
            plugin_names=strategy_result.request.plugin_names,
            start_time_ms=strategy_result.request.start_time_ms,
            end_time_ms=strategy_result.request.end_time_ms,
            request_id=strategy_result.request.request_id,
            correlation_id=strategy_result.request.correlation_id
        )
        return self.run(strategy_result.candidates, req)

    def save_to_cache(self, result: SignalScoringResult) -> None:
        from binance50.signals.cache import save_signal_result
        save_signal_result(result, self.config)
