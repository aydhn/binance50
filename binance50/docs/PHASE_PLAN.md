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
