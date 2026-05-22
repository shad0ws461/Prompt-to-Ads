from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import (
    CampaignGenerationRequest,
    CampaignResponse,
    DeployCampaignRequest
)
# Ensure standard naming check across your gemini_service.py file
try:
    from app.services.gemini_service import generate_campaign_with_ai as generate_campaign_with_gemini
except ImportError:
    from app.services.gemini_service import generate_campaign_with_gemini

from app.services.ads_service import deploy_campaign_to_google_ads
from app.services.oauth_service import get_google_auth_url, exchange_authorization_code
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend service for Prompt-to-Ads, generating and deploying campaigns automatically."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": settings.app_name,
        "environment": settings.environment
    }

@app.post("/api/generate-campaign", response_model=CampaignResponse)
async def api_generate_campaign(request: CampaignGenerationRequest):
    """
    Accepts business campaign prompts, location, budget, and website, 
    orchestrates with Gemini structured completions, and returns proposed configurations.
    """
    logger.info(f"Received campaign generation request for prompt: {request.prompt[:50]}...")
    
    start_time = time.time()
    try:
        ai_response = generate_campaign_with_gemini(
            prompt=request.prompt,
            location=request.target_location,
            budget=request.daily_budget or 50.0,
            website_url=request.website_url
        )

        generation_time = time.time() - start_time
        
        # Read key robustly from settings or env
        api_key = getattr(settings, "gemini_api_key", os.getenv("GEMINI_API_KEY"))
        is_mocked = not (api_key and not api_key.startswith("YOUR_") and api_key != "")

        return CampaignResponse(
            success=True,
            data=ai_response,
            raw_prompt=request.prompt,
            metadata={
                "processing_time_seconds": round(generation_time, 2),
                "timestamp": int(start_time),
                "ai_provider": "Google Gemini 1.5 Flash",
                "is_mocked": is_mocked
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/deploy-campaign")
async def api_deploy_campaign(request: DeployCampaignRequest):
    """
    Accepts campaign structure adjustments from the frontend and pushes them
    into the Google Ads API schema operations.
    """
    logger.info(f"Received deployment request for campaign: '{request.campaign_name}'")
    result = deploy_campaign_to_google_ads(request)
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(
            status_code=400, 
            detail=result
        )

@app.get("/api/oauth/url")
def api_get_oauth_url():
    """
    Returns the Google OAuth 2.0 URL needed to authenticate with Google Ads.
    """
    try:
        auth_url = get_google_auth_url()
        return {"url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oauth/callback")
def api_oauth_callback(
    code: str = Query(..., description="Google Auth Code"), 
    state: str = Query(None, description="Auth state identifier")
):
    """
    Receives authorization redirects from Google, exchanges authorization codes,
    and returns token credentials.
    """
    logger.info("Received callback from Google OAuth redirect.")
    result = exchange_authorization_code(code)
    
    if result.get("success"):
        return {
            "status": "authenticated",
            "message": "Successfully linked Google Ads Account.",
            "credentials": {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in")
            }
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"OAuth callback exchange failed: {result.get('error')}"
        )