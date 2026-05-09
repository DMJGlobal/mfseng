import os
import time
import random
from supabase import create_client
import google.generativeai as genai

# Setup Connections
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

def generate_narratives():
    # Fetch articles ready for drafting (p5)
    articles = supabase.table("articles").select("*").eq("status", "p5").execute().data
    
    if not articles:
        print("No p5 articles waiting for drafting.")
        return

    # Load Secret Instructions
    sme_data = os.environ.get("SME_PERSONAS", "").strip().split("\n")
    persona_map = {line.split("|")[0]: line.split("|")[1] for line in sme_data if "|" in line}
    
    category_map = os.environ.get("MASTER_CATEGORY_MAP", "").strip().split("\n")
    slop_rules = os.environ.get("ANTI_AI_SLOP_GUIDELINES", "")

    print(f"Drafting Engine: Processing {len(articles)} articles...")

    for art in articles:
        time.sleep(random.uniform(60, 90)) # Pacing for quality and rate limits
        
        # 1. Match Expert Persona
        expert_persona = persona_map.get(art['category'], "Senior Marketing Director with 15+ years experience")
        
        # 2. Filter relevant subcategories from the master map for the AI to choose from
        available_subs = [line.split("|")[1] for line in category_map if line.split("|")[0] == art['category']]
        subcategory_list = ", ".join(available_subs)

        print(f"Writing Narrative ({art['category']}): {art['title']}")

        # 3. The Comprehensive "Director" Prompt
        prompt = f"""
        {slop_rules}

        <context_layering>
        ACT AS: {expert_persona}
        TOPIC: {art['title']}
        FACTUAL_BACKBONE: 
        {art['content_p5']}
        </context_layering>

        <structural_parameters>
        - Format: 800+ word deep-dive feature article.
        - Architecture: Follow the 'Five-Boxes' journalistic structure (Hook, Nut Graph, Secondary Lead/Context, Midpoint Pivot, Forward-Looking Resolution).
        - No 'summary' conclusions. End with a 'Kicker'—actionable momentum or industry projection.
        </structural_parameters>

        <metadata_and_taxonomy>
        1. SUBCATEGORY SELECTION: From the list [{subcategory_list}], select the most relevant one. Output as: 'Subcategory: [Choice]'
        2. META DESCRIPTION: Write a 100-120 character hook for search engines.
        3. TAGS: Provide 4 or 5 relevant tags (max 4 words per tag, minimum 2 words per tag).
        4. IMAGE PLANNING:
           - FEATURED_IMAGE: Provide a specific image search term for Pexels/Pixabay.
           - INLINE_IMAGE_1: Provide a search term and indicate placement after a specific and relevant paragraph.
           - INLINE_IMAGE_2: Provide a search term and indicate placement after a specific and relevant paragraph.
        </metadata_and_taxonomy>

        <editorial_directive>
        Ensure every sentence is inextricably linked to the provided facts. Delete all probabilistic smoothing or generic transitions. 
        Use active verbs. Avoid nominalizations. Demonstrate profound understanding of the audience's pain points.
        </editorial_directive>
        """

        try:
            response = model.generate_content(prompt)
            full_draft = response.text
            
            # Save draft and promote to p6 (Executive Review)
            supabase.table("articles").update({
                "content_p5": full_draft,
                "status": "p6"
            }).eq("url", art['url']).execute()
            print(f"Result: SUCCESS (p6) - Narrative complete for {art['title']}")
                
        except Exception as e:
            print(f"Drafting Error for {art['title']}: {e}")

if __name__ == "__main__":
    generate_narratives()
