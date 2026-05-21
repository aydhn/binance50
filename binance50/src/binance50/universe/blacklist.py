from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from binance50.config.models import UniverseConfig


class SymbolListPolicy(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    assets: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def load_blacklist(path: Path) -> SymbolListPolicy:
    if not path.exists():
        return SymbolListPolicy()

    with open(path) as f:
        try:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return SymbolListPolicy()
            return SymbolListPolicy(
                symbols=data.get("symbols", []),
                assets=data.get("assets", []),
                patterns=data.get("patterns", []),
                notes=data.get("notes", []),
            )
        except Exception:
            return SymbolListPolicy()


def is_asset_excluded(base_asset: str, quote_asset: str, config: UniverseConfig) -> bool:
    excluded = set(config.exclude_assets)
    return base_asset in excluded or quote_asset in excluded


def matches_excluded_pattern(symbol: str, patterns: list[str]) -> bool:
    return any(pattern in symbol for pattern in patterns)


def is_symbol_blacklisted(symbol: str, policy: SymbolListPolicy, config: UniverseConfig) -> bool:
    if symbol in policy.symbols:
        return True

    if matches_excluded_pattern(symbol, policy.patterns):
        return True

    return bool(matches_excluded_pattern(symbol, config.exclude_symbol_patterns))
