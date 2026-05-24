# Phase 15: Market Regime Classification Report

## Oluşturulan/güncellenen dosyalar
- `src/binance50/regimes/__init__.py`
- `src/binance50/regimes/adapters/__init__.py`
- `src/binance50/regimes/adapters/base.py`
- `src/binance50/regimes/adapters/gmm_adapter.py`
- `src/binance50/regimes/adapters/hmm_adapter.py`
- `src/binance50/regimes/cache.py`
- `src/binance50/regimes/classifier.py`
- `src/binance50/regimes/confidence.py`
- `src/binance50/regimes/context.py`
- `src/binance50/regimes/datasets.py`
- `src/binance50/regimes/export.py`
- `src/binance50/regimes/features.py`
- `src/binance50/regimes/models.py`
- `src/binance50/regimes/quality.py`
- `src/binance50/regimes/reports.py`
- `src/binance50/regimes/rules.py`
- `src/binance50/regimes/smoothing.py`
- `src/binance50/regimes/stability.py`
- `src/binance50/regimes/transitions.py`
- `src/binance50/regimes/validators.py`
- `src/binance50/safety/regime_guard.py`
- `src/binance50/safety/regime_leakage_guard.py`
- `src/binance50/config/models.py` (Güncellendi)
- `config/default.yaml` (Güncellendi)
- `src/binance50/core/exceptions.py` (Güncellendi)
- `src/binance50/core/error_codes.py` (Güncellendi)
- `src/binance50/core/error_classifier.py` (Güncellendi)
- `src/binance50/storage/schemas.py` (Güncellendi)
- `src/binance50/storage/importers.py` (Güncellendi)
- `src/binance50/cli.py` (Güncellendi)
- `scripts/check_project.py` (Güncellendi)
- `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/PHASE_PLAN.md`, `README.md` (Güncellendi)
- Test dosyaları (13 adet): `test_regime_models.py`, `test_regime_features.py`, vb.

## Regime config kararları
- `rule_based` default metot olarak ayarlandı. Unsupervised modeller (GMM/HMM) opsiyonel kılındı.
- Order creation, live trade ve paper trade operasyonları kesinlikle engellendi. Lookahead leakage validation'ı zorunlu hale getirildi.

## Regime feature mimarisi
- Trend gücü (eğim), range skoru (BB Width, ADX), volatilite ve volume verileri forward-looking z-skoru kullanmaksızın strictly causal hesaplandı. Centered rolling işlemleri engellendi.

## Rule-based classifier kararları
- Volatilite öncelikli olmak üzere ADX ve slope metriklerine göre deterministic kurallar oluşturuldu. `trend_up`, `trend_down`, `volatile`, `range_bound`, `calm` kararları bu öncelik sınırlarına göre tayin edildi.

## Confidence hesaplama
- Confidence metrikleri threshold sınırlarına (ör: `trend_adx_min` ve `strong_trend_adx_min`) lineer mapping ile bağlanarak 0 ile 100 arasında scale edildi.

## Smoothing kararları
- Tek barlık flip'ler transition ve unknown sınıfına hapsedildi. Geçmiş-sınırlı majority vote `center=False` yapısıyla stabil hale getirildi.

## Transition detection
- Peşi sıra gelen rejim farklılıklarında `RegimeTransitionEvent` oluşturularak `family` içi veya çapraz geçiş metriği kaydedildi.

## Stability scoring
- Rejim sınıfının bir pencerede çoğunluğu elinde bulundurma oranıstability score olarak belirlendi ve config parametresine göre flip-penalty işleme kondu.

## Optional GMM/HMM adapter kararları
- Sınıflar izole Protocol sınıflarına entegre edildi, fit işlemleri için train data validation kısıtı leakage-guard içerisine zorunlu bağlandı. Kurulum olmaması gracefully catch edildi.

## Leakage guard kararları
- `target`, `label`, `future_return` vb. kolonların dataframe'de bulunması hard exception (`RegimeLeakageError`) üzerinden engellendi. Unclosed candle'larda kısıt kondu.

## Storage/cache entegrasyonu
- Dataset modeli olan `market_regimes` DataStore API schemas'ına eklendi. Execute field içermemesi import safhasında doğrulandı.

## CLI komutları
- `regime-config`, `regime-feature-build-fixture`, `regime-classify-fixture`, `regime-transitions-fixture`, `regime-health` komutları CLI listesine dahil edildi. `doctor` metoduna validasyon bağlandı.

## Test sonuçları
- 420+ testin tamamı ve CLI validation logic eksiksiz koşuldu ve hepsi başarıyla (100%) geçti.

## Bilinen sınırlamalar
- HMM ve GMM adapterları rule-based önceliğinden ötürü şimdilik iskelet formunda duruyor. Gerçek veri pipeline entegrasyonu (stream feed) Phase 16/17'ye bırakıldı.

## Phase 16’ya hazırlık
- Phase 16'da risk engine v1 kurulacak; scored signal ve regime context henüz emir üretmeden position sizing öncesi risk değerlendirme inputu olarak hazırlanacaktır.
