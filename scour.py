import os
import time
import random
from supabase import create_client
from ddgs import DDGS
from groq import Groq

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def deep_scour():
    # Only pick up articles you moved to p4
    articles = supabase.table("articles").select("*").eq("status", "p4").execute().data
    
    if not articles:
        print("No p4 articles waiting for deep research.")
        return

    for art in articles:
        time.sleep(random.uniform(45, 90)) # Stealth timer
        print(f"Deep Researching: {art['title']}")
        
        # Targeted search queries for depth
        queries = [
            f"{art['title']} key facts and details",
            f"{art['title']} statistics and expert opinions"
        ]
        
        raw_intel = ""
        with DDGS() as ddgs:
            for q in queries:
                results = [r for r in ddgs.text(q, max_results=5)]
                for r in results:
                    raw_intel += f"\nSource: {r['href']}\nIntel: {r['body']}\n"
                time.sleep(5) # Small gap between searches

        # Summarize intel into a structured fact-sheet for the writer
        prompt = f"Based on this raw data, extract a bulleted list of the 10 most important facts, dates, and names for an article about: {art['title']}. Data: {raw_intel}"

        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            fact_sheet = completion.choices[0].message.content
            
            # Save the fact sheet and move to p5
            supabase.table("articles").update({
                "content_p5": fact_sheet,
                "status": "p5"
            }).eq("url", art['url']).execute()
            print(f"Result: SUCCESS (p5) - Research gathered for {art['title']}")
                
        except Exception as e:
            print(f"Scour Error: {e}")

if __name__ == "__main__":
    deep_scour()
