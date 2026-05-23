Please review my changes. I have implemented Phase 12 of the binance50 project.
Features added:
- Indicator V2 core config via AppConfig
- Causal pivot points with strictly backward-looking rules
- Divergence candidates detection
- Multi-timeframe alignment using pandas merge_asof backwards
- Pattern registry and base skeleton adapters
- Feature safety guards against lookahead/repainting
- Typer CLI integration
Tests created:
- test_pivot_detection.py
- test_divergence_detection.py
- test_mtf_alignment.py
- test_feature_quality_v2.py
- test_feature_guard.py
- test_divergence_guard.py
- test_feature_metadata.py

Tests successfully pass for the newly added module logic.
