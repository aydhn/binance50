from binance50.config.models import AppConfig
from binance50.storage.catalog_models import DatasetRecord, DatasetVersionRecord, FileManifestRecord
from binance50.storage.integrity import StorageIntegrityReport
from binance50.storage.sqlite_catalog import SQLiteCatalog


def build_storage_config_report(config: AppConfig) -> dict:
    return {
        "enabled": config.storage.enabled,
        "root_dir": config.storage.root_dir,
        "parquet_root": config.storage.parquet_root_dir,
        "catalog_path": config.storage.sqlite_catalog_path,
        "safety_allow_delete": config.storage.safety.allow_delete,
        "safety_allow_destructive_migration": config.storage.safety.allow_destructive_migration
    }

def build_catalog_summary(catalog: SQLiteCatalog) -> dict:
    datasets = catalog.list_datasets()
    return {
        "total_datasets": len(datasets),
        "datasets": [d.dataset_name for d in datasets]
    }

def build_dataset_summary(dataset_name: str, catalog: SQLiteCatalog) -> dict:
    ds = catalog.get_dataset(dataset_name)
    if not ds:
         return {"error": "not found"}

    versions = catalog.list_versions(dataset_name)
    active_version = next((v for v in versions if v.is_active), None)

    return {
        "dataset_name": ds.dataset_name,
        "schema_version": ds.schema_version,
        "total_versions": len(versions),
        "active_version": active_version.version_id if active_version else None,
        "total_rows_active": active_version.row_count if active_version else 0
    }

def build_storage_health_report(config: AppConfig) -> dict:
    from binance50.storage.health import StorageHealthService
    return StorageHealthService(config).check()

def build_integrity_report_view(report: StorageIntegrityReport) -> dict:
    return {
        "status": report.status,
        "checked_at": report.checked_at_utc,
        "issues": report.issues,
        "warnings": report.warnings
    }

def format_dataset_table(records: list[DatasetRecord]) -> list[dict]:
    return [r.__dict__ for r in records]

def format_versions_table(records: list[DatasetVersionRecord]) -> list[dict]:
    return [r.__dict__ for r in records]

def format_files_table(records: list[FileManifestRecord]) -> list[dict]:
    return [r.__dict__ for r in records]
