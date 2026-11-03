# agent-skills

Agent skills from [PIER](https://www.pier.or.th/). Each folder under `skills/` is a
self-contained skill in the open Agent Skills format (`SKILL.md` + scripts + references),
usable from Claude Code, GitHub Copilot, Gemini CLI and other agents that read skills.

## Skills

| Skill | What it does |
|---|---|
| [`reference-to-bibtex`](skills/reference-to-bibtex/) | Converts free-text references into BibTeX, verifying each against Crossref, doi.org and the publisher's page, and reporting where the original reference was wrong. |

## Install

Scripts need Python 3 (standard library only; on Windows, `py` or `python`). Set
`CROSSREF_MAILTO` to your own email to use Crossref's polite pool; nothing is sent
unless you set it.

### Claude Code

This repo is a plugin marketplace:

```
/plugin marketplace add pier-x/agent-skills
/plugin install citations@pier-x
```

Update with `/plugin marketplace update pier-x`, or enable auto-update for the
marketplace in the `/plugin` menu.

### VS Code (GitHub Copilot) — as a plugin marketplace

VS Code can install from Claude Code-format marketplaces. This is experimental in
VS Code and not yet tested with this repo. In your user `settings.json`:

```json
"chat.plugins.enabled": true,
"chat.plugins.marketplaces": ["pier-x/agent-skills"]
```

Then open the Agent Customizations editor → **Browse** → install `citations`. Update
with **Chat: Update Plugins**. If this route doesn't work for you, use the Git install
below.

### Any agent — Git clone, kept up to date with `git pull`

Agents look for skills in a *skills root*, laid out as `<skills-root>/<name>/SKILL.md`.
This repo keeps its skills one level down, in `skills/<name>/`, so clone it somewhere
of your own and **link** each skill into your agent's personal skills root.

Personal skills roots:

| Agent | Folder |
|---|---|
| GitHub Copilot (VS Code, CLI) | `~/.copilot/skills` |
| Shared across agents that read it (incl. VS Code local sessions) | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` (or use the marketplace above) |

Check your agent's documentation if it isn't listed.

**macOS / Linux**

```sh
git clone https://github.com/pier-x/agent-skills ~/pier-agent-skills

SKILLS_ROOT=~/.copilot/skills          # pick from the table
mkdir -p "$SKILLS_ROOT"
for d in ~/pier-agent-skills/skills/*/; do
  ln -sfn "$d" "$SKILLS_ROOT/$(basename "$d")"
done
```

**Windows (PowerShell)** — uses directory junctions, which need no admin rights or
Developer Mode:

```powershell
git clone https://github.com/pier-x/agent-skills "$HOME\pier-agent-skills"

$SkillsRoot = "$HOME\.copilot\skills"   # pick from the table
New-Item -ItemType Directory -Force $SkillsRoot | Out-Null
Get-ChildItem "$HOME\pier-agent-skills\skills" -Directory | ForEach-Object {
  $link = Join-Path $SkillsRoot $_.Name
  if (-not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null }
}
```

**Updating** — this updates every linked skill in place:

```sh
git -C ~/pier-agent-skills pull               # macOS / Linux
```

```powershell
git -C "$HOME\pier-agent-skills" pull         # Windows (PowerShell)
```

Re-run the link loop only when a new skill is added to the repo, to link it too.

Why clone outside the skills root rather than into it: a clone at
`~/.copilot/skills/agent-skills` would itself look like a (broken) skill folder with
no `SKILL.md`, and its skills would sit one level too deep to be found.

**VS Code only — point a setting at the clone instead of linking.** VS Code has a
`chat.agentSkillsLocations` setting that can name `~/pier-agent-skills/skills` directly, so
no links are needed. It is supported, but it is an editor setting: GitHub Copilot CLI and
the GitHub Copilot app do not inherit it. VS Code's docs recommend native folders, so use
the links above if you use Copilot outside the editor.

**Not keeping it updated?** Copying a single folder works too, e.g. into a project's
`.github/skills/` — but that copy never updates.

## Tested with

- Claude Code

## Contributing

One skill per folder under `skills/`, and each folder must work on its own — no imports
or references outside it. When adding a skill, also add it to a plugin's `skills` list in
`.claude-plugin/marketplace.json`.

## License

[MIT](LICENSE)
