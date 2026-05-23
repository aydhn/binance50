import json
from pathlib import Path

from binance50.config.models import AppConfig
from binance50.storage.paths import get_exports_dir
from binance50.storage.sqlite_catalog import SQLiteCatalog


def _get_export_path(config: AppConfig, name: str, path: Path | None) -> Path:
    if path:
        return path
    exports_dir = get_exports_dir(config)
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir / f"{name}.json"


def export_catalog_to_json(config: AppConfig, path: Path | None = None) -> Path:
    catalog = SQLiteCatalog(config)
    datasets = catalog.list_datasets()

    data = {"datasets": [d.__dict__ for d in datasets]}

    out_path = _get_export_path(config, "catalog_export", path)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return out_path


def export_dataset_manifest(dataset_name: str, config: AppConfig, path: Path | None = None) -> Path:
    catalog = SQLiteCatalog(config)
    v = catalog.get_latest_active_version(dataset_name)
    if not v:
        raise ValueError(f"No active version for {dataset_name}")

    files = catalog.list_files(v.version_id)
    data = {
        "dataset_name": dataset_name,
        "version_id": v.version_id,
        "files": [f.__dict__ for f in files],
    }

    out_path = _get_export_path(config, f"{dataset_name}_manifest", path)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return out_path


def export_quality_index(dataset_name: str, config: AppConfig, path: Path | None = None) -> Path:
    from binance50.storage.quality_index import QualityIndex

    catalog = SQLiteCatalog(config)
    qi = QualityIndex(catalog)
    issues = qi.list_quality_issues(dataset_name)

    out_path = _get_export_path(config, f"{dataset_name}_quality", path)
    with open(out_path, "w") as f:
        json.dump([i.__dict__ for i in issues], f, indent=2)
    return out_path


def export_data_coverage(dataset_name: str, config: AppConfig, path: Path | None = None) -> Path:
    from binance50.storage.data_index import DataIndex

    catalog = SQLiteCatalog(config)
    di = DataIndex(catalog)
    coverage = di.list_coverage(dataset_name)

    out_path = _get_export_path(config, f"{dataset_name}_coverage", path)
    with open(out_path, "w") as f:
        json.dump([c.__dict__ for c in coverage], f, indent=2)
    return out_path
