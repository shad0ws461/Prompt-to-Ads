import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Prompt-to-Ads API"
    environment: str = "development"
    debug: bool = True
    
    # Google Gemini API Key (from Google AI Studio)
    gemini_api_key: Optional[str] = None
    
    # Google OAuth 2.0 Credentials
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/oauth/callback"
    
    # Google Ads API Settings
    google_developer_token: Optional[str] = None
    google_login_customer_id: Optional[str] = None
    
    # Model Config
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
