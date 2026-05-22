## Indicator Engine Phase 11 Report

### Oluşturulan/Güncellenen Dosyalar
**Modeller ve Config**:
- `src/binance50/config/models.py` (Yeni domain objeleri `IndicatorsConfig` vb.)
- `config/default.yaml` (Yüzlerce satırlık yeni trend, momentum, volatility ve indicator configi)
- `src/binance50/core/exceptions.py`, `src/binance50/core/error_codes.py`, `src/binance50/core/error_classifier.py`

**Indicators Engine Mimarisi (yeni)**:
- `src/binance50/indicators/models.py`: Domain modelleri (`IndicatorSpec`, `IndicatorRunRequest`, `IndicatorRunResult`)
- `src/binance50/indicators/context.py`: Engine scope context
- `src/binance50/indicators/validators.py`: Future column (label) detect eden ve Lookahead-bias koruması yapan input validatorleri
- `src/binance50/indicators/warmup.py`: Lookup window ve min require row analiz modülü
- `src/binance50/indicators/transforms.py`: Ortak transformlar (log return vb.)
- `src/binance50/indicators/trend.py`, `momentum.py`, `volatility.py`, `volume.py`: Native numpy/pandas algoritmaları
- `src/binance50/indicators/registry.py`: Dinamik register yapısı
- `src/binance50/indicators/adapters/`: `native.py`, `pandas_ta_adapter.py`, `talib_adapter.py`
- `src/binance50/indicators/quality.py`, `cache.py`, `engine.py`, `reports.py`

**Guard, Storage ve Features**:
- `src/binance50/safety/indicator_guard.py`
- `src/binance50/features/basic_returns.py`
- `src/binance50/storage/schemas.py`, `importers.py`
- `src/binance50/cli.py` komutları (örn: `indicator-compute-fixture`)

### Indicator Config Kararları
`default.yaml` içerisine `enabled`, `prevent_lookahead_bias`, `reject_duplicate_open_time` gibi anahtarlar girilmiştir. Tüm indikatör sınıfları (Trend, Volatility vs.) ayrı konfigürasyonlara bölünmüştür (örneğin SMA, EMA, MACD, RSI period yapılandırmaları). Default olarak strict kurallar ile çalışır.

### Native Backend Mimarisi
Native backend `pandas` ve `numpy` tabanlı tamamen deterministik metodlarla yazılmıştır. Her bir indikatör ayrı bir fonksiyondur ve native adaptörü vasıtasıyla dinamik bir listeye bağlı olarak çağrılır. Testlerin çoğu bu backend'in gücünü ispatlar.

### Optional Backend Adapter Kararları
`TA-Lib` ve `pandas-ta` bağımlılıkları kasıtlı olarak "zorunlu" tutulmamış (`try-except ImportError`), ve bir adaptör deseniyle sarılarak "Eğer mevcutsa availability report ile belirtilir, değilse fallback sağlanır" olarak yapılmıştır. Böylelikle CI veya lokal ortamda C kütüphanesi olmadan sorunsuz test yapılabilmektedir.

### Trend Indikatörleri
`sma`, `ema`, `wma`, `dema`, `tema`, `macd`, `adx`, `aroon` yazılmış ve test edilmiştir. EMA Wilders formülünde stabil hale getirilmiştir.

### Momentum Indikatörleri
`rsi`, `stochastic`, `stoch_rsi`, `roc`, `momentum`, `cci`, `williams_r` yazılmıştır. RSI için internal simple moving average bazlı bir formül kullanılmıştır.

### Volatilite Indikatörleri
`atr`, `natr`, `bollinger_bands`, `bollinger_bandwidth`, `keltner_channels`, `donchian_channels`, `rolling_std`, `realized_volatility` tamamen uygulanmıştır.

### Hacim Indikatörleri
`obv`, `volume_sma`, `volume_ema`, `vwap`, `mfi`, `cmf`, `accumulation_distribution_line` oluşturulmuştur.

### Transform / Helper Özellikleri
`typical_price`, `median_price`, `weighted_close`, `returns`, `log_returns`, `rolling_zscore`, `safe_divide` gibi işlemler oluşturulmuştur. Future leakage önlemek adına future parametreli (shift(-1)) gibi kullanımlar katı şekilde reddedilmektedir.

### Warmup/Lookback Kararları
`estimate_max_lookback` ile en yüksek history checki bulunarak, dataframe içerisinde bir `is_warmup` flag maskesi oluşturulur. İstenen default config limitine uyulmazsa `InsufficientHistoryError` fırlatılır.

### Lookahead-Bias Koruması
Input ve Output validate ederken `FORBIDDEN_COLUMNS = ["future_return", "target", "label", "next_close", "forward"]` gibi stringlere sahip olan özellikler reddedilir. Ayrıca `fill_policy: "bfill"` (backfill) güvenlik testlerinde exception fırlatır.

### Indicator Quality Kontrolleri
Veriler işlendikten sonra `quality.py` ile NaN (eksik veri oranı), Infinity, Exteme/Z-Score ve tümüyle NaN/Sabit değerlerden oluşan çıktı kolonları kalite skoru denetiminden geçer.

### Cache/Warehouse Entegrasyonu
Çıktı sonuçları JSON metadata ve parquet olarak saklanmakta. `importers.py` üzerinden `dynamic_schema` mantığı geliştirilerek, base statik columnların haricindeki hesaplanan dynamic feature kolonları otomatik olarak Storage Schema yapısına dönüştürülür.

### CLI Komutları
- `indicator-config`, `indicator-backends`, `indicator-list`
- `indicator-compute-fixture` (Offline test aracı), `indicator-quality-check`
- `indicator-safety-check`, `indicator-health`, `indicator-cache-list`
komutları `cli.py` dosyasına entegre edilmiştir.

### Test Sonuçları
Tüm Trend, Momentum, Volatilite, Hacim, Transform testleri, Model testleri, Engine ve Adaptör testleri, Kalite kontrol testleri tamamlanmış olup `pytest tests/` 284 PASS sonuçla dönmüştür. Pre-commit testlerinde `mypy`, `ruff`, ve `black` fixleri geçilmiştir.

### Bilinen Sınırlamalar
TA-lib/pandas-ta implementationları skeleton durumundadır. Engine native formülleri default kullanır. Optimizasyonlar büyük verisetlerinde multi-processing ihtiyacı duyabilir (ileriki memory limit sorunları olabilir).

### Phase 12'ye Hazırlık
İndikatör engine katmanı deterministik olarak feature üretimini halletmiş durumdadır. Bir sonraki fazda Divergence algılayıcılar, çoklu timeframe (MTF) mappingler ve candlestick patternleri için bu engine temel model olarak kullanılacaktır.
