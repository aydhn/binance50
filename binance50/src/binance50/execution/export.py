import json
from pathlib import Path

def _write_json(data: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    return path

def _write_jsonl(data: list, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    return path

def export_execution_summary_to_json(result: dict, path: Path) -> Path:
    return _write_json(result, path)

def export_intents_to_jsonl(intents: list, path: Path) -> Path:
    return _write_jsonl([i.__dict__ for i in intents], path)

def export_safety_scans_to_jsonl(scans: list, path: Path) -> Path:
    return _write_jsonl([s.__dict__ for s in scans], path)

def export_dry_runs_to_json(dry_runs: list, path: Path) -> Path:
    return _write_json([d.__dict__ for d in dry_runs], path)

def export_quality_report_to_json(report: dict, path: Path) -> Path:
    return _write_json(report, path)

def export_audit_timeline_to_json(events: list, path: Path) -> Path:
    return _write_jsonl(events, path)
