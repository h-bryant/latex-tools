"""Figure: the route to diagnosis, as mean months from symptom onset (Hilton et al., 2019, BMJ Open 9:e027000).

Writes fig.svg and fig.tex. Run from anywhere: python3 make_fig.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import Canvas, Style  # noqa: E402

W, H = 740, 232
X0, X1, MONTHS = 60.0, 700.0, 24.0
AXIS_Y = 125.0

# (months, label, high placement)  -- means for 43 patients, Hilton et al. 2019
EVENTS: list[tuple[float, str, bool]] = [
    (0.0, "Symptom onset", False),
    (6.4, "Referred by primary care", False),
    (12.5, "Cervical MRI", True),
    (15.8, "Neurosurgical review", False),
    (22.1, "Surgery", False),
]
MJOA_POINTS: list[tuple[float, str]] = [(6.4, "mJOA 16.0"), (15.8, "mJOA 14.8")]


def x_of(m: float) -> float:
    return X0 + (X1 - X0) * m / MONTHS


def main() -> None:
    c = Canvas(W, H, aria_label=(
        "Timeline over 24 months. Mean intervals from symptom onset: referral by primary care at 6.4 months, "
        "cervical MRI at 12.5 months, neurosurgical review at 15.8 months, surgery at 22.1 months. Below, function "
        "measured by the mJOA fell from 16.0 at the primary care assessment to 14.8 at the surgical assessment; "
        "59 percent of patients deteriorated during the pathway."))
    # axis with 6-month ticks
    c.line(X0 - 10, AXIS_Y, X1 + 20, AXIS_Y, color="ink2", width=1.2, arrow=True)
    for m in range(0, 25, 6):
        x = x_of(m)
        c.line(x, AXIS_Y - 4, x, AXIS_Y + 4, color="ink2", width=1)
        c.text(x, AXIS_Y + 22, f"{m}" + (" months" if m == 24 else ""), size=10.5, anchor="middle", color="muted", family="mono")
    # events
    for m, label, high in EVENTS:
        x = x_of(m)
        base = 50.0 if high else 88.0
        c.text(x, base, label, size=11.5, anchor="middle", weight="bold")
        c.text(x, base + 14, f"{m:g} months" if m else "0 months", size=10.5, anchor="middle", color="muted", family="mono")
        c.line(x, base + 20, x, AXIS_Y - 9, color="ink2", width=0.8, opacity=0.7)
        c.circle(x, AXIS_Y, 6.5, Style(fill="mark", stroke="surface", stroke_width=1.5))
    # function track
    c.text(X0, 198, "Disability while waiting", size=11, anchor="start", color="muted")
    (xa, la), (xb, lb) = [(x_of(m), t) for m, t in MJOA_POINTS]
    c.line(xa, 195, xb, 195, color="coral", width=2)
    for x, t in ((xa, la), (xb, lb)):
        c.circle(x, 195, 5, Style(fill="coral", stroke="surface", stroke_width=1.5))
        c.text(x, 184, t, size=11, anchor="middle", color="ink", family="mono")
    c.text((xa + xb) / 2, 216, "59% of patients deteriorated during the pathway", size=11, anchor="middle", color="ink2")
    c.write(HERE)
    print(f"wrote {HERE / 'fig.svg'} and {HERE / 'fig.tex'}")


if __name__ == "__main__":
    main()
