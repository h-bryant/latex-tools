"""Tiny drawing library that emits the same figure as inline SVG (for the HTML briefing)
and as TikZ (for the LaTeX briefing) from one description.

Coordinates are given in SVG convention: a 740-unit-wide canvas, y increasing downward.
The TikZ renderer flips y and scales the canvas to the text width.

Palette tokens (see learn-about.md, Section 8):
  mark, accent, coral, ink2, muted      shared data / accent hues
  ink                                    text color: currentColor in SVG, black in TikZ
  surface, marktrack, notebg, flagbg     neutral fills
  none                                   no fill / no stroke
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape as _esc
from pathlib import Path
from typing import Literal

Anchor = Literal["start", "middle", "end"]
Family = Literal["sans", "mono"]

SVG_COLOR = {
    "mark": "var(--mark)", "accent": "var(--accent)", "coral": "var(--coral)",
    "ink2": "var(--ink-2)", "muted": "var(--muted)", "ink": "currentColor",
    "surface": "var(--surface)", "marktrack": "var(--mark-track)",
    "notebg": "var(--note-bg)", "flagbg": "var(--flag-bg)", "none": "none",
}
TIKZ_COLOR = {
    "mark": "mark", "accent": "accent", "coral": "coral", "ink2": "ink2", "muted": "muted",
    "ink": "black", "surface": "white", "marktrack": "mark!22!white",
    "notebg": "accent!8!white", "flagbg": "coral!8!white", "none": "none",
}
TEXT_WIDTH_CM = 15.2  # modern.sty: letter paper, 1.25 in side margins


def tex_escape(s: str) -> str:
    table = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
             "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(table.get(c, c) for c in s)


def _tikz_font(size: float, width_units: int) -> str:
    """Font size in the PDF that matches the SVG size at print width (15.2 cm for 740 units).

    432 pt of text width / 740 units = 0.584 pt per unit; floor at 6 pt for legibility.
    """
    pt = max(6.0, size * (TEXT_WIDTH_CM / 2.54 * 72.27) / width_units)
    return rf"\fontsize{{{pt:.1f}pt}}{{{pt * 1.25:.1f}pt}}\selectfont"


@dataclass(frozen=True)
class Style:
    fill: str = "none"
    stroke: str = "none"
    stroke_width: float = 1.0
    opacity: float = 1.0
    fill_opacity: float = 1.0
    dash: bool = False
    rx: float = 0.0  # corner radius for rects


@dataclass
class Canvas:
    width: int
    height: int
    aria_label: str
    svg: list[str] = field(default_factory=list)
    tikz: list[str] = field(default_factory=list)
    markers: set[str] = field(default_factory=set)

    # ---- helpers -------------------------------------------------------
    def _y(self, y: float) -> float:
        return self.height - y

    def _svg_style(self, st: Style) -> str:
        parts = [f'fill="{SVG_COLOR[st.fill]}"', f'stroke="{SVG_COLOR[st.stroke]}"']
        if st.stroke != "none":
            parts.append(f'stroke-width="{st.stroke_width:g}"')
        if st.opacity != 1.0:
            parts.append(f'opacity="{st.opacity:g}"')
        if st.fill_opacity != 1.0:
            parts.append(f'fill-opacity="{st.fill_opacity:g}"')
        if st.dash:
            parts.append('stroke-dasharray="5 4"')
        return " ".join(parts)

    def _tikz_opts(self, st: Style) -> str:
        opts: list[str] = []
        if st.fill != "none":
            opts.append(f"fill={TIKZ_COLOR[st.fill]}")
            if st.fill_opacity != 1.0:
                opts.append(f"fill opacity={st.fill_opacity:g}")
        if st.stroke != "none":
            opts.append(f"draw={TIKZ_COLOR[st.stroke]}")
            opts.append(f"line width={st.stroke_width * 0.75:.2f}pt")
        if st.opacity != 1.0:
            opts.append(f"opacity={st.opacity:g}")
        if st.dash:
            opts.append("dashed")
        if st.rx:
            opts.append(f"rounded corners={st.rx * self._unit_cm():.2f}cm")
        return ", ".join(opts)

    def _unit_cm(self) -> float:
        return TEXT_WIDTH_CM / self.width

    # ---- primitives ----------------------------------------------------
    def rect(self, x: float, y: float, w: float, h: float, st: Style) -> None:
        rx = f' rx="{st.rx:g}"' if st.rx else ""
        self.svg.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{rx} {self._svg_style(st)}/>')
        self.tikz.append(f"\\path[{self._tikz_opts(st)}] ({x:g},{self._y(y + h):g}) rectangle ({x + w:g},{self._y(y):g});")

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, st: Style) -> None:
        self.svg.append(f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="{rx:g}" ry="{ry:g}" {self._svg_style(st)}/>')
        self.tikz.append(f"\\path[{self._tikz_opts(st)}] ({cx:g},{self._y(cy):g}) ellipse ({rx:g} and {ry:g});")

    def circle(self, cx: float, cy: float, r: float, st: Style) -> None:
        self.ellipse(cx, cy, r, r, st)

    def polygon(self, pts: list[tuple[float, float]], st: Style, closed: bool = True, smooth: bool = False) -> None:
        d = "M " + " L ".join(f"{x:g} {y:g}" for x, y in pts) + (" Z" if closed else "")
        if smooth:
            # Catmull-Rom-ish smoothing is overkill; use SVG quadratic smoothing through midpoints.
            d = _smooth_path(pts, closed)
        self.svg.append(f'<path d="{d}" {self._svg_style(st)}/>')
        coords = " -- ".join(f"({x:g},{self._y(y):g})" for x, y in pts)
        if smooth:
            coords = "plot[smooth" + (" cycle" if closed else "") + ", tension=0.6] coordinates {" + " ".join(f"({x:g},{self._y(y):g})" for x, y in pts) + "}"
            self.tikz.append(f"\\path[{self._tikz_opts(st)}] {coords};")
        else:
            self.tikz.append(f"\\path[{self._tikz_opts(st)}] {coords}{' -- cycle' if closed else ''};")

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str = "ink", width: float = 1.0,
             arrow: bool = False, dash: bool = False, opacity: float = 1.0) -> None:
        marker = ""
        if arrow:
            self.markers.add(color)
            marker = f' marker-end="url(#arr-{color})"'
        dash_s = ' stroke-dasharray="5 4"' if dash else ""
        op = f' opacity="{opacity:g}"' if opacity != 1.0 else ""
        self.svg.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{SVG_COLOR[color]}" stroke-width="{width:g}"{dash_s}{marker}{op} stroke-linecap="round"/>')
        opts = [f"draw={TIKZ_COLOR[color]}", f"line width={width * 0.75:.2f}pt"]
        if arrow:
            opts.append("-{Stealth[length=5pt, width=4pt]}")
        if dash:
            opts.append("dashed")
        if opacity != 1.0:
            opts.append(f"opacity={opacity:g}")
        self.tikz.append(f"\\draw[{', '.join(opts)}] ({x1:g},{self._y(y1):g}) -- ({x2:g},{self._y(y2):g});")

    def polyline(self, pts: list[tuple[float, float]], color: str = "ink", width: float = 1.0,
                 arrow: bool = False, dash: bool = False) -> None:
        marker = ""
        if arrow:
            self.markers.add(color)
            marker = f' marker-end="url(#arr-{color})"'
        dash_s = ' stroke-dasharray="5 4"' if dash else ""
        d = " ".join(f"{x:g},{y:g}" for x, y in pts)
        self.svg.append(f'<polyline points="{d}" fill="none" stroke="{SVG_COLOR[color]}" stroke-width="{width:g}"{dash_s}{marker} stroke-linejoin="round" stroke-linecap="round"/>')
        opts = [f"draw={TIKZ_COLOR[color]}", f"line width={width * 0.75:.2f}pt"]
        if arrow:
            opts.append("-{Stealth[length=5pt, width=4pt]}")
        if dash:
            opts.append("dashed")
        coords = " -- ".join(f"({x:g},{self._y(y):g})" for x, y in pts)
        self.tikz.append(f"\\draw[{', '.join(opts)}] {coords};")

    def text(self, x: float, y: float, lines: str | list[str], size: float = 12, anchor: Anchor = "start",
             color: str = "ink", weight: Literal["normal", "bold"] = "normal", italic: bool = False,
             family: Family = "sans", opacity: float = 1.0, line_height: float = 1.25) -> None:
        """Place one or more lines of text; (x, y) is the baseline of the first line."""
        if isinstance(lines, str):
            lines = [lines]
        fam = ('font-family="IBM Plex Mono, ui-monospace, monospace"' if family == "mono"
               else 'font-family="Source Sans 3, Segoe UI, system-ui, sans-serif"')
        anc = {"start": "start", "middle": "middle", "end": "end"}[anchor]
        wt = ' font-weight="600"' if weight == "bold" else ""
        it = ' font-style="italic"' if italic else ""
        op = f' opacity="{opacity:g}"' if opacity != 1.0 else ""
        tspans = "".join(
            f'<tspan x="{x:g}" dy="{(0 if i == 0 else size * line_height):g}">{_esc(t)}</tspan>' for i, t in enumerate(lines)
        )
        self.svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" text-anchor="{anc}" fill="{SVG_COLOR[color]}" {fam}{wt}{it}{op}>{tspans}</text>')
        # TikZ: anchor at the first baseline; use 'base west/base/base east'.
        tanchor = {"start": "base west", "middle": "base", "end": "base east"}[anchor]
        font = _tikz_font(size, self.width) + (r"\ttfamily" if family == "mono" else r"\headingfont")
        if weight == "bold":
            font += r"\bfseries"
        if italic:
            font += r"\itshape"
        opts = [f"anchor={tanchor}", f"text={TIKZ_COLOR[color]}", f"font={font}", "inner sep=0pt"]
        if opacity != 1.0:
            opts.append(f"opacity={opacity:g}")
        # One node per line, each on its own baseline: exact parity with the SVG tspans.
        for i, t in enumerate(lines):
            yy = y + i * size * line_height
            self.tikz.append(f"\\node[{', '.join(opts)}] at ({x:g},{self._y(yy):g}) {{{tex_escape(t)}}};")

    # ---- output --------------------------------------------------------
    def to_svg(self) -> str:
        defs = ""
        if self.markers:
            ms = "".join(
                f'<marker id="arr-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{SVG_COLOR[c]}"/></marker>' for c in sorted(self.markers)
            )
            defs = f"<defs>{ms}</defs>"
        body = "\n".join(self.svg)
        return (f'<svg viewBox="0 0 {self.width} {self.height}" role="img" aria-label="{_esc(self.aria_label)}">\n'
                f"{defs}\n{body}\n</svg>\n")

    def to_tikz(self) -> str:
        u = self._unit_cm()
        head = f"\\begin{{tikzpicture}}[x={u:.5f}cm, y={u:.5f}cm, line cap=round, line join=round]\n"
        return head + "\n".join(self.tikz) + "\n\\end{tikzpicture}\n"

    def write(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "fig.svg").write_text(self.to_svg(), encoding="utf-8")
        (directory / "fig.tex").write_text(self.to_tikz(), encoding="utf-8")


def _smooth_path(pts: list[tuple[float, float]], closed: bool) -> str:
    """Quadratic-Bezier smoothing through the midpoints of consecutive segments."""
    if len(pts) < 3:
        return "M " + " L ".join(f"{x:g} {y:g}" for x, y in pts)
    n = len(pts)
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    if closed:
        d = f"M {mids[-1][0]:g} {mids[-1][1]:g}"
        for i in range(n):
            d += f" Q {pts[i][0]:g} {pts[i][1]:g} {mids[i][0]:g} {mids[i][1]:g}"
        return d + " Z"
    d = f"M {pts[0][0]:g} {pts[0][1]:g}"
    for i in range(1, n - 1):
        d += f" Q {pts[i][0]:g} {pts[i][1]:g} {mids[i][0]:g} {mids[i][1]:g}"
    return d + f" L {pts[-1][0]:g} {pts[-1][1]:g}"
