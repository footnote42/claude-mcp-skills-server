#!/usr/bin/env python3
"""YouTube search via yt-dlp with structured, human-readable output."""

import subprocess
import json
import sys
import argparse
from datetime import datetime, timedelta

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def human_num(n):
    """Format a number as human-readable (e.g. 1.2M, 450K)."""
    if n is None:
        return "N/A"
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_duration(seconds):
    """Format seconds into H:MM:SS or M:SS."""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_date(date_str):
    """Convert YYYYMMDD to readable date like Mar 5, 2025."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(date_str), "%Y%m%d")
        return dt.strftime("%b %d, %Y").replace(" 0", " ")
    except Exception:
        return str(date_str)


def engagement_ratio(views, subscribers):
    """Calculate views-to-subscribers ratio."""
    if not views or not subscribers or int(subscribers) == 0:
        return "N/A"
    ratio = int(views) / int(subscribers)
    if ratio >= 10:
        return f"{ratio:.0f}x"
    return f"{ratio:.2f}x"


def run_search(query, results=20, months=6):
    """Run yt-dlp search and return parsed video data filtered by date."""
    date_threshold = datetime.now() - timedelta(days=months * 30)

    # YouTube search surfaces popular evergreen content, so old videos rank high.
    # We fetch a large pool (up to 100) and filter client-side, rather than relying
    # on yt-dlp's --dateafter which cuts off yt-dlp output entirely for filtered items.
    fetch_count = min(max(results * 4, 40), 100)

    cmd = [
        "yt-dlp",
        f"ytsearch{fetch_count}:{query}",
        "--dump-json",
        "--no-warnings",
        "--ignore-errors",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        print("ERROR: yt-dlp is not installed.")
        print("Install it with:  pip install yt-dlp")
        print("  or:             brew install yt-dlp  (macOS)")
        print("  or:             winget install yt-dlp  (Windows)")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: Search timed out after 180 seconds.")
        sys.exit(1)

    videos = []
    for line in proc.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            videos.append(data)
        except json.JSONDecodeError:
            continue

    # Filter by date client-side
    threshold_str = date_threshold.strftime("%Y%m%d")
    filtered = [
        v for v in videos
        if v.get("upload_date") and v["upload_date"] >= threshold_str
    ]

    # If nothing passes the filter (e.g., very niche query), fall back to unfiltered
    if not filtered and videos:
        print(f"  Note: No results from the last {months} months. Showing all-time results.\n")
        return videos[:results]

    return filtered[:results]


def print_results(videos, query, months):
    """Pretty-print video results with dividers."""
    divider = "-" * 72

    print(f"\n{divider}")
    print(f"  YouTube Search: \"{query}\"  |  Last {months} months  |  {len(videos)} results")
    print(divider)

    if not videos:
        print("\n  No results found.")
        return

    for i, v in enumerate(videos, 1):
        title = v.get("title") or "Unknown title"
        channel = v.get("uploader") or v.get("channel") or "Unknown channel"
        subscribers = v.get("channel_follower_count")
        views = v.get("view_count")
        duration = v.get("duration")
        upload_date = v.get("upload_date")
        url = v.get("webpage_url") or v.get("url") or f"https://www.youtube.com/watch?v={v.get('id', '')}"

        ratio = engagement_ratio(views, subscribers)

        print(f"\n  #{i}  {title}")
        print(f"      Channel:    {channel}  ({human_num(subscribers)} subscribers)")
        print(f"      Views:      {human_num(views)}   |   Duration: {format_duration(duration)}   |   Uploaded: {format_date(upload_date)}")
        print(f"      Engagement: {ratio} views/sub")
        print(f"      URL:        {url}")

        if i < len(videos):
            print(f"\n{divider}")

    print(f"\n{divider}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Search YouTube via yt-dlp and display structured results."
    )
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--results", "-n", type=int, default=20, help="Number of results (default: 20)")
    parser.add_argument("--months", "-m", type=int, default=6, help="Filter to last N months (default: 6)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")

    args = parser.parse_args()
    query = " ".join(args.query)

    videos = run_search(query, results=args.results, months=args.months)

    if args.json:
        print(json.dumps(videos, indent=2))
    else:
        print_results(videos, query, args.months)


if __name__ == "__main__":
    main()
