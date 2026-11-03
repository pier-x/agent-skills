#!/usr/bin/env python3
"""Mechanical helpers for turning reference text into verified BibTeX.

Standard library only. Every subcommand prints to stdout; errors go to stderr
with a non-zero exit code.

  search  "<reference text>" [--rows N]   Crossref bibliographic search -> JSON candidates
  bibtex  <doi>                           DOI -> normalized BibTeX (from doi.org)
  meta    <url>                           scrape citation_* / DC meta tags from a landing page
  normalize [file]                        normalize BibTeX from a file or stdin

Set CROSSREF_MAILTO to an address of your own to use Crossref's polite pool.
The script never sends one unless you set it.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA_API = "agent-skills-reference-to-bibtex/0.1 (+https://github.com/pier-x/agent-skills)"
UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
TIMEOUT = 30

MONTHS = {
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "may": "May", "jun": "June", "jul": "July", "aug": "August",
    "sep": "September", "oct": "October", "nov": "November", "dec": "December",
}
DROP_FIELDS = {"abstract", "keywords", "issn", "isbn", "file", "mendeley-tags", "annote"}


def fetch(url: str, accept: str | None = None, browser: bool = False) -> str:
    headers = {"User-Agent": UA_BROWSER if browser else UA_API}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


# ---------------------------------------------------------------- search

def cmd_search(text: str, rows: int) -> None:
    params = {"query.bibliographic": text, "rows": str(rows)}
    if os.environ.get("CROSSREF_MAILTO"):
        params["mailto"] = os.environ["CROSSREF_MAILTO"]
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = json.loads(fetch(url))
    out = []
    for it in data.get("message", {}).get("items", []):
        date = (it.get("issued") or {}).get("date-parts") or [[None]]
        authors = [
            ", ".join(p for p in (a.get("family"), a.get("given")) if p) or a.get("name", "")
            for a in it.get("author", [])
        ]
        out.append({
            "doi": it.get("DOI"),
            "score": it.get("score"),
            "type": it.get("type"),
            "title": (it.get("title") or [""])[0],
            "authors": authors,
            "year": date[0][0] if date and date[0] else None,
            "container": (it.get("container-title") or [""])[0],
            "publisher": it.get("publisher"),
            "number": it.get("number") or it.get("issue"),
            "ssrn_mirror": (it.get("DOI") or "").lower().startswith("10.2139/ssrn"),
        })
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


# ---------------------------------------------------------------- meta

META_RE = re.compile(r"<meta\b[^>]*>", re.I)
ATTR_RE = re.compile(r"""([a-zA-Z:_-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]{3,80}")


def cmd_meta(url: str) -> None:
    page = fetch(url, browser=True)
    tags: dict[str, list[str]] = {}
    for m in META_RE.finditer(page):
        attrs = {}
        for a in ATTR_RE.finditer(m.group(0)):
            attrs[a.group(1).lower()] = a.group(3) or a.group(4) or a.group(5) or ""
        # Attribute order and quoting vary by platform, so key on the
        # name/property value, never on a fixed attribute layout.
        key = (attrs.get("name") or attrs.get("property") or "").lower()
        if key.startswith(("citation_", "dc.", "dcterms.", "prism.", "og:title")):
            tags.setdefault(key, []).append(html.unescape(attrs.get("content", "")))
    dois = sorted({d.rstrip(".,;)") for d in DOI_RE.findall(page)})
    json.dump({"url": url, "meta": tags, "dois_in_source": dois}, sys.stdout,
              ensure_ascii=False, indent=2)
    print()


# ---------------------------------------------------------------- bibtex

def split_entries(text: str) -> list[tuple[str, str]]:
    """Return [(leading_comments, entry_text)] using brace matching."""
    out, i, pending = [], 0, ""
    while i < len(text):
        at = text.find("@", i)
        if at < 0:
            break
        pending += text[i:at]
        brace = text.find("{", at)
        if brace < 0:
            break
        depth, j = 0, brace
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((pending, text[at:j + 1]))
        pending, i = "", j + 1
    return out


def parse_entry(entry: str) -> tuple[str, str, list[tuple[str, str]]]:
    m = re.match(r"@(\w+)\s*\{\s*([^,\s]*)\s*,", entry)
    if not m:
        raise ValueError(f"cannot parse entry head: {entry[:60]!r}")
    etype, key = m.group(1), m.group(2)
    body, i, fields = entry[m.end():-1], 0, []
    while i < len(body):
        fm = re.match(r"\s*,?\s*([\w-]+)\s*=\s*", body[i:])
        if not fm:
            break
        name = fm.group(1).lower()
        i += fm.end()
        if i < len(body) and body[i] == "{":
            depth, j = 0, i
            while j < len(body):
                depth += body[j] == "{"
                depth -= body[j] == "}"
                if depth == 0:
                    break
                j += 1
            value, i = body[i + 1:j], j + 1
        elif i < len(body) and body[i] == '"':
            j = body.index('"', i + 1)
            value, i = body[i + 1:j], j + 1
        else:
            vm = re.match(r"[^,}\s]+", body[i:])
            value = vm.group(0) if vm else ""
            i += len(value)
        fields.append((name, " ".join(value.split())))
    return etype, key, fields


def normalize_entry(entry: str) -> str:
    etype, key, fields = parse_entry(entry)
    etype = etype.lower()
    if etype in ("report", "techreport"):
        etype = "techreport"
    d = dict(fields)
    out = []
    for name, value in fields:
        if name in DROP_FIELDS:
            continue
        if name == "url" and "doi" in d:
            continue  # DOI is the durable locator; drop the redundant URL
        if name == "pages":
            value = re.sub(r"\s*(--|–|—|-)\s*", "--", value)
        if name == "month":
            value = MONTHS.get(value.strip().lower()[:3], value)
        if name == "doi":
            value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.I)
        out.append((name, value))
    width = max((len(n) for n, _ in out), default=0)
    lines = [f"  {n.ljust(width)} = {{{v}}}" for n, v in out]
    return f"@{etype}{{{key},\n" + ",\n".join(lines) + "\n}"


def normalize_text(text: str) -> str:
    parts = []
    for comments, entry in split_entries(text):
        c = comments.strip()
        parts.append((c + "\n" if c else "") + normalize_entry(entry))
    return "\n\n".join(parts) + "\n"


def cmd_bibtex(doi: str) -> None:
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip(), flags=re.I)
    raw = fetch("https://doi.org/" + urllib.parse.quote(doi, safe="/:;()"),
                accept="application/x-bibtex; charset=utf-8")
    if "@" not in raw:
        sys.exit(f"doi.org returned no BibTeX for {doi}")
    sys.stdout.write(f"% source: doi.org content negotiation for {doi}\n")
    sys.stdout.write(normalize_text(raw))


def cmd_normalize(path: str | None) -> None:
    text = open(path, encoding="utf-8").read() if path else sys.stdin.read()
    sys.stdout.write(normalize_text(text))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("text"); s.add_argument("--rows", type=int, default=3)
    b = sub.add_parser("bibtex"); b.add_argument("doi")
    m = sub.add_parser("meta"); m.add_argument("url")
    n = sub.add_parser("normalize"); n.add_argument("file", nargs="?")
    a = p.parse_args()
    # Windows consoles default to a legacy code page; names like "Benoît" or Thai
    # titles would raise UnicodeEncodeError without this.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        if a.cmd == "search":
            cmd_search(a.text, a.rows)
        elif a.cmd == "bibtex":
            cmd_bibtex(a.doi)
        elif a.cmd == "meta":
            cmd_meta(a.url)
        else:
            cmd_normalize(a.file)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} for {e.url} — the site may block automated fetches; "
                 "see SKILL.md 'Blocked sites'")
    except urllib.error.URLError as e:
        sys.exit(f"network error: {e.reason}")


if __name__ == "__main__":
    main()
