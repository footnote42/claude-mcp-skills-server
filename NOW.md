# NOW — claude-mcp-skills-server

## Start here (fresh agent, 2026-10-25)
1. Read this file, then `CLAUDE.md`, then this repo's open issues and PRs on GitHub.
2. The plan to 13 Nov is programme `docs/plan-2026-11.md` (agreed by Wayne 25 Oct). Three streams are active: home-lab Phase 1, Command Centre with Comms, and Holly. Nothing outside them starts without Wayne's yes.
3. Ground rules (Wayne, 22-25 Oct 2026):
   - Work through GitHub issues. Comment on an issue when you take it; never work on one another session has claimed.
   - Agents never merge PRs and never run `hl-apply`. When a PR is green, comment on the PR: `ready for Holly: <repo>#<n> <sha>`. For an on-box step, comment `hl-apply <name> needed` on the issue. Holly (the chief of staff on New Dave) scans GitHub hourly and does the merge or the apply.
   - No root. Root work goes to Holly's reviewed-script route (`hl-apply`) or to Wayne as a script.
   - The move to New Dave is Holly's: home-lab #21, #70 and anything labelled `newdave`, plus the health check. Don't touch them.
   - Comms is left to nitro and Holly on New Dave.
   - No secrets, IPs or hostnames in any file, issue or comment.
   - Wayne is not an advanced GitHub user: when he has to do something, give him the exact clicks or commands.

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
