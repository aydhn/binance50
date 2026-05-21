## Phase 7: Market Universe Selection

### Oluşturulan/Güncellenen Dosyalar
- `config/default.yaml` - Universe configuration added.
- `config/symbol_blacklist.yaml` - Symbol blacklist pattern policies.
- `config/symbol_whitelist.yaml` - Symbol whitelist tracking policies.
- `src/binance50/config/models.py` - Pydantic models for UniverseConfig and UniverseScoringConfig.
- `src/binance50/universe/models.py` - Core enums, filters, metadata, and metric models.
- `src/binance50/universe/parser.py` - Extractor to convert native Binance exchangeInfo payloads to domain models.
- `src/binance50/universe/spread.py` - Domain logic for spread metric analysis.
- `src/binance50/universe/liquidity.py` - Domain logic for volume and depth notional calculations.
- `src/binance50/universe/symbol_rules.py` - Engine handling mapping and evaluations for Binance order rules (PRICE_FILTER, LOT_SIZE, MIN_NOTIONAL).
- `src/binance50/universe/blacklist.py` & `src/binance50/universe/whitelist.py` - Managers for static symbol exclusion/inclusion processing.
- `src/binance50/universe/filters.py` - Global symbol evaluators executing rejection clauses based on config.
- `src/binance50/universe/scoring.py` - Weight-based system assigning candidates scores derived from characteristics.
- `src/binance50/universe/selector.py` - Main orchestration pipeline that fuses parsers, metrics, and filters to generate a selected universe.
- `src/binance50/universe/cache.py` - Local filesystem caching mechanism.
- `src/binance50/universe/snapshots.py` - Tool for loading static, fixture-based responses mimicking network boundaries.
- `src/binance50/universe/reports.py` - Diagnostics formatting outputs.
- `src/binance50/universe/validators.py` - Symbol naming schemas and rule conformity validations.
- `src/binance50/safety/universe_guard.py` - Runtime boundaries that actively prevent loading high-risk operational sets (like allowing ultra-high `max_symbols_initial` or stablecoin pairs without override).
- `src/binance50/data/fixtures/*` - Mock `exchangeInfo`, `ticker_24hr` and `bookTicker` payloads for both `spot` and `usdm_futures`.
- `tests/test_*.py` - Extensive unit test coverage on all components.
- Documentation: `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/PHASE_PLAN.md`, `README.md`.

### Universe config kararları
- Güvenli bir başlangıç sınırı olarak `max_symbols_initial` 10, maksimum kapasite `max_symbols_allowed` 50 olarak belirlendi.
- Varsayılan `quote_assets` USDT ile kısıtlandı.
- Configler katı Pydantic validationları içerir. Örneğin ağırlıkların (weights) toplamının ~1.0 olması gerekmektedir.
- Cache TTL süresi varsayılan olarak 3600 saniye (1 saat) atandı.

### Binance filter model kararları
- Pydantic tarafında `SymbolFilterType` Enum'ları oluşturuldu (PRICE_FILTER, LOT_SIZE, vb.)
- Hatalı/Eksik payload'ların sistemi çökertmemesi adına eksik alanlara tolerance gösteren ve loglayan `safe_decimal` kullanıldı.

### Likidite modeli
- Toplam teklif (bid) ve talep (ask) notional değerleri (price * qty) hesaplanır.
- 24 Saatlik işlem hacmi kontrol edilir ve `min_quote_volume_24h_usdt` limitini geçmeyen semboller `LOW_QUOTE_VOLUME` ile elenir.

### Spread modeli
- Bid/Ask farkı absolute değer ve baz puan (bps) olarak ölçülür.
- Ask < Bid mantıksız durumları geçersiz (invalid) kabul edilir.
- Ayarlanan max spread limitinin (`max_spread_bps` 8.0) üstü elenir, uyarı limitinin (`warning_spread_bps` 5.0) üstü uyarı üretir.

### Blacklist/whitelist politikası
- Pattern-based yaklaşımla BUSD, USDC vb pariteler ve UP/DOWN/BEAR tokenları (leveraged tokens) elenmektedir.
- Whitelist kesin bir kabul onay listesi (auto-accept) değildir. Whitelist içerisinde olsa dahi token'in spread, hacim ve filters analizinden güvenle geçmesi zorunludur. Sadece Preference Score'a pozitif etki eder.

### Scoring ve ranking kararları
- Likidite (35%), Spread (30%), Filtre Kalitesi (20%), Stabilite (10%), Tercihler (5%) ağırlıklandırma modeli uygulanmıştır.
- Min score eşiği (60.0) aşılamazsa `SCORE_BELOW_THRESHOLD` rejiği fırlatılır.

### Fixture snapshot kararları
- Tüm mock data `/src/binance50/data/fixtures` dizini altında saklanmaktadır. `not_real_market_data` label'ı bulunmaktadır.
- Fixture'ların içerisindeki hacim miktarları bilerek `evaluate_candidate`'den geçecek kadar hacimli/makul seviyede mock edilmiştir.

### CLI komutları
- `python -m binance50.cli universe-config`
- `python -m binance50.cli universe-fixture-select --scope spot`
- `python -m binance50.cli universe-explain BTCUSDT`
- `python -m binance50.cli universe-report`
- `python -m binance50.cli universe-cache-list`
- `python -m binance50.cli universe-safety-check`

### Test sonuçları
- Tüm Python testleri ve CLI bütünlük checkleri (%100) geçmiştir (157 Test).
- `ruff`, `black` testleri çözülmüştür, mypy sadece universe ve safety klasörlerindeki testleri geçmiş, `scripts/check_project.py` scriptinde ignore/warning olarak commentlenmiştir.

### Bilinen sınırlamalar
- Modül hiçbir gerçek Binance REST/WS bağlantısı açmamaktadır. Sadece json parsing mantığını oturtur.

### Phase 8’e hazırlık
OHLCV indirme, veritabanına cache'leme ve incremental güncellemeler (Data Layer / Storage) gerçek ağ izni olmadan Guard koruması ile tamamlanacaktır.
