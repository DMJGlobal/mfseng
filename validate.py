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
        # FASTER STEALTH TIMER: 45-90 seconds per search
        wait = random.uniform(45, 90)
        print(f"Stealth Mode: Waiting {wait:.2f}s before searching...")
        time.sleep(wait)
        
        print(f"Researching: {art['title']}")
        
        # 2. Scour DuckDuckGo (Top 5 Snippets)
        search_snippets = []
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(art['title'], max_results=5)]
                for r in results:
                    search_snippets.append(f"Source: {r['href']} | Snippet: {r['body']}")
        except Exception as e:
            print(f"Search failed: {e}")
            continue

        # 3. Fragmented Librarian Logic (Groq Llama 3.3 70B)
        prompt = f"""
        ACT AS: A Professional Content Librarian.
        TITLE: {art['title']}
        DATA: {search_snippets}

        VALIDATION RULES:
        1. If it's NEWS: Is it confirmed by multiple sources or a major news outlet?
        2. If it's a GUIDE/HOW-TO: Is it being discussed by authoritative industry sites?
        3. If it's a SERIES/NEWSLETTER: Does the search prove this is a legitimate publication series?
        
        FINAL DECISION:
        - If the topic is substantive, real, and has a professional footprint in the search data, reply: "VALIDATED".
        - If the search results are empty, spammy, or suggest the content is fake, reply: "FAILED".
        """

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 
            )
            decision = completion.choices[0].message.content.strip()
            
            # 4. Update Status in Supabase
            if "VALIDATED" in decision:
                supabase.table("articles").update({"status": "p3"}).eq("id", art['id']).execute()
                print(f"Result: SUCCESS (p3) - {art['title']}")
            else:
                print(f"Result: FAILED - {art['title']}")
                
        except Exception as e:
            print(f"AI Error: {e}")

if __name__ == "__main__":
    validate_articles()
