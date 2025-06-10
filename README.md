# Pilot Light Playlist Generator

This project scrapes upcoming show data from [thepilotlight.com](https://thepilotlight.com), parses band names, and builds Spotify playlists for:

- **Upcoming Shows**
- **Recent Shows**

It integrates with the Spotify API to search for each band and add their top two tracks to a public playlist.

---

## Requirements

- Python 3.7+
- Spotify developer credentials
- `requests`, `beautifulsoup4`, `spotipy`, `python-dotenv`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the root directory (or use `.env_template` as a guide):

```
SPOTIFY_CLIENT_ID="your_client_id"
SPOTIFY_CLIENT_SECRET="your_client_secret"
SPOTIFY_REDIRECT_URI="http://127.0.0.1:9090"
```

---

## How to Use

### 1. Create or update playlists for **upcoming shows**

```bash
python create_pilotlight_playlist.py
```

This will scrape shows from today forward and generate a playlist called:

```
Pilot Light Playlist: Upcoming Shows
```

If the playlist already exists, it is updated. Tracks from past events are removed and moved to:

```
Pilot Light: Recent Shows
```

### 2. Scrape for **custom date ranges**

Use optional week arguments:

```bash
python pilotlight_scraper.py --week_start=0 --week_stop=3
```

To get all upcoming shows (no date window):

```bash
python pilotlight_scraper.py
```

To get past shows only (used to seed the Recent Shows playlist):

```bash
python pilotlight_scraper.py --week_start=-100 --week_stop=0
python add_to_playlist.py upcoming_artists_<date>.txt "Pilot Light: Recent Shows"
```

---

## Known Issues

- 🔹 Band names from **today's date** may be skipped if date comparison is overly strict
- 🔹 Requires Spotify developer credentials to function

---

## 📂 Output

- `upcoming_artists_<date>.txt`: Raw scraped data
- `playlist_tracks_<date>.csv`: Tracks added to Spotify

---

