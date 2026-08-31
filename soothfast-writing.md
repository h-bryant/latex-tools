# Soothfast Writing: A Guide for LLMs Drafting Academic Documents in LaTeX

This guide governs how an LLM drafts academic papers, research reports, and
similar manuscripts in LaTeX. Its purpose is to make human review of the fine
details of LLM-produced writing fast and reliable. The core obligation goes
beyond standard scholarly citation: **every substantive claim, number,
calculation, and figure must carry visible provenance**, recorded in
`todonotes` annotations that a reviewer can read in the margin of the draft
PDF and that vanish from the clean PDF.

"Soothfast" is an archaic word meaning established in truth and grounded
in fact. It describes something that is true and demonstrably so. Treat
that as the standard: if you cannot state where a piece of content came from,
either find out, flag it explicitly as unverified, or do not write it.

## 1. Toolchain

- **Engine: LuaLaTeX, always.** Never pdflatex or XeLaTeX. The templates
  require `fontspec`/`unicode-math`, which LuaLaTeX handles natively.
- **Style file: `modern.sty`** from this repo (`layout-templates`). Copy it
  into the project directory alongside the `.tex` file. It provides the fonts
  (TeX Gyre Pagella body and math, Optima-family headings), 1.2 line stretch,
  geometry, `microtype`, `biblatex`, and `hyperref`. Do not re-load or
  override those packages in the document preamble except as this guide
  directs.
- **Bibliography: `biblatex` with the Biber backend, always.** `modern.sty`
  already loads it with `style=authoryear`, `natbib=true`, `maxcitenames=2`,
  `maxbibnames=99`. Never load `natbib` as a package and never use the
  legacy `bibtex` backend.
- **Build tool: `latexmk`.** The user's global `~/.latexmkrc` already selects
  LuaLaTeX and Biber, but pass `-lualatex` explicitly anyway so builds are
  portable.
- **Line 1 of every `.tex` file:** `% !TEX program = lualatex`, so editor
  build commands route correctly.

### Document skeleton

```latex
% !TEX program = lualatex
\documentclass[11pt, letterpaper]{article}

\usepackage{modern}
\usepackage{todonotes}

% modern.sty sets 1.25in side margins; widen the margin-note box so notes
% are readable (default marginparwidth is too narrow and todonotes warns).
\setlength{\marginparwidth}{2.4cm}

% Provenance-note commands (Section 5). Pass todonotes options through the
% optional argument, e.g. \srcnote[inline]{...}.
\newcommand{\srcnote}[2][]{\todo[color=blue!15,size=\scriptsize,#1]{#2}}    % SRC, DATA
\newcommand{\calcnote}[2][]{\todo[color=green!15,size=\scriptsize,#1]{#2}}  % CALC, FIG
\newcommand{\kbnote}[2][]{\todo[color=orange!20,size=\scriptsize,#1]{#2}}   % KB, ASSUME
\newcommand{\checknote}[2][]{\todo[color=red!20,size=\scriptsize,#1]{#2}}   % CHECK

\addbibresource{references.bib}

\begin{document}
% ...
\listoftodos  % index of all provenance notes; a no-op in the clean build
\printbibliography
\end{document}
```

## 2. Writing style

Write in a formal academic register throughout.

- US spelling. Oxford comma. No em dashes; restructure with commas,
  parentheses, colons, or separate sentences instead.
- Active voice when natural; passive is acceptable where academic convention
  expects it (e.g., methods descriptions).
- Direct statements over hedging. Hedge only when genuinely uncertain, and
  quantify the uncertainty when you do ("roughly 20--30 percent" rather than
  "may be somewhat higher").
- No filler, no promotional language, no rhetorical questions. Claims should
  be precise enough to be falsifiable.
- In-prose citations are author-year: `\citet{key}` for "Smith (2020) shows"
  and `\citep{key}` for "(Smith, 2020)". Footnotes follow APA style.
- Math: `amsmath` environments only (`equation`, `align`, `aligned`; never
  `eqnarray`, never `$$...$$`). `\mathbb{R}` for number sets, `\mathbf`/`\vec`
  for matrices and vectors, `\operatorname` for named operators.
- Tables: `booktabs` rules, no vertical rules.

## 3. Citations and the bibliography

Use standard formal academic citations and references wherever academic
convention calls for them: prior literature, specific findings, methods
attributable to identifiable authors, data sources with canonical citations,
and direct quotations. The provenance notes of Section 5 supplement formal
citations; they never replace them.

Rules for `references.bib`:

- **Never fabricate or guess a reference.** Every entry must correspond to a
  real work whose bibliographic metadata you have verified against an
  authoritative source (publisher page, Crossref, Semantic Scholar).
  If you cannot verify that a work exists, do not
  cite it; state the claim's basis in a `CHECK` note instead.
- Include DOIs or stable URLs where they exist.
- Use pinpoint postnotes for specific claims: `\citep[p.~12]{key}`,
  `\citep[Table~3]{key}`.

## 4. The provenance requirement

This is the heart of the guide. Standard academic writing lets many factual
statements pass without citation because a knowledgeable reader could verify
them. An LLM does not get that benefit of the doubt. **Document the source of
every factual statement, assertion, number, and judgment call in a
`todonotes` annotation, even when the statement would not warrant a formal
citation.** The annotations exist so a human reviewer can check the fine
details of the text without reconstructing your reasoning.

The only exemption is genuinely mundane content that no one would ever need
to verify: transitional sentences, roadmap paragraphs ("Section 2 describes
the data"), restatements of the document's own results, and sentences that
merely introduce notation. When in doubt, annotate.

## 5. Provenance notes with `todonotes`

### Placement

- **Margin notes are the default.** Attach the note command immediately after
  the sentence or value it documents (before intervening whitespace changes
  the anchor point).
- **Inline notes** (`[inline]` option) are the exception, used only where a
  margin note would be very awkward: notes longer than a few lines, notes
  covering an entire table or paragraph, notes inside `figure`/`table`
  floats, and notes in the abstract.
- Never place a note inside `\caption`, `\section`, a math environment, a
  footnote, or a `tabular` body; these are fragile. Put an inline note
  immediately after the float or environment instead.
- If a page gets so dense with margin notes that they collide or overflow,
  convert the longest ones to inline notes. Never omit a note to fix layout;
  the annotated build is a working document and may look cluttered.

### Note taxonomy

Start every note with one of these tags, then keep the body terse and
self-contained:

| Tag | Command | Use for |
| --- | --- | --- |
| `SRC:` | `\srcnote` | The locus behind a claim: exact page, table, equation, or section of a cited work; URL and access date for web sources. Supplements the formal citation with whatever a reviewer needs to find the passage. |
| `DATA:` | `\srcnote` | Dataset name, vintage or download date, series/variable identifiers, and any filters applied. |
| `CALC:` | `\calcnote` | A calculation you performed whose result appears in the text. Point to the repo directory holding the code and give the command that reproduces the number (Section 6). |
| `FIG:` | `\calcnote` | A figure you produced. Point to the repo directory holding the plotting code and its input data (Section 6). |
| `KB:` | `\kbnote` | A statement made from model training knowledge with no consulted source. Name the kind of source a reviewer should check (a textbook, a survey article, an official statistic) and state your confidence. |
| `ASSUME:` | `\kbnote` | An assumption, modeling choice, or judgment call you made rather than took from a source. State the alternative(s) rejected if relevant. |
| `CHECK:` | `\checknote` | Anything you could not verify: a claim you believe but could not source, a reference you could not confirm, a number from a source you could not re-access. These demand human follow-up before the document circulates. |

### Examples

```latex
Overnight repo volumes averaged roughly \$1.1 trillion in
2023.\srcnote{SRC: OFR Short-Term Funding Monitor, series
REPO-TRI-TV-TOT, accessed 2026-08-31; average of daily values,
Jan--Dec 2023.}

The estimated elasticity is $-2.3$ (s.e.\ $0.4$).\calcnote{CALC:
analysis/demand\_elasticity/ ; reproduce with
\texttt{python analysis/demand\_elasticity/run.py}. Estimate in
output/results.csv, row 4.}

Histamine neurons fire tonically during
waking.\kbnote{KB: standard result in the sleep literature
(e.g., any review of TMN physiology); high confidence, but no
specific source consulted for this sentence.}

We set the discount factor to $0.95$.\kbnote{ASSUME: conventional
annual value in this literature; not estimated. 0.90 and 0.99
used in robustness checks.}
```

For a figure, place an inline note directly after the float:

```latex
\end{figure}
\calcnote[inline]{FIG: figures/volatility\_decomposition/ ;
\texttt{python figures/volatility\_decomposition/make\_fig.py}
writes fig2.pdf from data/clean/vol\_panel.parquet.}
```

Remember to escape LaTeX-special characters inside notes (`\_`, `\$`, `\%`,
`\&`), especially in file paths and URLs.

## 6. Calculations and figures live in the repo

Any calculation you performed whose result is reported in the document, and
any figure you created, must be reproducible from code saved in the project
repository. Do not report a number you computed "in your head" or in a
throwaway session without committing the code that produces it.

- Give each calculation or figure its own directory (e.g.,
  `analysis/<slug>/`, `figures/<slug>/`) containing the code, a pointer to
  its input data, and a single obvious entry point (`run.py`, `make_fig.py`,
  or a `Makefile` target).
- The corresponding `CALC:`/`FIG:` note in the manuscript names that
  directory (repo-relative path) and the exact reproduction command.
- Follow the user's Python conventions: type-hinted, functional-leaning
  Python; `plotly` for figures, exported to PDF via Kaleido for LaTeX
  inclusion; `polars` for new data work unless the ecosystem demands
  `pandas`.
- Figures enter the document as PDF via `\includegraphics`; diagrams are
  drawn in TikZ, with the `.tex` source likewise kept in the repo and
  pointed to by a `FIG:` note.

## 7. Build both PDFs

Unless instructed otherwise, always produce **two PDFs** from the same
source: an annotated build with all notes visible (for human review) and a
clean build with notes disabled (the document as it would circulate).

```sh
# Annotated review copy -> main-annotated.pdf
latexmk -lualatex -jobname=main-annotated main.tex

# Clean copy, notes disabled -> main.pdf
latexmk -lualatex -usepretex='\PassOptionsToPackage{disable}{todonotes}' main.tex
```

The `disable` option turns every `\todo`-based command and `\listoftodos`
into a no-op, so the source needs no edits between builds, and the wrapper
commands from Section 1 work unchanged. The distinct jobnames keep the two
builds' auxiliary files from clobbering each other. Expect pagination to
differ between the builds when inline notes are present; that is normal.

After building, check the log of the annotated build for `todonotes`
warnings about collided or off-page notes and fix them per Section 5.

## 8. Pre-handoff checklist

Before presenting a draft, confirm:

1. Line 1 is `% !TEX program = lualatex`; the document loads `modern.sty`
   and compiles under LuaLaTeX with Biber, with no unresolved citations or
   references.
2. Every entry in `references.bib` is verified real, with DOI or stable URL
   where available.
3. Every non-mundane factual statement, number, assumption, and judgment
   call carries a tagged provenance note; every reported calculation and
   figure has committed, runnable code in the repo that its note points to.
4. All `CHECK:` notes are genuinely unresolvable by you and are worded so
   the human knows exactly what to verify.
5. Both PDFs built: annotated and clean; the annotated build has no
   todonotes layout warnings.
6. Prose follows Section 2 (formal register, US spelling, Oxford comma, no
   em dashes, quantified hedging only).
