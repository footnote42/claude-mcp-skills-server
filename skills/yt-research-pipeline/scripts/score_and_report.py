#!/usr/bin/env python3
"""
Score YouTube search results by credibility and generate a structured metadata report.

Credibility composite score weights:
  40% - View popularity (log scale, so 1M views > 10K but not 100x more)
  30% - Channel authority (log scale subscriber count)
  30% - Engagement ratio (views/subscribers, capped to avoid gaming)

Higher score = more credible/relevant for research purposes.
"""

import json
import math
import sys
import argparse
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def credibility_score(video):
    views = video.get("view_count") or 0
    subscribers = video.get("channel_follower_count") or 0

    view_score = math.log10(max(views, 1)) / 8.0          # 0-1 (8 = log10(100M))
    sub_score = math.log10(max(subscribers, 1)) / 8.0     # 0-1

    # Engagement: views / subscribers, capped at 10x (viral ceiling)
    if subscribers > 0:
        engagement = min(views / subscribers, 10.0) / 10.0
    else:
        engagement = 0.0

    return round((view_score * 0.4) + (sub_score * 0.3) + (engagement * 0.3), 4)


def human_num(n):
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
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(date_str), "%Y%m%d")
        return dt.strftime("%b %d, %Y").replace(" 0", " ")
    except Exception:
        return str(date_str)


def score_badge(score):
    if score >= 0.7:
        return "*** HIGH"
    if score >= 0.45:
        return "**  MED"
    return "*   LOW"


def generate_markdown_report(videos, query, months, output_path):
    lines = [
        f"# YouTube Research: {query}",
        f"",
        f"**Search window:** Last {months} months  |  **Results:** {len(videos)} videos  |  **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
        f"## Credibility Score Guide",
        f"",
        f"Scores blend three signals on a 0–1 scale:",
        f"- **View popularity** (40%) — logarithmic, so 1M views isn't 100× better than 10K",
        f"- **Channel authority** (30%) — established channels with large subscriber bases score higher",
        f"- **Engagement ratio** (30%) — views ÷ subscribers; content that resonates beyond the channel's usual audience",
        f"",
        f"| Badge | Score | Interpretation |",
        f"|-------|-------|----------------|",
        f"| *** HIGH | 0.70+ | Strong signal on all three dimensions |",
        f"| **  MED  | 0.45–0.69 | Solid on 1-2 dimensions |",
        f"| *   LOW  | < 0.45 | Niche/new channel or low views — verify manually |",
        f"",
        f"---",
        f"",
        f"## Videos (ranked by credibility score)",
        f"",
    ]

    for i, v in enumerate(videos, 1):
        score = v["_credibility_score"]
        title = v.get("title") or "Unknown"
        channel = v.get("uploader") or v.get("channel") or "Unknown"
        subscribers = v.get("channel_follower_count")
        views = v.get("view_count")
        duration = v.get("duration")
        upload_date = v.get("upload_date")
        url = v.get("webpage_url") or v.get("url") or f"https://www.youtube.com/watch?v={v.get('id', '')}"

        if subscribers and views:
            ratio_raw = views / max(subscribers, 1)
            ratio_str = f"{ratio_raw:.2f}x" if ratio_raw < 10 else f"{ratio_raw:.0f}x"
        else:
            ratio_str = "N/A"

        lines += [
            f"### {i}. {title}",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Credibility** | {score_badge(score)} ({score}) |",
            f"| **Channel** | {channel} |",
            f"| **Subscribers** | {human_num(subscribers)} |",
            f"| **Views** | {human_num(views)} |",
            f"| **Engagement** | {ratio_str} views/sub |",
            f"| **Duration** | {format_duration(duration)} |",
            f"| **Uploaded** | {format_date(upload_date)} |",
            f"| **URL** | {url} |",
            f"",
        ]

    # Write file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Metadata report written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Score YouTube results and generate credibility report.")
    parser.add_argument("input_json", help="JSON file from youtube_search.py --json output")
    parser.add_argument("--query", default="Unknown query", help="Search query (for report title)")
    parser.add_argument("--months", type=int, default=6, help="Search window in months")
    parser.add_argument("--top", type=int, default=25, help="How many top results to keep")
    parser.add_argument("--report", default="metadata.md", help="Output markdown report path")
    parser.add_argument("--urls-only", action="store_true", help="Print only URLs (for piping to notebooklm)")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        videos = json.load(f)

    # Score and sort
    for v in videos:
        v["_credibility_score"] = credibility_score(v)

    videos.sort(key=lambda v: v["_credibility_score"], reverse=True)
    videos = videos[:args.top]

    if args.urls_only:
        for v in videos:
            url = v.get("webpage_url") or v.get("url") or f"https://www.youtube.com/watch?v={v.get('id', '')}"
            print(url)
        return

    # Print quick summary to terminal
    divider = "-" * 72
    print(f"\n{divider}")
    print(f"  Top {len(videos)} results for: \"{args.query}\"  (scored by credibility)")
    print(divider)
    for i, v in enumerate(videos, 1):
        score = v["_credibility_score"]
        title = (v.get("title") or "Unknown")[:55]
        channel = (v.get("uploader") or "Unknown")[:25]
        views = human_num(v.get("view_count"))
        subs = human_num(v.get("channel_follower_count"))
        print(f"  #{i:2d} [{score:.2f}] {title}")
        print(f"       {channel} | {subs} subs | {views} views")
    print(f"{divider}\n")

    generate_markdown_report(videos, args.query, args.months, args.report)

    # Write scored JSON for downstream use
    scored_path = args.report.replace(".md", "_scored.json")
    with open(scored_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(f"Scored JSON written to: {scored_path}")


if __name__ == "__main__":
    main()
