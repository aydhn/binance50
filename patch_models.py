import re

with open('binance50/src/binance50/config/models.py', 'r') as f:
    content = f.read()

models_code = """
from typing import Literal

class ParquetStorageConfig(BaseModel):
    enabled: bool = True
    compression: Literal["zstd", "snappy", "gzip", "brotli", "none"] = "zstd"
    fallback_compression: Literal["zstd", "snappy", "gzip", "brotli", "none"] = "snappy"
    use_dictionary: bool = True
    write_statistics: bool = True
    row_group_size: int = Field(default=100000, gt=0)
    max_rows_per_file: int = Field(default=500000, gt=0)
    partition_style: Literal["hive", "directory"] = "hive"
    schema_validation: bool = True
    atomic_write: bool = True
    temp_write_suffix: str = ".tmp"
    allow_overwrite: bool = False
    allow_append: bool = True
    allow_upsert: bool = True

    @model_validator(mode="after")
    def validate_parquet(self) -> "ParquetStorageConfig":
        if self.max_rows_per_file <= self.row_group_size:
            raise ValueError("max_rows_per_file must be greater than row_group_size")
        return self

class SQLiteStorageConfig(BaseModel):
    enabled: bool = True
    journal_mode: Literal["WAL", "DELETE", "TRUNCATE", "PERSIST", "MEMORY", "OFF"] = "WAL"
    synchronous: Literal["OFF", "NORMAL", "FULL", "EXTRA"] = "NORMAL"
    foreign_keys: bool = True
    busy_timeout_ms: int = Field(default=5000, ge=100, le=60000)
    integrity_check_on_start: bool = True
    quick_check_on_doctor: bool = True
    vacuum_on_compaction: bool = False
    backup_before_migration: bool = True

class StoragePartitioningConfig(BaseModel):
    by_market_scope: bool = True
    by_symbol: bool = True
    by_interval: bool = True
    by_year: bool = True
    by_month: bool = True
    by_day: bool = False

class StorageDatasetsConfig(BaseModel):
    ohlcv_dataset_name: str = "ohlcv"
    universe_dataset_name: str = "universe_selection"
    stream_events_dataset_name: str = "stream_events"
    quality_dataset_name: str = "quality_reports"
    allowed_dataset_names: list[str] = Field(default_factory=lambda: [
        "ohlcv", "universe_selection", "stream_events", "quality_reports",
        "feature_store_future", "backtest_results_future"
    ], min_length=1)

    @model_validator(mode="after")
    def validate_datasets(self) -> "StorageDatasetsConfig":
        for name in self.allowed_dataset_names:
            if not re.match(r'^[a-z0-9_]+$', name):
                raise ValueError(f"dataset name {name} must be a safe slug")
        return self

class StorageIntegrityConfig(BaseModel):
    compute_file_hash: bool = True
    compute_dataframe_hash: bool = True
    verify_after_write: bool = True
    verify_before_read: bool = True
    reject_schema_drift: bool = True
    reject_duplicate_primary_keys: bool = True
    reject_empty_dataset: bool = True

class StorageRetentionConfig(BaseModel):
    enabled: bool = False
    max_versions_per_dataset: int = Field(default=20, gt=0)
    keep_latest_versions: int = Field(default=5, gt=0)
    archive_old_versions: bool = True
    delete_archived_after_days: int = Field(default=365, ge=0)

    @model_validator(mode="after")
    def validate_retention(self) -> "StorageRetentionConfig":
        if self.max_versions_per_dataset < self.keep_latest_versions:
            raise ValueError("max_versions_per_dataset must be >= keep_latest_versions")
        return self

class StorageBackupConfig(BaseModel):
    enabled: bool = True
    backup_catalog: bool = True
    backup_manifests: bool = True
    backup_parquet_metadata_only: bool = True
    max_backups: int = Field(default=20, ge=1, le=100)

class StorageSafetyConfig(BaseModel):
    allow_delete: bool = False
    allow_destructive_migration: bool = False
    require_backup_before_migration: bool = True
    block_paths_outside_project: bool = True
    block_secret_columns: bool = True
    block_unknown_dataset_names: bool = True

class StorageConfig(BaseModel):
    enabled: bool = True
    root_dir: str = "data/warehouse"
    parquet_root_dir: str = "data/warehouse/parquet"
    sqlite_catalog_path: str = "data/warehouse/catalog/binance50_catalog.sqlite"
    manifest_dir: str = "data/warehouse/manifests"
    reports_dir: str = "data/warehouse/reports"
    backups_dir: str = "data/warehouse/backups"
    exports_dir: str = "data/warehouse/exports"
    temp_dir: str = "data/warehouse/tmp"
    lock_dir: str = "data/warehouse/locks"

    parquet: ParquetStorageConfig = Field(default_factory=ParquetStorageConfig)
    sqlite: SQLiteStorageConfig = Field(default_factory=SQLiteStorageConfig)
    partitioning: StoragePartitioningConfig = Field(default_factory=StoragePartitioningConfig)
    datasets: StorageDatasetsConfig = Field(default_factory=StorageDatasetsConfig)
    integrity: StorageIntegrityConfig = Field(default_factory=StorageIntegrityConfig)
    retention: StorageRetentionConfig = Field(default_factory=StorageRetentionConfig)
    backup: StorageBackupConfig = Field(default_factory=StorageBackupConfig)
    safety: StorageSafetyConfig = Field(default_factory=StorageSafetyConfig)

"""

# Insert models before AppConfig
content = content.replace("class AppConfig(BaseModel):", models_code + "\nclass AppConfig(BaseModel):")

# Add to AppConfig
content = content.replace(
    "    streams: StreamsConfig = StreamsConfig()",
    "    streams: StreamsConfig = StreamsConfig()\n    storage: StorageConfig = StorageConfig()"
)

# Also ensure "import re" is at the top
if "import re" not in content:
    content = "import re\n" + content

with open('binance50/src/binance50/config/models.py', 'w') as f:
    f.write(content)

