# Phase 6 Report

## Oluşturulan/güncellenen dosyalar
- `src/binance50/config/models.py` - Yeni konfigurasyon blockları (`NetworkConfig`, `BinanceTimingConfig`, `RateLimitConfig`, `WebSocketLimitsConfig`) ve bunların validasyon mantıkları eklendi. `AppConfig` objesine dâhil edildi.
- `src/binance50/rate_limit/models.py` - Oran limiti veri modelleri oluşturuldu (`RateLimitBudget`, `RateLimitDecision`, `RateLimitHeaderSnapshot` vb.).
- `src/binance50/rate_limit/parser.py` - Binance ağ yanıt başlıkları ("X-MBX-*", "Retry-After") çözümlendi ve snapshot objesine çevrildi.
- `src/binance50/rate_limit/tracker.py` - İn-memory oran limiti takip sınıfı. Thread-safe biçimde saniye ve dakika bazlı oran ağırlıkları güncellenip korunuyor.
- `src/binance50/rate_limit/limiter.py` - Limit aşımı öncesinde istekleri reddeden veya geciktiren karar motoru oluşturuldu. Conservative modu varsayılan olarak ayarlandı.
- `src/binance50/rate_limit/cooldown.py` - İstenmeyen durumlar için hard (örneğin 418) ve soft (örneğin 429) cooldowns yönetici sınıfı eklendi.
- `src/binance50/rate_limit/websocket_limits.py` - WebSocket üzerinden stream sınırları (Spot: 1024, USDM: 200) ve saniye bazlı mesaj limitleri (Spot: 5/s, USDM: 10/s) için kısıtlamalar eklendi.
- `src/binance50/network/backoff.py` - Gelişmiş Exponential Backoff (katlanarak artan süre) ve rastgele Jitter kullanımı oluşturuldu.
- `src/binance50/network/retry_policy.py` - `RetryController` yeniden deneme sayısını ve durumları filtreleyen sınıf tanımlandı.
- `src/binance50/network/timeout_policy.py` - Okuma, bağlanma ve istek süresi limitleri oluşturuldu.
- `src/binance50/network/recv_window.py` - İstek penceresi güvenlik doğrulama, offset aşımı kararları yazıldı. (varsayılan: 5000 ms, limit: 60000 ms)
- `src/binance50/network/clock.py` - `ClockSyncService` oluşturuldu. İleriki adımlarda server zamanını mocklamak veya kıyaslamak için yazıldı.
- `src/binance50/network/circuit_breaker.py` - Üst üste atılan hataları sayıp half_open ve open konumlarına geçen sistem yazıldı.
- `src/binance50/network/request_budget.py` - İstek ağırlığı kontrolü yapılarak kritik limitlerin proaktif şekilde engellenmesi sağlandı.
- `src/binance50/safety/rate_limit_guard.py` - Limit aşımlarını engellemek, 429 hatalarının yanlış retry kararlarını kontrol etmek gibi konfigürasyon güvenlik kuralları eklendi.
- `src/binance50/safety/clock_guard.py` - `recv_window` sınırlarını ve imza üretimi öncesi güvenlik ofsetlerinin uyumlu olup olmadığını denetleyen kurallar yazıldı.
- `src/binance50/core/exceptions.py` - Ağ kurallarına, saat aşımlarına ve limit aşımlarına yönelik spesifik exception sınıfları eklendi.
- `src/binance50/core/error_codes.py` - Exception sınıfları için spesifik string error code tanımları yapıldı.
- `src/binance50/core/error_classifier.py` - Gelen 429, 418 veya 5XX sunucu hatalarının Binance modelleri kapsamında tanımlanması için güncellendi.
- `src/binance50/connectors/connection_policy.py` - Phase 6 için gerçek ağ çağrılarının engellendiği ve mock'landığı denetim mekanizması uygulandı.
- `src/binance50/connectors/rest_client.py` ve `websocket_client.py` - İskelet kodlara Limit, Network Policy, Circuit Breaker özellikleri birleştirildi. Request ve connect işlemleri hard-fail şeklinde ayarlandı.
- `src/binance50/cli.py` ve `scripts/check_project.py` - Oran limiti durumunu, `simulate` test komutlarını çalıştıran `typer` komutları güncellendi.
- `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/PHASE_PLAN.md`, `README.md` - Mimari karar kayıtları eklendi ve plan faz 7'ye ilerletildi.
- Testler: `test_rate_limit_parser.py`, `test_rate_limit_tracker.py`, `test_rate_limiter.py`, `test_websocket_limits.py`, `test_backoff_policy.py`, `test_timeout_policy.py`, `test_recv_window.py`, `test_clock_sync.py`, `test_circuit_breaker.py`, `test_rate_limit_guard.py`, `test_cli_rate_limit.py`.

## Rate limit mimarisi
Tamamen in-memory olarak çalışan; ağırlıkların, istek sayılarının hesaplandığı ve "ok, warning, critical, exceeded, cooldown, banned" şeklinde sınırlandırdığı proaktif bir güvenlik modeli hazırlandı. Thread safe olarak tasarlandı. `budget` mantığıyla endpoint çağrılmadan önce sınırların aşılıp aşılmayacağı değerlendirilir.

## Header parser kararları
Binance başlık yapısındaki `X-MBX-USED-WEIGHT-1M`, `X-MBX-ORDER-COUNT-10S` gibi anahtar kelimeleri okuyup standart Snapshot nesnesine dönüştüren basit bir dict-loop yapısı benimsendi. Hatalı olan numara dönüşümleri güvenli bir şekilde pass geçildi (warning). Raw headers alanlarındaki potansiyel secret'lar `REDACTED` değerleriyle dışa yansıtılmaktadır.

## Limiter/cooldown kararları
Limiter 418 kodu (IP ban) algıladığında `cooldown_manager`ı hard flagiyle başlatıp kalıcı stop verir. 429 limiti aşıldığında belirlenen süre (örneğin 60s) boyunca istekleri geciktirir/yasaklar. `mode=conservative` durumunda 80% güvenlik sınırında bile ekstra `.delay_seconds` uyarısıyla tavsiye üretmektedir.

## Retry/backoff kararları
Exponential backoff için rastgelelik barındıran jitter eklentisi zorunlu ve test edilebilir kılındı (kalkış ve max_delay korumasıyla). 418 hatasında retry asla gerçekleşmez, 429 özel durumlara havale edildiğinden default olarak false belirlendi (yalnızca soft cooldown ile dinlenmesi hedeflendi). 500 hataları ve Timeout'lar tekrar edebilmektedir.

## Timeout policy kararları
`read_timeout_seconds`, `connect_timeout_seconds` değerlerinin `request_timeout_seconds` parametresini ihlal edememesi üzerine temel doğrulama mantığı yazıldı.

## recvWindow/timestamp kararları
60000ms üzeri `recv_window` doğrudan `SafetyError` verir. Zaman damgasının (timestamp), server_time'ın 1000ms'ten daha fazla önüne gitmesi engellenir. Clock drift ve network gecikmesini baz alan `estimate_safe_recv_window` metodu oluşturuldu.

## Clock sync kararları
Sistem, gerçek `/api/v3/time` API çağrısını yapamıyor; bu fazda yalnızca "server zamanı tahmini", "ping gidiş-dönüş hesabı (RTT)" yapan simülasyon iskeleti kuruldu. Sync devre dışıyken veya bilinmiyorken (bilhassa signed istekler için) koruma sağlayan guard'lar kodlandı.

## Circuit breaker kararları
Art arda gerçekleşen başarısızlıklar sonrasında sistemin "open" state'e geçerek Binance'e giden potansiyel trafiği korumaya alması sağlandı. 418 IP banı "direkt circuit open" olarak sınıflandırıldı.

## WebSocket limit kararları
Spot tarafında saniye başına max 5 mesaj, max 1024 stream sınırı uygulanırken; USDM Futures tarafında saniye başına 10 mesaj ve max 200 stream sınırı `WebSocketLimitDecision` üzerinden denetlenir. Lifetime (24h) ile süre tamamlanmadan önce proaktif `reconnect_deadline_utc` koruması oluşturuldu.

## Connector entegrasyonu
Mevcut `rest_client` ve `websocket_client` modellerine Timeout policy, Circuit Breaker, Rate Limiter ve Retry Controller özellikleri eklendi. Gelen `health` bilgilerinin "real_network_enabled" durumuna göre bağlantıyı reddetmesi sağlandı.

## CLI komutları
- `python -m binance50.cli rate-limit-status` -> Geçerli durum.
- `python -m binance50.cli rate-limit-simulate --status-code [HTTP_CODE]` -> Oran simülasyonu çalıştırıp karar sunar.
- `python -m binance50.cli recv-window-check` -> Validasyon ve örnek param çıkartır.
- `python -m binance50.cli clock-sync-status` -> Zaman offset değerini denetler.
- `python -m binance50.cli websocket-limits-check ...` -> Websocket limit validasyonu sunar.
- `python -m binance50.cli network-safety-report` -> Bütün sistemin ağ güvenliğini doğrular.
Tüm komutlar terminale `json.dumps()` aracılığıyla yansıtıldı.

## Test sonuçları
- 108/108 tüm Pytest Unit testleri başarıyla tamamlandı.
- Mypy tiplendirme doğrulamasında 83 dosyada 0 hata alındı.
- Ruff Linter, Black Formatter kontrollerinden sorunsuz geçildi.
- `check_project.py` scriptindeki CLI "Doctor", "Dry Run Guard", "Live Unlock Guard", vb. testlerin tümü `passed` ibaresi ile doğrulandı.

## Bilinen sınırlamalar
Şu an için dış networke çıkış kapalıdır (Phase 6 kısıtlaması nedeniyle). Saat senkronizasyonu gerçek anlamda internet üzerinden zaman verisini almaz, yalnızca localdeki simülasyon fonksiyonları kullanılır. Request budget kısmı için kullanılan Endpoint ağırlıkları (1, 20 vb.) tamamen placeholder konumundadır, ileriki aşamalarda weight registry ile gerçek API yapılarına evrilecektir.

## Phase 7’ye hazırlık
Phase 7 dahilinde market evreni oluşturulacak; hacim, spread, likidite filtreleri entegre edilerek Binance sembol filtresinin veri yönetimi ve offline modellemeleri gerçekleştirilecektir. Ağa bağlanabilme ihtimali yavaş yavaş değerlendirilecektir.
