"""Figure 2: fan chart of the 12-month-ahead forecast, Bryan TX 7:00 AM dew point.

Reproduce with:
    python figures/dewpoint_fan/make_fig.py

Input : analysis/dewpoint_forecast/output/forecast_quantiles.csv
        analysis/dewpoint_forecast/output/history_window.csv
Output: figures/dewpoint_fan/dewpoint_fan.pdf

The fan is anchored at the last observed month, whose value is known, so every
band starts from a point and widens. Bands are the central 50, 80, and 95
percent of the simulated predictive distribution, drawn as one blue hue stepped
light to dark so that the darker the shading, the more probable the region.
The y-axis matches Figure 1 so that the two can be read against each other.
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
    FAN_50,
    FAN_80,
    FAN_95,
    FAN_DARK,
    INK_MUTED,
    INK_SECONDARY,
    LINE_WIDTH,
    MARKER_SIZE,
    SURFACE,
    annotate,
    base_layout,
    contiguous_runs,
)

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
HERE: Final[Path] = Path(__file__).resolve().parent

# (lower quantile column, upper quantile column, fill color, legend label)
# (lower quantile, upper quantile, fill, legend label, legend position).
# Drawn widest first so the darker, narrower bands land on top; listed in the
# legend narrowest first, which is the order the shading reads in.
BANDS: Final[tuple[tuple[str, str, str, str, int], ...]] = (
    ("q025", "q975", FAN_95, "95%", 4),
    ("q100", "q900", FAN_80, "80%", 3),
    ("q250", "q750", FAN_50, "50% interval", 2),
)


def main() -> None:
    out_dir = ROOT / "analysis" / "dewpoint_forecast" / "output"
    history = pl.read_csv(out_dir / "history_window.csv", try_parse_dates=True).sort(
        "month_start"
    )
    forecast = pl.read_csv(out_dir / "forecast_quantiles.csv", try_parse_dates=True).sort(
        "month_start"
    )

    hist_dates = history["month_start"].to_list()
    hist_values = history["mean_dwpf"].to_list()
    anchor_date, anchor_value = hist_dates[-1], hist_values[-1]

    fan_dates = [anchor_date] + forecast["month_start"].to_list()

    fig = go.Figure(layout=base_layout(height_px=264))

    # Bands, widest first so the narrower and darker ones are drawn on top.
    for lo_col, hi_col, color, label, rank in BANDS:
        lo = [anchor_value] + forecast[lo_col].to_list()
        hi = [anchor_value] + forecast[hi_col].to_list()
        fig.add_trace(
            go.Scatter(
                x=fan_dates + fan_dates[::-1],
                y=hi + lo[::-1],
                fill="toself",
                fillcolor=color,
                line=dict(width=0),
                mode="lines",
                name=label,
                legendrank=rank,
            )
        )

    # Median, drawn in the surface color: it has to read against the darkest
    # band, and a dark line there would disappear.
    fig.add_trace(
        go.Scatter(
            x=fan_dates,
            y=[anchor_value] + forecast["q500"].to_list(),
            mode="lines",
            line=dict(color=SURFACE, width=LINE_WIDTH),
            showlegend=False,
        )
    )

    # Observed history, broken where the record is missing.
    first = True
    for run_dates, run_values in contiguous_runs(hist_dates, hist_values):
        fig.add_trace(
            go.Scatter(
                x=run_dates,
                y=run_values,
                mode="lines+markers",
                line=dict(color=FAN_DARK, width=LINE_WIDTH),
                marker=dict(
                    size=MARKER_SIZE,
                    color=FAN_DARK,
                    line=dict(color=SURFACE, width=2),
                ),
                name="Observed monthly average",
                legendgroup="obs",
                legendrank=1,
                showlegend=first,
            )
        )
        first = False

    # Divider between what is observed and what is simulated.
    fig.add_shape(
        type="line",
        x0=anchor_date.isoformat(), x1=anchor_date.isoformat(),
        yref="paper", y0=0.0, y1=0.90,
        line=dict(color=AXIS, width=1, dash="dot"),
    )
    annotate(fig, anchor_date.isoformat(), 80.4, "forecast →", xshift=4, anchor="left")
    annotate(fig, anchor_date.isoformat(), 80.4, "observed ", xshift=-4, anchor="right")

    # The median is direct-labelled rather than legended, because a white key on
    # a white legend background would be invisible. January is where the 50 per
    # cent band is widest, so the label fits inside it.
    widest = forecast.with_columns((pl.col("q750") - pl.col("q250")).alias("w")).sort(
        "w", descending=True
    ).row(0, named=True)
    annotate(
        fig, widest["month_start"], widest["q500"], "median",
        yshift=-11, color=SURFACE,
    )

    fig.update_yaxes(range=[26, 82])
    fig.update_xaxes(
        range=[
            hist_dates[0] - dt.timedelta(days=18),
            fan_dates[-1] + dt.timedelta(days=18),
        ]
    )
    fig.update_layout(margin=dict(l=44, r=10, t=30, b=34))

    out = HERE / "dewpoint_fan.pdf"
    fig.write_image(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
