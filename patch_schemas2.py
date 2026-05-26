with open("binance50/src/binance50/storage/schemas.py", "r") as f:
    content = f.read()

new_schemas = """

def get_ml_datasets_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_datasets",
        dataset_kind=DatasetKind.ML_DATASETS,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "datetime64[ns, UTC]", nullable=False, is_primary_key=True),
        ],
        primary_keys=["dataset_id", "open_time"],
        dynamic_columns_allowed=True,
        dynamic_column_prefixes=["trend_", "mom_", "vol_", "volu_", "tr_", "div_", "mtf_", "pat_", "reg_", "signal_", "risk_", "label_"],
        disallowed_column_names=[
            "target", "future_return", "next_close", "forward_return",
            "order_id", "client_order_id", "exchange_order_id", "live_order",
            "testnet_order", "paper_order", "real_order", "execution_gateway",
            "api_key", "secret", "signature"
        ]
    )

def get_ml_features_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_features",
        dataset_kind=DatasetKind.ML_FEATURES,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "datetime64[ns, UTC]", nullable=False, is_primary_key=True),
        ],
        primary_keys=["dataset_id", "open_time"],
        dynamic_columns_allowed=True,
        dynamic_column_prefixes=["trend_", "mom_", "vol_", "volu_", "tr_", "div_", "mtf_", "pat_", "reg_", "signal_", "risk_"],
        disallowed_column_names=[
            "target", "future_return", "next_close", "forward_return", "label_",
            "order_id", "client_order_id", "exchange_order_id", "live_order",
            "testnet_order", "paper_order", "real_order", "execution_gateway",
            "api_key", "secret", "signature"
        ]
    )

def get_ml_labels_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_labels",
        dataset_kind=DatasetKind.ML_LABELS,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "datetime64[ns, UTC]", nullable=False, is_primary_key=True),
            ColumnSchema("label_column", "string", nullable=False, is_primary_key=True),
            ColumnSchema("label_value", "float64", nullable=False),
        ],
        primary_keys=["dataset_id", "open_time", "label_column"],
        disallowed_column_names=[
            "order_id", "client_order_id", "exchange_order_id", "live_order",
            "testnet_order", "paper_order", "real_order", "execution_gateway",
            "api_key", "secret", "signature"
        ]
    )

def get_ml_dataset_manifests_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_dataset_manifests",
        dataset_kind=DatasetKind.ML_DATASET_MANIFESTS,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("dataset_version", "int64", nullable=False),
            ColumnSchema("symbol", "string", nullable=False),
            ColumnSchema("market_scope", "string", nullable=False),
            ColumnSchema("interval", "string", nullable=False),
            ColumnSchema("row_count", "int64", nullable=False),
            ColumnSchema("feature_count", "int64", nullable=False),
            ColumnSchema("label_count", "int64", nullable=False),
            ColumnSchema("dataset_hash", "string", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
            ColumnSchema("quality_status", "string", nullable=False),
            ColumnSchema("created_at_utc", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["dataset_id"],
    )

def get_ml_split_metadata_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_split_metadata",
        dataset_kind=DatasetKind.ML_SPLIT_METADATA,
        version=1,
        columns=[
            ColumnSchema("split_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("split_method", "string", nullable=False),
            ColumnSchema("train_start", "string", nullable=False),
            ColumnSchema("train_end", "string", nullable=False),
            ColumnSchema("validation_start", "string", nullable=True),
            ColumnSchema("validation_end", "string", nullable=True),
            ColumnSchema("test_start", "string", nullable=True),
            ColumnSchema("test_end", "string", nullable=True),
            ColumnSchema("train_rows", "int64", nullable=False),
            ColumnSchema("validation_rows", "int64", nullable=False),
            ColumnSchema("test_rows", "int64", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["split_id"],
    )

def get_ml_preprocessor_metadata_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_preprocessor_metadata",
        dataset_kind=DatasetKind.ML_PREPROCESSOR_METADATA,
        version=1,
        columns=[
            ColumnSchema("preprocessor_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("scaler", "string", nullable=False),
            ColumnSchema("imputation_strategy", "string", nullable=False),
            ColumnSchema("clipping_method", "string", nullable=False),
            ColumnSchema("fit_split", "string", nullable=False),
            ColumnSchema("hash", "string", nullable=False),
            ColumnSchema("fitted_at_utc", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["preprocessor_id"],
    )

def get_ml_leakage_reports_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_leakage_reports",
        dataset_kind=DatasetKind.ML_LEAKAGE_REPORTS,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("issue_count", "int64", nullable=False),
            ColumnSchema("future_column_count", "int64", nullable=False),
            ColumnSchema("label_in_feature_count", "int64", nullable=False),
            ColumnSchema("target_in_feature_count", "int64", nullable=False),
            ColumnSchema("generated_at_utc", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["dataset_id"],
    )

def get_ml_quality_reports_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="ml_quality_reports",
        dataset_kind=DatasetKind.ML_QUALITY_REPORTS,
        version=1,
        columns=[
            ColumnSchema("dataset_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("row_count", "int64", nullable=False),
            ColumnSchema("missing_feature_count", "int64", nullable=False),
            ColumnSchema("missing_label_count", "int64", nullable=False),
            ColumnSchema("nan_inf_feature_count", "int64", nullable=False),
            ColumnSchema("nan_inf_label_count", "int64", nullable=False),
            ColumnSchema("generated_at_utc", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
        ],
        primary_keys=["dataset_id"],
    )

def get_schema_registry() -> dict[str, DatasetSchema]:
    return {
        "ohlcv": get_ohlcv_schema(),
        "universe_selection": get_universe_selection_schema(),
        "stream_events": get_stream_events_schema(),
        "quality_reports": get_quality_reports_schema(),
        "strategy_candidates": get_strategy_candidates_schema(),
        "scored_signal_candidates": get_scored_signal_candidates_schema(),
        "market_regimes": get_market_regimes_schema(),
        "risk_assessments": get_risk_assessments_schema(),
        "optimization_runs": get_optimization_runs_schema(),
        "optimization_trials": get_optimization_trials_schema(),
        "optimization_overfit_reports": get_optimization_overfit_reports_schema(),
        "optimization_robustness_reports": get_optimization_robustness_reports_schema(),
        "optimization_search_spaces": get_optimization_search_spaces_schema(),
        "ml_datasets": get_ml_datasets_schema(),
        "ml_features": get_ml_features_schema(),
        "ml_labels": get_ml_labels_schema(),
        "ml_dataset_manifests": get_ml_dataset_manifests_schema(),
        "ml_split_metadata": get_ml_split_metadata_schema(),
        "ml_preprocessor_metadata": get_ml_preprocessor_metadata_schema(),
        "ml_leakage_reports": get_ml_leakage_reports_schema(),
        "ml_quality_reports": get_ml_quality_reports_schema(),
    }
"""
content = content.replace("""def get_schema_registry() -> dict[str, DatasetSchema]:
    return {
        "ohlcv": get_ohlcv_schema(),
        "universe_selection": get_universe_selection_schema(),
        "stream_events": get_stream_events_schema(),
        "quality_reports": get_quality_reports_schema(),
        "strategy_candidates": get_strategy_candidates_schema(),
        "scored_signal_candidates": get_scored_signal_candidates_schema(),
        "market_regimes": get_market_regimes_schema(),
        "risk_assessments": get_risk_assessments_schema(),
        "optimization_runs": get_optimization_runs_schema(),
        "optimization_trials": get_optimization_trials_schema(),
        "optimization_overfit_reports": get_optimization_overfit_reports_schema(),
        "optimization_robustness_reports": get_optimization_robustness_reports_schema(),
        "optimization_search_spaces": get_optimization_search_spaces_schema(),
    }""", new_schemas)

with open("binance50/src/binance50/storage/schemas.py", "w") as f:
    f.write(content)
