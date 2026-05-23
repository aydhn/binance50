import pandas as pd
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import uuid

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorV2Error

from .pivots import PivotPoint
from .divergence import DivergenceSignalCandidate, detect_all_divergences, add_divergence_features
from .mtf import MTFAlignmentRequest, MTFAlignmentResult, align_higher_tf_to_base, prepare_higher_tf_features
from .pattern_base import PatternCandidate, IndicatorContext
from .pattern_registry import PatternRegistry
from .feature_registry import FeatureRegistry
from .feature_groups import build_feature_group_report, FeatureGroupReport, add_feature_group_metadata
from .feature_metadata import FeatureSetMetadata, build_feature_set_metadata
from .quality_v2 import FeatureQualityReport, build_feature_quality_report, assert_feature_quality_passed

class IndicatorV2RunRequest(BaseModel):
    symbol: str
    market_scope: str
    base_interval: str
    higher_intervals: List[str] = []
    feature_groups: List[str] = []
    include_divergence: bool = True
    include_mtf: bool = True
    include_patterns: bool = True
    request_id: str
    correlation_id: str

class IndicatorV2RunResult(BaseModel):
    request: Optional[IndicatorV2RunRequest] = None
    output_df: Optional[pd.DataFrame] = None
    feature_set_metadata: Optional[FeatureSetMetadata] = None
    quality_report: Optional[FeatureQualityReport] = None
    divergence_candidates: List[DivergenceSignalCandidate] = []
    mtf_alignment_reports: List[Dict[str, Any]] = []
    pattern_candidates: List[PatternCandidate] = []
    success: bool = False
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class IndicatorEngineV2:
    def __init__(self, config: AppConfig, feature_registry: FeatureRegistry, pattern_registry: PatternRegistry, indicator_engine_v1=None, storage=None):
        self.config = config
        self.indicator_engine_v1 = indicator_engine_v1
        self.feature_registry = feature_registry
        self.pattern_registry = pattern_registry
        self.storage = storage

    def compute_v2_features(self, base_df: pd.DataFrame, indicator_df: Optional[pd.DataFrame] = None, request: Optional[IndicatorV2RunRequest] = None) -> IndicatorV2RunResult:
        if not self.config.indicator_v2.enabled:
            return IndicatorV2RunResult(success=False, error="Indicator V2 is disabled in config")

        try:
            # 1. Start with indicator_df if provided, else compute V1
            df = indicator_df.copy() if indicator_df is not None else base_df.copy()

            # (If no indicator_df, we'd normally call self.indicator_engine_v1.compute)

            result = IndicatorV2RunResult(request=request, success=True)

            # 2. Divergence
            if request and request.include_divergence and self.config.indicator_v2.divergence.enabled:
                df = self.compute_divergence_features(df, result)

            # 3. MTF
            # Usually higher_tf_frames are fetched and passed, here we mock the signature
            # In a real workflow, MTF frames would be provided to this engine or fetched by it

            # 4. Pattern Skeleton
            if request and request.include_patterns and self.config.indicator_v2.patterns.enabled:
                df = self.compute_pattern_skeleton_features(df, result, request)

            # 5. Feature Groups & Metadata
            # Build feature group report
            group_report = build_feature_group_report(df, self.config)

            # 6. Quality V2
            quality_report = build_feature_quality_report(
                df,
                [c for c in df.columns if c not in ["open_time", "close_time", "symbol", "interval", "market_scope"]],
                self.config,
                self.feature_registry
            )
            assert_feature_quality_passed(quality_report, self.config)
            result.quality_report = quality_report

            # 7. Finalize Metadata
            meta = build_feature_set_metadata(df, self.config, {}, "config_hash", "output_hash")

            # Register them
            self.feature_registry.register_feature_set(meta)

            result.feature_set_metadata = meta

            # Add identifiers
            df['feature_set_id'] = meta.feature_set_id
            df['feature_config_hash'] = meta.config_hash
            df['generated_at_utc'] = meta.generated_at_utc

            result.output_df = df

            return result

        except Exception as e:
            return IndicatorV2RunResult(request=request, success=False, error=str(e))

    def compute_divergence_features(self, df: pd.DataFrame, result: IndicatorV2RunResult) -> pd.DataFrame:
        candidates = detect_all_divergences(df, self.config)
        result.divergence_candidates = candidates
        return add_divergence_features(df, candidates, self.config)

    def align_mtf_features(self, base_df: pd.DataFrame, higher_tf_frames: Dict[str, pd.DataFrame], request: IndicatorV2RunRequest, result: IndicatorV2RunResult) -> pd.DataFrame:
        df = base_df.copy()

        cfg = self.config.indicator_v2.mtf
        if not cfg.enabled:
            return df

        for interval, h_df in higher_tf_frames.items():
            if interval not in cfg.higher_intervals:
                continue

            from .mtf import compute_mtf_tolerance_ms, build_mtf_alignment_metadata

            tol_ms = compute_mtf_tolerance_ms(request.base_interval, interval, cfg.max_alignment_tolerance_bars)

            req = MTFAlignmentRequest(
                symbol=request.symbol,
                market_scope=request.market_scope,
                base_interval=request.base_interval,
                higher_interval=interval,
                base_df_hash="mock",
                higher_df_hash="mock",
                tolerance_ms=tol_ms,
                require_higher_tf_closed=cfg.require_higher_tf_closed,
                alignment_method=cfg.alignment_method
            )

            h_df_prep = prepare_higher_tf_features(h_df, interval, self.config)

            align_result = align_higher_tf_to_base(df, h_df_prep, req, self.config)

            df = align_result.aligned_df
            result.mtf_alignment_reports.append(build_mtf_alignment_metadata(align_result))

        return df

    def compute_pattern_skeleton_features(self, df: pd.DataFrame, result: IndicatorV2RunResult, request: IndicatorV2RunRequest) -> pd.DataFrame:
        context = IndicatorContext(config=self.config, symbol=request.symbol, interval=request.base_interval)
        candidates = self.pattern_registry.detect_all(df, context)
        result.pattern_candidates = candidates

        # In a real impl, add them as pat_ features
        df = df.copy()
        for cand in candidates:
            col_name = f"{self.config.indicator_v2.patterns.output_prefix}{cand.pattern_name}"
            if col_name not in df.columns:
                df[col_name] = 0.0

            # Usually candidate open_time maps to df index/open_time
            if 'open_time' in df.columns:
                idx = df.index[df['open_time'] == cand.open_time]
            else:
                idx = df.index[df.index == cand.open_time]

            if len(idx) > 0:
                df.loc[idx, col_name] = cand.strength

        return df
