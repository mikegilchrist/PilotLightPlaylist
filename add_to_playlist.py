# Version 1.8.0

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

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:9090")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("Error: Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as environment variables or in a .env file.")
    sys.exit(1)

SCOPE = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))

def extract_band_names(filename):
    upcoming = []
    past = []
    today = datetime.today().date()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 2:
                date_str = parts[0].strip()
                try:
                    show_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue
                bands_part = parts[1].strip()
                bands = [b.strip() for b in bands_part.split(",") if b.strip()]
                if show_date < today:
                    past.extend(bands)
                else:
                    upcoming.extend(bands)
    return upcoming, past

def find_or_create_playlist(title):
    user_id = sp.current_user()["id"]
    playlists = sp.current_user_playlists(limit=50)["items"]
    for pl in playlists:
        if pl["name"] == title:
            return pl["id"], pl["external_urls"]["spotify"]
    playlist = sp.user_playlist_create(user=user_id, name=title, public=True)
    return playlist["id"], playlist["external_urls"]["spotify"]

def find_exact_artist_match(band):
    results = sp.search(q=f"artist:{band}", type="artist", limit=5)
    for artist in results.get("artists", {}).get("items", []):
        if artist["name"].lower() == band.lower():
            return artist
    return None

def get_current_playlist_track_uris(playlist_id):
    track_uris = set()
    results = sp.playlist_items(playlist_id, limit=100)
    while results:
        for item in results["items"]:
            track = item.get("track")
            if track:
                track_uris.add(track["uri"])
        if results.get("next"):
            results = sp.next(results)
        else:
            break
    return track_uris

def sync_top_tracks(band_names, playlist_id, max_tracks_per_artist=2):
    current_uris = get_current_playlist_track_uris(playlist_id)
    desired_uris = set()

    for band in band_names:
        artist = find_exact_artist_match(band)
        if artist:
            top_tracks = sp.artist_top_tracks(artist["id"])["tracks"][:max_tracks_per_artist]
            for track in top_tracks:
                desired_uris.add(track["uri"])

    to_add = list(desired_uris - current_uris)
    to_remove = list(current_uris - desired_uris)

    if to_remove:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, to_remove)
    if to_add:
        sp.playlist_add_items(playlist_id, to_add)

def append_top_tracks(band_names, playlist_id, max_tracks_per_artist=2):
    for band in band_names:
        artist = find_exact_artist_match(band)
        if artist:
            top_tracks = sp.artist_top_tracks(artist["id"])["tracks"][:max_tracks_per_artist]
            uris = [track["uri"] for track in top_tracks]
            if uris:
                sp.playlist_add_items(playlist_id, uris)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <artist_file.txt>")
        sys.exit(1)

    artist_file = sys.argv[1]
    upcoming_bands, past_bands = extract_band_names(artist_file)

    upcoming_id, upcoming_url = find_or_create_playlist("Pilot Light Playlist: Upcoming Shows")
    recent_id, recent_url = find_or_create_playlist("Pilot Light Playlist: Recent Shows")

    # Smart sync upcoming playlist
    sync_top_tracks(upcoming_bands, upcoming_id)

    # Append new past bands to recent playlist
    append_top_tracks(past_bands, recent_id)

    print(f"\nUpdated: {upcoming_url}")
    print(f"Added past shows to: {recent_url}")

if __name__ == "__main__":
    main()
