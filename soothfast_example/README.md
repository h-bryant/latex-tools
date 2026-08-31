# Worked example: `dew_point`

A report drafted under the rules in [`../soothfast-writing.md`](../soothfast-writing.md).
It documents two years of the monthly average 7:00 a.m. dew point at Bryan,
Texas, and forecasts that quantity twelve months ahead.

Two PDFs are built from the same source:

| File | What it is |
| --- | --- |
| `dew_point.pdf` | The clean report, provenance notes disabled. |
| `dew_point-annotated.pdf` | The review copy, every provenance note visible in the margin, plus an index of them. |

## Building

```sh
latexmk -lualatex -jobname=dew_point-annotated dew_point.tex
latexmk -lualatex -usepretex='\PassOptionsToPackage{disable}{todonotes}' dew_point.tex
```

LuaLaTeX and Biber, per the guide. `modern.sty` is copied into this directory
rather than referenced, so the project builds standalone.

## Reproducing the analysis

```sh
python -m venv .venv && .venv/bin/pip install numpy scipy polars plotly kaleido statsmodels
.venv/bin/python data/fetch_asos.py
.venv/bin/python analysis/monthly_dewpoint/run.py
.venv/bin/python analysis/dewpoint_forecast/select_spec.py
.venv/bin/python analysis/dewpoint_forecast/run.py
.venv/bin/python figures/dewpoint_history/make_fig.py
.venv/bin/python figures/dewpoint_fan/make_fig.py
```

Only the first step touches the network. Everything after it is deterministic
given that download and the simulation seed in `analysis/dewpoint_forecast/run.py`.
Re-running the download after 31 August 2026 retrieves a longer record and
changes every number in the report.

## Layout

| Path | Contents |
| --- | --- |
| `data/fetch_asos.py` | Downloads routine hourly observations for Coulter Field (KCFD, Bryan) and Easterwood Field (KCLL, College Station) from the Iowa Environmental Mesonet into `data/raw/`. |
| `analysis/monthly_dewpoint/` | Builds the daily 7:00 a.m. series and collapses it to monthly means, with coverage and cross-station diagnostics in `output/summary.txt`. |
| `analysis/dewpoint_forecast/model.py` | The model: harmonic seasonal mean, multiplicative seasonal variance, AR(1) anomaly, simulated predictive distribution. Shared by the two scripts below so they cannot diverge. |
| `analysis/dewpoint_forecast/select_spec.py` | Pseudo-out-of-sample comparison of fourteen specifications; writes `output/spec_comparison.txt`. |
| `analysis/dewpoint_forecast/run.py` | Final estimation, forecast, and backtest; writes `output/model_summary.txt`, which is the source for every number quoted in the report. |
| `figures/_style.py` | Shared figure tokens: palette, mark specifications, geometry. |
| `figures/dewpoint_history/` | Figure 1, the two-year history. |
| `figures/dewpoint_fan/` | Figure 2, the fan chart. |

Each `CALC:` and `FIG:` note in the manuscript names the directory and the exact
command that reproduces the value it documents.

## Figure conventions

Figures are 6.0 inches wide, matching the text block that `modern.sty` produces
on letterpaper, so `\includegraphics[width=\textwidth]` reproduces them at 1:1
and the type inside them renders at the size `figures/_style.py` specifies. Both
figures share a y-axis range so they can be read against each other. Colors are
validated for color-vision deficiency and for contrast against a white page: a
blue and orange pair for the two-series history figure, and a single blue hue
stepped light to dark for the fan bands, so that darker shading always means a
more probable region.

Body type in the figures is Palatino, which stands in for the TeX Gyre Pagella
of the document text; Pagella ships with TeX Live but is not registered with the
operating system font service that the figure renderer consults.
