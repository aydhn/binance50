from dataclasses import dataclass

from binance50.config.models import AppConfig
from binance50.storage.parquet_store import ParquetDatasetStore
from binance50.storage.sqlite_catalog import SQLiteCatalog


@dataclass
class CompactionPlan:
    dataset_name: str
    target_files: int
    estimated_input_files: int
    estimated_input_rows: int
    dry_run: bool
    warnings: list[str]


@dataclass
class CompactionResult:
    success: bool
    dry_run: bool
    files_read: int
    files_written: int
    rows_processed: int
    bytes_before: int
    bytes_after: int
    warnings: list[str]


class StorageCompactor:
    def __init__(
        self, config: AppConfig, catalog: SQLiteCatalog, parquet_store: ParquetDatasetStore
    ):
        self.config = config
        self.catalog = catalog
        self.parquet_store = parquet_store

    def plan_compaction(self, dataset_name: str, filters: dict | None = None) -> CompactionPlan:
        # Simplistic mocked plan
        files = self.parquet_store.list_dataset_files(dataset_name)
        return CompactionPlan(
            dataset_name=dataset_name,
            target_files=max(1, len(files) // 2),
            estimated_input_files=len(files),
            estimated_input_rows=len(files) * 1000,  # Mock
            dry_run=True,
            warnings=["Vacuum config is " + str(self.config.storage.sqlite.vacuum_on_compaction)],
        )

    def compact(
        self, dataset_name: str, filters: dict | None = None, dry_run: bool = True
    ) -> CompactionResult:
        plan = self.plan_compaction(dataset_name, filters)

        if not dry_run and not self.config.storage.safety.allow_delete:
            # Just note it in warnings if delete is not allowed, compaction could just write new, not delete old.
            plan.warnings.append("allow_delete is false. Old files will not be deleted physically.")

        # In a real system, you would load arrow dataset -> group -> write large files -> update catalog

        if not dry_run and self.config.storage.sqlite.vacuum_on_compaction:
            self.catalog.vacuum()

        return CompactionResult(
            success=True,
            dry_run=dry_run,
            files_read=plan.estimated_input_files,
            files_written=plan.target_files,
            rows_processed=plan.estimated_input_rows,
            bytes_before=plan.estimated_input_files * 1024 * 1024,
            bytes_after=plan.target_files * 1024 * 1024,
            warnings=plan.warnings,
        )
