# agent-skills

Agent skills from [PIER](https://www.pier.or.th/). Each top-level folder is a
self-contained skill in the open Agent Skills format (`SKILL.md` + scripts + references),
usable from Claude Code, GitHub Copilot, Gemini CLI and other agents that read skills.

## Skills

| Skill | What it does |
|---|---|
| [`reference-to-bibtex`](reference-to-bibtex/) | Converts free-text references into BibTeX, verifying each against Crossref, doi.org and the publisher's page, and reporting where the original reference was wrong. |

## Install

Scripts need Python 3 (standard library only; on Windows, `py` or `python`). Set
`CROSSREF_MAILTO` to your own email to use Crossref's polite pool; nothing is sent
unless you set it.

Agents look for skills in a *skills root*, laid out as `<skills-root>/<name>/SKILL.md`.
This repo has that layout, so a clone of it is itself a skills root. Updating is a
`git pull`.

Personal skills roots:

| Agent | Folder |
|---|---|
| Claude Code | `~/.claude/skills` |
| GitHub Copilot (VS Code, CLI) | `~/.copilot/skills` |
| Shared across agents that read it (incl. VS Code local sessions) | `~/.agents/skills` |

Check your agent's documentation if it isn't listed.

### Option A — clone straight into a skills root

Simplest, if that folder doesn't exist yet or is empty (it must hold only this repo):

```sh
git clone https://github.com/pier-x/agent-skills ~/.copilot/skills              # macOS / Linux
```

```powershell
git clone https://github.com/pier-x/agent-skills "$HOME\.copilot\skills"        # Windows
```

New skills appear on the next `git pull`; nothing else to do.

### Option B — clone elsewhere and link

Use this if the skills root already has other skills in it, or to feed several agents
from one clone.

**macOS / Linux**

```sh
git clone https://github.com/pier-x/agent-skills ~/pier-agent-skills

SKILLS_ROOT=~/.claude/skills           # pick from the table
mkdir -p "$SKILLS_ROOT"
for d in ~/pier-agent-skills/*/; do
  [ -f "$d/SKILL.md" ] && ln -sfn "$d" "$SKILLS_ROOT/$(basename "$d")"
done
```

**Windows (PowerShell)** — uses directory junctions, which need no admin rights or
Developer Mode:

```powershell
git clone https://github.com/pier-x/agent-skills "$HOME\pier-agent-skills"

$SkillsRoot = "$HOME\.copilot\skills"   # pick from the table
New-Item -ItemType Directory -Force $SkillsRoot | Out-Null
Get-ChildItem "$HOME\pier-agent-skills" -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
  ForEach-Object {
    $link = Join-Path $SkillsRoot $_.Name
    if (-not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $_.FullName | Out-Null }
  }
```

Using more than one agent? Run the loop once per skills root. Re-run it when a new
skill is added to the repo, to link that one too.

**VS Code only — point a setting at the clone instead of linking.** VS Code's
`chat.agentSkillsLocations` setting can name `~/pier-agent-skills` directly. It is
supported, but it is an editor setting: GitHub Copilot CLI and the GitHub Copilot app do
not inherit it, so use Option A or B if you use Copilot outside the editor.

### Updating

```sh
git -C ~/pier-agent-skills pull               # macOS / Linux (or the Option A folder)
```

```powershell
git -C "$HOME\pier-agent-skills" pull         # Windows (or the Option A folder)
```

**Not keeping it updated?** Copying a single skill folder works too, e.g. into a
project's `.github/skills/` — but that copy never updates.

## Tested with

- Claude Code

## Contributing

One skill per top-level folder, and each folder must work on its own — no imports or
references outside it. Add a row to the Skills table above.

## License

[MIT](LICENSE)
