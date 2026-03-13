# Claude MCP Skills Server

A local MCP server that exposes Wayne's coaching skills as tools for Claude Code.

## Architecture

```
Claude Code ←→ stdio ←→ mcp_server.py ←→ skills/{name}/SKILL.md
```

Skills are auto-discovered from the `skills/` directory. Each folder with a valid `SKILL.md` becomes a callable tool.

## Setup

**1. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Connect to Claude Code**
```bash
claude mcp add wayne-skills -- python mcp_server.py
```
Run from the project root. Verify with:
```bash
claude mcp list
```

## Adding New Skills

1. Create `skills/{your-skill-name}/SKILL.md`
2. Ensure frontmatter includes `name:` and `description:`
3. Restart the MCP server

Claude Code will pick up the new tool on next session start.

## Current Skills

| Tool | Description |
|------|-------------|
| `invoke_stoic_reflection_coach` | Stoic philosophical coaching persona |
| `invoke_rugby_session_planning_coach` | Rugby session planning coaching persona |

## Usage in Claude Code

Ask Claude: *"Activate the stoic reflection coach"*
Or invoke directly: `/mcp__wayne-skills__invoke_stoic_reflection_coach`
