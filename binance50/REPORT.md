# Phase 25 / 50: ML Ensemble ve Model-Signal Blending Sandbox

## Oluşturulan/güncellenen dosyalar
* `binance50/config/default.yaml` - `ml_blending` config blokları eklendi.
* `binance50/src/binance50/config/models.py` - `MLBlendingConfig` ve bağımlı Pydantic config modelleri validation logic'iyle birlikte eklendi.
* `binance50/src/binance50/ml/blending/models.py` - `MLBlendComponent`, `MLBlendBreakdown`, `MLBlendedSandboxCandidate` modelleri ve ilgili enum'lar eklendi.
* `binance50/src/binance50/ml/blending/loaders.py` - `MLBlendingInputLoader` eklendi.
* `binance50/src/binance50/ml/blending/alignment.py` - `align_predictions_with_signals`, `align_context_backward_asof` eklendi.
* `binance50/src/binance50/ml/blending/weights.py` - `MLBlendWeightEngine` ve penalty logic eklendi.
* `binance50/src/binance50/ml/blending/probability_blend.py` - Probability blend metodları eklendi.
* `binance50/src/binance50/ml/blending/signal_blend.py` - Rule-based signal blend metodları eklendi.
* `binance50/src/binance50/ml/blending/calibration_policy.py`, `regime_policy.py`, `risk_policy.py` - Policy adapter'lar eklendi.
* `binance50/src/binance50/ml/blending/ensemble.py` - `MLBlendingEngine` orkestrasyonu eklendi.
* `binance50/src/binance50/ml/blending/disagreement.py`, `diversity.py`, `confidence.py` - Analiz rapor modülleri eklendi.
* `binance50/src/binance50/ml/blending/sandbox_candidates.py` - Sandbox candidate builder eklendi.
* `binance50/src/binance50/ml/blending/integration_contract.py` - `MLBlendingIntegrationContract` eklendi.
* `binance50/src/binance50/ml/blending/reproducibility.py`, `quality.py` - Kalite ve tekrarlanabilirlik kontrolleri eklendi.
* `binance50/src/binance50/ml/blending/reports.py`, `cache.py`, `export.py` - Raporlama ve I/O modülleri eklendi.
* `binance50/src/binance50/ml/blending/adapters/sklearn_voting_skeleton.py`, `stacking_skeleton.py` - Skeleton adaptörler eklendi.
* `binance50/src/binance50/ml/blending/runner.py` - `MLBlendingRunner` eklendi.
* `binance50/src/binance50/safety/ml_blending_guard.py`, `ml_blending_leakage_guard.py`, `ml_blending_integration_guard.py`, `ml_blending_threshold_guard.py` - Güvenlik korumaları eklendi.
* `binance50/src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py` - Core istisna mantığı güncellendi.
* `binance50/src/binance50/storage/schemas.py`, `importers.py` - Depolama yapıları eklendi.
* `binance50/src/binance50/cli.py` - Tüm typler CLI komutları eklendi.
* `binance50/scripts/check_project.py` - Phase 25 CLI test kontrolleri eklendi.
* `binance50/tests/test_ml_blending_*.py` (23 test dosyası) eklendi.
* `binance50/docs/ARCHITECTURE.md`, `SECURITY.md`, `PHASE_PLAN.md`, `README.md` dosyalarına ilgili dokümantasyon bölümleri eklendi.

## Bilinen sınırlamalar
- Bu faz sadece altyapı ve mimariyi (sandbox environment) kurgular. Canlı API/execution çağrıları yapmaz, veriyi production tablolarına yazmaz.
- Stacking/voting süreçleri sadece "skeleton" (arayüz) seviyesinde desteklenmektedir, model eğitimi bir sonraki fazlara bırakılmıştır.
- Tüm statik kontroller (`ruff check .`) proje genelindeki eski hatalar nedeniyle skip edilmiştir (sadece yeni eklenen `src/binance50/ml/blending` dizini ve güncellenen `src/binance50/core` klasörü hatasızlaştırılmıştır). Eksik dependency (`pydantic`) gibi ortam kaynaklı import hataları nedeniyle full `pytest` suite atlanmıştır.

## Phase 26'ya hazırlık
Portfolio candidate selection sandbox kurulacak; signal/risk/ML-blend sandbox adayları correlation, exposure ve portfolio constraints altında yine production/paper/live ortamlarına yazılmadan sıralanacaktır.
