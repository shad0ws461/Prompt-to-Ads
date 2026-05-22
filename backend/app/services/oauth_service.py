import urllib.parse
import requests
import logging
from app.config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Scopes needed for Google Ads API access
GOOGLE_ADS_SCOPE = "https://www.googleapis.com/auth/adwords"

def get_google_auth_url() -> str:
    """
    Generates the Google OAuth 2.0 login URL for Ads authentication.
    """
    client_id = settings.google_client_id
    if not client_id or client_id.startswith("YOUR_"):
        # Fallback fake URL for client demonstration
        client_id = "mock_client_id_12345"
        
    params = {
        "client_id": client_id,
        "redirect_uri": settings.google_redirect_uri,
        "scope": GOOGLE_ADS_SCOPE,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": "prompt_to_ads_auth_state"
    }
    
    auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    auth_url = f"{auth_base_url}?{urllib.parse.urlencode(params)}"
    logger.info(f"Generated OAuth URL: {auth_url}")
    return auth_url

def exchange_authorization_code(code: str) -> Dict[str, Any]:
    """
    Exchanges authorization code for access and refresh tokens.
    """
    client_id = settings.google_client_id
    client_secret = settings.google_client_secret
    
    if not client_id or client_id.startswith("YOUR_") or not client_secret or client_secret.startswith("YOUR_"):
        logger.info("Using mock credentials for exchange token verification.")
        return {
            "success": True,
            "access_token": "mock_access_token_xyz_987654321",
            "refresh_token": "mock_refresh_token_abc_123456789",
            "expires_in": 3600,
            "scope": GOOGLE_ADS_SCOPE,
            "token_type": "Bearer"
        }
        
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(token_url, data=payload, timeout=10)
        response_data = response.json()
        
        if response.status_code == 200:
            logger.info("Successfully exchanged authorization code for Google Tokens.")
            return {
                "success": True,
                **response_data
            }
        else:
            logger.error(f"Failed token exchange from Google: {response_data}")
            return {
                "success": False,
                "error": response_data.get("error_description", "Unknown OAuth error")
            }
    except Exception as e:
        logger.error(f"Exception during OAuth token exchange: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
