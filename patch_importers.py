with open("binance50/src/binance50/storage/importers.py", "r") as f:
    content = f.read()

new_importer = """
from binance50.ml.datasets.models import MLDatasetBuildResult
from binance50.core.exceptions import DatasetImportError
from binance50.ml.datasets.storage import ml_dataset_to_storage_frames

def import_ml_dataset_result(
    storage_manager: Any,
    result: MLDatasetBuildResult,
    config: AppConfig,
    overwrite: bool = False,
) -> None:
    if not result.success or result.dataset_df is None or result.manifest is None:
        raise DatasetImportError("Cannot import failed or empty ML dataset result")

    if result.quality_report.status != "passed" and result.quality_report.status != "warnings":
         raise DatasetImportError("Cannot import dataset failing quality checks")

    if result.leakage_report.status != "clean" and result.leakage_report.status != "warnings":
        raise DatasetImportError("Cannot import dataset with critical leakage issues")

    for feature_col in result.manifest.feature_columns:
        if any(w in feature_col.lower() for w in ["label", "target", "future"]):
            raise DatasetImportError("Feature dataframe contains forbidden feature columns")

    frames = ml_dataset_to_storage_frames(result)
    for dataset_name, df in frames.items():
        if df is not None and not df.empty:
            storage_manager.append_dataframe(dataset_name, df)
"""

content += new_importer
with open("binance50/src/binance50/storage/importers.py", "w") as f:
    f.write(content)
