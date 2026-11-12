from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
from database import get_db
import csv
import io
from typing import Optional

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/sales/summary")
async def get_sales_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    database = Depends(get_db)
):
    """Get sales summary with date range"""
    try:
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now(timezone.utc).isoformat()
        if not start_date:
            start_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        
        # Aggregate sales data
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date},
                    "payment_status": "completed"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_orders": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"}
                }
            }
        ]
        
        cursor = database.orders.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        summary = result[0] if result else {
            "total_orders": 0,
            "total_revenue": 0,
            "avg_order_value": 0
        }
        
        # Remove MongoDB _id
        if "_id" in summary:
            del summary["_id"]
        
        return {
            "success": True,
            "data": {
                "period": {"start": start_date, "end": end_date},
                "total_orders": summary.get("total_orders", 0),
                "total_revenue": round(summary.get("total_revenue", 0), 2),
                "avg_order_value": round(summary.get("avg_order_value", 0), 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sales summary: {str(e)}")


@router.get("/export/orders")
async def export_orders_csv(
    database = Depends(get_db)
):
    """Export orders to CSV"""
    try:
        # Fetch all orders
        cursor = database.orders.find({}).sort("created_at", -1)
        orders = await cursor.to_list(length=1000)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order Number', 'Date', 'Customer Name', 'Customer Email', 
            'Items Count', 'Subtotal', 'Tax', 'Shipping', 'Total', 
            'Payment Status', 'Delivery Status'
        ])
        
        # Write data
        for order in orders:
            customer = order.get('customer_details', {})
            writer.writerow([
                order.get('order_number', ''),
                order.get('created_at', ''),
                customer.get('name', order.get('customer_name', '')),
                customer.get('email', order.get('customer_email', '')),
                len(order.get('items', [])),
                order.get('subtotal', 0),
                order.get('tax_amount', 0),
                order.get('shipping_cost', 0),
                order.get('total_amount', 0),
                order.get('payment_status', ''),
                order.get('delivery_status', '')
            ])
        
        # Prepare response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export orders: {str(e)}")


@router.get("/export/products")
async def export_products_csv(
    database = Depends(get_db)
):
    """Export products to CSV"""
    try:
        cursor = database.products.find({})
        products = await cursor.to_list(length=1000)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Product ID', 'Name', 'Category', 'Brand', 'Price', 
            'Original Price', 'Stock', 'SKU'
        ])
        
        for product in products:
            writer.writerow([
                product.get('id', ''),
                product.get('name', ''),
                product.get('category', ''),
                product.get('brand', ''),
                product.get('price', 0),
                product.get('original_price', 0),
                product.get('stock_quantity', 0),
                product.get('sku', '')
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=products_export.csv"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export products: {str(e)}")


@router.get("/export/customers")
async def export_customers_csv(
    database = Depends(get_db)
):
    """Export customers to CSV"""
    try:
        cursor = database.users.find({"role": "customer"})
        customers = await cursor.to_list(length=1000)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Customer ID', 'Name', 'Email', 'Created At'
        ])
        
        for customer in customers:
            writer.writerow([
                customer.get('id', customer.get('_id', '')),
                customer.get('name', ''),
                customer.get('email', ''),
                customer.get('created_at', '')
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=customers_export.csv"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export customers: {str(e)}")


@router.get("/product-performance")
async def get_product_performance(
    database = Depends(get_db)
):
    """Get top performing products"""
    try:
        # Aggregate orders to find top products
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": "$items.total"},
                    "order_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_revenue": -1}},
            {"$limit": 10}
        ]
        
        cursor = database.orders.aggregate(pipeline)
        products = await cursor.to_list(length=10)
        
        # Clean up
        for product in products:
            product["product_id"] = product.pop("_id")
        
        return {
            "success": True,
            "data": products
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product performance: {str(e)}")


@router.get("/daily-sales")
async def get_daily_sales(
    days: int = 30,
    database = Depends(get_db)
):
    """Get daily sales data for chart"""
    try:
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date},
                    "payment_status": "completed"
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$created_at", 0, 10]},
                    "orders": {"$sum": 1},
                    "revenue": {"$sum": "$total_amount"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        cursor = database.orders.aggregate(pipeline)
        daily_data = await cursor.to_list(length=days)
        
        result = []
        for item in daily_data:
            result.append({
                "date": item["_id"],
                "orders": item["orders"],
                "revenue": round(item["revenue"], 2)
            })
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily sales: {str(e)}")
