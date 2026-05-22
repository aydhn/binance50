import uuid
from datetime import UTC, datetime

from binance50.config.models import AppConfig
from binance50.core.exceptions import DatasetRegistryError
from binance50.storage.catalog_models import DatasetRecord, DatasetVersionRecord
from binance50.storage.manifest import DatasetManifest
from binance50.storage.schemas import DatasetKind, DatasetSchema
from binance50.storage.sqlite_catalog import SQLiteCatalog


class DatasetRegistry:
    def __init__(self, config: AppConfig, catalog: SQLiteCatalog):
        self.config = config
        self.catalog = catalog

    def _assert_dataset_allowed(self, dataset_name: str) -> None:
        if self.config.storage.safety.block_unknown_dataset_names:
            if dataset_name not in self.config.storage.datasets.allowed_dataset_names:
                raise DatasetRegistryError(f"Dataset {dataset_name} is not in allowed_dataset_names")

    def register_dataset(self, dataset_name: str, dataset_kind: DatasetKind, schema: DatasetSchema, description: str | None = None) -> DatasetRecord:
        self._assert_dataset_allowed(dataset_name)

        existing = self.catalog.get_dataset(dataset_name)
        now = datetime.now(UTC).isoformat()

        if existing:
            existing.schema_version = schema.version
            existing.updated_at_utc = now
            if description:
                existing.description = description
            record = existing
        else:
            record = DatasetRecord(
                dataset_id=uuid.uuid4().hex,
                dataset_name=dataset_name,
                dataset_kind=dataset_kind.value,
                schema_version=schema.version,
                status="active",
                created_at_utc=now,
                updated_at_utc=now,
                description=description or ""
            )

        self.catalog.upsert_dataset(record)
        return record

    def register_version(self, dataset_name: str, manifest: DatasetManifest, source: str, quality_status: str) -> DatasetVersionRecord:
        dataset = self.catalog.get_dataset(dataset_name)
        if not dataset:
            raise DatasetRegistryError(f"Dataset {dataset_name} not registered. Call register_dataset first.")

        latest_version = self.catalog.list_versions(dataset_name)
        v_num = latest_version[0].version_number + 1 if latest_version else 1

        record = DatasetVersionRecord(
            version_id=manifest.version_id,
            dataset_id=dataset.dataset_id,
            version_number=v_num,
            source=source,
            row_count=manifest.row_count,
            start_time_ms=manifest.min_time_ms or 0,
            end_time_ms=manifest.max_time_ms or 0,
            data_hash=manifest.data_hash,
            manifest_path=f"{manifest.dataset_name}_{manifest.version_id}.json",
            quality_status=quality_status,
            created_at_utc=datetime.now(UTC).isoformat(),
            is_active=0 # Default to inactive, requires explicit activation
        )
        self.catalog.create_dataset_version(record)
        return record

    def activate_version(self, version_id: str) -> None:
        # Fetch the version to get dataset_id
        res = self.catalog.execute("SELECT dataset_id FROM dataset_versions WHERE version_id = ?", (version_id,))
        if not res:
             raise DatasetRegistryError(f"Version {version_id} not found")
        dataset_id = res[0][0]

        with self.catalog.transaction() as c:
            # Deactivate all
            c.execute("UPDATE dataset_versions SET is_active = 0 WHERE dataset_id = ?", (dataset_id,))
            # Activate target
            c.execute("UPDATE dataset_versions SET is_active = 1 WHERE version_id = ?", (version_id,))

    def deactivate_version(self, version_id: str) -> None:
        with self.catalog.transaction() as c:
            c.execute("UPDATE dataset_versions SET is_active = 0 WHERE version_id = ?", (version_id,))

    def get_active_version(self, dataset_name: str) -> DatasetVersionRecord | None:
        return self.catalog.get_latest_active_version(dataset_name)

    def list_registered_datasets(self) -> list[DatasetRecord]:
        return self.catalog.list_datasets()
