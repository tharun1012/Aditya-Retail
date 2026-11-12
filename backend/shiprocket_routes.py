"""
Shiprocket Shipping Routes
API endpoints for shipping management with Shiprocket integration
"""
from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/shipping", tags=["Shipping"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Shiprocket Configuration
SHIPROCKET_BASE_URL = "https://apiv2.shiprocket.in/v1/external"
SHIPROCKET_EMAIL = os.environ.get('SHIPROCKET_EMAIL', '')
SHIPROCKET_PASSWORD = os.environ.get('SHIPROCKET_PASSWORD', '')
SHIPROCKET_PICKUP_LOCATION = os.environ.get('SHIPROCKET_PICKUP_LOCATION', 'Primary')

# Cache for Shiprocket token
shiprocket_token_cache = {
    "token": None,
    "expires_at": None,
    "last_failure_at": None,
    "last_failure_reason": None,
}


def get_shiprocket_token() -> str:
    """Get or refresh Shiprocket authentication token.

    Uses positive caching (9 days on success) and negative caching (5 min on failure)
    so we don't hammer Shiprocket's auth endpoint and get the account blocked.
    """
    global shiprocket_token_cache
    from datetime import timedelta

    # Positive cache: valid token
    if (shiprocket_token_cache["token"] and
            shiprocket_token_cache["expires_at"] and
            datetime.now() < shiprocket_token_cache["expires_at"]):
        return shiprocket_token_cache["token"]

    # Negative cache: recent failure — don't retry for 5 minutes
    if (shiprocket_token_cache.get("last_failure_at") and
            datetime.now() < shiprocket_token_cache["last_failure_at"] + timedelta(minutes=5)):
        reason = shiprocket_token_cache.get("last_failure_reason") or "authentication failed"
        raise HTTPException(status_code=503, detail=f"Shiprocket temporarily unavailable: {reason}")

    if not SHIPROCKET_EMAIL or not SHIPROCKET_PASSWORD:
        shiprocket_token_cache["last_failure_at"] = datetime.now()
        shiprocket_token_cache["last_failure_reason"] = "SHIPROCKET_EMAIL/PASSWORD not configured"
        raise HTTPException(status_code=503, detail="Shipping service not configured. Please contact support.")

    # Authenticate with Shiprocket
    auth_url = f"{SHIPROCKET_BASE_URL}/auth/login"
    auth_data = {
        "email": SHIPROCKET_EMAIL,
        "password": SHIPROCKET_PASSWORD
    }

    try:
        response = requests.post(auth_url, json=auth_data, timeout=30)
    except Exception as e:
        shiprocket_token_cache["last_failure_at"] = datetime.now()
        shiprocket_token_cache["last_failure_reason"] = f"network error: {e}"
        raise HTTPException(status_code=503, detail="Shipping service unreachable. Please try again shortly.")

    if response.status_code == 200:
        data = response.json()
        if "token" in data:
            shiprocket_token_cache["token"] = data["token"]
            shiprocket_token_cache["expires_at"] = datetime.now() + timedelta(days=9)
            shiprocket_token_cache["last_failure_at"] = None
            shiprocket_token_cache["last_failure_reason"] = None
            return data["token"]

    # Failure — record for negative cache
    reason = "unknown"
    try:
        body = response.json()
        reason = body.get("message") or str(body)[:200]
    except Exception:
        reason = response.text[:200] if response.text else f"HTTP {response.status_code}"

    shiprocket_token_cache["last_failure_at"] = datetime.now()
    shiprocket_token_cache["last_failure_reason"] = reason
    raise HTTPException(status_code=503, detail=f"Shiprocket authentication failed: {reason}")

# Pydantic Models
class ServiceabilityRequest(BaseModel):
    pickup_pincode: str = "560001"  # Default Bangalore
    delivery_pincode: str
    weight: float = 1.0
    cod: int = 1

class CreateShipmentRequest(BaseModel):
    order_id: str
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    address: str
    city: str
    state: str
    pincode: str
    payment_method: str = "Prepaid"
    items: List[Dict[str, Any]]
    subtotal: float
    weight: float = 1.0

class TrackShipmentRequest(BaseModel):
    awb_number: Optional[str] = None
    order_id: Optional[str] = None


def get_shiprocket_headers() -> Dict[str, str]:
    """Get headers with Shiprocket token"""
    token = get_shiprocket_token()
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }


@router.get("/status")
async def get_shiprocket_status():
    """Check Shiprocket integration status"""
    try:
        is_configured = bool(SHIPROCKET_EMAIL and SHIPROCKET_PASSWORD)
        
        if not is_configured:
            return {
                "status": "not_configured",
                "message": "Shiprocket credentials not set",
                "is_connected": False
            }
        
        # Try to authenticate
        token = get_shiprocket_token()
        
        return {
            "status": "connected",
            "message": "Shiprocket integration is active",
            "is_connected": True,
            "email": SHIPROCKET_EMAIL
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "is_connected": False
        }


@router.post("/serviceability")
async def check_serviceability(request: ServiceabilityRequest):
    """Check courier serviceability and get shipping rates"""
    try:
        if not SHIPROCKET_EMAIL or not SHIPROCKET_PASSWORD:
            # Fallback to manual calculation
            return await calculate_manual_shipping(request.delivery_pincode, request.weight)
        
        url = f"{SHIPROCKET_BASE_URL}/courier/serviceability/"
        params = {
            "pickup_postcode": request.pickup_pincode,
            "delivery_postcode": request.delivery_pincode,
            "weight": request.weight,
            "cod": request.cod
        }
        
        response = requests.get(url, params=params, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "data" in data:
            couriers = data["data"].get("available_courier_companies", [])
            
            if couriers:
                # Sort by rate
                couriers_sorted = sorted(couriers, key=lambda x: x["rate"])
                cheapest = couriers_sorted[0]
                
                return {
                    "status": "success",
                    "serviceable": True,
                    "recommended": {
                        "courier_name": cheapest["courier_name"],
                        "rate": cheapest["rate"],
                        "estimated_delivery": cheapest["etd"],
                        "courier_company_id": cheapest["courier_company_id"]
                    },
                    "all_options": [
                        {
                            "courier_name": c["courier_name"],
                            "rate": c["rate"],
                            "estimated_delivery": c["etd"],
                            "courier_company_id": c["courier_company_id"]
                        }
                        for c in couriers_sorted[:5]
                    ],
                    "total_options": len(couriers)
                }
            else:
                return {
                    "status": "success",
                    "serviceable": False,
                    "message": "No courier services available for this route"
                }
        else:
            return {
                "status": "error",
                "message": data.get("message", "Serviceability check failed")
            }
            
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to manual calculation
        return await calculate_manual_shipping(request.delivery_pincode, request.weight)


class CodChargesRequest(BaseModel):
    delivery_pincode: str
    order_value: float
    weight: float = 1.0


@router.post("/cod-charges")
async def get_cod_charges(request: CodChargesRequest):
    """Fetch COD extra charges from Shiprocket for the cheapest COD-supporting courier"""
    try:
        if not SHIPROCKET_EMAIL or not SHIPROCKET_PASSWORD:
            # Fallback: flat 2% or ₹40 whichever higher
            cod = max(40, round(request.order_value * 0.02))
            return {"status": "success", "cod_available": True, "cod_charges": cod, "source": "fallback"}

        url = f"{SHIPROCKET_BASE_URL}/courier/serviceability/"
        params = {
            "pickup_postcode": SHIPROCKET_PICKUP_LOCATION and "560058" or "560001",
            "delivery_postcode": request.delivery_pincode,
            "weight": request.weight,
            "cod": 1,
            "declared_value": request.order_value,
        }
        response = requests.get(url, params=params, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()

        if response.status_code == 200 and "data" in data:
            couriers = data["data"].get("available_courier_companies", [])
            cod_couriers = [c for c in couriers if c.get("cod") == 1 or c.get("is_cod_available")]
            if not cod_couriers:
                return {"status": "success", "cod_available": False, "cod_charges": 0}
            # Pick cheapest total (freight + cod_charges)
            cod_couriers.sort(key=lambda c: (c.get("cod_charges") or 0) + (c.get("rate") or 0))
            cheapest = cod_couriers[0]
            return {
                "status": "success",
                "cod_available": True,
                "cod_charges": round(cheapest.get("cod_charges") or 0),
                "courier_name": cheapest.get("courier_name"),
                "shipping_charges": round(cheapest.get("rate") or 0),
                "source": "shiprocket",
            }
        return {"status": "error", "cod_available": False, "cod_charges": 0, "message": data.get("message", "COD check failed")}
    except Exception as e:
        # Fallback
        cod = max(40, round(request.order_value * 0.02))
        return {"status": "success", "cod_available": True, "cod_charges": cod, "source": "fallback"}



async def calculate_manual_shipping(pincode: str, weight: float):
    """Manual shipping calculation as fallback"""
    metro_pincodes = ['110', '400', '700', '560', '600', '500']
    is_metro = any(pincode.startswith(metro) for metro in metro_pincodes)
    
    base_cost = 80 if is_metro else 120
    per_kg_cost = 30 if is_metro else 50
    
    shipping_cost = base_cost + (weight * per_kg_cost)
    estimated_days = "3-5" if is_metro else "5-7"
    
    return {
        "status": "success",
        "serviceable": True,
        "fallback": True,
        "recommended": {
            "courier_name": "Standard Shipping",
            "rate": shipping_cost,
            "estimated_delivery": f"{estimated_days} days",
            "courier_company_id": None
        },
        "all_options": [{
            "courier_name": "Standard Shipping",
            "rate": shipping_cost,
            "estimated_delivery": f"{estimated_days} days",
            "courier_company_id": None
        }],
        "message": "Using estimated shipping rates"
    }


@router.post("/create-order")
async def create_shiprocket_order(request: CreateShipmentRequest):
    """Create order in Shiprocket"""
    try:
        if not SHIPROCKET_EMAIL or not SHIPROCKET_PASSWORD:
            raise HTTPException(status_code=400, detail="Shiprocket not configured")
        
        # Prepare order data for Shiprocket
        order_data = {
            "order_id": request.order_number,
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pickup_location": SHIPROCKET_PICKUP_LOCATION,
            "billing_customer_name": request.customer_name,
            "billing_last_name": "",
            "billing_address": request.address,
            "billing_city": request.city,
            "billing_pincode": request.pincode,
            "billing_state": request.state,
            "billing_country": "India",
            "billing_email": request.customer_email,
            "billing_phone": request.customer_phone,
            "shipping_is_billing": True,
            "order_items": [
                {
                    "name": item.get("name", "Product"),
                    "sku": item.get("sku", item.get("product_id", "SKU001")),
                    "units": item.get("quantity", 1),
                    "selling_price": item.get("price", 0)
                }
                for item in request.items
            ],
            "payment_method": request.payment_method,
            "sub_total": request.subtotal,
            "length": 30,
            "breadth": 20,
            "height": 20,
            "weight": request.weight
        }
        
        url = f"{SHIPROCKET_BASE_URL}/orders/create/adhoc"
        response = requests.post(url, json=order_data, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "order_id" in data:
            # Save shipment info to database
            shipment_record = {
                "order_id": request.order_id,
                "order_number": request.order_number,
                "shiprocket_order_id": data["order_id"],
                "shipment_id": data.get("shipment_id"),
                "status": "created",
                "created_at": datetime.utcnow().isoformat()
            }
            
            await db.shipments.insert_one(shipment_record)
            
            return {
                "status": "success",
                "message": "Order created in Shiprocket",
                "shiprocket_order_id": data["order_id"],
                "shipment_id": data.get("shipment_id")
            }
        else:
            return {
                "status": "error",
                "message": data.get("message", "Order creation failed"),
                "errors": data.get("errors", {})
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-awb")
async def generate_awb(shipment_id: str, courier_company_id: int):
    """Generate AWB (Air Waybill) for shipment"""
    try:
        url = f"{SHIPROCKET_BASE_URL}/courier/assign/awb"
        awb_data = {
            "shipment_id": shipment_id,
            "courier_company_id": courier_company_id
        }
        
        response = requests.post(url, json=awb_data, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200 and data.get("awb_assign_status") == 1:
            awb_data = data["response"]["data"]
            
            # Update shipment record
            await db.shipments.update_one(
                {"shipment_id": shipment_id},
                {"$set": {
                    "awb_number": awb_data["awb_number"],
                    "courier_name": awb_data["courier_name"],
                    "status": "awb_assigned",
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            return {
                "status": "success",
                "awb_number": awb_data["awb_number"],
                "courier_name": awb_data["courier_name"],
                "courier_company_id": awb_data["courier_company_id"]
            }
        else:
            return {
                "status": "error",
                "message": data.get("message", "AWB generation failed")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/{awb_number}")
async def track_shipment(awb_number: str):
    """Track shipment using AWB number"""
    try:
        url = f"{SHIPROCKET_BASE_URL}/courier/track/awb/{awb_number}"
        
        response = requests.get(url, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "tracking_data" in data:
            tracking = data["tracking_data"]
            
            # Parse tracking events
            events = []
            if "shipment_track" in tracking:
                for event in tracking["shipment_track"]:
                    events.append({
                        "date": event.get("date"),
                        "status": event.get("sr-status"),
                        "location": event.get("location"),
                        "activity": event.get("activity")
                    })
            
            return {
                "status": "success",
                "current_status": tracking.get("track_status"),
                "expected_delivery": tracking.get("edd"),
                "delivered_date": tracking.get("delivered_date"),
                "events": events
            }
        else:
            return {
                "status": "error",
                "message": data.get("message", "Tracking failed")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/track/order/{order_id}")
async def track_by_order_id(order_id: str):
    """Track shipment by order ID"""
    try:
        # Find shipment record
        shipment = await db.shipments.find_one({"order_id": order_id}, {"_id": 0})
        
        if not shipment:
            return {
                "status": "error",
                "message": "Shipment not found for this order"
            }
        
        if shipment.get("awb_number"):
            # Track using AWB
            return await track_shipment(shipment["awb_number"])
        else:
            return {
                "status": "pending",
                "message": "AWB not yet generated",
                "shiprocket_order_id": shipment.get("shiprocket_order_id"),
                "shipment_status": shipment.get("status")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule-pickup")
async def schedule_pickup(shipment_id: str):
    """Schedule pickup for shipment"""
    try:
        url = f"{SHIPROCKET_BASE_URL}/courier/generate/pickup"
        pickup_data = {
            "shipment_id": [shipment_id]
        }
        
        response = requests.post(url, json=pickup_data, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            # Update shipment record
            await db.shipments.update_one(
                {"shipment_id": shipment_id},
                {"$set": {
                    "pickup_scheduled": True,
                    "status": "pickup_scheduled",
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            return {
                "status": "success",
                "message": "Pickup scheduled successfully",
                "response": data
            }
        else:
            return {
                "status": "error",
                "message": data.get("message", "Pickup scheduling failed")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_all_shipments(page: int = 1, limit: int = 20):
    """Get all shipments"""
    try:
        skip = (page - 1) * limit
        
        shipments = await db.shipments.find(
            {}, {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.shipments.count_documents({})
        
        return {
            "status": "success",
            "shipments": shipments,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pickup-locations")
async def get_pickup_locations():
    """Get configured pickup locations from Shiprocket"""
    try:
        url = f"{SHIPROCKET_BASE_URL}/settings/company/pickup"
        
        response = requests.get(url, headers=get_shiprocket_headers(), timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "status": "success",
                "pickup_locations": data.get("data", {}).get("shipping_address", [])
            }
        else:
            return {
                "status": "error",
                "message": "Could not fetch pickup locations"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def shiprocket_webhook(request: Request):
    """Receive real-time shipment status updates from Shiprocket.
    Configure in Shiprocket panel: Settings → API → Webhooks.
    Token (if configured) arrives in the x-api-key header.
    """
    from shiprocket_tracking_service import apply_tracking_update
    try:
        try:
            payload = await request.json()
            if not isinstance(payload, dict):
                payload = {}
        except Exception:
            payload = {}

        # Optional token verification (enforced only when SHIPROCKET_WEBHOOK_TOKEN is set)
        expected_token = os.environ.get("SHIPROCKET_WEBHOOK_TOKEN")
        if expected_token:
            provided = request.headers.get("x-api-key") or ""
            if provided != expected_token:
                return {"success": False, "message": "Invalid webhook token"}

        # Shiprocket webhook fields vary; extract robustly
        payload = payload or {}
        # Shiprocket webhook fields vary; extract robustly
        awb = str(payload.get("awb") or payload.get("awb_code") or "") or None
        sr_status = (payload.get("current_status") or payload.get("shipment_status")
                     or payload.get("status") or "")
        courier = payload.get("courier_name") or payload.get("courier") or None
        channel_order_id = str(payload.get("channel_order_id") or payload.get("order_id") or "") or None
        sr_order_id = payload.get("sr_order_id") or payload.get("shiprocket_order_id")

        # Log raw payload for debugging/recovery
        await db.shiprocket_webhooks.insert_one({
            "payload": payload,
            "received_at": datetime.now().isoformat(),
        })

        or_clauses = []
        if channel_order_id:
            or_clauses += [
                {"order_number": channel_order_id},
                {"id": channel_order_id},
                # Shiprocket sometimes sends its internal order id in "order_id"
                {"shiprocket_order_id": channel_order_id},
            ]
            if channel_order_id.isdigit():
                or_clauses.append({"shiprocket_order_id": int(channel_order_id)})
        if sr_order_id:
            or_clauses.append({"shiprocket_order_id": sr_order_id})
            or_clauses.append({"shiprocket_order_id": str(sr_order_id)})
        if awb:
            or_clauses.append({"sr_awb_code": awb})
        if not or_clauses:
            return {"success": True, "message": "No order identifiers in payload"}

        order = await db.orders.find_one({"$or": or_clauses}, {"_id": 0})
        if not order:
            return {"success": True, "message": "Order not found for webhook payload"}

        result = await apply_tracking_update(db, order, sr_status, awb, courier)
        return {"success": True, **result}
    except Exception as e:
        # Always ack webhooks with 200 so Shiprocket doesn't disable them
        return {"success": False, "message": str(e)}


@router.post("/poll-tracking")
async def manual_poll_tracking():
    """Manually trigger a Shiprocket tracking status sync for all active orders"""
    from shiprocket_tracking_service import poll_shiprocket_updates
    result = await poll_shiprocket_updates(db)
    return {"success": True, **result}


@router.post("/sync-order/{order_id}")
async def sync_order_to_shiprocket(order_id: str):
    """Manually retry pushing a website order to Shiprocket.

    Accepts either the order's UUID (`id`) or its human-readable `order_number`.
    Useful for orders that were created before auto-sync was live, or when a
    previous sync failed (Shiprocket auth blip, network error, etc.).
    """
    # Locate the order by id OR order_number
    order = await db.orders.find_one({"$or": [{"id": order_id}, {"order_number": order_id}]})
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    # If already synced successfully, short-circuit
    if order.get("shiprocket_order_id"):
        return {
            "status": "already_synced",
            "message": f"Order already synced to Shiprocket as #{order['shiprocket_order_id']}",
            "shiprocket_order_id": order["shiprocket_order_id"],
        }

    addr = order.get("shipping_address") or order.get("billing_address") or {}
    cust = order.get("customer_details") or {}
    sr_items = [
        {
            "name": (it.get("name") or "Product")[:50],
            "sku": it.get("sku") or it.get("model_number") or it.get("product_id") or "SKU001",
            "quantity": int(it.get("quantity") or 1),
            "price": float(it.get("price") or 0),
        }
        for it in order.get("items", [])
    ]
    total_weight = sum(float(it.get("weight") or 1.0) * int(it.get("quantity") or 1) for it in order.get("items", []))
    total_weight = max(total_weight, 0.5)

    req = CreateShipmentRequest(
        order_id=order.get("id") or order_id,
        order_number=order.get("order_number") or order_id,
        customer_name=(cust.get("name") or "Customer")[:100],
        customer_email=cust.get("email") or "noemail@adityaretail.com",
        customer_phone=str(cust.get("phone") or ""),
        address=(addr.get("address") or addr.get("line1") or "Address not provided")[:200],
        city=addr.get("city") or "Bangalore",
        state=addr.get("state") or "Karnataka",
        pincode=str(addr.get("pincode") or addr.get("zipcode") or "560058"),
        payment_method="COD" if (order.get("payment_method") or "cod").lower() == "cod" else "Prepaid",
        items=sr_items,
        subtotal=float(order.get("subtotal") or order.get("total_amount") or 0),
        weight=total_weight,
    )
    result = await create_shiprocket_order(req)

    if result and result.get("status") == "success":
        await db.orders.update_one(
            {"id": order["id"]},
            {"$set": {
                "shiprocket_order_id": result.get("shiprocket_order_id"),
                "shiprocket_shipment_id": result.get("shipment_id"),
                "shiprocket_synced_at": datetime.utcnow().isoformat(),
                "shiprocket_sync_error": None,
            }},
        )
    else:
        reason = (result or {}).get("message") or str(result)
        await db.orders.update_one(
            {"id": order["id"]},
            {"$set": {"shiprocket_sync_error": reason[:500]}},
        )
    return result


@router.get("/sync-status")
async def shiprocket_sync_status(limit: int = 20):
    """List recent orders and their Shiprocket sync state.

    Handy for the admin dashboard to see which orders are stuck / unsynced.
    """
    orders = await db.orders.find(
        {},
        {"_id": 0, "id": 1, "order_number": 1, "created_at": 1, "customer_details": 1,
         "total_amount": 1, "payment_method": 1, "shiprocket_order_id": 1,
         "shiprocket_synced_at": 1, "shiprocket_sync_error": 1},
    ).sort("created_at", -1).limit(limit).to_list(length=limit)

    return {
        "status": "success",
        "count": len(orders),
        "orders": [
            {
                "order_id": o.get("id"),
                "order_number": o.get("order_number"),
                "created_at": o.get("created_at"),
                "customer": (o.get("customer_details") or {}).get("name"),
                "total": o.get("total_amount"),
                "payment_method": o.get("payment_method"),
                "shiprocket_order_id": o.get("shiprocket_order_id"),
                "synced_at": o.get("shiprocket_synced_at"),
                "sync_error": o.get("shiprocket_sync_error"),
                "sync_state": (
                    "synced" if o.get("shiprocket_order_id")
                    else ("failed" if o.get("shiprocket_sync_error") else "pending")
                ),
            }
            for o in orders
        ],
    }
