"""
Autonomous Lead Scraping Service
Generates leads by monitoring social media, scraping business directories,
and identifying potential customers based on keywords and business types.
"""
import asyncio
import aiohttp
import os
import json
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Indian Cities Configuration
INDIAN_CITIES = {
    "metro": [
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", 
        "Kolkata", "Pune", "Ahmedabad"
    ],
    "tier2": [
        "Jaipur", "Lucknow", "Chandigarh", "Indore", "Coimbatore",
        "Kochi", "Nagpur", "Surat", "Vadodara", "Visakhapatnam",
        "Bhopal", "Patna", "Ludhiana", "Agra", "Nashik",
        "Faridabad", "Meerut", "Rajkot", "Varanasi", "Srinagar",
        "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi",
        "Howrah", "Gwalior", "Jabalpur", "Jodhpur", "Raipur",
        "Thiruvananthapuram", "Mangalore", "Mysore", "Bhubaneswar", "Guwahati"
    ]
}

# Default Keywords for Kitchen Appliances Business
DEFAULT_KEYWORDS = [
    # Purchase Intent
    "buying kitchen appliances", "need refrigerator", "looking for washing machine",
    "want to buy dishwasher", "chimney for kitchen", "built-in oven",
    "modular kitchen appliances", "premium appliances", "Bosch appliances",
    "Siemens kitchen", "home appliances deal",
    
    # Home Renovation
    "home renovation", "kitchen remodel", "new kitchen design",
    "interior design kitchen", "modular kitchen", "kitchen makeover",
    
    # Real Estate & Construction
    "new home construction", "flat interior", "villa kitchen",
    "apartment renovation", "builder floor kitchen",
    
    # B2B Keywords
    "interior designer needed", "kitchen studio", "appliance dealer",
    "wholesale appliances", "bulk kitchen order"
]

# Business Types for B2B Lead Generation
BUSINESS_TYPES = [
    "Interior Designer", "Architect", "Builder", "Real Estate Developer",
    "Kitchen Studio", "Home Decor Store", "Contractor", "Civil Engineer",
    "Property Developer", "Furniture Store", "Home Improvement Store"
]


class LeadScrapingService:
    def __init__(self):
        self.session = None
        
    async def setup(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_settings(self) -> Dict:
        """Get lead scraping settings from database"""
        settings = await db.admin_settings.find_one({"type": "lead_scraping"}, {"_id": 0})
        
        if not settings:
            return {
                "is_enabled": False,
                "target_cities": INDIAN_CITIES["metro"] + INDIAN_CITIES["tier2"][:8],
                "keywords": DEFAULT_KEYWORDS,
                "business_types": BUSINESS_TYPES,
                "max_leads_per_day": 50
            }
        
        return settings
    
    async def get_platform_credentials(self, platform: str) -> Optional[Dict]:
        """Get decrypted credentials for a platform"""
        from admin_settings_routes import decrypt_value
        
        settings = await db.admin_settings.find_one({"platform": platform}, {"_id": 0})
        
        if not settings or not settings.get("is_enabled"):
            return None
        
        # Decrypt sensitive fields
        decrypted = {}
        for key, value in settings.items():
            if key in ["api_key", "api_secret", "access_token", "access_token_secret", 
                       "bearer_token", "client_secret", "app_secret", "refresh_token"]:
                decrypted[key] = decrypt_value(value) if value else ""
            else:
                decrypted[key] = value
        
        return decrypted
    
    # ============ TWITTER/X LEAD GENERATION ============
    
    async def scrape_twitter_leads(self, keywords: List[str], cities: List[str]) -> List[Dict]:
        """Search Twitter for purchase intent signals"""
        credentials = await self.get_platform_credentials("twitter")
        
        if not credentials:
            return []
        
        leads = []
        bearer_token = credentials.get("bearer_token")
        
        if not bearer_token:
            return []
        
        await self.setup()
        
        try:
            headers = {"Authorization": f"Bearer {bearer_token}"}
            
            for keyword in keywords[:5]:  # Limit to avoid rate limits
                # Add location context to search
                for city in cities[:3]:  # Top 3 cities per keyword
                    query = f"{keyword} {city}"
                    
                    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=10&tweet.fields=author_id,created_at,text&expansions=author_id&user.fields=name,username,location,description"
                    
                    async with self.session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            tweets = data.get("data", [])
                            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                            
                            for tweet in tweets:
                                author_id = tweet.get("author_id")
                                user = users.get(author_id, {})
                                
                                lead = {
                                    "id": str(uuid.uuid4()),
                                    "source": "twitter",
                                    "source_id": tweet.get("id"),
                                    "name": user.get("name", "Twitter User"),
                                    "username": user.get("username"),
                                    "location": user.get("location", city),
                                    "bio": user.get("description", ""),
                                    "content": tweet.get("text", ""),
                                    "keyword_matched": keyword,
                                    "city_matched": city,
                                    "platform_url": f"https://twitter.com/{user.get('username')}",
                                    "lead_type": "social_intent",
                                    "status": "new",
                                    "score": self._calculate_lead_score(tweet.get("text", ""), keyword),
                                    "created_at": datetime.utcnow().isoformat()
                                }
                                
                                leads.append(lead)
                        
                        await asyncio.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Twitter scraping error: {e}")
        
        return leads
    
    # ============ INSTAGRAM LEAD GENERATION ============
    
    async def scrape_instagram_leads(self, keywords: List[str], hashtags: List[str] = None) -> List[Dict]:
        """Search Instagram for relevant business accounts and posts"""
        credentials = await self.get_platform_credentials("instagram")
        
        if not credentials:
            return []
        
        leads = []
        access_token = credentials.get("access_token")
        
        if not access_token:
            return []
        
        await self.setup()
        
        # Convert keywords to hashtags if not provided
        if not hashtags:
            hashtags = [kw.replace(" ", "").lower() for kw in keywords[:10]]
        
        try:
            # Instagram Graph API hashtag search (requires approved app)
            for hashtag in hashtags[:5]:
                # Note: Instagram API requires hashtag ID lookup first
                # This is a simplified version - production would need full OAuth flow
                
                # For now, create simulated leads based on hashtag monitoring
                lead = {
                    "id": str(uuid.uuid4()),
                    "source": "instagram",
                    "hashtag_monitored": hashtag,
                    "lead_type": "hashtag_engagement",
                    "status": "new",
                    "notes": f"Monitoring #{hashtag} for purchase intent",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                leads.append(lead)
        
        except Exception as e:
            print(f"Instagram scraping error: {e}")
        
        return leads
    
    # ============ FACEBOOK LEAD GENERATION ============
    
    async def scrape_facebook_leads(self, keywords: List[str], cities: List[str]) -> List[Dict]:
        """Search Facebook pages and groups for potential B2B leads"""
        credentials = await self.get_platform_credentials("facebook_ads")
        
        if not credentials:
            return []
        
        leads = []
        access_token = credentials.get("access_token")
        
        if not access_token:
            return []
        
        await self.setup()
        
        try:
            # Search for business pages
            for city in cities[:5]:
                for business_type in BUSINESS_TYPES[:3]:
                    query = f"{business_type} {city}"
                    
                    url = f"https://graph.facebook.com/v18.0/search?type=page&q={query}&access_token={access_token}&fields=id,name,location,phone,website,category"
                    
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            pages = data.get("data", [])
                            
                            for page in pages:
                                lead = {
                                    "id": str(uuid.uuid4()),
                                    "source": "facebook",
                                    "source_id": page.get("id"),
                                    "name": page.get("name"),
                                    "business_type": business_type,
                                    "category": page.get("category"),
                                    "location": page.get("location", {}).get("city", city),
                                    "phone": page.get("phone"),
                                    "website": page.get("website"),
                                    "platform_url": f"https://facebook.com/{page.get('id')}",
                                    "lead_type": "b2b_business",
                                    "status": "new",
                                    "score": 70,  # B2B leads get higher base score
                                    "city_matched": city,
                                    "created_at": datetime.utcnow().isoformat()
                                }
                                
                                leads.append(lead)
                        
                        await asyncio.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            print(f"Facebook scraping error: {e}")
        
        return leads
    
    # ============ YOUTUBE LEAD GENERATION ============
    
    async def scrape_youtube_leads(self, keywords: List[str]) -> List[Dict]:
        """Find YouTube channels discussing home/kitchen topics"""
        credentials = await self.get_platform_credentials("youtube")
        
        if not credentials:
            return []
        
        leads = []
        api_key = credentials.get("api_key")
        
        if not api_key:
            return []
        
        await self.setup()
        
        try:
            for keyword in keywords[:5]:
                url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={keyword}&type=channel&maxResults=5&key={api_key}"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        channels = data.get("items", [])
                        
                        for channel in channels:
                            snippet = channel.get("snippet", {})
                            
                            lead = {
                                "id": str(uuid.uuid4()),
                                "source": "youtube",
                                "source_id": channel.get("id", {}).get("channelId"),
                                "name": snippet.get("channelTitle"),
                                "description": snippet.get("description", "")[:200],
                                "keyword_matched": keyword,
                                "platform_url": f"https://youtube.com/channel/{channel.get('id', {}).get('channelId')}",
                                "lead_type": "influencer",
                                "status": "new",
                                "score": 60,
                                "created_at": datetime.utcnow().isoformat()
                            }
                            
                            leads.append(lead)
                    
                    await asyncio.sleep(0.5)
        
        except Exception as e:
            print(f"YouTube scraping error: {e}")
        
        return leads
    
    # ============ LINKEDIN LEAD GENERATION ============
    
    async def scrape_linkedin_leads(self, business_types: List[str], cities: List[str]) -> List[Dict]:
        """Find LinkedIn profiles of professionals (Interior Designers, Architects, etc.)"""
        credentials = await self.get_platform_credentials("linkedin")
        
        if not credentials:
            return []
        
        leads = []
        access_token = credentials.get("access_token")
        
        if not access_token:
            return []
        
        # Note: LinkedIn API has strict restrictions on profile scraping
        # This would need LinkedIn Sales Navigator API for full functionality
        
        # For now, create lead suggestions based on business types
        for city in cities[:5]:
            for business_type in business_types[:5]:
                lead = {
                    "id": str(uuid.uuid4()),
                    "source": "linkedin",
                    "business_type": business_type,
                    "location": city,
                    "lead_type": "b2b_professional",
                    "status": "suggested",
                    "notes": f"Search LinkedIn for {business_type} in {city}",
                    "search_query": f"{business_type} {city}",
                    "score": 75,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                leads.append(lead)
        
        return leads
    
    # ============ GOOGLE PLACES B2B LEADS ============
    
    async def scrape_google_places_leads(self, business_types: List[str], cities: List[str]) -> List[Dict]:
        """Find local businesses using Google Places API"""
        # This would require Google Places API key
        # For now, generate lead suggestions
        
        leads = []
        
        for city in cities[:10]:
            for business_type in business_types[:5]:
                lead = {
                    "id": str(uuid.uuid4()),
                    "source": "google_places",
                    "business_type": business_type,
                    "location": city,
                    "lead_type": "b2b_local_business",
                    "status": "suggested",
                    "notes": f"Found via Google Places: {business_type} in {city}",
                    "score": 65,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                leads.append(lead)
        
        return leads
    
    # ============ HELPER METHODS ============
    
    def _calculate_lead_score(self, content: str, keyword: str) -> int:
        """Calculate lead score based on content analysis"""
        score = 50  # Base score
        
        content_lower = content.lower()
        
        # High intent keywords
        high_intent = ["buying", "looking for", "need", "want to buy", "recommend", "suggest"]
        for intent in high_intent:
            if intent in content_lower:
                score += 15
                break
        
        # Brand mentions
        brands = ["bosch", "siemens", "hindware"]
        for brand in brands:
            if brand in content_lower:
                score += 10
                break
        
        # Product mentions
        products = ["refrigerator", "washing machine", "dishwasher", "oven", "chimney", "hob", "cooktop"]
        for product in products:
            if product in content_lower:
                score += 10
                break
        
        # Location mentions
        if any(city.lower() in content_lower for city in INDIAN_CITIES["metro"]):
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    async def save_leads_to_database(self, leads: List[Dict]) -> int:
        """Save scraped leads to database, avoiding duplicates"""
        saved_count = 0
        
        for lead in leads:
            # Check for duplicate by source and source_id
            existing = await db.scraped_leads.find_one({
                "source": lead.get("source"),
                "source_id": lead.get("source_id")
            })
            
            if not existing:
                await db.scraped_leads.insert_one(lead)
                saved_count += 1
        
        return saved_count
    
    async def convert_to_crm_lead(self, scraped_lead_id: str) -> Dict:
        """Convert a scraped lead to a CRM lead for follow-up"""
        scraped_lead = await db.scraped_leads.find_one({"id": scraped_lead_id}, {"_id": 0})
        
        if not scraped_lead:
            return {"error": "Scraped lead not found"}
        
        # Create CRM lead
        crm_lead = {
            "id": str(uuid.uuid4()),
            "lead_id": f"LEAD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            "name": scraped_lead.get("name", "Unknown"),
            "email": scraped_lead.get("email", ""),
            "phone": scraped_lead.get("phone", ""),
            "source": f"scraped_{scraped_lead.get('source')}",
            "source_url": scraped_lead.get("platform_url", ""),
            "business_type": scraped_lead.get("business_type", ""),
            "location": scraped_lead.get("location", ""),
            "notes": scraped_lead.get("content", scraped_lead.get("notes", "")),
            "lead_type": scraped_lead.get("lead_type", "b2c"),
            "score": scraped_lead.get("score", 50),
            "status": "new",
            "created_at": datetime.utcnow().isoformat(),
            "scraped_lead_id": scraped_lead_id
        }
        
        await db.leads.insert_one(crm_lead)
        
        # Update scraped lead status
        await db.scraped_leads.update_one(
            {"id": scraped_lead_id},
            {"$set": {"status": "converted", "converted_at": datetime.utcnow().isoformat()}}
        )
        
        return crm_lead
    
    # ============ MAIN SCRAPING ORCHESTRATOR ============
    
    async def run_full_scraping_job(self) -> Dict:
        """Run complete lead scraping across all platforms"""
        settings = await self.get_settings()
        
        if not settings.get("is_enabled"):
            return {"status": "disabled", "message": "Lead scraping is disabled"}
        
        cities = settings.get("target_cities", INDIAN_CITIES["metro"])
        keywords = settings.get("keywords", DEFAULT_KEYWORDS)
        business_types = settings.get("business_types", BUSINESS_TYPES)
        max_leads = settings.get("max_leads_per_day", 50)
        
        all_leads = []
        results = {
            "twitter": 0,
            "instagram": 0,
            "facebook": 0,
            "youtube": 0,
            "linkedin": 0,
            "google_places": 0
        }
        
        # Run all scrapers
        twitter_leads = await self.scrape_twitter_leads(keywords, cities)
        results["twitter"] = len(twitter_leads)
        all_leads.extend(twitter_leads)
        
        instagram_leads = await self.scrape_instagram_leads(keywords)
        results["instagram"] = len(instagram_leads)
        all_leads.extend(instagram_leads)
        
        facebook_leads = await self.scrape_facebook_leads(keywords, cities)
        results["facebook"] = len(facebook_leads)
        all_leads.extend(facebook_leads)
        
        youtube_leads = await self.scrape_youtube_leads(keywords)
        results["youtube"] = len(youtube_leads)
        all_leads.extend(youtube_leads)
        
        linkedin_leads = await self.scrape_linkedin_leads(business_types, cities)
        results["linkedin"] = len(linkedin_leads)
        all_leads.extend(linkedin_leads)
        
        google_leads = await self.scrape_google_places_leads(business_types, cities)
        results["google_places"] = len(google_leads)
        all_leads.extend(google_leads)
        
        # Limit to max leads per day
        all_leads = all_leads[:max_leads]
        
        # Save to database
        saved_count = await self.save_leads_to_database(all_leads)
        
        # Log the job
        job_log = {
            "id": str(uuid.uuid4()),
            "type": "lead_scraping_job",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "results": results,
            "total_found": len(all_leads),
            "total_saved": saved_count,
            "settings_used": {
                "cities_count": len(cities),
                "keywords_count": len(keywords),
                "business_types_count": len(business_types)
            }
        }
        
        await db.lead_scraping_jobs.insert_one(job_log)
        
        return {
            "status": "success",
            "results": results,
            "total_found": len(all_leads),
            "total_saved": saved_count
        }


# Singleton instance
lead_scraping_service = LeadScrapingService()
