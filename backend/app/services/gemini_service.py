import json
import re
import logging
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import (
    OpenAIStructuredCampaignResponse,
    CampaignTypeEnum,
    DemographicsSchema,
    GenderEnum,
    AdVariantSchema
)

logger = logging.getLogger(__name__)

# ─── Strict JSON system prompt for Gemini ────────────────────────────────────
SYSTEM_INSTRUCTION = """You are an expert Google Ads Campaign Architect.

Your ONLY job is to analyze the user's business description, target location, and budget,
then respond with a SINGLE valid JSON object — no markdown fences, no explanation, no extra text.

The JSON must match this schema EXACTLY:
{
  "campaign_type": "SEARCH" | "DISPLAY" | "PERFORMANCE_MAX",
  "negative_keywords": ["<str>", "<str>", "<str>"],
  "demographics": {
    "age_ranges": ["<str>", ...],
    "genders": ["MALE", "FEMALE", "UNDETERMINED"]
  },
  "keywords": ["<str>", "<str>", "<str>", "<str>", "<str>"],
  "ad_variants": [
    {
      "headlines": ["<max 30 chars>", "<max 30 chars>", "<max 30 chars>"],
      "descriptions": ["<max 90 chars>", "<max 90 chars>"]
    },
    { ... },
    { ... }
  ]
}

STRICT RULES — violating any rule makes the output invalid:
1. Return EXACTLY 3 items in negative_keywords.
2. Return EXACTLY 5 items in keywords — all highly intent-driven for the business.
3. Return EXACTLY 3 ad_variants.
4. Each ad_variant must have EXACTLY 3 headlines and EXACTLY 2 descriptions.
5. Every headline must be 30 characters or fewer (count carefully including spaces).
6. Every description must be 90 characters or fewer.
7. Do NOT include any text outside the JSON object. No markdown. No comments.
"""

# ─── Trim helpers to guarantee character limits ───────────────────────────────
def _trim(text: str, limit: int) -> str:
    """Hard-trim text to character limit, breaking at last space to avoid mid-word cuts."""
    if len(text) <= limit:
        return text
    trimmed = text[:limit]
    last_space = trimmed.rfind(' ')
    return (trimmed[:last_space] if last_space > limit // 2 else trimmed).rstrip()


def _safe_headlines(raw: list) -> list:
    """Return exactly 3 headlines each ≤ 30 chars."""
    headlines = [_trim(str(h), 30) for h in (raw or [])]
    while len(headlines) < 3:
        headlines.append("Learn More Today"[:30])
    return headlines[:3]


def _safe_descriptions(raw: list) -> list:
    """Return exactly 2 descriptions each ≤ 90 chars."""
    descs = [_trim(str(d), 90) for d in (raw or [])]
    while len(descs) < 2:
        descs.append("Contact us today to learn about our services and get started fast."[:90])
    return descs[:2]


# ─── Parse raw Gemini text → schema object ───────────────────────────────────
def _parse_gemini_response(raw_text: str) -> OpenAIStructuredCampaignResponse:
    """
    Robustly extract JSON from Gemini response text and map into our schema.
    Handles cases where the model accidentally wraps output in markdown fences.
    """
    # Strip markdown code fences if present
    cleaned = raw_text.strip()
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'```\s*$', '', cleaned, flags=re.MULTILINE).strip()

    # Find the outermost JSON object
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in Gemini response: {raw_text[:300]}")
    json_str = cleaned[start:end + 1]

    data = json.loads(json_str)

    # Map campaign_type safely
    raw_type = str(data.get("campaign_type", "SEARCH")).upper()
    try:
        campaign_type = CampaignTypeEnum(raw_type)
    except ValueError:
        campaign_type = CampaignTypeEnum.SEARCH

    # Demographics
    demo_raw = data.get("demographics", {})
    demographics = DemographicsSchema(
        age_ranges=demo_raw.get("age_ranges", ["25-34", "35-44"]),
        genders=[
            GenderEnum(g) if g in [e.value for e in GenderEnum]
            else GenderEnum.UNDETERMINED
            for g in demo_raw.get("genders", ["MALE", "FEMALE", "UNDETERMINED"])
        ]
    )

    # Keywords (exactly 5)
    keywords = [str(k) for k in data.get("keywords", [])][:5]
    while len(keywords) < 5:
        keywords.append("best service near me")

    # Negative keywords (exactly 3)
    neg_keywords = [str(k) for k in data.get("negative_keywords", [])][:3]
    while len(neg_keywords) < 3:
        neg_keywords.append("free trial")

    # Ad variants (exactly 3)
    raw_variants = data.get("ad_variants", [])
    ad_variants = []
    for v in raw_variants[:3]:
        ad_variants.append(AdVariantSchema(
            headlines=_safe_headlines(v.get("headlines", [])),
            descriptions=_safe_descriptions(v.get("descriptions", []))
        ))
    # Pad if Gemini returned fewer than 3
    while len(ad_variants) < 3:
        ad_variants.append(AdVariantSchema(
            headlines=["Top Service Available", "Call Us Today", "Get a Free Quote"],
            descriptions=[
                "We provide expert services tailored to your needs. Reach out today!",
                "Quality guaranteed. Book online or call for a free consultation now."
            ]
        ))

    return OpenAIStructuredCampaignResponse(
        campaign_type=campaign_type,
        negative_keywords=neg_keywords,
        demographics=demographics,
        keywords=keywords,
        ad_variants=ad_variants
    )


# ─── Smart rule-based fallback (no API key needed) ───────────────────────────
def _smart_mock(prompt: str, location: str, budget: float) -> OpenAIStructuredCampaignResponse:
    """Keyword-extraction based local fallback used when no API key is available."""
    stopwords = {
        "a","an","the","we","our","us","are","is","want","to","for","with","from",
        "on","at","in","near","and","or","of","local","business","boutique","service",
        "services","aiming","trying","scale","get","more","increase","boost","leads",
        "customers","sales","signups","help","best","top","online","shop","store",
        "company","agency","provider","i","my","am","about","how","its","it"
    }
    words = prompt.split()

    # Extract location from prompt if not provided
    loc = location or "Local Area"
    if not location:
        for pre in ["in", "near", "at", "around"]:
            lower_words = [w.lower() for w in words]
            if pre in lower_words:
                idx = lower_words.index(pre)
                candidates = [words[i].strip(".,!?;:") for i in range(idx+1, min(idx+3, len(words)))]
                if candidates:
                    loc = " ".join(candidates)
                    break

    # Extract main keyword
    filtered = [w.strip(".,!?;:()").title() for w in words
                if w.strip(".,!?;:()").lower() not in stopwords and w.isalpha()]
    keyword = " ".join(filtered[:2]) if len(filtered) >= 2 else (filtered[0] if filtered else "Business")

    kw, l = keyword.strip(), loc.strip()

    def h(text): return _trim(text, 30)
    def d(text): return _trim(text, 90)

    return OpenAIStructuredCampaignResponse(
        campaign_type=CampaignTypeEnum.SEARCH,
        negative_keywords=[f"free {kw}"[:30], f"cheap {kw}"[:30], f"{kw} jobs"[:30]],
        demographics=DemographicsSchema(
            age_ranges=["22-34", "35-44", "45-54"],
            genders=[GenderEnum.FEMALE, GenderEnum.MALE, GenderEnum.UNDETERMINED]
        ),
        keywords=[
            f"{kw} {l}".lower(), f"best {kw}".lower(),
            f"top {kw} near me".lower(), f"buy {kw} online".lower(),
            f"premium {kw} services".lower()
        ],
        ad_variants=[
            AdVariantSchema(
                headlines=[h(f"Best {kw} Service"), h(f"Top {kw} in {l}"), h(f"Get 20% Off {kw}")],
                descriptions=[
                    d(f"Looking for {kw} in {l}? Call our specialists today!"),
                    d(f"Professional {kw} services tailored to your budget. Order now!")
                ]
            ),
            AdVariantSchema(
                headlines=[h(f"Expert {kw} Help"), h(f"Top {kw} Near {l}"), h(f"Book {kw} Online")],
                descriptions=[
                    d(f"Unlock top-rated {kw} services. Expert support and 24/7 help."),
                    d(f"Get premium {kw} with zero hassle. Book for seasonal discounts.")
                ]
            ),
            AdVariantSchema(
                headlines=[h(f"Premium {kw}"), h(f"Trusted {kw} Services"), "Special Promo Pricing"],
                descriptions=[
                    d(f"Find out why we're the leading {kw} provider in {l}. Call now."),
                    d(f"High-quality {kw} packages. Great reliability, 5-star rating.")
                ]
            )
        ]
    )


# ─── Main public function ─────────────────────────────────────────────────────
def generate_campaign_with_gemini(
    prompt: str,
    location: str = None,
    budget: float = 50.0,
    website_url: str = None
) -> OpenAIStructuredCampaignResponse:
    """
    Primary entry point. Calls Gemini 1.5 Flash with a strict JSON system prompt.
    Falls back gracefully to the smart rule-based mock if the API key is missing.
    """
    api_key = settings.gemini_api_key

    if not api_key or api_key.startswith("YOUR_"):
        logger.info("GEMINI_API_KEY not set — using smart rule-based mock generator.")
        return _smart_mock(prompt, location, budget)

    # Build the user message
    user_parts = [f"Business Prompt: {prompt}"]
    if location:
        user_parts.append(f"Target Location: {location}")
    if budget:
        user_parts.append(f"Daily Budget: {budget} USD")
    if website_url:
        user_parts.append(f"Website URL: {website_url}")
    user_message = "\n".join(user_parts)

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                response_mime_type="application/json",
            )
        )

        raw_text = response.text
        logger.info(f"Gemini raw response (first 200 chars): {raw_text[:200]}")

        return _parse_gemini_response(raw_text)

    except Exception as e:
        logger.error(f"Gemini API error: {e}. Falling back to smart mock.")
        return _smart_mock(prompt, location, budget)
