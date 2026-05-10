import os
import time
import random
from supabase import create_client
from google import genai

# 1. Setup Connections - Explicitly targeting the v1 Stable API
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'}
) # FIXED: Added missing closing bracket

def generate_narratives():
    # FIXED: Added missing quote and proper indentation
    print("AUDIT: Phase 8 Writer (model gemini-3-flash) is active.")
    # Only target articles that have finished research (p5)
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
        time.sleep(random.uniform(30, 60))
        
        # Match Expert Persona and Filter Subcategories
        expert_persona = persona_map.get(art['category'], "Senior Marketing Director with 15+ years experience")
        available_subs = [line.split("|")[1] for line in category_map if line.split("|")[0] == art['category']]
        subcategory_list = ", ".join(available_subs)

        print(f"Writing Narrative ({art['category']}): {art['title']}")

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
        - Architecture: Follow the 'Five-Boxes' journalistic structure (Hook, Nut Graph, Secondary Lead, Midpoint Pivot, Forward-Looking Resolution).
        - No 'summary' conclusions. End with a 'Kicker'.
        </structural_parameters>

        <metadata_and_taxonomy>
        1. SUBCATEGORY SELECTION: From [{subcategory_list}], select the most relevant one. Output as: 'Subcategory: [Choice]'
        2. META DESCRIPTION: Write a 100-120 character hook.
        3. TAGS: Provide 4-5 relevant tags (max 4 words per tag, minimum 2 words per tag).
        4. IMAGE PLANNING: Provide search terms for FEATURED_IMAGE and 2 INLINE_IMAGES with specific placements.
        </metadata_and_taxonomy>

        <editorial_directive>
        Ensure every sentence is inextricably linked to the provided facts. Delete all generic transitions. 
        Use active verbs. Avoid nominalizations.
        </editorial_directive>
        """

        try:
            # Modern gemini-2.5-pro MODEL
            response = client.models.generate_content(
                model='gemini-3-flash',
                contents=prompt
            )
            full_draft = response.text
            
            # Save the draft and promote to p6
            supabase.table("articles").update({
                "content_p5": full_draft,
                "status": "p6"
            }).eq("url", art['url']).execute()
            print(f"Result: SUCCESS (p6) - Narrative complete for {art['title']}")
                
        except Exception as e:
            print(f"Drafting Error for {art['title']}: {e}")

if __name__ == "__main__":
    generate_narratives()
