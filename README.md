# Claude MCP Skills Server

A local MCP server that exposes Wayne's coaching and research skills as tools for Claude Code and the Claude desktop app.

## Architecture

```
Claude (desktop or CLI) ←→ stdio ←→ mcp_server.py ←→ skills/{name}/SKILL.md
```

Skills are auto-discovered from the `skills/` directory at server startup. Each folder containing a valid `SKILL.md` becomes a callable tool. No code changes are needed to add or remove skills — only a server restart.

---

## Setup

**1. Create virtual environment and install dependencies**
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**2. Register with Claude Code (CLI)**
```bash
claude mcp add wayne-skills -- "C:/Users/kenho/Projects/claude-mcp-skills-server/.venv/Scripts/python.exe" "C:/Users/kenho/Projects/claude-mcp-skills-server/mcp_server.py"
```
Use **forward slashes** — backslashes in the config JSON cause escape failures on Windows.

Verify with:
```bash
claude mcp list
# wayne-skills: ... ✓ Connected
```

**3. Register with Claude desktop app**

Add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "wayne-skills": {
      "command": "C:/Users/kenho/Projects/claude-mcp-skills-server/.venv/Scripts/python.exe",
      "args": ["C:/Users/kenho/Projects/claude-mcp-skills-server/mcp_server.py"]
    }
  }
}
```
Restart the desktop app after saving. Skills appear under the tools (plug) icon in the chat input bar.

---

## Current Skills

| Tool name | Description |
|-----------|-------------|
| `invoke_stoic_reflection_coach` | Stoic philosophical coaching persona |
| `invoke_rugby_session_planning_coach` | Rugby session planning coaching persona |
| `invoke_youtube_search` | Search YouTube via yt-dlp with ranked results |
| `invoke_notebooklm` | Full NotebookLM API — create notebooks, podcasts, briefings |

---

## Invoking Skills

### Claude Code (CLI)

**Natural language** — Claude will call the right tool automatically:
> *"Activate the stoic reflection coach"*
> *"Search YouTube for talks on stoicism"*

**Direct slash command:**
```
/mcp__wayne-skills__invoke_stoic_reflection_coach
/mcp__wayne-skills__invoke_youtube_search
/mcp__wayne-skills__invoke_notebooklm
/mcp__wayne-skills__invoke_rugby_session_planning_coach
```

### Claude desktop app

Use natural language — the assistant picks up the tool from context. You can also click the plug icon in the chat input bar to browse and invoke tools manually.

---

## Editing Skills

Skill content is read **fresh on every tool call** — edits take effect immediately without restarting the server.

| Skill | File location |
|-------|--------------|
| `stoic-reflection-coach` | `skills/stoic-reflection-coach/SKILL.md` |
| `rugby-session-planning-coach` | `skills/rugby-session-planning-coach/SKILL.md` |
| `youtube-search` | `C:\Users\kenho\.claude\skills\youtube-search\SKILL.md` (source) |
| `notebooklm` | `C:\Users\kenho\.claude\skills\notebooklm\SKILL.md` (source) |

`youtube-search` and `notebooklm` are junction-linked from `~/.claude/skills/` — edit the source files there, not inside this repo.

The `name` and `description` frontmatter fields are only read at **startup**. Changing them requires a server restart to take effect.

---

## Adding New Skills

### Option A — Self-contained skill (lives in this repo)

1. Create `skills/{your-skill-name}/SKILL.md` with valid frontmatter:
```markdown
---
name: your-skill-name
description: One-line description shown to Claude as the tool description.
---

Your skill content here...
```
2. Restart the MCP server (Claude Code: `claude mcp restart wayne-skills`; desktop app: restart the app).

### Option B — Linked skill (source lives elsewhere)

Use a junction so the skill is maintained in its source location:
```python
import subprocess
subprocess.run([
    'cmd.exe', '/c', 'mklink', '/J',
    r'skills\your-skill-name',
    r'C:\path\to\source\your-skill-name'
])
```
Then add the folder to `.gitignore`:
```
skills/your-skill-name/
```
Restart the server to register the new tool.

### Tool naming

The folder name is irrelevant — the tool name is derived from the `name` field in frontmatter:
- Lowercased, spaces and hyphens → underscores
- Non-alphanumeric characters stripped
- Prefixed with `invoke_`

Example: `name: My Skill` → tool `invoke_my_skill`

Folders without a `SKILL.md`, or with missing/invalid `name` frontmatter, are skipped with a warning at startup.
