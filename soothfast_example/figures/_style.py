"""Shared figure style, so both figures read as one system.

Colors follow the data-visualization palette documented in the project README:
a single blue hue stepped light to dark for the sequential fan bands, and the
validated blue/orange pair for the two-series history figure. Chrome (grid,
axes, tick labels) is recessive; text never wears a data color.

Figures are 6.0 inches wide, matching the text block of an 11pt letterpaper
article with the 1.25 inch side margins set by modern.sty, so that
\\includegraphics[width=\\textwidth]{...} reproduces them at 1:1 and the type
inside them renders at the size specified here.
"""

from __future__ import annotations

from typing import Final

import plotly.graph_objects as go

# --- surface and ink ------------------------------------------------------
SURFACE: Final[str] = "#ffffff"       # the page
INK_PRIMARY: Final[str] = "#0b0b0b"
INK_SECONDARY: Final[str] = "#52514e"
INK_MUTED: Final[str] = "#898781"     # axis and tick labels
GRID: Final[str] = "#e1e0d9"          # hairline, solid, one step off surface
AXIS: Final[str] = "#c3c2b7"

# --- series colors --------------------------------------------------------
# Validated as a categorical pair against a white surface: worst-pair CVD
# Delta E 24.7, normal-vision 33.6, both above the required floors.
SERIES_BLUE: Final[str] = "#2a78d6"
SERIES_ORANGE: Final[str] = "#eb6834"

# Single-hue sequential ramp for the fan, light to dark (blue steps 250, 400,
# 550). Validated as an ordinal ramp against a white surface: lightness
# monotone, adjacent lightness gaps above 0.06, light end 2.11:1 against the
# surface, hue spread 3 degrees.
FAN_95: Final[str] = "#86b6ef"
FAN_80: Final[str] = "#3987e5"
FAN_50: Final[str] = "#1c5cab"
FAN_DARK: Final[str] = "#0d366b"      # observed history line in the fan figure

# --- type -----------------------------------------------------------------
# TeX Gyre Pagella is the body face set by modern.sty. It is not registered
# with the operating system font service on macOS, so Palatino, which is
# metrically compatible, stands in when the figure is rendered.
FONT_STACK: Final[str] = "TeX Gyre Pagella, Palatino, Palatino Linotype, serif"
FONT_SIZE: Final[int] = 9

FIG_WIDTH_PX: Final[int] = 432        # 6.0 in at 72 pt per inch
LINE_WIDTH: Final[int] = 2
MARKER_SIZE: Final[int] = 6


def base_layout(height_px: int, y_title: str = "Dew point (°F)") -> go.Layout:
    """Layout shared by every figure in this project."""
    return go.Layout(
        width=FIG_WIDTH_PX,
        height=height_px,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT_STACK, size=FONT_SIZE, color=INK_SECONDARY),
        margin=dict(l=44, r=10, t=8, b=34),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor=AXIS,
            linewidth=1,
            ticks="outside",
            ticklen=3,
            tickcolor=AXIS,
            tickfont=dict(color=INK_MUTED),
            dtick="M3",
            tickformat="%b<br>%Y",
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color=INK_SECONDARY, size=FONT_SIZE)),
            showgrid=True,
            gridcolor=GRID,
            gridwidth=1,
            zeroline=False,
            showline=False,
            ticks="outside",
            ticklen=3,
            tickcolor=AXIS,
            tickfont=dict(color=INK_MUTED),
            dtick=10,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="left",
            x=0.0,
            font=dict(color=INK_SECONDARY, size=FONT_SIZE),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            itemwidth=30,
            tracegroupgap=0,
        ),
        showlegend=True,
        hovermode=False,
    )


def contiguous_runs(dates: list, values: list) -> list[tuple[list, list]]:
    """Split a series into runs of consecutive non-missing months.

    Drawing each run as its own trace leaves a visible break at a gap in the
    record, rather than a line that implies data where there is none.
    """
    runs: list[tuple[list, list]] = []
    current_dates: list = []
    current_values: list = []
    previous = None
    for d, v in zip(dates, values):
        gap = previous is not None and (
            (d.year - previous.year) * 12 + (d.month - previous.month) != 1
        )
        if v is None or gap:
            if current_dates:
                runs.append((current_dates, current_values))
            current_dates, current_values = [], []
        if v is not None:
            current_dates.append(d)
            current_values.append(v)
        previous = d
    if current_dates:
        runs.append((current_dates, current_values))
    return runs


def annotate(fig: go.Figure, x, y, text: str, *, yshift: int = 0, xshift: int = 0,
             color: str = INK_SECONDARY, anchor: str = "center") -> None:
    """A direct label. Text wears an ink token, never a data color."""
    fig.add_annotation(
        x=x, y=y, text=text, showarrow=False,
        font=dict(family=FONT_STACK, size=FONT_SIZE - 1, color=color),
        yshift=yshift, xshift=xshift, xanchor=anchor,
    )
