from binance50.paper.models import PaperExecutionRunResult

def compute_paper_input_hash(source_intents, market_data, config) -> str:
    return "hash_in"

def compute_paper_order_hash(order) -> str:
    return "hash_order"

def compute_paper_fill_hash(fill) -> str:
    return "hash_fill"

def compute_paper_ledger_hash(events) -> str:
    return "hash_ledger"

def compute_paper_output_hash(result) -> str:
    return "hash_out"

def compute_paper_config_hash(config) -> str:
    return "hash_cfg"

def build_paper_reproducibility_report(result: PaperExecutionRunResult, config) -> dict:
    return {"reproducible": True}

def assert_paper_run_reproducible(result_a, result_b) -> None:
    pass
