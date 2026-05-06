import os
import time
import random
from supabase import create_client
from duckduckgo_search import DDGS
from groq import Groq

# 1. Setup Clients
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def validate_articles():
    # Fetch articles you approved (p2)
    articles = supabase.table("articles").select("*").eq("status", "p2").execute().data
    
    if not articles:
        print("No p2 articles waiting for validation.")
        return

    print(f"Found {len(articles)} articles to validate.")

    for art in articles:
        # STEALTH TIMER: Wait a few seconds between searches
        wait = random.uniform(130, 250)
        print(f"Stealth Mode: Waiting {wait:.2f}s before searching...")
        time.sleep(wait)
        
        print(f"Investigating: {art['title']}")
        
        # 2. Scour DuckDuckGo (Top 5 Snippets)
        search_snippets = []
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(art['title'], max_results=5)]
                for r in results:
                    search_snippets.append(f"Source: {r['href']} | Snippet: {r['body']}")
        except Exception as e:
            print(f"Search failed for this item: {e}")
            continue

        # 3. Groq (Llama 3.3 70B) Decision Logic
        prompt = f"""
        TASK: Validate this news headline.
        HEADLINE: {art['title']}
        SEARCH DATA: {search_snippets}

        RULES:
        1. Is this news real, current, and verified by multiple sources in the snippets?
        2. If your confidence is 80% or higher, reply with exactly: "VALIDATED"
        3. If it is fake, old, or unverified, reply with exactly: "FAILED"
        """

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 # Keep it strictly factual
            )
            decision = completion.choices[0].message.content.strip()
            
            # 4. Update Status in Supabase
            if "VALIDATED" in decision:
                supabase.table("articles").update({"status": "p3"}).eq("id", art['id']).execute()
                print(f"Result: SUCCESS (p3) - {art['title']}")
            else:
                print(f"Result: FAILED - {art['title']}")
                
        except Exception as e:
            print(f"AI Logic Error: {e}")

if __name__ == "__main__":
    validate_articles()
