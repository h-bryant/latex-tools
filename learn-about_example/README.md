# Degenerative cervical myelopathy: a subject briefing

A worked example of the `learn-about.md` workflow: a self-contained briefing on one
subject, delivered as an HTML file with hover definitions and as a LuaLaTeX PDF with
an end glossary, both rendered from the same content, glossary, bibliography, and
figure sources.

- **Subject:** degenerative cervical myelopathy (DCM) in humans: age-related narrowing
  of the cervical spinal canal that injures the spinal cord.
- **Audience:** the guide's default: a numerate, scientifically literate adult who is
  new to the field. Every field-specific term is defined; no clinical background is
  assumed.
- **Emphasis:** balanced, on the medical arc (overview, mechanism, epidemiology,
  presentation, natural history, diagnosis, treatment, prognosis, debates).
- **Compiled:** September 3, 2026.
- **Length:** about 4,800 words of body prose, about 7,300 words including tables,
  callouts, and captions; 41 PDF pages, of which 19 are body text (including the
  contents), 11 are sources, and 11 are the glossary. Sixty works cited, 81 glossary
  terms, 4 figures, 8 tables.

## The prompt that produced this briefing

Verbatim, as typed:

> I want to learn about degenerative cervical myelopathy in humans.  Use the instructions in github.com/h-bryant/tools/learn-about.md.  Include this prompt in a footnote.

The prompt appears as footnote 1 in both formats, attached to the one-sentence
description under the title.

## Files

```
README.md                             this file
degenerative-cervical-myelopathy.html the HTML briefing (self-contained; only the Google Fonts stylesheet is external)
degenerative-cervical-myelopathy.tex  the LaTeX source
degenerative-cervical-myelopathy.pdf  the built PDF
modern.sty                            copied unmodified from the repository root
references.bib                        every cited work; single source for both formats
glossary.json                         every defined term; single source for both formats
glossary.tex                          generated from glossary.json by make_glossary.py; do not edit
make_glossary.py                      the generator from learn-about.md, Section 5, verbatim
figures/figlib.py                     small library that writes each figure as inline SVG and as TikZ from one description
figures/canal-cross-section/          Figure 1: make_fig.py, fig.svg, fig.tex
figures/prevalence-iceberg/           Figure 2: make_fig.py, data.csv, fig.svg, fig.tex
figures/diagnostic-pathway/           Figure 3: make_fig.py, fig.svg, fig.tex
figures/management-algorithm/         Figure 4: make_fig.py, fig.svg, fig.tex
```

The files sit at the top of this directory rather than in a `<slug>/` subdirectory,
mirroring the layout of `soothfast_example/`. The slug is
`degenerative-cervical-myelopathy`.

## Build

```sh
for d in figures/*/; do python3 "$d/make_fig.py"; done        # regenerate fig.svg and fig.tex (only if a figure changed)
python3 make_glossary.py degenerative-cervical-myelopathy      # glossary.tex + HTML injection + parity check
latexmk -lualatex degenerative-cervical-myelopathy.tex         # runs Biber and the glossary reruns automatically
```

The HTML needs no build step beyond the glossary injection. Checks that were run:
`node --check` on the page script (clean); `xmllint --html --noout` (clean apart from
HTML5 element names the 2006 libxml parser does not know); the glossary generator
reports parity between the two formats; the LaTeX log shows no errors, no undefined
citations or glossary entries, and no overfull boxes. Build products other than the
PDF are excluded by `.gitignore`.

## How it was made

Research came first: the 2017 AO Spine and CSRS clinical practice guideline and its
systematic reviews, the AO Spine North America and International surgical cohorts,
the Cambridge group's epidemiological and diagnostic studies, the two randomized
trials in the field (Kadaňka 2011; CSM-S 2021), the CSM-Protect drug trial, the
RECODE-DCM consensus papers, and recent reviews. The personal research library
(infohord) was searched first and held nothing on the subject. Bibliographic
metadata for every DOI was pulled from Crossref and cached; the citation labels in
the HTML were then matched to the a/b suffixes biblatex assigned.

The text was drafted once in a scratch Markdown file with lightweight markup for
glossary terms, citations, tables, figures, and callouts, and a small scratch script
rendered it into the HTML skeleton and the LaTeX skeleton from `learn-about.md`. That
script is not part of the deliverable; edit the HTML and TeX directly from here on.

## Judgment calls and deviations from learn-about.md

1. **Data chart without plotly.** The guide asks for data charts through plotly and
   Kaleido. Kaleido needs a Chrome binary, which this machine does not have, so each
   figure is instead produced by a dependency-free `make_fig.py` that emits the SVG
   and the TikZ from one geometric description (`figures/figlib.py`). The chart data
   live in `figures/prevalence-iceberg/data.csv`. Parity is therefore exact rather
   than approximate.
2. **Glossary marker.** The skeleton marks terms with ulem's `\dotuline`. Under
   `glossaries-extra` the marked text arrives wrapped in a macro, so ulem treats a
   multi-word term as a single unbreakable word; long terms such as "modified Japanese
   Orthopaedic Association score" overflowed the margin by up to 67 pt. The PDF uses
   `lua-ul` (with `luacolor`) to draw the same dotted accent underline after line
   breaking. This is LuaLaTeX-only, which the house style already requires.
3. **Other preamble additions**, all commented in the `.tex`: `array` (for wrapping
   table columns); `\ExecuteBibliographyOptions{uniquename=false}` (Crossref spells
   the same author differently across papers, and biblatex otherwise prints given
   names in citations to tell them apart); `breakable` on the callout boxes (the "In
   brief" box otherwise jumped to page 2, leaving page 1 nearly empty); and URL break
   penalties for the bibliography. `modern.sty` is unmodified.
4. **Table widths** in the PDF are computed from content length as `p{}` columns so
   every table fits the text width without shrinking below `\small`.
5. **One remaining log warning**, from hyperref: the bookmark for "Works cited" shares
   an anchor with its parent section and hyperref adds one itself. It has no visible
   effect.

## Verify before relying on this document

- **Twenty-two DOI links** resolve correctly (each was matched to its metadata on
  Crossref) but the publisher pages return HTTP 403 to automated fetches: SAGE (Global
  Spine Journal), BMJ, JAMA, Wiley, Oxford (Brain), Science, and MDPI. Open them in a
  browser to confirm. Where a free PMC copy exists it is linked and was fetched.
- **RECEDE-Myelopathy (ibudilast)**: the registry (ISRCTN16682024) listed the trial as
  recruiting when this was compiled and no results had been published. Check for a
  readout.
- **OPLL outside East Asia** is described qualitatively ("far more common in East
  Asian than in Western populations"). The Japanese prevalence (1.9 to 4.3% over age
  30) is from the Matsunaga and Sakou (2012) abstract; the full text of the Sakai et
  al. (2022) epidemiology review could not be fetched programmatically.
- **Cost per QALY** figures (about CAD 11,500 and 20,500) are taken from the 2017
  guideline's summary of Witiw et al. (2017); that paper's abstract was truncated
  before the numbers.
- **mJOA item wording and Nurick grade wording** follow the StatPearls chapter
  (Margetis and Donnally, 2025); severity bands follow Tetreault et al. (2017). Benzel
  (1991), Nurick (1972), and Yu et al. (2011) are cited from verified metadata and
  abstracts, not full text.
- **Karadimas et al. (2015)** is cited for the 9.3% postoperative decline and 44%
  residual impairment figures as stated in that paper's abstract; the underlying cohort
  is not identified there.
- **The Torg–Pavlov threshold of about 0.8** in the glossary is textbook usage rather
  than a figure from a cited paper; the 13 mm canal threshold is from Bajwa et al.
  (2012).
- **Compression prevalence by region** (39.7% American/European versus 11.1% Asian)
  comes from Smith et al. (2021), whose authors could not fully explain the
  difference; treat it as an observation, not an established fact.
- Guidelines change. The 2017 guideline remains the reference standard; the 2025 AO
  Spine appraisal (Fehlings et al., 2025) adds conditional recommendations but is not
  a new guideline. Check for a successor before relying on the management section.
