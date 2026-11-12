#!/usr/bin/env python3
"""
Create admin accounts for the user's Google emails
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import uuid

async def create_admin_accounts():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'startup_template')
    db = client[db_name]
    
    # User details
    users_data = [
        {"email": "rohit.gadiya@gmail.com", "name": "Rohit Gadiya"},
        {"email": "slant.ninety@gmail.com", "name": "Slant Ninety"}
    ]
    
    print("Creating admin accounts...\n")
    
    session_tokens = []
    
    for user_data in users_data:
        email = user_data["email"]
        name = user_data["name"]
        
        # Check if user exists
        existing = await db.users.find_one({"email": email})
        
        if existing:
            print(f"User {email} exists. Updating to admin...")
            await db.users.update_one(
                {"email": email},
                {"$set": {"role": "admin"}}
            )
            user_id = existing.get("id") or existing.get("_id")
        else:
            print(f"Creating new user {email}...")
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": "admin",
                "picture": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)
        
        # Create session
        session_token = f"admin_session_{uuid.uuid4()}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        # Delete old sessions
        await db.user_sessions.delete_many({"user_id": str(user_id)})
        
        # Create new session
        session_doc = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.user_sessions.insert_one(session_doc)
        
        session_tokens.append({"email": email, "token": session_token})
        print(f"✅ Created admin account for {email}")
    
    print("\n" + "="*70)
    print("✅ ALL ADMIN ACCOUNTS CREATED!")
    print("="*70)
    
    for item in session_tokens:
        print(f"\nEmail: {item['email']}")
        print(f"Cookie command:")
        print(f"document.cookie = 'session_token={item['token']}; path=/; max-age=604800'")
    
    print("\n" + "="*70)
    print("INSTRUCTIONS:")
    print("="*70)
    print("1. Open browser console (F12)")
    print("2. Paste ONE of the cookie commands above")
    print("3. Navigate to: https://acct-workflow-1.preview.emergentagent.com/#/admin")
    print("4. You should see the admin dashboard!")
    print("="*70 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_accounts())
