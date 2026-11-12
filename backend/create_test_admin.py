#!/usr/bin/env python3
"""
Create a test admin user manually
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import uuid

async def create_test_admin():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'startup_template')
    db = client[db_name]
    
    # Test admin user details
    test_email = "admin@test.com"
    test_name = "Test Admin"
    
    print(f"Creating test admin user: {test_email}")
    
    # Check if user already exists
    existing = await db.users.find_one({"email": test_email})
    
    if existing:
        print(f"User {test_email} already exists. Updating role to admin...")
        await db.users.update_one(
            {"email": test_email},
            {"$set": {"role": "admin"}}
        )
        user_id = existing.get("id") or existing.get("_id")
    else:
        print(f"Creating new user {test_email}...")
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": test_email,
            "name": test_name,
            "role": "admin",
            "picture": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
    
    # Create a test session token
    session_token = f"test_session_{uuid.uuid4()}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Delete old sessions for this user
    await db.user_sessions.delete_many({"user_id": str(user_id)})
    
    # Create new session
    session_doc = {
        "id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    print("\n" + "="*60)
    print("✅ Test admin user created successfully!")
    print("="*60)
    print(f"\nEmail: {test_email}")
    print(f"Role: admin")
    print(f"Session Token: {session_token}")
    print("\nTo login, use this in browser console:")
    print(f"document.cookie = 'session_token={session_token}; path=/; max-age=604800'")
    print("\nThen refresh the page and navigate to: /#/admin")
    print("="*60 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_admin())
