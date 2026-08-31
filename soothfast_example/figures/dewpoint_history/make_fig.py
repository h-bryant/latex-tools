"""Figure 1: two years of the monthly average 7:00 AM dew point at Bryan, TX.

Reproduce with:
    python figures/dewpoint_history/make_fig.py

Input : analysis/monthly_dewpoint/output/history_window.csv is not used; the
        window is taken from analysis/dewpoint_forecast/output/history_window.csv
        so that figure and text always describe the same 24 months.
        analysis/monthly_dewpoint/output/climatology.csv supplies the reference.
Output: figures/dewpoint_history/dewpoint_history.pdf

The shaded band is the 10th to 90th percentile of the daily 7:00 AM readings
within each month, not an uncertainty interval about the mean. It is included
because it shows directly why the forecast fan in Figure 2 is so much wider in
winter than in summer.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from typing import Final

import plotly.graph_objects as go
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _style import (  # noqa: E402
    AXIS,
    INK_MUTED,
    LINE_WIDTH,
    MARKER_SIZE,
    SERIES_BLUE,
    SERIES_ORANGE,
    SURFACE,
    annotate,
    base_layout,
    contiguous_runs,
)

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
HERE: Final[Path] = Path(__file__).resolve().parent
STATION: Final[str] = "CFD"


def main() -> None:
    history = pl.read_csv(
        ROOT / "analysis" / "dewpoint_forecast" / "output" / "history_window.csv",
        try_parse_dates=True,
    ).sort("month_start")
    climatology = pl.read_csv(
        ROOT / "analysis" / "monthly_dewpoint" / "output" / "climatology.csv"
    ).filter(pl.col("station") == STATION)

    dates = history["month_start"].to_list()
    means = history["mean_dwpf"].to_list()
    p10 = history["p10_dwpf"].to_list()
    p90 = history["p90_dwpf"].to_list()

    clim_by_month = dict(
        zip(climatology["month"].to_list(), climatology["clim_mean_dwpf"].to_list())
    )
    clim_line = [clim_by_month[d.month] for d in dates]

    fig = go.Figure(layout=base_layout(height_px=252))

    # Within-month spread, drawn first so the lines sit on top of it. One
    # closed shape per run of consecutive months, so the gap in the record
    # stays a gap.
    p90_by_date = dict(zip(dates, p90))
    first_band = True
    for run_dates, run_p10 in contiguous_runs(dates, p10):
        run_p90 = [p90_by_date[d] for d in run_dates]
        fig.add_trace(
            go.Scatter(
                x=run_dates + run_dates[::-1],
                y=run_p90 + run_p10[::-1],
                fill="toself",
                fillcolor="rgba(42,120,214,0.10)",
                line=dict(width=0),
                mode="lines",
                name="Daily readings, 10th–90th percentile",
                legendgroup="spread",
                legendrank=3,
                showlegend=first_band,
            )
        )
        first_band = False

    # Station climatology. Dashed, so the two series separate in grayscale and
    # under color-vision deficiency as well as by hue.
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=clim_line,
            mode="lines",
            line=dict(color=SERIES_ORANGE, width=LINE_WIDTH, dash="dash"),
            name=f"Average for the month, {int(climatology['first_year'].min())}–"
            f"{int(climatology['last_year'].max())}",
            legendgroup="clim",
            legendrank=2,
        )
    )

    # Observed monthly means, broken where the record is missing.
    first_series = True
    for run_dates, run_means in contiguous_runs(dates, means):
        fig.add_trace(
            go.Scatter(
                x=run_dates,
                y=run_means,
                mode="lines+markers",
                line=dict(color=SERIES_BLUE, width=LINE_WIDTH),
                marker=dict(
                    size=MARKER_SIZE,
                    color=SERIES_BLUE,
                    line=dict(color=SURFACE, width=2),  # surface ring
                ),
                name="Monthly average, 7:00 a.m.",
                legendgroup="obs",
                legendrank=1,
                showlegend=first_series,
            )
        )
        first_series = False

    # Months absent from the record, marked rather than passed over in silence.
    # Plotly wants an ISO string, not a date object, for shapes on a date axis.
    present = {d for d in dates}
    expected = [
        dt.date(y, m, 1)
        for y in range(dates[0].year, dates[-1].year + 1)
        for m in range(1, 13)
        if dates[0] <= dt.date(y, m, 1) <= dates[-1]
    ]
    for d in [d for d in expected if d not in present]:
        fig.add_shape(
            type="line", x0=d.isoformat(), x1=d.isoformat(),
            yref="paper", y0=0.0, y1=0.86,
            line=dict(color=AXIS, width=1, dash="dot"),
        )
        annotate(fig, d.isoformat(), 28.6, "no data", color=INK_MUTED)

    # Selective direct labels: the two extremes of the window.
    hottest = history.sort("mean_dwpf", descending=True).row(0, named=True)
    coldest = history.sort("mean_dwpf").row(0, named=True)
    annotate(
        fig, hottest["month_start"], hottest["mean_dwpf"],
        f"{hottest['mean_dwpf']:.1f}°F", yshift=13,
    )
    annotate(
        fig, coldest["month_start"], coldest["mean_dwpf"],
        f"{coldest['mean_dwpf']:.1f}°F", yshift=-13,
    )

    fig.update_yaxes(range=[26, 82])
    fig.update_xaxes(
        range=[dates[0] - dt.timedelta(days=18), dates[-1] + dt.timedelta(days=18)]
    )
    fig.update_layout(margin=dict(l=44, r=10, t=30, b=34))

    out = HERE / "dewpoint_history.pdf"
    fig.write_image(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
