# CLAUDE.md -- PilotLight Playlist Builder

## Project Purpose

Scrapes upcoming concert listings from thepilotlight.com (a music venue in
Knoxville, TN), looks up each artist on Spotify, and maintains two public
playlists: one for upcoming shows and one for recent (past) shows.

## Architecture

```
pilotlight_scraper.py   -- scrape website -> CSV (date,artist,price)
       |
create_pilotlight_playlist.py  -- main driver
       |
       +-- split by date -> upcoming artists / recent artists
       |
       +-- playlist_utils.py  -- Spotify auth, search, backup, update
              |
              +-- search_artist_top_tracks()  -- find artist, get 3 top tracks
              +-- update_playlist()           -- replace playlist with found tracks
              +-- backup_playlist()           -- save current playlist to CSV
```

## Key Files

| File                            | Role                                        |
|---------------------------------|---------------------------------------------|
| `create_pilotlight_playlist.py` | Entry point, orchestrates scrape and update  |
| `pilotlight_scraper.py`         | Scrapes thepilotlight.com, outputs CSV       |
| `playlist_utils.py`             | All Spotify API interactions                 |
| `config.yaml`                   | Playlist IDs (not in git)                    |
| `.env`                          | Spotify credentials (not in git)             |
| `run_pilotlight_cron.sh`        | Cron wrapper for weekly unattended runs      |

## Testing

```bash
# Scraper only
python pilotlight_scraper.py --verbose

# Full dry run (no Spotify changes)
python create_pilotlight_playlist.py --dry-run --verbose --debug

# Check output
cat tmp-upcoming-artists_*.csv
cat logs/debug_*.log
```

## Spotify OAuth

- Credentials in `.env` (SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
  SPOTIPY_REDIRECT_URI)
- Token cached at `~/.cache/spotify_token.json`
- First run requires a browser for OAuth; subsequent runs auto-refresh
- Scopes: playlist-modify-public, playlist-modify-private

## Config Structure (config.yaml)

```yaml
playlists:
  upcoming:
    name: "Pilot Light Playlist: Upcoming Shows"
    id:   "<spotify_playlist_id>"
  recent:
    name: "Pilot Light Playlist: Recent Shows"
    id:   "<spotify_playlist_id>"
```

## Conventions

- Filenames: lowercase, hyphens or underscores
- Scraped CSV format: `date,artist,price` (one artist per row)
- Backup CSV format: `Artist,Title,URI`
- Temp/dry-run files: prefixed with `tmp-` (git-ignored)
- Logs go to `logs/` directory (git-ignored)

## Important Notes

- `.env` and `config.yaml` contain credentials/secrets -- never commit them
- `add_to_playlist.py` is deprecated; use `create_pilotlight_playlist.py`
- The scraper relies on the website rendering band names in ALL CAPS;
  if the site redesigns, the parser will need updating
- `python-dateutil` is required for the year-boundary date fix
