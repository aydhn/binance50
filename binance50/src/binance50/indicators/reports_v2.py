from typing import Dict, Any, List
from binance50.config.models import AppConfig
from .engine_v2 import IndicatorV2RunResult
from .divergence import DivergenceSignalCandidate
from .mtf import MTFAlignmentResult, build_mtf_alignment_metadata
from .feature_groups import FeatureGroupReport
from .pattern_registry import PatternRegistry

def build_indicator_v2_summary(result: IndicatorV2RunResult) -> Dict[str, Any]:
    if not result.success:
        return {
            "status": "fail",
            "error": result.error,
            "request_id": result.request.request_id if result.request else None
        }

    return {
        "status": "success",
        "request_id": result.request.request_id if result.request else None,
        "feature_set_id": result.feature_set_metadata.feature_set_id if result.feature_set_metadata else None,
        "feature_count": result.feature_set_metadata.feature_count if result.feature_set_metadata else 0,
        "divergence_candidates": len(result.divergence_candidates),
        "pattern_candidates": len(result.pattern_candidates),
        "mtf_alignments": len(result.mtf_alignment_reports),
        "quality_status": result.quality_report.status if result.quality_report else "unknown"
    }

def build_divergence_report(candidates: List[DivergenceSignalCandidate]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for c in candidates:
        counts[c.divergence_type.value] = counts.get(c.divergence_type.value, 0) + 1

    return {
        "total_candidates": len(candidates),
        "counts_by_type": counts,
        "trade_signal": False,
        "note": "Divergence candidates are not trade signals."
    }

def build_mtf_alignment_report(results: List[MTFAlignmentResult]) -> Dict[str, Any]:
    reports = []
    total_matched = 0
    total_unmatched = 0

    for r in results:
        meta = build_mtf_alignment_metadata(r)
        reports.append(meta)
        total_matched += meta["matched"]
        total_unmatched += meta["unmatched"]

    return {
        "alignments": reports,
        "total_matched": total_matched,
        "total_unmatched": total_unmatched
    }

def build_feature_group_report_view(report: FeatureGroupReport) -> Dict[str, Any]:
    return {
        "total_features": report.total_features,
        "grouped_features": report.grouped_features,
        "ungrouped_features": report.ungrouped_features,
        "group_counts": {g: len(c) for g, c in report.groups.items()}
    }

def build_pattern_availability_report(pattern_registry: PatternRegistry) -> Dict[str, Any]:
    return pattern_registry.availability_report()

def build_indicator_v2_health_report(config: AppConfig, feature_registry=None, pattern_registry=None) -> Dict[str, Any]:
    cfg = config.indicator_v2
    return {
        "enabled": cfg.enabled,
        "pivots": {
            "enabled": cfg.pivots.enabled,
            "repainting_allowed": cfg.pivots.allow_repainting,
            "centered_window": cfg.pivots.use_centered_window
        },
        "divergence": {
            "enabled": cfg.divergence.enabled,
            "detect_regular": cfg.divergence.detect_regular,
            "detect_hidden": cfg.divergence.detect_hidden
        },
        "mtf": {
            "enabled": cfg.mtf.enabled,
            "alignment_method": cfg.mtf.alignment_method,
            "disallow_forward": cfg.mtf.disallow_forward_alignment
        },
        "patterns": {
            "enabled": cfg.patterns.enabled,
            "native_skeleton": cfg.patterns.native_pattern_skeleton_enabled,
            "talib_adapter": cfg.patterns.talib_pattern_adapter_enabled
        },
        "registries": {
            "features": feature_registry.to_report() if feature_registry else None,
            "patterns": pattern_registry.availability_report() if pattern_registry else None
        }
    }
