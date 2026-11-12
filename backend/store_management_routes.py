"""
Multi-Store Management Routes
Handles store creation, store users, and store-level access control
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from database import get_db
from pydantic import BaseModel, EmailStr
import uuid
import hashlib

router = APIRouter(prefix="/stores", tags=["Store Management"])

# ============ MODELS ============

class StoreCreate(BaseModel):
    name: str
    code: str  # Unique store code like "ST001", "BLR01"
    address: str
    city: str
    state: str
    pincode: str
    phone: str
    email: Optional[str] = None
    manager_name: Optional[str] = None
    is_warehouse: bool = False  # True if this is a warehouse, not a retail store
    # Document-related fields
    gst_number: Optional[str] = None  # GSTIN for tax invoices
    pan_number: Optional[str] = None  # PAN for documents
    tagline: Optional[str] = None  # Company tagline
    invoice_prefix: Optional[str] = None  # Custom prefix for invoices
    so_prefix: Optional[str] = None  # Custom prefix for sales orders

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_warehouse: Optional[bool] = None
    # Document-related fields
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    tagline: Optional[str] = None
    invoice_prefix: Optional[str] = None
    so_prefix: Optional[str] = None

class StoreUserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "store_manager"  # store_manager, store_staff, store_accountant, or custom role ID
    permissions: Optional[Dict[str, List[str]]] = None  # Custom permissions override

class StoreUserLogin(BaseModel):
    email: EmailStr
    password: str

class StorePermissions(BaseModel):
    can_create_sales: bool = True
    can_create_purchases: bool = True
    can_create_expenses: bool = True
    can_view_reports: bool = True
    can_manage_stock: bool = True
    can_create_challans: bool = True
    can_view_other_stores: bool = False
    can_transfer_stock: bool = True

# ============ STORE CRUD ============

@router.post("/")
async def create_store(store: StoreCreate, db = Depends(get_db)):
    """Create a new store"""
    try:
        # Check if store code already exists
        existing = await db.stores.find_one({"code": store.code.upper()})
        if existing:
            raise HTTPException(status_code=400, detail=f"Store with code {store.code} already exists")
        
        store_id = str(uuid.uuid4())
        store_data = {
            "id": store_id,
            "code": store.code.upper(),
            "name": store.name,
            "address": store.address,
            "city": store.city,
            "state": store.state,
            "pincode": store.pincode,
            "phone": store.phone,
            "email": store.email,
            "manager_name": store.manager_name,
            "is_warehouse": store.is_warehouse,
            "is_active": True,
            # Document-related fields with sensible defaults
            "gst_number": store.gst_number or "",
            "pan_number": store.pan_number or "",
            "tagline": store.tagline or "",
            "invoice_prefix": store.invoice_prefix or f"{store.code.upper()}-INV",
            "so_prefix": store.so_prefix or f"{store.code.upper()}-SO",
            "permissions": StorePermissions().dict(),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.stores.insert_one(store_data)
        
        # Initialize store inventory
        await db.store_inventory.insert_one({
            "store_id": store_id,
            "store_code": store.code.upper(),
            "products": {},  # product_id: quantity
            "last_updated": datetime.now(timezone.utc)
        })
        
        return {
            "status": "success",
            "message": f"Store {store.name} created successfully",
            "store_id": store_id,
            "store_code": store.code.upper()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_stores(
    include_inactive: bool = False,
    db = Depends(get_db)
):
    """List all stores"""
    try:
        query = {} if include_inactive else {"is_active": True}
        stores = await db.stores.find(query, {"_id": 0}).sort("code", 1).to_list(None)
        
        # Get inventory summary and user count for each store
        for store in stores:
            inventory = await db.store_inventory.find_one(
                {"store_id": store["id"]},
                {"_id": 0, "products": 1}
            )
            if inventory:
                store["total_products"] = len(inventory.get("products", {}))
                store["total_stock"] = sum(inventory.get("products", {}).values())
            else:
                store["total_products"] = 0
                store["total_stock"] = 0
            
            # Get user count for this store
            user_count = await db.store_users.count_documents({"store_id": store["id"]})
            store["user_count"] = user_count
        
        return {
            "status": "success",
            "stores": stores,
            "count": len(stores)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}")
async def get_store(store_id: str, db = Depends(get_db)):
    """Get store details"""
    try:
        store = await db.stores.find_one({"id": store_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get store users
        users = await db.store_users.find(
            {"store_id": store_id},
            {"_id": 0, "password_hash": 0}
        ).to_list(None)
        store["users"] = users
        
        # Get inventory
        inventory = await db.store_inventory.find_one(
            {"store_id": store_id},
            {"_id": 0}
        )
        store["inventory_summary"] = {
            "total_products": len(inventory.get("products", {})) if inventory else 0,
            "total_stock": sum(inventory.get("products", {}).values()) if inventory else 0
        }
        
        return {
            "status": "success",
            "store": store
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{store_id}")
async def update_store(store_id: str, update: dict, db = Depends(get_db)):
    """Update store details including module permissions"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Handle module_permissions separately if provided
        module_permissions = update.pop("module_permissions", None)
        
        # Build update data from remaining fields
        update_data = {k: v for k, v in update.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Add module_permissions if provided
        if module_permissions is not None:
            update_data["module_permissions"] = module_permissions
        
        await db.stores.update_one(
            {"id": store_id},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": "Store updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{store_id}")
async def delete_store(store_id: str, db = Depends(get_db)):
    """Delete a store and all its associated users"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        store_name = store.get("name", "Unknown")
        
        # Delete all users associated with this store
        deleted_users = await db.store_users.delete_many({"store_id": store_id})
        
        # Delete the document numbering config for this store
        await db.document_numbering.delete_one({"store_id": store_id})
        
        # Delete the store
        await db.stores.delete_one({"id": store_id})
        
        return {
            "status": "success",
            "message": f"Store '{store_name}' deleted successfully",
            "deleted_users_count": deleted_users.deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{store_id}/permissions")
async def update_store_permissions(
    store_id: str,
    permissions: StorePermissions,
    db = Depends(get_db)
):
    """Update store permissions (Admin only)"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        await db.stores.update_one(
            {"id": store_id},
            {"$set": {
                "permissions": permissions.dict(),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "status": "success",
            "message": "Store permissions updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STORE USER MANAGEMENT ============

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/{store_id}/users")
async def create_store_user(
    store_id: str,
    user_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a user for a specific store with role and custom permissions"""
    try:
        # Verify store exists
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        email = (user_data.get("email") or "").lower().strip() or None
        username = (user_data.get("username") or "").lower().strip() or None
        phone = (user_data.get("phone") or "").strip() or None
        name = user_data.get("first_name", "") + " " + user_data.get("last_name", "")
        name = name.strip() or user_data.get("name", "")
        
        # Must have at least one identifier
        if not email and not username and not phone:
            raise HTTPException(
                status_code=400, 
                detail="At least one of email, username, or phone is required"
            )
        
        # Generate username if not provided
        if not username:
            if email:
                username = email.split('@')[0]
            elif name:
                username = name.lower().replace(' ', '_')
            else:
                username = f"user_{store['code'].lower()}_{str(uuid.uuid4())[:6]}"
        
        # Check for existing user with same identifiers
        existing_query = {"$or": [{"username": username}]}
        if email:
            existing_query["$or"].append({"email": email})
        if phone:
            existing_query["$or"].append({"phone": phone})
        
        existing = await db.store_users.find_one(existing_query)
        if existing:
            conflict = []
            if email and existing.get("email") == email:
                conflict.append("email")
            if existing.get("username") == username:
                conflict.append("username")
            if phone and existing.get("phone") == phone:
                conflict.append("phone")
            raise HTTPException(
                status_code=400, 
                detail=f"User with this {'/'.join(conflict)} already exists"
            )
        
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "store_id": store_id,
            "store_code": store["code"],
            "store_name": store["name"],
            "username": username,
            "email": email,
            "phone": phone,
            "password_hash": hash_password(user_data.get("password", "")),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "name": name,
            "role": user_data.get("role", "sales_staff"),
            "permissions": user_data.get("permissions", {}),  # Custom permissions
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        await db.store_users.insert_one(new_user)
        
        login_info = username
        if email:
            login_info = f"{email} or {username}"
        elif phone:
            login_info = f"{username} or {phone}"
        
        return {
            "status": "success",
            "message": f"User created for store {store['name']}. Login with: {login_info}",
            "user_id": user_id,
            "username": username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_id}/users")
async def get_store_users(store_id: str, db = Depends(get_db)):
    """Get all users for a specific store"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        users = await db.store_users.find(
            {"store_id": store_id},
            {"_id": 0, "password_hash": 0}
        ).to_list(None)
        
        return {
            "status": "success",
            "users": users or []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{store_id}/users/{user_id}")
async def update_store_user(
    store_id: str,
    user_id: str,
    update_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Update a store user"""
    try:
        user = await db.store_users.find_one({"id": user_id, "store_id": store_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_fields = {"updated_at": datetime.now(timezone.utc)}
        
        # Allowed fields to update
        allowed_fields = ["first_name", "last_name", "phone", "role", "permissions", "is_active"]
        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                update_fields[field] = update_data[field]
        
        # Handle password update separately
        if "password" in update_data and update_data["password"]:
            update_fields["password_hash"] = hash_password(update_data["password"])
        
        await db.store_users.update_one(
            {"id": user_id},
            {"$set": update_fields}
        )
        
        return {
            "status": "success",
            "message": "User updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{store_id}/users/{user_id}")
async def delete_store_user(store_id: str, user_id: str, db = Depends(get_db)):
    """Delete a store user"""
    try:
        result = await db.store_users.delete_one({"id": user_id, "store_id": store_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "status": "success",
            "message": "User deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/login")
async def store_user_login(credentials: StoreUserLogin, db = Depends(get_db)):
    """Store user login"""
    try:
        user = await db.store_users.find_one({
            "email": credentials.email.lower(),
            "is_active": True
        })
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user["password_hash"] != hash_password(credentials.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get store details
        store = await db.stores.find_one({"id": user["store_id"]}, {"_id": 0})
        
        # Update last login
        await db.store_users.update_one(
            {"id": user["id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Generate simple token (in production, use JWT)
        token = str(uuid.uuid4())
        await db.store_sessions.update_one(
            {"user_id": user["id"]},
            {"$set": {
                "token": token,
                "store_id": user["store_id"],
                "created_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
        
        # Ensure module_permissions exists (for unified dashboard)
        module_permissions = store.get("module_permissions", {}) if store else {}
        
        return {
            "status": "success",
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "role": user["role"],
                "store_id": user["store_id"],
                "store_code": user["store_code"],
                "store_name": user["store_name"]
            },
            "store": store,
            "module_permissions": module_permissions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}/users")
async def list_store_users(store_id: str, db = Depends(get_db)):
    """List all users for a store"""
    try:
        users = await db.store_users.find(
            {"store_id": store_id},
            {"_id": 0, "password_hash": 0}
        ).to_list(None)
        
        return {
            "status": "success",
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ STORE DASHBOARD DATA ============

@router.get("/{store_id}/dashboard")
async def get_store_dashboard(
    store_id: str,
    period: str = "today",  # today, week, month, year
    db = Depends(get_db)
):
    """Get store dashboard summary"""
    try:
        store = await db.stores.find_one({"id": store_id})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get date range
        now = datetime.now(timezone.utc)
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            from datetime import timedelta
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Sales summary — online orders (db.orders)
        sales_pipeline = [
            {"$match": {
                "store_id": store_id,
                "created_at": {"$gte": start_date},
                "payment_status": {"$in": ["completed", "paid"]}
            }},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": "$total_amount"},
                "order_count": {"$sum": 1}
            }}
        ]
        sales_result = await db.orders.aggregate(sales_pipeline).to_list(1)
        sales_data = sales_result[0] if sales_result else {"total_sales": 0, "order_count": 0}

        # Sales summary — offline invoices + sales orders (db.offline_invoices, store_code-scoped)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        now_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        offline_date_match = {
            "$or": [
                {"created_at": {"$gte": start_date, "$type": "date"}},
                {"created_at": {"$gte": start_date_str, "$type": "string"}}
            ]
        }

        # Revenue: completed offline invoices only
        offline_revenue_pipeline = [
            {"$match": {
                "store_code": store["code"],
                "document_type": "invoice",
                **offline_date_match
            }},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": {"$ifNull": ["$total_amount", 0]}},
                "order_count": {"$sum": 1}
            }}
        ]
        offline_revenue_result = await db.offline_invoices.aggregate(offline_revenue_pipeline).to_list(1)
        offline_revenue_data = offline_revenue_result[0] if offline_revenue_result else {"total_sales": 0, "order_count": 0}

        # Order count: sales orders + invoices together
        offline_orders_count = await db.offline_invoices.count_documents({
            "store_code": store["code"],
            "document_type": {"$in": ["sales_order", "invoice"]},
            **offline_date_match
        })

        # Combine online + offline
        sales_data = {
            "total_sales": sales_data.get("total_sales", 0) + offline_revenue_data.get("total_sales", 0),
            "order_count": sales_data.get("order_count", 0) + offline_orders_count
        }
        
        # Purchase summary
        purchase_pipeline = [
            {"$match": {
                "store_id": store_id,
                "created_at": {"$gte": start_date}
            }},
            {"$group": {
                "_id": None,
                "total_purchases": {"$sum": "$total_amount"},
                "bill_count": {"$sum": 1}
            }}
        ]
        purchase_result = await db.purchase_bills.aggregate(purchase_pipeline).to_list(1)
        purchase_data = purchase_result[0] if purchase_result else {"total_purchases": 0, "bill_count": 0}
        
        # Pending deliveries
        pending_deliveries = await db.orders.count_documents({
            "store_id": store_id,
            "order_status": {"$in": ["confirmed", "processing", "shipped"]}
        })
        
        # Low stock items + total products stocked by this store
        inventory = await db.store_inventory.find_one({"store_id": store_id})
        low_stock_count = 0
        total_products_count = 0
        if inventory:
            store_products = inventory.get("products", {})
            total_products_count = len(store_products)
            for product_id, qty in store_products.items():
                if qty < 5:  # Low stock threshold
                    low_stock_count += 1
        
        # Pending POs
        pending_pos = await db.purchases.count_documents({
            "store_id": store_id,
            "status": {"$in": ["pending", "partial"]}
        })
        
        return {
            "status": "success",
            "store": {
                "id": store["id"],
                "code": store["code"],
                "name": store["name"]
            },
            "period": period,
            "summary": {
                "total_products": total_products_count,
                "total_sales": sales_data.get("total_sales", 0),
                "order_count": sales_data.get("order_count", 0),
                "total_purchases": purchase_data.get("total_purchases", 0),
                "purchase_count": purchase_data.get("bill_count", 0),
                "pending_deliveries": pending_deliveries,
                "low_stock_items": low_stock_count,
                "pending_purchase_orders": pending_pos
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ STORE REPORTS ============

@router.get("/{store_id}/reports/sales")
async def get_store_sales_report(
    store_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    group_by: str = "day",  # day, week, month, item
    source: str = "both",  # online, offline, both
    db = Depends(get_db)
):
    """Get store sales report with date and item-wise breakdown"""
    try:
        from dateutil import parser
        
        # Parse dates
        now = datetime.now(timezone.utc)
        if from_date:
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        else:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
        else:
            end = now
        
        # Base query
        match_query = {
            "store_id": store_id,
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        
        if group_by == "item":
            merged = {}

            if source in ("online", "both"):
                online_pipeline = [
                    {"$match": match_query},
                    {"$unwind": "$items"},
                    {"$group": {
                        "_id": "$items.product_name",
                        "product_id": {"$first": "$items.product_id"},
                        "quantity_sold": {"$sum": "$items.quantity"},
                        "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                        "order_count": {"$sum": 1}
                    }}
                ]
                online_results = await db.orders.aggregate(online_pipeline).to_list(None)
                for r in online_results:
                    key = r["_id"]
                    if key not in merged:
                        merged[key] = {
                            "_id": key,
                            "product_id": r.get("product_id"),
                            "quantity_sold": 0,
                            "total_revenue": 0,
                            "order_count": 0
                        }
                    merged[key]["quantity_sold"] += r.get("quantity_sold", 0)
                    merged[key]["total_revenue"] += r.get("total_revenue", 0)
                    merged[key]["order_count"] += r.get("order_count", 0)

            if source in ("offline", "both"):
                store = await db.stores.find_one({"id": store_id})
                store_code = store.get("code") if store else None
                start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
                end_str = end.strftime("%Y-%m-%dT%H:%M:%S")
                offline_match = {
                    "store_code": store_code,
                    "document_type": "invoice",
                    "$or": [
                        {"created_at": {"$gte": start, "$lte": end, "$type": "date"}},
                        {"created_at": {"$gte": start_str, "$lte": end_str, "$type": "string"}}
                    ]
                }
                offline_pipeline = [
                    {"$match": offline_match},
                    {"$unwind": "$items"},
                    {"$group": {
                        "_id": "$items.product_name",
                        "product_id": {"$first": "$items.product_id"},
                        "quantity_sold": {"$sum": "$items.quantity"},
                        "total_revenue": {"$sum": {"$ifNull": ["$items.total", 0]}},
                        "order_count": {"$sum": 1}
                    }}
                ]
                offline_results = await db.offline_invoices.aggregate(offline_pipeline).to_list(None)
                for r in offline_results:
                    key = r["_id"]
                    if key not in merged:
                        merged[key] = {
                            "_id": key,
                            "product_id": r.get("product_id"),
                            "quantity_sold": 0,
                            "total_revenue": 0,
                            "order_count": 0
                        }
                    merged[key]["quantity_sold"] += r.get("quantity_sold", 0)
                    merged[key]["total_revenue"] += r.get("total_revenue", 0)
                    merged[key]["order_count"] += r.get("order_count", 0)

            results = sorted(merged.values(), key=lambda x: x["total_revenue"], reverse=True)
        else:
            # Date-wise grouping
            if group_by == "day":
                date_format = "%Y-%m-%d"
            elif group_by == "week":
                date_format = "%Y-W%V"
            else:  # month
                date_format = "%Y-%m"
            
            pipeline = [
                {"$match": match_query},
                {"$group": {
                    "_id": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                    "total_sales": {"$sum": "$total_amount"},
                    "order_count": {"$sum": 1},
                    "avg_order_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"_id": 1}}
            ]
            results = await db.orders.aggregate(pipeline).to_list(None)
        
        # Calculate totals
        total_revenue = sum(r.get("total_sales", r.get("total_revenue", 0)) for r in results)
        total_orders = sum(r.get("order_count", 0) for r in results)
        
        return {
            "status": "success",
            "store_id": store_id,
            "period": {"from": start.isoformat(), "to": end.isoformat()},
            "group_by": group_by,
            "source": source,
            "data": results,
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "avg_order_value": total_revenue / total_orders if total_orders > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}/reports/purchases")
async def get_store_purchases_report(
    store_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    group_by: str = "day",  # day, week, month, item, vendor
    db = Depends(get_db)
):
    """Get store purchases report"""
    try:
        from dateutil import parser
        
        now = datetime.now(timezone.utc)
        if from_date:
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        else:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
        else:
            end = now
        
        match_query = {
            "store_id": store_id,
            "created_at": {"$gte": start, "$lte": end}
        }
        
        if group_by == "item":
            pipeline = [
                {"$match": match_query},
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.product_name",
                    "product_id": {"$first": "$items.product_id"},
                    "quantity_purchased": {"$sum": "$items.quantity"},
                    "total_cost": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "bill_count": {"$sum": 1}
                }},
                {"$sort": {"total_cost": -1}}
            ]
        elif group_by == "vendor":
            pipeline = [
                {"$match": match_query},
                {"$group": {
                    "_id": "$vendor_name",
                    "vendor_id": {"$first": "$vendor_id"},
                    "total_amount": {"$sum": "$total_amount"},
                    "bill_count": {"$sum": 1}
                }},
                {"$sort": {"total_amount": -1}}
            ]
        else:
            if group_by == "day":
                date_format = "%Y-%m-%d"
            elif group_by == "week":
                date_format = "%Y-W%V"
            else:
                date_format = "%Y-%m"
            
            pipeline = [
                {"$match": match_query},
                {"$group": {
                    "_id": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                    "total_purchases": {"$sum": "$total_amount"},
                    "bill_count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
        
        results = await db.purchase_bills.aggregate(pipeline).to_list(None)
        
        total_cost = sum(r.get("total_purchases", r.get("total_cost", r.get("total_amount", 0))) for r in results)
        total_bills = sum(r.get("bill_count", 0) for r in results)
        
        return {
            "status": "success",
            "store_id": store_id,
            "period": {"from": start.isoformat(), "to": end.isoformat()},
            "group_by": group_by,
            "data": results,
            "summary": {
                "total_cost": total_cost,
                "total_bills": total_bills
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
