from dataclasses import dataclass

from binance50.config.models import AppConfig
from binance50.core.exceptions import DestructiveActionBlockedError
from binance50.storage.sqlite_catalog import SQLiteCatalog


@dataclass
class RetentionPlan:
    dataset_name: str
    versions_to_delete: list[str]
    versions_to_archive: list[str]
    files_to_delete: list[str]
    dry_run: bool

@dataclass
class RetentionResult:
    dataset_name: str
    versions_deleted: int
    versions_archived: int
    files_deleted: int
    dry_run: bool

class StorageRetentionManager:
    def __init__(self, config: AppConfig, catalog: SQLiteCatalog):
        self.config = config
        self.catalog = catalog

    def plan_retention(self, dataset_name: str) -> RetentionPlan:
        # Mock simplistic retention plan
        versions = self.catalog.list_versions(dataset_name)
        to_archive = []
        to_delete = []

        if not self.config.storage.retention.enabled:
             return RetentionPlan(dataset_name, [], [], [], dry_run=True)

        # Mock logic
        if len(versions) > self.config.storage.retention.max_versions_per_dataset:
             excess = versions[self.config.storage.retention.max_versions_per_dataset:]
             for v in excess:
                  if self.config.storage.retention.archive_old_versions:
                       to_archive.append(v.version_id)
                  else:
                       to_delete.append(v.version_id)

        return RetentionPlan(
             dataset_name=dataset_name,
             versions_to_delete=to_delete,
             versions_to_archive=to_archive,
             files_to_delete=[],
             dry_run=True
        )

    def apply_retention(self, plan: RetentionPlan, dry_run: bool = True) -> RetentionResult:
        if not dry_run and plan.versions_to_delete and not self.config.storage.safety.allow_delete:
             raise DestructiveActionBlockedError("Retention requires allow_delete=true to delete versions")

        if not dry_run:
             # Apply logic to database
             with self.catalog.transaction() as c:
                  for v in plan.versions_to_archive:
                       # Mock status change
                       c.execute("UPDATE dataset_versions SET quality_status='archived' WHERE version_id=?", (v,))
                  for v in plan.versions_to_delete:
                       c.execute("DELETE FROM file_manifests WHERE version_id=?", (v,))
                       c.execute("DELETE FROM dataset_versions WHERE version_id=?", (v,))

        return RetentionResult(
             dataset_name=plan.dataset_name,
             versions_deleted=len(plan.versions_to_delete),
             versions_archived=len(plan.versions_to_archive),
             files_deleted=len(plan.files_to_delete),
             dry_run=dry_run
        )
