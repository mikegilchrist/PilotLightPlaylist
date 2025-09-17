# PilotLight Playlist Builder

## Overview

A modular system to scrape upcoming show information from thepilotlight.com, construct a Spotify playlist from the featured artists, and maintain versioned backups for reproducibility and safety.

---

## Usage Summary

Run the driver script with your desired options:

```
create_pilotlight_playlist.py [OPTIONS]
```

### Flags

| Flag              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `--verbose`, `-v` | Enable detailed logging                                                     |
| `--force`, `-f`   | Overwrite existing backup files without renaming                           |
| `--backup-only`   | Run the scraper and generate output files, but do not update Spotify       |
| `--week-start`    | ISO format date (YYYY-MM-DD) to start parsing events from                  |
| `--week-stop`     | Relative stop week (e.g., `-1` for last week, `0` for this week, etc.)     |
| `--help`, `-h`    | Show help message and exit                                                 |

---

## Example Workflows

### 1. Backup Playlists Without Updating Spotify

This will scrape upcoming events, build the list of artists, and save all intermediate files with timestamps, but **will not** update your Spotify playlists:

```bash
./create_pilotlight_playlist.py --backup-only --verbose
```

### 2. Restore Playlists from a Timestamped Backup

To restore a previous playlist (e.g., after accidental clearing), pass the saved file to `add_to_playlist.py` with the appropriate playlist configured in `config.yaml`:

```bash
./add_to_playlist.py data/upcoming_artists_all-2025-08-04_13-55.txt --playlist upcoming
```

Use `--playlist recent` to target the past shows playlist instead.

### 3. Update Playlists (Full Run)

This performs a full end-to-end scrape and update of both playlists:

```bash
./create_pilotlight_playlist.py --verbose
```

---

## Backup Strategy

- All generated files (`*.txt`, `*.csv`) are suffixed with the date and time in `YYYY-MM-DD_HH-MM` format.
- If a file with that name already exists, it will be renamed with a numeric suffix before being overwritten (e.g., `file-2025-08-04_13-55-1.csv`) **unless** you pass `--force`.
- This ensures historical data is preserved for debugging or restoration.

---

## Playlist Configurations

The playlist names and IDs are specified in `config.yaml`:

```yaml
playlists:
  upcoming:
    name: "Pilot Light Playlist: Upcoming Shows"
    id:   "your_upcoming_playlist_id"
  recent:
    name: "Pilot Light Playlist: Recent Shows"
    id:   "your_recent_playlist_id"
```

This decouples the script logic from hardcoded values, making playlist changes safer and more portable.

---

## Dependencies

- Python 3.10+
- `spotipy`, `requests`, `PyYAML`, `python-dotenv`

Install with:

```bash
pip install -r requirements.txt
```

---

## Authentication

Ensure you have a `.env` file with the following Spotify credentials:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

The `.env` file is automatically loaded if it exists in the project root.

---

## Error Handling

- Errors during scraping, file writing, or Spotify API interactions are logged with detailed context.
- Files are never overwritten without explicit `--force`.
- Scripts can be run independently or chained for testing, development, or recovery scenarios.
