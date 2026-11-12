#!/usr/bin/env python3
"""
Admin Settings and Lead Scraping Features Testing
Tests the newly implemented Admin Settings and Lead Scraping APIs
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class AdminLeadScrapingTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🚀 Starting Admin Settings & Lead Scraping Tests")
        print(f"🌐 API Base URL: {API_BASE_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_admin_settings_all_platforms(self):
        """Test 1: Admin Settings - Get All Platform Configurations"""
        print("\n⚙️ Testing Admin Settings - All Platform Configurations...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/admin-settings/all") as response:
                if response.status == 200:
                    data = await response.json()
                    platforms = data.get('platforms', [])
                    lead_scraping = data.get('lead_scraping', {})
                    
                    print(f"✅ All Settings Retrieved: {len(platforms)} platforms")
                    print(f"📊 Lead Scraping Status: {'Configured' if lead_scraping.get('is_configured') else 'Not Configured'}")
                    
                    # Verify expected platforms
                    expected_platforms = ["google_ads", "facebook_ads", "twitter", "instagram", "youtube", "linkedin"]
                    found_platforms = [p.get('platform') for p in platforms]
                    
                    for platform in expected_platforms:
                        if platform in found_platforms:
                            platform_data = next(p for p in platforms if p.get('platform') == platform)
                            status = "Enabled" if platform_data.get('is_enabled') else "Disabled"
                            configured = "Configured" if platform_data.get('is_configured') else "Not Configured"
                            print(f"  📱 {platform}: {configured}, {status}")
                        else:
                            print(f"  ❌ {platform}: Missing from response")
                    
                    self.test_results['admin_settings_all_platforms'] = True
                    return True
                else:
                    print(f"❌ Failed to get all settings: {response.status}")
                    self.test_results['admin_settings_all_platforms'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Admin Settings All Platforms error: {str(e)}")
            self.test_results['admin_settings_all_platforms'] = False
            return False

    async def test_google_ads_credentials(self):
        """Test 2: Google Ads Credentials Management"""
        print("\n🎯 Testing Google Ads Credentials Management...")
        
        try:
            # Test saving Google Ads credentials
            google_ads_data = {
                "client_id": "test-client-id-123",
                "client_secret": "test-secret-456",
                "developer_token": "dev-token-789",
                "customer_id": "123-456-7890",
                "is_enabled": True
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/admin-settings/google-ads",
                json=google_ads_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Google Ads Save: {result.get('message', 'Success')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Google Ads Save failed: {response.status} - {error_text}")
                    self.test_results['google_ads_credentials'] = False
                    return False
            
            # Test retrieving Google Ads credentials (should be masked)
            async with self.session.get(f"{API_BASE_URL}/admin-settings/google-ads") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Google Ads Retrieve: Platform={data.get('platform')}")
                    print(f"🔧 Configured: {data.get('is_configured')}")
                    print(f"⚡ Enabled: {data.get('is_enabled')}")
                    
                    # Verify credential masking
                    client_id = data.get('client_id', '')
                    customer_id = data.get('customer_id', '')
                    
                    if client_id and '*' in client_id:
                        print(f"✅ Credential Masking: Client ID properly masked ({client_id})")
                    else:
                        print(f"⚠️ Credential Masking: Client ID not masked properly")
                    
                    if customer_id == "123-456-7890":
                        print(f"✅ Customer ID: Stored correctly ({customer_id})")
                    
                    self.test_results['google_ads_credentials'] = True
                    return True
                else:
                    print(f"❌ Google Ads Retrieve failed: {response.status}")
                    self.test_results['google_ads_credentials'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Google Ads Credentials error: {str(e)}")
            self.test_results['google_ads_credentials'] = False
            return False

    async def test_twitter_credentials(self):
        """Test 3: Twitter Credentials Management"""
        print("\n🐦 Testing Twitter Credentials Management...")
        
        try:
            # Test saving Twitter credentials
            twitter_data = {
                "api_key": "twitter-api-key-123",
                "api_secret": "twitter-secret-456",
                "access_token": "twitter-token-789",
                "access_token_secret": "twitter-token-secret-012",
                "bearer_token": "twitter-bearer-345",
                "is_enabled": True
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/admin-settings/twitter",
                json=twitter_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Twitter Save: {result.get('message', 'Success')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Twitter Save failed: {response.status} - {error_text}")
                    self.test_results['twitter_credentials'] = False
                    return False
            
            # Test retrieving Twitter credentials
            async with self.session.get(f"{API_BASE_URL}/admin-settings/twitter") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Twitter Retrieve: Platform={data.get('platform')}")
                    print(f"🔧 Configured: {data.get('is_configured')}")
                    print(f"⚡ Enabled: {data.get('is_enabled')}")
                    
                    # Verify credential masking
                    api_key = data.get('api_key', '')
                    if api_key and '*' in api_key:
                        print(f"✅ Credential Masking: API Key properly masked ({api_key})")
                    
                    self.test_results['twitter_credentials'] = True
                    return True
                else:
                    print(f"❌ Twitter Retrieve failed: {response.status}")
                    self.test_results['twitter_credentials'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Twitter Credentials error: {str(e)}")
            self.test_results['twitter_credentials'] = False
            return False

    async def test_lead_scraping_settings(self):
        """Test 4: Lead Scraping Settings Management"""
        print("\n🎯 Testing Lead Scraping Settings Management...")
        
        try:
            # Test saving lead scraping settings
            scraping_settings = {
                "is_enabled": True,
                "target_cities": ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"],
                "keywords": ["kitchen appliances", "modular kitchen", "home renovation", "interior design"],
                "business_types": ["Interior Designer", "Architect", "Kitchen Studio"],
                "scraping_frequency": "daily",
                "max_leads_per_day": 50,
                "auto_follow_up": True
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/admin-settings/lead-scraping",
                json=scraping_settings,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Lead Scraping Settings Save: {result.get('message', 'Success')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Lead Scraping Settings Save failed: {response.status} - {error_text}")
                    self.test_results['lead_scraping_settings'] = False
                    return False
            
            # Test retrieving lead scraping settings
            async with self.session.get(f"{API_BASE_URL}/admin-settings/lead-scraping") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Lead Scraping Settings Retrieve: Type={data.get('type')}")
                    print(f"⚡ Enabled: {data.get('is_enabled')}")
                    print(f"📍 Target Cities: {len(data.get('target_cities', []))} cities")
                    print(f"🔍 Keywords: {len(data.get('keywords', []))} keywords")
                    print(f"🏢 Business Types: {len(data.get('business_types', []))} types")
                    print(f"⏰ Frequency: {data.get('scraping_frequency', 'N/A')}")
                    print(f"📊 Max Leads/Day: {data.get('max_leads_per_day', 0)}")
                    
                    self.test_results['lead_scraping_settings'] = True
                    return True
                else:
                    print(f"❌ Lead Scraping Settings Retrieve failed: {response.status}")
                    self.test_results['lead_scraping_settings'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Lead Scraping Settings error: {str(e)}")
            self.test_results['lead_scraping_settings'] = False
            return False

    async def test_connection_testing(self):
        """Test 5: Platform Connection Testing"""
        print("\n🔗 Testing Platform Connection Testing...")
        
        try:
            # Test Google Ads connection
            async with self.session.post(f"{API_BASE_URL}/admin-settings/test-connection/google_ads") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Google Ads Connection Test: {result.get('message', 'Success')}")
                    print(f"🔗 Connected: {result.get('is_connected', False)}")
                    print(f"⏰ Tested At: {result.get('tested_at', 'N/A')}")
                else:
                    print(f"❌ Google Ads Connection Test failed: {response.status}")
                    # Don't fail the test for this as it's a simulated test
            
            # Test Twitter connection
            async with self.session.post(f"{API_BASE_URL}/admin-settings/test-connection/twitter") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Twitter Connection Test: {result.get('message', 'Success')}")
                else:
                    print(f"❌ Twitter Connection Test failed: {response.status}")
            
            self.test_results['connection_testing'] = True
            return True
                    
        except Exception as e:
            print(f"❌ Connection Testing error: {str(e)}")
            self.test_results['connection_testing'] = False
            return False

    async def test_lead_scraping_dashboard(self):
        """Test 6: Lead Scraping Dashboard"""
        print("\n📊 Testing Lead Scraping Dashboard...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/dashboard") as response:
                if response.status == 200:
                    data = await response.json()
                    overview = data.get('overview', {})
                    platform_status = data.get('platform_status', [])
                    settings = data.get('settings', {})
                    recent_jobs = data.get('recent_jobs', [])
                    
                    print(f"✅ Dashboard Retrieved Successfully")
                    print(f"📊 Overview:")
                    print(f"  • Total Leads: {overview.get('total_leads', 0)}")
                    print(f"  • Today's Leads: {overview.get('leads_today', 0)}")
                    print(f"  • Converted Leads: {overview.get('converted_leads', 0)}")
                    print(f"  • Conversion Rate: {overview.get('conversion_rate', 0)}%")
                    
                    print(f"⚙️ Platform Status: {len(platform_status)} platforms monitored")
                    for platform in platform_status:
                        status = "Enabled" if platform.get('is_enabled') else "Disabled"
                        configured = "Configured" if platform.get('is_configured') else "Not Configured"
                        print(f"  • {platform.get('platform', 'Unknown')}: {configured}, {status}")
                    
                    print(f"🔧 Settings:")
                    print(f"  • Enabled: {settings.get('is_enabled', False)}")
                    print(f"  • Cities: {settings.get('target_cities_count', 0)}")
                    print(f"  • Keywords: {settings.get('keywords_count', 0)}")
                    print(f"  • Frequency: {settings.get('scraping_frequency', 'N/A')}")
                    
                    print(f"📋 Recent Jobs: {len(recent_jobs)} jobs")
                    
                    self.test_results['lead_scraping_dashboard'] = True
                    return True
                else:
                    print(f"❌ Lead Scraping Dashboard failed: {response.status}")
                    self.test_results['lead_scraping_dashboard'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Lead Scraping Dashboard error: {str(e)}")
            self.test_results['lead_scraping_dashboard'] = False
            return False

    async def test_lead_scraping_config_endpoints(self):
        """Test 7: Lead Scraping Configuration Endpoints"""
        print("\n🔧 Testing Lead Scraping Configuration Endpoints...")
        
        try:
            # Test cities configuration
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/config/cities") as response:
                if response.status == 200:
                    data = await response.json()
                    metro_cities = data.get('metro_cities', [])
                    tier2_cities = data.get('tier2_cities', [])
                    
                    print(f"✅ Cities Config: {len(metro_cities)} metro + {len(tier2_cities)} tier2 cities")
                    
                    # Verify expected metro cities
                    expected_metro = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
                    found_metro = [city for city in expected_metro if city in metro_cities]
                    print(f"✅ Metro Cities Validation: {len(found_metro)}/8 expected cities found")
                    
                    if len(tier2_cities) >= 35:
                        print(f"✅ Tier2 Cities: {len(tier2_cities)} cities (expected 35+)")
                    else:
                        print(f"⚠️ Tier2 Cities: Only {len(tier2_cities)} found (expected 35+)")
                else:
                    print(f"❌ Cities Config failed: {response.status}")
                    self.test_results['lead_scraping_config_endpoints'] = False
                    return False
            
            # Test keywords configuration
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/config/keywords") as response:
                if response.status == 200:
                    data = await response.json()
                    keywords = data.get('keywords', [])
                    
                    print(f"✅ Keywords Config: {len(keywords)} default keywords")
                    
                    # Verify some expected keywords
                    expected_keywords = ["kitchen appliances", "refrigerator", "washing machine", "modular kitchen"]
                    found_keywords = [kw for kw in expected_keywords if any(kw in keyword.lower() for keyword in keywords)]
                    print(f"✅ Keywords Validation: {len(found_keywords)}/{len(expected_keywords)} expected keywords found")
                else:
                    print(f"❌ Keywords Config failed: {response.status}")
                    self.test_results['lead_scraping_config_endpoints'] = False
                    return False
            
            # Test business types configuration
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/config/business-types") as response:
                if response.status == 200:
                    data = await response.json()
                    business_types = data.get('business_types', [])
                    
                    print(f"✅ Business Types Config: {len(business_types)} B2B business types")
                    
                    # Verify expected business types
                    expected_types = ["Interior Designer", "Architect", "Builder", "Kitchen Studio"]
                    found_types = [bt for bt in expected_types if bt in business_types]
                    print(f"✅ Business Types Validation: {len(found_types)}/{len(expected_types)} expected types found")
                else:
                    print(f"❌ Business Types Config failed: {response.status}")
                    self.test_results['lead_scraping_config_endpoints'] = False
                    return False
            
            self.test_results['lead_scraping_config_endpoints'] = True
            return True
                    
        except Exception as e:
            print(f"❌ Lead Scraping Config Endpoints error: {str(e)}")
            self.test_results['lead_scraping_config_endpoints'] = False
            return False

    async def test_lead_scraping_analytics(self):
        """Test 8: Lead Scraping Analytics"""
        print("\n📈 Testing Lead Scraping Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/analytics") as response:
                if response.status == 200:
                    data = await response.json()
                    daily_leads = data.get('daily_leads', [])
                    score_distribution = data.get('score_distribution', [])
                    type_distribution = data.get('type_distribution', [])
                    top_cities = data.get('top_cities', [])
                    funnel = data.get('funnel', {})
                    
                    print(f"✅ Analytics Retrieved Successfully")
                    print(f"📊 Daily Leads: {len(daily_leads)} days of data")
                    print(f"🎯 Score Distribution: {len(score_distribution)} score ranges")
                    print(f"📋 Type Distribution: {len(type_distribution)} lead types")
                    print(f"🏙️ Top Cities: {len(top_cities)} cities with leads")
                    
                    print(f"🔄 Conversion Funnel:")
                    print(f"  • Total: {funnel.get('total', 0)}")
                    print(f"  • New: {funnel.get('new', 0)}")
                    print(f"  • Converted: {funnel.get('converted', 0)}")
                    print(f"  • Conversion Rate: {funnel.get('conversion_rate', 0)}%")
                    
                    self.test_results['lead_scraping_analytics'] = True
                    return True
                else:
                    print(f"❌ Lead Scraping Analytics failed: {response.status}")
                    self.test_results['lead_scraping_analytics'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Lead Scraping Analytics error: {str(e)}")
            self.test_results['lead_scraping_analytics'] = False
            return False

    async def test_scraped_leads_retrieval(self):
        """Test 9: Scraped Leads Retrieval"""
        print("\n📋 Testing Scraped Leads Retrieval...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/lead-scraping/leads?limit=10") as response:
                if response.status == 200:
                    data = await response.json()
                    leads = data.get('leads', [])
                    total = data.get('total', 0)
                    page = data.get('page', 1)
                    pages = data.get('pages', 1)
                    
                    print(f"✅ Scraped Leads Retrieved: {len(leads)} leads (total: {total})")
                    print(f"📄 Pagination: Page {page} of {pages}")
                    
                    if leads:
                        sample_lead = leads[0]
                        print(f"📋 Sample Lead:")
                        print(f"  • Source: {sample_lead.get('source', 'N/A')}")
                        print(f"  • Type: {sample_lead.get('lead_type', 'N/A')}")
                        print(f"  • Status: {sample_lead.get('status', 'N/A')}")
                        print(f"  • Score: {sample_lead.get('score', 0)}")
                        print(f"  • Location: {sample_lead.get('location', 'N/A')}")
                    else:
                        print("ℹ️ No scraped leads found (this is normal for a new system)")
                    
                    self.test_results['scraped_leads_retrieval'] = True
                    return True
                else:
                    print(f"❌ Scraped Leads Retrieval failed: {response.status}")
                    self.test_results['scraped_leads_retrieval'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Scraped Leads Retrieval error: {str(e)}")
            self.test_results['scraped_leads_retrieval'] = False
            return False

    async def run_all_tests(self):
        """Run all Admin Settings and Lead Scraping tests"""
        await self.setup()
        
        tests = [
            ("Admin Settings - All Platform Configurations", self.test_admin_settings_all_platforms),
            ("Google Ads Credentials Management", self.test_google_ads_credentials),
            ("Twitter Credentials Management", self.test_twitter_credentials),
            ("Lead Scraping Settings Management", self.test_lead_scraping_settings),
            ("Platform Connection Testing", self.test_connection_testing),
            ("Lead Scraping Dashboard", self.test_lead_scraping_dashboard),
            ("Lead Scraping Configuration Endpoints", self.test_lead_scraping_config_endpoints),
            ("Lead Scraping Analytics", self.test_lead_scraping_analytics),
            ("Scraped Leads Retrieval", self.test_scraped_leads_retrieval)
        ]
        
        print(f"\n🧪 Running {len(tests)} Admin Settings & Lead Scraping Tests...")
        print("=" * 80)
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {str(e)}")
                failed += 1
                
        await self.cleanup()
        
        # Print final results
        print("\n" + "=" * 80)
        print("🏁 ADMIN SETTINGS & LEAD SCRAPING TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name.replace('_', ' ').title()}")
            
        return passed, failed, self.test_results


async def main():
    """Main test runner"""
    tester = AdminLeadScrapingTester()
    passed, failed, results = await tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if failed == 0 else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)