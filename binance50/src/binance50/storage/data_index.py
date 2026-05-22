import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
import pandas as pd
from binance50.storage.sqlite_catalog import SQLiteCatalog

@dataclass
class DataCoverageRecord:
    coverage_id: str
    dataset_name: str
    market_scope: str
    symbol: str
    interval: str
    start_time_ms: int
    end_time_ms: int
    row_count: int
    gap_count: int
    quality_status: str
    version_id: str
    updated_at_utc: str

class DataIndex:
    def __init__(self, catalog: SQLiteCatalog):
        self.catalog = catalog

    def build_coverage_from_ohlcv(self, df: pd.DataFrame, version_id: str, quality_status: str = "pass") -> list[DataCoverageRecord]:
        if df.empty:
            return []

        records = []
        now = datetime.now(timezone.utc).isoformat()

        # Group by scope, symbol, interval
        for name, group in df.groupby(['market_scope', 'symbol', 'interval']):
            market_scope, symbol, interval = name
            start_time = int(group['open_time'].min())
            end_time = int(group['open_time'].max())

            records.append(DataCoverageRecord(
                coverage_id=uuid.uuid4().hex,
                dataset_name="ohlcv",
                market_scope=market_scope,
                symbol=symbol,
                interval=interval,
                start_time_ms=start_time,
                end_time_ms=end_time,
                row_count=len(group),
                gap_count=0, # Need to be computed during quality check ideally
                quality_status=quality_status,
                version_id=version_id,
                updated_at_utc=now
            ))

        return records

    def upsert_coverage(self, records: list[DataCoverageRecord]) -> None:
        sql = """
            INSERT INTO data_index (
                coverage_id, dataset_name, market_scope, symbol, interval,
                start_time_ms, end_time_ms, row_count, gap_count, quality_status,
                version_id, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(dataset_name, market_scope, symbol, interval) DO UPDATE SET
                start_time_ms=excluded.start_time_ms,
                end_time_ms=excluded.end_time_ms,
                row_count=excluded.row_count,
                gap_count=excluded.gap_count,
                quality_status=excluded.quality_status,
                version_id=excluded.version_id,
                updated_at_utc=excluded.updated_at_utc
        """
        # Note: Added ON CONFLICT requires a UNIQUE index which we should add to migration.
        # But for now we just do a simpler query or assume standard usage.

        # Safe fallback if unique constraint is missing:
        with self.catalog.transaction() as c:
             for r in records:
                 # Check if exists
                 c.execute("SELECT coverage_id FROM data_index WHERE dataset_name=? AND market_scope=? AND symbol=? AND interval=?",
                           (r.dataset_name, r.market_scope, r.symbol, r.interval))
                 existing = c.fetchone()
                 if existing:
                     # Update
                     update_sql = """
                         UPDATE data_index SET
                             start_time_ms=?, end_time_ms=?, row_count=?, gap_count=?,
                             quality_status=?, version_id=?, updated_at_utc=?
                         WHERE coverage_id=?
                     """
                     c.execute(update_sql, (
                         r.start_time_ms, r.end_time_ms, r.row_count, r.gap_count,
                         r.quality_status, r.version_id, r.updated_at_utc, existing[0]
                     ))
                 else:
                     # Insert
                     c.execute("""
                        INSERT INTO data_index (
                            coverage_id, dataset_name, market_scope, symbol, interval,
                            start_time_ms, end_time_ms, row_count, gap_count, quality_status,
                            version_id, updated_at_utc
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                     """, (
                         r.coverage_id, r.dataset_name, r.market_scope, r.symbol, r.interval,
                         r.start_time_ms, r.end_time_ms, r.row_count, r.gap_count, r.quality_status,
                         r.version_id, r.updated_at_utc
                     ))

    def get_coverage(self, symbol: str, interval: str, market_scope: str) -> DataCoverageRecord | None:
        sql = "SELECT * FROM data_index WHERE symbol=? AND interval=? AND market_scope=?"
        res = self.catalog.execute(sql, (symbol, interval, market_scope))
        if res:
             return DataCoverageRecord(**dict(res[0]))
        return None

    def list_coverage(self, dataset_name: str | None = None) -> list[DataCoverageRecord]:
        if dataset_name:
             sql = "SELECT * FROM data_index WHERE dataset_name=?"
             res = self.catalog.execute(sql, (dataset_name,))
        else:
             res = self.catalog.execute("SELECT * FROM data_index")
        return [DataCoverageRecord(**dict(r)) for r in res]

    def find_missing_coverage(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list[tuple[int, int]]:
        # Extremely simplified logic
        sql = "SELECT start_time_ms, end_time_ms FROM data_index WHERE symbol=? AND interval=?"
        res = self.catalog.execute(sql, (symbol, interval))

        if not res:
            return [(start_ms, end_ms)]

        covered_start = min([r['start_time_ms'] for r in res])
        covered_end = max([r['end_time_ms'] for r in res])

        missing = []
        if start_ms < covered_start:
             missing.append((start_ms, min(end_ms, covered_start - 1)))
        if end_ms > covered_end:
             missing.append((max(start_ms, covered_end + 1), end_ms))

        return missing
