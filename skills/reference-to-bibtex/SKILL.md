---
name: reference-to-bibtex
description: Convert free-text references (an APA/Chicago/etc. reference list, a pasted citation, a "References" section of a paper) into verified BibTeX entries. Looks each work up in Crossref, doi.org and the publisher's own page rather than trusting the text, records where metadata came from, and reports discrepancies between the original reference and the verified record. Use when asked to make a .bib from references, convert citations to BibTeX, or build a bibliography from a reference list.
---

# Reference text → BibTeX

**The reference text is a lead, not a citation.** Reference lists are typed by hand and
are wrong often enough — misspelled authors, wrong years, a working paper dated by its
later journal version — that they cannot be transcribed as-is. Get the metadata from an
authoritative record, then check the original against it.

**Never fill a field from memory.** Every field comes from a fetched record or from the
reference text itself. If neither has it, leave it out and say so. A plausible-looking
volume number you did not fetch is worse than a missing one.

## Inputs and outputs

- **In:** one or more references as text, in any style or language.
- **Out:**
  1. BibTeX entries, each preceded by a `% source:` comment saying where the metadata
     came from (BibTeX parsers ignore `%` lines).
  2. A short report to the user: entries whose original reference disagreed with the
     verified record, entries that could not be verified, and every DOI/URL added that
     was not in the original text.

## Modes

Ask which the user wants if it is not clear from context; default to **enrich**.

- **enrich** (default) — add a `doi` (or `url` when no DOI exists) when the match is
  certain: same title, same authors, same year, same kind of work. List every added
  locator in the report so a person can confirm it.
- **strict** — transcribe and verify only. Do not add locators the original did not
  have; flag entries that lack one. Use this when a project has decided a human must
  choose locators.

## Tools

`scripts/bibtools.py` (Python 3, standard library only) does the mechanical work.
Run it with the skill directory's path. On Windows the interpreter is usually `py` or
`python`, not `python3`:

```
python3 scripts/bibtools.py search "<title + authors + year>" [--rows 3]   # Crossref candidates as JSON
python3 scripts/bibtools.py bibtex <doi>                                    # DOI -> normalized BibTeX
python3 scripts/bibtools.py meta <landing-page-url>                         # citation_* meta tags + DOIs in page source
python3 scripts/bibtools.py normalize [file]                                # normalize BibTeX from file/stdin
```

If you cannot run scripts, the same requests work by hand: the Crossref URL is
`https://api.crossref.org/works?rows=3&query.bibliographic=<url-encoded text>`, and a DOI's
BibTeX is a GET to `https://doi.org/<doi>` with header `Accept: application/x-bibtex`.

## Procedure, per reference

**1. DOI in the text → fetch it.** `bibtools.py bibtex <doi>`. That is authoritative;
go to step 5.

**2. No DOI → search Crossref by title before concluding there isn't one.** Reference
lists rarely print DOIs, and many institutional working papers have one (IMF
`10.5089/*`, NBER `10.3386/w<number>`). Run `search` with title + first author + year.
Accept a candidate only if title, authors, year and **type** all agree with the text.
Two traps:

- **SSRN mirror DOIs (`10.2139/ssrn.*`) are not the publisher's version.** The script
  flags them (`"ssrn_mirror": true`). Cite the institutional series instead and leave
  the DOI off rather than pointing at the mirror.
- **A working paper's later journal version is a different work.** Crossref will
  happily return it. If the reference cites the working paper, cite the working paper —
  different year, often a different title, and results may have changed. Do not promote
  the entry to the journal version.

Crossref records for institutional series are often thin (corporate author only, no
pages). Take what they confirm and fill the rest from step 3, saying so in the comment.

**3. Still nothing → find the publisher's own page** for the work (search the exact title)
and use its "Cite" / "Export citation" / `.bib` download. Publisher metadata beats
Google Scholar and beats the reference text. Then run `meta <url>`: most journal and
institutional pages emit `citation_doi` (and title/authors/date) in the page source even
when no DOI is visible.

- Match on the meta *name*, not on attribute layout — sites write
  `<meta content='…' name='citation_title'>` with content first and single quotes. The
  script already handles this; keep it in mind if you grep by hand.
- **No `citation_doi` tag is not proof there is no DOI** unless the step-2 title search
  also came back empty. Do not use a Crossref *members* lookup as a shortcut: the series
  name is often not the registering body (the Commission on Growth and Development has
  no membership; its papers are World Bank DOIs under `10.1596`).

**4. Publisher page unavailable** → use the best other source — RePEc
(`ideas.repec.org`), the institution's series listing, the PDF's cover page, an archived
copy — and name it in the comment:

```bibtex
% source: publisher page unavailable; metadata from RePEc
@techreport{wang2005inflation,
```

**Blocked sites.** Some publishers (imf.org, SSRN, Wiley, MIT Press Direct, other
Cloudflare-fronted platforms) return 403 to scripts. That is not a reason to fall back to
the reference text. In order: Crossref (needs no publisher access), the PDF itself
(`pdftotext -f 1 -l 2`; for scans, render a page to an image and read it), then RePEc.
The DOI is often already in the landing-page URL.

**5. Cross-check against the original reference.** If they disagree, the verified record
wins — but **keep the disagreement visible**: a `%` comment above the entry and a line in
the report. Never silently "fix" the author's reference.

```bibtex
% original says 2006; the FRB St. Louis working paper is 2005 (2005-076)
@techreport{wang2005inflation,
```

If the verified record turns out to be a *different work* from what the text describes
(not just a typo), stop and ask rather than choosing.

**6. Unverifiable** → transcribe from the text, mark it `% source: unverified — transcribed
from reference text`, and list it in the report. Grey literature, older non-English works
and local-language publications are often absent from Crossref; this outcome is normal for
them, not a failure.

## Normalization

`bibtools.py bibtex` and `normalize` apply these automatically; apply them by hand
otherwise:

- Pages use `--`: `pages = {524--535}`.
- Month is the full name: `month = {August}`.
- Drop `abstract`, `keywords`, `issn`, `isbn`, `file`.
- When a `doi` is present, drop `url` — the DOI is the durable locator.
- `doi` holds the bare DOI, not a `https://doi.org/` URL.
- `@report` → `@techreport`.

By hand only:

- **Authors** as `Last, First and Last, First`. Corporate authors take double braces so
  they are not split into first/last names: `author = {{International Monetary Fund}}`.
- **Surname particles** take braces: `Eddy {van Doorslaer}`.
- **Same person, one spelling.** If two entries write one author differently
  (`Felkner, John S.` / `Felkner, John`), sorting and year-disambiguation treat them as two
  people. Use the fuller form consistently and mention it.
- Keep title capitalization as published; brace proper nouns and acronyms if the target
  style lowercases titles (`{Thailand}`, `{GDP}`).

## Working papers and reports

Google Scholar and many reference managers export working papers as `@article` with the
series name in `journal`. **A numbered paper in an institutional series is
`@techreport`**: `institution` = the body, `type` = the series as the body brands it,
`number` = the series number. See `references/series-table.md` for canonical forms of
common series and which bodies do or do not register DOIs.

## Citekeys

Default to Google Scholar style **`lastnameYYYYfirstword`** (lowercase, first author's
surname, year, first significant title word): `ciccarelli2010global`. The key follows the
*verified* year, not the reference text's. If the user's project has its own key
convention, follow it instead.

## Stop and ask

- The verified record appears to be a different work, not a corrected version of the same one.
- Several candidates match equally well (same title, different years or venues).
- The user asked for strict mode and a reference has no locator — flag it; do not search
  one out.
