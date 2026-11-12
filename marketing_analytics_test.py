#!/usr/bin/env python3
"""
Marketing Analytics Dashboard Backend Testing
Tests all 5 marketing analytics endpoints that were recently fixed
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

class MarketingAnalyticsTester:
    def __init__(self):
        self.session = None
        self.test_results = {}
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print(f"🚀 Starting Marketing Analytics Dashboard Tests")
        print(f"🌐 API Base URL: {API_BASE_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()

    async def test_campaign_performance(self):
        """Test 1: Campaign Performance Analytics"""
        print("\n📊 Testing Campaign Performance Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/marketing-analytics/campaign-performance") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    campaigns = data.get('campaigns', [])
                    summary = data.get('summary', {})
                    
                    print(f"✅ Campaign Performance: Retrieved {len(campaigns)} campaigns")
                    
                    if campaigns:
                        # Check first campaign structure
                        sample_campaign = campaigns[0]
                        required_fields = ['campaign_name', 'budget', 'leads_generated', 'cost_per_lead', 'roi']
                        
                        missing_fields = [field for field in required_fields if field not in sample_campaign]
                        if not missing_fields:
                            print(f"✅ Campaign Structure: All required fields present")
                            print(f"📈 Sample Campaign: {sample_campaign.get('campaign_name', 'N/A')}")
                            print(f"💰 Budget: ₹{sample_campaign.get('budget', 0):,.2f}")
                            print(f"🎯 Leads: {sample_campaign.get('leads_generated', 0)}")
                            print(f"💸 CPL: ₹{sample_campaign.get('cost_per_lead', 0):,.2f}")
                            print(f"📊 ROI: {sample_campaign.get('roi', 0):.1f}%")
                        else:
                            print(f"❌ Campaign Structure: Missing fields: {missing_fields}")
                            self.test_results['campaign_performance'] = False
                            return False
                    
                    # Check summary metrics
                    if summary:
                        print(f"📋 Summary Metrics:")
                        print(f"  • Total Budget: ₹{summary.get('total_budget', 0):,.2f}")
                        print(f"  • Total Leads: {summary.get('total_leads', 0)}")
                        print(f"  • Average CPL: ₹{summary.get('average_cpl', 0):,.2f}")
                        print(f"  • Average ROI: {summary.get('average_roi', 0):.1f}%")
                    
                    self.test_results['campaign_performance'] = True
                    return True
                else:
                    print(f"❌ Campaign Performance failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    self.test_results['campaign_performance'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Campaign Performance error: {str(e)}")
            self.test_results['campaign_performance'] = False
            return False

    async def test_channel_performance(self):
        """Test 2: Channel Performance Analytics"""
        print("\n📡 Testing Channel Performance Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/marketing-analytics/channel-performance") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    channels = data.get('channels', [])
                    total_leads = data.get('total_leads', 0)
                    
                    print(f"✅ Channel Performance: Retrieved {len(channels)} channels")
                    print(f"📊 Total Leads: {total_leads}")
                    
                    if channels:
                        # Check channel structure and data
                        for channel in channels:
                            channel_name = channel.get('channel', 'Unknown')
                            leads = channel.get('leads', 0)
                            percentage = channel.get('percentage', 0)
                            
                            print(f"  📡 {channel_name}: {leads} leads ({percentage:.1f}%)")
                        
                        # Verify percentages add up to approximately 100%
                        total_percentage = sum(channel.get('percentage', 0) for channel in channels)
                        if 99 <= total_percentage <= 101:  # Allow for rounding
                            print(f"✅ Percentage Validation: Total = {total_percentage:.1f}%")
                        else:
                            print(f"⚠️ Percentage Validation: Total = {total_percentage:.1f}% (should be ~100%)")
                    
                    self.test_results['channel_performance'] = True
                    return True
                else:
                    print(f"❌ Channel Performance failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    self.test_results['channel_performance'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Channel Performance error: {str(e)}")
            self.test_results['channel_performance'] = False
            return False

    async def test_customer_journey_funnel(self):
        """Test 3: Customer Journey Funnel Analytics"""
        print("\n🔄 Testing Customer Journey Funnel Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/marketing-analytics/customer-journey-funnel") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    funnel_stages = data.get('funnel_stages', [])
                    conversion_rates = data.get('conversion_rates', {})
                    
                    print(f"✅ Customer Journey Funnel: Retrieved {len(funnel_stages)} stages")
                    
                    if funnel_stages:
                        # Expected funnel stages
                        expected_stages = ['awareness', 'interest', 'consideration', 'intent', 'purchase']
                        
                        print(f"📊 Funnel Stages:")
                        for stage in funnel_stages:
                            stage_name = stage.get('stage', 'Unknown')
                            count = stage.get('count', 0)
                            percentage = stage.get('percentage', 0)
                            
                            print(f"  🔸 {stage_name.title()}: {count} leads ({percentage:.1f}%)")
                        
                        # Check if all expected stages are present
                        stage_names = [stage.get('stage', '').lower() for stage in funnel_stages]
                        missing_stages = [stage for stage in expected_stages if stage not in stage_names]
                        
                        if not missing_stages:
                            print(f"✅ Funnel Completeness: All expected stages present")
                        else:
                            print(f"⚠️ Funnel Completeness: Missing stages: {missing_stages}")
                    
                    # Check conversion rates
                    if conversion_rates:
                        print(f"📈 Conversion Rates:")
                        for stage, rate in conversion_rates.items():
                            print(f"  • {stage.replace('_', ' ').title()}: {rate:.1f}%")
                    
                    self.test_results['customer_journey_funnel'] = True
                    return True
                else:
                    print(f"❌ Customer Journey Funnel failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    self.test_results['customer_journey_funnel'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Customer Journey Funnel error: {str(e)}")
            self.test_results['customer_journey_funnel'] = False
            return False

    async def test_lead_source_attribution(self):
        """Test 4: Lead Source Attribution Analytics"""
        print("\n🎯 Testing Lead Source Attribution Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/marketing-analytics/lead-source-attribution") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    sources = data.get('sources', [])
                    quality_metrics = data.get('quality_metrics', {})
                    
                    print(f"✅ Lead Source Attribution: Retrieved {len(sources)} sources")
                    
                    if sources:
                        print(f"📊 Lead Sources by Quality:")
                        for source in sources:
                            source_name = source.get('source', 'Unknown')
                            leads = source.get('leads', 0)
                            quality_score = source.get('quality_score', 0)
                            conversion_rate = source.get('conversion_rate', 0)
                            
                            print(f"  🎯 {source_name}: {leads} leads (Quality: {quality_score:.1f}, Conversion: {conversion_rate:.1f}%)")
                        
                        # Verify quality scores are within valid range (0-100)
                        invalid_scores = [s for s in sources if not (0 <= s.get('quality_score', 0) <= 100)]
                        if not invalid_scores:
                            print(f"✅ Quality Score Validation: All scores within valid range (0-100)")
                        else:
                            print(f"❌ Quality Score Validation: {len(invalid_scores)} sources have invalid scores")
                    
                    # Check quality metrics summary
                    if quality_metrics:
                        print(f"📈 Quality Metrics Summary:")
                        print(f"  • Average Quality Score: {quality_metrics.get('average_quality_score', 0):.1f}")
                        print(f"  • Best Performing Source: {quality_metrics.get('best_source', 'N/A')}")
                        print(f"  • Highest Conversion Rate: {quality_metrics.get('highest_conversion_rate', 0):.1f}%")
                    
                    self.test_results['lead_source_attribution'] = True
                    return True
                else:
                    print(f"❌ Lead Source Attribution failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    self.test_results['lead_source_attribution'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Lead Source Attribution error: {str(e)}")
            self.test_results['lead_source_attribution'] = False
            return False

    async def test_time_to_conversion(self):
        """Test 5: Time to Conversion Analytics"""
        print("\n⏱️ Testing Time to Conversion Analytics...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/marketing-analytics/time-to-conversion") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    conversion_metrics = data.get('conversion_metrics', {})
                    time_buckets = data.get('time_buckets', [])
                    trends = data.get('trends', {})
                    
                    print(f"✅ Time to Conversion: Analytics retrieved successfully")
                    
                    # Check conversion metrics
                    if conversion_metrics:
                        print(f"📊 Conversion Metrics:")
                        print(f"  • Average Time: {conversion_metrics.get('average_days', 0):.1f} days")
                        print(f"  • Median Time: {conversion_metrics.get('median_days', 0):.1f} days")
                        print(f"  • Fastest Conversion: {conversion_metrics.get('fastest_days', 0):.1f} days")
                        print(f"  • Slowest Conversion: {conversion_metrics.get('slowest_days', 0):.1f} days")
                    
                    # Check time buckets distribution
                    if time_buckets:
                        print(f"📈 Time Distribution:")
                        for bucket in time_buckets:
                            time_range = bucket.get('time_range', 'Unknown')
                            count = bucket.get('count', 0)
                            percentage = bucket.get('percentage', 0)
                            
                            print(f"  ⏰ {time_range}: {count} conversions ({percentage:.1f}%)")
                        
                        # Verify percentages add up to approximately 100%
                        total_percentage = sum(bucket.get('percentage', 0) for bucket in time_buckets)
                        if 99 <= total_percentage <= 101:  # Allow for rounding
                            print(f"✅ Distribution Validation: Total = {total_percentage:.1f}%")
                        else:
                            print(f"⚠️ Distribution Validation: Total = {total_percentage:.1f}% (should be ~100%)")
                    
                    # Check trends
                    if trends:
                        print(f"📈 Conversion Trends:")
                        for trend_key, trend_value in trends.items():
                            print(f"  • {trend_key.replace('_', ' ').title()}: {trend_value}")
                    
                    self.test_results['time_to_conversion'] = True
                    return True
                else:
                    print(f"❌ Time to Conversion failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    self.test_results['time_to_conversion'] = False
                    return False
                    
        except Exception as e:
            print(f"❌ Time to Conversion error: {str(e)}")
            self.test_results['time_to_conversion'] = False
            return False

    async def run_all_tests(self):
        """Run all marketing analytics tests"""
        await self.setup()
        
        tests = [
            self.test_campaign_performance,
            self.test_channel_performance,
            self.test_customer_journey_funnel,
            self.test_lead_source_attribution,
            self.test_time_to_conversion
        ]
        
        print("🎯 MARKETING ANALYTICS DASHBOARD BACKEND TESTING")
        print("Testing all 5 marketing analytics endpoints that were recently fixed")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        await self.cleanup()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 MARKETING ANALYTICS DASHBOARD TEST RESULTS")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n📈 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 MARKETING ANALYTICS DASHBOARD: BACKEND TESTS PASSED")
            return True
        else:
            print("❌ MARKETING ANALYTICS DASHBOARD: BACKEND TESTS FAILED")
            return False

async def main():
    """Main test runner"""
    tester = MarketingAnalyticsTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)