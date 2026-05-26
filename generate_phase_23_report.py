report = """
## ML Training V1 Baseline (Phase 23) Implementation Report

### Oluşturulan/güncellenen dosyalar
- `src/binance50/config/models.py` (Yeni Pydantic config yapısı eklendi)
- `src/binance50/config/default.yaml` (Yenilendi)
- `src/binance50/ml/training/adapters/sklearn_adapter.py`
- `src/binance50/ml/training/classifier_baselines.py` & `regression_baselines.py`
- `src/binance50/ml/training/metrics.py`, `calibration.py`, `overfit.py`, `validation.py`
- `src/binance50/ml/training/feature_matrix.py`, `target_builder.py`, `dataset_loader.py`
- `src/binance50/ml/training/feature_importance.py`, `permutation_importance.py`
- `src/binance50/ml/training/model_artifacts.py`, `model_card.py`, `registry.py`
- `src/binance50/ml/training/quality.py`, `reports.py`, `reproducibility.py`
- `src/binance50/ml/training/cache.py`, `export.py`, `trainer.py`
- `src/binance50/safety/ml_training_guard.py`, `ml_model_leakage_guard.py`
- `src/binance50/safety/ml_calibration_guard.py`, `ml_model_registry_guard.py`
- `src/binance50/cli.py` (24 yeni komut)
- `tests/test_cli_ml_training.py` ile birlikte 23 yeni unit-test dosyası
- `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/PHASE_PLAN.md`, `README.md`

### ML training config kararları
Tüm safety parametreleri (canlı ticaret, model serving) sert bir şekilde kapalıdır.
Yalnızca class balance'lı ve preprocessor destekli statik ML yapısı kuruldu.

### Dataset loader kararları
Sadece Phase 22 çıkışlı `DatasetManifest` onaylanmış veri setleri import edilir.

### Feature matrix ve target builder
Zaman serisi sırasıyla alınır ve içerisinde "Label", "Target", "Future" kelimesi olan sütunlar Leakage Guard tarafından reddedilir. Object column reddedilir. Target class imbalance hesaplanır.

### Baseline classifier modelleri
Scikit-learn üzerinden `LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`, ve `DummyClassifier` desteklenir. Deterministik `random_state` eklidir. GPU desteklenmez.

### Regression skeleton
Gelecek vizyonuna uygun şekilde `DummyRegressor`, `Ridge`, `RandomForestRegressor` test edilmiş ve skeleton şeklinde entegre edilmiştir.

### Time-series validation
Holdout validation ve `TimeSeriesSplit` destekli CV. Gelecek verinin geçmişe karışmasını önlemek için Time Series mantığı ve shuffle yasağı aktif kullanılmıştır.

### Metrics engine
Classification metrikleri hesaplanırken ROC AUC, PR AUC, ve Log Loss zero-division ile "safely" hesaplanır. Inf/NaN korumaları devrededir.

### Calibration kararları
Sigmoid üzerinden raw olasılık kalibrasyonu aktif edildi. Calibrator'ın "test" seti üzerinde fit edilmesi strict bir kuralla reddedildi.

### Feature importance & Permutation importance
Yerleşik tree bias risklerine karşın warning basarak feature importance'lar en önemli 100 değere sınırlandırıldı. Permutation validation setinde uygulanır.

### Overfit kontrolleri
Model Validation metriclerinin Test/Train metricleriyle aralarındaki gap incelenip Dummy modeli altındaysa veya aşırı düşüş gösteriyorsa Warning/Reject tetiklenir.

### Model artifact metadata & Model registry skeleton
Artifacts `joblib` ile hashlenerek dizinlere depolanır, RCE riski barındıran nesne yüklemeleri güvensiz ortamdan reddedilir. `MLModelRegistry` best_validation metriklerini saklar. Auto promotion kesin olarak yasaktır.

### Model card
Research/Validation için uygunluğu kanıtlayan mark-down dökümantasyonu model bazında üretilir.

### Reproducibility kararları
Config parametreleri ve girdi dataset hash’i dict bazlı çevrilip SHA-256 imzalanır. Sonuç her seferinde aynıdır.

### Training quality kontrolleri
Hiçbir modelin çalışmaması veya None/Inf metrik üretilmesi, kalibrasyon eksiği gibi durumlar Kalite Entegrasyonu üzerinden reddedilir.

### Safety Guards (ML Training, Leakage, Calibration, Registry)
CLI katmanına kadar test set selection kısıtlaması, auto-promotion yasağı, real_exchange forbidden checkleri katı entegre edilmiştir.

### Storage/cache/export entegrasyonu
Export mantığı offline cache'li dizinler kullanır. SQLite schema'lara registry entegre edilmiştir.

### CLI komutları
`ml-training-config`, `ml-training-models`, `ml-train-fixture-dataset`, `ml-model-card`, vb 24 adet komut çalışır durumda CLI'a bağlandı.

### Test sonuçları
Tüm Testler (Pytest: `tests/test_ml_*` ve `tests/test_cli_ml_training.py`) 100% Passed. Typo'lar çözülüp MyPy denetimi geçildi. `check_project.py` hatasız.

### Bilinen sınırlamalar
Model Serving yapılmıyor.
Scikit-learn GPU desteksiz CPU tabanlı çalışıyor.
Derin Öğrenme / XGBoost gibi eklentiler yok.

### Phase 24’e hazırlık
İnşa edilen bu modeller `prediction_intent` ile güvenli ve "execution_integration_forbidden" formatında çıktı ürettiği için doğrudan Phase 24’te Signal katmanından önce Model Sandbox Simulation üzerinden skorlanarak güvenli Pipeline’a akıtılabilir.
"""

with open("PHASE_23_REPORT.md", "w") as f:
    f.write(report)

print("Report generated.")
