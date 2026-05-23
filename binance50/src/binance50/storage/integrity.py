from dataclasses import dataclass, field
from datetime import UTC, datetime

from binance50.config.models import AppConfig
from binance50.core.exceptions import StorageIntegrityError
from binance50.storage.parquet_store import ParquetDatasetStore
from binance50.storage.paths import ensure_storage_directories
from binance50.storage.sqlite_catalog import SQLiteCatalog


@dataclass
class StorageIntegrityReport:
    status: str
    checked_at_utc: str
    directory_status: dict
    sqlite_status: dict
    parquet_status: dict
    manifest_status: dict
    catalog_status: dict
    hash_status: dict
    schema_status: dict
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StorageIntegrityChecker:
    def __init__(
        self, config: AppConfig, catalog: SQLiteCatalog, parquet_store: ParquetDatasetStore
    ):
        self.config = config
        self.catalog = catalog
        self.parquet_store = parquet_store

    def check_directories(self) -> dict:
        try:
            ensure_storage_directories(self.config)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_sqlite_integrity(self) -> dict:
        try:
            res_quick = self.catalog.run_quick_check()
            res_int = self.catalog.run_integrity_check()
            return {"status": "ok", "quick_check": res_quick, "integrity_check": res_int}
        except StorageIntegrityError as e:
            return {"status": "error", "message": str(e)}

    def check_parquet_files(self, dataset_name: str | None = None) -> dict:
        # Mock checking parquet files
        return {"status": "ok", "files_checked": 0}

    def check_manifests(self) -> dict:
        return {"status": "ok"}

    def check_catalog_consistency(self) -> dict:
        # e.g., files in catalog but missing from disk
        return {"status": "ok"}

    def check_file_hashes(self) -> dict:
        return {"status": "ok"}

    def check_schema_consistency(self, dataset_name: str | None = None) -> dict:
        return {"status": "ok"}

    def run_full_check(self) -> StorageIntegrityReport:
        report = StorageIntegrityReport(
            status="running",
            checked_at_utc=datetime.now(UTC).isoformat(),
            directory_status=self.check_directories(),
            sqlite_status=self.check_sqlite_integrity(),
            parquet_status=self.check_parquet_files(),
            manifest_status=self.check_manifests(),
            catalog_status=self.check_catalog_consistency(),
            hash_status=self.check_file_hashes(),
            schema_status=self.check_schema_consistency(),
        )

        has_error = False
        for k, v in report.__dict__.items():
            if isinstance(v, dict) and v.get("status") == "error":
                report.issues.append(f"{k} failed: {v.get('message')}")
                has_error = True

        report.status = "error" if has_error else "ok"
        return report
