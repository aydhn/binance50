import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any
from binance50.config.models import AppConfig
from binance50.core.exceptions import SQLiteCatalogError, StorageIntegrityError
from binance50.storage.paths import get_sqlite_catalog_path
from binance50.storage.catalog_models import (
    DatasetRecord, DatasetVersionRecord, FileManifestRecord,
    QualityIndexRecord, SnapshotRecord, StorageJobRecord
)

class SQLiteCatalog:
    def __init__(self, config: AppConfig, path: Path | None = None):
        self.config = config
        self.path = path or get_sqlite_catalog_path(config)
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if not self._conn:
            try:
                self._conn = sqlite3.connect(
                    self.path,
                    timeout=self.config.storage.sqlite.busy_timeout_ms / 1000.0,
                    check_same_thread=False
                )
                self._conn.row_factory = sqlite3.Row
                # Apply pragmas
                self._conn.execute(f"PRAGMA journal_mode={self.config.storage.sqlite.journal_mode}")
                self._conn.execute(f"PRAGMA synchronous={self.config.storage.sqlite.synchronous}")
                if self.config.storage.sqlite.foreign_keys:
                    self._conn.execute("PRAGMA foreign_keys=ON")
                else:
                    self._conn.execute("PRAGMA foreign_keys=OFF")
            except sqlite3.Error as e:
                raise SQLiteCatalogError(f"Failed to connect to SQLite: {e}")
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        conn = self.connect()
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise SQLiteCatalogError(f"Transaction failed: {e}")

    def execute(self, sql: str, params: tuple | dict | None = None) -> list[sqlite3.Row]:
        conn = self.connect()
        try:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise SQLiteCatalogError(f"Query execution failed: {e}")

    def initialize(self) -> None:
        """Create the catalog directory if needed, connect."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connect()

    def run_quick_check(self) -> str:
        res = self.execute("PRAGMA quick_check")
        status = res[0][0]
        if status != "ok":
            raise StorageIntegrityError(f"SQLite quick_check failed: {status}")
        return status

    def run_integrity_check(self) -> str:
        res = self.execute("PRAGMA integrity_check")
        status = res[0][0]
        if status != "ok":
            raise StorageIntegrityError(f"SQLite integrity_check failed: {status}")
        return status

    def vacuum(self) -> None:
        self.execute("VACUUM")

    # --- UPSERTS & INSERTS ---

    def upsert_dataset(self, record: DatasetRecord) -> None:
        sql = """
            INSERT INTO datasets (dataset_id, dataset_name, dataset_kind, schema_version, status, created_at_utc, updated_at_utc, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(dataset_name) DO UPDATE SET
                schema_version=excluded.schema_version,
                status=excluded.status,
                updated_at_utc=excluded.updated_at_utc,
                description=excluded.description
        """
        with self.transaction() as c:
            c.execute(sql, (
                record.dataset_id, record.dataset_name, record.dataset_kind, record.schema_version,
                record.status, record.created_at_utc, record.updated_at_utc, record.description
            ))

    def create_dataset_version(self, record: DatasetVersionRecord) -> str:
        sql = """
            INSERT INTO dataset_versions (
                version_id, dataset_id, version_number, source, row_count, start_time_ms, end_time_ms,
                data_hash, manifest_path, quality_status, created_at_utc, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as c:
            # Enforce single active version logic here or in dataset_registry
            c.execute(sql, (
                record.version_id, record.dataset_id, record.version_number, record.source, record.row_count,
                record.start_time_ms, record.end_time_ms, record.data_hash, record.manifest_path,
                record.quality_status, record.created_at_utc, record.is_active
            ))
        return record.version_id

    def add_file_manifest(self, record: FileManifestRecord) -> None:
        sql = """
            INSERT INTO file_manifests (
                file_id, version_id, dataset_name, file_path, file_format, compression,
                row_count, file_size_bytes, file_hash, min_open_time, max_open_time, partition_values, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as c:
            c.execute(sql, (
                record.file_id, record.version_id, record.dataset_name, record.file_path, record.file_format,
                record.compression, record.row_count, record.file_size_bytes, record.file_hash,
                record.min_open_time, record.max_open_time, record.partition_values, record.created_at_utc
            ))

    def add_quality_index(self, record: QualityIndexRecord) -> None:
        sql = """
            INSERT INTO quality_index (
                quality_id, version_id, dataset_name, symbol, interval, issue_type, severity,
                issue_count, first_seen_open_time, last_seen_open_time, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as c:
            c.execute(sql, (
                record.quality_id, record.version_id, record.dataset_name, record.symbol, record.interval,
                record.issue_type, record.severity, record.issue_count, record.first_seen_open_time,
                record.last_seen_open_time, record.created_at_utc
            ))

    def add_snapshot(self, record: SnapshotRecord) -> None:
        sql = """
            INSERT INTO snapshots (
                snapshot_id, snapshot_type, source, dataset_version_id, metadata, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as c:
            c.execute(sql, (
                record.snapshot_id, record.snapshot_type, record.source, record.dataset_version_id,
                record.metadata, record.created_at_utc
            ))

    def add_job(self, record: StorageJobRecord) -> None:
        sql = """
            INSERT INTO storage_jobs (
                job_id, job_type, status, started_at_utc, finished_at_utc, error, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.transaction() as c:
            c.execute(sql, (
                record.job_id, record.job_type, record.status, record.started_at_utc,
                record.finished_at_utc, record.error, record.metadata
            ))

    # --- FETCHERS ---

    def get_dataset(self, dataset_name: str) -> DatasetRecord | None:
        sql = "SELECT * FROM datasets WHERE dataset_name = ?"
        res = self.execute(sql, (dataset_name,))
        if not res:
            return None
        return DatasetRecord(**dict(res[0]))

    def list_datasets(self) -> list[DatasetRecord]:
        sql = "SELECT * FROM datasets"
        return [DatasetRecord(**dict(row)) for row in self.execute(sql)]

    def list_versions(self, dataset_name: str) -> list[DatasetVersionRecord]:
        ds = self.get_dataset(dataset_name)
        if not ds:
            return []
        sql = "SELECT * FROM dataset_versions WHERE dataset_id = ? ORDER BY version_number DESC"
        return [DatasetVersionRecord(**dict(row)) for row in self.execute(sql, (ds.dataset_id,))]

    def list_files(self, version_id: str) -> list[FileManifestRecord]:
        sql = "SELECT * FROM file_manifests WHERE version_id = ?"
        return [FileManifestRecord(**dict(row)) for row in self.execute(sql, (version_id,))]

    def get_latest_active_version(self, dataset_name: str, symbol: str | None = None, interval: str | None = None) -> DatasetVersionRecord | None:
        # A simple active version fetch. Filtering by symbol/interval could mean finding the version where file_manifests have those partitions.
        ds = self.get_dataset(dataset_name)
        if not ds:
            return None
        sql = "SELECT * FROM dataset_versions WHERE dataset_id = ? AND is_active = 1 ORDER BY version_number DESC LIMIT 1"
        res = self.execute(sql, (ds.dataset_id,))
        if not res:
            return None
        return DatasetVersionRecord(**dict(res[0]))
