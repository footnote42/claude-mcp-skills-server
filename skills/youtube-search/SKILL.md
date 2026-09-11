---
name: youtube-search
description: Search YouTube for videos using yt-dlp and display structured, ranked results with metadata. Use this skill whenever the user wants to search YouTube, find videos, discover content on a topic, research channels, or analyze video engagement. Trigger on phrases like "search YouTube", "find videos about", "YouTube results for", "look up videos", "yt-dlp search", or any request to find or list YouTube videos on a topic.
---

# YouTube Search

Search YouTube via yt-dlp and return the top results with rich metadata and engagement metrics.

## Setup check

Before running a search, verify yt-dlp is installed:

```bash
yt-dlp --version
```

If not installed, tell the user and offer to install it:
- **pip**: `pip install yt-dlp`
- **Windows (winget)**: `winget install yt-dlp`
- **macOS (brew)**: `brew install yt-dlp`

## Running a search

Use the bundled script at `scripts/youtube_search.py` (relative to this skill's directory):

```bash
python "<skill-dir>/scripts/youtube_search.py" "QUERY" [options]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--results N` / `-n N` | 20 | Number of results to return. **Pass 15 explicitly** — see timeout note below |
| `--months N` / `-m N` | 6 | Filter to last N months |
| `--json` | off | Dump raw JSON instead of formatted output |

**Examples:**
```bash
# Default: top 20 from last 6 months
python script.py "rust programming tutorial"

# Custom time range
python script.py "valorant tips" --months 3

> **yt-dlp has a hard 180-second search ceiling.** Above ~15 results the search does not finish
> inside it and dies with `ERROR: Search timed out after 180 seconds.` The script's default of 20
> is marginal and 40 always fails. For breadth, run several narrower queries at `--results 15`
> and merge, rather than raising the count.

# Fewer results, wider window
python script.py "claude ai demo" --results 5 --months 12

# Raw JSON for further processing
python script.py "machine learning" --json
```

## Output fields

Each result includes:
- **Title** and rank number
- **Channel name** + subscriber count
- **View count**, **duration**, **upload date**
- **Engagement ratio**: views ÷ subscribers (higher = video punching above channel weight)
- **URL**

Numbers are formatted as human-readable (e.g. `1.4M`, `230K`).

## Notes on subscriber count

Subscriber counts come from yt-dlp's channel extraction and are available most of the time, but may show as `N/A` for some channels (typically very new channels or those that hide subscriber counts). This is a YouTube/yt-dlp limitation, not a bug.

## Interpreting engagement ratio

- **< 0.1x** — low engagement relative to channel size (common for large channels)
- **0.5x–2x** — solid engagement
- **5x+** — viral or highly recommended content

This metric helps surface videos gaining traction even from smaller channels.
