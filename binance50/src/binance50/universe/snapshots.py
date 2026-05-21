import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from binance50.core.enums import MarketScope


class UniverseSnapshot(BaseModel):
    snapshot_id: str
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))
    market_scope: MarketScope
    exchange_info_payload: dict[str, Any]
    ticker_24h_payload: list[dict[str, Any]] | dict[str, Any]
    book_ticker_payload: list[dict[str, Any]] | dict[str, Any]
    source: str = "fixture"
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_snapshot_from_payloads(
    snapshot_id: str,
    market_scope: MarketScope,
    exchange_info_payload: dict[str, Any],
    ticker_24h_payload: list[dict[str, Any]] | dict[str, Any],
    book_ticker_payload: list[dict[str, Any]] | dict[str, Any],
    source: str = "fixture",
) -> UniverseSnapshot:
    return UniverseSnapshot(
        snapshot_id=snapshot_id,
        market_scope=market_scope,
        exchange_info_payload=exchange_info_payload,
        ticker_24h_payload=ticker_24h_payload,
        book_ticker_payload=book_ticker_payload,
        source=source,
    )


def load_snapshot_from_files(
    exchange_info_path: Path,
    ticker_path: Path,
    book_path: Path,
    market_scope: MarketScope,
) -> UniverseSnapshot:
    with open(exchange_info_path) as f:
        exchange_info_payload = json.load(f)

    with open(ticker_path) as f:
        ticker_24h_payload = json.load(f)

    with open(book_path) as f:
        book_ticker_payload = json.load(f)

    snapshot_id = f"{market_scope.value}_fixture_snapshot"

    return build_snapshot_from_payloads(
        snapshot_id=snapshot_id,
        market_scope=market_scope,
        exchange_info_payload=exchange_info_payload,
        ticker_24h_payload=ticker_24h_payload,
        book_ticker_payload=book_ticker_payload,
        source="fixture",
    )


def snapshot_to_dict(snapshot: UniverseSnapshot) -> dict[str, Any]:
    # Using model_dump with mode='json' to handle datetime serialization
    return snapshot.model_dump(mode="json")


def validate_snapshot(snapshot: UniverseSnapshot) -> None:
    if not snapshot.exchange_info_payload:
        raise ValueError("Snapshot missing exchange_info_payload")
    if not snapshot.ticker_24h_payload:
        raise ValueError("Snapshot missing ticker_24h_payload")
    if not snapshot.book_ticker_payload:
        raise ValueError("Snapshot missing book_ticker_payload")
