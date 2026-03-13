# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Set up
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -r requirements.txt

# Verify server starts and registers tools correctly
python -c "import mcp_server"

# Run server (stays open on stdio — Ctrl+C to stop)
python mcp_server.py

# Re-register with Claude Code (use venv Python and forward slashes)
claude mcp add wayne-skills -- "C:/Users/kenho/Projects/claude-mcp-skills-server/.venv/Scripts/python.exe" "C:/Users/kenho/Projects/claude-mcp-skills-server/mcp_server.py"

# Check registration
claude mcp list
```

## Architecture

Single-file FastMCP server (`mcp_server.py`) over stdio transport. At import time it scans `./skills/` and dynamically registers one MCP tool per discovered skill — no code changes needed to add a skill.

**Startup flow:** `register_skill_tools()` → `discover_skills()` → reads each `SKILL.md` → `parse_frontmatter()` extracts `name`/`description` → tool name becomes `invoke_<sanitized_name>` → registered via `mcp.tool(name=..., description=...)`.

**Tool call flow:** When Claude invokes a skill tool, the handler re-reads `SKILL.md` fresh (so edits take effect without restart), strips frontmatter, wraps the body in a persona-activation prompt, and returns it as a string.

## Skill File Format

Each skill lives at `skills/<folder-name>/SKILL.md`. The frontmatter must include:

```yaml
---
name: my-skill-name        # becomes invoke_my_skill_name
description: One-liner     # shown to Claude as the tool description
---
```

The body (everything after `---`) is returned verbatim as the coaching persona content. Only `SKILL.md` is loaded; any `Resources/` or `references/` subdirectories are ignored.

**Tool naming:** `name` is lowercased, spaces/hyphens → underscores, non-alphanumeric chars stripped, prefixed with `invoke_`. Invalid names are skipped with a warning at startup.

## MCP Registration Note

The `claude mcp add` command stores config in `~/.claude.json` scoped to this project. Use absolute paths with forward slashes on Windows — backslashes cause JSON escape failures. Always use the `.venv` Python so the `mcp` package is on the path.
