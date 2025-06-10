# Version 1.0.0

import subprocess
import sys
from datetime import datetime

# Define filenames and playlist title
scraper_script = "pilotlight_scraper.py"
playlist_script = "add_to_playlist.py"
today_str = datetime.today().strftime("%Y-%m-%d")
artist_file = f"upcoming_artists_{today_str}.txt"

print("Running scraper...")
try:
    subprocess.run(["python", scraper_script], check=True)
except subprocess.CalledProcessError:
    print("Error running pilotlight_scraper.py")
    sys.exit(1)

print("Running playlist generator...")
try:
    subprocess.run(["python", playlist_script, artist_file], check=True)
except subprocess.CalledProcessError:
    print("Error running add_to_playlist.py")
    sys.exit(1)

print("All steps completed successfully.")
