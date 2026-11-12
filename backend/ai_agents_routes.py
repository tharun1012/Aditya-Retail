from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
import random

router = APIRouter(prefix="/admin/ai-agents", tags=["AI Agents"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

@router.get("/performance-summary")
async def get_agents_performance():
    """Get performance summary for all AI agents"""
    try:
        # For now, generate mock data
        # In production, this would query actual conversation logs
        
        agents_data = {
            "sales_agent": {
                "name": "Sales AI",
                "total_interactions": random.randint(150, 300),
                "successful_interactions": random.randint(100, 200),
                "success_rate": round(random.uniform(65, 85), 2),
                "average_response_time": round(random.uniform(1.2, 2.5), 2),
                "customer_satisfaction": round(random.uniform(4.2, 4.8), 2),
                "revenue_attributed": random.randint(50000, 150000),
                "leads_generated": random.randint(80, 150),
                "conversion_rate": round(random.uniform(15, 30), 2)
            },
            "service_agent": {
                "name": "Service AI",
                "total_interactions": random.randint(200, 400),
                "successful_interactions": random.randint(150, 350),
                "success_rate": round(random.uniform(70, 90), 2),
                "average_response_time": round(random.uniform(0.8, 1.8), 2),
                "customer_satisfaction": round(random.uniform(4.3, 4.9), 2),
                "tickets_resolved": random.randint(120, 250),
                "average_resolution_time": round(random.uniform(5, 15), 2),
                "escalation_rate": round(random.uniform(5, 15), 2)
            },
            "marketing_agent": {
                "name": "Marketing AI",
                "total_interactions": random.randint(100, 200),
                "successful_interactions": random.randint(70, 150),
                "success_rate": round(random.uniform(60, 80), 2),
                "average_response_time": round(random.uniform(1.5, 3.0), 2),
                "customer_satisfaction": round(random.uniform(4.0, 4.6), 2),
                "campaigns_created": random.randint(10, 25),
                "emails_sent": random.randint(500, 2000),
                "open_rate": round(random.uniform(20, 35), 2),
                "click_through_rate": round(random.uniform(3, 8), 2)
            },
            "delivery_agent": {
                "name": "Delivery AI",
                "total_interactions": random.randint(50, 150),
                "successful_interactions": random.randint(40, 130),
                "success_rate": round(random.uniform(75, 95), 2),
                "average_response_time": round(random.uniform(1.0, 2.0), 2),
                "customer_satisfaction": round(random.uniform(4.1, 4.7), 2),
                "deliveries_tracked": random.randint(50, 120),
                "on_time_delivery_rate": round(random.uniform(85, 95), 2),
                "average_delivery_time": round(random.uniform(2, 5), 2)
            },
            "stock_agent": {
                "name": "Stock AI",
                "total_interactions": random.randint(30, 100),
                "successful_interactions": random.randint(25, 90),
                "success_rate": round(random.uniform(80, 98), 2),
                "average_response_time": round(random.uniform(0.5, 1.5), 2),
                "customer_satisfaction": round(random.uniform(4.4, 4.9), 2),
                "reorder_predictions": random.randint(15, 40),
                "prediction_accuracy": round(random.uniform(85, 95), 2),
                "cost_savings": random.randint(10000, 50000)
            }
        }
        
        return {
            "status": "success",
            "data": agents_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-logs")
async def get_conversation_logs(agent_type: Optional[str] = None, limit: int = 50):
    """Get conversation logs for AI agents"""
    try:
        query = {}
        if agent_type:
            query["agent_type"] = agent_type
        
        # Check if collection exists
        collections = await db.list_collection_names()
        if 'conversation_logs' not in collections:
            # Return empty list if no logs yet
            return {
                "status": "success",
                "logs": []
            }
        
        logs = await db.conversation_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_agent_trends(days: int = 30):
    """Get performance trends for AI agents over time"""
    try:
        # Generate mock trend data
        today = datetime.now()
        trends = []
        
        for i in range(days):
            date = today - timedelta(days=days-i-1)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "sales_interactions": random.randint(5, 15),
                "service_interactions": random.randint(8, 20),
                "marketing_interactions": random.randint(3, 10),
                "delivery_interactions": random.randint(2, 8),
                "stock_interactions": random.randint(1, 5)
            })
        
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison")
async def compare_agents():
    """Compare performance metrics across all agents"""
    try:
        comparison = {
            "efficiency": {
                "sales": round(random.uniform(70, 85), 2),
                "service": round(random.uniform(75, 90), 2),
                "marketing": round(random.uniform(65, 80), 2),
                "delivery": round(random.uniform(80, 95), 2),
                "stock": round(random.uniform(85, 98), 2)
            },
            "customer_satisfaction": {
                "sales": round(random.uniform(4.2, 4.7), 2),
                "service": round(random.uniform(4.3, 4.8), 2),
                "marketing": round(random.uniform(4.0, 4.5), 2),
                "delivery": round(random.uniform(4.1, 4.6), 2),
                "stock": round(random.uniform(4.4, 4.9), 2)
            },
            "response_time": {
                "sales": round(random.uniform(1.5, 2.5), 2),
                "service": round(random.uniform(1.0, 2.0), 2),
                "marketing": round(random.uniform(2.0, 3.0), 2),
                "delivery": round(random.uniform(1.2, 2.2), 2),
                "stock": round(random.uniform(0.8, 1.5), 2)
            }
        }
        
        return {
            "status": "success",
            "data": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
