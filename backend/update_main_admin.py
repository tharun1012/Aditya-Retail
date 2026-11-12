#!/usr/bin/env python3
"""
Update main admin credentials for Aditya Retail
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

async def update_main_admin():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'startup_template')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Main admin details
    admin_email = "rohit.gadiya@gmail.com"
    admin_password = "Purvi@vriddhi01"
    admin_name = "Rohit Gadiya"
    
    print("\n" + "="*70)
    print("UPDATING MAIN ADMIN ACCOUNT")
    print("="*70 + "\n")
    
    # Check if admin exists
    existing_admin = await db.admins.find_one({"email": admin_email})
    
    if existing_admin:
        print(f"✅ Admin {admin_email} already exists. Updating...")
        await db.admins.update_one(
            {"email": admin_email},
            {"$set": {
                "password": simple_hash(admin_password),
                "name": admin_name,
                "role": "super_admin",
                "permissions": ["all"],  # Full access
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        print(f"✅ Creating new admin: {admin_email}")
        admin_doc = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password": simple_hash(admin_password),
            "name": admin_name,
            "role": "super_admin",
            "permissions": ["all"],  # Full access to everything
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.admins.insert_one(admin_doc)
    
    # Remove old test admin
    await db.admins.delete_many({"email": "admin@adityaretail.com"})
    
    print("\n" + "="*70)
    print("✅ MAIN ADMIN ACCOUNT UPDATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n🔐 YOUR ADMIN LOGIN:")
    print(f"   URL: http://localhost:3000/#/admin/login")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"\n   Role: Super Admin (Full Control)")
    print(f"   Access: All features + Admin Management")
    print("\n" + "="*70 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_main_admin())
