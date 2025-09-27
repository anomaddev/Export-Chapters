#!/usr/bin/env python3
import json
import shutil
import subprocess
import argparse
import math
import sys
from pathlib import Path

def check_ffprobe():
    if shutil.which("ffprobe") is None:
        raise SystemExit("Error: ffprobe not found. Install FFmpeg and ensure ffprobe is in your PATH.")

def ffprobe_chapters(input_path: Path):
    cmd = ["ffprobe","-v","error","-print_format","json","-show_chapters","-i",str(input_path)]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"ffprobe failed:\n{e.output.decode('utf-8', errors='replace')}")
    data = json.loads(out.decode("utf-8"))
    chapters = []
    for idx, ch in enumerate(data.get("chapters", []), start=1):
        tags = ch.get("tags", {}) or {}
        title = tags.get("title") or tags.get("TITLE") or None
        try:
            start = float(ch.get("start_time")); end = float(ch.get("end_time"))
        except (TypeError, ValueError):
            start = float(ch.get("start", 0)); end = float(ch.get("end", 0))
        chapters.append({"id": idx, "start": start, "end": end, "title": title})
    return chapters

def format_time_youtube(t: float) -> str:
    """
    Format time with seconds always shown:
      - Under 1 hour: M:SS
      - 1 hour or more: H:MM:SS
    """
    total = int(t)  # floor to whole seconds
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"

def build_youtube_lines(chapters, timestamp_first: bool):
    lines = []
    for ch in chapters:
        title = (ch["title"] or f"Chapter {ch['id']}").strip()
        ts = format_time_youtube(ch["start"])
        lines.append(f"{ts} - {title}" if timestamp_first else f"{title} - {ts}")
    return lines

def copy_to_clipboard(text: str):
    try:
        if sys.platform == "darwin":
            subprocess.run("pbcopy", text=True, input=text, check=True)
        elif sys.platform.startswith("win"):
            subprocess.run("clip", text=True, input=text, check=True)
        else:
            if shutil.which("xclip"):
                subprocess.run(["xclip","-selection","clipboard"], text=True, input=text, check=True)
            elif shutil.which("xsel"):
                subprocess.run(["xsel","--clipboard","--input"], text=True, input=text, check=True)
            else:
                print("⚠️  Clipboard tools not found. Install `xclip` or `xsel` to use --copy on Linux.")
                return False
        return True
    except Exception as e:
        print(f"⚠️  Failed to copy to clipboard: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Export chapter markers from MP4/MOV to YouTube-friendly text."
    )
    parser.add_argument("input", help="Path to input video file (.mp4/.mov)")
    parser.add_argument("--title-first", action="store_true",
                        help="Output `Title - timestamp` instead of the default `timestamp - Title`.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o","--output", help="Write to this file (default: <input>.yt.txt).")
    group.add_argument("--copy", action="store_true", help="Copy result to clipboard (no file).")
    group.add_argument("--stdout", action="store_true", help="Print result to stdout (no file).")
    args = parser.parse_args()

    check_ffprobe()

    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    chapters = ffprobe_chapters(in_path)
    if not chapters:
        raise SystemExit("No chapters found in the file.")

    lines = build_youtube_lines(chapters, timestamp_first=not args.title_first)
    text = "\n".join(lines)

    if args.copy:
        if copy_to_clipboard(text):
            print("📋 Copied chapter list to clipboard!")
        return

    if args.stdout:
        print(text)
        return

    out_path = Path(args.output).expanduser().resolve() if args.output else in_path.with_name(in_path.stem + ".yt.txt")
    out_path.write_text(text, encoding="utf-8")
    print(f"✅ Wrote {len(chapters)} chapters to: {out_path}")

if __name__ == "__main__":
    main()
