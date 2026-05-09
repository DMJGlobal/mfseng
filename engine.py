import os
import feedparser
import time
import random
from datetime import datetime
from supabase import create_client

# 1. Connect to Supabase (The Articles Vault)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_and_save():
    # 2. PRIVACY UPDATE: Fetch feeds from GitHub Secret instead of Supabase Table
    raw_feeds = os.environ.get("RSS_FEEDS_LIST")
    
    if not raw_feeds:
        print("Error: RSS_FEEDS_LIST secret is empty or missing.")
        return

    # Split the secret into individual lines and clean them up
    feed_lines = [line.strip() for line in raw_feeds.strip().split("\n") if "|" in line]
    
    print(f"Scout Engine: Checking {len(feed_lines)} private sources...")

    for line in feed_lines:
        # Split each line by the pipe symbol (Category|URL)
        category, rss_url = line.split("|")
        
        # STEALTH: Wait between checking different sources
        delay = random.uniform(26, 105)
        print(f"Stealth Mode: Waiting {delay:.2f}s before checking {category}...")
        time.sleep(delay)
        
        # 3. Parse the News
        d = feedparser.parse(rss_url)
        
        for entry in d.entries:
            data = {
                "title": entry.title,
                "url": entry.link,
                "source_name": d.feed.title if 'title' in d.feed else category,
                "category": category,
                "status": "p1",
                "fetched_at": datetime.utcnow().isoformat() # Keeps your timeline accurate
            }
            
            try:
                # Insert into Supabase (Duplicates will fail automatically via the 'url' constraint)
                supabase.table("articles").insert(data).execute()
                print(f"Saved: {entry.title}")
            except:
                # If article already exists, the engine simply moves to the next one
                continue

if __name__ == "__main__":
    fetch_and_save()
