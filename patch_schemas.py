with open("binance50/src/binance50/storage/schemas.py", "r") as f:
    content = f.read()

new_kinds = """
    PORTFOLIO_SELECTION_RUNS = "portfolio_selection_runs"
    PORTFOLIO_INPUT_CANDIDATES = "portfolio_input_candidates"
    PORTFOLIO_SELECTED_SANDBOX_CANDIDATES = "portfolio_selected_sandbox_candidates"
    PORTFOLIO_CANDIDATE_SCORE_BREAKDOWNS = "portfolio_candidate_score_breakdowns"
    PORTFOLIO_CORRELATION_REPORTS = "portfolio_correlation_reports"
    PORTFOLIO_SIMILARITY_REPORTS = "portfolio_similarity_reports"
    PORTFOLIO_EXPOSURE_REPORTS = "portfolio_exposure_reports"
    PORTFOLIO_CONCENTRATION_REPORTS = "portfolio_concentration_reports"
    PORTFOLIO_DIVERSIFICATION_REPORTS = "portfolio_diversification_reports"
    PORTFOLIO_RISK_BUDGET_REPORTS = "portfolio_risk_budget_reports"
    PORTFOLIO_QUALITY_REPORTS = "portfolio_quality_reports"
"""
content = content.replace("    ML_QUALITY_REPORTS = \"ml_quality_reports\"", "    ML_QUALITY_REPORTS = \"ml_quality_reports\"\n" + new_kinds)

schema_funcs = """
def get_portfolio_selection_runs_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="portfolio_selection_runs",
        dataset_kind=DatasetKind.PORTFOLIO_SELECTION_RUNS,
        version=1,
        columns=[
            ColumnSchema("run_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["run_id"],
    )

def get_portfolio_input_candidates_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="portfolio_input_candidates",
        dataset_kind=DatasetKind.PORTFOLIO_INPUT_CANDIDATES,
        version=1,
        columns=[
            ColumnSchema("candidate_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["candidate_id"],
    )

def get_portfolio_selected_sandbox_candidates_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="portfolio_selected_sandbox_candidates",
        dataset_kind=DatasetKind.PORTFOLIO_SELECTED_SANDBOX_CANDIDATES,
        version=1,
        columns=[
            ColumnSchema("selected_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["selected_id"],
    )

def get_portfolio_candidate_score_breakdowns_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="portfolio_candidate_score_breakdowns",
        dataset_kind=DatasetKind.PORTFOLIO_CANDIDATE_SCORE_BREAKDOWNS,
        version=1,
        columns=[
            ColumnSchema("selected_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["selected_id"],
    )

def get_portfolio_reports_schema(name: str, kind: DatasetKind) -> DatasetSchema:
    return DatasetSchema(
        dataset_name=name,
        dataset_kind=kind,
        version=1,
        columns=[
            ColumnSchema("run_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["run_id"],
    )
"""

content = content.replace("def get_schema_registry() -> dict[str, DatasetSchema]:", schema_funcs + "\ndef get_schema_registry() -> dict[str, DatasetSchema]:")

registry_items = """
        "portfolio_selection_runs": get_portfolio_selection_runs_schema(),
        "portfolio_input_candidates": get_portfolio_input_candidates_schema(),
        "portfolio_selected_sandbox_candidates": get_portfolio_selected_sandbox_candidates_schema(),
        "portfolio_candidate_score_breakdowns": get_portfolio_candidate_score_breakdowns_schema(),
        "portfolio_correlation_reports": get_portfolio_reports_schema("portfolio_correlation_reports", DatasetKind.PORTFOLIO_CORRELATION_REPORTS),
        "portfolio_similarity_reports": get_portfolio_reports_schema("portfolio_similarity_reports", DatasetKind.PORTFOLIO_SIMILARITY_REPORTS),
        "portfolio_exposure_reports": get_portfolio_reports_schema("portfolio_exposure_reports", DatasetKind.PORTFOLIO_EXPOSURE_REPORTS),
        "portfolio_concentration_reports": get_portfolio_reports_schema("portfolio_concentration_reports", DatasetKind.PORTFOLIO_CONCENTRATION_REPORTS),
        "portfolio_diversification_reports": get_portfolio_reports_schema("portfolio_diversification_reports", DatasetKind.PORTFOLIO_DIVERSIFICATION_REPORTS),
        "portfolio_risk_budget_reports": get_portfolio_reports_schema("portfolio_risk_budget_reports", DatasetKind.PORTFOLIO_RISK_BUDGET_REPORTS),
        "portfolio_quality_reports": get_portfolio_reports_schema("portfolio_quality_reports", DatasetKind.PORTFOLIO_QUALITY_REPORTS),
"""
content = content.replace("        \"ml_quality_reports\": get_ml_quality_reports_schema(),", "        \"ml_quality_reports\": get_ml_quality_reports_schema(),\n" + registry_items)

with open("binance50/src/binance50/storage/schemas.py", "w") as f:
    f.write(content)
