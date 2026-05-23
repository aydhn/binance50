with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

signal_models = """
class SignalScoringRulesConfig(BaseModel):
    min_score: float = Field(default=0.0)
    max_score: float = Field(default=100.0)
    default_no_action_score: float = Field(default=0.0)
    confidence_normalization: Literal["linear_0_100"] = Field(default="linear_0_100")
    clamp_scores: bool = Field(default=True)
    round_scores_decimals: int = Field(default=4, ge=0)
    score_tiers: dict[str, tuple[float, float]] = Field(
        default_factory=lambda: {
            "very_low": (0.0, 20.0),
            "low": (20.0, 40.0),
            "medium": (40.0, 60.0),
            "high": (60.0, 80.0),
            "very_high": (80.0, 100.0)
        }
    )
    min_score_for_research_candidate: float = Field(default=50.0)
    min_score_for_risk_review: float = Field(default=65.0)
    min_score_for_future_backtest_candidate: float = Field(default=70.0)

    @model_validator(mode="after")
    def validate_scores(self) -> "SignalScoringRulesConfig":
        if self.min_score >= self.max_score:
            raise ValueError("min_score must be less than max_score")
        return self


class SignalConfluenceConfig(BaseModel):
    enabled: bool = Field(default=True)
    same_direction_bonus_per_plugin: float = Field(default=5.0)
    max_same_direction_bonus: float = Field(default=20.0)
    require_distinct_plugin_types: bool = Field(default=True)
    plugin_type_diversity_bonus: float = Field(default=5.0)
    trend_volume_confirmation_bonus: float = Field(default=5.0)
    mtf_confirmation_bonus: float = Field(default=5.0)
    divergence_confirmation_bonus: float = Field(default=3.0)
    pattern_confirmation_bonus: float = Field(default=1.0)
    max_confluence_score: float = Field(default=100.0)
    min_plugins_for_confluence: int = Field(default=2, ge=1)


class SignalConflictConfig(BaseModel):
    enabled: bool = Field(default=True)
    detect_opposite_direction_same_bar: bool = Field(default=True)
    detect_same_plugin_opposite_direction: bool = Field(default=True)
    bearish_bullish_conflict_penalty: float = Field(default=20.0)
    same_plugin_conflict_penalty: float = Field(default=30.0)
    max_conflict_penalty: float = Field(default=50.0, ge=0.0)
    keep_conflicted_candidates: bool = Field(default=True)
    mark_conflicted_candidates: bool = Field(default=True)


class SignalFreshnessConfig(BaseModel):
    enabled: bool = Field(default=True)
    default_expiry_bars: int = Field(default=3, ge=1)
    max_expiry_bars: int = Field(default=50, ge=1)
    score_decay_mode: Literal["linear", "step"] = Field(default="linear")
    expired_score_multiplier: float = Field(default=0.0, ge=0.0, le=1.0)
    stale_score_multiplier: float = Field(default=0.5, ge=0.0, le=1.0)
    current_bar_multiplier: float = Field(default=1.0, ge=0.0, le=1.0)


class SignalCalibrationConfig(BaseModel):
    enabled: bool = Field(default=True)
    mode: Literal["placeholder_metrics_only"] = Field(default="placeholder_metrics_only")
    require_backtest_before_live_calibration: bool = Field(default=True)
    brier_score_supported: bool = Field(default=True)
    reliability_bins: int = Field(default=10, ge=2, le=50)
    expected_calibration_error_supported: bool = Field(default=True)
    calibration_training_deferred: bool = Field(default=True)

    @field_validator("calibration_training_deferred")
    def validate_deferred(cls, v: bool) -> bool:
        if not v:
            raise ValueError("calibration_training_deferred must be True in Phase 14")
        return v


class SignalThresholdConfig(BaseModel):
    enabled: bool = Field(default=True)
    no_action_below: float = Field(default=40.0)
    research_candidate_min: float = Field(default=50.0)
    risk_review_min: float = Field(default=65.0)
    future_backtest_candidate_min: float = Field(default=70.0)
    execution_threshold_deferred: bool = Field(default=True)

    @field_validator("execution_threshold_deferred")
    def validate_deferred(cls, v: bool) -> bool:
        if not v:
            raise ValueError("execution_threshold_deferred must be True in Phase 14")
        return v


class SignalQualityConfig(BaseModel):
    reject_empty_scored_set: bool = Field(default=False)
    warn_empty_scored_set: bool = Field(default=True)
    reject_score_out_of_range: bool = Field(default=True)
    reject_missing_breakdown: bool = Field(default=True)
    reject_missing_explanation: bool = Field(default=True)
    reject_order_language: bool = Field(default=True)
    reject_execution_intent: bool = Field(default=True)
    warn_high_conflict_ratio: bool = Field(default=True)
    max_conflict_ratio: float = Field(default=0.50, ge=0.0, le=1.0)
    warn_single_plugin_high_score: bool = Field(default=True)
    max_single_plugin_score_without_confluence: float = Field(default=70.0)


class SignalsConfig(BaseModel):
    enabled: bool = Field(default=True)
    output_dataset_name: str = Field(default="scored_signal_candidates")
    cache_enabled: bool = Field(default=True)
    cache_dir: str = Field(default="data/signals")
    export_dir: str = Field(default="data/signals/exports")
    execution_forbidden: bool = Field(default=True)
    order_creation_forbidden: bool = Field(default=True)
    paper_trade_forbidden: bool = Field(default=True)
    backtest_forbidden: bool = Field(default=True)
    live_trade_forbidden: bool = Field(default=True)
    risk_engine_required_before_execution: bool = Field(default=True)
    require_explanations: bool = Field(default=True)
    require_score_breakdown: bool = Field(default=True)
    require_candidate_intent_no_order: bool = Field(default=True)
    reject_order_like_language: bool = Field(default=True)
    reject_execution_fields: bool = Field(default=True)
    reject_future_columns: bool = Field(default=True)
    reject_target_columns: bool = Field(default=True)
    reject_label_columns: bool = Field(default=True)
    warmup_candidates_allowed: bool = Field(default=False)

    scoring: SignalScoringRulesConfig = Field(default_factory=SignalScoringRulesConfig)
    plugin_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "trend_following": 1.00,
            "mean_reversion": 0.85,
            "momentum_continuation": 0.90,
            "volatility_breakout": 0.80,
            "volume_confirmation": 0.60,
            "divergence_candidate": 0.75,
            "mtf_confirmation": 0.70,
            "pattern_candidate": 0.35,
            "composite_skeleton": 0.50
        }
    )
    component_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "candidate_confidence": 0.35,
            "plugin_weighted_score": 0.20,
            "confluence": 0.20,
            "confirmation": 0.10,
            "freshness": 0.05,
            "data_quality": 0.10,
            "conflict_penalty": -0.20
        }
    )
    confluence: SignalConfluenceConfig = Field(default_factory=SignalConfluenceConfig)
    conflicts: SignalConflictConfig = Field(default_factory=SignalConflictConfig)
    freshness: SignalFreshnessConfig = Field(default_factory=SignalFreshnessConfig)
    calibration: SignalCalibrationConfig = Field(default_factory=SignalCalibrationConfig)
    thresholds: SignalThresholdConfig = Field(default_factory=SignalThresholdConfig)
    quality: SignalQualityConfig = Field(default_factory=SignalQualityConfig)

    @field_validator(
        "execution_forbidden",
        "order_creation_forbidden",
        "live_trade_forbidden",
        "backtest_forbidden",
        "paper_trade_forbidden",
        "risk_engine_required_before_execution"
    )
    def validate_forbidden(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"{info.field_name} must be True in Phase 14")
        return v

    @field_validator("plugin_weights")
    def validate_plugin_weights(cls, v: dict[str, float]) -> dict[str, float]:
        for weight in v.values():
            if weight < 0.0 or weight > 5.0:
                raise ValueError("plugin weights must be between 0.0 and 5.0")
        return v

class AppConfig(BaseModel):
"""

content = content.replace("class AppConfig(BaseModel):", signal_models)
with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)
