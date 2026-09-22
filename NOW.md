# NOW — claude-mcp-skills-server

## Status
QUEUED — no active work, repo healthy; intent to return and develop further

## Next
Read `mcp_server.py` end to end and write down how discovery, registration and the tool-call flow work; then decide what to build on it.

## Context
- Purpose: built for the YouTube → NotebookLM research cycle; also serves as a shared skills layer between Claude Code and Claude Desktop
- In daily use: registered as `wayne-skills`, 5 skills load clean (notebooklm, rugby-session-coach, stoic-reflection-coach, youtube-search, yt-research-pipeline)
- `skills/notebooklm/` is gitignored (`.gitignore:153`) — a fresh clone registers 4 skills, not 5
- Single-file server: `mcp_server.py`
- Obsidian: none (no vault folder exists)

## Blocker
None

## Last session
2026-09-22 — Triage. No secrets in history, remote exists, entry point intact. Lesson: just because something works is no excuse for ignoring how it works and not exploiting it further.
