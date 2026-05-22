import json
import logging
import os
import google.generativeai as genai
from app.config import settings
from app.schemas import (
    OpenAIStructuredCampaignResponse, 
    CampaignTypeEnum, 
    DemographicsSchema, 
    GenderEnum, 
    AdVariantSchema
)

logger = logging.getLogger(__name__)

def generate_mock_campaign(prompt: str, location: str = None, budget: float = 50.0) -> OpenAIStructuredCampaignResponse:
    """
    Generates a highly contextual mock campaign response based on the input prompt keywords
    using a Smart Rule-Based Mock Generator to support custom queries.
    """
    prompt_lower = prompt.lower()
    
    # Clean location logic
    target_loc = location
    words = prompt.split()
    
    if not target_loc:
        for pre in ["in", "near", "at", "around"]:
            if pre in [w.lower() for w in words]:
                try:
                    idx = [w.lower() for w in words].index(pre)
                    loc_candidates = []
                    for i in range(idx + 1, len(words)):
                        w = words[i].strip(".,?!;: ")
                        if w:
                            loc_candidates.append(w)
                        if len(loc_candidates) >= 2 or (i + 1 < len(words) and not words[i+1][0].isupper()):
                            break
                    target_loc = " ".join(loc_candidates)
                except:
                    pass
                    
    if target_loc:
        target_loc = target_loc.strip(".,?!;: ")
    else:
        target_loc = "Local Area"

    stopwords = {
        "a", "an", "the", "we", "our", "us", "are", "is", "want", "to", "for", "with", "from", "on", "at",
        "in", "near", "and", "or", "of", "local", "business", "boutique", "service", "services", "aiming",
        "trying", "scale", "get", "more", "increase", "boost", "leads", "customers", "sales", "signups",
        "help", "best", "top", "online", "shop", "store", "company", "agency", "provider"
    }
    
    filtered_words = [
        w.strip(".,?!;:()").title() 
        for w in words 
        if w.strip(".,?!;:()").lower() not in stopwords and w.isalpha()
    ]
    
    if len(filtered_words) >= 2:
        keyword = f"{filtered_words[0]} {filtered_words[1]}"
    elif len(filtered_words) == 1:
        keyword = filtered_words[0]
    else:
        keyword = "Business Services"
        
    keyword = keyword.strip()
    target_loc = target_loc.strip()

    h1_v1 = f"Best {keyword} Service"[:30]
    h2_v1 = f"Top Rated {keyword} in {target_loc}"[:30]
    h3_v1 = f"Get 20% Off {keyword}"[:30]
    
    h1_v2 = f"Expert {keyword} Help"[:30]
    h2_v2 = f"Best {keyword} Near {target_loc}"[:30]
    h3_v2 = f"Book {keyword} Online Now"[:30]
    
    h1_v3 = f"Premium {keyword} Solutions"[:30]
    h2_v3 = f"Trusted {keyword} Services"[:30]
    h3_v3 = "Special Promotional Pricing"[:30]

    if len(h3_v3) > 30: h3_v3 = "Special Promo Pricing"
    if len(h2_v1) > 30: h2_v1 = f"Top {keyword} in {target_loc}"[:30]
    if len(h2_v1) > 30: h2_v1 = f"{keyword} - {target_loc}"[:30]
    if len(h2_v2) > 30: h2_v2 = f"{keyword} in {target_loc}"[:30]

    d1_v1 = f"Looking for high-quality {keyword} in {target_loc}? Call our specialists today!"[:90]
    d2_v1 = f"We provide professional, certified {keyword} services tailored to your budget. Order now!"[:90]
    
    d1_v2 = f"Unlock top-rated {keyword} services. Satisfied clients, expert support and 24/7 help."[:90]
    d2_v2 = f"Get premium {keyword} with zero hassle. Book online for special seasonal discounts."[:90]
    
    d1_v3 = f"Find out why we are the leading choice for {keyword} in the {target_loc} region. Call now."[:90]
    d2_v3 = f"Get your quote on {keyword} packages. High efficiency, great reliability, 5-star rating."[:90]

    return OpenAIStructuredCampaignResponse(
        campaign_type=CampaignTypeEnum.SEARCH,
        negative_keywords=[
            f"cheap {keyword}"[:30], 
            f"free {keyword}"[:30], 
            f"jobs in {keyword}"[:30]
        ],
        demographics=DemographicsSchema(
            age_ranges=["22-34", "35-44", "45-54"],
            genders=[GenderEnum.FEMALE, GenderEnum.MALE, GenderEnum.UNDETERMINED]
        ),
        keywords=[
            f"{keyword} {target_loc}".lower(),
            f"best {keyword}".lower(),
            f"top {keyword} near me".lower(),
            f"buy {keyword} online".lower(),
            f"premium {keyword} services".lower()
        ],
        ad_variants=[
            AdVariantSchema(headlines=[h1_v1, h2_v1, h3_v1], descriptions=[d1_v1, d2_v1]),
            AdVariantSchema(headlines=[h1_v2, h2_v2, h3_v2], descriptions=[d1_v2, d2_v2]),
            AdVariantSchema(headlines=[h1_v3, h2_v3, h3_v3], descriptions=[d1_v3, d2_v3])
        ]
    )

def generate_campaign_with_ai(
    prompt: str, 
    location: str = None, 
    budget: float = 50.0, 
    website_url: str = None
) -> OpenAIStructuredCampaignResponse:
    """
    Calls Real Google Gemini API with native strict schema validation.
    Falls back to mock data generator if API key is missing or fails.
    """
    # config se gemini key check karega, agar missing ho toh environment variables se pull karega
    api_key = getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY"))
    
    if not api_key or api_key.startswith("YOUR_") or api_key == "":
        logger.info("Gemini API Key not set. Generating mock campaign data locally.")
        return generate_mock_campaign(prompt, location, budget)
        
    try:
        # Google SDK authentication config injection
        genai.configure(api_key=api_key)
        
        system_prompt = (
            "You are an expert Google Ads Campaign Architect.\n"
            "Your task is to analyze the user's business description, target location, and budget, "
            "then generate a highly optimized campaign structure matching the requested JSON schema.\n\n"
            "CRITICAL RULES:\n"
            "1. You must provide exactly 3 negative keywords to filter unqualified search intent.\n"
            "2. You must suggest a highly intent-driven set of target keywords (5-10 keywords).\n"
            "3. You must provide EXACTLY 3 ad variants.\n"
            "4. For EACH ad variant, you must provide EXACTLY 3 headlines and EXACTLY 2 descriptions.\n"
            "5. Character limits are STRICT:\n"
            "   - Headlines: Max 30 characters each.\n"
            "   - Descriptions: Max 90 characters each.\n"
            "6. Make the copy highly relevant to the business goal described in the prompt."
        )
        
        user_message = f"Business Prompt: {prompt}\n"
        if location:
            user_message += f"Target Location: {location}\n"
        if budget:
            user_message += f"Daily Budget: {budget} USD\n"
        if website_url:
            user_message += f"Website: {website_url}\n"

        # Initialize the model with the system instructions
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )
        
        # Pydantic Schema injection directly into Gemini GenerationConfig
        response = model.generate_content(
            user_message,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=OpenAIStructuredCampaignResponse,
                temperature=0.7
            )
        )
        
        # Parse text into json and instantiate the Pydantic Response Object
        json_dict = json.loads(response.text.strip())
        return OpenAIStructuredCampaignResponse(**json_dict)
            
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}. Falling back to mock generator.")
        return generate_mock_campaign(prompt, location, budget)
# cd backend    
# .\venv\Scripts\activate                                                             
# uvicorn app.main:app --port 8000