"""Choose the forecasting specification by pseudo-out-of-sample performance.

Reproduce with:
    python analysis/dewpoint_forecast/select_spec.py

Input : analysis/monthly_dewpoint/output/monthly_dewpoint_0700.csv
Output: analysis/dewpoint_forecast/output/spec_comparison.csv
        analysis/dewpoint_forecast/output/spec_comparison.txt

Each candidate specification is run through the same expanding-window backtest,
with every quantity at each origin estimated from data dated on or before that
origin. Specifications are ranked on the continuous ranked probability score,
which scores the whole predictive distribution rather than a point forecast, and
checked for calibration with the coverage rates of the 50, 80, and 95 percent
intervals and a chi-square test of uniformity of the probability integral
transform.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl

from model import Spec, backtest, load_series, pit_uniformity_pvalue

OUT_DIR: Final[Path] = Path(__file__).resolve().parent / "output"
SEED: Final[int] = 20260831

CANDIDATES: Final[tuple[Spec, ...]] = (
    # How to treat the trend, holding the rest fixed.
    Spec(trend="free", scale_source="target"),
    Spec(trend="none", scale_source="target"),
    Spec(trend="anchored", scale_source="target"),
    # Where the seasonal variance profile comes from.
    Spec(trend="anchored", scale_source="anchor"),
    Spec(trend="anchored", scale_source="anchor", l_scale=1),
    Spec(trend="anchored", scale_source="anchor", l_scale=2),
    Spec(trend="anchored", scale_source="anchor", l_scale=3),
    Spec(trend="anchored", scale_source="target", l_scale=2),
    # Harmonics in the mean, and weighted versus unweighted fitting.
    Spec(trend="anchored", scale_source="anchor", k_mean=1),
    Spec(trend="anchored", scale_source="anchor", k_mean=2),
    Spec(trend="anchored", scale_source="anchor", k_mean=3),
    Spec(trend="anchored", scale_source="anchor", weighted=False),
    Spec(trend="anchored", scale_source="anchor", k_mean=2, weighted=False),
    Spec(trend="none", scale_source="anchor", weighted=False),
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    target = load_series("CFD")
    anchor = load_series("CLL")
    reference: dt.date = target["month_start"].to_list()[0]

    rows: list[dict[str, object]] = []
    for spec in CANDIDATES:
        # A fresh generator per specification so the comparison is not affected
        # by the order in which specifications are run.
        rng = np.random.default_rng(SEED)
        bt = backtest(target, anchor, reference, spec, rng)
        pit = bt["pit"].to_numpy()
        rows.append(
            {
                "trend": spec.trend,
                "k_mean": "BIC" if spec.k_mean is None else str(spec.k_mean),
                "l_scale": "BIC" if spec.l_scale is None else str(spec.l_scale),
                "scale_source": spec.scale_source,
                "fit": "WLS" if spec.weighted else "OLS",
                "n": bt.height,
                "crps": round(bt["crps"].mean(), 4),
                "mae": round(bt["abs_err"].mean(), 4),
                "rmse": round(bt["sq_err"].mean() ** 0.5, 4),
                "bias": round(bt["err"].mean(), 4),
                "cover50": round(bt["in50"].mean(), 4),
                "cover80": round(bt["in80"].mean(), 4),
                "cover95": round(bt["in95"].mean(), 4),
                "pit_p": round(pit_uniformity_pvalue(pit), 5),
            }
        )
        print(f"  done: {spec.label}  CRPS {rows[-1]['crps']:.4f}")

    table = pl.DataFrame(rows).sort("crps")
    table.write_csv(OUT_DIR / "spec_comparison.csv")

    header = (
        f"{'trend':<9s} {'K':>4s} {'L':>4s} {'scale':>7s} {'fit':>4s} {'n':>5s} "
        f"{'CRPS':>7s} {'MAE':>6s} {'RMSE':>6s} {'bias':>7s} "
        f"{'cov50':>6s} {'cov80':>6s} {'cov95':>6s} {'PIT p':>7s}"
    )
    lines = [
        "Pseudo-out-of-sample comparison of forecasting specifications.",
        "Expanding window, origins 2019-08 through 2026-07, horizons 1-12 months,",
        "4,000 simulated paths per origin. Ranked by CRPS (lower is better);",
        "nominal coverage 0.50 / 0.80 / 0.95. 'scale' is the record whose",
        "residuals shape the seasonal variance profile: the target station",
        "(Coulter Field) or the longer anchor record (Easterwood Field).",
        "",
        "PIT p is a chi-square test of uniformity of the probability integral",
        "transform on ten bins. The 930 forecast-target pairs at each",
        "specification overlap heavily (each target month is forecast from up to",
        "twelve origins, and neighbouring origins share nearly all of their",
        "training data), so the test's independence assumption fails badly and",
        "the p-value is far too small. Use it only to rank specifications",
        "against each other, never as a formal test.",
        "",
        header,
        "-" * len(header),
    ]
    for r in table.iter_rows(named=True):
        lines.append(
            f"{r['trend']:<9s} {r['k_mean']:>4s} {r['l_scale']:>4s} "
            f"{r['scale_source']:>7s} {r['fit']:>4s} {r['n']:>5d} "
            f"{r['crps']:>7.3f} {r['mae']:>6.3f} {r['rmse']:>6.3f} {r['bias']:>+7.3f} "
            f"{r['cover50']:>6.3f} {r['cover80']:>6.3f} {r['cover95']:>6.3f} {r['pit_p']:>7.4f}"
        )

    text = "\n".join(lines)
    (OUT_DIR / "spec_comparison.txt").write_text(text, encoding="utf-8")
    print()
    print(text)


if __name__ == "__main__":
    main()
