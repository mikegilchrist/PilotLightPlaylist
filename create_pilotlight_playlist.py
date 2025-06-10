# Version 1.1.0

import subprocess
import sys
import os
from datetime import datetime

scraper_script = "pilotlight_scraper.py"
playlist_script = "add_to_playlist.py"
today_str = datetime.today().strftime("%Y-%m-%d")
artist_file = "upcoming_artists_all.txt"

print("Running scraper...")
try:
    subprocess.run([
        "python", scraper_script, "--week_stop", "-1"
    ], check=True, text=True, stdout=sys.stdout, stderr=sys.stderr)
except subprocess.CalledProcessError:
    print("Error running pilotlight_scraper.py")
    sys.exit(1)

print("Running playlist generator...")
try:
    subprocess.run([
        "python", playlist_script, artist_file
    ], check=True)
except subprocess.CalledProcessError:
    print("Error running add_to_playlist.py")
    sys.exit(1)

print("All steps completed successfully.")
