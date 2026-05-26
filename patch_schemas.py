with open("binance50/src/binance50/storage/schemas.py", "r") as f:
    content = f.read()

new_enums = """    BACKTEST_DRAWDOWN_REPORTS = "backtest_drawdown_reports"
    BACKTEST_TRADE_DISTRIBUTION_REPORTS = "backtest_trade_distribution_reports"

    ML_DATASETS = "ml_datasets"
    ML_FEATURES = "ml_features"
    ML_LABELS = "ml_labels"
    ML_DATASET_MANIFESTS = "ml_dataset_manifests"
    ML_SPLIT_METADATA = "ml_split_metadata"
    ML_PREPROCESSOR_METADATA = "ml_preprocessor_metadata"
    ML_LEAKAGE_REPORTS = "ml_leakage_reports"
    ML_QUALITY_REPORTS = "ml_quality_reports"
"""

content = content.replace('    BACKTEST_TRADE_DISTRIBUTION_REPORTS = "backtest_trade_distribution_reports"', new_enums)

with open("binance50/src/binance50/storage/schemas.py", "w") as f:
    f.write(content)
