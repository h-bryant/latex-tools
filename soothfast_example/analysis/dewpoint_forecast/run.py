"""Final probabilistic forecast of the monthly average 7:00 AM dew point, Bryan TX.

Reproduce with:
    python analysis/dewpoint_forecast/run.py

Requires analysis/monthly_dewpoint/run.py to have been run first. The chosen
specification comes from select_spec.py; the model itself lives in model.py.

Output: analysis/dewpoint_forecast/output/forecast_quantiles.csv
        analysis/dewpoint_forecast/output/fitted_components.csv
        analysis/dewpoint_forecast/output/seasonal_profile.csv
        analysis/dewpoint_forecast/output/backtest_by_horizon.csv
        analysis/dewpoint_forecast/output/backtest_detail.csv
        analysis/dewpoint_forecast/output/trend_stability.csv
        analysis/dewpoint_forecast/output/history_window.csv
        analysis/dewpoint_forecast/output/model_summary.txt
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl

from model import (
    HORIZON,
    Spec,
    add_months,
    backtest,
    crps_from_ensemble,
    estimate_anchor_scale,
    estimate_anchor_trend,
    fit_model,
    forecast_inputs,
    load_series,
    make_arrays,
    month_index,
    pit_uniformity_pvalue,
    replace_phi,
    seasonal_profile,
    simulate,
)

OUT_DIR: Final[Path] = Path(__file__).resolve().parent / "output"

TARGET_STATION: Final[str] = "CFD"
ANCHOR_STATION: Final[str] = "CLL"
N_PATHS: Final[int] = 50_000
SEED: Final[int] = 20260831
HISTORY_MONTHS: Final[int] = 24

# Selected by pseudo-out-of-sample CRPS in select_spec.py. See
# output/spec_comparison.txt for the full comparison.
SPEC: Final[Spec] = Spec(
    trend="anchored",
    k_mean=None,
    l_scale=None,
    weighted=False,
    scale_source="anchor",
)

QUANTILES: Final[tuple[float, ...]] = (
    0.025, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.975,
)


def trend_stability(target: pl.DataFrame, reference: dt.date) -> pl.DataFrame:
    """Trend estimated on the target station alone, as the sample lengthens.

    Documents why the freely estimated trend is not extrapolated: it is a
    low-frequency feature of a short record, not a stable slope.
    """
    free = Spec(trend="free", scale_source="target")
    rows: list[dict[str, object]] = []
    cut = dt.date(2019, 8, 1)
    while cut <= target["month_start"].max():
        train = target.filter(pl.col("month_start") <= cut)
        a = make_arrays(train, reference)
        f = fit_model(a["y"], a["month"], a["tau"], a["t_index"], free)
        rows.append(
            {
                "sample_end": cut,
                "n_months": f.n_obs,
                "trend_f_per_decade": round(10.0 * f.delta, 3),
                "hac_se": round(10.0 * f.delta_se, 3),
            }
        )
        cut = add_months(cut, 12)
    return pl.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    target = load_series(TARGET_STATION)
    anchor = load_series(ANCHOR_STATION)
    dates = target["month_start"].to_list()
    reference: dt.date = dates[0]
    last_obs: dt.date = dates[-1]

    arrays = make_arrays(target, reference)
    anchor_delta = estimate_anchor_trend(anchor, last_obs)
    anchor_gamma = estimate_anchor_scale(anchor, last_obs, SPEC.l_scale)
    fit = fit_model(
        arrays["y"], arrays["month"], arrays["tau"], arrays["t_index"],
        SPEC, anchor_delta, anchor_gamma,
    )

    # ---------------- forecast ----------------
    future, f_month, f_tau = forecast_inputs(last_obs, reference)
    draws = simulate(fit, f_month, f_tau, N_PATHS, rng)
    q = np.quantile(draws, QUANTILES, axis=0)

    forecast = pl.DataFrame(
        {
            "month_start": future,
            "h": list(range(1, HORIZON + 1)),
            "mean": np.round(draws.mean(axis=0), 3),
            "sd": np.round(draws.std(axis=0, ddof=1), 3),
            **{f"q{int(p * 1000):03d}": np.round(q[i], 3) for i, p in enumerate(QUANTILES)},
        }
    )
    forecast.write_csv(OUT_DIR / "forecast_quantiles.csv")

    # ---------------- in-sample components ----------------
    z = fit.resid / fit.sigma_hat
    pl.DataFrame(
        {
            "month_start": dates,
            "actual": np.round(arrays["y"], 3),
            "mu_hat": np.round(arrays["y"] - fit.resid, 3),
            "sigma_hat": np.round(fit.sigma_hat, 3),
            "z": np.round(z, 4),
        }
    ).write_csv(OUT_DIR / "fitted_components.csv")

    mu_season, sd_season = seasonal_profile(fit, fit.tau_origin)
    pl.DataFrame(
        {
            "month": list(range(1, 13)),
            "mu_at_origin": np.round(mu_season, 3),
            "sigma": np.round(sd_season, 3),
        }
    ).write_csv(OUT_DIR / "seasonal_profile.csv")

    # ---------------- history window for the first figure ----------------
    window_start = add_months(last_obs, -(HISTORY_MONTHS - 1))
    history = target.filter(pl.col("month_start") >= window_start)
    history.write_csv(OUT_DIR / "history_window.csv")

    # ---------------- diagnostics ----------------
    stability = trend_stability(target, reference)
    stability.write_csv(OUT_DIR / "trend_stability.csv")

    bt = backtest(target, anchor, reference, SPEC, rng, n_paths=8_000, with_benchmark=True)
    bt.write_csv(OUT_DIR / "backtest_detail.csv")
    by_h = (
        bt.group_by("h")
        .agg(
            pl.len().alias("n"),
            pl.col("abs_err").mean().round(3).alias("mae"),
            pl.col("sq_err").mean().sqrt().round(3).alias("rmse"),
            pl.col("crps").mean().round(3).alias("crps"),
            pl.col("crps_no_ar").mean().round(3).alias("crps_no_ar"),
            pl.col("in50").mean().round(3).alias("cover50"),
            pl.col("in80").mean().round(3).alias("cover80"),
            pl.col("in95").mean().round(3).alias("cover95"),
        )
        .sort("h")
    )
    by_h.write_csv(OUT_DIR / "backtest_by_horizon.csv")

    # ---------------- narrative summary ----------------
    obs_2y = history["mean_dwpf"].to_numpy()
    climatology = (
        target.group_by(pl.col("month_start").dt.month().alias("m"))
        .agg(pl.col("mean_dwpf").mean().alias("clim"))
        .sort("m")
    )
    clim_map = dict(zip(climatology["m"].to_list(), climatology["clim"].to_list()))
    anomalies = [
        row["mean_dwpf"] - clim_map[row["month_start"].month]
        for row in history.iter_rows(named=True)
    ]
    hottest = history.sort("mean_dwpf", descending=True).row(0, named=True)
    driest = history.sort("mean_dwpf").row(0, named=True)

    late = bt.filter(pl.col("origin") >= dt.date(2023, 8, 1))
    free_spec_note = stability.row(0, named=True), stability.row(-1, named=True)

    L: list[str] = [
        "=" * 78,
        "MONTHLY AVERAGE 7:00 AM DEW POINT, BRYAN TEXAS",
        "=" * 78,
        "",
        "[data]",
        f"  target station             : {TARGET_STATION} (Coulter Field, Bryan, TX)",
        f"  anchor station             : {ANCHOR_STATION} (Easterwood Field, College Station)",
        f"  estimation sample          : {dates[0]} to {last_obs} ({fit.n_obs} months)",
        f"  months missing from span   : "
        f"{month_index(last_obs, reference) + 1 - fit.n_obs}",
        "",
        "[selected specification]",
        f"  {SPEC.label}",
        f"  mean harmonics K (BIC)     : {fit.k_mean}",
        f"  scale harmonics L (BIC)    : {fit.l_scale}",
        f"  imposed trend              : {10 * fit.delta:+.3f} F per decade "
        f"(HAC s.e. {10 * fit.delta_se:.3f}), from {ANCHOR_STATION} "
        f"{anchor['month_start'].min()} to {last_obs}",
        f"  AR(1) phi                  : {fit.phi:+.4f} (s.e. {fit.phi_se:.4f})",
        f"  Ljung-Box Q(12) p          : {fit.ljung_box_p:.3f}",
        f"  innovation skewness        : {float(((fit.eps / fit.eps.std()) ** 3).mean()):+.3f}",
        f"  innovation excess kurtosis : "
        f"{float(((fit.eps / fit.eps.std()) ** 4).mean()) - 3.0:+.3f}",
        f"  var of standardized resid  : {z.var(ddof=0):.4f}",
        f"  standardized resid, {last_obs}: {fit.z_last:+.3f}",
        "",
        "[why the trend is not estimated freely on the target record]",
        "  trend on CFD alone, by sample end (F per decade):",
    ]
    for r in stability.iter_rows(named=True):
        L.append(
            f"    {r['sample_end']}  n={r['n_months']:3d}  "
            f"{r['trend_f_per_decade']:+6.2f}  (s.e. {r['hac_se']:.2f})"
        )
    L += [
        f"  the estimate falls from {free_spec_note[0]['trend_f_per_decade']:+.2f} to "
        f"{free_spec_note[1]['trend_f_per_decade']:+.2f} F per decade as the record lengthens,",
        f"  against {10 * anchor_delta[0]:+.3f} F per decade from the "
        f"{anchor.height}-month anchor record.",
        "",
        "[seasonal mean and scale at the forecast origin, deg F]",
        "  month     mu   sigma",
    ]
    for i in range(12):
        L.append(f"  {i + 1:5d}  {mu_season[i]:5.1f}   {sd_season[i]:5.2f}")

    L += [
        "",
        f"[observed history: last {HISTORY_MONTHS} months, "
        f"{window_start} to {last_obs}]",
        f"  months observed            : {history.height} of {HISTORY_MONTHS}",
        f"  mean over the window       : {obs_2y.mean():.2f} F",
        f"  mean anomaly vs 2013-2026 climatology: {np.mean(anomalies):+.2f} F",
        f"  months above climatology   : {sum(a > 0 for a in anomalies)} of {len(anomalies)}",
        f"  largest positive anomaly   : {max(anomalies):+.2f} F "
        f"({history.row(int(np.argmax(anomalies)), named=True)['month_start']})",
        f"  largest negative anomaly   : {min(anomalies):+.2f} F "
        f"({history.row(int(np.argmin(anomalies)), named=True)['month_start']})",
        f"  highest monthly mean       : {hottest['mean_dwpf']:.2f} F "
        f"({hottest['month_start']})",
        f"  lowest monthly mean        : {driest['mean_dwpf']:.2f} F "
        f"({driest['month_start']})",
        "",
        f"[forecast, {future[0]} to {future[-1]}, {N_PATHS:,} paths, seed {SEED}]",
        "  month        median    50% interval       80% interval       95% interval",
    ]
    for row in forecast.iter_rows(named=True):
        L.append(
            f"  {row['month_start']}   {row['q500']:6.1f}   "
            f"[{row['q250']:5.1f}, {row['q750']:5.1f}]    "
            f"[{row['q100']:5.1f}, {row['q900']:5.1f}]    "
            f"[{row['q025']:5.1f}, {row['q975']:5.1f}]"
        )
    widths = (forecast["q900"] - forecast["q100"]).to_list()
    narrow, wide = int(np.argmin(widths)), int(np.argmax(widths))
    L += [
        f"  80% interval width: {widths[narrow]:.1f} F ({future[narrow]}) to "
        f"{widths[wide]:.1f} F ({future[wide]})",
        "",
        "[backtest: expanding window, 8,000 paths per origin]",
        f"  origins                    : {bt['origin'].min()} to {bt['origin'].max()}",
        f"  forecast-target pairs      : {bt.height}",
        "  h     n    MAE   RMSE   CRPS  CRPS(no AR)  cov50  cov80  cov95",
    ]
    for r in by_h.iter_rows(named=True):
        L.append(
            f"  {r['h']:2d}  {r['n']:4d}  {r['mae']:5.2f}  {r['rmse']:5.2f}  "
            f"{r['crps']:5.2f}      {r['crps_no_ar']:5.2f}   "
            f"{r['cover50']:5.3f}  {r['cover80']:5.3f}  {r['cover95']:5.3f}"
        )
    by_month = (
        bt.with_columns(pl.col("target").dt.month().alias("m"))
        .group_by("m")
        .agg(
            pl.len().alias("n"),
            pl.col("err").mean().round(2).alias("bias"),
            pl.col("abs_err").mean().round(2).alias("mae"),
            pl.col("in80").mean().round(3).alias("cover80"),
        )
        .sort("m")
    )
    by_month.write_csv(OUT_DIR / "backtest_by_month.csv")
    L += ["", "  by calendar month of the target:", "  month    n    bias    MAE  cov80"]
    for r in by_month.iter_rows(named=True):
        L.append(
            f"  {r['m']:5d}  {r['n']:3d}  {r['bias']:+6.2f}  {r['mae']:5.2f}  {r['cover80']:5.3f}"
        )

    L += [
        "",
        f"  pooled : MAE {bt['abs_err'].mean():.3f}  RMSE {bt['sq_err'].mean() ** 0.5:.3f}  "
        f"CRPS {bt['crps'].mean():.3f}  (no AR: {bt['crps_no_ar'].mean():.3f})",
        f"           coverage {bt['in50'].mean():.3f} / {bt['in80'].mean():.3f} / "
        f"{bt['in95'].mean():.3f}  against nominal 0.50 / 0.80 / 0.95",
        f"           PIT uniformity chi-square p = {pit_uniformity_pvalue(bt['pit'].to_numpy()):.4f}"
        " (overlapping pairs; indicative only)",
        f"  origins 2023-08 onward (n={late.height}): CRPS {late['crps'].mean():.3f}, "
        f"coverage {late['in50'].mean():.3f} / {late['in80'].mean():.3f} / "
        f"{late['in95'].mean():.3f}",
        f"  AR(1) gain at h=1          : CRPS "
        f"{bt.filter(pl.col('h') == 1)['crps'].mean():.3f} with AR versus "
        f"{bt.filter(pl.col('h') == 1)['crps_no_ar'].mean():.3f} without "
        f"({100 * (1 - bt.filter(pl.col('h') == 1)['crps'].mean() / bt.filter(pl.col('h') == 1)['crps_no_ar'].mean()):.1f}% "
        "improvement)",
    ]

    text = "\n".join(L)
    (OUT_DIR / "model_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
