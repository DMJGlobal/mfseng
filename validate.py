import os
import time
import random
from supabase import create_client
from ddgs import DDGS # Updated library name
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
        # UPDATED TIMER: 45-90 seconds (Faster but still stealthy)
        wait = random.uniform(45, 90)
        print(f"Stealth Mode: Waiting {wait:.2f}s before searching...")
        time.sleep(wait)
        
        print(f"Researching: {art['title']}")
        
        # 2. Scour DuckDuckGo
        search_snippets = []
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(art['title'], max_results=5)]
                for r in results:
                    search_snippets.append(f"Source: {r['href']} | Snippet: {r['body']}")
        except Exception as e:
            print(f"Search failed: {e}")
            continue

        # 3. LIBRARIAN LOGIC (More inclusive than the "Detective")
        prompt = f"""
        ACT AS: A Professional Content Librarian.
        TITLE: {art['title']}
        SEARCH DATA: {search_snippets}

        VALIDATION RULES:
        1. If it's NEWS: Is it confirmed by at least one reputable source?
        2. If it's a GUIDE/HOW-TO: Is the topic being discussed by authoritative industry sites?
        3. If it's a SERIES/NEWSLETTER: Does the search prove this is a legitimate publication?
        
        FINAL DECISION:
        - If the topic is REAL, SUBSTANTIVE, and has a professional footprint, reply: "VALIDATED".
        - If the search results are empty, scammy, or suggest the content is fake, reply: "FAILED".
        """

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 
            )
            decision = completion.choices[0].message.content.strip()
            
            if "VALIDATED" in decision:
                supabase.table("articles").update({"status": "p3"}).eq("id", art['id']).execute()
                print(f"Result: SUCCESS (p3) - {art['title']}")
            else:
                print(f"Result: FAILED - {art['title']}")
                
        except Exception as e:
            print(f"AI Error: {e}")

if __name__ == "__main__":
    validate_articles()
