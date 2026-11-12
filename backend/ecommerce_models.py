# Complete Ecommerce Models for AI Platform
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    image = Column(String(500))
    is_active = Column(Boolean, default=True)
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id])

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    sku = Column(String(100), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    cost_price = Column(Float)
    brand = Column(String(100), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    images = Column(JSON)  # Store array of image URLs
    features = Column(JSON)  # Store array of features
    specifications = Column(JSON)  # Store product specifications
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    weight = Column(Float)  # For shipping calculations
    dimensions = Column(JSON)  # {"length": 10, "width": 20, "height": 30}
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    fast_moving = Column(Boolean, default=False)
    seo_title = Column(String(200))
    seo_description = Column(Text)
    meta_keywords = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Customer Information
    billing_address = Column(JSON)  # Full billing address
    shipping_address = Column(JSON)  # Full shipping address
    customer_notes = Column(Text)
    
    # Order Totals
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    shipping_cost = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String(50), default="pending")  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String(50))  # phonepe, cod, etc.
    payment_transaction_id = Column(String(200))
    
    # Shipping
    shipping_method = Column(String(100))
    tracking_number = Column(String(200))
    estimated_delivery = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    order_history = relationship("OrderStatusHistory", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)  # Store name at time of order
    product_sku = Column(String(100), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    status = Column(String(50), nullable=False)
    notes = Column(Text)
    created_by = Column(String(100))  # system, admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_history")

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(200), nullable=False)  # For guest carts
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

class ProductReview(Base):
    __tablename__ = "product_reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200))
    review_text = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="reviews")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    current_stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)  # Items in pending orders
    available_stock = Column(Integer, default=0)  # current - reserved
    reorder_point = Column(Integer, default=10)
    max_stock_level = Column(Integer, default=100)
    last_restocked = Column(DateTime)
    supplier_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShippingRate(Base):
    __tablename__ = "shipping_rates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pincode_start = Column(String(10), nullable=False)
    pincode_end = Column(String(10), nullable=False)
    zone = Column(String(50))  # metro, urban, rural
    base_rate = Column(Float, nullable=False)
    per_kg_rate = Column(Float, default=0)
    cod_charges = Column(Float, default=0)
    estimated_days = Column(Integer, default=7)
    is_serviceable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    discount_type = Column(String(20), nullable=False)  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    minimum_amount = Column(Float, default=0)
    maximum_discount = Column(Float)
    usage_limit = Column(Integer)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    applicable_categories = Column(JSON)  # List of category IDs
    applicable_products = Column(JSON)  # List of product IDs
    created_at = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    dimensions = Column(JSON)  # Additional context data
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailNotification(Base):
    __tablename__ = "email_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    to_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body_text = Column(Text)
    body_html = Column(Text)
    notification_type = Column(String(100))  # order_confirmation, shipping_update, etc.
    status = Column(String(50), default="pending")  # pending, sent, failed
    error_message = Column(Text)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class PincodeServiceability(Base):
    __tablename__ = "pincode_serviceability"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pincode = Column(String(10), nullable=False, unique=True)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    is_serviceable = Column(Boolean, default=True)
    cod_available = Column(Boolean, default=True)
    estimated_delivery_days = Column(Integer, default=7)
    zone_type = Column(String(50))  # metro, tier1, tier2, rural
    shiprocket_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)