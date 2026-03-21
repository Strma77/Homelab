#!/usr/bin/env python3
"""
musiq.py — download a song from YouTube, tag it, save to ~/Music/Songs

Usage:
  python3 musiq.py                          # interactive mode
  python3 musiq.py "Starset" "Monster"      # direct args
  python3 musiq.py "Starset" "Monster" "https://youtu.be/..."  # with URL
"""

import sys
import os
import subprocess
import shutil

# ── config ────────────────────────────────────────────────────────────────────
MUSIC_DIR = os.path.expanduser("~/Music/Songs")
TEMP_DIR  = os.path.expanduser("~/Music/.tmp")
# ─────────────────────────────────────────────────────────────────────────────


def check_dependencies():
    missing = [t for t in ["yt-dlp", "ffmpeg"] if not shutil.which(t)]
    if missing:
        print(f"[error] missing tools: {', '.join(missing)}")
        sys.exit(1)


def search_youtube(artist: str, track: str) -> str:
    query = f"ytsearch1:{artist} {track} official audio"
    print(f"[search] {artist} - {track}")
    result = subprocess.run(
        ["yt-dlp", "--get-id", "--no-playlist", query],
        capture_output=True, text=True
    )
    video_id = result.stdout.strip()
    if not video_id:
        print("[error] no results found on YouTube")
        sys.exit(1)
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[found]  {url}")
    return url


def download(url: str, dest: str) -> str:
    os.makedirs(dest, exist_ok=True)
    output_template = os.path.join(dest, "download.%(ext)s")
    cmd = [
        "yt-dlp", "-x",
        "--audio-format", "opus",
        "--audio-quality", "0",
        "--no-playlist",
        "-o", output_template,
        url
    ]
    print(f"[download] fetching audio...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[error] yt-dlp failed:")
        print(result.stderr[-600:])
        sys.exit(1)
    files = [f for f in os.listdir(dest) if f.endswith(".opus")]
    if not files:
        print("[error] no opus file found after download")
        sys.exit(1)
    return os.path.join(dest, files[0])


def write_tags(filepath: str, artist: str, track: str) -> str:
    tagged = os.path.join(os.path.dirname(filepath), "tagged.opus")
    cmd = [
        "ffmpeg", "-y",
        "-i", filepath,
        "-c", "copy",
        "-metadata", f"artist={artist}",
        "-metadata", f"title={track}",
        "-metadata", "album=",
        tagged
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        os.remove(filepath)
        print(f"[tagged]  {artist} - {track}")
        return tagged
    else:
        print("[warn]   ffmpeg tagging failed")
        return filepath


def save(filepath: str, artist: str, track: str):
    dest_dir = os.path.join(MUSIC_DIR, artist)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"{track}.opus")
    shutil.move(filepath, dest_path)
    print(f"[saved]  {dest_path}")


def cleanup(folder: str):
    if os.path.exists(folder):
        shutil.rmtree(folder)


def main():
    check_dependencies()

    if len(sys.argv) >= 3:
        artist = sys.argv[1].strip()
        track  = sys.argv[2].strip()
        url    = sys.argv[3].strip() if len(sys.argv) >= 4 else None
    else:
        print("┌──────────────────────────────┐")
        print("│  musiq — download pipeline   │")
        print("└──────────────────────────────┘")
        artist = input("Artist: ").strip()
        track  = input("Track:  ").strip()
        url_in = input("YouTube URL (blank to auto-search): ").strip()
        url    = url_in if url_in else None

    if not artist or not track:
        print("[error] artist and track required")
        sys.exit(1)

    safe_name = f"{artist}_{track}".replace(" ", "_").replace("/", "_")
    temp_folder = os.path.join(TEMP_DIR, safe_name)

    try:
        if not url:
            url = search_youtube(artist, track)
        filepath = download(url, temp_folder)
        filepath = write_tags(filepath, artist, track)
        save(filepath, artist, track)
    finally:
        cleanup(temp_folder)

    print(f"\n✓ done")


if __name__ == "__main__":
    main()
