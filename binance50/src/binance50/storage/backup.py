import shutil
from pathlib import Path
from datetime import datetime, timezone
from binance50.config.models import AppConfig
from binance50.storage.paths import get_backups_dir, get_sqlite_catalog_path, get_manifest_dir

class StorageBackupManager:
    def __init__(self, config: AppConfig):
        self.config = config
        self.backup_dir = get_backups_dir(config)

    def _generate_backup_path(self, prefix: str, reason: str) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_reason = reason.replace(" ", "_").replace("/", "_")
        return self.backup_dir / f"{prefix}_{ts}_{safe_reason}"

    def backup_catalog(self, reason: str) -> Path:
        catalog_path = get_sqlite_catalog_path(self.config)
        if not catalog_path.exists():
            raise FileNotFoundError("Catalog database not found for backup.")

        backup_path = self._generate_backup_path("catalog", reason).with_suffix(".sqlite")
        shutil.copy2(catalog_path, backup_path)
        return backup_path

    def backup_manifests(self, reason: str) -> Path:
        manifest_dir = get_manifest_dir(self.config)
        backup_path = self._generate_backup_path("manifests", reason).with_suffix(".zip")
        if manifest_dir.exists() and any(manifest_dir.iterdir()):
             shutil.make_archive(str(backup_path.with_suffix("")), 'zip', manifest_dir)
        return backup_path

    def backup_storage_metadata(self, reason: str) -> Path:
        cat_path = self.backup_catalog(reason)
        man_path = self.backup_manifests(reason)
        return self.backup_dir

    def list_backups(self) -> list[Path]:
        return sorted(list(self.backup_dir.glob("*")), key=lambda x: x.stat().st_mtime)

    def prune_backups(self, dry_run: bool = True) -> dict:
        backups = self.list_backups()
        max_b = self.config.storage.backup.max_backups

        to_delete = []
        if len(backups) > max_b:
             to_delete = backups[:-max_b]

        if not dry_run:
             for f in to_delete:
                  f.unlink()

        return {
            "total_backups": len(backups),
            "kept": len(backups) - len(to_delete),
            "deleted": len(to_delete),
            "dry_run": dry_run
        }
