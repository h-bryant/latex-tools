"""Figure: how common cord compression and DCM are, from imaging studies to hospital records.

Reads data.csv (one row per estimate with a 95% CI); writes fig.svg and fig.tex.
Run from anywhere: python3 make_fig.py
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import Canvas, Style  # noqa: E402

W, H = 740, 300
X0, X1 = 320.0, 700.0          # bar area in canvas units
XMAX = 60.0                    # percent at the right edge
ROW0, ROWH, BARH = 44.0, 46.0, 16.0


@dataclass(frozen=True)
class Row:
    label: str
    est: float
    lo: float
    hi: float
    hue: str


def read_rows(path: Path) -> list[Row]:
    with path.open(encoding="utf-8", newline="") as f:
        return [Row(r["label"], float(r["estimate_pct"]), float(r["ci_low_pct"]), float(r["ci_high_pct"]), r["hue"])
                for r in csv.DictReader(f)]


def x_of(pct: float) -> float:
    return X0 + (X1 - X0) * pct / XMAX


def split_label(label: str) -> list[str]:
    head, _, tail = label.partition(": ")
    return [head + ":", tail] if tail else [label]


def main() -> None:
    rows = read_rows(HERE / "data.csv")
    c = Canvas(W, H, aria_label=(
        "Horizontal bar chart. Cord compression on MRI is present in about 35 percent of healthy adults aged 60 and "
        "over, 24 percent of all healthy adults, and 7 percent of those under 60. About 2.3 percent of healthy "
        "volunteers meet clinical criteria for degenerative cervical myelopathy, while UK hospital records capture "
        "only 0.19 percent of adults. Whiskers show 95 percent confidence intervals."))
    # gridlines and axis
    for pct in range(0, int(XMAX) + 1, 10):
        x = x_of(pct)
        c.line(x, ROW0 - 18, x, ROW0 + ROWH * len(rows) - 12, color="ink", width=0.6, opacity=0.12)
        c.text(x, ROW0 + ROWH * len(rows) + 6, f"{pct}", size=10.5, anchor="middle", color="muted", family="mono")
    c.line(X0, ROW0 - 18, X0, ROW0 + ROWH * len(rows) - 12, color="ink2", width=1)
    c.text((X0 + X1) / 2, H - 6, "Percent of population", size=11, anchor="middle", color="muted")

    for i, r in enumerate(rows):
        yc = ROW0 + ROWH * i + ROWH / 2 - 6
        lines = split_label(r.label)
        if len(lines) == 2:
            c.text(X0 - 14, yc - 3, lines[0], size=11.5, anchor="end", color="ink2")
            c.text(X0 - 14, yc + 11, lines[1], size=11.5, anchor="end", color="ink")
        else:
            c.text(X0 - 14, yc + 4, lines[0], size=11.5, anchor="end", color="ink")
        # bar
        c.rect(X0, yc - BARH / 2, max(x_of(r.est) - X0, 1.5), BARH, Style(fill=r.hue, stroke="none", rx=3))
        # 95% CI whisker
        c.line(x_of(r.lo), yc, x_of(r.hi), yc, color="ink2", width=1.2)
        c.line(x_of(r.lo), yc - 5, x_of(r.lo), yc + 5, color="ink2", width=1.2)
        c.line(x_of(r.hi), yc - 5, x_of(r.hi), yc + 5, color="ink2", width=1.2)
        # value label to the right of the whisker
        val = f"{r.est:g}%"
        c.text(x_of(r.hi) + 8, yc + 4, val, size=11, anchor="start", color="ink", family="mono")
    c.write(HERE)
    print(f"wrote {HERE / 'fig.svg'} and {HERE / 'fig.tex'}")


if __name__ == "__main__":
    main()
