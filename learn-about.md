# Learn About: A Guide for LLMs Producing Subject Briefings in HTML and PDF

This guide governs how an LLM produces a **subject briefing**: a self-contained,
well-sourced document that teaches an intelligent reader about one subject from
a standing start. Every briefing ships in two formats built from the same
content:

- **HTML**: a single self-contained file with a sticky section navigator,
  inline figures, external links, and **hover definitions** on every marked
  technical term.
- **PDF**: a LuaLaTeX document in the `modern.sty` house style, with the same
  sections, figures, and links, a **glossary at the end** holding the same
  definitions, and a visible **marker on every glossary term** where it occurs
  in the body text.

The two formats are authored separately (an HTML file and a `.tex` file), but
the things most likely to drift are single-sourced: the glossary lives in one
JSON file that generates both renderings, the bibliography lives in one `.bib`
file, and figure data lives in one script per figure. A generator script
checks that the two formats mark the same terms.

The standard of truth is the same as in `soothfast-writing.md`: do not state
what you cannot source. A briefing that is wrong teaches the wrong thing with
confidence, which is worse than no briefing.

## 1. The assignment

### Inputs

The user supplies a **subject** and, optionally, an **audience**, an
**emphasis**, a **length**, and a **slug**. Defaults when unspecified:

- **Audience:** a numerate, scientifically literate adult who is new to this
  field. Assume intelligence, not background. Define every field-specific term
  (Section 5) and explain every mechanism from first principles once.
- **Emphasis:** balanced coverage across the default arc in Section 3.
- **Length:** 3,000 to 6,000 words of body text. Go longer only when the
  subject genuinely demands it, never to pad.
- **Slug:** the subject in kebab-case (`small-fiber-neuropathy`,
  `repo-market-plumbing`, `bayesian-vars`).

If the subject is ambiguous in a way that would change the whole document
(for example, "duration" in finance versus physics), ask before researching.
Otherwise make routine judgment calls yourself and state them in the README.

### Deliverables and layout

```
<slug>/
  README.md              # what this is, the prompt that produced it, how to build
  <slug>.html            # the HTML briefing, self-contained
  <slug>.tex             # the LaTeX source
  <slug>.pdf             # the built PDF
  modern.sty             # copied from the tools repo, unmodified
  references.bib         # every cited work; single source for both formats
  glossary.json          # every defined term; single source for both formats
  glossary.tex           # generated from glossary.json, never edited by hand
  make_glossary.py       # the generator in Section 5, verbatim
  figures/<fig-slug>/    # one directory per figure: source, data, outputs
```

The README states the subject, the audience assumed, the date compiled, the
prompt that produced the briefing (verbatim), the build commands from
Section 7, and anything the user should verify (Section 2). Build products
other than the PDF (`.aux`, `.bbl`, `.glsdefs`, and so on) stay out of version
control.

## 2. Research before writing

Research the subject before drafting a sentence. The briefing is a synthesis
of what authoritative sources say, not a recital of training knowledge.

- **Consult sources actively.** Use web search and fetch tools to read primary
  literature, systematic reviews, clinical or professional guidelines, official
  statistics, standards documents, and textbooks, as the subject demands. When
  the user's personal research library (the `infohord` tools) is available and
  the subject overlaps their work, search it first; the user's own saved
  material is the best guide to what they already know and care about.
- **Source hierarchy.** Prefer, in order: peer-reviewed primary studies and
  meta-analyses; guidelines and consensus statements from recognized bodies;
  official data producers; high-quality reviews and textbooks; reputable
  explainers from institutions (a clinic, a central bank, a standards body).
  Blogs, forums, and commercial pages are acceptable only for what they are
  uniquely good at (practical tips, community resources) and must be labeled as
  such.
- **Numbers.** Every number in the briefing traces to a listed source.
  Report ranges rather than false precision when sources disagree ("45 to 90
  percent across cohorts" rather than "70 percent"), and say what population,
  period, and method the figure describes. Never invent a statistic, a dose, a
  price, a date, or a sample size. If a needed number cannot be found, say so
  in the text rather than approximating silently.
- **Consensus, contested, speculative.** Separate what the field agrees on,
  what is actively debated (say by whom and why), and what is speculative or
  early. Do not present a single study's finding as settled.
- **Dates.** Stamp both formats "Compiled MONTH YEAR" and read recent sources:
  guidelines and prices change, and a briefing that quietly reports a
  superseded standard misleads.
- **Verify every link.** Fetch each URL you intend to publish and confirm it
  resolves to the work you describe. Never guess a DOI, PubMed identifier, or
  URL from memory. If you cannot verify a stable identifier for a work you are
  confident exists, link to a search-results URL that will surface it (a PubMed
  or Google Scholar query) and make the link text say so ("PubMed search").
- **What you could not verify** goes in a short "Verify" list in the README,
  so the user knows exactly what to check before relying on the document.

If the user asks for the full provenance apparatus of `soothfast-writing.md`
(tagged `todonotes` margin annotations and an annotated review build), layer
it onto the PDF exactly as that guide describes. It is not required by
default.

## 3. Structure of a briefing

### The default arc

Adapt the section names and count to the subject; the arc below is the
fallback, not a template to fill. A medical subject reads naturally as
Overview, Risk factors, Symptoms, Differential, Diagnosis, Treatment,
Prognosis. A market or institution reads as What it is, How it works, Who the
players are, What can go wrong, How it is regulated, Open questions. A method
reads as The problem it solves, The idea, The machinery, When it works and
fails, How to use it, Where the field is going.

1. **Overview.** What the subject is, why it matters, and how it fits into
   its wider field. Ends with the reader able to explain the subject in two
   sentences.
2. **Mechanism or core concepts.** How it works, built up from parts the
   reader already understands. This is where the anchoring figure lives.
3. **The evidence.** What is known quantitatively: prevalence, magnitudes,
   effect sizes, performance, costs, with sources and ranges.
4. **Distinctions.** What it is not; how it differs from the things it is
   confused with; common misconceptions and why they arise.
5. **Practice.** What a practitioner does with this knowledge: diagnosis and
   treatment, estimation and pitfalls, policy levers, implementation choices.
6. **Debates and outlook.** Open questions, live controversies, and what is
   coming.
7. **Sources and further reading.** Every cited work plus curated links
   (Section 9), grouped and annotated.
8. **Glossary.** PDF only, generated (Section 5). The HTML carries the same
   definitions as hover text.

### Fixed elements

- **Masthead.** Title; a one-sentence description ("dek") stating the scope in
  plain language; a meta line with "Compiled MONTH YEAR", the hint "Dotted
  terms: hover, tap, or focus for definitions" (HTML) or "Dotted terms are
  defined in the glossary" (PDF), and, for medical, legal, financial, or
  safety subjects, "Educational briefing, not [medical] advice".
- **In brief.** Five to eight bullets immediately after the masthead giving
  the whole story for a reader with two minutes. Every bullet is a complete
  claim, not a topic label.
- **Section headings that state the point.** "Why the exam can look normal"
  teaches; "Diagnosis" does not. Sentence case. A heading phrased as the
  reader's own question ("How common is it?") is acceptable because it is
  navigational; rhetorical questions in body text are not.
- **Callouts.** A *Note* callout for the key takeaway or an important nuance;
  a *Caution* callout for the must-not-miss point, the common error, or the
  safety issue. At most one or two per section; a page of callouts is a page
  with no emphasis.
- **Tables** for any comparison of three or more items on two or more
  attributes. Ranges get a range meter (HTML) or an explicit range (PDF).
- **Figures** wherever they help (Section 8).
- **Footer.** Compilation date, a sentence on the evidence base and its limits,
  and the advice disclaimer where applicable.

## 4. Writing style

- US spelling. Oxford comma. **No em dashes**; restructure with commas,
  colons, parentheses, or separate sentences.
- Formal but readable register. Third person by default. Active voice when
  natural.
- Direct statements. Hedge only when genuinely uncertain, and quantify the
  hedge ("roughly a third" rather than "some").
- **Explain before you use.** The first time a concept appears, the sentence
  around it should carry enough that the reader can continue without the
  hover text. The glossary is a safety net, not a substitute for teaching.
- One idea per paragraph; paragraphs of three to six sentences. Lists for
  parallel items, prose for argument.
- No filler, no promotional language, no throat-clearing ("It is important to
  note that"). Cut any sentence that would survive deletion without loss.
- Inline citations are author-year with a link: "Peters et al. (2013)" in the
  HTML links to the work; in the PDF use `\citet{key}` and `\citep{key}` from
  the shared `references.bib`.
- Numbers: digits for anything measured; spell out one through nine when
  used as ordinary words; thin or non-breaking spaces between a number and
  its unit; en dash for ranges in the PDF (`45--90\%`), a hyphen or "to" in
  running HTML text.

## 5. Glossary: one source, two renderings

### What counts as jargon

Mark any term the default reader would not reliably know: field-specific
nouns, named tests and instruments, abbreviations and acronyms, eponyms, and
ordinary words used with a technical meaning ("sensitivity", "duration",
"liquidity"). Do not mark words the reader knows from general education, and
do not mark the subject itself in its own briefing.

### `glossary.json`

One object, keyed by stable lowercase alphanumeric keys:

```json
{
  "peripheralneuropathy": {
    "term": "peripheral neuropathy",
    "definition": "Damage to the nerves outside the brain and spinal cord. Subtypes are named for the fibers involved: large-fiber, small-fiber, or mixed."
  },
  "nociceptor": {
    "term": "nociceptor",
    "plural": "nociceptors",
    "definition": "A sensory nerve ending specialized to detect actual or threatened tissue damage and signal it as pain."
  },
  "nnt": {
    "term": "number needed to treat (NNT)",
    "definition": "How many patients must take a drug for one to achieve at least 50% pain relief beyond placebo. Lower is better: an NNT of 4 is a good neuropathic-pain drug; an NNT of 10 is marginal."
  }
}
```

Rules:

- **`key`**: lowercase letters and digits only, no spaces or punctuation,
  stable once used (it appears in both the HTML and the LaTeX).
- **`term`**: the headword as it would appear in running text: lowercase
  unless it is a proper noun or an acronym. Put an acronym in parentheses
  after the expansion. The glossary capitalizes the first letter itself.
- **`plural`**: only when the plural is irregular or the PDF uses `\glspl`.
- **`definition`**: one to three sentences, plain Unicode text, no HTML and
  no LaTeX. Self-contained (do not lean on the surrounding paragraph), and
  where possible end with why the term matters for this subject. Use real
  characters (≥, ≈, en dash, Greek letters); the generator escapes LaTeX
  specials such as `%`, `&`, `$`, and `_`.

### Marking terms in the text

- Mark the **first occurrence in each top-level section**, in both formats,
  so a reader who jumps in from the navigator or the contents page meets the
  definition. Mark later occurrences only where the text is likely to be read
  in isolation (a table cell, a callout).
- The visible text may differ from the headword: "myelinated" can point at
  the `myelin` entry, "NNT" at the `nnt` entry.
- **Never** mark terms inside headings, figure captions, figure text, table
  headers, the masthead, the sources section, or the glossary itself. Both
  the HTML tooltip and the LaTeX marker are fragile there, and headings should
  not depend on hover text.

HTML markup:

```html
a form of <span class="t" data-g="peripheralneuropathy">peripheral neuropathy</span> that
```

LaTeX markup (`glossaries-extra`):

```latex
a form of \gls{peripheralneuropathy} that        % prints the headword
the thinly \glslink{myelin}{myelinated} fibers    % arbitrary visible text
\Gls{nociceptor} fire; \glspl{nociceptor} adapt   % capitalized; plural
```

### The generator

Save this file verbatim as `make_glossary.py` in the project directory and run
`python3 make_glossary.py <slug>` before every build. It writes
`glossary.tex`, injects the JSON into the HTML's
`<script type="application/json" id="glossary">` block, checks that every key
used in either format is defined, and reports keys used in one format but not
the other. Treat every line it prints as a task; a clean run prints one line.

```python
"""Generate glossary.tex and inject the glossary JSON into the HTML from glossary.json.

Usage: python3 make_glossary.py <slug>
Reads  glossary.json; writes glossary.tex; rewrites the <script id="glossary"> block
in <slug>.html; then checks that every key used in <slug>.html and <slug>.tex exists
and reports keys used in one format but not the other.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LATEX_SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def tex_escape(s: str) -> str:
    return "".join(LATEX_SPECIALS.get(c, c) for c in s)


def tex_entry(key: str, e: dict[str, str]) -> str:
    plural = f",\n  plural={{{tex_escape(e['plural'])}}}" if "plural" in e else ""
    return (
        f"\\newglossaryentry{{{key}}}{{\n"
        f"  name={{{tex_escape(e['term'])}}},\n"
        f"  description={{{tex_escape(e['definition'])}}}{plural}\n}}"
    )


def inject_html(html: str, gloss: dict[str, dict[str, str]]) -> str:
    payload = json.dumps(gloss, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    pattern = re.compile(r'(<script type="application/json" id="glossary">)(.*?)(</script>)', re.S)
    if not pattern.search(html):
        sys.exit('error: no <script type="application/json" id="glossary"> block in HTML')
    return pattern.sub(lambda m: f"{m.group(1)}\n{payload}\n{m.group(3)}", html, count=1)


def keys_used(text: str, fmt: str) -> set[str]:
    if fmt == "html":
        return set(re.findall(r'data-g="([^"]+)"', text))
    return set(re.findall(r"\\[gG]ls(?:pl|link|text|first)?\*?(?:\[[^\]]*\])?\{([^}]+)\}", text))


def main(slug: str) -> None:
    gloss: dict[str, dict[str, str]] = json.loads(Path("glossary.json").read_text(encoding="utf-8"))
    Path("glossary.tex").write_text(
        "% Generated by make_glossary.py from glossary.json. Do not edit by hand.\n"
        + "\n".join(tex_entry(k, e) for k, e in sorted(gloss.items())) + "\n",
        encoding="utf-8",
    )
    html_path, tex_path = Path(f"{slug}.html"), Path(f"{slug}.tex")
    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(inject_html(html, gloss), encoding="utf-8")

    used = {"html": keys_used(html, "html"), "tex": keys_used(tex_path.read_text(encoding="utf-8"), "tex")}
    defined = set(gloss)
    problems = [f"{fmt}: undefined key {k!r}" for fmt, ks in used.items() for k in sorted(ks - defined)]
    problems += [f"defined but unused in {fmt}: {k!r}" for fmt, ks in used.items() for k in sorted(defined - ks)]
    problems += [f"used in html only: {k!r}" for k in sorted(used["html"] - used["tex"])]
    problems += [f"used in tex only: {k!r}" for k in sorted(used["tex"] - used["html"])]
    print("\n".join(problems) if problems else f"glossary ok: {len(defined)} terms, parity between html and tex")
    if any(p.startswith(("html: undefined", "tex: undefined")) for p in problems):
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: make_glossary.py <slug>"))
```

## 6. The HTML briefing

One file, no build step, opens from disk. The only network requests are the
Google Fonts stylesheet (with system fallbacks declared, so the page reads
correctly offline). No external images, scripts, or stylesheets otherwise;
figures are inline SVG (Section 8).

### Behavior the file must have

- **Hover definitions.** Every `span.t` shows its definition in a tooltip on
  hover, on keyboard focus, and on tap (toggle). Escape closes it. The term is
  reachable by Tab and carries an `aria-label` with the full definition.
- **Sticky navigator** with one link per top-level section and a scrollspy
  that highlights the current section.
- **Theme-aware.** Light palette on `:root`, dark palette under
  `prefers-color-scheme: dark` and under `[data-theme="dark"]`. SVG figures
  use `currentColor` and CSS variables so they follow the theme.
- **Responsive.** Body text column about 46 rem; tables scroll inside their
  own wrapper; no horizontal page scroll on a phone.
- **Accessible.** Reduced-motion respected, visible focus rings, `role="img"`
  and `aria-label` on every SVG, external links marked.

### Skeleton

Copy this skeleton and fill it in. Keep the CSS intact so briefings look like
one family; add component styles rather than rewriting these. The tooltip
script reads the glossary from the JSON block that `make_glossary.py` fills.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SUBJECT</title>
<meta name="description" content="One-sentence description of the briefing.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --bg: #FBF9F6; --surface: #FFFFFF; --ink: #21282A; --ink-2: #4E5A58; --muted: #7C8683;
    --accent: #0E6E6E; --accent-ink: #0B5757; --coral: #A8433B;
    --line: #E4DFD6; --line-soft: #EEEAE2; --note-bg: #EDF3F0; --flag-bg: #F8ECE7;
    --mark: #00876F; --mark-track: #D2E6DF; --tip-bg: #24302E; --tip-ink: #F4F1EA;
    --code-bg: #F1EDE5; --shadow: 0 10px 30px rgba(33,40,42,.12);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #14181A; --surface: #1B2124; --ink: #E5E2DA; --ink-2: #ABB4B0; --muted: #7C8683;
      --accent: #4FB3AC; --accent-ink: #6BC4BD; --coral: #E08078;
      --line: #2B3336; --line-soft: #232B2E; --note-bg: #1B2624; --flag-bg: #291F1D;
      --mark: #2AA093; --mark-track: #24413D; --tip-bg: #E5E2DA; --tip-ink: #1B2124;
      --code-bg: #222A2D; --shadow: 0 10px 30px rgba(0,0,0,.45);
    }
  }
  :root[data-theme="dark"] {
    --bg: #14181A; --surface: #1B2124; --ink: #E5E2DA; --ink-2: #ABB4B0; --muted: #7C8683;
    --accent: #4FB3AC; --accent-ink: #6BC4BD; --coral: #E08078;
    --line: #2B3336; --line-soft: #232B2E; --note-bg: #1B2624; --flag-bg: #291F1D;
    --mark: #2AA093; --mark-track: #24413D; --tip-bg: #E5E2DA; --tip-ink: #1B2124;
    --code-bg: #222A2D; --shadow: 0 10px 30px rgba(0,0,0,.45);
  }

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; scroll-padding-top: 4.5rem; }
  @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
  body { background: var(--bg); color: var(--ink); font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif; font-size: 17px; line-height: 1.65; margin: 0; }
  h1, h2, h3 { font-family: "Source Serif 4", Georgia, "Times New Roman", serif; line-height: 1.2; text-wrap: balance; color: var(--ink); }
  h1 { font-size: clamp(2.1rem, 5.5vw, 3.1rem); font-weight: 700; margin: .35em 0 .3em; }
  h2 { font-size: 1.65rem; font-weight: 700; margin: 0 0 .6em; }
  h3 { font-size: 1.18rem; font-weight: 600; margin: 2em 0 .5em; }
  p { margin: 0 0 1em; }
  a { color: var(--accent-ink); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 2px; }
  a:hover { text-decoration-thickness: 2px; }
  a:focus-visible, .t:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
  a.ext::after { content: "\2197"; font-size: .72em; margin-left: .18em; vertical-align: super; text-decoration: none; display: inline-block; }
  ul, ol { padding-left: 1.35em; margin: 0 0 1em; }
  li { margin-bottom: .45em; }
  strong { font-weight: 600; }
  code { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .88em; background: var(--code-bg); padding: .05em .3em; border-radius: 4px; }
  .wrap { max-width: 46rem; margin: 0 auto; padding: 0 1.25rem; }
  .wide { max-width: 60rem; }

  /* masthead */
  header.masthead { padding: 3.5rem 0 2rem; border-bottom: 1px solid var(--line); }
  .eyebrow { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--accent-ink); margin: 0 0 .4rem; }
  .dek { font-size: 1.15rem; color: var(--ink-2); max-width: 40rem; margin-bottom: 1.2rem; }
  .meta { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .74rem; color: var(--muted); display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; }

  /* sticky navigator */
  nav.toc { position: sticky; top: 0; z-index: 40; background: color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border-bottom: 1px solid var(--line); }
  nav.toc .row { display: flex; gap: .25rem; overflow-x: auto; padding: 0 1rem; max-width: 60rem; margin: 0 auto; scrollbar-width: none; }
  nav.toc .row::-webkit-scrollbar { display: none; }
  nav.toc a { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-2); text-decoration: none; white-space: nowrap; padding: .8rem .6rem calc(.8rem - 2px); border-bottom: 2px solid transparent; }
  nav.toc a:hover { color: var(--accent-ink); }
  nav.toc a.on { color: var(--accent-ink); border-bottom-color: var(--accent); }

  /* sections */
  section.block { padding: 3rem 0 1.5rem; border-bottom: 1px solid var(--line); }
  section.block:last-of-type { border-bottom: none; }
  .sec-eyebrow { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); margin-bottom: .35rem; }

  /* glossary terms and tooltip */
  .t { cursor: help; text-decoration: underline dotted; text-decoration-color: var(--accent); text-decoration-thickness: 1.5px; text-underline-offset: 3px; }
  #tip { position: fixed; z-index: 100; max-width: 21rem; background: var(--tip-bg); color: var(--tip-ink); border-radius: 8px; padding: .65rem .85rem; font-size: .84rem; line-height: 1.5; box-shadow: var(--shadow); pointer-events: none; }
  #tip b { display: block; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .25rem; opacity: .75; }

  /* callouts */
  .note, .flag { border-radius: 10px; padding: 1rem 1.2rem; margin: 1.4rem 0; font-size: .95rem; }
  .note { background: var(--note-bg); border-left: 3px solid var(--accent); }
  .flag { background: var(--flag-bg); border-left: 3px solid var(--coral); }
  .note .lab, .flag .lab { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; display: block; margin-bottom: .35rem; }
  .note .lab { color: var(--accent-ink); }
  .flag .lab { color: var(--coral); }
  .note p:last-child, .flag p:last-child, .note ul:last-child { margin-bottom: 0; }

  /* tables */
  .tablewrap { overflow-x: auto; margin: 1.5rem 0; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
  table { border-collapse: collapse; width: 100%; font-size: .92rem; line-height: 1.5; }
  th { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .68rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); text-align: left; font-weight: 500; padding: .8rem .9rem; border-bottom: 1px solid var(--line); background: var(--line-soft); }
  td { padding: .75rem .9rem; border-bottom: 1px solid var(--line-soft); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  td .sub { color: var(--muted); font-size: .85rem; display: block; }
  .num { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .84rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .tablenote { font-size: .85rem; color: var(--ink-2); margin: -.9rem 0 1.5rem; line-height: 1.55; }
  /* range meter: div.rng containing an i element positioned with inline left and width percentages */
  .rng { position: relative; width: 7.5rem; height: 8px; border-radius: 4px; background: var(--mark-track); margin-top: .45rem; }
  .rng i { position: absolute; top: 0; height: 8px; border-radius: 4px; background: var(--mark); }
  /* magnitude bar: div.bar containing an i element with an inline width percentage */
  .bar { position: relative; width: 9rem; max-width: 100%; height: 10px; border-radius: 0 4px 4px 0; background: var(--mark-track); margin-top: .4rem; overflow: hidden; }
  .bar i { position: absolute; left: 0; top: 0; height: 10px; border-radius: 0 4px 4px 0; background: var(--mark); }

  /* figures */
  figure { margin: 1.8rem 0; padding: 1.3rem 1.3rem 1rem; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
  figure svg { max-width: 100%; height: auto; display: block; margin: 0 auto; color: var(--ink); }
  figcaption { font-size: .85rem; color: var(--ink-2); margin-top: .9rem; line-height: 1.55; }
  figcaption b { color: var(--ink); }

  /* optional depth: a details element with a summary and a div.body */
  details { border: 1px solid var(--line); border-radius: 8px; margin: .6rem 0; background: var(--surface); }
  summary { cursor: pointer; padding: .7rem 1rem; font-weight: 600; font-size: .97rem; list-style: none; display: flex; align-items: baseline; gap: .6rem; }
  summary::before { content: "+"; font-family: "IBM Plex Mono", monospace; color: var(--accent-ink); }
  details[open] summary::before { content: "\2212"; }
  details .body { padding: 0 1rem .9rem; font-size: .95rem; color: var(--ink-2); }

  /* card grid for parallel lists */
  .cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); gap: 1.2rem; margin: 1.3rem 0; }
  .col-card { border: 1px solid var(--line); border-radius: 10px; background: var(--surface); padding: 1.1rem 1.2rem; }
  .col-card h4 { margin: 0 0 .6rem; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; color: var(--accent-ink); font-weight: 500; }
  .col-card ul { margin: 0; padding-left: 1.15em; font-size: .93rem; }

  /* sources */
  .refs { font-size: .9rem; }
  .refs li { margin-bottom: .7em; }
  .refs .j { color: var(--muted); font-style: italic; }
  footer.foot { padding: 2.5rem 0 3.5rem; color: var(--muted); font-size: .85rem; border-top: 1px solid var(--line); margin-top: 2rem; }
</style>
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <p class="eyebrow">Subject briefing</p>
    <h1>SUBJECT</h1>
    <p class="dek">One-sentence description of what the briefing covers and for whom.</p>
    <p class="meta">
      <span>Compiled MONTH YEAR</span>
      <span>Dotted terms: hover, tap, or focus for definitions</span>
      <span>Educational briefing, not [medical] advice</span>
    </p>
  </div>
</header>

<nav class="toc" aria-label="Sections">
  <div class="row">
    <a href="#overview">Overview</a>
    <a href="#mechanism">Mechanism</a>
    <a href="#sources">Sources</a>
  </div>
</nav>

<main>

<section class="block" id="overview">
  <div class="wrap">
    <p class="sec-eyebrow">Overview</p>
    <h2>Heading that states the point</h2>
    <div class="note">
      <span class="lab">In brief</span>
      <ul>
        <li>Complete claim one.</li>
        <li>Complete claim two.</li>
      </ul>
    </div>
    <p>Body text with a <span class="t" data-g="examplekey">marked term</span> and a
       cited claim (<a class="ext" href="https://doi.org/...">Author et al., 2020</a>).</p>

    <figure>
      <svg viewBox="0 0 740 300" role="img" aria-label="What the figure shows, in one sentence">
        <!-- inline SVG; use fill="currentColor" and style="fill:var(--mark)" for theme-aware color -->
      </svg>
      <figcaption><b>The takeaway in a few words.</b> One or two sentences explaining what to see.</figcaption>
    </figure>

    <div class="flag">
      <span class="lab">Must not miss</span>
      <p>The safety-critical or most-often-missed point.</p>
    </div>

    <div class="tablewrap">
      <table>
        <thead><tr><th>Item</th><th>Attribute</th><th>Range</th></tr></thead>
        <tbody>
          <tr><td>Row<span class="sub">qualifier</span></td><td>Value</td>
              <td><span class="num">45–90%</span><div class="rng"><i style="left:45%;width:45%"></i></div></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="block" id="sources">
  <div class="wrap">
    <p class="sec-eyebrow">Sources &amp; further reading</p>
    <h2>Where these claims come from</h2>
    <h3>Key primary literature</h3>
    <ol class="refs">
      <li>Author, A., et&nbsp;al. (2020). Title. <span class="j">Journal</span>. <a class="ext" href="https://doi.org/...">DOI</a> One line on what this source supports.</li>
    </ol>
    <h3>Reviews, guidelines, and accessible explainers</h3>
    <ul class="refs">
      <li><a class="ext" href="https://...">Title</a>, Publisher (year). Why it is worth the reader's time.</li>
    </ul>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <p>Compiled MONTH YEAR from the sources cited above. One or two sentences on the evidence base and its limits. Educational briefing, not [medical] advice.</p>
  </div>
</footer>

<div id="tip" hidden role="tooltip"></div>

<script type="application/json" id="glossary">
{}
</script>

<script>
(function () {
  "use strict";

  /* glossary: filled by make_glossary.py from glossary.json */
  var G = JSON.parse(document.getElementById("glossary").textContent || "{}");

  /* tooltip */
  var tip = document.getElementById("tip");
  var openEl = null;

  function place(el) {
    var r = el.getBoundingClientRect();
    tip.style.left = "0px"; tip.style.top = "0px";
    var tw = tip.offsetWidth, th = tip.offsetHeight;
    var left = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
    var top = r.top - th - 10;
    if (top < 8) top = r.bottom + 10;
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  }
  function show(el) {
    var g = G[el.getAttribute("data-g")];
    if (!g) return;
    tip.textContent = "";
    var b = document.createElement("b");
    b.textContent = g.term;
    tip.appendChild(b);
    tip.appendChild(document.createTextNode(g.definition));
    tip.hidden = false;
    place(el);
    openEl = el;
  }
  function hide() { tip.hidden = true; openEl = null; }

  document.querySelectorAll(".t").forEach(function (el) {
    var g = G[el.getAttribute("data-g")];
    if (!g) { console.warn("glossary key not defined:", el.getAttribute("data-g")); return; }
    el.tabIndex = 0;
    el.setAttribute("role", "button");
    el.setAttribute("aria-label", g.term + ": " + g.definition);
    el.addEventListener("mouseenter", function () { show(el); });
    el.addEventListener("mouseleave", hide);
    el.addEventListener("focus", function () { show(el); });
    el.addEventListener("blur", hide);
    el.addEventListener("click", function (e) {      /* touch: toggle */
      e.stopPropagation();
      if (openEl === el && !tip.hidden) hide(); else show(el);
    });
  });
  document.addEventListener("click", hide);
  window.addEventListener("scroll", function () { if (openEl) place(openEl); }, { passive: true });
  window.addEventListener("resize", hide);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(); });

  /* scrollspy for the navigator */
  var links = {};
  document.querySelectorAll("nav.toc a").forEach(function (a) {
    links[a.getAttribute("href").slice(1)] = a;
  });
  if ("IntersectionObserver" in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove("on"); });
          var l = links[en.target.id];
          if (l) l.classList.add("on");
        }
      });
    }, { rootMargin: "-35% 0px -55% 0px" });
    document.querySelectorAll("section.block").forEach(function (s) { spy.observe(s); });
  }
})();
</script>
</body>
</html>
```

### Checks

```sh
# Script syntax
sed -n '/^<script>$/,/^<\/script>$/p' <slug>.html | sed '1d;$d' > /tmp/briefing.js && node --check /tmp/briefing.js
# Markup, only if an HTML5-aware tidy is installed (brew install tidy-html5).
# The tidy that ships with macOS dates from 2006 and rejects <header>, <nav>, and <main>.
tidy -q -e -utf8 <slug>.html
```

Then open the file in a browser and confirm, in both light and dark mode:
tooltips appear on hover, focus, and tap and never run off-screen; the
navigator highlights as you scroll; every figure is legible; no horizontal
scroll at a 375 px width.

## 7. The PDF briefing

### Toolchain

- **Engine: LuaLaTeX, always.** Never pdflatex or XeLaTeX; `modern.sty` needs
  `fontspec`/`unicode-math`.
- **Style: `modern.sty`** from the tools repo, copied unmodified into
  the project directory. It supplies fonts, geometry, `microtype`, `biblatex`
  (Biber backend, `authoryear`, `natbib=true`), and `hyperref`.
- **Glossary: `glossaries-extra`** with `\makenoidxglossaries`, so no external
  indexer is needed; `latexmk` handles the reruns.
- **Marker:** every `\gls` in the body gets a dotted underline in the accent
  color (matching the HTML) and a hyperlink to its glossary entry. The
  glossary lists the pages on which each term is marked.
- **Build: `latexmk -lualatex`.** Line 1 of the `.tex` file is
  `% !TEX program = lualatex`.

### Skeleton

Every command below has been compiled together; keep the load order.

```latex
% !TEX program = lualatex
\documentclass[11pt, letterpaper]{article}

\usepackage{modern}                 % fonts, geometry, biblatex, hyperref (tools)
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning}
\usepackage[normalem]{ulem}         % \dotuline for the glossary marker
\usepackage[most]{tcolorbox}        % callout boxes

% modern.sty's heading font on macOS is Apple's Optima, which lacks the Central
% European glyphs named in microtype's generic character-inheritance list. If
% Optima is the first font microtype meets that has no family-specific settings
% (it is, in this title block), the build emits dozens of harmless "Unknown slot
% number of character" warnings. An empty inheritance list for the family
% prevents that; the line is inert when a different heading font is in use.
\DeclareCharacterInheritance{encoding=TU, family=Optima}{}

% Shared palette: the same values the HTML uses.
\definecolor{accent}{HTML}{0E6E6E}
\definecolor{coral}{HTML}{A8433B}
\definecolor{ink2}{HTML}{4E5A58}
\definecolor{muted}{HTML}{7C8683}
\definecolor{mark}{HTML}{00876F}

% Glossary. glossaries-extra must load after hyperref, which modern.sty loads.
\usepackage[nopostdot, nogroupskip, toc, section=section]{glossaries-extra}
\glssetcategoryattribute{general}{glossname}{firstuc}     % capitalize headwords in the glossary
\newcommand{\glossmark}[1]{{\color{accent}\dotuline{\textcolor{black}{#1}}}}
\glssetcategoryattribute{general}{textformat}{glossmark}  % marker on every \gls in the body
\setglossarystyle{altlist}
\renewcommand*{\glossaryentrynumbers}[1]{\ \textcolor{muted}{\footnotesize\textsf{p.~#1}}}
\makenoidxglossaries
\loadglsentries{glossary}           % glossary.tex, generated by make_glossary.py

% Callouts, mirroring the HTML .note and .flag components.
\newtcolorbox{note}[1][Note]{enhanced, colback=accent!8, colframe=accent!8,
  borderline west={2pt}{0pt}{accent}, arc=2pt, fonttitle=\sffamily\scriptsize\bfseries,
  coltitle=accent, title=\MakeUppercase{#1}, attach title to upper=\par}
\newtcolorbox{flag}[1][Caution]{enhanced, colback=coral!8, colframe=coral!8,
  borderline west={2pt}{0pt}{coral}, arc=2pt, fonttitle=\sffamily\scriptsize\bfseries,
  coltitle=coral, title=\MakeUppercase{#1}, attach title to upper=\par}

\addbibresource{references.bib}

\begin{document}

% Title block, mirroring the HTML masthead.
\begin{center}
  {\headingfont\LARGE\bfseries SUBJECT\par}\vspace{.7em}
  {\large\itshape One-sentence description of what the briefing covers and for whom.\par}\vspace{.7em}
  {\small\sffamily\color{muted}
   Compiled MONTH YEAR \quad\textperiodcentered\quad
   Dotted terms are defined in the glossary \quad\textperiodcentered\quad
   Educational briefing, not [medical] advice\par}
\end{center}
\vspace{1em}

\begin{note}[In brief]
\begin{itemize}
  \item Complete claim one.
  \item Complete claim two.
\end{itemize}
\end{note}

\tableofcontents

\section{Heading that states the point}
Body text with a \gls{examplekey} and a cited claim \citep{author2020}.

\begin{figure}[htbp]
\centering
\begin{tikzpicture}
  % same content and labels as the HTML SVG
\end{tikzpicture}
\caption{\textbf{The takeaway in a few words.} One or two sentences explaining what to see.}
\end{figure}

\begin{flag}[Must not miss]
The safety-critical or most-often-missed point.
\end{flag}

\begin{table}[htbp]
\centering\small
\begin{tabular}{@{}lll@{}}
\toprule
Item & Attribute & Range \\
\midrule
Row  & Value     & 45--90\% \\
\bottomrule
\end{tabular}
\caption{What the table compares, and the population or period it describes.}
\end{table}

\section{Sources and further reading}
\subsection*{Reviews, guidelines, and accessible explainers}
\begin{itemize}
  \item \href{https://...}{Title}, Publisher (year). Why it is worth the reader's time.
        \\ {\small\url{https://...}}
\end{itemize}
\printbibliography[heading=subbibintoc, title={Works cited}]

\printnoidxglossary[sort=word, title={Glossary}]   % last: the glossary closes the document

\end{document}
```

Notes on the skeleton:

- **Order at the end:** curated links, then the bibliography, then the
  glossary as the final element. A reader flipping to the back for a
  definition finds it there.
- **Links in print.** `\href` alone is invisible on paper. In the further
  reading section print the URL as well with `\url`, so the PDF is useful
  printed. Inline in the body, `\href{URL}{Author et al., 2020}` or a plain
  `\citep` is enough because the bibliography carries the DOI or URL.
- **Bibliography entries** carry `doi` or `url` fields, verified (Section 2).
- **No `\gls` inside** `\section`, `\caption`, `\footnote`, TikZ nodes, or
  table headers (Section 5).
- **Tables:** `booktabs` rules only, no vertical rules. Long tables scroll in
  the HTML but must fit the text width in the PDF; drop a column or split the
  table rather than shrink below `\small`.
- Read the log after building for `undefined` citations or glossary entries,
  `Overfull \hbox` lines wider than about 5 pt, and any `glossaries` or
  `microtype` warning. The skeleton builds with none.

### Build

```sh
python3 make_glossary.py <slug>      # glossary.tex + HTML injection + parity check
latexmk -lualatex <slug>.tex         # runs Biber and the glossary reruns automatically
```

The global `~/.latexmkrc` already selects LuaLaTeX and Biber; pass `-lualatex`
anyway so the build is portable.

## 8. Figures

### When a figure earns its place

Use a figure wherever a reader would otherwise have to build a mental picture
from prose:

- **Structure or mechanism**: parts and how they connect (anatomy, a market's
  plumbing, an algorithm's components).
- **Process, flow, or timeline**: steps, decision trees, the order in which
  things happen, how a disease or a crisis progresses.
- **Comparison or taxonomy**: what is spared versus affected, what falls
  under what, how alternatives differ.
- **Quantitative relationship**: a trend, a distribution, a dose-response
  curve, a set of performance ranges.

Expect one anchoring figure in the overview or mechanism section and one in
each further section whose content is visual. Every figure has a caption that
opens with the takeaway in bold ("**Why the exam can look normal.**") followed
by one or two sentences saying what to see. A figure that needs a paragraph
to explain is the wrong figure.

### Parity and provenance

Every figure appears in **both** formats with the same content, labels, and
caption. Each figure has its own directory `figures/<fig-slug>/` holding
whatever produced it: the plotting script and its data for a chart, the TikZ
source for a diagram, the SVG source. A reader of the PDF or HTML never sees
these paths; they are for the maintainer.

### Palette

Both formats draw from one palette so they read as one family:

| Role | Hex | HTML variable | LaTeX color |
| --- | --- | --- | --- |
| Data emphasis (the thing the figure is about) | `#00876F` | `--mark` | `mark` |
| Accent (rules, labels, callout bars) | `#0E6E6E` | `--accent` | `accent` |
| Warning or "affected" contrast | `#A8433B` | `--coral` | `coral` |
| Secondary text | `#4E5A58` | `--ink-2` | `ink2` |
| De-emphasized elements | `#7C8683` | `--muted` | `muted` |

Neutral structure (spared elements, baselines, axes) is the text color at
reduced opacity, never a second hue. One data hue plus one contrast hue is
almost always enough; if a figure needs more, it is probably two figures.

### HTML: inline SVG

- Inline `<svg viewBox="0 0 740 H" role="img" aria-label="…">` inside the
  `<figure>`; no `width`/`height` attributes, so the CSS scales it.
- Color with `fill="currentColor"` (plus `opacity` for de-emphasis) and with
  CSS variables via the style attribute, `style="fill:var(--mark)"`, so the
  figure follows light and dark themes. Never hard-code black or white.
- Text at 10.5 px or larger in a 740-unit-wide viewBox; the body font stack
  by default, the mono stack for measurement labels. No overlapping labels;
  check at phone width.
- Draw diagrams by hand in SVG. For data charts, generate the SVG from the
  same script that produces the PDF version (below) and paste it inline,
  removing the fixed `width`/`height` and keeping `viewBox`.

### PDF: TikZ and included PDFs

- **Diagrams in TikZ**, drawn to the same content and labels as the SVG, using
  the named palette colors. Keep the TikZ source in the figure's directory and
  `\input` it or paste it into the `figure` environment.
- **Data charts with `plotly`**, in a type-hinted script `make_fig.py` in the
  figure's directory that writes both `fig.pdf` (for `\includegraphics`) and
  `fig.svg` (for the HTML) through Kaleido, using the palette above and the
  document's fonts as far as Kaleido allows. Install with `pip install plotly
  kaleido` if absent.
- **Shortcut for an SVG diagram** when TikZ would be awkward: convert with
  `rsvg-convert -f pdf -o fig.pdf fig.svg`. Before converting, replace
  `currentColor` and `var(--…)` with literal palette hexes and use font
  families installed on the machine; librsvg does not resolve CSS variables
  and falls back silently on missing fonts. Inspect the result.

## 9. External resources

Links are part of the teaching: they tell the reader where to go next and let
them check the briefing's claims.

- **Where they appear.** Inline at the point of the claim (HTML: `<a
  class="ext" href="…">Author et al., 2020</a>`; PDF: `\citep{key}` or
  `\href`), and gathered in the *Sources and further reading* section in
  both formats, grouped as **Key primary literature**, **Reviews, guidelines,
  and accessible explainers**, and, where relevant, **Data, tools, and
  communities**. Each entry carries a one-line note on why it is worth the
  reader's time or which claim it supports.
- **Quality bar.** Prefer stable identifiers (DOI, PubMed, official
  publisher, institutional pages). Link the version of record, not a preprint,
  when both exist. Include at least one accessible entry point (a good review,
  a textbook chapter, an institutional explainer) alongside the primary
  literature, and at least one resource a practitioner would actually use
  (a calculator, a dataset, a guideline PDF, a community) where such a thing
  exists.
- **Verification.** Every URL fetched and confirmed before publication
  (Section 2). Search-results URLs are the honest fallback, labeled as such.
  Nothing paywalled is described as freely available.
- **Same set in both formats.** The HTML sources section and the PDF
  bibliography plus further-reading list contain the same works.

## 10. Workflow

1. **Scope.** Confirm the subject, audience, emphasis, and slug (Section 1).
   Copy `modern.sty` into the project directory.
2. **Research and outline.** Read sources, collect numbers with their
   provenance, and write the section outline with one sentence per section
   saying what the reader will be able to do afterward.
3. **Draft the content once**, in a scratch Markdown file that is not
   delivered, so that both formats are rendered from the same text. Add
   glossary entries to `glossary.json` as terms arise.
4. **Figures.** Decide the figure list from the outline; produce each in its
   directory for both formats (Section 8).
5. **Render the HTML** from the skeleton in Section 6; then **render the
   LaTeX** from the skeleton in Section 7. Mark the same terms in both.
6. **Generate and build.** `python3 make_glossary.py <slug>`, fix every line it
   prints, then `latexmk -lualatex <slug>.tex`. Run the HTML checks.
7. **Read both outputs as a reader would**, not as their author: open the
   HTML in light and dark mode and on a narrow window; page through the PDF.
8. **Write the README** and run the checklist below.

## 11. Pre-handoff checklist

1. Both deliverables exist and open: `<slug>.html` renders from disk with
   working tooltips, navigator, and figures in light and dark mode;
   `<slug>.pdf` built under LuaLaTeX with Biber, no undefined citations or
   glossary entries, and no overfull boxes wider than about 5 pt.
2. `make_glossary.py` reports a clean run: every key defined, and the same
   set of terms marked in HTML and LaTeX.
3. Every glossary definition is one to three sentences of plain text, correct,
   and self-contained; no term is marked inside a heading, caption, figure,
   table header, or the sources section.
4. The PDF glossary is the last element of the document, alphabetized, with
   capitalized headwords and page references; every marked term carries the
   dotted marker and links to its entry, and the first occurrence in each
   top-level section is marked in both formats.
5. Every number in the text traces to a listed source, with population,
   period, and method stated; disagreements between sources are reported as
   ranges; consensus, contested, and speculative claims are distinguished.
6. Every URL in either format has been fetched and resolves to the described
   work; no DOI, identifier, or URL was written from memory; search-results
   links are labeled as such; `references.bib` entries carry `doi` or `url`.
7. The same sections, figures (with identical captions), sources, and
   compilation date appear in both formats.
8. Every figure has a bold-lead caption, uses the shared palette, is legible
   at phone width (HTML) and at print size (PDF), and has its sources in
   `figures/<fig-slug>/`.
9. Prose follows Section 4: US spelling, Oxford comma, no em dashes,
   quantified hedging only, terms explained before use.
10. The README states subject, audience, date, the verbatim prompt, the build
    commands, and a "Verify" list of anything you could not confirm.
