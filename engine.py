import os
import feedparser
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_and_save():
    # 1. Get all feeds from your database
    feeds = supabase.table("feeds").select("*").execute().data
    
    for feed in feeds:
        print(f"Checking {feed['category']}: {feed['rss_url']}")
        d = feedparser.parse(feed['rss_url'])
        
        for entry in d.entries:
            # Prepare the p1 data
            data = {
                "title": entry.title,
                "url": entry.link,
                "source_name": d.feed.title if 'title' in d.feed else feed['category'],
                "category": feed['category'],
                "status": "p1"
            }
            
            # 2. Try to save to articles table
            try:
                supabase.table("articles").insert(data).execute()
                print(f"Saved: {entry.title}")
            except:
                # This prevents duplicates because we set URL to 'unique'
                continue

if __name__ == "__main__":
    fetch_and_save()
