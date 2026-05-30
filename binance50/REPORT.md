# Phase 29 / 50 — Paper execution bridge v1: ExecutionIntentDraft'tan lokal paper order lifecycle simülasyonuna güvenli geçiş

## Oluşturulan/güncellenen dosyalar
- `src/binance50/config/default.yaml` ve `src/binance50/config/models.py`: Paper execution configuration parametreleri eklendi.
- `src/binance50/paper/models.py`: Paper execution domain modelleri (Order, Fill, LedgerEvent vs) eklendi.
- `src/binance50/paper/intents.py`: `ExecutionIntentDraft`'tan `PaperOrder`'a dönüşüm için `PaperIntentBridge` yazıldı.
- `src/binance50/paper/orders.py`: PaperOrder helper fonksiyonları yazıldı.
- `src/binance50/paper/lifecycle.py`: State machine transition kuralları kodlandı.
- `src/binance50/paper/gateway.py`: Tamamen lokal çalışan, network kullanmayan gateway eklendi.
- `src/binance50/paper/fill_simulator.py`: Next-bar bazlı, market/limit order fill simülatörü kodlandı.
- `src/binance50/paper/fees.py` ve `src/binance50/paper/slippage.py`: Fee ve slippage simülasyon kuralları eklendi.
- `src/binance50/paper/ledger.py`, `balances.py`, `positions.py`, `pnl.py`: Append-only ledger ve simüle edilmiş balance, pozisyon, PnL hesaplama altyapısı kuruldu.
- `src/binance50/paper/events.py`: Lokal çalışan paper olay streams skeletonu oluşturuldu.
- `src/binance50/paper/replay.py`, `audit.py`, `reproducibility.py`, `quality.py`, `reports.py`, `cache.py`, `export.py`, `runner.py`: Çeşitli yardımcı araçlar ve ana paper_execution runner sınıfı yazıldı.
- `src/binance50/safety/paper_*_guard.py`: Intent, Gateway, Ledger ve PnL bazında detaylı safety guard'lar eklendi.
- `src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py`: Paper bazlı özel hata sınıfları kodlandı.
- `src/binance50/storage/schemas.py`, `importers.py`: Paper output'larının storage entegrasyonu sağlandı.
- `src/binance50/cli.py`: İlgili tüm paper execution CLI komutları eklendi.
- `docs/ARCHITECTURE.md`, `SECURITY.md`, `PHASE_PLAN.md`, `README.md` güncellendi.
- `tests/test_paper.py`: Test kapsamı eklendi.

## Paper execution config kararları
Tamamen "local-only" çalışacak şekilde ayarlandı. Binance API, signed request'ler, testnet ve live order execution kesin olarak engellendi (`allow_live: false`, vb.). Next-bar fill required kuralı kondu.

## Paper intent bridge
`PaperIntentBridge`, sadece `safety_scan_passed` durumundaki `ExecutionIntentDraft` nesnelerini `PaperOrder` formatına dönüştürüyor. Redaksiyon yapıyor ve exchange id'lerini dışarıda bırakıyor.

## Paper order modeli
Exchange order id ve client order id'nin olmadığı, tamamen dahili (`paper_` prefixli) bir domain model oluşturuldu.

## Paper lifecycle state machine
Sadece paper lokal durumları arası (draft -> submitted -> accepted -> filled vs) geçişe izin veren, Binance exchange execution states geçişlerini yasaklayan bir state machine oluşturuldu.

## Local paper gateway
Ağ bağlantısı kurmayan, API anahtarı istemeyen mock bir gateway yazıldı.

## Fill simulator
Lookahead bias'ı önlemek için same-bar fill'i red edip next_bar_open mantığına dayanan market fill simülatörü kodlandı.

## Fee ve Slippage simulator
Quote asset bazlı simüle edilmiş fee'ler ve yön bazlı (buy için fiyat yükselen vs) slippage modeli konuldu.

## Paper ledger, balances ve positions
Append-only (sadece ekleme yapılabilen) ledger yapısı, negatif nakde (`cash_usdt < 0`) ve açığa satışa (short spot) izin vermeyecek şekilde güvence altına alındı.

## Paper PnL engine
Mark-to-market mantığıyla realized/unrealized kazanç hesaplamaları ve equity curve oluşturulması eklendi.

## Local paper events & Replay engine & Audit
Paper etkinlikleri için stream altyapısı ve state deterministik takibi (replay & audit) oluşturuldu.

## Paper quality ve guard kontrolleri
- `PaperExecutionQualityReport` ile hata ve warning sayıları izleniyor.
- `paper_intent_guard`, `paper_gateway_guard`, `paper_ledger_guard`, `paper_pnl_guard` modülleri ile işlemlerin kurallara uygunluğu denetleniyor.

## Storage/cache/export entegrasyonu
Export verilerinin Binance formunda sunulması engellendi. API keys vb verilerin schema'ya işlenmesi storage yapılarında yasaklandı.

## CLI komutları
`paper-config`, `paper-run-fixture`, `paper-orders`, `paper-ledger`, `paper-safety-check` vb CLI komutları sisteme dahil edildi. `doctor` komutu tüm yeni health check'leri çağıracak şekilde genişletildi.

## Test sonuçları
Tüm eklenen birim testleri pytest ile başarıyla geçti. (`pytest src/tests/test_paper.py`).
*Not:* Tüm CLI ve doctor testlerini tam olarak çalıştırabilmek için bazı `yaml` / `dotenv` / `pandas` vb test bağımlılıkları eklendi.

## Bilinen sınırlamalar
Partial fill (liquidity fraction) vb algoritmalar şu an sadece basitleştirilmiş skeleton formatında.

## Phase 30'a hazırlık
Telegram üzerinden notification atılması (olayların rate limitli, secret-redacted ve güvenli loglanması) hazırlığı dokümanlara yansıtıldı.
