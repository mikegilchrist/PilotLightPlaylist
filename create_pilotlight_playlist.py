#!/usr/bin/env python3
# Purpose: Coordinate scraper and playlist update with dry-run and verbose
# Usage: python create_pilotlight_playlist.py [--dry-run/-n] [--verbose/-v]
# Date: 2025-08-04
# Version: 1.2.0

import argparse
import subprocess
import sys
from datetime import datetime

SCRAPER     = "pilotlight_scraper.py"
PLAYLIST    = "add_to_playlist.py"
ARTIST_FILE = "upcoming_artists_all.txt"

def parse_args():
    p = argparse.ArgumentParser(description="Run scraper and playlist update steps")
    p.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simulate actions; do not push updates to Spotify"
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show child scripts’ output"
    )
    return p.parse_args()

args = parse_args()

# Build command for scraper (only verbose)
scraper_cmd = [sys.executable, SCRAPER, "--week_stop", "-1"]
if args.verbose:
    scraper_cmd.append("--verbose")

print(f"{('[DRY RUN] ' if args.dry_run else '')}Running scraper…")
subprocess.run(
    scraper_cmd,
    check=True,
    stdout=(sys.stdout if args.verbose else None),
    stderr=(sys.stderr if args.verbose else None)
)

# Build command for playlist (dry-run + verbose)
playlist_cmd = [sys.executable, PLAYLIST, ARTIST_FILE]
if args.dry_run:
    playlist_cmd.append("--dry-run")
if args.verbose:
    playlist_cmd.append("--verbose")

print(f"{('[DRY RUN] ' if args.dry_run else '')}Running playlist update…")
subprocess.run(
    playlist_cmd,
    check=True,
    stdout=(sys.stdout if args.verbose else None),
    stderr=(sys.stderr if args.verbose else None)
)

print("Done.")

