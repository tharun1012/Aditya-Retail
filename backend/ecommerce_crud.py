# Complete CRUD Operations for AI Ecommerce Platform
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException
import uuid

from ecommerce_models import (
    Product, Category, Order, OrderItem, Cart, CartItem, 
    ProductReview, Inventory, ShippingRate, Coupon, 
    Analytics, PincodeServiceability
)
from auth_system import User

class ProductCRUD:
    @staticmethod
    def create_product(db: Session, product_data: Dict[str, Any]) -> Product:
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create inventory record
        inventory = Inventory(
            product_id=product.id,
            current_stock=product.stock_quantity,
            available_stock=product.stock_quantity,
            reorder_point=product.reorder_level
        )
        db.add(inventory)
        db.commit()
        
        return product
    
    @staticmethod
    def get_products(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = True,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Product]:
        query = db.query(Product).filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        
        if min_price:
            query = query.filter(Product.price >= min_price)
        
        if max_price:
            query = query.filter(Product.price <= max_price)
        
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.brand.ilike(f"%{search}%")
                )
            )
        
        # Sorting
        if sort_order == "desc":
            query = query.order_by(desc(getattr(Product, sort_by)))
        else:
            query = query.order_by(asc(getattr(Product, sort_by)))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def update_product(db: Session, product_id: str, update_data: Dict[str, Any]) -> Optional[Product]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        for key, value in update_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        
        # Update inventory if stock changed
        if 'stock_quantity' in update_data:
            inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
            if inventory:
                inventory.current_stock = update_data['stock_quantity']
                inventory.available_stock = update_data['stock_quantity'] - inventory.reserved_stock
                inventory.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: str) -> bool:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        product.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_low_stock_products(db: Session, threshold: int = None) -> List[Product]:
        query = db.query(Product).join(Inventory)
        if threshold:
            query = query.filter(Inventory.current_stock <= threshold)
        else:
            query = query.filter(Inventory.current_stock <= Product.reorder_level)
        
        return query.filter(Product.is_active == True).all()

class CategoryCRUD:
    @staticmethod
    def create_category(db: Session, category_data: Dict[str, Any]) -> Category:
        category = Category(**category_data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def get_categories(db: Session, include_inactive: bool = False) -> List[Category]:
        query = db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.all()
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: str) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

class CartCRUD:
    @staticmethod
    def get_or_create_cart(db: Session, user_id: Optional[str], session_id: str) -> Cart:
        cart = db.query(Cart).filter(
            or_(Cart.user_id == user_id, Cart.session_id == session_id)
        ).first()
        
        if not cart:
            cart = Cart(user_id=user_id, session_id=session_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
    
    @staticmethod
    def add_to_cart(db: Session, cart_id: str, product_id: str, quantity: int = 1) -> CartItem:
        # Check if item already exists
        existing_item = db.query(CartItem).filter(
            and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.added_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def remove_from_cart(db: Session, cart_id: str, product_id: str) -> bool:
        cart_item = db.query(CartItem).filter(
            and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        ).first()
        
        if cart_item:
            db.delete(cart_item)
            db.commit()
            return True
        return False
    
    @staticmethod
    def update_cart_item_quantity(db: Session, cart_id: str, product_id: str, quantity: int) -> Optional[CartItem]:
        cart_item = db.query(CartItem).filter(
            and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        ).first()
        
        if cart_item:
            if quantity <= 0:
                db.delete(cart_item)
                db.commit()
                return None
            else:
                cart_item.quantity = quantity
                db.commit()
                db.refresh(cart_item)
                return cart_item
        return None
    
    @staticmethod
    def get_cart_items(db: Session, cart_id: str) -> List[CartItem]:
        return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    
    @staticmethod
    def clear_cart(db: Session, cart_id: str) -> bool:
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.commit()
        return True

class OrderCRUD:
    @staticmethod
    def create_order(db: Session, order_data: Dict[str, Any], order_items: List[Dict[str, Any]]) -> Order:
        # Generate order number
        order_count = db.query(Order).count()
        order_number = f"AD{datetime.now().strftime('%Y%m%d')}{order_count + 1:04d}"
        
        order_data['order_number'] = order_number
        order = Order(**order_data)
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        total_amount = 0
        for item_data in order_items:
            item_data['order_id'] = order.id
            item_data['total_price'] = item_data['unit_price'] * item_data['quantity']
            total_amount += item_data['total_price']
            
            order_item = OrderItem(**item_data)
            db.add(order_item)
            
            # Update inventory
            inventory = db.query(Inventory).filter(Inventory.product_id == item_data['product_id']).first()
            if inventory:
                inventory.reserved_stock += item_data['quantity']
                inventory.available_stock = inventory.current_stock - inventory.reserved_stock
        
        # Update order total
        order.subtotal = total_amount
        order.total_amount = total_amount + order.tax_amount + order.shipping_cost - order.discount_amount
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def get_user_orders(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.customer_id == user_id).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_order_status(db: Session, order_id: str, status: str, notes: Optional[str] = None) -> Optional[Order]:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        old_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # Handle status-specific updates
        if status == "shipped" and old_status != "shipped":
            order.shipped_at = datetime.utcnow()
        elif status == "delivered" and old_status != "delivered":
            order.delivered_at = datetime.utcnow()
            # Release reserved inventory
            for item in order.order_items:
                inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
                if inventory:
                    inventory.current_stock -= item.quantity
                    inventory.reserved_stock -= item.quantity
                    inventory.available_stock = inventory.current_stock - inventory.reserved_stock
        elif status == "cancelled":
            # Release reserved inventory
            for item in order.order_items:
                inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
                if inventory:
                    inventory.reserved_stock -= item.quantity
                    inventory.available_stock = inventory.current_stock - inventory.reserved_stock
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_orders_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.status == status).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

class ShippingCRUD:
    @staticmethod
    def check_pincode_serviceability(db: Session, pincode: str) -> Optional[PincodeServiceability]:
        return db.query(PincodeServiceability).filter(PincodeServiceability.pincode == pincode).first()
    
    @staticmethod
    def calculate_shipping_cost(db: Session, pincode: str, weight: float) -> Dict[str, Any]:
        serviceability = db.query(PincodeServiceability).filter(PincodeServiceability.pincode == pincode).first()
        
        if not serviceability or not serviceability.is_serviceable:
            return {
                "serviceable": False,
                "cost": 0,
                "estimated_days": 0,
                "cod_available": False
            }
        
        # Simple shipping calculation (can integrate with Shiprocket API)
        base_cost = 50  # Base shipping cost
        per_kg_cost = 20
        total_cost = base_cost + (weight * per_kg_cost)
        
        # Free shipping above certain amount
        if total_cost > 500:  # If order value > 500, free shipping
            total_cost = 0
        
        return {
            "serviceable": True,
            "cost": total_cost,
            "estimated_days": serviceability.estimated_delivery_days,
            "cod_available": serviceability.cod_available,
            "zone": serviceability.zone_type
        }

class CouponCRUD:
    @staticmethod
    def validate_coupon(db: Session, coupon_code: str, order_total: float, user_id: Optional[str] = None) -> Dict[str, Any]:
        coupon = db.query(Coupon).filter(
            and_(
                Coupon.code == coupon_code,
                Coupon.is_active == True,
                Coupon.valid_from <= datetime.utcnow(),
                Coupon.valid_until >= datetime.utcnow()
            )
        ).first()
        
        if not coupon:
            return {"valid": False, "message": "Invalid or expired coupon"}
        
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return {"valid": False, "message": "Coupon usage limit exceeded"}
        
        if order_total < coupon.minimum_amount:
            return {"valid": False, "message": f"Minimum order amount ₹{coupon.minimum_amount} required"}
        
        # Calculate discount
        if coupon.discount_type == "percentage":
            discount_amount = (order_total * coupon.discount_value) / 100
        else:  # fixed
            discount_amount = coupon.discount_value
        
        # Apply maximum discount limit
        if coupon.maximum_discount:
            discount_amount = min(discount_amount, coupon.maximum_discount)
        
        return {
            "valid": True,
            "discount_amount": discount_amount,
            "coupon_id": coupon.id,
            "message": f"Coupon applied! You saved ₹{discount_amount}"
        }

class AnalyticsCRUD:
    @staticmethod
    def track_metric(db: Session, metric_name: str, value: float, dimensions: Dict[str, Any] = None):
        analytics = Analytics(
            metric_name=metric_name,
            metric_value=value,
            dimensions=dimensions
        )
        db.add(analytics)
        db.commit()
    
    @staticmethod
    def get_sales_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        # Total orders and revenue
        orders_query = db.query(Order).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        )
        
        total_orders = orders_query.count()
        total_revenue = orders_query.with_entities(func.sum(Order.total_amount)).scalar() or 0
        
        # Orders by status
        orders_by_status = db.query(Order.status, func.count(Order.id)).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        ).group_by(Order.status).all()
        
        # Top selling products
        top_products = db.query(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(Order).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        ).group_by(OrderItem.product_name).order_by(desc('total_sold')).limit(10).all()
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0,
            "orders_by_status": dict(orders_by_status),
            "top_products": [
                {
                    "name": product[0],
                    "quantity_sold": product[1],
                    "revenue": float(product[2])
                }
                for product in top_products
            ]
        }
    
    @staticmethod
    def get_inventory_analytics(db: Session) -> Dict[str, Any]:
        # Low stock products
        low_stock = db.query(Product).join(Inventory).filter(
            Inventory.current_stock <= Product.reorder_level
        ).count()
        
        # Out of stock products
        out_of_stock = db.query(Product).join(Inventory).filter(
            Inventory.current_stock <= 0
        ).count()
        
        # Total inventory value
        inventory_value = db.query(
            func.sum(Product.cost_price * Inventory.current_stock)
        ).join(Inventory).scalar() or 0
        
        return {
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "total_inventory_value": float(inventory_value),
            "total_products": db.query(Product).filter(Product.is_active == True).count()
        }

# Initialize CRUD instances
product_crud = ProductCRUD()
category_crud = CategoryCRUD()
cart_crud = CartCRUD()
order_crud = OrderCRUD()
shipping_crud = ShippingCRUD()
coupon_crud = CouponCRUD()
analytics_crud = AnalyticsCRUD()