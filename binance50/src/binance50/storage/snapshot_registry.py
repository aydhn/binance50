import json
import uuid
from datetime import UTC, datetime

from binance50.storage.catalog_models import SnapshotRecord
from binance50.storage.sqlite_catalog import SQLiteCatalog


class SnapshotRegistry:
    def __init__(self, catalog: SQLiteCatalog):
        self.catalog = catalog

    def _register(self, snapshot_type: str, source: str, metadata: dict) -> SnapshotRecord:
        record = SnapshotRecord(
            snapshot_id=uuid.uuid4().hex,
            snapshot_type=snapshot_type,
            source=source,
            dataset_version_id="",
            metadata=json.dumps(metadata),
            created_at_utc=datetime.now(UTC).isoformat()
        )
        self.catalog.add_snapshot(record)
        return record

    def register_universe_snapshot(self, source: str, metadata: dict) -> SnapshotRecord:
        return self._register("universe_selection", source, metadata)

    def register_ohlcv_snapshot(self, source: str, metadata: dict) -> SnapshotRecord:
        return self._register("ohlcv_cache", source, metadata)

    def register_stream_replay_snapshot(self, source: str, metadata: dict) -> SnapshotRecord:
        return self._register("stream_replay", source, metadata)

    def list_snapshots(self, snapshot_type: str | None = None) -> list[SnapshotRecord]:
        if snapshot_type:
             sql = "SELECT * FROM snapshots WHERE snapshot_type = ? ORDER BY created_at_utc DESC"
             res = self.catalog.execute(sql, (snapshot_type,))
        else:
             sql = "SELECT * FROM snapshots ORDER BY created_at_utc DESC"
             res = self.catalog.execute(sql)
        return [SnapshotRecord(**dict(r)) for r in res]

    def get_snapshot(self, snapshot_id: str) -> SnapshotRecord | None:
        sql = "SELECT * FROM snapshots WHERE snapshot_id = ?"
        res = self.catalog.execute(sql, (snapshot_id,))
        if res:
             return SnapshotRecord(**dict(res[0]))
        return None

    def link_snapshot_to_dataset(self, snapshot_id: str, version_id: str) -> None:
        sql = "UPDATE snapshots SET dataset_version_id = ? WHERE snapshot_id = ?"
        with self.catalog.transaction() as c:
             c.execute(sql, (version_id, snapshot_id))
