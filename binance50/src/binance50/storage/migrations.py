from dataclasses import dataclass
from typing import Any
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.core.exceptions import StorageMigrationError, DestructiveActionBlockedError
from binance50.storage.sqlite_catalog import SQLiteCatalog

@dataclass
class Migration:
    version: int
    name: str
    sql_statements: list[str]
    destructive: bool
    created_at_utc: str

MIGRATIONS = [
    Migration(
        version=1,
        name="001_init_catalog_tables",
        sql_statements=[
            """CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at_utc TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT PRIMARY KEY,
                dataset_name TEXT UNIQUE NOT NULL,
                dataset_kind TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                description TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS dataset_versions (
                version_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                source TEXT,
                row_count INTEGER NOT NULL,
                start_time_ms INTEGER,
                end_time_ms INTEGER,
                data_hash TEXT,
                manifest_path TEXT,
                quality_status TEXT,
                created_at_utc TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id)
            )""",
            """CREATE TABLE IF NOT EXISTS file_manifests (
                file_id TEXT PRIMARY KEY,
                version_id TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_format TEXT NOT NULL,
                compression TEXT,
                row_count INTEGER NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                file_hash TEXT,
                min_open_time INTEGER,
                max_open_time INTEGER,
                partition_values TEXT,
                created_at_utc TEXT NOT NULL,
                FOREIGN KEY(version_id) REFERENCES dataset_versions(version_id)
            )"""
        ],
        destructive=False,
        created_at_utc="2024-05-22T00:00:00Z"
    ),
    Migration(
        version=2,
        name="002_add_quality_index",
        sql_statements=[
            """CREATE TABLE IF NOT EXISTS quality_index (
                quality_id TEXT PRIMARY KEY,
                version_id TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                issue_count INTEGER NOT NULL,
                first_seen_open_time INTEGER,
                last_seen_open_time INTEGER,
                created_at_utc TEXT NOT NULL,
                FOREIGN KEY(version_id) REFERENCES dataset_versions(version_id)
            )"""
        ],
        destructive=False,
        created_at_utc="2024-05-22T00:00:00Z"
    ),
    Migration(
        version=3,
        name="003_add_data_index",
        sql_statements=[
            """CREATE TABLE IF NOT EXISTS data_index (
                coverage_id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                market_scope TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                start_time_ms INTEGER NOT NULL,
                end_time_ms INTEGER NOT NULL,
                row_count INTEGER NOT NULL,
                gap_count INTEGER NOT NULL,
                quality_status TEXT NOT NULL,
                version_id TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                FOREIGN KEY(version_id) REFERENCES dataset_versions(version_id)
            )"""
        ],
        destructive=False,
        created_at_utc="2024-05-22T00:00:00Z"
    ),
    Migration(
        version=4,
        name="004_add_storage_jobs_snapshots",
        sql_statements=[
            """CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                snapshot_type TEXT NOT NULL,
                source TEXT NOT NULL,
                dataset_version_id TEXT,
                metadata TEXT,
                created_at_utc TEXT NOT NULL,
                FOREIGN KEY(dataset_version_id) REFERENCES dataset_versions(version_id)
            )""",
            """CREATE TABLE IF NOT EXISTS storage_jobs (
                job_id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at_utc TEXT NOT NULL,
                finished_at_utc TEXT,
                error TEXT,
                metadata TEXT
            )"""
        ],
        destructive=False,
        created_at_utc="2024-05-22T00:00:00Z"
    )
]

class StorageMigrationManager:
    def __init__(self, config: AppConfig, catalog: SQLiteCatalog):
        self.config = config
        self.catalog = catalog

    def get_current_version(self) -> int:
        try:
            # Check if schema_migrations table exists
            res = self.catalog.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            if not res:
                return 0

            res = self.catalog.execute("SELECT MAX(version) FROM schema_migrations")
            return res[0][0] or 0
        except Exception:
            return 0

    def apply_migrations(self) -> None:
        current_version = self.get_current_version()

        migrations_to_apply = [m for m in MIGRATIONS if m.version > current_version]

        if not migrations_to_apply:
            return

        if self.config.storage.sqlite.backup_before_migration and current_version > 0:
            from binance50.storage.backup import StorageBackupManager
            backup_mgr = StorageBackupManager(self.config)
            backup_mgr.backup_catalog(f"pre_migration_to_{migrations_to_apply[-1].version}")

        for m in sorted(migrations_to_apply, key=lambda x: x.version):
            if m.destructive and not self.config.storage.safety.allow_destructive_migration:
                raise DestructiveActionBlockedError(f"Migration {m.name} is destructive and is blocked by safety config.")

            try:
                with self.catalog.transaction() as c:
                    for sql in m.sql_statements:
                        c.execute(sql)

                    c.execute(
                        "INSERT INTO schema_migrations (version, name, applied_at_utc) VALUES (?, ?, ?)",
                        (m.version, m.name, datetime.now(timezone.utc).isoformat())
                    )
            except Exception as e:
                 raise StorageMigrationError(f"Failed to apply migration {m.name}: {e}")

    def list_migrations(self) -> list[Migration]:
        return MIGRATIONS

    def validate_migration_state(self) -> None:
        current_version = self.get_current_version()
        latest_version = max([m.version for m in MIGRATIONS] + [0])
        if current_version < latest_version:
             raise StorageMigrationError(f"Database schema is out of date. Current: {current_version}, Latest: {latest_version}")
