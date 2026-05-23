from dataclasses import dataclass


@dataclass
class DatasetRecord:
    dataset_id: str
    dataset_name: str
    dataset_kind: str
    schema_version: int
    status: str
    created_at_utc: str
    updated_at_utc: str
    description: str


@dataclass
class DatasetVersionRecord:
    version_id: str
    dataset_id: str
    version_number: int
    source: str
    row_count: int
    start_time_ms: int
    end_time_ms: int
    data_hash: str
    manifest_path: str
    quality_status: str
    created_at_utc: str
    is_active: int  # 0 or 1 for sqlite


@dataclass
class FileManifestRecord:
    file_id: str
    version_id: str
    dataset_name: str
    file_path: str
    file_format: str
    compression: str
    row_count: int
    file_size_bytes: int
    file_hash: str
    min_open_time: int
    max_open_time: int
    partition_values: str  # JSON string
    created_at_utc: str


@dataclass
class QualityIndexRecord:
    quality_id: str
    version_id: str
    dataset_name: str
    symbol: str
    interval: str
    issue_type: str
    severity: str
    issue_count: int
    first_seen_open_time: int
    last_seen_open_time: int
    created_at_utc: str


@dataclass
class SnapshotRecord:
    snapshot_id: str
    snapshot_type: str
    source: str
    dataset_version_id: str
    metadata: str  # JSON string
    created_at_utc: str


@dataclass
class StorageJobRecord:
    job_id: str
    job_type: str
    status: str
    started_at_utc: str
    finished_at_utc: str | None
    error: str | None
    metadata: str  # JSON string
