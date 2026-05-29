
# Phase 27: Portfolio Construction Sandbox v1 Report

## Oluşturulan/Güncellenen Dosyalar
- `src/binance50/config/models.py`
- `src/binance50/core/exceptions.py`
- `src/binance50/core/error_codes.py`
- `src/binance50/core/error_classifier.py`
- `src/binance50/portfolio/construction/__init__.py`
- `src/binance50/portfolio/construction/models.py`
- `src/binance50/portfolio/construction/loaders.py`
- `src/binance50/portfolio/construction/returns.py`
- `src/binance50/portfolio/construction/covariance.py`
- `src/binance50/portfolio/construction/volatility.py`
- `src/binance50/portfolio/construction/baselines.py`
- `src/binance50/portfolio/construction/inverse_volatility.py`
- `src/binance50/portfolio/construction/volatility_targeting.py`
- `src/binance50/portfolio/construction/risk_parity.py`
- `src/binance50/portfolio/construction/risk_contribution.py`
- `src/binance50/portfolio/construction/constraints.py`
- `src/binance50/portfolio/construction/allocation.py`
- `src/binance50/portfolio/construction/explanations.py`
- `src/binance50/portfolio/construction/optimizer_skeleton.py`
- `src/binance50/portfolio/construction/adapters/base.py`
- `src/binance50/portfolio/construction/adapters/scipy_slsqp_adapter.py`
- `src/binance50/portfolio/construction/adapters/pyportfolioopt_adapter.py`
- `src/binance50/portfolio/construction/reports.py`
- `src/binance50/portfolio/construction/cache.py`
- `src/binance50/portfolio/construction/export.py`
- `src/binance50/portfolio/construction/reproducibility.py`
- `src/binance50/portfolio/construction/quality.py`
- `src/binance50/portfolio/construction/runner.py`
- `src/binance50/safety/portfolio_construction_guard.py`
- `src/binance50/safety/portfolio_allocation_guard.py`
- `src/binance50/safety/portfolio_optimizer_construction_guard.py`
- `src/binance50/safety/portfolio_construction_integration_guard.py`
- `src/binance50/storage/schemas.py`
- `src/binance50/storage/importers.py`
- `src/binance50/cli.py`
- `scripts/check_project.py`
- `tests/*` (added new tests)
- `docs/*` (updated docs)

## Portfolio Construction Config Kararları
- Sandbox and purely hypothetical setup with explicit blocks against real execution and production allocation.
- Implemented flags for blocking outputs such as `quantity`, `leverage`, and `entry_price`.
- Introduced simulated capital for calculations (`hypothetical_notional_usdt`).
- Implemented support for method selection, constraints, covariance, and volatility.

## Mimarideki Bileşenler
- **Loader:** Extracts the sandbox candidates and evaluates flags to ensure blocked intent.
- **Returns & Covariance Matrix:** Backward-looking data for covariance calculation avoiding future data.
- **Volatility Estimates:** Symbol & portfolio realized volatility calculation with optional floors and caps.
- **Equal Weight Baseline:** Benchmark allocation.
- **Inverse Volatility Allocation:** The default method assigning weight based on `1/volatility`.
- **Volatility Targeting:** Modifies inverse volatility to fit a portfolio risk budget target using scale factors (max 1.0).
- **Risk Parity Skeleton:** SciPy optimized risk parity calculation seeking equal marginal risk contribution (ERC).
- **Risk Contribution Analysis:** Breakdowns marginal, component, and percentage risk contribution.
- **Constraints:** Strict rules handling `max_single_weight_pct`, `max_pair_correlation`, etc.
- **Optimizer Skeletons:** Implemented base SciPy SLSQP bounds and PyPortfolioOpt structural outlines ensuring production block safety.

## Güvenlik, Kalite ve Doğrulama
- Built **Safety Guards** (Construction, Allocation, Optimizer, and Integration) restricting any form of position sizing or exchange interaction.
- Verified missing explanations, unexpected outputs, `NaN` or infinite constraints within **Quality Reports**.
- Setup cache retrieval, database storage updates, and CLI tools for local manual operations.

## Test Sonuçları
- All PyTest unit tests pass successfully.
- Code formatted and checked with Ruff & Black.
- The `check_project.py` script validates the new commands.

## Bilinen Sınırlamalar
- No live allocation or actual position sizing functionality.

## Phase 28’e Hazırlık
The system now outputs sandbox allocation values along with their justifications. In Phase 28, the execution abstraction layer will separate this safely from gateway integration without mixing orders with hypothetical signals.
