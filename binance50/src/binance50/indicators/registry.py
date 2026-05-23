from collections.abc import Callable

from binance50.config.models import AppConfig
from binance50.core.exceptions import IndicatorRegistryError
from binance50.indicators.models import IndicatorBackend, IndicatorGroup, IndicatorSpec


class IndicatorRegistry:
    def __init__(self, config: AppConfig):
        self.config = config
        self._specs: dict[str, IndicatorSpec] = {}
        self._funcs: dict[str, Callable] = {}

        # Load default specs based on config
        defaults = self.build_default_specs(config)
        for spec, func in defaults:
            self.register(spec, func)

    def register(self, spec: IndicatorSpec, func: Callable | None = None) -> None:
        if spec.name in self._specs:
            raise IndicatorRegistryError(f"Indicator with name '{spec.name}' is already registered")

        if len(self._specs) >= self.config.indicators.max_indicator_specs_per_run:
            raise IndicatorRegistryError(
                f"Maximum number of indicators ({self.config.indicators.max_indicator_specs_per_run}) reached"
            )

        self._specs[spec.name] = spec
        if func:
            self._funcs[spec.name] = func

    def get(self, name: str) -> IndicatorSpec:
        spec = self._specs.get(name)
        if not spec:
            raise IndicatorRegistryError(f"Indicator not found: {name}")
        return spec

    def get_func(self, name: str) -> Callable | None:
        return self._funcs.get(name)

    def list_specs(
        self, group: IndicatorGroup | None = None, backend: IndicatorBackend | None = None
    ) -> list[IndicatorSpec]:
        res = list(self._specs.values())
        if group:
            res = [s for s in res if s.group == group]
        if backend:
            res = [s for s in res if s.backend == backend]
        return res

    def validate_specs(self, specs: list[IndicatorSpec], config: AppConfig) -> None:
        if len(specs) > config.indicators.max_indicator_specs_per_run:
            raise IndicatorRegistryError(f"Too many indicator specs: {len(specs)}")

        out_cols = 0
        for s in specs:
            out_cols += len(s.output_columns)

        if out_cols > config.indicators.max_columns_allowed:
            raise IndicatorRegistryError(f"Too many output columns: {out_cols}")

    @staticmethod
    def build_default_specs(config: AppConfig) -> list[tuple[IndicatorSpec, Callable | None]]:
        # This will map configuration to specs. For native, we don't strictly need to pass func
        # if the engine knows how to route to native. But passing func is cleaner.
        from binance50.indicators import momentum, trend, volatility, volume

        specs = []
        ind_cfg = config.indicators
        backend = IndicatorBackend(ind_cfg.default_backend)

        if ind_cfg.trend.enabled:
            for p in ind_cfg.trend.sma_periods:
                spec = IndicatorSpec(
                    f"sma_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"trend_sma_{p}"],
                    p,
                )
                specs.append((spec, trend.sma))
            for p in ind_cfg.trend.ema_periods:
                spec = IndicatorSpec(
                    f"ema_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"trend_ema_{p}"],
                    p,
                )
                specs.append((spec, trend.ema))
            for p in ind_cfg.trend.wma_periods:
                spec = IndicatorSpec(
                    f"wma_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"trend_wma_{p}"],
                    p,
                )
                specs.append((spec, trend.wma))
            for p in ind_cfg.trend.dema_periods:
                spec = IndicatorSpec(
                    f"dema_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"trend_dema_{p}"],
                    p,
                )
                specs.append((spec, trend.dema))
            for p in ind_cfg.trend.tema_periods:
                spec = IndicatorSpec(
                    f"tema_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"trend_tema_{p}"],
                    p,
                )
                specs.append((spec, trend.tema))

            if ind_cfg.trend.macd.enabled:
                f, s, sig = (
                    ind_cfg.trend.macd.fast,
                    ind_cfg.trend.macd.slow,
                    ind_cfg.trend.macd.signal,
                )
                if s > f:
                    spec = IndicatorSpec(
                        f"macd_{f}_{s}_{sig}",
                        IndicatorGroup.TREND,
                        backend,
                        {"fast": f, "slow": s, "signal": sig},
                        ["close"],
                        [
                            f"trend_macd_{f}_{s}_{sig}",
                            f"trend_macd_signal_{f}_{s}_{sig}",
                            f"trend_macd_hist_{f}_{s}_{sig}",
                        ],
                        s + sig,
                    )
                    specs.append((spec, trend.macd))

            if ind_cfg.trend.adx.enabled:
                p = ind_cfg.trend.adx.period
                spec = IndicatorSpec(
                    f"adx_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["high", "low", "close"],
                    [f"trend_adx_{p}", f"trend_plus_di_{p}", f"trend_minus_di_{p}"],
                    p * 2,
                )
                specs.append((spec, trend.adx))

            if ind_cfg.trend.aroon.enabled:
                p = ind_cfg.trend.aroon.period
                spec = IndicatorSpec(
                    f"aroon_{p}",
                    IndicatorGroup.TREND,
                    backend,
                    {"period": p},
                    ["high", "low"],
                    [f"trend_aroon_up_{p}", f"trend_aroon_down_{p}", f"trend_aroon_osc_{p}"],
                    p + 1,
                )
                specs.append((spec, trend.aroon))

        if ind_cfg.momentum.enabled:
            for p in ind_cfg.momentum.rsi_periods:
                spec = IndicatorSpec(
                    f"rsi_{p}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"mom_rsi_{p}"],
                    p,
                )
                specs.append((spec, momentum.rsi))
            if ind_cfg.momentum.stochastic.enabled:
                k, d, sk = (
                    ind_cfg.momentum.stochastic.k_period,
                    ind_cfg.momentum.stochastic.d_period,
                    ind_cfg.momentum.stochastic.smooth_k,
                )
                spec = IndicatorSpec(
                    f"stoch_{k}_{d}_{sk}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"k_period": k, "d_period": d, "smooth_k": sk},
                    ["high", "low", "close"],
                    [f"mom_stoch_k_{k}_{d}_{sk}", f"mom_stoch_d_{k}_{d}_{sk}"],
                    k + d,
                )
                specs.append((spec, momentum.stochastic))
            if ind_cfg.momentum.stoch_rsi.enabled:
                rsip, sp, kp, dp = (
                    ind_cfg.momentum.stoch_rsi.rsi_period,
                    ind_cfg.momentum.stoch_rsi.stoch_period,
                    ind_cfg.momentum.stoch_rsi.k_period,
                    ind_cfg.momentum.stoch_rsi.d_period,
                )
                spec = IndicatorSpec(
                    f"stoch_rsi_{rsip}_{sp}_{kp}_{dp}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"rsi_period": rsip, "stoch_period": sp, "k_period": kp, "d_period": dp},
                    ["close"],
                    [
                        f"mom_stoch_rsi_k_{rsip}_{sp}_{kp}_{dp}",
                        f"mom_stoch_rsi_d_{rsip}_{sp}_{kp}_{dp}",
                    ],
                    rsip + sp + kp + dp,
                )
                specs.append((spec, momentum.stoch_rsi))
            for p in ind_cfg.momentum.roc_periods:
                spec = IndicatorSpec(
                    f"roc_{p}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"mom_roc_{p}"],
                    p,
                )
                specs.append((spec, momentum.roc))
            for p in ind_cfg.momentum.mom_periods:
                spec = IndicatorSpec(
                    f"mom_{p}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"mom_mom_{p}"],
                    p,
                )
                specs.append((spec, momentum.momentum))
            for p in ind_cfg.momentum.cci_periods:
                spec = IndicatorSpec(
                    f"cci_{p}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"period": p},
                    ["high", "low", "close"],
                    [f"mom_cci_{p}"],
                    p,
                )
                specs.append((spec, momentum.cci))
            for p in ind_cfg.momentum.willr_periods:
                spec = IndicatorSpec(
                    f"willr_{p}",
                    IndicatorGroup.MOMENTUM,
                    backend,
                    {"period": p},
                    ["high", "low", "close"],
                    [f"mom_willr_{p}"],
                    p,
                )
                specs.append((spec, momentum.williams_r))

        if ind_cfg.volatility.enabled:
            for p in ind_cfg.volatility.atr_periods:
                spec = IndicatorSpec(
                    f"atr_{p}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p},
                    ["high", "low", "close"],
                    [f"vol_atr_{p}"],
                    p,
                )
                specs.append((spec, volatility.atr))
            for p in ind_cfg.volatility.natr_periods:
                spec = IndicatorSpec(
                    f"natr_{p}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p},
                    ["high", "low", "close"],
                    [f"vol_natr_{p}"],
                    p,
                )
                specs.append((spec, volatility.natr))
            if ind_cfg.volatility.bollinger.enabled:
                p, s = ind_cfg.volatility.bollinger.period, ind_cfg.volatility.bollinger.stddev
                spec = IndicatorSpec(
                    f"bb_{p}_{int(s)}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p, "stddev": s},
                    ["close"],
                    [
                        f"vol_bb_mid_{p}_{int(s)}",
                        f"vol_bb_upper_{p}_{int(s)}",
                        f"vol_bb_lower_{p}_{int(s)}",
                    ],
                    p,
                )
                specs.append((spec, volatility.bollinger_bands))
            if ind_cfg.volatility.keltner.enabled:
                p, ap, m = (
                    ind_cfg.volatility.keltner.period,
                    ind_cfg.volatility.keltner.atr_period,
                    ind_cfg.volatility.keltner.multiplier,
                )
                spec = IndicatorSpec(
                    f"kc_{p}_{ap}_{int(m)}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p, "atr_period": ap, "multiplier": m},
                    ["high", "low", "close"],
                    [
                        f"vol_kc_mid_{p}_{ap}_{int(m)}",
                        f"vol_kc_upper_{p}_{ap}_{int(m)}",
                        f"vol_kc_lower_{p}_{ap}_{int(m)}",
                    ],
                    max(p, ap),
                )
                specs.append((spec, volatility.keltner_channels))
            if ind_cfg.volatility.donchian.enabled:
                p = ind_cfg.volatility.donchian.period
                spec = IndicatorSpec(
                    f"donchian_{p}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p},
                    ["high", "low"],
                    [f"vol_donchian_high_{p}", f"vol_donchian_low_{p}"],
                    p,
                )
                specs.append((spec, volatility.donchian_channels))
            for p in ind_cfg.volatility.rolling_std_periods:
                spec = IndicatorSpec(
                    f"rolling_std_{p}",
                    IndicatorGroup.VOLATILITY,
                    backend,
                    {"period": p},
                    ["close"],
                    [f"vol_rolling_std_{p}"],
                    p,
                )
                specs.append((spec, volatility.rolling_std))

        if ind_cfg.volume.enabled:
            if ind_cfg.volume.obv:
                spec = IndicatorSpec(
                    "obv", IndicatorGroup.VOLUME, backend, {}, ["close", "volume"], ["volu_obv"], 1
                )
                specs.append((spec, volume.obv))
            if ind_cfg.volume.vwap.enabled:
                p = ind_cfg.volume.vwap.rolling_period
                spec = IndicatorSpec(
                    f"vwap_{p}",
                    IndicatorGroup.VOLUME,
                    backend,
                    {"period": p},
                    ["high", "low", "close", "volume"],
                    [f"volu_vwap_{p}"],
                    p,
                )
                specs.append((spec, volume.vwap))
            for p in ind_cfg.volume.mfi_periods:
                spec = IndicatorSpec(
                    f"mfi_{p}",
                    IndicatorGroup.VOLUME,
                    backend,
                    {"period": p},
                    ["high", "low", "close", "volume"],
                    [f"volu_mfi_{p}"],
                    p,
                )
                specs.append((spec, volume.mfi))
            for p in ind_cfg.volume.cmf_periods:
                spec = IndicatorSpec(
                    f"cmf_{p}",
                    IndicatorGroup.VOLUME,
                    backend,
                    {"period": p},
                    ["high", "low", "close", "volume"],
                    [f"volu_cmf_{p}"],
                    p,
                )
                specs.append((spec, volume.cmf))
            if ind_cfg.volume.adl:
                spec = IndicatorSpec(
                    "adl",
                    IndicatorGroup.VOLUME,
                    backend,
                    {},
                    ["high", "low", "close", "volume"],
                    ["volu_adl"],
                    1,
                )
                specs.append((spec, volume.accumulation_distribution_line))
            for p in ind_cfg.volume.volume_sma_periods:
                spec = IndicatorSpec(
                    f"volume_sma_{p}",
                    IndicatorGroup.VOLUME,
                    backend,
                    {"period": p},
                    ["volume"],
                    [f"volu_volume_sma_{p}"],
                    p,
                )
                specs.append((spec, volume.volume_sma))
            for p in ind_cfg.volume.volume_ema_periods:
                spec = IndicatorSpec(
                    f"volume_ema_{p}",
                    IndicatorGroup.VOLUME,
                    backend,
                    {"period": p},
                    ["volume"],
                    [f"volu_volume_ema_{p}"],
                    p,
                )
                specs.append((spec, volume.volume_ema))

        return specs
