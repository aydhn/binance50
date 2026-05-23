with open("binance50/src/binance50/storage/schemas.py", "r") as f:
    content = f.read()

new_schema = """
def get_scored_signal_candidates_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="scored_signal_candidates",
        dataset_kind=DatasetKind.SCORED_SIGNAL_CANDIDATES,
        version=1,
        columns=[
            ColumnSchema("scored_signal_id", "string", nullable=False, is_primary_key=True),
            ColumnSchema("source_candidate_id", "string", nullable=False),
            ColumnSchema("symbol", "string", nullable=False, is_primary_key=True),
            ColumnSchema("market_scope", "string", nullable=False, is_primary_key=True),
            ColumnSchema("interval", "string", nullable=False, is_primary_key=True),
            ColumnSchema("open_time", "int64", nullable=False, is_primary_key=True),
            ColumnSchema("close_time", "int64", nullable=True),
            ColumnSchema("direction", "string", nullable=False),
            ColumnSchema("status", "string", nullable=False),
            ColumnSchema("intent", "string", nullable=False),
            ColumnSchema("score", "float64", nullable=False),
            ColumnSchema("score_tier", "string", nullable=False),
            ColumnSchema("confidence", "float64", nullable=False),
            ColumnSchema("plugin_name", "string", nullable=False),
            ColumnSchema("plugin_type", "string", nullable=False),
            ColumnSchema("strategy_strength", "string", nullable=False),
            ColumnSchema("confluence_group_id", "string", nullable=True),
            ColumnSchema("conflicted", "bool", nullable=False),
            ColumnSchema("expired", "bool", nullable=False),
            ColumnSchema("conflict_reasons_json", "string", nullable=False),
            ColumnSchema("score_breakdown_json", "string", nullable=False),
            ColumnSchema("explanation_json", "string", nullable=False),
            ColumnSchema("metadata_json", "string", nullable=False),
            ColumnSchema("created_at_utc", "int64", nullable=False),
            ColumnSchema("config_hash", "string", nullable=False),
        ],
        primary_keys=[
            "market_scope",
            "symbol",
            "interval",
            "open_time",
            "scored_signal_id",
        ],
        partition_columns=["market_scope", "symbol", "interval"],
        timestamp_column="open_time",
        disallowed_column_names=[
            "order_id",
            "quantity",
            "qty",
            "leverage",
            "margin",
            "entry_price",
            "exit_price",
            "stop_loss",
            "take_profit",
            "order_type",
            "position_side"
        ],
    )
"""

if "DatasetKind.SCORED_SIGNAL_CANDIDATES" not in content:
    # 1. Add DatasetKind
    content = content.replace(
        "    STRATEGY_CANDIDATES = \"strategy_candidates\"",
        "    STRATEGY_CANDIDATES = \"strategy_candidates\"\n    SCORED_SIGNAL_CANDIDATES = \"scored_signal_candidates\""
    )

    # 2. Add the schema function
    insert_pos = content.find("def get_schema_registry() -> dict[str, DatasetSchema]:")
    content = content[:insert_pos] + new_schema + "\n\n" + content[insert_pos:]

    # 3. Add to registry
    registry_str = """        "strategy_candidates": get_strategy_candidates_schema(),"""
    new_registry_str = registry_str + """\n        "scored_signal_candidates": get_scored_signal_candidates_schema(),"""
    content = content.replace(registry_str, new_registry_str)

with open("binance50/src/binance50/storage/schemas.py", "w") as f:
    f.write(content)
