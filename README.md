# PilotLight Playlist Builder

## Overview

A modular system to scrape upcoming show information from thepilotlight.com,
look up each artist's top tracks on Spotify, and maintain two playlists:

- **Upcoming Shows** -- artists with future show dates
- **Recent Shows** -- artists whose shows have already happened

Backups of existing playlist contents are saved before every update for
safety and reproducibility.

---

## Quick Start

```bash
# Install dependencies
pip install -r required.libraries.txt

# Copy and edit config with your Spotify playlist IDs
cp config.yaml.example config.yaml

# Create .env with Spotify credentials (see Authentication below)

# Dry run -- scrapes site, searches Spotify, writes tmp-* files only
./create_pilotlight_playlist.py --dry-run --verbose

# Live run -- actually updates your Spotify playlists
./create_pilotlight_playlist.py --verbose
```

---

## Usage

```
create_pilotlight_playlist.py [OPTIONS] [filename]
```

### Options

| Flag              | Description                                                |
|-------------------|------------------------------------------------------------|
| `filename`        | Optional pre-scraped artist CSV (skips scraping)           |
| `--backup-only`   | Back up playlists without updating                         |
| `--dry-run`       | Write to `./tmp-*` files, do not update Spotify            |
| `--force`, `-f`   | Overwrite existing backup files without renaming           |
| `--verbose`       | Print detailed progress messages                           |
| `--debug`         | Write detailed log to `logs/` with full API/HTTP output    |
| `--help`, `-h`    | Show help message and exit                                 |

### Scraper Options (standalone)

```
pilotlight_scraper.py [--week_start N] [--week_stop M] [--filename FILE] [-v]
```

---

## How It Works

1. **Scrape** -- `pilotlight_scraper.py` fetches thepilotlight.com and
   extracts show dates, artist names, and ticket prices into a CSV with
   one row per artist:
   ```
   date,artist,price
   2025-09-17,COOPER,10
   2025-09-17,PEACE PURSUERS,10
   ```

2. **Split** -- Artists are split by date: future shows go to the
   "upcoming" playlist, past shows go to "recent".

3. **Search** -- For each artist, the top 3 tracks are fetched from
   Spotify using `artist_top_tracks()`.

4. **Update** -- The Spotify playlists are replaced with the found tracks.
   A CSV backup of the previous playlist contents is saved first.

---

## Playlist Configuration

Playlist names and IDs are in `config.yaml` (not tracked in git):

```yaml
playlists:
  upcoming:
    name: "Pilot Light Playlist: Upcoming Shows"
    id:   "your_upcoming_playlist_id"
  recent:
    name: "Pilot Light Playlist: Recent Shows"
    id:   "your_recent_playlist_id"
```

Use `get_playlist_ids.py` to list your Spotify playlists and find IDs.

---

## Authentication

Create a `.env` file in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:9090
```

The first run will open a browser for Spotify OAuth.  Subsequent runs use
a cached token at `~/.cache/spotify_token.json`.

---

## Cron Setup

A wrapper script is provided for unattended weekly runs:

```bash
# Edit run_pilotlight_cron.sh to remove --dry-run when ready
crontab -e
# Add:
0 8 * * 1 /home/mikeg/Repositories/PilotLightPlaylist/run_pilotlight_cron.sh
```

The cron script:
- Changes to the repo directory
- Loads `.env` credentials
- Activates a virtualenv if present at `./venv`
- Runs the updater (starts in `--dry-run` mode by default)
- Logs output to `logs/cron_YYYY-MM-DD.log`

---

## File Overview

| File                            | Purpose                                      |
|---------------------------------|----------------------------------------------|
| `create_pilotlight_playlist.py` | Main driver: scrape, split, update playlists |
| `pilotlight_scraper.py`         | Web scraper for thepilotlight.com            |
| `playlist_utils.py`             | Spotify helpers: auth, backup, search, update|
| `get_playlist_ids.py`           | List Spotify playlists and IDs               |
| `run_pilotlight_cron.sh`        | Cron wrapper script                          |
| `config.yaml`                   | Playlist IDs and names (not in git)          |
| `.env`                          | Spotify credentials (not in git)             |
| `add_to_playlist.py`            | Deprecated -- use create_pilotlight_playlist |

---

## Dependencies

- Python 3.10+
- `requests`, `beautifulsoup4`, `spotipy`, `python-dotenv`, `pyyaml`,
  `python-dateutil`

```bash
pip install -r required.libraries.txt
```

---

## Debug Mode

Pass `--debug` to write a detailed log to `logs/debug_YYYY-MM-DD_HHMM.log`
with HTTP response details, Spotify API search payloads, and full artist
match results.  Debug mode implies `--verbose`.

---

## Backup Strategy

- Playlist contents are backed up to CSV before every update
- Files are timestamped (`playlist_upcoming-artists_YYYY-MM-DD_HHMM.csv`)
- Existing files are renamed with a numeric suffix unless `--force` is used
- Dry-run output goes to `./tmp-*` files (excluded from git)
