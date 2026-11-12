from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# Authentication Models for Emergent Auth
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "customer"  # customer, admin, manager
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class UserSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# Product Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    price: float
    original_price: Optional[float] = None
    image: str
    brand: str
    description: str
    features: List[str] = []
    stock: int = 0
    fast_moving: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    original_price: Optional[float] = None
    image: str
    brand: str
    description: str
    features: List[str] = []
    stock: int = 0
    fast_moving: bool = False

# Cart Models
class CartItem(BaseModel):
    product_id: str
    quantity: int = 1
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# AI Chat Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    agent_type: str  # sales, service, stock, marketing, delivery
    sender: str  # user, ai
    message: str
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str
    agent_type: str
    status: str = "active"  # active, closed
    context: Dict[str, Any] = {}
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    session_id: str
    agent_type: str
    message: str
    context: Optional[Dict[str, Any]] = None

# Service Request Models
class ServiceRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(default_factory=lambda: f"SR{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6]}")
    customer_name: str
    customer_email: str
    customer_phone: str
    product_name: str
    issue_description: str
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "open"  # open, assigned, in_progress, resolved, closed
    assigned_technician: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceRequestCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    product_name: str
    issue_description: str
    priority: str = "medium"

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    total: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = Field(default_factory=lambda: f"AD{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6]}")
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    items: List[OrderItem]
    subtotal: float
    tax: float
    total: float
    status: str = "pending"  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status: str = "pending"  # pending, paid, failed, refunded
    delivery_status: str = "pending"  # pending, scheduled, in_transit, delivered
    delivery_date: Optional[datetime] = None
    tracking_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    items: List[OrderItem]

# Analytics Models
class ProductAnalytics(BaseModel):
    product_id: str
    views: int = 0
    add_to_cart: int = 0
    purchases: int = 0
    revenue: float = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class InventoryAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    current_stock: int
    reorder_level: int
    suggested_reorder_qty: int
    priority: str = "medium"  # low, medium, high
    status: str = "active"  # active, acknowledged, resolved
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Marketing Models
class MarketingCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # email, sms, push, banner
    target_audience: str
    message: str
    discount_percentage: Optional[float] = None
    start_date: datetime
    end_date: datetime
    status: str = "draft"  # draft, active, paused, completed
    metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerBehavior(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    actions: List[Dict[str, Any]] = []  # page_views, clicks, searches, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Status Check Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str
    status: str = "healthy"  # healthy, degraded, down
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    service_name: str
    status: str = "healthy"
    response_time: Optional[float] = None
    error_message: Optional[str] = None