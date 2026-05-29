import re

with open("binance50/src/binance50/config/models.py", "r") as f:
    content = f.read()

# First, remove the previously inserted incorrect line if it exists
content = content.replace("class AppConfig(BaseModel):\n    portfolio_sandbox: PortfolioSandboxConfig = Field(default_factory=PortfolioSandboxConfig)", "class AppConfig(BaseModel):")

new_models = """
class PortfolioSandboxInputConfig(BaseModel):
    use_scored_signals: bool = True
    use_risk_assessments: bool = True
    use_ml_blended_candidates: bool = True
    use_regime_context: bool = True
    require_at_least_one_candidate_source: bool = True
    require_risk_context: bool = False
    require_ml_blend_context: bool = False
    allow_missing_ml_with_penalty: bool = True
    allow_missing_risk_with_penalty: bool = True
    reject_execution_fields: bool = True
    reject_live_paper_intent: bool = True

class PortfolioCandidateNormalizationConfig(BaseModel):
    score_min: float = 0.0
    score_max: float = 100.0
    probability_min: float = 0.0
    probability_max: float = 1.0
    normalize_ml_probability_to_score: bool = True
    normalize_signal_score: bool = True
    normalize_risk_score: bool = True
    require_explanation: bool = True
    require_source_trace: bool = True

class PortfolioEligibilityConfig(BaseModel):
    enabled: bool = True
    min_signal_score: float = 60.0
    min_risk_score: float = 50.0
    min_ml_blend_score: float = 50.0
    allow_research_only_candidates: bool = True
    reject_blocked_risk: bool = True
    reject_missing_symbol: bool = True
    reject_missing_interval: bool = True
    reject_missing_direction: bool = True
    reject_stale_candidates: bool = True
    max_candidate_age_bars: int = 3
    reject_duplicate_symbol_direction_bar: bool = True

class PortfolioCorrelationConfig(BaseModel):
    enabled: bool = True
    method: str = "pearson"
    allowed_methods: list[str] = Field(default_factory=lambda: ["pearson", "spearman", "kendall"])
    lookback_bars: int = 500
    min_periods: int = 100
    use_returns: bool = True
    return_column: str = "close"
    reject_forward_returns: bool = True
    reject_future_columns: bool = True
    max_abs_pair_correlation_warning: float = 0.80
    max_abs_pair_correlation_block: float = 0.95
    missing_correlation_policy: str = "penalty"
    correlation_penalty: float = 15.0

    @model_validator(mode="after")
    def validate_correlation_config(self) -> "PortfolioCorrelationConfig":
        if self.lookback_bars <= self.min_periods:
            raise ValueError("lookback_bars must be greater than min_periods")
        if self.max_abs_pair_correlation_block < self.max_abs_pair_correlation_warning:
            raise ValueError("block threshold cannot be lower than warning threshold")
        return self

class PortfolioSimilarityConfig(BaseModel):
    enabled: bool = True
    use_cosine_similarity_for_candidate_vectors: bool = True
    similarity_threshold_warning: float = 0.85
    similarity_threshold_block: float = 0.95
    include_score_vector: list[str] = Field(default_factory=lambda: [
        "signal_score", "risk_score", "ml_blend_score", "regime_score", "volatility_risk", "liquidity_risk"
    ])
    missing_vector_policy: str = "warning"

class PortfolioExposureConfig(BaseModel):
    enabled: bool = True
    mode: str = "hypothetical_only"
    starting_equity_usdt: float = 1000.0
    max_total_hypothetical_exposure_pct: float = 30.0
    max_symbol_hypothetical_exposure_pct: float = 10.0
    max_directional_exposure_pct: float = 20.0
    max_candidates_selected: int = 5
    max_candidates_per_symbol: int = 1
    max_candidates_per_interval: int = 5
    max_candidates_same_direction: int = 4
    default_candidate_notional_usdt: float = 50.0
    use_risk_hypothetical_notional_if_available: bool = True
    real_balance_fetch_forbidden: bool = True

    @model_validator(mode="after")
    def validate_exposure_config(self) -> "PortfolioExposureConfig":
        if not (0.0 <= self.max_total_hypothetical_exposure_pct <= 100.0):
            raise ValueError("max_total_hypothetical_exposure_pct must be between 0 and 100")
        if not (0.0 <= self.max_symbol_hypothetical_exposure_pct <= 100.0):
            raise ValueError("max_symbol_hypothetical_exposure_pct must be between 0 and 100")
        if not (0.0 <= self.max_directional_exposure_pct <= 100.0):
            raise ValueError("max_directional_exposure_pct must be between 0 and 100")
        if self.max_candidates_selected < 1:
            raise ValueError("max_candidates_selected must be at least 1")
        return self

class PortfolioConcentrationConfig(BaseModel):
    enabled: bool = True
    max_single_symbol_weight_pct: float = 20.0
    max_top_3_symbol_weight_pct: float = 60.0
    max_same_regime_ratio: float = 0.80
    max_same_direction_ratio: float = 0.80
    max_same_strategy_plugin_ratio: float = 0.70
    concentration_penalty: float = 20.0
    warn_high_concentration: bool = True

    @model_validator(mode="after")
    def validate_concentration_config(self) -> "PortfolioConcentrationConfig":
        if not (0.0 <= self.max_same_regime_ratio <= 1.0):
            raise ValueError("max_same_regime_ratio must be between 0 and 1")
        if not (0.0 <= self.max_same_direction_ratio <= 1.0):
            raise ValueError("max_same_direction_ratio must be between 0 and 1")
        if not (0.0 <= self.max_same_strategy_plugin_ratio <= 1.0):
            raise ValueError("max_same_strategy_plugin_ratio must be between 0 and 1")
        return self

class PortfolioDiversificationConfig(BaseModel):
    enabled: bool = True
    reward_low_correlation: bool = True
    reward_signal_source_diversity: bool = True
    reward_regime_diversity: bool = True
    reward_interval_diversity: bool = False
    diversification_bonus_max: float = 10.0
    low_diversification_penalty: float = 15.0

class PortfolioRiskBudgetConfig(BaseModel):
    enabled: bool = True
    mode: str = "placeholder"
    max_total_risk_budget_pct: float = 2.0
    max_single_candidate_risk_budget_pct: float = 0.50
    risk_budget_unit: str = "percent_of_simulated_equity"
    allocate_budget_production_forbidden: bool = True
    budget_is_hypothetical: bool = True

class PortfolioRankingConfig(BaseModel):
    enabled: bool = True
    method: str = "weighted_score"
    score_clamp_min: float = 0.0
    score_clamp_max: float = 100.0
    components: dict[str, float] = Field(default_factory=lambda: {
        "candidate_quality_weight": 0.30,
        "risk_quality_weight": 0.20,
        "ml_blend_weight": 0.20,
        "diversification_weight": 0.10,
        "correlation_penalty_weight": -0.10,
        "concentration_penalty_weight": -0.10,
        "liquidity_penalty_weight": -0.05,
        "stale_candidate_penalty_weight": -0.05
    })
    require_breakdown: bool = True
    require_explanation: bool = True

class PortfolioOptimizerSkeletonConfig(BaseModel):
    enabled: bool = True
    default_enabled_for_selection: bool = False
    scipy_optional: bool = True
    fail_if_scipy_missing: bool = False
    method: str = "slsqp_skeleton"
    constraints: dict[str, Any] = Field(default_factory=lambda: {
        "sum_weights_lte_one": True,
        "long_only_weights": True,
        "max_single_weight": 0.20,
        "max_total_exposure": 0.30,
        "max_pair_correlation": 0.80
    })
    production_allocation_forbidden: bool = True
    optimization_output_sandbox_only: bool = True

    @model_validator(mode="after")
    def validate_optimizer_skeleton_config(self) -> "PortfolioOptimizerSkeletonConfig":
        if not self.production_allocation_forbidden:
            raise ValueError("production_allocation_forbidden must be True")
        return self

class PortfolioSandboxOutputConfig(BaseModel):
    create_selected_candidate_set: bool = True
    create_portfolio_selection_report: bool = True
    create_allocation_placeholder: bool = True
    selected_candidate_production_forbidden: bool = True
    allocation_production_forbidden: bool = True
    write_to_signal_engine_forbidden: bool = True
    write_to_risk_engine_forbidden: bool = True
    write_to_paper_engine_forbidden: bool = True
    write_to_live_engine_forbidden: bool = True
    require_blocked_flags: bool = True
    require_research_only_intent: bool = True
    require_no_order_intent: bool = True

class PortfolioSandboxQualityConfig(BaseModel):
    reject_no_candidates: bool = False
    warn_no_candidates: bool = True
    reject_missing_breakdown: bool = True
    reject_missing_explanation: bool = True
    reject_score_out_of_range: bool = True
    reject_nan_inf_scores: bool = True
    reject_missing_hashes: bool = True
    reject_forward_correlation: bool = True
    reject_future_columns: bool = True
    reject_production_write_intent: bool = True
    reject_live_or_paper_intent: bool = True
    warn_high_correlation: bool = True
    warn_high_concentration: bool = True
    warn_low_diversification: bool = True
    warn_missing_correlation_data: bool = True

class PortfolioSandboxConfig(BaseModel):
    enabled: bool = True
    output_dataset_name: str = "portfolio_candidate_selection_sandbox"
    cache_enabled: bool = True
    cache_dir: str = "data/portfolio/sandbox/cache"
    export_dir: str = "data/portfolio/sandbox/exports"
    reports_dir: str = "data/portfolio/sandbox/reports"

    real_exchange_forbidden: bool = True
    paper_trade_forbidden: bool = True
    live_trade_forbidden: bool = True
    order_creation_forbidden: bool = True
    api_key_forbidden: bool = True
    signed_request_forbidden: bool = True
    dashboard_forbidden: bool = True
    signal_auto_write_forbidden: bool = True
    risk_auto_write_forbidden: bool = True
    paper_auto_write_forbidden: bool = True
    live_auto_write_forbidden: bool = True
    allocation_production_forbidden: bool = True
    position_sizing_production_forbidden: bool = True

    inputs: PortfolioSandboxInputConfig = Field(default_factory=PortfolioSandboxInputConfig)
    candidate_normalization: PortfolioCandidateNormalizationConfig = Field(default_factory=PortfolioCandidateNormalizationConfig)
    eligibility: PortfolioEligibilityConfig = Field(default_factory=PortfolioEligibilityConfig)
    correlation: PortfolioCorrelationConfig = Field(default_factory=PortfolioCorrelationConfig)
    similarity: PortfolioSimilarityConfig = Field(default_factory=PortfolioSimilarityConfig)
    exposure: PortfolioExposureConfig = Field(default_factory=PortfolioExposureConfig)
    concentration: PortfolioConcentrationConfig = Field(default_factory=PortfolioConcentrationConfig)
    diversification: PortfolioDiversificationConfig = Field(default_factory=PortfolioDiversificationConfig)
    risk_budget: PortfolioRiskBudgetConfig = Field(default_factory=PortfolioRiskBudgetConfig)
    ranking: PortfolioRankingConfig = Field(default_factory=PortfolioRankingConfig)
    optimizer_skeleton: PortfolioOptimizerSkeletonConfig = Field(default_factory=PortfolioOptimizerSkeletonConfig)
    sandbox_output: PortfolioSandboxOutputConfig = Field(default_factory=PortfolioSandboxOutputConfig)
    quality: PortfolioSandboxQualityConfig = Field(default_factory=PortfolioSandboxQualityConfig)

    @model_validator(mode="after")
    def validate_safety_flags(self) -> "PortfolioSandboxConfig":
        if not self.real_exchange_forbidden: raise ValueError("real_exchange_forbidden must be True")
        if not self.paper_trade_forbidden: raise ValueError("paper_trade_forbidden must be True")
        if not self.live_trade_forbidden: raise ValueError("live_trade_forbidden must be True")
        if not self.order_creation_forbidden: raise ValueError("order_creation_forbidden must be True")
        if not self.api_key_forbidden: raise ValueError("api_key_forbidden must be True")
        if not self.signed_request_forbidden: raise ValueError("signed_request_forbidden must be True")
        if not self.dashboard_forbidden: raise ValueError("dashboard_forbidden must be True")
        if not self.signal_auto_write_forbidden: raise ValueError("signal_auto_write_forbidden must be True")
        if not self.risk_auto_write_forbidden: raise ValueError("risk_auto_write_forbidden must be True")
        if not self.paper_auto_write_forbidden: raise ValueError("paper_auto_write_forbidden must be True")
        if not self.live_auto_write_forbidden: raise ValueError("live_auto_write_forbidden must be True")
        if not self.allocation_production_forbidden: raise ValueError("allocation_production_forbidden must be True")
        if not self.position_sizing_production_forbidden: raise ValueError("position_sizing_production_forbidden must be True")

        import re
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.output_dataset_name):
            raise ValueError("output_dataset_name is not safe")

        return self
"""
# Ensure new models are injected before AppConfig
content = re.sub(r'class AppConfig\(BaseModel\):', new_models + '\nclass AppConfig(BaseModel):\n    portfolio_sandbox: PortfolioSandboxConfig = Field(default_factory=PortfolioSandboxConfig)', content)

# But wait, looking at the previous patch attempt, we need to be careful not to duplicate. Let's just find the first occurrence of MLInferenceConfig definition and put them right after.
# Wait, let's look for AppConfig instead to append it right above.
with open("binance50/src/binance50/config/models.py", "w") as f:
    f.write(content)
