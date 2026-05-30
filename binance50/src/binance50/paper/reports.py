from binance50.paper.models import PaperExecutionRunResult

def build_paper_execution_summary(result: PaperExecutionRunResult) -> dict:
    return {
        "run_id": result.run_id,
        "mode": result.mode.value,
        "success": result.success,
        "order_count": len(result.paper_orders),
        "fill_count": len(result.paper_fills)
    }

def build_paper_order_table(orders: list, limit: int = 100) -> list[dict]:
    return [o.dict() for o in orders[:limit]]

def build_paper_fill_table(fills: list, limit: int = 100) -> list[dict]:
    return [f.dict() for f in fills[:limit]]

def build_paper_ledger_report(events: list) -> dict:
    return {"events": len(events)}

def build_paper_balance_report(snapshots: list) -> dict:
    return {"snapshots": len(snapshots)}

def build_paper_positions_report(positions: list) -> dict:
    return {"positions": len(positions)}

def build_paper_pnl_report_view(result: PaperExecutionRunResult) -> dict:
    return result.pnl_report

def build_paper_event_report(events: list) -> dict:
    return {"events": len(events)}

def build_paper_health_report(config) -> dict:
    return {"status": "healthy"}
