import pandas as pd
from typing import Dict, List, Optional, Any
from binance50.core.exceptions import PatternEngineError
from .pattern_base import PatternDetectorProtocol, PatternCandidate, IndicatorContext

class PatternRegistry:
    def __init__(self):
        self._detectors: Dict[str, PatternDetectorProtocol] = {}

    def register(self, detector: PatternDetectorProtocol) -> None:
        if detector.name in self._detectors:
            raise PatternEngineError(f"Pattern detector {detector.name} already registered")
        self._detectors[detector.name] = detector

    def get(self, name: str) -> Optional[PatternDetectorProtocol]:
        return self._detectors.get(name)

    def list_detectors(self) -> List[PatternDetectorProtocol]:
        return list(self._detectors.values())

    def detect_all(self, df: pd.DataFrame, context: IndicatorContext) -> List[PatternCandidate]:
        all_candidates = []
        for det in self._detectors.values():
            if det.is_available():
                try:
                    cands = det.detect(df, context)
                    all_candidates.extend(cands)
                except Exception as e:
                    # Log gracefully but continue with others
                    pass
        return all_candidates

    def availability_report(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "total_detectors": len(self._detectors),
            "available_detectors": sum(1 for d in self._detectors.values() if d.is_available()),
            "detectors": {}
        }
        for det in self._detectors.values():
            report["detectors"][det.name] = det.is_available()

        return report
