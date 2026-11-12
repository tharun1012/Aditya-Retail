# Complete API Routes for AI Ecommerce Platform
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from database import get_db
from auth_system import (
    User, get_current_active_user, require_admin, require_permissions,
    UserCreate, UserResponse, Token
)
import logging
from sqlalchemy import func
from ecommerce_models import (
    Product, Category, Order, OrderItem, Cart, CartItem,
    ProductReview, Inventory, ShippingRate, Coupon,
    Analytics, PincodeServiceability
)
from ecommerce_crud import (
    product_crud, category_crud, cart_crud, order_crud,
    coupon_crud, analytics_crud
)

logger = logging.getLogger(__name__)
from payment_integration import payment_service, PaymentCRUD
from shipping_integration import shipping_service, ShippingCRUD
from email_service import email_service, email_queue

# Product Management Routes
products_router = APIRouter(prefix="/products", tags=["Products"])

@products_router.get("/", response_model=List[Dict[str, Any]])
async def get_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category_id: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: bool = True,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(name|price|created_at|stock_quantity)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Get products with filtering and pagination"""
    products = product_crud.get_products(
        db=db, skip=skip, limit=limit, category_id=category_id,
        brand=brand, min_price=min_price, max_price=max_price,
        in_stock=in_stock, search=search, sort_by=sort_by, sort_order=sort_order
    )
    
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "sku": product.sku,
            "price": product.price,
            "original_price": product.original_price,
            "brand": product.brand,
            "category_id": product.category_id,
            "images": product.images or [],
            "features": product.features or [],
            "stock_quantity": product.stock_quantity,
            "is_featured": product.is_featured,
            "fast_moving": product.fast_moving,
            "created_at": product.created_at.isoformat()
        }
        result.append(product_dict)
    
    return result

@products_router.get("/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get single product by ID"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "short_description": product.short_description,
        "sku": product.sku,
        "price": product.price,
        "original_price": product.original_price,
        "brand": product.brand,
        "category_id": product.category_id,
        "images": product.images or [],
        "features": product.features or [],
        "specifications": product.specifications or {},
        "stock_quantity": product.stock_quantity,
        "weight": product.weight,
        "dimensions": product.dimensions or {},
        "is_featured": product.is_featured,
        "fast_moving": product.fast_moving,
        "seo_title": product.seo_title,
        "seo_description": product.seo_description,
        "created_at": product.created_at.isoformat()
    }

@products_router.post("/")
async def create_product(
    product_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create_products", "manage_products"]))
):
    """Create new product (Admin only)"""
    try:
        product = product_crud.create_product(db, product_data)
        return {"message": "Product created successfully", "product_id": product.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@products_router.put("/{product_id}")
async def update_product(
    product_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update_products", "manage_products"]))
):
    """Update product (Admin only)"""
    product = product_crud.update_product(db, product_id, update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@products_router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["delete_products", "manage_products"]))
):
    """Delete product (Admin only)"""
    if product_crud.delete_product(db, product_id):
        return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

# Category Management Routes
categories_router = APIRouter(prefix="/categories", tags=["Categories"])

@categories_router.get("/")
async def get_categories(
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """Get all categories"""
    categories = category_crud.get_categories(db, include_inactive)
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "image": cat.image,
            "is_active": cat.is_active,
            "created_at": cat.created_at.isoformat()
        }
        for cat in categories
    ]

@categories_router.post("/")
async def create_category(
    category_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new category (Admin only)"""
    category = category_crud.create_category(db, category_data)
    return {"message": "Category created successfully", "category_id": category.id}

# Cart Management Routes
cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.post("/add")
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Add item to cart"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    user_id = current_user.id if current_user else None
    cart = cart_crud.get_or_create_cart(db, user_id, session_id)
    
    # Check product exists and has stock
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cart_item = cart_crud.add_to_cart(db, cart.id, product_id, quantity)
    
    return {
        "message": "Item added to cart",
        "cart_id": cart.id,
        "session_id": session_id
    }

@cart_router.get("/{session_id}")
async def get_cart(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get cart contents"""
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        return {"items": [], "total": 0, "count": 0}
    
    cart_items = cart_crud.get_cart_items(db, cart.id)
    items = []
    total = 0
    
    for item in cart_items:
        product = product_crud.get_product_by_id(db, item.product_id)
        if product:
            item_total = product.price * item.quantity
            items.append({
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image": product.images[0] if product.images else None,
                    "stock_quantity": product.stock_quantity
                },
                "quantity": item.quantity,
                "item_total": item_total
            })
            total += item_total
    
    return {
        "items": items,
        "total": total,
        "count": len(items)
    }

@cart_router.delete("/{session_id}/item/{product_id}")
async def remove_from_cart(
    session_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if cart_crud.remove_from_cart(db, cart.id, product_id):
        return {"message": "Item removed from cart"}
    raise HTTPException(status_code=404, detail="Item not found in cart")

# Order Management Routes
orders_router = APIRouter(prefix="/orders", tags=["Orders"])

@orders_router.post("/")
async def create_order(
    order_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new order"""
    try:
        # Get cart items
        session_id = order_data.get("session_id")
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Prepare order items
        order_items = []
        total_weight = 0
        
        for cart_item in cart.items:
            product = product_crud.get_product_by_id(db, cart_item.product_id)
            if not product:
                continue
            
            if product.stock_quantity < cart_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for {product.name}"
                )
            
            order_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "unit_price": product.price,
                "quantity": cart_item.quantity
            })
            
            total_weight += (product.weight or 1.0) * cart_item.quantity
        
        # Calculate shipping
        pincode = order_data["shipping_address"]["pincode"]
        shipping_result = shipping_service.calculate_shipping_cost(pincode, total_weight)
        shipping_cost = shipping_result.get("shipping_cost", 0)
        
        # Prepare order
        order_create_data = {
            "customer_id": current_user.id,
            "billing_address": order_data["billing_address"],
            "shipping_address": order_data.get("shipping_address", order_data["billing_address"]),
            "customer_notes": order_data.get("customer_notes"),
            "shipping_cost": shipping_cost,
            "tax_amount": 0,  # Calculate based on business rules
            "discount_amount": 0
        }
        
        # Apply coupon if provided
        coupon_code = order_data.get("coupon_code")
        if coupon_code:
            subtotal = sum(item["unit_price"] * item["quantity"] for item in order_items)
            coupon_result = coupon_crud.validate_coupon(db, coupon_code, subtotal, current_user.id)
            if coupon_result["valid"]:
                order_create_data["discount_amount"] = coupon_result["discount_amount"]
        
        # Create order
        order = order_crud.create_order(db, order_create_data, order_items)
        
        # Process payment
        payment_method = order_data["payment_method"]
        user_details = {
            "phone": current_user.phone or "",
            "name": f"{current_user.first_name} {current_user.last_name}",
            "email": current_user.email
        }
        
        payment_result = payment_service.initiate_payment(
            db=db,
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            user_details=user_details
        )
        
        if payment_result["success"]:
            # Clear cart
            cart_crud.clear_cart(db, cart.id)
            
            # Send order confirmation email
            email_data = {
                "customer_email": current_user.email,
                "order_number": order.order_number,
                "order_date": order.created_at.strftime("%d %b %Y"),
                "payment_method": payment_method.title(),
                "estimated_delivery": "5-7 business days",
                "items": order_items,
                "subtotal": order.subtotal,
                "shipping_cost": order.shipping_cost,
                "tax_amount": order.tax_amount,
                "total_amount": order.total_amount,
                "tracking_url": f"http://localhost:3000/orders/{order.order_number}"
            }
            
            await email_queue.add_notification({
                "type": "order_confirmation",
                "data": email_data
            })
            
            # Create shipment if payment is successful (for COD) or after payment verification (for PhonePe)
            if payment_method == "cod":
                shipment_data = {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "order_date": order.created_at.strftime("%Y-%m-%d"),
                    "customer_name": f"{current_user.first_name} {current_user.last_name}",
                    "customer_email": current_user.email,
                    "customer_phone": current_user.phone,
                    "billing_address": order.billing_address,
                    "shipping_address": order.shipping_address,
                    "items": order_items,
                    "subtotal": order.subtotal,
                    "payment_method": payment_method,
                    "weight": total_weight
                }
                
                shipping_result = shipping_service.create_shipment(db, shipment_data)
            
            return {
                "success": True,
                "order_id": order.id,
                "order_number": order.order_number,
                "payment": payment_result
            }
        else:
            # Delete order if payment initiation failed
            db.delete(order)
            db.commit()
            raise HTTPException(status_code=400, detail=payment_result.get("error", "Payment failed"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@orders_router.get("/")
async def get_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's orders"""
    orders = order_crud.get_user_orders(db, current_user.id, skip, limit)
    
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat(),
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            "items_count": len(order.order_items)
        })
    
    return result

@orders_router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order details"""
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order or is admin
    if order.customer_id != current_user.id and not any(role.name in ["admin", "super_admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get tracking info
    tracking = ShippingCRUD.get_shipment_by_order_id(db, order_id)
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "billing_address": order.billing_address,
        "shipping_address": order.shipping_address,
        "subtotal": order.subtotal,
        "tax_amount": order.tax_amount,
        "shipping_cost": order.shipping_cost,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_name": item.product_name,
                "product_sku": item.product_sku,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "total_price": item.total_price
            }
            for item in order.order_items
        ],
        "tracking": {
            "awb_number": tracking.awb_number if tracking else None,
            "courier_name": tracking.courier_name if tracking else None,
            "current_status": tracking.current_status if tracking else "Order Placed",
            "tracking_url": tracking.tracking_url if tracking else None
        } if tracking else None
    }

# Payment Routes
payments_router = APIRouter(prefix="/payments", tags=["Payments"])

@payments_router.post("/phonepe/callback")
async def phonepe_callback(
    callback_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle PhonePe payment callback"""
    try:
        # Extract transaction ID from callback
        transaction_id = callback_data.get("transactionId")
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Transaction ID missing")
        
        # Verify payment with PhonePe
        verification_result = payment_service.verify_payment(db, transaction_id)
        
        if verification_result["success"] and verification_result["status"] == "success":
            # Update order status
            payment = PaymentCRUD.get_payment_by_transaction_id(db, transaction_id)
            if payment:
                order = order_crud.get_order_by_id(db, payment.order_id)
                if order:
                    order_crud.update_order_status(db, order.id, "confirmed")
                    
                    # Create shipment
                    # Implementation similar to COD order creation
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Payment callback error: {str(e)}")
        return {"status": "error", "message": str(e)}

# Shipping Routes  
shipping_router = APIRouter(prefix="/shipping", tags=["Shipping"])

@shipping_router.post("/check")
async def check_shipping(
    pincode: str,
    weight: float = 1.0,
    db: Session = Depends(get_db)
):
    """Check shipping availability and cost"""
    result = shipping_service.calculate_shipping_cost(pincode, weight)
    return result

@shipping_router.get("/track/{order_id}")
async def track_shipment(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Track shipment by order ID"""
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.customer_id != current_user.id and not any(role.name in ["admin", "super_admin"] for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Access denied")
    
    tracking_result = shipping_service.track_shipment(db, order_id)
    return tracking_result

# Admin Analytics Routes
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

@analytics_router.get("/sales")
async def get_sales_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["view_analytics"]))
):
    """Get sales analytics (Admin only)"""
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    analytics = analytics_crud.get_sales_analytics(db, start_dt, end_dt)
    return analytics

@analytics_router.get("/inventory")
async def get_inventory_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["view_analytics", "manage_inventory"]))
):
    """Get inventory analytics (Admin only)"""
    analytics = analytics_crud.get_inventory_analytics(db)
    return analytics

@analytics_router.get("/dashboard")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get dashboard summary (Admin only)"""
    
    # Get recent stats
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order stats
    total_orders = db.query(Order).count()
    weekly_orders = db.query(Order).filter(Order.created_at >= week_ago).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    
    # Revenue stats  
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.payment_status == "paid").scalar() or 0
    monthly_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid",
        Order.created_at >= month_ago
    ).scalar() or 0
    
    # Product stats
    total_products = db.query(Product).filter(Product.is_active == True).count()
    low_stock_products = len(product_crud.get_low_stock_products(db))
    
    return {
        "orders": {
            "total": total_orders,
            "weekly": weekly_orders,
            "pending": pending_orders
        },
        "revenue": {
            "total": float(total_revenue),
            "monthly": float(monthly_revenue)
        },
        "products": {
            "total": total_products,
            "low_stock": low_stock_products
        },
        "alerts": {
            "low_stock_items": low_stock_products,
            "pending_orders": pending_orders
        }
    }