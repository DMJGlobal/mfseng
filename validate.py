import os
import time
import random
from supabase import create_client
from ddgs import DDGS
from groq import Groq

# Setup
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def validate_articles():
    articles = supabase.table("articles").select("*").eq("status", "p2").execute().data
    
    if not articles:
        print("No p2 articles to validate.")
        return

    for art in articles:
        # Randomized wait
        time.sleep(random.uniform(45, 90))
        
        # TRUNCATE QUERY: Only search the first 8 words to avoid "No results"
        search_query = " ".join(art['title'].split()[:8])
        print(f"Researching: {search_query}")
        
        search_snippets = []
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(search_query, max_results=5)]
                if not results:
                    print(f"No results found for: {search_query}")
                    continue
                for r in results:
                    search_snippets.append(f"Snippet: {r['body']}")
        except Exception as e:
            print(f"Search failed: {e}")
            continue

        prompt = f"Verify legitimacy of this topic: {art['title']}. Data: {search_snippets}. If real/professional, reply 'VALIDATED'. Else 'FAILED'."

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 
            )
            decision = completion.choices[0].message.content.strip()
            
            # FIX: Use 'url' to find the row instead of 'id'
            if "VALIDATED" in decision:
                supabase.table("articles").update({"status": "p3"}).eq("url", art['url']).execute()
                print(f"Result: SUCCESS (p3)")
            else:
                print(f"Result: FAILED")
                
        except Exception as e:
            print(f"AI Update Error: {e}")

if __name__ == "__main__":
    validate_articles()
