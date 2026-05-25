# Phase Plan

- Phase 1: Project Skeleton & Foundation (Completed)
- Phase 2: Binance Environment Matrix (Completed)
- Phase 3: Logging, audit trail, hata sınıfları ve güvenli exception mimarisi kurulur. (Completed)
- Phase 4: .env, secrets, API key guard, dry-run/live kilitleri ve güvenli çalışma modu sertleştirilir. (Completed)
- Phase 5: Binance connector katmanı REST/WebSocket soyutlama, güvenli client factory, disabled/mock client ve endpoint resolver olarak kurulur. (Completed)
- Phase 6: Rate limit, retry, backoff, timeout, recvWindow, clock-sync, circuit breaker ve WebSocket limit altyapısı kurulur. (Completed)
- Phase 7: Market universe seçimi: sembol filtreleri, likidite, spread ve hacim ön-eleme modeli kurulacak.
- Phase 7-50: To be detailed...

### Phase 8
- OHLCV/kline veri indirme altyapısı, cache, incremental update, parquet store, veri kalite kontrol ve fixture testleri kurulur.

### Phase 9 Hazırlığı
- Phase 9'da WebSocket market stream hattı, kline/ticker/orderbook stream modelleri ve stream buffer mimarisi kurulacak; gerçek bağlantı yine guard kontrollü ilerleyecek.

- Phase 10: [Pending] Lokal veri ambarı, parquet/sqlite partition yönetimi, veri katalogu ve veri kalite indeksleri kurulacak.

- Phase 11: Indicator engine v1; trend, momentum, volatilite, hacim ve temel transform indikatörleri native pandas/numpy backend ile kurulur.
- Phase 12: Indicator engine v2 genişletilecek: divergence, multi-timeframe alignment, pattern/candlestick hazırlıkları ve feature grouping modeli kurulacak.

### Phase 14 hazırlığı:
Phase 14: Signal scoring ve confluence engine; strategy candidate'ları ağırlıklı, açıklanabilir, conflict-aware ve execution'dan ayrılmış skorlu sinyal taslaklarına dönüştürür. (Completed)
### Phase 15 hazırlığı:
Phase 15'te rejim sınıflandırma v1 kurulacak; trend/range/volatile/calm piyasa rejimleri sinyal skorlarının bağlamsal filtresi olarak hazırlanacak.

- Phase 21: Walk-forward validation v1; rolling/expanding/anchored windows, optimizer bridge, OOS evaluation, OOS equity stitching, degradation/drift/stability/robustness/regime analysis ve leakage/safety guard altyapısını kurar.
- Phase 22: Phase 22'de ML dataset builder v1 kurulacak; indicator/signal/regime/risk/backtest çıktıları leakage-safe feature-label dataset hazırlığına bağlanacak, fakat ML training henüz kontrollü/skeleton kalacak.
