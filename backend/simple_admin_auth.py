from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import os
import jwt
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/auth/admin", tags=["Admin Auth"])

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# MongoDB connection - use DB_NAME from environment
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginResponse(BaseModel):
    token: str
    access_token: Optional[str] = None  # alias for `token` — added for frontend compatibility
    user: dict

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify bcrypt password"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        # Find admin user by email in admin_users collection
        admin = await db.admin_users.find_one({"email": request.email})
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if this is a delivery person - they should use delivery login
        if admin.get("role") == "delivery_person":
            raise HTTPException(status_code=401, detail="Please use the Delivery Person login portal")
        
        # Verify password using bcrypt
        if not verify_password(request.password, admin.get("password", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active (default to True for backward compatibility)
        if not admin.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is disabled")
        
        # Create access token
        token_data = {
            "sub": admin.get("email"),
            "user_id": admin.get("id"),
            "role": admin.get("role", "admin")
        }
        access_token = create_access_token(token_data)
        
        # Return token and user info
        user_info = {
            "id": admin.get("id"),
            "email": admin.get("email"),
            "first_name": admin.get("first_name", admin.get("name", "Admin").split()[0] if admin.get("name") else "Admin"),
            "last_name": admin.get("last_name", " ".join(admin.get("name", "").split()[1:]) if admin.get("name") else ""),
            "role": admin.get("role", "admin"),
            "is_active": admin.get("is_active", True)
        }
        
        return {
            "token": access_token,
            "access_token": access_token,
            "user": user_info
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/logout")
async def admin_logout():
    """Admin logout (client should clear token)"""
    return {"message": "Logged out successfully"}

@router.get("/verify")
async def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        admin = await db.admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "valid": True,
            "user": {
                "id": admin.get("id"),
                "email": admin.get("email"),
                "name": admin.get("name"),
                "role": admin.get("role")
            }
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
