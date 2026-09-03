"""Figure: axial schematic of the cervical spinal canal, normal versus degeneratively narrowed.

Writes fig.svg (inline in the HTML) and fig.tex (TikZ, \\input in the PDF).
Run from anywhere: python3 make_fig.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from figlib import Canvas, Style  # noqa: E402

W, H = 740, 280


def panel(c: Canvas, x0: float, degenerate: bool) -> None:
    cx = x0 + 120
    title = "Degenerative narrowing" if degenerate else "Normal canal"
    c.text(cx, 20, title, size=14, anchor="middle", weight="bold")
    c.text(cx, 38, "front", size=10.5, anchor="middle", color="muted")
    c.text(cx, 266, "back", size=10.5, anchor="middle", color="muted")

    bone = Style(fill="ink", fill_opacity=0.12, stroke="ink2", stroke_width=1, rx=12)
    # vertebral body (anterior)
    c.rect(cx - 75, 48, 150, 52, bone)
    c.text(cx, 79, "Vertebral body", size=12, anchor="middle", color="ink2")
    # facet joints (lateral)
    c.rect(cx - 118, 140, 24, 36, Style(fill="ink", fill_opacity=0.12, stroke="ink2", stroke_width=1, rx=5))
    c.rect(cx + 94, 140, 24, 36, Style(fill="ink", fill_opacity=0.12, stroke="ink2", stroke_width=1, rx=5))
    # posterior arch (lamina) as a thick smooth stroke
    arch = [(cx - 70, 104), (cx - 88, 150), (cx - 72, 215), (cx, 240), (cx + 72, 215), (cx + 88, 150), (cx + 70, 104)]
    c.polygon(arch, Style(fill="none", stroke="ink", stroke_width=11, opacity=0.5), closed=False, smooth=True)
    # ligamentum flavum lining the arch
    lig = [(cx - 60, 120), (cx - 74, 155), (cx - 60, 205), (cx, 224), (cx + 60, 205), (cx + 74, 155), (cx + 60, 120)]
    c.polygon(lig, Style(fill="none", stroke="coral", stroke_width=(10 if degenerate else 3), opacity=(0.85 if degenerate else 0.7)),
              closed=False, smooth=True)
    if degenerate:
        # disc bulge and osteophyte protruding from the posterior margin of the body
        bump = [(cx - 58, 100), (cx - 34, 124), (cx, 133), (cx + 34, 124), (cx + 58, 100)]
        c.polygon(bump, Style(fill="coral", fill_opacity=0.85, stroke="none"), closed=True, smooth=True)
        c.ellipse(cx, 170, 52, 30, Style(fill="accent", fill_opacity=0.15, stroke="none"))  # residual CSF
        c.ellipse(cx, 172, 42, 15, Style(fill="mark", stroke="none"))                        # flattened cord
        c.ellipse(cx + 6, 172, 8, 5, Style(fill="surface", stroke="ink2", stroke_width=0.8))  # T2 signal change
    else:
        c.ellipse(cx, 165, 56, 46, Style(fill="accent", fill_opacity=0.15, stroke="none"))  # CSF
        c.ellipse(cx, 165, 36, 28, Style(fill="mark", stroke="none"))                        # cord

    def label(lines: str | list[str], ly: float, sx: float, sy: float) -> None:
        c.line(sx, sy, cx + 122, ly - 3, color="ink2", width=0.8, opacity=0.8)
        c.text(cx + 126, ly, lines, size=11, anchor="start", color="ink2")

    if degenerate:
        label(["Disc bulge and", "osteophyte"], 114, cx + 40, 118)
        label("Flattened cord", 160, cx + 36, 168)
        label("T2 signal change", 188, cx + 14, 174)
        label(["Thickened", "ligamentum flavum"], 214, cx + 66, 206)
        label("Lamina", 250, cx + 42, 233)
    else:
        label("Spinal cord", 150, cx + 30, 158)
        label("Cerebrospinal fluid", 182, cx + 52, 178)
        label("Ligamentum flavum", 214, cx + 62, 204)
        label("Lamina (bone)", 250, cx + 42, 233)
    c.text(cx - 118, 192, "Facet joint", size=10.5, anchor="start", color="ink2")


def main() -> None:
    c = Canvas(W, H, aria_label=(
        "Two axial schematics of the cervical spine. Left, a normal canal: the spinal cord floats in "
        "cerebrospinal fluid between the vertebral body in front and the lamina and thin ligamentum flavum behind. "
        "Right, degenerative narrowing: a disc bulge with osteophyte protrudes from the front and a thickened "
        "ligamentum flavum from behind, flattening the cord, which shows a T2 signal change."))
    panel(c, 0, degenerate=False)
    panel(c, 375, degenerate=True)
    c.write(HERE)
    print(f"wrote {HERE / 'fig.svg'} and {HERE / 'fig.tex'}")


if __name__ == "__main__":
    main()
