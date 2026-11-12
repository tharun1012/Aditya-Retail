from fastapi import APIRouter, Response, Depends
from datetime import datetime, timezone, timedelta
from database import get_db
import uuid

router = APIRouter(prefix="/test-admin", tags=["test-admin"])

@router.get("/login/{email}")
async def test_admin_login(
    email: str,
    response: Response,
    database = Depends(get_db)
):
    """
    Test admin login - DEVELOPMENT ONLY
    Creates a session for the given email with admin role
    """
    # Find or create user
    user = await database.users.find_one({"email": email})
    
    if not user:
        # Create new admin user
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "name": email.split('@')[0].replace('.', ' ').title(),
            "role": "admin",
            "picture": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await database.users.insert_one(user)
    else:
        # Update to admin if not already
        user_id = user.get("id") or user.get("_id")
        await database.users.update_one(
            {"email": email},
            {"$set": {"role": "admin"}}
        )
    
    # Create session
    session_token = f"test_{uuid.uuid4()}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Delete old sessions
    await database.user_sessions.delete_many({"user_id": str(user_id)})
    
    # Create new session
    session_doc = {
        "id": str(uuid.uuid4()),
        "user_id": str(user_id),
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await database.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "success": True,
        "message": f"Test admin session created for {email}",
        "session_token": session_token,
        "redirect_to": "/#/admin"
    }
