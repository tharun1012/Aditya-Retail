from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
from utils import normalize_phone
from motor.motor_asyncio import AsyncIOMotorClient
import random

router = APIRouter(prefix="/admin/customers", tags=["Customers"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    customer_type: str = "B2C"  # B2B or B2C
    gst_number: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_pincode: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_pincode: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_location_link: Optional[str] = None
    store_code: Optional[str] = None
    notes: Optional[str] = None


@router.post("/")
async def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    try:
        # Check if customer with phone already exists
        normalized_phone = normalize_phone(customer.phone)
        existing = await db.customers.find_one({"phone": normalized_phone}) if normalized_phone else None
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
        
        customer_data = {
            "id": str(uuid.uuid4()),
            "name": customer.name,
            "phone": normalized_phone,
            "email": customer.email,
            "customer_type": customer.customer_type,
            "gst_number": customer.gst_number,
            "billing_address": customer.billing_address,
            "billing_city": customer.billing_city,
            "billing_state": customer.billing_state,
            "billing_pincode": customer.billing_pincode,
            "shipping_address": customer.shipping_address,
            "shipping_city": customer.shipping_city,
            "shipping_state": customer.shipping_state,
            "shipping_pincode": customer.shipping_pincode,
            "shipping_phone": customer.shipping_phone,
            "shipping_location_link": customer.shipping_location_link,
            "store_code": customer.store_code,
            "notes": customer.notes,
            "order_count": 0,
            "total_spent": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.customers.insert_one(customer_data)
        
        return {
            "status": "success",
            "message": "Customer created successfully",
            "customer_id": customer_data["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_all_customers(page: int = 1, limit: int = 20, segment: Optional[str] = None, store_code: Optional[str] = None):
    """Get all customers with pagination and segmentation"""
    try:
        query = {}
        if store_code:
            query["store_code"] = store_code
        if segment:
            if segment == "vip":
                query["total_spent"] = {"$gte": 50000}
            elif segment == "regular":
                query["order_count"] = {"$gte": 5}
            elif segment == "new":
                query["order_count"] = {"$lt": 2}
            elif segment == "inactive":
                # Customers with no orders in last 90 days
                pass
        
        skip = (page - 1) * limit
        
        # Check if customers collection exists
        collections = await db.list_collection_names()
        if 'customers' not in collections:
            return {
                "status": "success",
                "customers": [],
                "pagination": {"page": 1, "limit": limit, "total": 0, "pages": 0}
            }
        
        customers = await db.customers.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        total = await db.customers.count_documents(query)
        
        return {
            "status": "success",
            "customers": customers,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}")
async def get_customer_details(customer_id: str):
    """Get detailed customer information"""
    try:
        customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get customer's orders (limit to most recent 100 for performance)
        orders = await db.orders.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1).limit(100).to_list(100)

        # Get customer's quotations. Match by linked customer_id (new
        # quotations) OR by phone (older quotations created before the
        # customer_id link existed), so nothing falls through the cracks.
        quotation_query = {"customer_id": customer_id}
        if customer.get("phone"):
            quotation_query = {
                "$or": [
                    {"customer_id": customer_id},
                    {"customer_phone": customer["phone"]}
                ]
            }
        quotations = await db.quotations.find(quotation_query, {"_id": 0}).sort("created_at", -1).limit(100).to_list(100)

        return {
            "status": "success",
            "customer": customer,
            "orders": orders,
            "quotations": quotations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_customer_stats():
    """Get customer statistics summary"""
    try:
        collections = await db.list_collection_names()
        if 'customers' not in collections:
            return {
                "status": "success",
                "data": {
                    "total_customers": 0,
                    "new_this_month": 0,
                    "vip_customers": 0,
                    "regular_customers": 0,
                    "inactive_customers": 0,
                    "average_clv": 0
                }
            }
        
        total_customers = await db.customers.count_documents({})
        vip_customers = await db.customers.count_documents({"total_spent": {"$gte": 50000}})
        regular_customers = await db.customers.count_documents({"order_count": {"$gte": 5}})
        
        # Calculate average CLV
        pipeline = [
            {"$group": {"_id": None, "avg_clv": {"$avg": "$total_spent"}}}
        ]
        clv_result = await db.customers.aggregate(pipeline).to_list(1)
        avg_clv = (clv_result[0]['avg_clv'] if clv_result else 0) or 0

        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        new_this_month = await db.customers.count_documents({"created_at": {"$gte": month_start}})
        inactive_customers = await db.customers.count_documents({"$or": [{"order_count": {"$in": [0, None]}}, {"order_count": {"$exists": False}}]})

        return {
            "status": "success",
            "data": {
                "total_customers": total_customers,
                "new_this_month": new_this_month,
                "vip_customers": vip_customers,
                "regular_customers": regular_customers,
                "inactive_customers": inactive_customers,
                "average_clv": round(avg_clv, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/segments/breakdown")
async def get_customer_segments():
    """Get customer segmentation breakdown"""
    try:
        collections = await db.list_collection_names()
        if 'customers' not in collections:
            return {
                "status": "success",
                "data": []
            }
        
        # Segment by spending
        segments = [
            {"segment": "VIP (>₹50K)", "count": await db.customers.count_documents({"total_spent": {"$gte": 50000}})},
            {"segment": "Premium (₹20K-₹50K)", "count": await db.customers.count_documents({"total_spent": {"$gte": 20000, "$lt": 50000}})},
            {"segment": "Regular (₹5K-₹20K)", "count": await db.customers.count_documents({"total_spent": {"$gte": 5000, "$lt": 20000}})},
            {"segment": "New (<₹5K)", "count": await db.customers.count_documents({"total_spent": {"$lt": 5000}})}
        ]
        
        return {
            "status": "success",
            "data": segments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
