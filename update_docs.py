import re

with open("binance50/docs/ARCHITECTURE.md", "a") as f:
    f.write("\n## Rate limit and Network architecture (Phase 6)\n")
    f.write("- **Header parser:** Parses X-MBX-* and Retry-After headers.\n")
    f.write("- **In-memory tracker:** Tracks 1m weights and order counts safely in memory.\n")
    f.write("- **Limiter decision engine:** Uses conservative thresholds to predict and prevent limits.\n")
    f.write("- **Cooldown manager:** Manages soft 429 delays and hard 418 bans.\n")
    f.write("- **Retry/backoff controller:** Computes exponential backoff with jitter and respects max attempts.\n")
    f.write("- **Timeout policy:** Validates granular httpx-compatible timeouts.\n")
    f.write("- **Circuit breaker:** Detects generic network failures and allows cool-off.\n")
    f.write("- **Clock sync design:** Uses mock implementations for safe server-local offset checks.\n")
    f.write("- **recvWindow timing security:** Evaluates if drift is safe for a signed request.\n")
    f.write("- **WebSocket limit model:** Applies 1024/200 stream and msg/s limit rules per domain.\n")
    f.write("- **Neden Phase 6’da gerçek network yok?:** We are building a deterministic mock layer before allowing real external egress to ensure total local safety.\n")


with open("binance50/docs/SECURITY.md", "a") as f:
    f.write("\n## Network Safety (Phase 6)\n")
    f.write("- **429 handling policy:** Explicit soft cooldown to avoid automated repeat bans.\n")
    f.write("- **418 IP ban hard stop policy:** Direct halt if encountered, requires manual clear.\n")
    f.write("- **Retry-After policy:** Strictly respected if provided.\n")
    f.write("- **5XX unknown execution status policy:** They are caught as retryable in general, but order submission states are carefully flagged.\n")
    f.write("- **recvWindow ve timestamp güvenliği:** Checked locally before generating a request payload.\n")
    f.write("- **Clock drift guard:** High clock drift will reject signed order paths.\n")
    f.write("- **WebSocket incoming message limit güvenliği:** Connections rejecting streams exceeding docs max (e.g. 1024 or 200).\n")
    f.write("- **Request budget ve aggressive polling yasağı:** Budget usage is projected to block early before real 429.\n")
    f.write("- **Rate limit aşımında botun nasıl sakinleşeceği:** Uses the local CooldownManager and Circuit Breaker.\n")


with open("binance50/docs/PHASE_PLAN.md", "r") as f:
    plan = f.read()
plan = re.sub(r'Phase 6:.*', 'Phase 6: Rate limit, retry, backoff, timeout, recvWindow, clock-sync, circuit breaker ve WebSocket limit altyapısı kurulur.', plan)
plan = re.sub(r'Phase 7:.*', 'Phase 7: Market universe seçimi: sembol filtreleri, likidite, spread ve hacim ön-eleme modeli kurulacak.', plan)
with open("binance50/docs/PHASE_PLAN.md", "w") as f:
    f.write(plan)


with open("binance50/README.md", "a") as f:
    f.write("\n## Network Safety\n")
    f.write("Gerçek network hâlâ kapalı. 429 ve 418 IP ban simülasyonları destekleniyor.\n")
    f.write("Aşağıdaki komutlarla rate limit ve clock drift test edilebilir:\n")
    f.write("```\n")
    f.write("python -m binance50.cli rate-limit-status\n")
    f.write("python -m binance50.cli rate-limit-simulate --status-code 429\n")
    f.write("python -m binance50.cli rate-limit-simulate --status-code 418\n")
    f.write("python -m binance50.cli recv-window-check\n")
    f.write("python -m binance50.cli clock-sync-status\n")
    f.write("python -m binance50.cli websocket-limits-check --scope spot --stream-count 10 --messages-per-second 1\n")
    f.write("python -m binance50.cli network-safety-report\n")
    f.write("```\n")

print("Docs updated")
