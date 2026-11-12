#!/usr/bin/env python3
"""
Update user roles to admin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def update_to_admin():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'startup_template')
    db = client[db_name]
    
    # Update both email addresses to admin
    emails = ["rohit.gadiya@gmail.com", "slant.ninety@gmail.com"]
    
    for email in emails:
        result = await db.users.update_one(
            {"email": email},
            {"$set": {"role": "admin"}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Updated {email} to admin role")
        else:
            print(f"❌ User {email} not found in database")
    
    # List all users to verify
    print("\n" + "="*60)
    print("All users in database:")
    print("="*60)
    cursor = db.users.find({})
    users = await cursor.to_list(length=100)
    
    for user in users:
        email = user.get("email")
        role = user.get("role")
        print(f"  {email:40s} → {role}")
    
    print("="*60 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_to_admin())
