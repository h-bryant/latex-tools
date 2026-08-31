"""Estimation and simulation machinery for the Bryan dew point forecast.

Imported by run.py (final forecast) and by select_spec.py (specification
search). Kept separate so that the two scripts cannot drift apart.

Model
-----
Let y_t be the mean of the daily 7:00 AM dew point readings in month t, m(t) the
calendar month, and tau_t time in years measured from a fixed reference month.

    y_t   = mu_t + sigma_t * z_t
    mu_t  = b0 + delta * tau_t + sum_{k=1..K} [a_k cos(2 pi k m/12) + c_k sin(...)]
    log sigma_t^2 = g0        + sum_{l=1..L} [d_l cos(2 pi l m/12) + e_l sin(...)]
    z_t   = phi z_{t-1} + eps_t,   eps_t iid, mean zero

The scale equation is the multiplicative heteroskedasticity model of
Harvey (1976). The 7:00 AM dew point is roughly four times as variable in
January as in July, because winter mornings alternate between continental and
maritime air masses while summer mornings are almost always in Gulf air.

`delta` is handled three ways, chosen by out-of-sample comparison in
select_spec.py:

  "free"     estimate the trend on the Coulter Field record itself;
  "none"     impose delta = 0;
  "anchored" impose the trend estimated from the much longer Easterwood Field
             record, using only Easterwood data dated on or before the
             forecast origin.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, Literal

import numpy as np
import polars as pl
import statsmodels.api as sm

ROOT: Final[Path] = Path(__file__).resolve().parents[2]

HORIZON: Final[int] = 12
HAC_LAGS: Final[int] = 6
MAX_HARMONICS_MEAN: Final[int] = 4
MAX_HARMONICS_SCALE: Final[int] = 3

# E[log chi^2_1] = digamma(1/2) + log 2; subtracting it de-biases the
# log-variance regression (Harvey, 1976).
LOG_CHI2_BIAS: Final[float] = -1.2703628454614782

TrendMode = Literal["free", "none", "anchored"]


ScaleSource = Literal["target", "anchor"]


@dataclass(frozen=True)
class Spec:
    """A model specification."""

    trend: TrendMode = "anchored"
    k_mean: int | None = None            # None selects K by BIC
    l_scale: int | None = None           # None selects L by BIC
    weighted: bool = True                # weight the mean fit by 1 / sigma^2
    scale_source: ScaleSource = "target"  # whose residuals shape log sigma^2

    @property
    def label(self) -> str:
        k = "BIC" if self.k_mean is None else str(self.k_mean)
        l = "BIC" if self.l_scale is None else str(self.l_scale)
        return (
            f"trend={self.trend:<8s} K={k:<3s} L={l:<3s} "
            f"{'WLS' if self.weighted else 'OLS'} scale={self.scale_source}"
        )


# --------------------------------------------------------------------------
# calendar helpers
# --------------------------------------------------------------------------

def month_index(d: dt.date, origin: dt.date) -> int:
    return (d.year - origin.year) * 12 + (d.month - origin.month)


def add_months(d: dt.date, k: int) -> dt.date:
    total = (d.year * 12 + d.month - 1) + k
    return dt.date(total // 12, total % 12 + 1, 1)


# --------------------------------------------------------------------------
# design matrices
# --------------------------------------------------------------------------

def harmonics(month: np.ndarray, n_harmonics: int) -> np.ndarray:
    """Fourier basis [cos(2 pi k m / 12), sin(2 pi k m / 12)] for k = 1..K."""
    angle = 2.0 * np.pi * month[:, None] * np.arange(1, n_harmonics + 1)[None, :] / 12.0
    return np.hstack([np.cos(angle), np.sin(angle)])


def mean_design(month: np.ndarray, tau: np.ndarray, k: int, with_trend: bool) -> np.ndarray:
    cols = [np.ones((month.size, 1))]
    if with_trend:
        cols.append(tau[:, None])
    cols.append(harmonics(month, k))
    return np.hstack(cols)


def scale_design(month: np.ndarray, l: int) -> np.ndarray:
    return np.hstack([np.ones((month.size, 1)), harmonics(month, l)])


def bic(resid: np.ndarray, n_params: int) -> float:
    n = resid.size
    return n * np.log(float(resid @ resid) / n) + n_params * np.log(n)


# --------------------------------------------------------------------------
# fitting
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Fit:
    spec: Spec
    k_mean: int
    l_scale: int
    with_trend: bool
    beta: np.ndarray
    beta_cov: np.ndarray
    beta_se: np.ndarray
    gamma: np.ndarray
    delta: float               # trend in degrees F per year actually applied
    delta_se: float
    phi: float
    phi_se: float
    eps: np.ndarray            # centered innovations of the standardized series
    z_last: float
    tau_origin: float
    sigma_hat: np.ndarray
    resid: np.ndarray
    n_obs: int
    ljung_box_p: float


def _fit_scale(resid: np.ndarray, month: np.ndarray, l: int) -> np.ndarray:
    target = np.log(np.maximum(resid**2, 1e-8)) - LOG_CHI2_BIAS
    return np.linalg.lstsq(scale_design(month, l), target, rcond=None)[0]


def _ols_resid(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return y - x @ np.linalg.lstsq(x, y, rcond=None)[0]


def _select_k(y: np.ndarray, month: np.ndarray, tau: np.ndarray, with_trend: bool) -> int:
    n_fixed = 2 if with_trend else 1
    return min(
        range(1, MAX_HARMONICS_MEAN + 1),
        key=lambda k: bic(
            _ols_resid(mean_design(month, tau, k, with_trend), y), n_fixed + 2 * k
        ),
    )


def _select_l(resid: np.ndarray, month: np.ndarray) -> int:
    log_sq = np.log(np.maximum(resid**2, 1e-8))
    return min(
        range(1, MAX_HARMONICS_SCALE + 1),
        key=lambda l: bic(_ols_resid(scale_design(month, l), log_sq), 1 + 2 * l),
    )


def estimate_anchor_trend(anchor: pl.DataFrame, cutoff: dt.date) -> tuple[float, float]:
    """Trend in degrees F per year from the long cross-check record, using only
    observations dated on or before `cutoff` so the backtest stays honest."""
    sub = anchor.filter(pl.col("month_start") <= cutoff).sort("month_start")
    dates = sub["month_start"].to_list()
    y = sub["mean_dwpf"].to_numpy()
    month = np.array([d.month for d in dates], dtype=float)
    tau = np.array([month_index(d, dates[0]) for d in dates]) / 12.0
    x = mean_design(month, tau, 2, with_trend=True)
    fitted = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    return float(fitted.params[1]), float(fitted.bse[1])


def estimate_anchor_scale(
    anchor: pl.DataFrame, cutoff: dt.date, l: int | None
) -> tuple[np.ndarray, int]:
    """Seasonal shape of log sigma^2 from the long cross-check record.

    Thirteen years of Coulter Field data supply only about thirteen observations
    per calendar month, and log(u^2) has variance pi^2 / 2, so the seasonal
    variance profile is poorly determined at the target station. The Easterwood
    record is more than twice as long. Only its level is discarded: the shape is
    carried over and rescaled to the target station in `fit_model`.
    """
    sub = anchor.filter(pl.col("month_start") <= cutoff).sort("month_start")
    dates = sub["month_start"].to_list()
    y = sub["mean_dwpf"].to_numpy()
    month = np.array([d.month for d in dates], dtype=float)
    tau = np.array([month_index(d, dates[0]) for d in dates]) / 12.0
    resid = _ols_resid(mean_design(month, tau, 2, with_trend=True), y)
    l_used = l if l is not None else _select_l(resid, month)
    return _fit_scale(resid, month, l_used), l_used


def fit_model(
    y: np.ndarray,
    month: np.ndarray,
    tau: np.ndarray,
    t_index: np.ndarray,
    spec: Spec,
    anchor_delta: tuple[float, float] = (0.0, 0.0),
    anchor_gamma: tuple[np.ndarray, int] | None = None,
) -> Fit:
    """Fit the mean, scale, and AR(1) equations in sequence."""
    with_trend = spec.trend == "free"
    delta, delta_se = anchor_delta if spec.trend == "anchored" else (0.0, 0.0)

    # With an imposed trend, remove it before fitting, then restore it.
    y_work = y - delta * tau if spec.trend == "anchored" else y

    k = spec.k_mean if spec.k_mean is not None else _select_k(y_work, month, tau, with_trend)
    x = mean_design(month, tau, k, with_trend)

    first_resid = _ols_resid(x, y_work)

    def scale_coefficients(resid: np.ndarray) -> tuple[np.ndarray, int]:
        """Coefficients and order of the log-variance equation."""
        if spec.scale_source == "anchor":
            if anchor_gamma is None:
                raise ValueError("scale_source='anchor' requires anchor_gamma")
            return anchor_gamma
        order = spec.l_scale if spec.l_scale is not None else _select_l(resid, month)
        return _fit_scale(resid, month, order), order

    gamma, l = scale_coefficients(first_resid)

    fitted = sm.OLS(y_work, x).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    if spec.weighted:
        # Two passes of feasible GLS: reweight by the fitted scale, refit the scale.
        for _ in range(2):
            sigma = np.exp(0.5 * (scale_design(month, l) @ gamma))
            fitted = sm.WLS(y_work, x, weights=1.0 / sigma**2).fit(
                cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
            )
            gamma, l = scale_coefficients(np.asarray(fitted.resid))
    else:
        gamma, l = scale_coefficients(np.asarray(fitted.resid))

    resid = np.asarray(fitted.resid)

    # Normalize the level of the scale function so that the standardized
    # residuals have unit variance at the target station. This leaves the
    # seasonal shape untouched and is what makes a borrowed shape usable.
    sigma = np.exp(0.5 * (scale_design(month, l) @ gamma))
    level = float((resid / sigma).std(ddof=0))
    gamma = gamma + np.concatenate(([2.0 * np.log(level)], np.zeros(gamma.size - 1)))
    sigma = sigma * level
    z = resid / sigma

    if with_trend:
        delta, delta_se = float(fitted.params[1]), float(fitted.bse[1])

    # AR(1) on the standardized residuals, using consecutive month pairs only so
    # the gaps in the record do not create spurious lags.
    consecutive = np.diff(t_index) == 1
    ar = sm.OLS(z[1:][consecutive], z[:-1][consecutive][:, None]).fit()
    eps = np.asarray(ar.resid)
    eps = eps - eps.mean()

    return Fit(
        spec=spec,
        k_mean=k,
        l_scale=l,
        with_trend=with_trend,
        beta=np.asarray(fitted.params),
        beta_cov=np.asarray(fitted.cov_params()),
        beta_se=np.asarray(fitted.bse),
        gamma=gamma,
        delta=delta,
        delta_se=delta_se,
        phi=float(ar.params[0]),
        phi_se=float(ar.bse[0]),
        eps=eps,
        z_last=float(z[-1]),
        tau_origin=float(tau[-1]),
        sigma_hat=sigma,
        resid=resid,
        n_obs=y.size,
        ljung_box_p=float(
            sm.stats.acorr_ljungbox(ar.resid, lags=[12], return_df=True)["lb_pvalue"].iloc[0]
        ),
    )


# --------------------------------------------------------------------------
# simulation
# --------------------------------------------------------------------------

def simulate(
    fit: Fit,
    future_month: np.ndarray,
    future_tau: np.ndarray,
    n_paths: int,
    rng: np.random.Generator,
    parameter_uncertainty: bool = True,
) -> np.ndarray:
    """Return an (n_paths, horizon) array of simulated monthly means."""
    horizon = future_month.size
    x_future = mean_design(future_month, future_tau, fit.k_mean, fit.with_trend)
    sigma_future = np.exp(0.5 * (scale_design(future_month, fit.l_scale) @ fit.gamma))

    if parameter_uncertainty:
        beta_draws = rng.multivariate_normal(fit.beta, fit.beta_cov, size=n_paths)
        phi_draws = np.clip(rng.normal(fit.phi, fit.phi_se, size=n_paths), -0.98, 0.98)
    else:
        beta_draws = np.tile(fit.beta, (n_paths, 1))
        phi_draws = np.full(n_paths, fit.phi)

    mu_paths = beta_draws @ x_future.T

    if fit.spec.trend == "anchored":
        # The imposed trend carries its own estimation error, drawn per path.
        delta_draws = rng.normal(fit.delta, fit.delta_se, size=n_paths)
        mu_paths = mu_paths + delta_draws[:, None] * future_tau[None, :]

    shocks = rng.choice(fit.eps, size=(n_paths, horizon), replace=True)
    z = np.full(n_paths, fit.z_last)
    z_paths = np.empty((n_paths, horizon))
    for h in range(horizon):
        z = phi_draws * z + shocks[:, h]
        z_paths[:, h] = z

    return mu_paths + z_paths * sigma_future[None, :]


def seasonal_profile(fit: Fit, tau: float) -> tuple[np.ndarray, np.ndarray]:
    """Conditional mean and scale for each calendar month at a given tau."""
    months = np.arange(1, 13, dtype=float)
    mu = mean_design(months, np.full(12, tau), fit.k_mean, fit.with_trend) @ fit.beta
    if fit.spec.trend == "anchored":
        mu = mu + fit.delta * tau
    sd = np.exp(0.5 * (scale_design(months, fit.l_scale) @ fit.gamma))
    return mu, sd


def crps_from_ensemble(sample: np.ndarray, observed: float) -> float:
    """CRPS of an ensemble forecast (Hersbach, 2000), via the order-statistic
    identity for E|X - X'|, which is O(n) once the sample is sorted."""
    x = np.sort(sample)
    n = x.size
    term1 = float(np.abs(x - observed).mean())
    weights = 2.0 * np.arange(1, n + 1) - n - 1
    term2 = float(2.0 * (weights * x).sum() / (n * n))
    return term1 - 0.5 * term2


# --------------------------------------------------------------------------
# data assembly
# --------------------------------------------------------------------------

def load_series(station: str) -> pl.DataFrame:
    return (
        pl.read_csv(
            ROOT / "analysis" / "monthly_dewpoint" / "output" / "monthly_dewpoint_0700.csv",
            try_parse_dates=True,
        )
        .filter(pl.col("station") == station)
        .sort("month_start")
    )


def make_arrays(df: pl.DataFrame, reference: dt.date) -> dict[str, np.ndarray]:
    dates = df["month_start"].to_list()
    t_index = np.array([month_index(d, reference) for d in dates])
    return {
        "y": df["mean_dwpf"].to_numpy(),
        "month": np.array([d.month for d in dates], dtype=float),
        "tau": t_index / 12.0,
        "t_index": t_index,
    }


def forecast_inputs(last_obs: dt.date, reference: dt.date, horizon: int = HORIZON):
    """Calendar months, month numbers, and tau values for the forecast period."""
    future = [add_months(last_obs, h) for h in range(1, horizon + 1)]
    month = np.array([d.month for d in future], dtype=float)
    tau = np.array([month_index(d, reference) for d in future]) / 12.0
    return future, month, tau


# --------------------------------------------------------------------------
# backtest
# --------------------------------------------------------------------------

def backtest(
    df: pl.DataFrame,
    anchor: pl.DataFrame,
    reference: dt.date,
    spec: Spec,
    rng: np.random.Generator,
    first_origin: dt.date = dt.date(2019, 8, 1),
    n_paths: int = 4_000,
    with_benchmark: bool = False,
) -> pl.DataFrame:
    """Expanding-window pseudo-out-of-sample evaluation.

    Every quantity used at an origin is estimated from data dated on or before
    that origin, including the anchored trend.
    """
    dates = df["month_start"].to_list()
    values = dict(zip(dates, df["mean_dwpf"].to_list()))
    rows: list[dict[str, object]] = []

    cut = first_origin
    while cut <= add_months(dates[-1], -1):
        train = df.filter(pl.col("month_start") <= cut)
        if train.height < 60:
            cut = add_months(cut, 1)
            continue
        arrays = make_arrays(train, reference)
        anchor_delta = (
            estimate_anchor_trend(anchor, cut) if spec.trend == "anchored" else (0.0, 0.0)
        )
        anchor_gamma = (
            estimate_anchor_scale(anchor, cut, spec.l_scale)
            if spec.scale_source == "anchor"
            else None
        )
        fit = fit_model(
            arrays["y"],
            arrays["month"],
            arrays["tau"],
            arrays["t_index"],
            spec,
            anchor_delta,
            anchor_gamma,
        )

        future, f_month, f_tau = forecast_inputs(cut, reference)
        draws = simulate(fit, f_month, f_tau, n_paths, rng)
        draws_noar = (
            simulate(replace_phi(fit, 0.0), f_month, f_tau, n_paths, rng)
            if with_benchmark
            else None
        )

        for h, d in enumerate(future, start=1):
            if d not in values:
                continue
            actual = values[d]
            s = draws[:, h - 1]
            median = float(np.median(s))
            lo50, hi50 = np.quantile(s, [0.25, 0.75])
            lo80, hi80 = np.quantile(s, [0.10, 0.90])
            lo95, hi95 = np.quantile(s, [0.025, 0.975])
            row = {
                "origin": cut,
                "target": d,
                "h": h,
                "actual": actual,
                "median": median,
                "err": median - actual,
                "abs_err": abs(median - actual),
                "sq_err": (median - actual) ** 2,
                "crps": crps_from_ensemble(s, actual),
                "pit": float((s < actual).mean()),
                "in50": float(lo50 <= actual <= hi50),
                "in80": float(lo80 <= actual <= hi80),
                "in95": float(lo95 <= actual <= hi95),
            }
            if draws_noar is not None:
                row["crps_no_ar"] = crps_from_ensemble(draws_noar[:, h - 1], actual)
            rows.append(row)
        cut = add_months(cut, 1)

    return pl.DataFrame(rows)


def replace_phi(fit: Fit, phi: float) -> Fit:
    return replace(fit, phi=phi, phi_se=0.0)


def pit_uniformity_pvalue(pit: np.ndarray) -> float:
    """Pearson chi-square test that the PIT values are uniform on ten bins."""
    from scipy import stats

    counts, _ = np.histogram(pit, bins=10, range=(0.0, 1.0))
    expected = pit.size / 10.0
    stat = float(((counts - expected) ** 2 / expected).sum())
    return float(stats.chi2.sf(stat, df=9))
