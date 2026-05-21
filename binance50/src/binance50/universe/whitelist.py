from pathlib import Path

import yaml

from binance50.config.models import UniverseConfig
from binance50.universe.blacklist import SymbolListPolicy
from binance50.universe.models import UniverseCandidate


def load_whitelist(path: Path) -> SymbolListPolicy:
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


def is_symbol_whitelisted(symbol: str, policy: SymbolListPolicy) -> bool:
    return symbol in policy.symbols


def apply_whitelist_preference(
    candidate: UniverseCandidate, config: UniverseConfig
) -> UniverseCandidate:
    # Whitelist is not an auto-accept. It's handled purely during candidate evaluation/scoring
    # as a preference boost if the candidate passes all rules.
    # We will mark it with a note or warning flag to be picked up by scoring if needed.
    return candidate
