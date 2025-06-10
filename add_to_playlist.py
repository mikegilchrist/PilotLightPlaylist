# Version 1.3.1

import os
import sys
import re
import csv
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load from .env if present
load_dotenv()

# Fallback to environment or .env file (correct keys)
SPOTIPY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:9090")

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    print("Error: Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as environment variables or in a .env file.")
    sys.exit(1)

SCOPE = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

def extract_band_names(filename):
    band_names = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                bands_part = parts[1].strip()
                bands = [b.strip() for b in bands_part.split(",") if b.strip()]
                band_names.extend(bands)
    return band_names  # keep order

def create_playlist(title):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=title, public=True)
    return playlist["id"], playlist["external_urls"]["spotify"]

def find_exact_artist_match(band):
    results = sp.search(q=f"artist:{band}", type="artist", limit=5)
    for artist in results.get("artists", {}).get("items", []):
        if artist["name"].lower() == band.lower():
            return artist
    return None

def add_top_tracks_to_playlist(band_names, playlist_id, output_csv, max_tracks_per_artist=2):
    track_uris = []
    all_tracks = []

    for band in band_names:
        artist = find_exact_artist_match(band)
        if artist:
            artist_id = artist["id"]
            artist_genres = ", ".join(artist.get("genres", []))
            top_tracks = sp.artist_top_tracks(artist_id)["tracks"][:max_tracks_per_artist]
            for track in top_tracks:
                uri = track["uri"]
                name = track["name"]
                artist_name = track["artists"][0]["name"]
                url = track["external_urls"]["spotify"]
                duration_ms = track["duration_ms"]
                duration_min = round(duration_ms / 60000, 2)
                album = track["album"]["name"]
                all_tracks.append([artist_name, name, url, album, artist_genres, duration_min])
                track_uris.append(uri)

    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Artist", "Track", "Spotify URL", "Album", "Genres", "Duration (min)"])
        writer.writerows(all_tracks)

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_to_playlist.py <artist_file.txt> [playlist_name]")
        sys.exit(1)

    artist_file = sys.argv[1]
    playlist_title = sys.argv[2] if len(sys.argv) > 2 else f"Pilot Light Playlist {datetime.today().strftime('%Y-%m-%d')}"

    band_names = extract_band_names(artist_file)
    playlist_id, playlist_url = create_playlist(playlist_title)

    csv_filename = f"playlist_tracks_{datetime.today().strftime('%Y-%m-%d')}.csv"
    add_top_tracks_to_playlist(band_names, playlist_id, csv_filename)

    print(f"\nPlaylist '{playlist_title}' created: {playlist_url}")
    print(f"Tracklist saved to: {csv_filename}")

if __name__ == "__main__":
    main()
