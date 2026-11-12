"""
Marketing Analytics Routes
Comprehensive marketing performance tracking and customer journey analytics
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/marketing-analytics", tags=["Marketing Analytics"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

@router.get("/campaign-performance")
async def get_campaign_performance():
    """
    Get performance metrics for all marketing campaigns
    Shows ROI, CPL, conversion rates, etc.
    """
    try:
        campaigns = await db.marketing_campaigns.find({}, {"_id": 0}).to_list(100)
        
        campaign_metrics = []
        
        for campaign in campaigns:
            campaign_id = campaign.get('id')
            budget = campaign.get('budget', 0)
            
            # Count leads from this campaign
            leads_from_campaign = await db.leads.count_documents({
                "source_campaign": campaign_id
            })
            
            # If no specific campaign tracking, use estimated metrics
            if leads_from_campaign == 0:
                # Use expected metrics from campaign
                expected = campaign.get('expected_metrics', {})
                leads_from_campaign = expected.get('leads_per_month', 5)
            
            # Calculate CPL
            cost_per_lead = (budget / leads_from_campaign) if leads_from_campaign > 0 else budget
            
            # Count conversions (leads that became orders)
            conversions = await db.orders.count_documents({
                "lead_source_campaign": campaign_id
            })
            
            # Calculate conversion rate
            conversion_rate = (conversions / leads_from_campaign * 100) if leads_from_campaign > 0 else 0
            
            # Calculate revenue from this campaign
            orders = await db.orders.find({
                "lead_source_campaign": campaign_id
            }, {"_id": 0, "total": 1}).to_list(1000)
            
            revenue = sum(order.get('total', 0) for order in orders)
            
            # Calculate ROI
            roi = ((revenue - budget) / budget * 100) if budget > 0 else 0
            
            # Simulated metrics for campaigns without real ad tracking
            # These will be replaced when Google/Facebook ads are connected
            simulated_impressions = int(budget * 10)  # Rough estimate: ₹1 = 10 impressions
            simulated_clicks = int(simulated_impressions * 0.02)  # 2% CTR
            ctr = 2.0  # Click-through rate
            
            campaign_metrics.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign.get('campaign_name'),
                "product_name": campaign.get('product_name'),
                "budget": budget,
                "budget_spent": budget,  # Assume fully spent for now
                "status": campaign.get('status'),
                "impressions": simulated_impressions,
                "clicks": simulated_clicks,
                "ctr": ctr,
                "leads": leads_from_campaign,
                "cost_per_lead": round(cost_per_lead, 2),
                "conversions": conversions,
                "conversion_rate": round(conversion_rate, 2),
                "revenue": round(revenue, 2),
                "roi": round(roi, 2),
                "channels": campaign.get('channels', []),
                "created_at": campaign.get('created_at')
            })
        
        # Calculate totals
        total_budget = sum(c['budget'] for c in campaign_metrics)
        total_leads = sum(c['leads'] for c in campaign_metrics)
        total_conversions = sum(c['conversions'] for c in campaign_metrics)
        total_revenue = sum(c['revenue'] for c in campaign_metrics)
        avg_cpl = (total_budget / total_leads) if total_leads > 0 else 0
        overall_roi = ((total_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "status": "success",
            "summary": {
                "total_campaigns": len(campaign_metrics),
                "total_budget": round(total_budget, 2),
                "total_leads": total_leads,
                "total_conversions": total_conversions,
                "total_revenue": round(total_revenue, 2),
                "avg_cost_per_lead": round(avg_cpl, 2),
                "overall_roi": round(overall_roi, 2),
                "avg_conversion_rate": round((total_conversions / total_leads * 100) if total_leads > 0 else 0, 2)
            },
            "campaigns": campaign_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channel-performance")
async def get_channel_performance():
    """
    Get performance metrics by marketing channel
    (Google Ads, Facebook, Email, WhatsApp, etc.)
    """
    try:
        # Get leads by source
        lead_sources = await db.leads.aggregate([
            {
                "$group": {
                    "_id": "$source",
                    "count": {"$sum": 1},
                    "leads": {"$push": "$id"}
                }
            }
        ]).to_list(100)
        
        channel_metrics = []
        
        for source_group in lead_sources:
            source = source_group['_id']
            lead_count = source_group['count']
            lead_ids = source_group['leads']
            
            # Count conversions from this source
            conversions = await db.orders.count_documents({
                "customer_email": {"$in": [
                    lead.get('email') 
                    for lead in await db.leads.find(
                        {"id": {"$in": lead_ids}}, 
                        {"_id": 0, "email": 1}
                    ).to_list(1000)
                ]}
            })
            
            # Calculate conversion rate
            conversion_rate = (conversions / lead_count * 100) if lead_count > 0 else 0
            
            # Get revenue from this source
            lead_emails = [
                lead.get('email') 
                for lead in await db.leads.find(
                    {"id": {"$in": lead_ids}}, 
                    {"_id": 0, "email": 1}
                ).to_list(1000)
            ]
            
            orders = await db.orders.find({
                "customer_email": {"$in": lead_emails}
            }, {"_id": 0, "total": 1}).to_list(1000)
            
            revenue = sum(order.get('total', 0) for order in orders)
            
            # Map source to channel name
            channel_map = {
                'google': 'Google Ads',
                'facebook': 'Facebook Ads',
                'instagram': 'Instagram',
                'ai_chat_website': 'Website (AI Chat)',
                'email': 'Email Campaign',
                'whatsapp': 'WhatsApp',
                'referral': 'Referral',
                'walk_in': 'Walk-in',
                'organic': 'Organic Search'
            }
            
            channel_name = channel_map.get(source, source.title())
            
            channel_metrics.append({
                "channel": channel_name,
                "source_key": source,
                "leads": lead_count,
                "conversions": conversions,
                "conversion_rate": round(conversion_rate, 2),
                "revenue": round(revenue, 2),
                "avg_revenue_per_lead": round(revenue / lead_count, 2) if lead_count > 0 else 0
            })
        
        # Sort by leads descending
        channel_metrics.sort(key=lambda x: x['leads'], reverse=True)
        
        return {
            "status": "success",
            "channels": channel_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer-journey-funnel")
async def get_customer_journey_funnel():
    """
    Get customer journey funnel data
    Shows progression through stages: Awareness → Interest → Consideration → Intent → Purchase
    """
    try:
        # Count leads by status/stage
        total_leads = await db.leads.count_documents({})
        
        # Map lead status to journey stages
        stage_mapping = {
            'new': 'awareness',
            'contacted': 'interest',
            'interested': 'consideration',
            'demo_scheduled': 'consideration',
            'warm': 'intent',
            'proposal_sent': 'intent',
            'negotiation': 'intent',
            'won': 'purchase',
            'lost': 'dropped'
        }
        
        # Get all leads with their status
        leads = await db.leads.find({}, {"_id": 0, "status": 1, "created_at": 1}).to_list(10000)
        
        # Count by stage
        stage_counts = {
            'awareness': 0,
            'interest': 0,
            'consideration': 0,
            'intent': 0,
            'purchase': 0
        }
        
        for lead in leads:
            status = lead.get('status', 'new')
            stage = stage_mapping.get(status, 'awareness')
            if stage in stage_counts:
                stage_counts[stage] += 1
        
        # Calculate percentages and drop-offs
        funnel_data = []
        previous_count = total_leads
        
        stages = [
            ('awareness', 'Awareness', 'Lead captured'),
            ('interest', 'Interest', 'Engaged with content'),
            ('consideration', 'Consideration', 'Evaluating options'),
            ('intent', 'Intent', 'Ready to buy'),
            ('purchase', 'Purchase', 'Converted')
        ]
        
        for stage_key, stage_label, description in stages:
            count = stage_counts[stage_key]
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            drop_off = previous_count - count
            drop_off_rate = (drop_off / previous_count * 100) if previous_count > 0 else 0
            
            funnel_data.append({
                "stage": stage_key,
                "label": stage_label,
                "description": description,
                "count": count,
                "percentage": round(percentage, 1),
                "drop_off": drop_off,
                "drop_off_rate": round(drop_off_rate, 1)
            })
            
            previous_count = count
        
        # Calculate overall conversion rate
        purchases = stage_counts['purchase']
        overall_conversion = (purchases / total_leads * 100) if total_leads > 0 else 0
        
        # Identify bottleneck (stage with highest drop-off rate)
        bottleneck = max(funnel_data[:-1], key=lambda x: x['drop_off_rate']) if len(funnel_data) > 1 else None
        
        return {
            "status": "success",
            "funnel": funnel_data,
            "summary": {
                "total_leads": total_leads,
                "total_purchases": purchases,
                "overall_conversion_rate": round(overall_conversion, 2),
                "bottleneck_stage": bottleneck['label'] if bottleneck else None,
                "bottleneck_drop_off": bottleneck['drop_off_rate'] if bottleneck else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lead-source-attribution")
async def get_lead_source_attribution():
    """
    Attribution analysis - which sources bring best quality leads
    """
    try:
        sources = await db.leads.distinct("source")
        
        attribution_data = []
        
        for source in sources:
            # Get leads from this source
            source_leads = await db.leads.find(
                {"source": source}, 
                {"_id": 0, "id": 1, "email": 1, "created_at": 1}
            ).to_list(10000)
            
            lead_count = len(source_leads)
            lead_emails = [lead.get('email') for lead in source_leads if lead.get('email')]
            
            # Count conversions
            conversions = await db.orders.count_documents({
                "customer_email": {"$in": lead_emails}
            })
            
            # Calculate revenue
            orders = await db.orders.find({
                "customer_email": {"$in": lead_emails}
            }, {"_id": 0, "total": 1}).to_list(10000)
            
            revenue = sum(order.get('total', 0) for order in orders)
            
            # Calculate metrics
            conversion_rate = (conversions / lead_count * 100) if lead_count > 0 else 0
            revenue_per_lead = revenue / lead_count if lead_count > 0 else 0
            
            # Quality score (based on conversion rate and revenue per lead)
            quality_score = (conversion_rate * 0.6) + (min(revenue_per_lead / 10000, 10) * 0.4)
            
            attribution_data.append({
                "source": source,
                "leads": lead_count,
                "conversions": conversions,
                "conversion_rate": round(conversion_rate, 2),
                "revenue": round(revenue, 2),
                "revenue_per_lead": round(revenue_per_lead, 2),
                "quality_score": round(quality_score, 1),
                "quality_rating": "High" if quality_score > 7 else "Medium" if quality_score > 4 else "Low"
            })
        
        # Sort by quality score
        attribution_data.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return {
            "status": "success",
            "attribution": attribution_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/time-to-conversion")
async def get_time_to_conversion():
    """
    Analyze average time from lead capture to conversion
    """
    try:
        # Get all converted leads (those who have orders)
        orders = await db.orders.find({}, {"_id": 0, "customer_email": 1, "created_at": 1}).to_list(10000)
        
        conversion_times = []
        
        for order in orders:
            email = order.get('customer_email')
            order_date = order.get('created_at')
            
            if not email or not order_date:
                continue
            
            # Find the lead with this email
            lead = await db.leads.find_one(
                {"email": email}, 
                {"_id": 0, "created_at": 1}
            )
            
            if lead and lead.get('created_at'):
                lead_date = lead['created_at']
                
                # Calculate time difference - handle both string and datetime formats
                try:
                    if isinstance(order_date, str):
                        order_datetime = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                    else:
                        order_datetime = order_date
                    
                    if isinstance(lead_date, str):
                        lead_datetime = datetime.fromisoformat(lead_date.replace('Z', '+00:00'))
                    else:
                        lead_datetime = lead_date
                    
                    # Make both timezone-naive for comparison
                    if hasattr(order_datetime, 'tzinfo') and order_datetime.tzinfo is not None:
                        order_datetime = order_datetime.replace(tzinfo=None)
                    if hasattr(lead_datetime, 'tzinfo') and lead_datetime.tzinfo is not None:
                        lead_datetime = lead_datetime.replace(tzinfo=None)
                    
                    time_diff = (order_datetime - lead_datetime).total_seconds() / 86400  # Days
                    if time_diff >= 0:  # Only add positive time differences
                        conversion_times.append(time_diff)
                except Exception:
                    continue  # Skip problematic date entries
        
        if conversion_times:
            avg_time = sum(conversion_times) / len(conversion_times)
            min_time = min(conversion_times)
            max_time = max(conversion_times)
            median_time = sorted(conversion_times)[len(conversion_times) // 2]
        else:
            avg_time = min_time = max_time = median_time = 0
        
        return {
            "status": "success",
            "metrics": {
                "average_days": round(avg_time, 1),
                "median_days": round(median_time, 1),
                "fastest_days": round(min_time, 1),
                "slowest_days": round(max_time, 1),
                "total_conversions": len(conversion_times)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
