from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional
from enum import Enum

class CampaignTypeEnum(str, Enum):
    SEARCH = "SEARCH"
    DISPLAY = "DISPLAY"
    PERFORMANCE_MAX = "PERFORMANCE_MAX"

class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNDETERMINED = "UNDETERMINED"

class DemographicsSchema(BaseModel):
    age_ranges: List[str] = Field(
        ..., 
        description="Target age ranges (e.g., '18-24', '25-34', '35-44', '45-54', '55-64', '65+')"
    )
    genders: List[GenderEnum] = Field(
        ..., 
        description="Target genders, using MALE, FEMALE, or UNDETERMINED"
    )

class AdVariantSchema(BaseModel):
    headlines: List[str] = Field(
        ..., 
        description="Exactly 3 ad headlines, each must be 30 characters or less.",
        min_items=3,
        max_items=3
    )
    descriptions: List[str] = Field(
        ..., 
        description="Exactly 2 ad descriptions, each must be 90 characters or less.",
        min_items=2,
        max_items=2
    )

    @field_validator('headlines')
    @classmethod
    def validate_headlines(cls, v):
        for h in v:
            if len(h) > 30:
                raise ValueError(f"Headline '{h}' exceeds 30 character limit (length: {len(h)})")
        return v

    @field_validator('descriptions')
    @classmethod
    def validate_descriptions(cls, v):
        for d in v:
            if len(d) > 90:
                raise ValueError(f"Description '{d}' exceeds 90 character limit (length: {len(d)})")
        return v

class CampaignGenerationRequest(BaseModel):
    prompt: str = Field(..., description="The text prompt describing business goals and target audience.")
    target_location: Optional[str] = Field(None, description="Optional target city or country.")
    daily_budget: Optional[float] = Field(50.0, description="Daily budget in USD.")
    website_url: Optional[str] = Field(None, description="Optional business website URL.")

class OpenAIStructuredCampaignResponse(BaseModel):
    campaign_type: CampaignTypeEnum = Field(..., description="Google Ads campaign type recommendations.")
    negative_keywords: List[str] = Field(
        ..., 
        description="Exactly 3 negative keywords to filter junk traffic.",
        min_items=3,
        max_items=3
    )
    demographics: DemographicsSchema = Field(..., description="Target audience demographics.")
    keywords: List[str] = Field(..., description="Intent-based target keywords (minimum 5).")
    ad_variants: List[AdVariantSchema] = Field(
        ..., 
        description="Exactly 3 Google ad variants, each containing headlines and descriptions.",
        min_items=3,
        max_items=3
    )

class CampaignResponse(BaseModel):
    success: bool
    data: OpenAIStructuredCampaignResponse
    raw_prompt: str
    metadata: dict

class DeployCampaignRequest(BaseModel):
    campaign_data: OpenAIStructuredCampaignResponse = Field(..., description="The final campaign configurations approved by user.")
    campaign_name: str = Field(..., description="The name of the campaign.")
    daily_budget: float = Field(..., description="The daily budget of the campaign.")
    website_url: Optional[str] = Field(None, description="Website landing page for ads.")
    target_location: Optional[str] = Field(None, description="Target location.")
    customer_id: Optional[str] = Field(None, description="Optional specific Google Ads Customer ID.")
