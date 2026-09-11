---
name: yt-research-pipeline
description: Full YouTube-to-NotebookLM research pipeline. Searches YouTube for a topic, scores results by credibility (views + channel authority + engagement), feeds the top videos into a new NotebookLM notebook as sources, generates a briefing doc + podcast + infographic, and produces a local metadata report. Use this skill whenever the user wants to research a topic using YouTube videos, build a research notebook from video sources, create a podcast or briefing from YouTube content, or says anything like "research X on YouTube", "find YouTube videos about X and analyze them", "build a NotebookLM notebook from YouTube", or "create a research pipeline for X". This is a multi-step orchestration skill — always invoke it for YouTube-to-NotebookLM workflows even if the user only mentions one part.
---

# YouTube → NotebookLM Research Pipeline

This skill orchestrates a full research pipeline: search YouTube by topic → score by credibility → load into NotebookLM → generate artifacts + metadata report.

## Quick prerequisite check

Before starting, verify both tools are ready:

```bash
# 1. YouTube search tool
python "C:/Users/kenho/Projects/claude-mcp-skills-server/skills/youtube-search/scripts/youtube_search.py" --help

# 2. NotebookLM auth (Windows: prefix with PYTHONUTF8=1)
PYTHONUTF8=1 notebooklm auth check
```

If NotebookLM auth fails, tell the user to run `PYTHONUTF8=1 notebooklm login` and complete the browser login before continuing.

## Pipeline overview

```
User query
   ↓
[Phase 1] YouTube search (yt-dlp) → raw video JSON
   ↓
[Phase 2] Score + rank by credibility → metadata.md + scored list
   ↓
[Phase 3] Confirm with user (show top results, allow exclusions)
   ↓
[Phase 4] NotebookLM: create notebook, add YouTube URLs as sources
   ↓
[Phase 5] Wait for sources to process, then generate artifacts
   ↓
[Phase 6] Download artifacts, report completion
```

## Phase 1: Search YouTube

The search script is at `C:/Users/kenho/Projects/claude-mcp-skills-server/skills/youtube-search/scripts/youtube_search.py`.

Run it with `--json` to get raw data, fetching extra results since we'll re-rank by credibility:

```bash
python "C:/Users/kenho/Projects/claude-mcp-skills-server/skills/youtube-search/scripts/youtube_search.py" \
  "QUERY HERE" \
  --results 40 \
  --months 6 \
  --json > "OUTPUT_DIR/raw_results.json"
```

Adjust `--months` if the user specifies a time window. Fetch 40 to have headroom after scoring (we'll keep the top 20-25 after ranking).

## Phase 2: Score and rank

Use the bundled scoring script:

```bash
python "C:/Users/kenho/Projects/claude-mcp-skills-server/skills/yt-research-pipeline/scripts/score_and_report.py" \
  "OUTPUT_DIR/raw_results.json" \
  --query "QUERY HERE" \
  --months 6 \
  --top 25 \
  --report "OUTPUT_DIR/metadata.md"
```

This produces:
- `metadata.md` — the structured credibility report (always kept, for reading at leisure)
- `metadata_scored.json` — sorted list with scores (used in Phase 4)

**How credibility scoring works** (explain this to the user if they ask):
- **View popularity (40%)** — log-scaled, so very popular videos rank well but don't completely dominate
- **Channel authority (30%)** — established channels with large subscriber bases
- **Engagement ratio (30%)** — views ÷ subscribers; content that resonated beyond the channel's usual audience

## Phase 3: Confirm with user

Show the scored list (the script prints a summary to terminal) and ask:

> "I found [N] videos ranked by credibility. Here are the top results — shall I load all of them into NotebookLM, or would you like to exclude any before I continue? (Processing [N] sources will take a few minutes.)"

This pause matters because NotebookLM source processing takes time and counts against account quotas. It's also a good chance for the user to spot obviously off-topic results.

## Phase 4: Set up NotebookLM notebook

Create the notebook and add YouTube URLs as sources. Always use `PYTHONUTF8=1` on Windows:

```bash
# Create notebook
PYTHONUTF8=1 notebooklm create "YouTube Research: QUERY" --json
# → save the notebook ID from output

PYTHONUTF8=1 notebooklm use NOTEBOOK_ID

# Add each video URL as a source
# Get URLs from scored JSON:
python "C:/Users/kenho/Projects/claude-mcp-skills-server/skills/yt-research-pipeline/scripts/score_and_report.py" \
  "OUTPUT_DIR/raw_results.json" \
  --query "QUERY" \
  --top 25 \
  --report "OUTPUT_DIR/metadata.md" \
  --urls-only
# → prints one URL per line; add each with: notebooklm source add "URL" --json
```

Add URLs in a loop, capturing source IDs for the wait step. If any source add fails (invalid URL, geo-blocked), skip it and log a warning — don't abort the whole pipeline.

## Phase 5: Wait for sources, then generate artifacts

### Wait for source processing

Sources must be indexed before generation. Use a background subagent if the list is long (each source takes 30s–2min):

```bash
# For each source_id captured above:
PYTHONUTF8=1 notebooklm source wait SOURCE_ID --timeout 120
```

Or check in batch: `PYTHONUTF8=1 notebooklm source list --json` and wait until all status = `ready`.

### Generate artifacts

Generate in this order — from most reliable to least reliable:

**1. Briefing doc (always, fast and reliable):**
```bash
PYTHONUTF8=1 notebooklm generate report --format briefing-doc --json
# → save task_id
PYTHONUTF8=1 notebooklm artifact wait TASK_ID --timeout 900
PYTHONUTF8=1 notebooklm download report "OUTPUT_DIR/briefing.md"
```

**2. Podcast / audio overview (attempt, may fail due to rate limits):**
```bash
PYTHONUTF8=1 notebooklm generate audio "Focus on key findings and credibility of sources" --json
# → save task_id
PYTHONUTF8=1 notebooklm artifact wait TASK_ID --timeout 1200
PYTHONUTF8=1 notebooklm download audio "OUTPUT_DIR/podcast.mp3"
```

**3. Infographic (attempt, may fail):**
```bash
PYTHONUTF8=1 notebooklm generate infographic --detail detailed --json
# → save task_id
PYTHONUTF8=1 notebooklm artifact wait TASK_ID --timeout 900
PYTHONUTF8=1 notebooklm download infographic "OUTPUT_DIR/infographic.png"
```

If any artifact generation fails (rate limit, timeout, error), log the failure and continue — don't block the whole pipeline. The briefing doc is the most important output.

## Phase 6: Final output report

After all steps complete, tell the user what was produced with a clean summary:

```
Research pipeline complete for: "QUERY"

Output folder: OUTPUT_DIR/
  metadata.md      — Video credibility report (view + channel + engagement data)
  briefing.md      — NotebookLM analysis briefing document
  podcast.mp3      — Audio overview  [or: FAILED - rate limited, retry manually]
  infographic.png  — Visual summary  [or: FAILED - rate limited, retry manually]

NotebookLM notebook: "YouTube Research: QUERY"
  Notebook ID: NOTEBOOK_ID
  Sources added: N/M videos (M skipped due to errors)
  You can continue chatting with the notebook: PYTHONUTF8=1 notebooklm use NOTEBOOK_ID

To retry failed artifacts:
  PYTHONUTF8=1 notebooklm use NOTEBOOK_ID
  PYTHONUTF8=1 notebooklm generate audio --retry 3
```

## Output folder naming

Name the output folder to be findable later:

```
yt-research-[sanitized-query]-[YYYYMMDD]/
```

Example: `yt-research-quantum-computing-20260312/`

Create it in the current working directory, or in a `~/Research/` folder if the user has one.

## Handling edge cases

| Situation | Action |
|-----------|--------|
| NotebookLM not authenticated | Stop, tell user to run `PYTHONUTF8=1 notebooklm login` |
| YouTube search returns < 5 results | Warn user, suggest wider time window (--months 12) |
| Source add fails for a URL | Skip and log; proceed with the others |
| Source processing fails | Mark as failed in summary; exclude from generation |
| Artifact generation rate-limited | Log failure, include retry command in summary |
| User wants fewer/more sources | Adjust `--top` in the scoring step |

## Rate limit awareness

NotebookLM enforces quotas on audio, video, quiz, and infographic generation. If the user has been generating a lot of content recently, artifact generation may fail. The briefing doc (text report) is almost never rate-limited and should always succeed.

If generation fails, include this in the summary and tell the user they can retry later with:
```bash
PYTHONUTF8=1 notebooklm use NOTEBOOK_ID
PYTHONUTF8=1 notebooklm generate audio --retry 3
```
