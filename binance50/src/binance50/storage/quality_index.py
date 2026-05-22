import uuid
from datetime import datetime, timezone
from binance50.storage.catalog_models import QualityIndexRecord

class QualityIndex:
    def __init__(self, catalog):
        self.catalog = catalog

    def index_quality_report(self, version_id: str, dataset_name: str, report: dict) -> list[QualityIndexRecord]:
        records = []
        now = datetime.now(timezone.utc).isoformat()

        # Assume report is a dict representation of OHLCVQualityReport from Phase 8
        symbol = report.get("symbol", "UNKNOWN")
        interval = report.get("interval", "UNKNOWN")

        issues = []
        if report.get("gaps_detected"):
            issues.append(("GAP", "high", report.get("gap_count", 1)))
        if report.get("duplicates_detected"):
            issues.append(("DUPLICATE", "medium", report.get("duplicate_count", 1)))
        if report.get("negative_prices_detected"):
            issues.append(("NEGATIVE_PRICE", "critical", 1))

        for issue_type, severity, count in issues:
             record = QualityIndexRecord(
                 quality_id=uuid.uuid4().hex,
                 version_id=version_id,
                 dataset_name=dataset_name,
                 symbol=symbol,
                 interval=interval,
                 issue_type=issue_type,
                 severity=severity,
                 issue_count=count,
                 first_seen_open_time=0, # placeholder
                 last_seen_open_time=0,
                 created_at_utc=now
             )
             records.append(record)
             self.catalog.add_quality_index(record)

        return records

    def summarize_quality(self, dataset_name: str, symbol: str | None = None, interval: str | None = None) -> dict:
        sql = "SELECT severity, COUNT(*) as cnt FROM quality_index WHERE dataset_name = ?"
        params = [dataset_name]
        if symbol:
            sql += " AND symbol = ?"
            params.append(symbol)
        if interval:
            sql += " AND interval = ?"
            params.append(interval)
        sql += " GROUP BY severity"

        res = self.catalog.execute(sql, tuple(params))
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in res:
             if r["severity"] in summary:
                 summary[r["severity"]] = r["cnt"]
        return summary

    def list_quality_issues(self, dataset_name: str, severity: str | None = None) -> list[QualityIndexRecord]:
        sql = "SELECT * FROM quality_index WHERE dataset_name = ?"
        params = [dataset_name]
        if severity:
            sql += " AND severity = ?"
            params.append(severity)

        res = self.catalog.execute(sql, tuple(params))
        return [QualityIndexRecord(**dict(r)) for r in res]

    def assert_dataset_quality_acceptable(self, dataset_name: str, version_id: str) -> None:
        sql = "SELECT COUNT(*) FROM quality_index WHERE version_id = ? AND severity = 'critical'"
        res = self.catalog.execute(sql, (version_id,))
        if res and res[0][0] > 0:
             from binance50.core.exceptions import QualityIndexError
             raise QualityIndexError(f"Critical quality issues found for dataset {dataset_name} version {version_id}")
