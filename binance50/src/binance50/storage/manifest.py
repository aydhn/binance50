import json
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import StorageManifestError
from binance50.storage.catalog_models import FileManifestRecord
from binance50.storage.paths import get_manifest_dir
from binance50.storage.schemas import DatasetSchema


@dataclass
class DatasetManifest:
    manifest_id: str
    dataset_name: str
    dataset_kind: str
    version_id: str
    schema_version: int
    files: list[dict[str, Any]]
    row_count: int
    data_hash: str
    min_time_ms: int | None
    max_time_ms: int | None
    quality_status: str
    created_at_utc: str
    metadata: dict[str, Any]


def build_manifest(
    dataset_name: str,
    version_id: str,
    files: list[Path],
    df: pd.DataFrame,
    schema: DatasetSchema,
    quality_status: str,
    metadata: dict | None = None,
) -> DatasetManifest:

    file_records = []
    # Note: In a real app we'd query the parquet store to calculate hashes
    for f in files:
        file_records.append(
            {
                "file_id": uuid.uuid4().hex,
                "file_path": str(f.absolute()),  # Or relative
                "file_format": "parquet",
                "compression": "zstd",
                "row_count": len(df) // len(files) if files else 0,  # Approximation
                "file_size_bytes": f.stat().st_size if f.exists() else 0,
                "file_hash": "hash_placeholder",
                "partition_values": {},
            }
        )

    min_t = None
    max_t = None
    if schema.timestamp_column and schema.timestamp_column in df.columns and not df.empty:
        min_t = int(df[schema.timestamp_column].min())
        max_t = int(df[schema.timestamp_column].max())

    return DatasetManifest(
        manifest_id=uuid.uuid4().hex,
        dataset_name=dataset_name,
        dataset_kind=schema.dataset_kind.value,
        version_id=version_id,
        schema_version=schema.version,
        files=file_records,
        row_count=len(df),
        data_hash="df_hash_placeholder",
        min_time_ms=min_t,
        max_time_ms=max_t,
        quality_status=quality_status,
        created_at_utc=datetime.now(UTC).isoformat(),
        metadata=metadata or {},
    )


def write_manifest(manifest: DatasetManifest, config: AppConfig) -> Path:
    man_dir = get_manifest_dir(config)
    path = man_dir / f"{manifest.dataset_name}_{manifest.version_id}.json"

    # Redact secrets from metadata
    safe_metadata = manifest.metadata.copy()
    for k in safe_metadata:
        if any(secret in k.lower() for secret in ["key", "secret", "token", "pwd"]):
            safe_metadata[k] = "***REDACTED***"
    manifest.metadata = safe_metadata

    with open(path, "w") as f:
        json.dump(asdict(manifest), f, indent=2)
    return path


def read_manifest(path: Path) -> DatasetManifest:
    try:
        with open(path) as f:
            data = json.load(f)
            return DatasetManifest(**data)
    except Exception as e:
        raise StorageManifestError(f"Failed to read manifest: {e}")


def validate_manifest(manifest: DatasetManifest, config: AppConfig) -> None:
    if not manifest.files and manifest.row_count > 0:
        raise StorageManifestError("Manifest claims rows but has no files")

    # Real logic would verify file hashes against physical files here


def manifest_to_catalog_records(manifest: DatasetManifest) -> list[FileManifestRecord]:
    records = []
    for f in manifest.files:
        records.append(
            FileManifestRecord(
                file_id=f["file_id"],
                version_id=manifest.version_id,
                dataset_name=manifest.dataset_name,
                file_path=f["file_path"],
                file_format=f["file_format"],
                compression=f["compression"],
                row_count=f["row_count"],
                file_size_bytes=f["file_size_bytes"],
                file_hash=f["file_hash"],
                min_open_time=manifest.min_time_ms or 0,
                max_open_time=manifest.max_time_ms or 0,
                partition_values=json.dumps(f["partition_values"]),
                created_at_utc=manifest.created_at_utc,
            )
        )
    return records
