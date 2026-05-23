
# Phase 13 Report: Strategy Engine Implementation

## Oluşturulan/güncellenen dosyalar
- **Config & Core:** `config/default.yaml`, `src/binance50/config/models.py`, `src/binance50/core/exceptions.py`, `src/binance50/core/error_codes.py`, `src/binance50/core/error_classifier.py`
- **Domain & Engine:** `src/binance50/strategies/models.py`, `src/binance50/strategies/base.py`, `src/binance50/strategies/context.py`, `src/binance50/strategies/engine.py`, `src/binance50/strategies/registry.py`, `src/binance50/strategies/plugin_loader.py`
- **Rules & Validation:** `src/binance50/strategies/conditions.py`, `src/binance50/strategies/rule_dsl.py`, `src/binance50/strategies/validators.py`, `src/binance50/strategies/quality.py`
- **Output & Safety:** `src/binance50/strategies/candidates.py`, `src/binance50/strategies/explanations.py`, `src/binance50/strategies/reports.py`, `src/binance50/strategies/cache.py`, `src/binance50/strategies/export.py`, `src/binance50/safety/strategy_guard.py`, `src/binance50/safety/signal_candidate_guard.py`
- **Plugins:** 9 built-in plugin files implemented.
- **Testing & Tooling:** 11 core strategy test files, 7 plugin test files, updated CLI tooling, and complete `scripts/check_project.py` integration.
- **Storage:** Updated schemas and importers for `strategy_candidates`.
- **Docs:** Updated `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, and `PHASE_PLAN.md`.

## Strategy config kararları
Strategy konfigurasyonu katı execution engellerine default olarak (`execution_forbidden: True`, vb.) sahiptir. Minimum and maximum expiry constraints, required rule confidence ranges, and isolated plugin limitations are defined using explicit Pydantic models.

## Strategy plugin mimarisi
Architecture encapsulates a generic protocol interface (`StrategyPluginProtocol`) ensuring individual plugin evaluation executes safely via `StrategyEngine` which catches any component failure, preventing full pipeline crashes.

## Strategy registry
A localized stateful mapping ensuring unique naming and dynamic toggling capabilities. Unhealthy plugins are logged but ignored rather than halting processes.

## Rule DSL ve condition sistemi
The `RuleBlock` logic arrays decouple mathematical boolean evaluation (`gt`, `lt`, `crosses_above`) out from raw Python allowing declarative criteria definition over DataFrames.

## Built-in pluginler
9 isolated logic implementations ranging from Trend Following (EMAs/ADX), Mean Reversion (Bollinger/RSI), to basic Composite tracking were integrated.

## SignalCandidate modeli
Immutable execution-absent domain object. Explicitly rejects tracking actionable trade attributes (`order_id`, `quantity`). Uses explicit enums for direction (`bullish`, `bearish`) and intent.

## Explanation modeli
Deterministic evidence tracker. Generates both string summaries completely free from imperative action verbs (like "buy now") and mapped dictionary details enumerating passed/failed conditions.

## Composite skeleton
Implemented as a deferral candidate structure that checks multiple plugins for directional agreement but explicitly restricts generating unified final signals (`final_signal_scoring_deferred: True`).

## Strategy quality kontrolleri
The engine implements rigorous scans to catch missing explanations, out-of-range confidence thresholds, duplicate generation identifiers, and intra-bar candidate conflicts (e.g. bullish and bearish signals output on the same timestamp).

## Strategy safety guard
Multi-layer protection. `strategy_guard.py` acts against configuration overrides disabling default constraints. `signal_candidate_guard.py` rejects actionable output phrases ("buy now", "execute"). The output payload is scanned against reserved execution keywords (`entry_price`, `quantity`).

## CLI komutları
Integration added for `strategy-config`, `strategy-list`, `strategy-plugin-health`, `strategy-run-fixture`, `strategy-candidates-preview`, `strategy-quality-check`, `strategy-cache-list`, `strategy-safety-check`, and `strategy-health`.

## Test sonuçları
The full `pytest` suite reports 331 passing tests successfully traversing boundary constraints, syntactic configurations, missing fixture mocks, logic rules, and engine isolation checks safely.

## Bilinen sınırlamalar
- Dynamic loading of non-builtin external plugins remains blocked by default.
- Phase 13 lacks full data warehousing traversal since testing logic was bound strictly via simulated mock data sets and offline DataFrame operations.

## Phase 14’e hazırlık
Input parameters strictly structured safely. Candidates ready to be passed into a future signal scoring and confluence engine without causing false execution triggering since the intent boundary remains cleanly sealed.
