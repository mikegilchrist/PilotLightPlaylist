# Pilot Light Spotify Playlist Generator

This tool scrapes upcoming events from thepilotlight.com, extracts artist names, finds their most popular tracks on Spotify, and builds a playlist for you.

## Features

- Automatically scrapes upcoming shows
- Skips canceled or non-band content (like "Out Series" and strike-throughs)
- Finds the correct artist using exact name matching
- Adds top 2 Spotify tracks per artist
- Maintains show order in playlist
- Exports track metadata to a CSV file

## Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/pilotlight-playlist.git
cd pilotlight-playlist
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Spotify Developer App

Visit: https://developer.spotify.com/dashboard  
- Click "Create an App"
- Note your Client ID and Client Secret
- Set Redirect URI to: http://127.0.0.1:9090

### 4. Add Your Credentials

Copy the environment template:

```bash
cp .env_template .env
```

Then edit `.env` with your Spotify keys:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:9090
```

## Running the Full Script

Use the unified runner script:

```bash
python run_all.py
```

This will:
1. Scrape upcoming events (default: today through 3 weeks out)
2. Build a Spotify playlist
3. Export a CSV with all track details

## Customizing the Date Range

By default, the scraper includes events from this week to 3 weeks from now.

You can customize that with:

```bash
python pilotlight_scraper.py --week_start 1 --week_stop 2
```

This would include events starting next week through 2 weeks from now.

Then run the playlist builder manually:

```bash
python add_to_playlist.py upcoming_artists_YYYY-MM-DD.txt
```

Replace `YYYY-MM-DD` with the date on the file that was just generated.

## Output Files

- `upcoming_artists_YYYY-MM-DD.txt`: Band metadata per event
- `playlist_tracks_YYYY-MM-DD.csv`: CSV export with track/artist info
- Spotify playlist URL is printed in the terminal

## Requirements

- Python 3.8+
- A free Spotify account (plus developer app)
- Internet access

