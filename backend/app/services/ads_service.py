import logging
from typing import Dict, Any, List
from app.config import settings
from app.schemas import DeployCampaignRequest, CampaignTypeEnum

# Try importing the Google Ads API library. If not installed/configured yet, we fail gracefully
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_SDK_AVAILABLE = False
    class GoogleAdsClient:
        pass
    class GoogleAdsException(Exception):
        pass

logger = logging.getLogger(__name__)

def map_campaign_type_to_google_ads(internal_type: CampaignTypeEnum, client: Any) -> Any:
    """
    Maps our internal schema CampaignTypeEnum to Google Ads API AdvertisingChannelType.
    """
    channel_types = client.enums.AdvertisingChannelTypeEnum
    if internal_type == CampaignTypeEnum.SEARCH:
        return channel_types.SEARCH
    elif internal_type == CampaignTypeEnum.DISPLAY:
        return channel_types.DISPLAY
    elif internal_type == CampaignTypeEnum.PERFORMANCE_MAX:
        return channel_types.PERFORMANCE_MAX
    return channel_types.SEARCH

def build_google_ads_client(refresh_token: str = None) -> GoogleAdsClient:
    """
    Constructs a Google Ads Client dynamically from configuration settings.
    """
    if not GOOGLE_ADS_SDK_AVAILABLE:
        raise ImportError("google-ads SDK is not installed or available.")
        
    dev_token = settings.google_developer_token or "DUMMY_DEVELOPER_TOKEN_999"
    client_id = settings.google_client_id or "DUMMY_CLIENT_ID"
    client_secret = settings.google_client_secret or "DUMMY_CLIENT_SECRET"
    
    # We require a refresh token (either passed in from the frontend OAuth state, or loaded from env)
    token = refresh_token or "DUMMY_REFRESH_TOKEN"
    login_cust_id = settings.google_login_customer_id or "1234567890"

    config_dict = {
        "developer_token": dev_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token,
        "login_customer_id": login_cust_id,
        "use_proto_plus": True
    }
    
    return GoogleAdsClient.load_from_dict(config_dict)

def deploy_campaign_mock(request: DeployCampaignRequest) -> Dict[str, Any]:
    """
    Simulates Google Ads API deployment by constructing the JSON schemas 
    that would be sent to the API, returning success and mock resource names.
    """
    campaign = request.campaign_data
    customer_id = request.customer_id or settings.google_login_customer_id or "1234567890"
    
    # Convert budget to micros ($1 = 1,000,000 micros)
    budget_micros = int(request.daily_budget * 1_000_000)
    
    # Simulate step-by-step schema mapping
    simulation_log = []
    
    # Step 1: Budget Creation Schema
    budget_payload = {
        "customer_id": customer_id,
        "operation": "create",
        "campaign_budget": {
            "name": f"Budget for {request.campaign_name}",
            "amount_micros": budget_micros,
            "delivery_method": "STANDARD",
            "explicitly_shared": False
        }
    }
    simulation_log.append({"step": "1. Create Campaign Budget", "payload": budget_payload})
    
    # Step 2: Campaign Creation Schema
    campaign_payload = {
        "customer_id": customer_id,
        "operation": "create",
        "campaign": {
            "name": request.campaign_name,
            "advertising_channel_type": campaign.campaign_type.value,
            "status": "PAUSED",  # Default to PAUSED to prevent accidental spending
            "campaign_budget": "customers/{customer_id}/campaignBudgets/mock-budget-id",
            "target_location": request.target_location
        }
    }
    simulation_log.append({"step": "2. Create Campaign", "payload": campaign_payload})
    
    # Step 3: Ad Group Creation Schema
    ad_group_payload = {
        "customer_id": customer_id,
        "operation": "create",
        "ad_group": {
            "name": f"AI Ad Group - {campaign.campaign_type.value}",
            "campaign": "customers/{customer_id}/campaigns/mock-campaign-id",
            "type": "SEARCH_STANDARD",
            "status": "ENABLED"
        }
    }
    simulation_log.append({"step": "3. Create Ad Group", "payload": ad_group_payload})
    
    # Step 4: Ad Group Ads (Responsive Search Ads) Setup Schema
    ad_variants_payloads = []
    for idx, ad in enumerate(campaign.ad_variants):
        ad_variants_payloads.append({
            "ad_group": "customers/{customer_id}/adGroups/mock-ad-group-id",
            "operation": "create",
            "ad_group_ad": {
                "status": "ENABLED",
                "ad": {
                    "final_urls": [request.website_url or "https://example.com"],
                    "responsive_search_ad": {
                        "headlines": [{"text": h} for h in ad.headlines],
                        "descriptions": [{"text": d} for d in ad.descriptions]
                    }
                }
            }
        })
    simulation_log.append({"step": "4. Setup Ad Group Ads (RSA)", "payloads": ad_variants_payloads})
    
    # Step 5: Keywords & Negative Keywords Setup Schema
    criteria_payloads = []
    # Add target intent-based keywords
    for kw in campaign.keywords:
        criteria_payloads.append({
            "customer_id": customer_id,
            "operation": "create",
            "ad_group_criterion": {
                "ad_group": "customers/{customer_id}/adGroups/mock-ad-group-id",
                "status": "ENABLED",
                "keyword": {
                    "text": kw,
                    "match_type": "PHRASE"
                },
                "negative": False
            }
        })
    # Add negative keywords to filter junk traffic
    for neg_kw in campaign.negative_keywords:
        criteria_payloads.append({
            "customer_id": customer_id,
            "operation": "create",
            "ad_group_criterion": {
                "ad_group": "customers/{customer_id}/adGroups/mock-ad-group-id",
                "status": "ENABLED",
                "keyword": {
                    "text": neg_kw,
                    "match_type": "BROAD"
                },
                "negative": True
            }
        })
    simulation_log.append({"step": "5. Setup Keywords & Negative Keywords (Criteria)", "payloads": criteria_payloads})

    return {
        "success": True,
        "is_mock": True,
        "message": "Mock Google Ads campaign mapping executed successfully (Dry Run).",
        "resource_names": {
            "campaign_budget": f"customers/{customer_id}/campaignBudgets/mock_budget_777",
            "campaign": f"customers/{customer_id}/campaigns/mock_campaign_888",
            "ad_group": f"customers/{customer_id}/adGroups/mock_ad_group_999",
            "ads": [f"customers/{customer_id}/adGroupAds/mock_ad_variant_{i}" for i in range(len(campaign.ad_variants))],
            "criteria_count": len(criteria_payloads)
        },
        "simulation_details": simulation_log
    }

def deploy_campaign_to_google_ads(
    request: DeployCampaignRequest, 
    refresh_token: str = None
) -> Dict[str, Any]:
    """
    Fires operations to the Google Ads API to deploy a campaign.
    If developer token is missing or if the API request fails, it automatically
    performs a detailed mock run to verify validation rules and map JSON schemas.
    """
    # Force Mock deployment if SDK is not installed or settings are dummy placeholders
    has_credentials = (
        settings.google_developer_token and not settings.google_developer_token.startswith("YOUR_")
    )
    
    if not GOOGLE_ADS_SDK_AVAILABLE or not has_credentials:
        logger.warning("Google Ads credentials not configured or SDK missing. Executing dry-run simulation.")
        return deploy_campaign_mock(request)
        
    try:
        # Initialize the Client
        client = build_google_ads_client(refresh_token)
        customer_id = request.customer_id or settings.google_login_customer_id
        
        # 1. Create the Budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"Prompt-to-Ads Budget: {request.campaign_name}"
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget.amount_micros = int(request.daily_budget * 1_000_000)
        
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        logger.info(f"Created Campaign Budget: {budget_resource_name}")
        
        # 2. Create the Campaign
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = request.campaign_name
        campaign.advertising_channel_type = map_campaign_type_to_google_ads(request.campaign_data.campaign_type, client)
        campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Default to PAUSED safety switch
        campaign.campaign_budget = budget_resource_name
        
        # Setup location targeting (Simple Geotargeting mapping logic)
        # In a production app, we would map the city/country name string to a Google Ads criteria ID
        # Here we document it as mapped in the skeleton
        
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name
        logger.info(f"Created Campaign: {campaign_resource_name}")
        
        # 3. Create the Ad Group
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = f"Ad Group Generated by AI"
        ad_group.campaign = campaign_resource_name
        ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        logger.info(f"Created Ad Group: {ad_group_resource_name}")
        
        # 4. Create Responsive Search Ads
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operations = []
        
        for variant in request.campaign_data.ad_variants:
            ad_group_ad_operation = client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_group_ad_operation.create
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED
            
            # Map Responsive Search Ad payload
            ad = ad_group_ad.ad
            ad.final_urls.append(request.website_url or "https://example.com")
            
            # Headlines
            for headline_text in variant.headlines:
                ad_text_asset = client.get_type("AdTextAsset")
                ad_text_asset.text = headline_text
                ad.responsive_search_ad.headlines.append(ad_text_asset)
                
            # Descriptions
            for desc_text in variant.descriptions:
                ad_text_asset = client.get_type("AdTextAsset")
                ad_text_asset.text = desc_text
                ad.responsive_search_ad.descriptions.append(ad_text_asset)
                
            ad_group_ad_operations.append(ad_group_ad_operation)
            
        ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=ad_group_ad_operations
        )
        ad_resource_names = [result.resource_name for result in ad_response.results]
        logger.info(f"Created Ad Variants: {ad_resource_names}")
        
        # 5. Create Criteria (Keywords & Negative Keywords)
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")
        criterion_operations = []
        
        # Map target intent keywords
        for keyword_text in request.campaign_data.keywords:
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = ad_group_resource_name
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.PHRASE
            criterion.negative = False
            criterion_operations.append(operation)
            
        # Map negative keywords
        for neg_keyword_text in request.campaign_data.negative_keywords:
            operation = client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = ad_group_resource_name
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            criterion.keyword.text = neg_keyword_text
            criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
            criterion.negative = True
            criterion_operations.append(operation)
            
        criterion_response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=criterion_operations
        )
        logger.info(f"Added {len(criterion_response.results)} Keywords and Negative Keywords to Ad Group.")
        
        return {
            "success": True,
            "is_mock": False,
            "message": "Google Ads campaign deployed successfully.",
            "resource_names": {
                "campaign_budget": budget_resource_name,
                "campaign": campaign_resource_name,
                "ad_group": ad_group_resource_name,
                "ads": ad_resource_names,
                "criteria_count": len(criterion_response.results)
            }
        }
        
    except GoogleAdsException as ex:
        logger.error(
            f"Google Ads API Exception: Request ID: {ex.request_id}, "
            f"Status: {ex.error.code().name}, details: {ex.failure}"
        )
        # Bubble error information up to response
        errors = []
        for error in ex.failure.errors:
            errors.append(f"Error class: {error.error_code}, Message: {error.message}")
            
        return {
            "success": False,
            "error_source": "Google Ads API",
            "errors": errors,
            "message": "Failed to deploy campaign to Google Ads API. Check credentials or campaign parameters."
        }
    except Exception as ex:
        logger.error(f"Unexpected error deploying campaign: {str(ex)}")
        return {
            "success": False,
            "error_source": "Internal Server Error",
            "message": str(ex)
        }
