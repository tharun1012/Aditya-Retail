from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Order Status Enum
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"

# Payment Status Enum
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Payment Method Enum
class PaymentMethod(str, Enum):
    COD = "cod"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"

# Order Item Model
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    model_number: str
    quantity: int
    price: float
    discount: float = 0
    tax: float = 0
    total: float

# Shipping Address Model
class ShippingAddress(BaseModel):
    name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"

# Order Timeline Event
class OrderTimelineEvent(BaseModel):
    status: OrderStatus
    timestamp: str
    message: str
    updated_by: Optional[str] = "system"

# Order Model
class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    
    # Order Items
    items: List[OrderItem]
    
    # Pricing
    subtotal: float
    tax_amount: float
    shipping_charges: float
    discount_amount: float = 0
    total_amount: float
    
    # Payment
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_id: Optional[str] = None
    payment_timestamp: Optional[str] = None
    
    # Shipping
    shipping_address: ShippingAddress
    billing_address: Optional[ShippingAddress] = None
    
    # Delivery
    tracking_number: Optional[str] = None
    delivery_partner: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    delivered_date: Optional[str] = None
    
    # Status
    order_status: OrderStatus = OrderStatus.PENDING
    timeline: List[OrderTimelineEvent] = []
    
    # Notes
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    
    # Timestamps
    created_at: str
    updated_at: str
    
    class Config:
        use_enum_values = True

# Analytics Models
class SalesMetrics(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    conversion_rate: float
    
class DailySales(BaseModel):
    date: str
    revenue: float
    orders: int
    
class CategoryPerformance(BaseModel):
    category: str
    revenue: float
    orders: int
    units_sold: int
    
class ProductPerformance(BaseModel):
    product_id: str
    product_name: str
    model_number: str
    units_sold: int
    revenue: float
    rating: float
    
# AI Agent Performance Models
class AgentMetrics(BaseModel):
    agent_name: str
    total_interactions: int
    successful_interactions: int
    success_rate: float
    average_response_time: float
    customer_satisfaction: float
    revenue_attributed: float = 0

class ConversationLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str  # sales, service, marketing, delivery, stock
    customer_id: Optional[str] = None
    timestamp: str
    duration: float  # in seconds
    messages_count: int
    outcome: str  # converted, resolved, escalated, abandoned
    satisfaction_score: Optional[float] = None
    tags: List[str] = []

# Marketing Campaign Model
class Campaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # email, sms, banner, social
    status: str  # draft, scheduled, active, completed, cancelled
    
    # Targeting
    target_audience: str
    customer_segment: Optional[str] = None
    
    # Content
    subject: Optional[str] = None
    message: str
    banner_image: Optional[str] = None
    
    # Schedule
    start_date: str
    end_date: Optional[str] = None
    
    # Metrics
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    converted_count: int = 0
    revenue_generated: float = 0
    
    # Meta
    created_by: str
    created_at: str
    updated_at: str

# Inventory Alert Model
class InventoryAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    model_number: str
    alert_type: str  # low_stock, out_of_stock, overstock
    current_stock: int
    threshold: int
    priority: str  # low, medium, high, critical
    is_resolved: bool = False
    created_at: str
    resolved_at: Optional[str] = None

import uuid
