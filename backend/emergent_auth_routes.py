from fastapi import APIRouter, HTTPException, Response, Request, Depends, Cookie
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, timezone, timedelta
import httpx
import os
from database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

EMERGENT_AUTH_API = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"

@router.get("/session")
async def process_session(
    session_id: str,
    response: Response,
    database = Depends(get_db)
):
    """
    Process session_id from Emergent Auth and create user session
    """
    try:
        # Call Emergent Auth API to get user data
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                EMERGENT_AUTH_API,
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session ID")
            
            user_data = auth_response.json()
        
        # Check if user exists in our database
        existing_user = await database.users.find_one({"email": user_data["email"]}, {"_id": 0})
        
        if not existing_user:
            # Create new user with a stable user_id field
            import uuid
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_doc = {
                "user_id": user_id,
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "role": "customer",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await database.users.insert_one(user_doc)
            from website_leads import create_website_signup_lead
            await create_website_signup_lead(database, user_doc)
            user_role = "customer"
        else:
            user_id = existing_user.get("user_id") or existing_user.get("id") or str(existing_user.get("_id", ""))
            user_role = existing_user.get("role", "customer")
            # Ensure user_id field exists for future lookups
            if not existing_user.get("user_id"):
                await database.users.update_one(
                    {"email": user_data["email"]},
                    {"$set": {"user_id": user_id}}
                )
        
        # Get session_token from Emergent Auth response
        session_token = user_data.get("session_token")
        if not session_token:
            raise HTTPException(status_code=500, detail="No session token received from auth provider")
        
        # Create user session in our database
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await database.user_sessions.insert_one(session_doc)
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        return {
            "success": True,
            "access_token": session_token,
            "user": {
                "id": user_id,
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "role": user_role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Session processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process session: {str(e)}")


@router.get("/me")
async def get_current_user(
    request: Request,
    database = Depends(get_db)
):
    """
    Get current authenticated user
    Checks cookie first, then Authorization header
    """
    # Try to get token from cookie
    token = request.cookies.get("session_token")
    
    # Fallback to Authorization header if no cookie
    if not token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session in database
    session = await database.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Check if session is expired
    expires_at = session.get("expires_at")
    if expires_at:
        # Handle both string and datetime formats
        if isinstance(expires_at, str):
            from dateutil.parser import parse as parse_date
            try:
                expires_dt = parse_date(expires_at)
                if expires_dt.tzinfo is None:
                    expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            except Exception:
                expires_dt = None
        elif isinstance(expires_at, datetime):
            expires_dt = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_dt = None
        
        if expires_dt and expires_dt < datetime.now(timezone.utc):
            await database.user_sessions.delete_one({"session_token": token})
            raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user data - try multiple lookup fields
    user_id = session.get("user_id")
    user_doc = await database.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user_doc:
        user_doc = await database.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        user_doc = await database.users.find_one({"email": session.get("email")}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user_doc.get("user_id") or user_doc.get("id") or "",
        "email": user_doc.get("email"),
        "name": user_doc.get("name"),
        "picture": user_doc.get("picture"),
        "role": user_doc.get("role", "customer")
    }


@router.post("/logout")
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None),
    database = Depends(get_db)
):
    """
    Logout user and clear session
    """
    if session_token:
        # Delete session from database
        await database.user_sessions.delete_one({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    
    return {"success": True, "message": "Logged out successfully"}
