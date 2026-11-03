# Working-paper and report series — canonical forms

Use with the rule in SKILL.md: **a numbered paper in an institutional series is
`@techreport`**, with `institution` = the body, `type` = the series name as the body
brands it, `number` = the series number. Never `@article` with the series stuffed into
`journal`.

Why it matters — the same paper rendered in APA both ways:

```
@article form:     … Inequality of opportunity and economic growth.
                   World Bank Policy Research Working Paper, (6915).
@techreport form:  … Inequality of opportunity and economic growth
                   (Policy Research Working Paper No. 6915). World Bank.
```

The table leans toward economics and central banking because that is where it was
built. Add rows for the bodies you meet — the "DOI" column is the expensive knowledge.

| Publisher | `institution` | `type` | `number` example | DOI | Notes |
|---|---|---|---|---|---|
| NBER | `National Bureau of Economic Research` | `Working Paper` | `23583` | `10.3386/w<number>` | |
| World Bank | `World Bank` | `Policy Research Working Paper` | `6915` | `10.1596/*`, search per item | |
| World Bank (Economic Premise) | `World Bank` | `Economic Premise` | `137` | search per item | RePEc's `wbk:prmecp:ep<N>` handle can be off by one from the printed number |
| Commission on Growth and Development | `World Bank` | `Commission on Growth and Development Working Paper` | `4` | `10.1596/<id>` | registered by the World Bank, not the Commission — find via title search |
| IMF (working paper) | `International Monetary Fund` | `IMF Working Paper` | `WP/10/285` | `10.5089/*` | always has one; imf.org blocks bots, get it from Crossref |
| IMF (WEO chapter) | `International Monetary Fund` | `World Economic Outlook` | — | | use `month` + `pages` |
| BIS | `Bank for International Settlements` | `BIS Working Papers` | `227` | **none exist** | not a Crossref member; pages carry `citation_title`/`citation_author` but no `citation_doi` |
| ECB | `European Central Bank` | `ECB Working Paper Series` | `1039` | **none exist** | not a Crossref member; only SSRN mirrors show up |
| Bank of England | `Bank of England` | `Working Paper` | `248` | **none exist** | only an SSRN mirror shows up |
| Central Bank of Chile | `Central Bank of Chile` | `Working Papers` | `315` | **none exist** | |
| FRB Minneapolis | `Federal Reserve Bank of Minneapolis` | `Working Paper` | `706` | `10.21034/wp.<number>` | staff reports are `10.21034/sr.<number>` |
| Cowles Foundation | `Cowles Foundation for Research in Economics, Yale University` | `Cowles Foundation Paper` | `190` | **none exist** | reprint series; cite without pages |
| Bank of Thailand | `Bank of Thailand` | `Discussion Paper` | `07/2014` | | symposium papers: `type = {Symposium Paper}`, no number |
| PIER | `Puey Ungphakorn Institute for Economic Research` | `Discussion Paper` | `4` | **none exist** | add `url = {https://www.pier.or.th/dp/<NNN>/}` |

"**none exist**" means the body does not register DOIs — a title search that comes back
with only an SSRN mirror or a later journal article is expected, not a miss.

Cosmetic quirk: citeproc-based renderers show a `number` containing a dash as "Nos."
(`2005-076` → `Working Paper Nos. 2005–076`). Not worth working around.
