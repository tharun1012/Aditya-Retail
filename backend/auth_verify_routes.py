from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
from database import get_db

router = APIRouter(prefix="/auth-verify", tags=["auth-verify"])

@router.get("/user")
async def verify_user(
    request: Request,
    database = Depends(get_db)
):
    """
    Verify user session and return user data
    Simple endpoint that works!
    """
    # Get token from cookie
    token = request.cookies.get("session_token")
    
    print(f"[Auth Verify] Cookie token: {token}")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    session = await database.user_sessions.find_one({"session_token": token})
    print(f"[Auth Verify] Session found: {session is not None}")
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session.get("expires_at")
    if expires_at and expires_at < datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user_id = session.get("user_id")
    user = await database.users.find_one({"id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role", "customer"),
        "picture": user.get("picture")
    }
