import shutil
import tempfile
import os
from pathlib import Path
from typing import Any
from binance50.config.models import AppConfig
from binance50.storage.paths import get_storage_root, get_parquet_root, get_sqlite_catalog_path

class StorageHealthService:
    def __init__(self, config: AppConfig):
        self.config = config

    def check(self) -> dict[str, Any]:
        return {
            "catalog": self.check_catalog(),
            "parquet_root": self.check_parquet_root(),
            "free_space": self.check_free_space(),
            "permissions": self.check_permissions(),
            "status": "healthy"
        }

    def check_catalog(self) -> dict[str, Any]:
        path = get_sqlite_catalog_path(self.config)
        return {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0
        }

    def check_parquet_root(self) -> dict[str, Any]:
        path = get_parquet_root(self.config)
        return {
            "path": str(path),
            "exists": path.exists()
        }

    def check_free_space(self) -> dict[str, Any]:
        path = get_storage_root(self.config)
        if not path.exists():
            return {"status": "unknown"}
        total, used, free = shutil.disk_usage(path)
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "free_pct": round(free / total * 100, 2) if total > 0 else 0
        }

    def check_permissions(self) -> dict[str, Any]:
        root = get_storage_root(self.config)
        status = {"read": False, "write": False}
        if not root.exists():
            return status

        # check read
        status["read"] = os.access(root, os.R_OK)

        # check write via temp file
        try:
            fd, path = tempfile.mkstemp(dir=root)
            os.close(fd)
            os.unlink(path)
            status["write"] = True
        except Exception:
            status["write"] = False

        return status
