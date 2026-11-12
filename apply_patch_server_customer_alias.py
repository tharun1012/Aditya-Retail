path = "backend/server.py"
with open(path, "r") as f:
    content = f.read()

changes_made = []

# 1. Import the real create_customer function and its model
import_old = "from customers_routes import router as customers_router"
import_new = "from customers_routes import router as customers_router\nfrom customers_routes import create_customer as _create_customer_impl, CustomerCreate as _CustomerCreate"
if import_new not in content and import_old in content:
    content = content.replace(import_old, import_new, 1)
    changes_made.append("added import")

# 2. Replace the duplicated endpoint body with a delegation call
old = '''@api_router.post("/customers/")
@api_router.post("/customers")
async def create_customer_alias(customer: CustomerCreateRequest):
    """Create a new customer (alias for store users)"""
    try:
        from database import get_db
        import uuid
        from datetime import datetime, timezone
        
        db = await get_db()
        
        # Check if customer with phone already exists
        existing = await db.customers.find_one({"phone": customer.phone})
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
        
        customer_data = {
            "id": str(uuid.uuid4()),
            "name": customer.name,
            "phone": customer.phone,
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
        }'''

new = '''@api_router.post("/customers/")
@api_router.post("/customers")
async def create_customer_alias(customer: CustomerCreateRequest):
    """Create a new customer (alias for store users) - delegates to customers_routes to avoid duplicate logic"""
    try:
        shared_customer = _CustomerCreate(**customer.dict())
        return await _create_customer_impl(shared_customer)'''

if old not in content:
    print("BLOCK NOT FOUND - aborting, no changes written")
    exit()
content = content.replace(old, new)
changes_made.append("delegated create_customer_alias to customers_routes.create_customer")

with open(path, "w") as f:
    f.write(content)

print("Patch applied successfully:", ", ".join(changes_made))
