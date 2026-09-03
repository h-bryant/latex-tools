# tools

A toolkit for producing documents with an LLM's help. It began as a pair of LaTeX house styles and now has three layers:

1. **LaTeX style files** (`classic.sty`, `modern.sty`) that fix fonts, geometry, bibliography, and hyperlink conventions, with driver documents and a shared bibliography.
2. **Guides for LLM-drafted documents**, read by the LLM before it writes: `soothfast-writing.md` for academic manuscripts with visible provenance, and `learn-about.md` for self-contained subject briefings in HTML and PDF.
3. **Worked examples**, one per guide, each produced by pointing an LLM at the guide with a one-paragraph prompt: `soothfast_example/` and `learn-about_example/`.

Everything LaTeX targets **LuaLaTeX** with **biblatex + Biber**. Do not build with pdflatex or XeLaTeX; the styles rely on `fontspec`/`unicode-math`.

## Contents

| Path | Purpose |
| --- | --- |
| `classic.sty` | Libertinus body + Libertinus Math, old-style figures, bold sans-serif headings via `titlesec`. |
| `modern.sty` | TeX Gyre Pagella body + Pagella Math, Optima → URW Classico → TeX Gyre Heros heading fallback, 1.2× line stretch, 1.25 in side margins. Required by both guides. |
| `classic.tex`, `modern.tex` | Driver documents exercising each style (headings, math, tables, citations). Compiled output in `classic.pdf` and `modern.pdf`. |
| `references.bib` | Shared bibliography used by the driver documents. |
| `soothfast-writing.md` | Guide governing how an LLM drafts academic manuscripts in LaTeX, with margin provenance notes and reproducible calculations (see below). |
| `learn-about.md` | Guide governing how an LLM produces a subject briefing as a self-contained HTML file and a matching PDF, from one glossary and one bibliography (see below). |
| `soothfast_example/` | Worked example of `soothfast-writing.md`: a report on the 7:00 a.m. dew point at Bryan, Texas, with clean and annotated PDFs and the code behind every number and figure. |
| `learn-about_example/` | Worked example of `learn-about.md`: a briefing on degenerative cervical myelopathy in HTML and PDF. |

## LaTeX style files

Both styles load the same bibliography setup (`biblatex`, `backend=biber`, `style=authoryear`, `natbib=true`, `maxcitenames=2`, `maxbibnames=99`) and the same `hyperref` colors (blue cite/URL links, black internal links), so a project can swap between them without rewriting citations.

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

## Guides for LLM-drafted documents

Each guide is a complete specification that an LLM follows when producing a document: toolchain, writing style, structure, required checks, and a pre-handoff checklist. To use one, point the LLM at the guide and state the assignment. The prompts that produced the two worked examples are one paragraph each and are recorded verbatim in the examples' READMEs. Both guides build on `modern.sty`, which is copied unmodified into the project directory so the project builds standalone.

### Soothfast writing

`soothfast-writing.md` sets the standard for LLM-drafted manuscripts. "Soothfast" (Old English *sooþfæst*, "steadfast in truth") is an archaic word for that which is true and demonstrably so. The guide's core obligation: every substantive claim, number, calculation, and figure carries visible provenance, recorded in tagged `todonotes` margin annotations (`SRC:`, `DATA:`, `CALC:`, `FIG:`, `KB:`, `ASSUME:`, `CHECK:`). Every manuscript is built twice from the same source: an annotated review copy (`<name>-annotated.pdf`) with all notes visible and an index of them after the bibliography, and a clean copy (`<name>.pdf`) with the notes disabled. Reported calculations and figures must be reproducible from code committed to the project repository, and the manuscript body never refers to that repository; only the notes do.

### Learn-about briefings

`learn-about.md` sets the standard for LLM-produced subject briefings: self-contained learning documents on one topic, delivered as an HTML file and a PDF built from the same content. The HTML carries hover definitions on every marked technical term, a sticky section navigator, inline SVG figures, and verified external links. The PDF (LuaLaTeX, `modern.sty`, `glossaries-extra`) marks the same terms with a dotted underline linked to a glossary that closes the document, with page back-references. Definitions live once in `glossary.json`; a small generator described in the guide writes the LaTeX entries, injects the JSON into the HTML, and checks that both formats mark the same terms. The guide also covers research before drafting, the default section arc, figure parity between SVG and TikZ, and what the accompanying README must tell the reader to verify.

## Worked examples

Each example directory is a complete, standalone project with its own README recording the prompt that produced it, the build commands, the judgment calls made along the way, and anything a reader should verify before relying on the document.

| Example | Follows | Deliverables |
| --- | --- | --- |
| `soothfast_example/` | `soothfast-writing.md` | `dew_point.pdf` (clean) and `dew_point-annotated.pdf` (review copy with margin notes and a note index). Python under `data/`, `analysis/`, and `figures/` reproduces every reported number and figure from a single download. |
| `learn-about_example/` | `learn-about.md` | `degenerative-cervical-myelopathy.html` and `.pdf`, with `glossary.json`, `references.bib`, and one `make_fig.py` per figure as the shared sources for both formats. |
