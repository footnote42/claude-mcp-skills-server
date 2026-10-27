# NOW — claude-mcp-skills-server

## Start here
Start here: read programme `NOW.md` (Start here) and `CLAUDE.md`; this repo's own notes follow.

## Status
PARKED — in production use as `wayne-skills`, healthy; not in programme plan-2026-11. No open issues or PRs.

## Next
Do a real `yt-research-pipeline` run to prove the reworked Phases 4-5 (exclusions from `metadata_scored.json`, `generate --wait`, `artifact retry`) against NotebookLM. Needs the PC (NotebookLM auth), so it is nitro work.

## Context
- Purpose: built for the YouTube to NotebookLM research cycle; also a shared skills layer between Claude Code and Claude Desktop
- Registered once, at user scope, as `wayne-skills`; 5 tools (notebooklm, rugby-session-coach, stoic-reflection-coach, youtube-search, yt-research-pipeline)
- Frontmatter: single-line `description:` only (line-based parser); `persona: true` opts a skill into the coaching wrapper
- `skills/notebooklm/` is gitignored, so a fresh clone registers 4 skills, not 5
- How it works: `Resources/Vault Maintenance/Wayne Skills Server Guide.html` in the vault
- a1cleanup's Stage 7.10b reviews the yt-research skill here; check a1cleanup's NOW.md before changing it
- Obsidian: none (no vault folder exists)

## Blocker
None

## Last session
2026-10-25 — NOW.md refreshed for a fresh start (no code change).
2026-10-10 — rugby-session-coach: reflection mode added, TREDS and habits gaps fixed, retros saved in the rugby Area season folder (`33534cf`, `23aa8f3`).
2026-09-29 — Curated all 5 tools with `curating-skills`: fixed dropped Phase 3 exclusions, coach descriptions, persona wrapper on every tool; tools now return their folder path.
