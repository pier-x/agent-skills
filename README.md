# agent-skills

Agent skills from [PIER](https://www.pier.or.th/). Each folder under `skills/` is a
self-contained skill in the open Agent Skills format (`SKILL.md` + scripts + references),
usable from Claude Code, GitHub Copilot, Gemini CLI and other agents that read skills.

## Skills

| Skill | What it does |
|---|---|
| [`reference-to-bibtex`](skills/reference-to-bibtex/) | Converts free-text references into BibTeX, verifying each against Crossref, doi.org and the publisher's page, and reporting where the original reference was wrong. |

## Install

**Claude Code** — this repo is a plugin marketplace:

```
/plugin marketplace add pier-x/agent-skills
/plugin install citations@pier-x
```

**Any other agent** — copy (or symlink) the skill folder into your agent's skills
directory, e.g. for GitHub Copilot:

```
git clone https://github.com/pier-x/agent-skills
cp -r agent-skills/skills/reference-to-bibtex .github/skills/
```

Check your agent's documentation for its skills directory.

Scripts need Python 3 (standard library only). Set `CROSSREF_MAILTO` to your own email
to use Crossref's polite pool; nothing is sent unless you set it.

## Tested with

- Claude Code

## Contributing

One skill per folder under `skills/`, and each folder must work on its own — no imports
or references outside it. When adding a skill, also add it to a plugin's `skills` list in
`.claude-plugin/marketplace.json`.

## License

[MIT](LICENSE)
