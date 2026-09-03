# latex-tools

Tools I use for creating LaTeX documents: two reusable article style files, driver documents that demonstrate them, and a writing guide for LLM-drafted manuscripts.

Everything targets **LuaLaTeX** with **biblatex + Biber**. Do not build with pdflatex or XeLaTeX; the styles rely on `fontspec`/`unicode-math`.

## Contents

| File | Purpose |
| --- | --- |
| `classic.sty` | Libertinus body + Libertinus Math, old-style figures, bold sans-serif headings via `titlesec`. |
| `modern.sty` | TeX Gyre Pagella body + Pagella Math, Optima → URW Classico → TeX Gyre Heros heading fallback, 1.2× line stretch, 1.25 in side margins. |
| `classic.tex`, `modern.tex` | Driver documents exercising each style (headings, math, tables, citations). Compiled output in `classic.pdf` and `modern.pdf`. |
| `references.bib` | Shared bibliography used by the driver documents. |
| `soothfast-writing.md` | Guide governing how an LLM drafts academic documents in LaTeX (see below). |
| `learn-about.md` | Guide governing how an LLM produces a subject briefing in HTML (hover definitions) and PDF (end glossary with marked terms) from one glossary and one bibliography (see below). |
| `soothfast_example/` | Placeholder for a worked example following the guide. |

Both styles load the same bibliography setup (`biblatex`, `backend=biber`, `style=authoryear`, `natbib=true`, `maxcitenames=2`, `maxbibnames=99`) and the same `hyperref` colors (blue cite/URL links, black internal links), so a project can swap between them without rewriting citations.

## Usage

Copy the chosen `.sty` file into the project directory alongside the document, then:

```latex
% !TEX program = lualatex
\documentclass[11pt, letterpaper]{article}
\usepackage{modern}   % or: classic
\addbibresource{references.bib}
```

Build with latexmk:

```sh
latexmk -lualatex modern.tex
```

The global `~/.latexmkrc` already selects LuaLaTeX (`$pdf_mode = 4`) and Biber (`$bibtex_use = 2`), but passing `-lualatex` explicitly keeps builds portable. Keep `% !TEX program = lualatex` on line 1 of every `.tex` file so editor build commands route correctly.

## Soothfast writing

`soothfast-writing.md` sets the standard for LLM-drafted manuscripts. "Soothfast" (Old English *sooþfæst*, "steadfast in truth") is an archaic word for that which is true and demonstrably so. The guide's core obligation: every substantive claim, number, calculation, and figure carries visible provenance, recorded in tagged `todonotes` margin annotations (`SRC:`, `DATA:`, `CALC:`, `FIG:`, `KB:`, `ASSUME:`, `CHECK:`) that appear in an annotated review PDF and vanish from the clean build. Reported calculations and figures must be reproducible from code committed to the project repository.

## Learn-about briefings

`learn-about.md` sets the standard for LLM-produced subject briefings: self-contained learning documents on one topic, delivered as an HTML file and a PDF built from the same content. The HTML carries hover definitions on every marked technical term, a sticky section navigator, inline SVG figures, and verified external links. The PDF (LuaLaTeX, `modern.sty`, `glossaries-extra`) marks the same terms with a dotted underline linked to a glossary that closes the document, with page back-references. Definitions live once in `glossary.json`; a small generator described in the guide writes the LaTeX entries, injects the JSON into the HTML, and checks that both formats mark the same terms.
