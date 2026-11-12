#!/usr/bin/env python3
"""
Create admin and customer test accounts for Aditya Retail
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import hashlib
import uuid

def simple_hash(password: str) -> str:
    """Simple SHA256 password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_accounts():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("\n" + "="*70)
    print("CREATING ACCOUNTS FOR ADITYA RETAIL")
    print("="*70 + "\n")
    
    # ==================== ADMIN ACCOUNT ====================
    admin_email = "admin@adityaretail.com"
    admin_password = "admin123"  # Change this to your preferred password
    admin_name = "Aditya Retail Admin"
    
    print("📋 CREATING ADMIN ACCOUNT...")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    
    # Check if admin exists
    existing_admin = await db.admins.find_one({"email": admin_email})
    
    if existing_admin:
        print(f"   ⚠️  Admin already exists. Updating password...")
        await db.admins.update_one(
            {"email": admin_email},
            {"$set": {
                "password": simple_hash(admin_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password": simple_hash(admin_password),
            "name": admin_name,
            "role": "super_admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.admins.insert_one(admin_doc)
        print(f"   ✅ Admin account created!")
    
    # ==================== CUSTOMER ACCOUNTS ====================
    customers = [
        {
            "email": "customer1@test.com",
            "password": "customer123",
            "name": "Test Customer 1",
            "phone": "+91-9876543210"
        },
        {
            "email": "customer2@test.com",
            "password": "customer123",
            "name": "Test Customer 2",
            "phone": "+91-9876543211"
        }
    ]
    
    print("\n📋 CREATING CUSTOMER ACCOUNTS...")
    
    for customer in customers:
        existing_customer = await db.users.find_one({"email": customer["email"]})
        
        if existing_customer:
            print(f"   ⚠️  {customer['email']} already exists")
        else:
            customer_doc = {
                "id": str(uuid.uuid4()),
                "email": customer["email"],
                "password": simple_hash(customer["password"]),
                "name": customer["name"],
                "phone": customer["phone"],
                "role": "customer",
                "addresses": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(customer_doc)
            print(f"   ✅ Created: {customer['email']} | Password: {customer['password']}")
    
    # ==================== SUMMARY ====================
    print("\n" + "="*70)
    print("✅ ACCOUNTS CREATED SUCCESSFULLY!")
    print("="*70)
    
    print("\n🔐 ADMIN LOGIN:")
    print(f"   URL: http://localhost:3000/#/admin/login")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    
    print("\n👤 CUSTOMER LOGIN:")
    print(f"   URL: http://localhost:3000/#/login")
    print(f"   Customer 1: customer1@test.com | Password: customer123")
    print(f"   Customer 2: customer2@test.com | Password: customer123")
    
    print("\n💡 TIPS:")
    print("   - Admin has full access to dashboard and management")
    print("   - Customers can browse products, add to cart, and place orders")
    print("   - Change passwords after first login for security")
    
    print("\n" + "="*70 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_accounts())
