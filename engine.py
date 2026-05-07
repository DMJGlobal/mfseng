import os
import feedparser
import time
import random
from datetime import datetime
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_and_save():
    feeds = supabase.table("feeds").select("*").execute().data
    
    for feed in feeds:
        delay = random.uniform(26, 105)
        print(f"Waiting {delay:.2f}s before checking {feed['category']}...")
        time.sleep(delay)
        
        d = feedparser.parse(feed['rss_url'])
        
        for entry in d.entries:
            data = {
                "title": entry.title,
                "url": entry.link,
                "source_name": d.feed.title if 'title' in d.feed else feed['category'],
                "category": feed['category'],
                "status": "p1",
                "fetched_at": datetime.utcnow().isoformat() # NEW: Captures fetch time
            }
            
            try:
                supabase.table("articles").insert(data).execute()
                print(f"Saved: {entry.title}")
            except:
                continue

if __name__ == "__main__":
    fetch_and_save()
