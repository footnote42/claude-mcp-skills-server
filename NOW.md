# NOW — claude-mcp-skills-server

## Status
PARKED — curated 2026-09-29, repo healthy; intent to return and develop further (dropped from QUEUED 2026-09-23 for pitch-mate-rota)

## Next
Do a real `yt-research-pipeline` run to prove the reworked Phases 4-5 (exclusions from `metadata_scored.json`, `generate --wait`, `artifact retry`) against NotebookLM.

## Context
- Purpose: built for the YouTube → NotebookLM research cycle; also a shared skills layer between Claude Code and Claude Desktop
- Registered once, at user scope, as `wayne-skills`; 5 tools (notebooklm, rugby-session-coach, stoic-reflection-coach, youtube-search, yt-research-pipeline)
- Frontmatter: single-line `description:` only (line-based parser); `persona: true` opts a skill into the coaching wrapper
- `skills/notebooklm/` is gitignored (`.gitignore:153`), so a fresh clone registers 4 skills, not 5
- How it works: `Resources/Vault Maintenance/Wayne Skills Server Guide.html` in the vault
- Obsidian: none (no vault folder exists)

## Blocker
None

## Last session
2026-09-29 — Curated all 5 tools with `curating-skills`: fixed dropped Phase 3 exclusions, `">"` coach descriptions, persona wrapper on every tool; tools now return their folder path. The old Next ("read `mcp_server.py` and write down how it works") is done; that's the server guide.

2026-09-22 — Triage. No secrets in history, remote exists, entry point intact. Lesson: just because something works is no excuse for ignoring how it works and not exploiting it further.
