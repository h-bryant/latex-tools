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
- **Style file: `modern.sty`** from this repo (`tools`). Copy it
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
\printbibliography

% Index of all provenance notes, last in the document and retitled.
% A no-op in the clean build, optional argument and all.
\listoftodos[Review notes]
\end{document}
```

The note index goes **after** `\printbibliography`, so it is the very last
thing in the annotated PDF, and it is titled **"Review notes"** rather than
`todonotes`' default "Todo list". Section 7 explains both.

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
- Write for a reader with no access to the project repository. Paths,
  commands, script names, and any other reference to the code stay out of the
  manuscript text and live in the provenance notes instead (Section 6).
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

### The repository is invisible to the manuscript

**Keep every reference to the project repository inside the provenance notes.
Nothing about the code may appear in the manuscript text itself.** The clean
PDF is the document as it circulates, and its readers have no access to the
repository and no reason to care how it is laid out. The annotated PDF is the
working document, and its reader is a reviewer checking your arithmetic, who
needs exactly that information. Confining repository references to the notes
keeps each build addressed to its own audience.

Concretely, none of the following belongs in the manuscript body, in a
section heading, in a caption, in a table, or in a footnote:

- file and directory paths (`analysis/<slug>/`, `figures/<slug>/make_fig.py`);
- commands that run the code, and lists of them in the order they must run;
- names of scripts, modules, functions, output files, or variables in the code;
- a "Reproduction", "Code availability", or "Replication files" section that
  exists to tell the reader how to re-run the analysis;
- statements about the code's internal organization, such as which module a
  routine lives in or which scripts share it.

All of it goes in `CALC:`, `FIG:`, and `DATA:` notes instead, where
`\listoftodos` gathers it into an index the reviewer can work through. If a
piece of repository information seems too important to hide from the clean
build, that is a sign it is not really repository information: restate the
substance in prose without naming the code. "The predictive distribution is
obtained from 50,000 simulated paths" belongs in the text; "written by
`run.py` with seed 20260831" belongs in the note attached to it.

Two things are not exceptions to this rule, because they are not references to
the project repository. The first is a published, citable data source or
software package, which is a normal bibliography entry and is cited in the
text as any other work would be. The second is a passage the document quotes
verbatim, such as a reproduced prompt or a quoted email, where altering the
text to remove a path would misrepresent the source.

Build instructions and a description of the repository layout are still worth
writing. They belong in the project's `README.md`, which is where a
collaborator with repository access will look for them, not in the manuscript.

## 7. Build both PDFs

Unless instructed otherwise, always produce **two PDFs** from the same
source: an annotated build with all notes visible (for human review) and a
clean build with notes disabled (the document as it would circulate).

**Naming convention:** the clean build keeps the document's own name; the
annotated build appends `-annotated` to the base name via `-jobname`. So a
document `report.tex` produces `report.pdf` (clean) and
`report-annotated.pdf` (annotated).

```sh
# Annotated review copy -> report-annotated.pdf
latexmk -lualatex -jobname=report-annotated report.tex

# Clean copy, notes disabled -> report.pdf
latexmk -lualatex -usepretex='\PassOptionsToPackage{disable}{todonotes}' report.tex
```

The `disable` option turns every `\todo`-based command and `\listoftodos`
into a no-op, so the source needs no edits between builds, and the wrapper
commands from Section 1 work unchanged. The distinct jobnames keep the two
builds' auxiliary files from clobbering each other. Expect pagination to
differ between the builds when inline notes are present; that is normal.

After building, check the log of the annotated build for `todonotes`
warnings about collided or off-page notes and fix them per Section 5.

### Where the note index goes, and what it is called

**Put `\listoftodos` after `\printbibliography`, as the last thing in the
document.** The references are part of the manuscript and belong with it; the
note index is apparatus for the reviewer and belongs after everything the
manuscript itself contains. Placing it last also makes the annotated build a
clean superset of the circulating document: everything up to the end of the
bibliography is the manuscript, and everything after it is review material.
An index sitting between the last section and the references splits the
manuscript in two and reads as though it were content.

**Title the index "Review notes".** `todonotes` calls it "Todo list", which
misdescribes it: these notes are not outstanding work items, they are
provenance records, and most of them are complete rather than pending. Pass
the title through the optional argument of `\listoftodos`:

```latex
\listoftodos[Review notes]
```

The optional argument is supported by `todonotes` and needs no patching of
package internals. It is also safe under the `disable` option, whose
replacement definition accepts and discards the argument, so the same source
line serves both builds and no stray heading appears in the clean PDF.

Do not retitle the index to anything that reads as part of the manuscript,
such as "Notes" or "Appendix". The name should make clear to anyone holding
the annotated PDF that what follows is review apparatus, not content.

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
5. The clean PDF contains no reference to the project repository: no paths,
   no commands, no script or output-file names, and no section devoted to
   reproduction (Section 6). Read the clean build, not the source, to
   confirm this, and check captions, tables, and footnotes as well as the
   body.
6. Both PDFs built: annotated and clean; the annotated build has no
   todonotes layout warnings, and its note index is titled "Review notes"
   and sits after the bibliography as the last thing in the document
   (Section 7).
7. Prose follows Section 2 (formal register, US spelling, Oxford comma, no
   em dashes, quantified hedging only).
