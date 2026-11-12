# Complete Authentication System for AI Ecommerce Platform
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from pydantic import BaseModel, EmailStr, validator, Field
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uuid
import secrets
import os
from app.database import Base, get_db
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', String, ForeignKey('permissions.id'), primary_key=True)
)

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    pincode = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    orders = relationship("Order", back_populates="customer")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    resource = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    roles: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    expires_in: int

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permission_names: List[str] = []

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    permissions: List[str] = []
    
    class Config:
        from_attributes = True

# Authentication Handler
class AuthHandler:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

auth_handler = AuthHandler()

# CRUD Operations
class AuthCRUD:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = auth_handler.hash_password(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            address=user.address,
            pincode=user.pincode,
            hashed_password=hashed_password
        )
        
        # Assign default customer role
        customer_role = db.query(Role).filter(Role.name == "customer").first()
        if customer_role:
            db_user.roles.append(customer_role)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not auth_handler.verify_password(password, user.hashed_password):
            return None
        
        user.last_login = datetime.utcnow()
        db.commit()
        return user
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: str, token: str) -> RefreshToken:
        expires_at = datetime.utcnow() + timedelta(days=7)
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        return db_token
    
    @staticmethod
    def get_valid_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
        return db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
    
    @staticmethod
    def initialize_roles_and_permissions(db: Session):
        # Create permissions
        permissions_data = [
            {"name": "read_products", "description": "View products", "resource": "products", "action": "read"},
            {"name": "create_products", "description": "Create products", "resource": "products", "action": "create"},
            {"name": "update_products", "description": "Update products", "resource": "products", "action": "update"},
            {"name": "delete_products", "description": "Delete products", "resource": "products", "action": "delete"},
            {"name": "manage_users", "description": "Manage users", "resource": "users", "action": "manage"},
            {"name": "manage_orders", "description": "Manage orders", "resource": "orders", "action": "manage"},
            {"name": "view_analytics", "description": "View analytics", "resource": "analytics", "action": "read"},
            {"name": "manage_inventory", "description": "Manage inventory", "resource": "inventory", "action": "manage"},
        ]
        
        created_permissions = {}
        for perm_data in permissions_data:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
                db.flush()
                created_permissions[perm_data["name"]] = permission
            else:
                created_permissions[perm_data["name"]] = existing
        
        # Create roles
        roles_data = [
            {
                "name": "super_admin",
                "description": "Super administrator with full access",
                "permissions": list(created_permissions.keys())
            },
            {
                "name": "admin",
                "description": "Administrator with management access",
                "permissions": ["create_products", "update_products", "delete_products", "manage_users", "manage_orders", "view_analytics", "manage_inventory"]
            },
            {
                "name": "manager",
                "description": "Manager with operational access",
                "permissions": ["read_products", "update_products", "manage_orders", "view_analytics"]
            },
            {
                "name": "customer",
                "description": "Customer with basic access",
                "permissions": ["read_products"]
            }
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(name=role_data["name"], description=role_data["description"])
                role.permissions = [created_permissions[perm_name] for perm_name in role_data["permissions"]]
                db.add(role)
        
        db.commit()

auth_crud = AuthCRUD()

# Dependencies
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = auth_handler.verify_token(token)
        username = payload.get("sub")
        user = auth_crud.get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_permissions(permissions: List[str]):
    def permission_checker(user: User = Depends(get_current_active_user)):
        user_permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.name)
        
        if not any(perm in user_permissions for perm in permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return permission_checker

def require_admin(user: User = Depends(get_current_active_user)):
    if not any(role.name in ["admin", "super_admin"] for role in user.roles):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if auth_crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if auth_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = auth_crud.create_user(db, user)
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        phone=db_user.phone,
        address=db_user.address,
        pincode=db_user.pincode,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        roles=[role.name for role in db_user.roles],
        created_at=db_user.created_at
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    
    # Create tokens
    access_token = auth_handler.create_access_token(data={"sub": user.username})
    refresh_token = auth_handler.create_refresh_token()
    
    # Store refresh token
    auth_crud.create_refresh_token(db, user.id, refresh_token)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=1800
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        address=current_user.address,
        pincode=current_user.pincode,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        roles=[role.name for role in current_user.roles],
        created_at=current_user.created_at
    )

@router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    users = db.query(User).all()
    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        address=user.address,
        pincode=user.pincode,
        is_active=user.is_active,
        is_verified=user.is_verified,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    ) for user in users]

@router.post("/roles", response_model=RoleResponse)
async def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    # Check if role exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    db_role = Role(name=role.name, description=role.description)
    
    # Add permissions
    for perm_name in role.permission_names:
        permission = db.query(Permission).filter(Permission.name == perm_name).first()
        if permission:
            db_role.permissions.append(permission)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return RoleResponse(
        id=db_role.id,
        name=db_role.name,
        description=db_role.description,
        permissions=[perm.name for perm in db_role.permissions]
    )

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    roles = db.query(Role).all()
    return [RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[perm.name for perm in role.permissions]
    ) for role in roles]

@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role(user_id: str, role_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = auth_crud.get_user_by_id(db, user_id)
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    return {"message": "Role assigned successfully"}