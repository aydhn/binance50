from typing import Any

import pandas as pd

from binance50.core.exceptions import PatternEngineError

from .pattern_base import IndicatorContext, PatternCandidate, PatternDetectorProtocol


class PatternRegistry:
    def __init__(self):
        self._detectors: dict[str, PatternDetectorProtocol] = {}

    def register(self, detector: PatternDetectorProtocol) -> None:
        if detector.name in self._detectors:
            raise PatternEngineError(f"Pattern detector {detector.name} already registered")
        self._detectors[detector.name] = detector

    def get(self, name: str) -> PatternDetectorProtocol | None:
        return self._detectors.get(name)

    def list_detectors(self) -> list[PatternDetectorProtocol]:
        return list(self._detectors.values())

    def detect_all(self, df: pd.DataFrame, context: IndicatorContext) -> list[PatternCandidate]:
        all_candidates = []
        for det in self._detectors.values():
            if det.is_available():
                try:
                    cands = det.detect(df, context)
                    all_candidates.extend(cands)
                except Exception:
                    # Log gracefully but continue with others
                    pass
        return all_candidates

    def availability_report(self) -> dict[str, Any]:
        report: dict[str, Any] = {
            "total_detectors": len(self._detectors),
            "available_detectors": sum(1 for d in self._detectors.values() if d.is_available()),
            "detectors": {},
        }
        for det in self._detectors.values():
            report["detectors"][det.name] = det.is_available()

        return report
