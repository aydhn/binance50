report = """
## Phase 26 Report

**Oluşturulan/güncellenen dosyalar:**
- `binance50/config/default.yaml` (Updated with `portfolio_sandbox` configuration)
- `binance50/src/binance50/config/models.py` (Added corresponding Pydantic models)
- `binance50/src/binance50/portfolio/sandbox/models.py` (Domain models, CandidateSourceType, etc.)
- `binance50/src/binance50/portfolio/sandbox/loaders.py` (Loaders for mock risk, signals, ML blend)
- `binance50/src/binance50/portfolio/sandbox/normalization.py` (Score clamping, scale standardization)
- `binance50/src/binance50/portfolio/sandbox/eligibility.py` (Stale detection, minimal score checks)
- `binance50/src/binance50/portfolio/sandbox/deduplication.py` (Duplicate resolution deterministic)
- `binance50/src/binance50/portfolio/sandbox/correlation.py` (Returns matrix, threshold check)
- `binance50/src/binance50/portfolio/sandbox/similarity.py` (Cosine similarity implementation)
- `binance50/src/binance50/portfolio/sandbox/exposure.py` (Hypothetical limits on symbols/directions)
- `binance50/src/binance50/portfolio/sandbox/concentration.py` (Top N ratios, penalizations)
- `binance50/src/binance50/portfolio/sandbox/diversification.py` (Scoring rules for source diversity)
- `binance50/src/binance50/portfolio/sandbox/risk_budget.py` (Placeholder logic)
- `binance50/src/binance50/portfolio/sandbox/constraints.py` (Hard blocks)
- `binance50/src/binance50/portfolio/sandbox/ranking.py` (Engine merging scores/penalties)
- `binance50/src/binance50/portfolio/sandbox/selection.py` (Top N extraction and validation)
- `binance50/src/binance50/portfolio/sandbox/explanations.py` (Textual breakdown generation)
- `binance50/src/binance50/portfolio/sandbox/optimizer_skeleton.py` (Optional SciPy optimization logic bounds)
- `binance50/src/binance50/portfolio/sandbox/reproducibility.py` (Hash checks on IO)
- `binance50/src/binance50/portfolio/sandbox/quality.py` (Data sanity assertions)
- `binance50/src/binance50/portfolio/sandbox/reports.py` (Dictionary formatters)
- `binance50/src/binance50/portfolio/sandbox/cache.py` (Disk read/write handlers)
- `binance50/src/binance50/portfolio/sandbox/export.py` (Parquet/JSON dumps)
- `binance50/src/binance50/portfolio/sandbox/runner.py` (Pipeline orchestrator)
- `binance50/src/binance50/safety/portfolio_sandbox_guard.py` (Config safety check)
- `binance50/src/binance50/safety/portfolio_correlation_guard.py` (Future data check)
- `binance50/src/binance50/safety/portfolio_integration_guard.py` (Prod write prevention check)
- `binance50/src/binance50/safety/portfolio_optimizer_guard.py` (Weight output limits)
- `binance50/src/binance50/core/exceptions.py`, `error_codes.py`, `error_classifier.py`
- `binance50/src/binance50/cli.py` (New CLI commands and doctor integration)
- `binance50/scripts/check_project.py` (Phase 26 commands validation loop)
- 16 new test files corresponding to modules.

**Portfolio sandbox config kararları:**
- Real exchange, live trade, and paper trade features are explicitly locked (forbidden = true).
- Signal auto-write, allocation production, and position sizing production are blocked.
- Uses Pearson correlation method as default.
- Strict limits: `max_total_hypothetical_exposure_pct: 30.0`
- Correlation and similarity trigger a warning/penalty if > 0.85, block if >= 0.95.

**Candidate input loader:**
Aggregates independent rule-based signals, risk context evaluations, regime data, and ML blended scores into a single structural input representation `PortfolioCandidateInput`.

**Candidate normalization:**
Clamps scores inside 0.0 - 100.0, handles ML probability shifts automatically if configured. Applies lowercase validation to the direction field.

**Eligibility ve deduplication:**
Discards entries based on user configurable variables (e.g. staleness exceeding age parameters, scores dropping beneath threshold limits). If duplicate source inputs match entirely, resolves deterministically prioritizing the highest combined score available.

**Correlation analysis:**
Generates a returns data frame checking for future leakage. Outputs `PortfolioCorrelationReport` maintaining pairs that violate specific defined thresholds.

**Similarity analysis:**
Builds numeric metric vectors across signal/risk/ml qualities per candidate and evaluates similarity using SciPy cosine bounds. If SciPy defaults to absolute metrics due to absence, operates a fallback.

**Hypothetical exposure:**
Tracks and computes directional constraints and max symbol weights mapped against an imaginary offline equity baseline (e.g. 1000 USDT). Blocks any real exchange balancing fetches.

**Concentration analysis:**
Penalizes identical structural layouts. Reports overbearing limits on regimes and trade direction overlaps to ranking engine.

**Diversification scoring:**
Calculates positive bonuses representing uniqueness across different model scopes. Modifies `diversification_score` bound by configuration maximums.

**Risk budget placeholder:**
Serves as an independent limit validation module against fixed values defining theoretical risk metrics.

**Constraint checks:**
Checks exposure, limit blocks, identical candidate overloads and formats violations as blocks or penalties for the Ranking engine.

**Ranking engine:**
Takes multi-sourced weighted combinations (signal + risk + ml_blend - dependencies). Outputs a final portfolio ranking value adhering bounds constraints.

**Selected sandbox candidates:**
Rejects irrelevant candidates, populates an array with validated, successfully vetted candidates marking each non-execution/sandbox-only. Generates explanatory reasoning for trace purposes without executing actionable intents.

**Optional optimizer skeleton:**
Implements SciPy verification checks demonstrating optimization intent under rigid boundaries (e.g., correlation max, limits) strictly outputting sandbox-restricted weight models.

**Reproducibility kararları:**
Hash checks run against dataset configuration, individual candidates, and resulting structures to prevent non-deterministic variations between selection executions.

**Quality kontrolleri:**
Generates warning or failing status models based on empty explanations, invalid scores out of operational bounds, or NaN/Inf metrics identified.

**Portfolio safety guard:**
Blocks the initialization loop fundamentally if `real_exchange_forbidden` or similarly crucial flags differ from "true".

**Correlation guard:**
Detects column structures commonly recognized as future data inside metadata structures. Validates symmetry and non-nan structures of generated frames.

**Integration guard:**
Strictly guarantees no outputs interact with live production execution endpoints and forces selection instances to inherently adopt non-executory `blocked_*` parameters as true.

**Optimizer guard:**
Ensures theoretical SciPy weight configurations aren't inherently configured as defaults for selection processes. Limits its domain to hypothesis visualization only.

**Storage/cache/export entegrasyonu:**
Extends `DatasetKind` enums allowing independent offline preservation of analytical outputs (e.g. reports, sandbox candidate dumps) inside non-intrusive Parquet or JSON records. Imports are completely fenced.

**CLI komutları:**
All pipeline features accessible independently via the console via `python -m binance50.cli portfolio-xyz` combinations. `doctor` handles the full sequence.

**Test sonuçları:**
24 comprehensive tests covering structural behavior, normalization mapping, similarity calculation fail-safes (scipy installed/missing), algorithm tie-breaking, limits validation, optimizer failure modes, and safety checks executed flawlessly in `check_project`.

**Bilinen sınırlamalar:**
- Selection does not actively allocate portfolio positions or handle execution mechanisms.
- Requires offline pre-calculated data points (e.g., historical returns matrix structure).
- Exposure analysis utilizes artificial theoretical bases entirely uncoupled from market equity realities.

**Phase 27’ye hazırlık:**
The current layer exposes finalized sandbox selection arrays along with extensive correlational matrix contexts. Phase 27 can now reliably process these non-actionable outputs inside Portfolio Construction routines, developing structural allocations (e.g. Volatility Targeting or Risk Parity), whilst maintaining stringent boundaries against execution processes.
"""
with open("PHASE_26_REPORT.md", "w") as f:
    f.write(report)
