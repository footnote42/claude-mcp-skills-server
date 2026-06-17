# claude-mcp-skills-server

A local [Model Context Protocol](https://modelcontextprotocol.io/) server that extends Claude Code and the Claude desktop app with custom skills — coaching personas, research pipelines, and tool integrations — without touching a line of application code.

Built and maintained using vibe-coding methodology: Claude Code writes the implementation, I write the skills.

---

## What it does

Skills in this server are just markdown files. Each `SKILL.md` defines a persona, a methodology, and a set of instructions. When Claude invokes a skill tool, the server reads the file fresh, wraps it in a persona-activation prompt, and returns it — transforming Claude into a specialist for that conversation.

The server is also a practical demonstration of agentic AI composition: skills like `yt-research-pipeline` don't just return text, they orchestrate multi-step workflows across external tools (yt-dlp, the NotebookLM CLI) with background subagents handling long-running tasks while the main conversation stays unblocked.

---

## Architecture

```
Claude Code or Claude desktop app
          |
          | stdio (MCP protocol)
          |
    mcp_server.py  (FastMCP, single file)
          |
          | scans at startup
          |
    skills/
      notebooklm/SKILL.md
      rugby-session-coach/SKILL.md
      stoic-reflection-coach/SKILL.md
      youtube-search/SKILL.md
      yt-research-pipeline/SKILL.md
```

The server is a single Python file, `mcp_server.py`, built on [FastMCP](https://github.com/jlowin/fastmcp). At import time it scans `./skills/`, reads frontmatter from each `SKILL.md`, and dynamically registers one MCP tool per skill — no code changes required to add or remove skills.

**Startup flow:** `register_skill_tools()` scans `skills/` → reads `SKILL.md` frontmatter → derives tool name (`invoke_<sanitized_name>`) → registers handler via `mcp.tool()`.

**Tool call flow:** Handler re-reads `SKILL.md` fresh on every invocation (so you can edit a skill without restarting the server), strips frontmatter, wraps body in a persona-activation prompt, returns as string.

One deliberate design decision: tool names are derived from the `name` frontmatter field, not the folder name. The folder is just storage; the name in frontmatter is what Claude sees. A factory function closes over each skill's data to avoid the classic late-binding closure bug in Python loops.

---

## Skills

### `invoke_rugby_session_coach`

Expert rugby coach mentor that guides coaches through session planning via Socratic dialogue. Built around the Trojans RFC Coaching Framework and RFU principles (APES criteria, Coaching Habits, RFU Activate warm-up protocol).

Does not write the session plan for you — it coaches you through building it. Covers context gathering, priority identification, structure development, and logistics, then generates two artefacts: a full structured session plan and a condensed WhatsApp summary for the coaching team.

### `invoke_stoic_reflection_coach`

Stoic philosophy coaching persona for navigating difficult situations using Socratic dialogue rather than lectures. Applies the dichotomy of control as the core analytical frame, the four Stoic virtues as guides to action, and six practical exercises. Includes guardrails: explicitly flags when a situation warrants professional help rather than philosophy.

### `invoke_youtube_search`

Searches YouTube via `yt-dlp` and returns ranked results with rich metadata: title, channel, subscriber count, view count, duration, upload date, and an engagement ratio (views / subscribers) that surfaces content punching above a channel's weight.

### `invoke_notebooklm`

Full programmatic access to Google NotebookLM — including capabilities not exposed in the web UI. Covers the complete workflow: create notebooks, add sources (URLs, YouTube, PDFs, audio, video, images), chat with content, generate all artifact types (podcast, video, slide deck, infographic, report, mind map, quiz, flashcards), download in multiple formats, manage sharing.

### `invoke_yt_research_pipeline`

End-to-end orchestration pipeline: YouTube search → credibility scoring → NotebookLM notebook → artefact generation.

**Pipeline stages:**
1. Search YouTube via yt-dlp (fetches 40 candidates)
2. Score and re-rank by credibility (40% view popularity, 30% channel authority, 30% engagement ratio)
3. Confirm top results with the user before proceeding
4. Create a NotebookLM notebook and add top video URLs as sources
5. Wait for source processing (uses background subagents for parallel waiting)
6. Generate briefing doc (reliable), then attempt podcast and infographic (rate-limited)
7. Output a folder: `yt-research-[topic]-[YYYYMMDD]/` containing `metadata.md`, `briefing.md`, `podcast.mp3`, `infographic.png`

---

## Setup

**Requirements:** Python 3.11+, `yt-dlp` on PATH, `notebooklm-py` with browser extra

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

**Register with Claude Code:**
```bash
claude mcp add wayne-skills -- \
  "C:/path/to/.venv/Scripts/python.exe" \
  "C:/path/to/claude-mcp-skills-server/mcp_server.py"

claude mcp list
# wayne-skills: ... connected
```

Use forward slashes on Windows — backslashes in the JSON config cause escape failures.

**Register with Claude desktop app** — add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "wayne-skills": {
      "command": "/path/to/.venv/Scripts/python.exe",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

---

## Adding a skill

1. Create `skills/{folder-name}/SKILL.md` with frontmatter:

```markdown
---
name: my-skill
description: One line shown to Claude as the tool description.
---

Skill body here — persona, methodology, instructions.
```

2. Restart the server (`claude mcp restart wayne-skills` in Claude Code, or restart the desktop app).

Skill content is re-read on every tool call — edits to the body take effect immediately. Changes to `name` or `description` frontmatter require a restart.

---

## Skill file format

```
skills/
  {folder-name}/
    SKILL.md          # required — frontmatter + persona body
    scripts/          # optional — helper scripts called by the skill
    references/       # optional — supplementary docs referenced in the body
```
