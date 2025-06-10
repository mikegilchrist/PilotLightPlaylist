# Version 1.1.0

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import sys

# Step 1: Scrape upcoming artist info from thepilotlight.com (future events only)
def get_upcoming_artist_info(start_week=0, stop_week=3):
    url = "https://www.thepilotlight.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    today = datetime.today().date()
    start_date = today + timedelta(weeks=start_week)
    end_date = today + timedelta(weeks=stop_week)

    ignore_phrases = ["Out Series"]
    cancel_phrases = ["UPDATE", "UPDATE!"]

    paragraphs = soup.find_all("p")
    events = []

    for p in paragraphs:
        # Remove <s> tags and capture their contents
        struck_texts = set()
        for s in p.find_all("s"):
            struck_texts.update(re.findall(r"\b[A-Z][A-Z0-9\s&!'.-]+\b", s.get_text(separator=" ", strip=True)))
            s.extract()

        raw_text = p.get_text(separator=" ", strip=True)

        # Remove text between **...** (markdown-style emphasis)
        raw_text = re.sub(r"\*\*.*?\*\*", "", raw_text)

        # Skip if it's just an "Out Series" improvised music set
        if any(phrase in raw_text for phrase in ignore_phrases) and "Improvised music" in raw_text:
            continue

        clean_text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', raw_text)  # Remove ordinal suffixes

        # Try to extract date from the first part of the string
        match = re.match(r"^(\w+day) (\w+ \d+)(.*)", clean_text)
        if match:
            try:
                event_date = datetime.strptime(match.group(2), "%B %d").replace(year=today.year).date()
                if start_date <= event_date <= end_date:
                    filtered_text = raw_text

                    band_matches = re.findall(r"\b[A-Z][A-Z0-9\s&!'.-]+\b", filtered_text)
                    band_names = []
                    for b in band_matches:
                        name = b.strip()
                        if name in ignore_phrases or name in cancel_phrases or len(name) <= 1:
                            continue
                        if name in struck_texts:
                            continue
                        band_names.append(name)

                    # Extract pricing info
                    price_match = re.search(r"\$FREE|\$\d+", raw_text)
                    price_info = price_match.group() if price_match else ""

                    if band_names:
                        events.append({
                            "date": event_date,
                            "bands": band_names,
                            "info": price_info
                        })
            except ValueError:
                continue

    # Sort by date
    events.sort(key=lambda x: x["date"])
    return events, start_date, end_date

if __name__ == "__main__":
    start_week = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    stop_week = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    events, start_date, end_date = get_upcoming_artist_info(start_week, stop_week)
    print("Upcoming events:")

    date_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"upcoming_artists_{date_str}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        for event in events:
            event_line = f"{event['date'].strftime('%Y-%m-%d')} | {', '.join(event['bands'])} | {event['info']}"
            print(event_line)
            file.write(event_line + "\n")

    print(f"\nSaved to {filename}")

    # Construct playlist title with date range
    playlist_title = f"Pilot Light Shows {start_date.strftime('%b %d')}–{end_date.strftime('%b %d')}"
    print(f"Suggested playlist title: {playlist_title}")
