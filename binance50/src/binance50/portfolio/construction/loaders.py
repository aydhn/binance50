from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioConstructionInputError


class PortfolioConstructionLoader:
    def __init__(self, data_warehouse=None, cache=None):
        self.warehouse = data_warehouse
        self.cache = cache

    def load_portfolio_selection_result(self, run_id: str, config: AppConfig) -> dict[str, Any]:
        if not config.portfolio_construction.inputs.require_portfolio_selection_result:
            return {}
        return {}

    def load_latest_portfolio_selection(self, symbol: str, market_scope: str, interval: str, config: AppConfig) -> dict[str, Any]:
        return {}

    def extract_selected_candidates(self, selection_result: dict[str, Any], config: AppConfig) -> list[Any]:
        candidates = selection_result.get("selected_sandbox_candidates", [])
        if config.portfolio_construction.inputs.require_selected_sandbox_candidates and not candidates:
            raise PortfolioConstructionInputError("No selected sandbox candidates found in selection result.")

        valid_candidates = []
        for c in candidates:
            if isinstance(c, dict):
                is_blocked = c.get("blocked_from_execution", False) or c.get("blocked_from_live_engine", False)
                if config.portfolio_construction.inputs.require_blocked_flags and not is_blocked and config.portfolio_construction.inputs.reject_execution_fields:
                    raise PortfolioConstructionInputError(f"Candidate {c.get('symbol')} missing required blocked flags.")

                intent = c.get("intent", "")
                if config.portfolio_construction.inputs.reject_live_paper_intent and intent in ("live", "paper"):
                    raise PortfolioConstructionInputError(f"Candidate {c.get('symbol')} has forbidden live/paper intent.")
                valid_candidates.append(c)
            else:
                is_blocked = getattr(c, "blocked_from_execution", False) or getattr(c, "blocked_from_live_engine", False)
                if config.portfolio_construction.inputs.require_blocked_flags and not is_blocked and config.portfolio_construction.inputs.reject_execution_fields:
                    raise PortfolioConstructionInputError(f"Candidate {getattr(c, 'symbol', 'unknown')} missing required blocked flags.")

                intent = getattr(c, "intent", "")
                if config.portfolio_construction.inputs.reject_live_paper_intent and str(intent) in ("live", "paper", "PortfolioSandboxIntent.live"):
                    raise PortfolioConstructionInputError(f"Candidate {getattr(c, 'symbol', 'unknown')} has forbidden live/paper intent.")
                valid_candidates.append(c)

        min_required = config.portfolio_construction.inputs.min_selected_candidates
        if len(valid_candidates) < min_required:
            raise PortfolioConstructionInputError(f"Found {len(valid_candidates)} candidates, minimum required is {min_required}.")

        return valid_candidates

    def load_market_data_for_candidates(self, candidates: list[Any], config: AppConfig) -> dict[str, pd.DataFrame]:
        return {}

    def validate_loaded_inputs(self, selection_result: dict[str, Any], candidates: list[Any], market_data: dict[str, pd.DataFrame], config: AppConfig) -> None:
        if config.portfolio_construction.inputs.require_selected_sandbox_candidates and not candidates:
            raise PortfolioConstructionInputError("No candidates provided for validation.")
        min_required = config.portfolio_construction.inputs.min_selected_candidates
        if len(candidates) < min_required:
            raise PortfolioConstructionInputError(f"Found {len(candidates)} candidates, minimum required is {min_required}.")

    def build_loader_report(self, candidates: list[Any], market_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        return {
            "candidates_loaded": len(candidates),
            "market_data_symbols": list(market_data.keys())
        }
