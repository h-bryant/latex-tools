"""Figure: management by severity, following the 2017 AO Spine/CSRS guideline (Fehlings et al., 2017).

Writes fig.svg and fig.tex. Run from anywhere: python3 make_fig.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import Canvas, Style  # noqa: E402

W, H = 740, 410
SIZE, LH = 11.5, 1.25

DECISION = Style(fill="accent", fill_opacity=0.12, stroke="accent", stroke_width=1.2, rx=8)
PLAIN = Style(fill="surface", stroke="ink2", stroke_width=1, rx=8)
SURGERY = Style(fill="mark", fill_opacity=0.2, stroke="mark", stroke_width=1.2, rx=8)
WATCH = Style(fill="notebg", stroke="accent", stroke_width=1.2, rx=8)
ALERT = Style(fill="flagbg", stroke="coral", stroke_width=1.2, rx=8)


def box(c: Canvas, x: float, y: float, w: float, h: float, lines: list[str], st: Style,
        bold_first: bool = False, size: float = SIZE) -> None:
    c.rect(x, y, w, h, st)
    total = size * (1 + (len(lines) - 1) * LH)
    first = y + h / 2 - total / 2 + size * 0.82
    if bold_first:
        c.text(x + w / 2, first, lines[0], size=size, anchor="middle", weight="bold")
        if len(lines) > 1:
            c.text(x + w / 2, first + size * LH, lines[1:], size=size, anchor="middle", color="ink2")
    else:
        c.text(x + w / 2, first, lines, size=size, anchor="middle")


def main() -> None:
    c = Canvas(W, H, aria_label=(
        "Flowchart. Cervical cord compression on MRI. If there are signs or symptoms of myelopathy, grade severity "
        "with the mJOA: severe (11 or less) and moderate (12 to 14) get surgery, a strong recommendation; mild "
        "(15 to 17) gets surgery or a supervised trial of structured rehabilitation with close follow-up, a weak "
        "recommendation, with surgery if the patient deteriorates and consideration of surgery if they fail to "
        "improve. If there is no myelopathy, ask about radiculopathy: with it, counsel on the higher risk and offer "
        "surgery or close follow-up; without it, no prophylactic surgery, counsel, teach warning signs, and follow up."))
    box(c, 250, 14, 240, 34, ["Cervical cord compression on MRI"], PLAIN, bold_first=True)
    c.line(370, 48, 370, 76, color="ink2", width=1.2, arrow=True)
    box(c, 235, 78, 270, 36, ["Signs or symptoms of myelopathy?"], DECISION, bold_first=True)

    # Yes branch (left)
    c.polyline([(235, 96), (180, 96), (180, 146)], color="ink2", width=1.2, arrow=True)
    c.text(206, 92, "Yes", size=11, anchor="middle", color="accent", weight="bold")
    box(c, 95, 148, 170, 34, ["Grade severity with the mJOA"], PLAIN)
    cols = [(65, ["Severe", "mJOA 0–11"]), (185, ["Moderate", "mJOA 12–14"]), (315, ["Mild", "mJOA 15–17"])]
    for cx, lines in cols:
        c.polyline([(180, 182), (180, 198), (cx, 198), (cx, 212)], color="ink2", width=1.2, arrow=True)
        box(c, cx - 55, 214, 110, 40, lines, PLAIN, bold_first=True)
        c.line(cx, 254, cx, 278, color="ink2", width=1.2, arrow=True)
    box(c, 10, 280, 230, 48, ["Surgery", "strong recommendation"], SURGERY, bold_first=True)
    box(c, 255, 280, 150, 76, ["Surgery, or a supervised", "trial of structured", "rehabilitation with", "close follow-up (weak)"], WATCH)
    c.line(330, 356, 330, 372, color="coral", width=1.2, arrow=True)
    box(c, 245, 374, 170, 32, ["Deteriorates: operate", "Fails to improve: consider surgery"], ALERT, size=10.5)

    # No branch (right)
    c.polyline([(505, 96), (590, 96), (590, 146)], color="ink2", width=1.2, arrow=True)
    c.text(548, 92, "No", size=11, anchor="middle", color="accent", weight="bold")
    box(c, 470, 148, 240, 44, ["Radiculopathy?", "nerve-root pain, weakness, or numbness"], DECISION, bold_first=True)
    c.polyline([(520, 192), (520, 232)], color="ink2", width=1.2, arrow=True)
    c.text(508, 216, "Yes", size=11, anchor="end", color="accent", weight="bold")
    c.polyline([(660, 192), (660, 232)], color="ink2", width=1.2, arrow=True)
    c.text(672, 216, "No", size=11, anchor="start", color="accent", weight="bold")
    box(c, 445, 234, 150, 92, ["Higher risk: counsel;", "offer surgery, or close", "serial follow-up or", "structured rehabilitation", "(weak)"], WATCH)
    box(c, 600, 234, 135, 92, ["No prophylactic", "surgery; counsel,", "teach warning signs,", "follow up clinically", "(weak)"], WATCH)
    c.write(HERE)
    print(f"wrote {HERE / 'fig.svg'} and {HERE / 'fig.tex'}")


if __name__ == "__main__":
    main()
