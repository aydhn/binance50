
### Phase 17: Paper Trading Engine v1

**1. Oluşturulan/güncellenen dosyalar:**
- `src/binance50/config/models.py` (Paper Config Models added)
- `src/binance50/paper/models.py` (Paper Domain Models: PaperPosition, PaperFill, PaperSimulationEvent)
- `src/binance50/paper/account.py` (Paper Account state handling)
- `src/binance50/paper/ledger.py` (Event, Fill and Position tracking ledger)
- `src/binance50/paper/positions.py` (Paper position manager)
- `src/binance50/paper/fills.py` (Next-bar open fill simulation)
- `src/binance50/paper/fees.py` (Estimated maker/taker fee handling)
- `src/binance50/paper/slippage.py` (BPS-based slippage model)
- `src/binance50/paper/portfolio.py` (Snapshots & mark-to-market functions)
- `src/binance50/paper/pnl.py` (Unrealized and Realized simulation-only PnL logic)
- `src/binance50/paper/journal.py` (Logging closed simulated positions natively)
- `src/binance50/paper/simulator.py` (The overarching Sequential Bar-by-Bar simulator)
- `src/binance50/paper/quality.py` (Validation for quality issues such as negative cash or missed fills)
- `src/binance50/paper/reports.py` (Summarization of run outputs)
- `src/binance50/paper/cache.py`, `src/binance50/paper/export.py`, `src/binance50/paper/datasets.py`, `src/binance50/paper/replay.py` (Storage utilities)
- `src/binance50/paper/validators.py` (Strict safety rules blocking API keys, order_ids and live executions)
- `src/binance50/safety/paper_guard.py` & `src/binance50/safety/paper_execution_guard.py` (Safety wrappers)
- `src/binance50/cli.py` (New CLI commands for interacting with Paper engine)
- Updated `src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py` and `src/binance50/storage/schemas.py`.

**2. Paper config kararları:**
- The engine operates purely via a local configuration structure under the `paper` key.
- By default `allow_negative_cash`, `allow_margin`, `allow_short_spot` and `produce_real_order_quantity` are entirely `False`.
- Interactions with real networking components (`real_exchange`, `binance_client`, `order_gateway`, `api_key`) are strictly forbidden (`True`).

**3. Paper account modeli:**
- Simulates cash holding and records used notional reserves. Provides helper methods indicating if reserves are viable.
- Generates snapshot events detailing equity, unrealized PnL, cash reserves, and active position counts.

**4. Paper ledger mimarisi:**
- A pure, append-only local collection of events representing the timeline of execution.
- Emits entries mapping to actions like: `run_started`, `candidate_received`, `position_opened`, `fill_simulated`, `mark_to_market`.

**5. Fill simulation kararları:**
- By default employs `next_bar_open`, prohibiting same-bar fills to guarantee lookahead-bias safety.
- Handles partial checks locally via `require_next_candle`. If there isn't a viable bar subsequently, it will optionally skip or trigger warnings.

**6. Fee/slippage modeli:**
- Implemented as customizable BPS models via configuration. Supports volatile regimes adding slippage multipliers.
- Computed inherently and directly modifying simulated price / tracking fees within position metadata instead of generating standalone real "fee transfers".

**7. Position ve portfolio yönetimi:**
- Uses the simulated fill to spawn `PaperPositionStatus.open` entries. Opposite directions force closures safely.
- Marks positions to market based strictly off historical close inputs via the snapshot builder locally.

**8. Paper PnL v1:**
- Purely simulated differences computed using quantity * price deltas + fee subtraction.
- Retains separation between unrealized tracking for active equity metrics and realized for final journaling.

**9. Paper journal:**
- Maintains descriptive ledger snapshots containing the full lifecycle of a trade upon close. Enforces requirement of explanation and explicit intent context.

**10. Risk assessment entegrasyonu:**
- Evaluates directly on `status`. Requires targets to hold `approved_for_paper_review` or equivalent, otherwise it instantly emits `candidate_rejected` events into the ledger.

**11. Paper quality kontrolleri:**
- Evaluates post-simulation for inconsistencies. Triggers critical failures on missing fill prices, invalid cash usage (e.g. going negative), or leaking execution-based attributes.

**12. Paper safety guard:**
- Evaluates runtime capabilities beforehand and after the process. Completely aborts and generates a `PaperExchangeDependencyError` or similar exception if network requests are discovered or configured to run.

**13. Paper execution guard:**
- Blocks explicitly any payload holding fields named `order_id`, `api_key`, `live_order`, `signature`. Validates entire payload objects recursively down into `metadata`.

**14. Storage/cache entegrasyonu:**
- Dataset schemas updated specifically to encompass simulation output arrays (`paper_fills`, `paper_journal`, etc). All exports seamlessly translate to Dataframes without issues.

**15. CLI komutları:**
- All endpoints fully wired into `binance50.cli`, providing tools for config checking (`paper-config`), initialisation (`paper-account-init`), simulations (`paper-run-fixture`), auditing (`paper-ledger-report`), and safety auditing (`paper-execution-guard-check`).

**16. Test sonuçları:**
- Created 14+ specific testing modules enforcing guards and lifecycle flows successfully.
- Pytest, Ruff and Mypy passed entirely.
- `scripts/check_project.py` confirms successful project health integrity alongside Phase 17 additions.

**17. Bilinen sınırlamalar:**
- Simplistic portfolio logic currently restricts complex multi-currency pairs accurately (defaults fully strictly tracking `USDT` baselines).
- Margin/Leverage models rely on dummy metadata markers temporarily while robust future implementations follow.

**18. Phase 18'e hazırlık:**
- Successfully prepared the backbone for deterministic, historical bar-by-bar backtest executions routing directly through this established paper simulator.
