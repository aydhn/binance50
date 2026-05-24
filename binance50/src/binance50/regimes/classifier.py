from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.regimes.confidence import compute_rule_confidence
from binance50.regimes.features import build_regime_features
from binance50.regimes.models import (
    RegimeClassification,
    RegimeMethod,
    RegimeRunMetadata,
    RegimeRunRequest,
    RegimeRunResult,
)
from binance50.regimes.rules import classify_row_rule_based
from binance50.regimes.smoothing import smooth_regime_sequence
from binance50.regimes.stability import compute_regime_stability
from binance50.regimes.transitions import add_transition_flags, detect_regime_transitions


class RegimeClassifier:
    def __init__(self, config: AppConfig, method: RegimeMethod = RegimeMethod.rule_based):
        self.config = config
        self.method = method

    def prepare_input(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.copy()

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        return build_regime_features(df, self.config)

    def classify_rule_based(self, feature_df: pd.DataFrame) -> list[RegimeClassification]:
        classifications = []
        for i in range(len(feature_df)):
            row = feature_df.iloc[i]
            decision = classify_row_rule_based(row, self.config)
            conf = compute_rule_confidence(decision, row, self.config)

            c = RegimeClassification(
                regime_id=f"{row['symbol']}_{int(row['open_time'])}",
                symbol=row["symbol"],
                market_scope=row.get("market_scope", "spot"),
                interval=row.get("interval", "1m"),
                open_time=int(row["open_time"]),
                close_time=int(row.get("close_time", 0)),
                regime=decision.regime,
                family=decision.family,
                method=RegimeMethod.rule_based,
                confidence=conf,
                risk_context=decision.risk_context,
                explanation={"reasons": decision.reasons, "evidence": decision.feature_evidence},
                feature_snapshot={"adx": decision.feature_evidence.get("adx", 0.0)},
                created_at_utc=0,
            )
            classifications.append(c)
        return classifications

    def classify_with_optional_model(
        self, feature_df: pd.DataFrame, method: RegimeMethod
    ) -> list[RegimeClassification]:
        return self.classify_rule_based(feature_df)

    def smooth_classifications(
        self, classifications: list[RegimeClassification]
    ) -> list[RegimeClassification]:
        return smooth_regime_sequence(classifications, self.config)

    def detect_transitions(self, classifications: list[RegimeClassification]) -> list[Any]:
        return detect_regime_transitions(classifications, self.config)

    def build_metadata(
        self, request: RegimeRunRequest, class_count: int, trans_count: int
    ) -> RegimeRunMetadata:
        return RegimeRunMetadata(
            symbol=request.symbol,
            market_scope=request.market_scope,
            interval=request.interval,
            row_count=class_count,
            classification_count=class_count,
            transition_count=trans_count,
            input_hash="dummy",
            output_hash="dummy",
            config_hash="dummy",
            method=self.method,
            generated_at_utc=0,
        )

    def classify(self, df: pd.DataFrame, request: RegimeRunRequest) -> RegimeRunResult:
        df_in = self.prepare_input(df)
        df_feat = self.build_features(df_in)

        if self.method == RegimeMethod.rule_based:
            classifications = self.classify_rule_based(df_feat)
        else:
            classifications = self.classify_with_optional_model(df_feat, self.method)

        classifications = self.smooth_classifications(classifications)
        classifications = compute_regime_stability(classifications, self.config)
        transitions = self.detect_transitions(classifications)
        classifications = add_transition_flags(classifications, transitions, self.config)

        metadata = self.build_metadata(request, len(classifications), len(transitions))

        return RegimeRunResult(
            request=request,
            classifications=classifications,
            transitions=transitions,
            metadata=metadata,
            success=True,
        )

    def save_to_cache(self, result: RegimeRunResult):
        pass

    def save_to_warehouse(self, result: RegimeRunResult):
        pass
