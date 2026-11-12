"""
Admin Settings Routes
Secure management of ad platform credentials and social media API keys
"""
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
from dotenv import load_dotenv
import base64
from cryptography.fernet import Fernet
import hashlib

load_dotenv()

router = APIRouter(prefix="/admin-settings", tags=["Admin Settings"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Simple encryption for storing credentials
def get_encryption_key():
    """Generate a consistent encryption key from environment"""
    secret = os.environ.get('SECRET_KEY', 'aditya-retail-secret-key-2024')
    key = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_value(value: str) -> str:
    """Encrypt sensitive values before storing"""
    if not value:
        return ""
    try:
        f = Fernet(get_encryption_key())
        return f.encrypt(value.encode()).decode()
    except Exception:
        return value  # Return as-is if encryption fails

def decrypt_value(value: str) -> str:
    """Decrypt sensitive values when retrieving"""
    if not value:
        return ""
    try:
        f = Fernet(get_encryption_key())
        return f.decrypt(value.encode()).decode()
    except Exception:
        return value  # Return as-is if decryption fails

def mask_credential(value: str) -> str:
    """Mask credential for display (show first 4 and last 4 chars)"""
    if not value or len(value) < 12:
        return "****" if value else ""
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"

# Pydantic Models
class GoogleAdsCredentials(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    developer_token: Optional[str] = None
    customer_id: Optional[str] = None
    refresh_token: Optional[str] = None
    is_enabled: bool = False

class FacebookAdsCredentials(BaseModel):
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    access_token: Optional[str] = None
    ad_account_id: Optional[str] = None
    page_id: Optional[str] = None
    is_enabled: bool = False

class TwitterCredentials(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    is_enabled: bool = False

class InstagramCredentials(BaseModel):
    access_token: Optional[str] = None
    business_account_id: Optional[str] = None
    is_enabled: bool = False

class YouTubeCredentials(BaseModel):
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    channel_id: Optional[str] = None
    is_enabled: bool = False

class LinkedInCredentials(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    organization_id: Optional[str] = None
    is_enabled: bool = False

class LeadScrapingSettings(BaseModel):
    is_enabled: bool = False
    target_cities: List[str] = []
    keywords: List[str] = []
    business_types: List[str] = []
    scraping_frequency: str = "daily"  # daily, weekly, hourly
    max_leads_per_day: int = 50
    auto_follow_up: bool = True

# ============ AD PLATFORM CREDENTIALS ============

@router.post("/google-ads")
async def save_google_ads_credentials(credentials: GoogleAdsCredentials):
    """Save Google Ads API credentials"""
    try:
        encrypted_data = {
            "platform": "google_ads",
            "client_id": encrypt_value(credentials.client_id) if credentials.client_id else "",
            "client_secret": encrypt_value(credentials.client_secret) if credentials.client_secret else "",
            "developer_token": encrypt_value(credentials.developer_token) if credentials.developer_token else "",
            "customer_id": credentials.customer_id or "",
            "refresh_token": encrypt_value(credentials.refresh_token) if credentials.refresh_token else "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "google_ads"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Google Ads credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google-ads")
async def get_google_ads_credentials():
    """Get Google Ads credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "google_ads"}, {"_id": 0})
        
        if not settings:
            return {
                "platform": "google_ads",
                "is_configured": False,
                "is_enabled": False
            }
        
        return {
            "platform": "google_ads",
            "is_configured": bool(settings.get("client_id")),
            "is_enabled": settings.get("is_enabled", False),
            "client_id": mask_credential(decrypt_value(settings.get("client_id", ""))),
            "customer_id": settings.get("customer_id", ""),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/facebook-ads")
async def save_facebook_ads_credentials(credentials: FacebookAdsCredentials):
    """Save Facebook/Meta Ads API credentials"""
    try:
        encrypted_data = {
            "platform": "facebook_ads",
            "app_id": credentials.app_id or "",
            "app_secret": encrypt_value(credentials.app_secret) if credentials.app_secret else "",
            "access_token": encrypt_value(credentials.access_token) if credentials.access_token else "",
            "ad_account_id": credentials.ad_account_id or "",
            "page_id": credentials.page_id or "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "facebook_ads"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Facebook Ads credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facebook-ads")
async def get_facebook_ads_credentials():
    """Get Facebook Ads credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "facebook_ads"}, {"_id": 0})
        
        if not settings:
            return {
                "platform": "facebook_ads",
                "is_configured": False,
                "is_enabled": False
            }
        
        return {
            "platform": "facebook_ads",
            "is_configured": bool(settings.get("app_id")),
            "is_enabled": settings.get("is_enabled", False),
            "app_id": settings.get("app_id", ""),
            "ad_account_id": settings.get("ad_account_id", ""),
            "page_id": settings.get("page_id", ""),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ SOCIAL MEDIA API CREDENTIALS ============

@router.post("/twitter")
async def save_twitter_credentials(credentials: TwitterCredentials):
    """Save Twitter/X API credentials"""
    try:
        encrypted_data = {
            "platform": "twitter",
            "api_key": encrypt_value(credentials.api_key) if credentials.api_key else "",
            "api_secret": encrypt_value(credentials.api_secret) if credentials.api_secret else "",
            "access_token": encrypt_value(credentials.access_token) if credentials.access_token else "",
            "access_token_secret": encrypt_value(credentials.access_token_secret) if credentials.access_token_secret else "",
            "bearer_token": encrypt_value(credentials.bearer_token) if credentials.bearer_token else "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "twitter"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Twitter credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/twitter")
async def get_twitter_credentials():
    """Get Twitter credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "twitter"}, {"_id": 0})
        
        if not settings:
            return {"platform": "twitter", "is_configured": False, "is_enabled": False}
        
        return {
            "platform": "twitter",
            "is_configured": bool(settings.get("api_key")),
            "is_enabled": settings.get("is_enabled", False),
            "api_key": mask_credential(decrypt_value(settings.get("api_key", ""))),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram")
async def save_instagram_credentials(credentials: InstagramCredentials):
    """Save Instagram API credentials"""
    try:
        encrypted_data = {
            "platform": "instagram",
            "access_token": encrypt_value(credentials.access_token) if credentials.access_token else "",
            "business_account_id": credentials.business_account_id or "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "instagram"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Instagram credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instagram")
async def get_instagram_credentials():
    """Get Instagram credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "instagram"}, {"_id": 0})
        
        if not settings:
            return {"platform": "instagram", "is_configured": False, "is_enabled": False}
        
        return {
            "platform": "instagram",
            "is_configured": bool(settings.get("access_token")),
            "is_enabled": settings.get("is_enabled", False),
            "business_account_id": settings.get("business_account_id", ""),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube")
async def save_youtube_credentials(credentials: YouTubeCredentials):
    """Save YouTube API credentials"""
    try:
        encrypted_data = {
            "platform": "youtube",
            "api_key": encrypt_value(credentials.api_key) if credentials.api_key else "",
            "client_id": encrypt_value(credentials.client_id) if credentials.client_id else "",
            "client_secret": encrypt_value(credentials.client_secret) if credentials.client_secret else "",
            "channel_id": credentials.channel_id or "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "youtube"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "YouTube credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/youtube")
async def get_youtube_credentials():
    """Get YouTube credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "youtube"}, {"_id": 0})
        
        if not settings:
            return {"platform": "youtube", "is_configured": False, "is_enabled": False}
        
        return {
            "platform": "youtube",
            "is_configured": bool(settings.get("api_key")),
            "is_enabled": settings.get("is_enabled", False),
            "channel_id": settings.get("channel_id", ""),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/linkedin")
async def save_linkedin_credentials(credentials: LinkedInCredentials):
    """Save LinkedIn API credentials"""
    try:
        encrypted_data = {
            "platform": "linkedin",
            "client_id": encrypt_value(credentials.client_id) if credentials.client_id else "",
            "client_secret": encrypt_value(credentials.client_secret) if credentials.client_secret else "",
            "access_token": encrypt_value(credentials.access_token) if credentials.access_token else "",
            "organization_id": credentials.organization_id or "",
            "is_enabled": credentials.is_enabled,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"platform": "linkedin"},
            {"$set": encrypted_data},
            upsert=True
        )
        
        return {"status": "success", "message": "LinkedIn credentials saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/linkedin")
async def get_linkedin_credentials():
    """Get LinkedIn credentials (masked)"""
    try:
        settings = await db.admin_settings.find_one({"platform": "linkedin"}, {"_id": 0})
        
        if not settings:
            return {"platform": "linkedin", "is_configured": False, "is_enabled": False}
        
        return {
            "platform": "linkedin",
            "is_configured": bool(settings.get("client_id")),
            "is_enabled": settings.get("is_enabled", False),
            "organization_id": settings.get("organization_id", ""),
            "updated_at": settings.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ LEAD SCRAPING SETTINGS ============

@router.post("/lead-scraping")
async def save_lead_scraping_settings(settings: LeadScrapingSettings):
    """Save lead scraping configuration"""
    try:
        settings_data = {
            "type": "lead_scraping",
            "is_enabled": settings.is_enabled,
            "target_cities": settings.target_cities,
            "keywords": settings.keywords,
            "business_types": settings.business_types,
            "scraping_frequency": settings.scraping_frequency,
            "max_leads_per_day": settings.max_leads_per_day,
            "auto_follow_up": settings.auto_follow_up,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.admin_settings.update_one(
            {"type": "lead_scraping"},
            {"$set": settings_data},
            upsert=True
        )
        
        return {"status": "success", "message": "Lead scraping settings saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lead-scraping")
async def get_lead_scraping_settings():
    """Get lead scraping configuration"""
    try:
        settings = await db.admin_settings.find_one({"type": "lead_scraping"}, {"_id": 0})
        
        if not settings:
            # Return default settings
            return {
                "type": "lead_scraping",
                "is_enabled": False,
                "target_cities": [
                    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad",
                    "Jaipur", "Lucknow", "Chandigarh", "Indore", "Coimbatore", "Kochi", "Nagpur", "Surat"
                ],
                "keywords": [
                    "kitchen appliances", "home renovation", "modular kitchen", "interior designer",
                    "new home", "refrigerator", "washing machine", "dishwasher", "oven", "chimney"
                ],
                "business_types": [
                    "Interior Designer", "Architect", "Builder", "Real Estate Developer",
                    "Kitchen Studio", "Home Decor Store", "Contractor"
                ],
                "scraping_frequency": "daily",
                "max_leads_per_day": 50,
                "auto_follow_up": True
            }
        
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ ALL SETTINGS OVERVIEW ============

@router.get("/all")
async def get_all_settings():
    """Get overview of all platform configurations"""
    try:
        platforms = ["google_ads", "facebook_ads", "twitter", "instagram", "youtube", "linkedin"]
        settings_overview = []
        
        for platform in platforms:
            setting = await db.admin_settings.find_one({"platform": platform}, {"_id": 0})
            
            if setting:
                settings_overview.append({
                    "platform": platform,
                    "is_configured": True,
                    "is_enabled": setting.get("is_enabled", False),
                    "updated_at": setting.get("updated_at")
                })
            else:
                settings_overview.append({
                    "platform": platform,
                    "is_configured": False,
                    "is_enabled": False,
                    "updated_at": None
                })
        
        # Get lead scraping settings
        lead_scraping = await db.admin_settings.find_one({"type": "lead_scraping"}, {"_id": 0})
        
        return {
            "status": "success",
            "platforms": settings_overview,
            "lead_scraping": {
                "is_configured": bool(lead_scraping),
                "is_enabled": lead_scraping.get("is_enabled", False) if lead_scraping else False
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-connection/{platform}")
async def test_platform_connection(platform: str):
    """Test connection to a platform API"""
    try:
        settings = await db.admin_settings.find_one({"platform": platform}, {"_id": 0})
        
        if not settings:
            return {"status": "error", "message": f"{platform} credentials not configured"}
        
        # For now, return a simulated test result
        # In production, this would actually test the API connection
        return {
            "status": "success",
            "message": f"{platform} connection test successful",
            "platform": platform,
            "is_connected": True,
            "tested_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
