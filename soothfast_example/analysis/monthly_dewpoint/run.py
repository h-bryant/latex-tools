"""Build the monthly series of average 7:00 AM dew point from raw hourly data.

Reproduce with:
    python analysis/monthly_dewpoint/run.py

Input : data/raw/cfd_hourly.csv, data/raw/cll_hourly.csv
        (written by data/fetch_asos.py)
Output: analysis/monthly_dewpoint/output/monthly_dewpoint_0700.csv
        analysis/monthly_dewpoint/output/daily_dewpoint_0700.csv
        analysis/monthly_dewpoint/output/summary.txt

Definitions
-----------
"The 7:00 AM observation" is the routine hourly observation whose local
(America/Chicago) valid time falls within 15 minutes of 07:00. At Coulter Field
routine observations are issued at 55 minutes past the hour, so in practice this
is the 06:55 report; at Easterwood Field it is the 06:53 report. Local clock
time is used, so the observation shifts by one hour in solar terms across the
daylight saving transitions.

A calendar month enters the monthly series only if at least 20 days in it carry
a valid 7:00 AM dew point reading.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import polars as pl

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
OUT_DIR: Final[Path] = Path(__file__).resolve().parent / "output"

# Window half-width, in minutes, around 07:00 local time.
WINDOW_MINUTES: Final[int] = 15

# Minimum number of valid daily readings for a month to be reported.
MIN_DAYS_PER_MONTH: Final[int] = 20

# Physically implausible dew points for this location are dropped as sensor
# faults. The all-time record low dew point anywhere in Texas is far above
# -40 F, and dew point cannot exceed air temperature.
DWPF_FLOOR: Final[float] = -20.0
DWPF_CEIL: Final[float] = 90.0


def load_seven_am(station: str) -> pl.DataFrame:
    """Return one row per date: the routine observation nearest 07:00 local."""
    raw = pl.read_csv(
        ROOT / "data" / "raw" / f"{station}_hourly.csv",
        null_values=["M", "T"],
        schema_overrides={"tmpf": pl.Float64, "dwpf": pl.Float64, "relh": pl.Float64},
    )
    # dt.hour() and dt.minute() are Int8; cast before multiplying so that
    # hour * 60 does not overflow.
    obs = raw.with_columns(
        pl.col("valid").str.to_datetime("%Y-%m-%d %H:%M").alias("ts")
    ).with_columns(
        (
            pl.col("ts").dt.hour().cast(pl.Int32) * 60
            + pl.col("ts").dt.minute().cast(pl.Int32)
            - 7 * 60
        )
        .abs()
        .alias("mins_from_0700"),
        pl.col("ts").dt.date().alias("date"),
    )

    near_seven = obs.filter(pl.col("mins_from_0700") <= WINDOW_MINUTES)

    # Dew point cannot exceed the air temperature; where it does by more than the
    # 0.1 F reporting resolution, the pair is treated as a sensor fault.
    clean = near_seven.filter(
        pl.col("dwpf").is_not_null()
        & pl.col("dwpf").is_between(DWPF_FLOOR, DWPF_CEIL)
        & (pl.col("dwpf") <= pl.col("tmpf").fill_null(pl.col("dwpf")) + 0.1)
    )

    # One observation per date: the one closest to 07:00.
    return (
        clean.sort(["date", "mins_from_0700"])
        .group_by("date", maintain_order=True)
        .first()
        .select(
            pl.lit(station.upper()).alias("station"),
            "date",
            "ts",
            "tmpf",
            "dwpf",
        )
        .sort("date")
    )


def monthly(daily: pl.DataFrame) -> pl.DataFrame:
    """Collapse the daily 7:00 AM series to monthly means and within-month spread."""
    return (
        daily.with_columns(
            pl.col("date").dt.year().alias("year"),
            pl.col("date").dt.month().alias("month"),
            pl.col("date").dt.truncate("1mo").alias("month_start"),
        )
        .group_by(["station", "year", "month", "month_start"], maintain_order=True)
        .agg(
            pl.len().alias("n_days"),
            pl.col("dwpf").mean().round(3).alias("mean_dwpf"),
            pl.col("dwpf").std().round(3).alias("sd_dwpf"),
            pl.col("dwpf").quantile(0.10, "linear").round(2).alias("p10_dwpf"),
            pl.col("dwpf").quantile(0.25, "linear").round(2).alias("p25_dwpf"),
            pl.col("dwpf").median().round(2).alias("p50_dwpf"),
            pl.col("dwpf").quantile(0.75, "linear").round(2).alias("p75_dwpf"),
            pl.col("dwpf").quantile(0.90, "linear").round(2).alias("p90_dwpf"),
            pl.col("dwpf").min().alias("min_dwpf"),
            pl.col("dwpf").max().alias("max_dwpf"),
        )
        .filter(pl.col("n_days") >= MIN_DAYS_PER_MONTH)
        .sort(["station", "month_start"])
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    daily = pl.concat([load_seven_am(s) for s in ("cfd", "cll")])
    monthly_df = monthly(daily)

    daily.write_csv(OUT_DIR / "daily_dewpoint_0700.csv")
    monthly_df.write_csv(OUT_DIR / "monthly_dewpoint_0700.csv")

    # Raw station climatology: the mean of each calendar month over the whole
    # record. Used as the reference line in the history figure. This is a plain
    # average over whatever years are available, not a WMO 30-year normal.
    (
        monthly_df.group_by(["station", pl.col("month_start").dt.month().alias("month")])
        .agg(
            pl.len().alias("n_years"),
            pl.col("mean_dwpf").mean().round(3).alias("clim_mean_dwpf"),
            pl.col("mean_dwpf").std().round(3).alias("clim_sd_dwpf"),
            pl.col("month_start").min().dt.year().alias("first_year"),
            pl.col("month_start").max().dt.year().alias("last_year"),
        )
        .sort(["station", "month"])
        .write_csv(OUT_DIR / "climatology.csv")
    )

    lines: list[str] = []
    for station in ("CFD", "CLL"):
        d = daily.filter(pl.col("station") == station)
        m = monthly_df.filter(pl.col("station") == station)
        span_days = (d["date"].max() - d["date"].min()).days + 1
        lines += [
            f"[{station}]",
            f"  daily 7:00 AM observations : {d.height:,}",
            f"  calendar span              : {d['date'].min()} to {d['date'].max()} ({span_days:,} days)",
            f"  daily coverage             : {d.height / span_days:.3%}",
            f"  months passing >= {MIN_DAYS_PER_MONTH} days : {m.height}",
            f"  monthly span               : {m['month_start'].min()} to {m['month_start'].max()}",
            f"  mean dew point (F)         : {d['dwpf'].mean():.2f}",
            "",
        ]

    # Reporting resolution. METAR encodes temperature in whole degrees Celsius,
    # so a record whose Fahrenheit values are overwhelmingly whole numbers has
    # been through a different encoding path from one whose values are not.
    lines.append("[reporting resolution of the raw dew point field]")
    for station in ("cfd", "cll"):
        raw = pl.read_csv(
            ROOT / "data" / "raw" / f"{station}_hourly.csv",
            null_values=["M", "T"],
            schema_overrides={"tmpf": pl.Float64, "dwpf": pl.Float64, "relh": pl.Float64},
        )["dwpf"].drop_nulls()
        whole = ((raw * 10) % 10 == 0).mean()
        lines += [
            f"  {station.upper()}: {raw.len():,} readings, "
            f"{whole:.2%} reported as whole degrees F, "
            f"{raw.n_unique()} distinct values",
        ]
    lines.append("")

    # Agreement between the two stations over their common months.
    wide = (
        monthly_df.pivot(on="station", index="month_start", values="mean_dwpf")
        .drop_nulls()
        .sort("month_start")
    )
    diff = (wide["CFD"] - wide["CLL"]).to_list()
    corr = wide.select(pl.corr("CFD", "CLL")).item()
    lines += [
        "[cross-station check, common months]",
        f"  months compared            : {wide.height}",
        f"  correlation of monthly means: {corr:.4f}",
        f"  mean difference CFD - CLL  : {sum(diff) / len(diff):+.3f} F",
        f"  max absolute difference    : {max(abs(x) for x in diff):.3f} F",
        "",
    ]

    text = "\n".join(lines)
    (OUT_DIR / "summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
