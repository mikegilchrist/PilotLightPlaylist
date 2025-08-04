# Version 1.4.8 (reverted: match only ALL CAPS names)

import argparse
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re

parser = argparse.ArgumentParser(description="Scrape Pilot Light upcoming events")
parser.add_argument("--week_start", type=int, default=0)
parser.add_argument("--week_stop", type=int, default=-1)
args = parser.parse_args()

start_week = args.week_start
stop_week = args.week_stop

URL = "https://thepilotlight.com"
IGNORE_PHRASES = ["Out Series", "UPDATE", "UPDATE!", "Improvised music sets"]

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")
paragraphs = soup.find_all("p")

today = datetime.today().date()
start_date = today + timedelta(weeks=start_week)
end_date = None if stop_week == -1 else today + timedelta(weeks=stop_week)

def parse_event(p):
    for tag in p.find_all(['s']):
        tag.decompose()

    text = p.get_text(separator="\n")
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)

    match = re.search(r"(\w+day)\s+(\w+)\s+(\d+).*?\$(FREE|\d+)", text, re.IGNORECASE)
    if not match:
        return None

    date_str = f"{match.group(2)} {match.group(3)} {datetime.today().year}"

    # parse both abbreviated and full month names
    for fmt in ("%b %d %Y", "%B %d %Y"):
        try:
            show_date = datetime.strptime(date_str, fmt).date()
            break
        except ValueError:
            show_date = None
    if show_date is None:
        print(f"Date parse error: '{date_str}' from text: {text}")
        return None

    print(f"Parsed show date: {show_date}, Today: {today}, Start: {start_date}")

    if show_date < start_date:
        print(f"Skipping past show: {show_date} < {start_date}")
        return None
    if end_date and show_date > end_date:
        print(f"Skipping future show: {show_date} > {end_date}")
        return None

    price = match.group(4).upper()

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    band_lines = []
    for line in lines:
        if any(phrase in line for phrase in IGNORE_PHRASES):
            continue
        if re.search(r"[A-Z]{2,}", line):
            band_lines.append(line)

    bands = []
    for line in band_lines:
        parts = re.split(r"with|and|,|/", line, flags=re.IGNORECASE)
        for part in parts:
            part = part.strip()
            if part.upper() in ["FREE", "UPDATE", "UPDATE!"]:
                continue
            if part and part.isupper():
                bands.append(part)

    if not bands:
        return None

    return f"{show_date} | {', '.join(bands)} | ${price}"

events = []
for p in paragraphs:
    result = parse_event(p)
    if result:
        events.append(result)

print("Upcoming events:")
for e in events:
    print(e)

filename = "upcoming_artists_all.txt" if stop_week == -1 else f"upcoming_artists_{today.strftime('%Y-%m-%d')}.txt"
with open(filename, "w", encoding="utf-8") as f:
    for e in events:
        f.write(e + "\n")

start_label = start_date.strftime("%b %d")
end_label = "" if stop_week == -1 else (end_date - timedelta(days=1)).strftime("%b %d")
if end_label:
    print(f"Suggested playlist title: Pilot Light Shows {start_label}–{end_label}")
else:
    print("Suggested playlist title: Pilot Light Playlist: Upcoming Shows")
