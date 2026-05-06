import os
from supabase import create_client

# Connect to your Heart (Supabase)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Your Phase 1 list mapped with categories
feed_data = [
    {"category": "AI", "rss_url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"category": "AI", "rss_url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"category": "AI", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/ai/"},
    {"category": "AI", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/ai-governance-policy/"},
    {"category": "AI", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/ai-infrastructure/"},
    {"category": "AI", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/artificial-intelligence/"},
    {"category": "AI", "rss_url": "https://bair.berkeley.edu/blog/feed.xml"},
    {"category": "AI", "rss_url": "https://arstechnica.com/ai/feed/"},
    {"category": "AI", "rss_url": "https://aiweekly.co/feed/"},
    {"category": "Cloud Computing", "rss_url": "https://techcrunch.com/tag/cloud-computing/feed/"},
    {"category": "Crypto", "rss_url": "https://techcrunch.com/category/cryptocurrency/feed/"},
    {"category": "Crypto", "rss_url": "https://cointelegraph.com/rss"},
    {"category": "Crypto", "rss_url": "https://news.bitcoin.com/feed/"},
    {"category": "Crypto", "rss_url": "https://cryptobriefing.com/feed/"},
    {"category": "Crypto", "rss_url": "https://www.newsbtc.com/feed/"},
    {"category": "Crypto", "rss_url": "https://cryptopotato.com/feed/"},
    {"category": "Crypto", "rss_url": "https://cryptonews.com/news/feed/"},
    {"category": "EV", "rss_url": "https://techcrunch.com/tag/evs/feed/"},
    {"category": "Fintech", "rss_url": "https://techcrunch.com/category/fintech/feed/"},
    {"category": "Fintech", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/fintech/"},
    {"category": "Fintech", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/payments/"},
    {"category": "Gadgets", "rss_url": "https://techcrunch.com/category/gadgets/feed/"},
    {"category": "Robotics", "rss_url": "https://techcrunch.com/category/robotics/feed/"},
    {"category": "Robotics", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/robotics/"},
    {"category": "Robotics", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/robots/"},
    {"category": "Tech", "rss_url": "https://www.theverge.com/rss/tech/index.xml"},
    {"category": "Tech", "rss_url": "https://www.bleepingcomputer.com/feed/"},
    {"category": "Tech", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/enterprise-technology/"},
    {"category": "Apple", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/apple/"},
    {"category": "Android", "rss_url": "https://www.techrepublic.com/rssfeeds/topic/android/"}
]

# Push to Supabase
for feed in feed_data:
    try:
        supabase.table("feeds").insert(feed).execute()
        print(f"Added: {feed['rss_url']}")
    except Exception as e:
        print(f"Already exists or error: {feed['rss_url']}")
