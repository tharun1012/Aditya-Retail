from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/admin/analytics", tags=["Analytics"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """Get overall dashboard summary with key metrics"""
    try:
        # Count total orders
        total_orders = await db.orders.count_documents({})
        
        # Calculate total revenue
        orders = await db.orders.find({}).to_list(None)
        total_revenue = sum(order.get('total_amount', 0) for order in orders)
        
        # Count active products
        total_products = await db.products.count_documents({})
        
        # Calculate averages
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2),
                "total_products": total_products,
                "avg_order_value": round(avg_order_value, 2),
                "growth_rate": 15.3  # Mock growth rate
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales-trends")
async def get_sales_trends(days: int = 30):
    """Get sales trends over specified number of days"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get orders within date range
        orders = await db.orders.find({}).to_list(None)
        
        # Group by date
        daily_sales = {}
        for order in orders:
            created_at = order.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    date = created_at.split()[0]
                else:
                    date = created_at.strftime('%Y-%m-%d')
                
                if date not in daily_sales:
                    daily_sales[date] = {'orders': 0, 'revenue': 0}
                
                daily_sales[date]['orders'] += 1
                daily_sales[date]['revenue'] += order.get('total_amount', 0)
        
        # Convert to list
        trends = [
            {
                "date": date,
                "orders": data['orders'],
                "revenue": round(data['revenue'], 2)
            }
            for date, data in sorted(daily_sales.items())
        ]
        
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-products")
async def get_top_products(limit: int = 10):
    """Get top selling products"""
    try:
        # Get all orders
        orders = await db.orders.find({}).to_list(None)
        
        # Count product sales
        product_sales = {}
        for order in orders:
            items = order.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                if product_id:
                    if product_id not in product_sales:
                        product_sales[product_id] = {
                            'product_name': item.get('product_name', 'Unknown'),
                            'quantity': 0,
                            'revenue': 0
                        }
                    
                    product_sales[product_id]['quantity'] += item.get('quantity', 0)
                    product_sales[product_id]['revenue'] += item.get('price', 0) * item.get('quantity', 0)
        
        # Convert to list and sort
        top_products = [
            {
                "product_id": pid,
                "product_name": data['product_name'],
                "quantity_sold": data['quantity'],
                "revenue": round(data['revenue'], 2)
            }
            for pid, data in sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:limit]
        ]
        
        return {
            "status": "success",
            "data": top_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer-insights")
async def get_customer_insights():
    """Get customer behavior insights"""
    try:
        # Get orders
        orders = await db.orders.find({}).to_list(None)
        
        # Calculate metrics
        unique_customers = len(set(order.get('customer_id', 'unknown') for order in orders))
        total_orders = len(orders)
        total_revenue = sum(order.get('total_amount', 0) for order in orders)
        
        return {
            "status": "success",
            "data": {
                "total_customers": unique_customers,
                "repeat_rate": round((total_orders - unique_customers) / unique_customers * 100, 2) if unique_customers > 0 else 0,
                "lifetime_value": round(total_revenue / unique_customers, 2) if unique_customers > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer-signups")
async def get_customer_signups(days: int = 30):
    """Get customer signup statistics"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all customers/users
        users = await db.users.find({}).to_list(None)
        
        # Filter by date if created_at exists
        total_users = len(users)
        recent_signups = []
        signups_by_date = {}
        
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d')
                    except Exception:
                        date_str = created_at.split('T')[0] if 'T' in created_at else created_at.split()[0]
                else:
                    dt = created_at
                    date_str = dt.strftime('%Y-%m-%d')
                
                if date_str not in signups_by_date:
                    signups_by_date[date_str] = 0
                signups_by_date[date_str] += 1
                
                # Add to recent signups list (last 20)
                if len(recent_signups) < 20:
                    recent_signups.append({
                        "email": user.get('email', ''),
                        "name": user.get('name', user.get('full_name', '')),
                        "phone": user.get('phone', ''),
                        "created_at": created_at if isinstance(created_at, str) else created_at.isoformat() if created_at else None,
                        "source": user.get('source', 'website')
                    })
        
        # Sort recent signups by date (most recent first)
        recent_signups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Get signups trend
        signups_trend = [
            {"date": date, "count": count}
            for date, count in sorted(signups_by_date.items())
        ][-30:]  # Last 30 days
        
        return {
            "status": "success",
            "data": {
                "total_customers": total_users,
                "recent_signups": recent_signups[:10],
                "signups_trend": signups_trend,
                "signups_last_7_days": sum(1 for d, c in signups_by_date.items() 
                    if datetime.strptime(d, '%Y-%m-%d') > end_date - timedelta(days=7)),
                "signups_last_30_days": sum(1 for d, c in signups_by_date.items()
                    if datetime.strptime(d, '%Y-%m-%d') > end_date - timedelta(days=30))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/site-activity")
async def get_site_activity():
    """Get overall site activity metrics"""
    try:
        # Count various entities
        total_users = await db.users.count_documents({})
        total_admin_users = await db.admin_users.count_documents({})
        total_products = await db.products.count_documents({})
        total_orders = await db.offline_invoices.count_documents({"document_type": "invoice"})
        total_sales_orders = await db.offline_invoices.count_documents({"document_type": "sales_order"})
        total_service_requests = await db.service_requests.count_documents({})
        total_consultations = await db.consultations.count_documents({})
        
        # Get recent activity
        recent_invoices = await db.offline_invoices.find(
            {"document_type": "invoice"},
            {"_id": 0, "invoice_number": 1, "customer_name": 1, "total_amount": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(None)
        
        recent_service = await db.service_requests.find(
            {},
            {"_id": 0, "ticket_number": 1, "customer_name": 1, "product_name": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(None)
        
        return {
            "status": "success",
            "data": {
                "counts": {
                    "customers": total_users,
                    "admin_users": total_admin_users,
                    "products": total_products,
                    "invoices": total_orders,
                    "sales_orders": total_sales_orders,
                    "service_requests": total_service_requests,
                    "consultations": total_consultations
                },
                "recent_invoices": recent_invoices,
                "recent_service_requests": recent_service
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

