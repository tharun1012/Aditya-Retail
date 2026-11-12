from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import hashlib
import uuid
from database import get_db
from roles_permissions import PERMISSION_MODULES, ROLE_TEMPLATES, check_permission, get_modules_by_category, get_roles_by_level

router = APIRouter(prefix="/admin/management", tags=["Admin Management"])

# Permission definitions
AVAILABLE_PERMISSIONS = {
    "all": "Full access to everything",
    "products": "Manage products (add, edit, delete)",
    "orders": "View and manage orders",
    "service_tickets": "Manage service tickets",
    "customers": "View and manage customers",
    "analytics": "View analytics and reports",
    "marketing": "Manage marketing campaigns",
    "inventory": "Manage inventory",
    "settings": "Manage system settings",
    "admins": "Manage other admins (requires super_admin)"
}

# Role definitions
ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full control + can manage other admins",
        "default_permissions": ["all"]
    },
    "admin": {
        "name": "Admin",
        "description": "Full control except admin management",
        "default_permissions": ["products", "orders", "service_tickets", "customers", "analytics", "marketing", "inventory", "settings"]
    },
    "accountant": {
        "name": "Accountant",
        "description": "Manage accounting, invoices, GST reports, and financial data",
        "default_permissions": ["orders", "analytics", "accounting", "gst_reports", "invoices", "purchase_bills"]
    },
    "marketing_head": {
        "name": "Marketing Head",
        "description": "Manage marketing campaigns, banners, promotions, and social media",
        "default_permissions": ["marketing", "analytics", "banners", "promotions", "social_media", "customers"]
    },
    "service_head": {
        "name": "Service Head",
        "description": "Manage service tickets, warranty, and customer support",
        "default_permissions": ["service_tickets", "customers", "orders", "analytics"]
    },
    "operations_manager": {
        "name": "Operations Manager",
        "description": "Manage inventory, deliveries, and stock transfers",
        "default_permissions": ["inventory", "orders", "deliveries", "stock_transfers", "analytics"]
    },
    "warehouse_manager": {
        "name": "Warehouse Manager",
        "description": "Manage warehouse inventory, challans, and deliveries",
        "default_permissions": ["inventory", "deliveries", "stock_transfers", "challans"]
    },
    "manager": {
        "name": "Manager",
        "description": "Manage operations (orders, tickets, customers)",
        "default_permissions": ["orders", "service_tickets", "customers", "analytics"]
    },
    "support": {
        "name": "Support Staff",
        "description": "Handle customer support and service tickets",
        "default_permissions": ["service_tickets", "customers", "orders"]
    },
    "content_manager": {
        "name": "Content Manager",
        "description": "Manage products and marketing only",
        "default_permissions": ["products", "marketing", "inventory"]
    }
}

def simple_hash(password: str) -> str:
    """Simple SHA256 password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

class CreateAdminRequest(BaseModel):
    email: Optional[str] = None  # Made optional
    username: Optional[str] = None  # Alternative to email
    name: str
    phone: Optional[str] = None
    password: str
    role: str  # super_admin, admin, manager, support, content_manager, accountant, etc.
    # Granular per-module permissions: {module_id: [permission, ...]}.
    # Frontend sends this as a dict matching PERMISSION_MODULES structure.
    custom_permissions: Optional[Dict[str, List[str]]] = None
    use_custom_permissions: Optional[bool] = False

class UpdateAdminRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None
    is_active: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    admin_id: str
    new_password: str

# Dependency to verify super admin
async def verify_super_admin(db = Depends(get_db)):
    # In production, this should extract from JWT token
    # For now, we'll check if the request has admin privileges
    # This is a simplified version - you should implement proper JWT verification
    return db

@router.get("/permissions")
async def get_available_permissions():
    """Get list of all available permissions"""
    return {
        "status": "success",
        "permissions": AVAILABLE_PERMISSIONS
    }

@router.get("/roles")
async def get_available_roles():
    """Get list of all available roles with their permissions"""
    return {
        "status": "success",
        "roles": ROLES
    }

@router.post("/admins")
async def create_admin(
    admin_data: CreateAdminRequest,
    db = Depends(verify_super_admin)
):
    """Create a new admin user (Super Admin only)"""
    try:
        # Validate role: accept legacy ROLES, built-in ROLE_TEMPLATES, and
        # any custom role template stored in the DB.
        valid_role = admin_data.role in ROLES or admin_data.role in ROLE_TEMPLATES
        if not valid_role:
            custom = await db.role_templates.find_one({"id": admin_data.role})
            valid_role = custom is not None
        if not valid_role:
            all_valid = list(ROLES.keys()) + list(ROLE_TEMPLATES.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role '{admin_data.role}'. Choose from: {', '.join(all_valid)}"
            )
        
        # Must have either email, username, or phone
        if not admin_data.email and not admin_data.username and not admin_data.phone:
            raise HTTPException(
                status_code=400, 
                detail="At least one of email, username, or phone is required"
            )
        
        # Generate username if not provided
        username = admin_data.username
        if not username:
            if admin_data.email:
                username = admin_data.email.split('@')[0].lower()
            else:
                # Generate from name
                username = admin_data.name.lower().replace(' ', '_')
        
        # Check for existing user with same email, username, or phone
        existing_query = {"$or": []}
        if admin_data.email:
            existing_query["$or"].append({"email": admin_data.email.lower()})
        if username:
            existing_query["$or"].append({"username": username.lower()})
        if admin_data.phone:
            existing_query["$or"].append({"phone": admin_data.phone})
        
        if existing_query["$or"]:
            existing = await db.admins.find_one(existing_query)
            if existing:
                conflict = []
                if admin_data.email and existing.get("email") == admin_data.email.lower():
                    conflict.append("email")
                if existing.get("username") == username.lower():
                    conflict.append("username")
                if admin_data.phone and existing.get("phone") == admin_data.phone:
                    conflict.append("phone")
                raise HTTPException(
                    status_code=400, 
                    detail=f"User with this {'/'.join(conflict)} already exists"
                )
        
        # Determine permissions:
        # - If the admin explicitly opted into custom permissions, honor that
        #   payload (even if empty) so they can restrict a user to zero modules.
        # - If custom_permissions provided, use those.
        # - Otherwise fall back to the role's defaults (ROLES → ROLE_TEMPLATES → DB custom).
        if admin_data.use_custom_permissions:
            permissions = admin_data.custom_permissions or {}
        elif admin_data.custom_permissions:
            permissions = admin_data.custom_permissions
        elif admin_data.role in ROLES:
            permissions = ROLES[admin_data.role]["default_permissions"]
        elif admin_data.role in ROLE_TEMPLATES:
            permissions = ROLE_TEMPLATES[admin_data.role].get("permissions", {})
        else:
            custom_tmpl = await db.role_templates.find_one({"id": admin_data.role}, {"_id": 0})
            permissions = (custom_tmpl or {}).get("permissions", {})
        
        # Create admin document
        admin_doc = {
            "id": str(uuid.uuid4()),
            "username": username.lower(),
            "email": admin_data.email.lower() if admin_data.email else None,
            "phone": admin_data.phone,
            "password": simple_hash(admin_data.password),
            "name": admin_data.name,
            "role": admin_data.role,
            "permissions": permissions,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "super_admin"  # In production, get from JWT
        }
        
        await db.admins.insert_one(admin_doc)
        
        # Remove password from response
        admin_doc.pop("password")
        admin_doc.pop("_id", None)
        
        login_info = username
        if admin_data.email:
            login_info = f"{admin_data.email} or {username}"
        elif admin_data.phone:
            login_info = f"{username} or {admin_data.phone}"
        
        return {
            "status": "success",
            "message": f"User '{admin_data.name}' created successfully. Login with: {login_info}",
            "admin": admin_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")

@router.get("/admins")
async def list_admins(db = Depends(verify_super_admin)):
    """List all admin users (Super Admin only)"""
    try:
        admins = await db.admins.find({}, {"_id": 0, "password": 0}).to_list(100)
        
        return {
            "status": "success",
            "total": len(admins),
            "admins": admins
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admins: {str(e)}")

@router.get("/admins/{admin_id}")
async def get_admin(admin_id: str, db = Depends(verify_super_admin)):
    """Get specific admin details"""
    try:
        admin = await db.admins.find_one({"id": admin_id}, {"_id": 0, "password": 0})
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return {
            "status": "success",
            "admin": admin
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admin: {str(e)}")

@router.put("/admins/{admin_id}")
async def update_admin(
    admin_id: str,
    update_data: UpdateAdminRequest,
    db = Depends(verify_super_admin)
):
    """Update admin user details (Super Admin only)"""
    try:
        # Check if admin exists
        admin = await db.admins.find_one({"id": admin_id})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Prepare update
        update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if update_data.name:
            update_fields["name"] = update_data.name
        
        if update_data.role:
            if update_data.role not in ROLES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid role. Choose from: {', '.join(ROLES.keys())}"
                )
            update_fields["role"] = update_data.role
            # Update permissions based on new role if not custom
            if not update_data.permissions:
                update_fields["permissions"] = ROLES[update_data.role]["default_permissions"]
        
        if update_data.permissions:
            update_fields["permissions"] = update_data.permissions
        
        if update_data.is_active is not None:
            update_fields["is_active"] = update_data.is_active
        
        # Update admin
        await db.admins.update_one(
            {"id": admin_id},
            {"$set": update_fields}
        )
        
        # Get updated admin
        updated_admin = await db.admins.find_one({"id": admin_id}, {"_id": 0, "password": 0})
        
        return {
            "status": "success",
            "message": "Admin updated successfully",
            "admin": updated_admin
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating admin: {str(e)}")

@router.post("/admins/change-password")
async def change_admin_password(
    password_data: ChangePasswordRequest,
    db = Depends(verify_super_admin)
):
    """Change admin password (Super Admin only)"""
    try:
        # Check if admin exists
        admin = await db.admins.find_one({"id": password_data.admin_id})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Update password
        await db.admins.update_one(
            {"id": password_data.admin_id},
            {"$set": {
                "password": simple_hash(password_data.new_password),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@router.delete("/admins/{admin_id}")
async def delete_admin(admin_id: str, db = Depends(verify_super_admin)):
    """Delete admin user (Super Admin only)"""
    try:
        # Check if admin exists
        admin = await db.admins.find_one({"id": admin_id})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Prevent deleting super admin
        if admin.get("role") == "super_admin":
            raise HTTPException(status_code=403, detail="Cannot delete super admin")
        
        # Delete admin
        await db.admins.delete_one({"id": admin_id})
        
        return {
            "status": "success",
            "message": "Admin deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting admin: {str(e)}")

@router.get("/roles/templates")
async def get_role_templates(db = Depends(verify_super_admin)):
    """Get all role templates (built-in + user-defined custom roles)."""
    # Load custom roles saved by admins into MongoDB
    custom = await db.role_templates.find({}, {"_id": 0}).to_list(200)
    custom_map = {
        c["id"]: {
            "name": c.get("name", c["id"]),
            "level": c.get("level", "manager"),
            "description": c.get("description", "Custom role"),
            "permissions": c.get("permissions", {}),
            "is_custom": True,
        }
        for c in custom if c.get("id")
    }
    # Merge — custom roles overlay built-in only if id collides (rare)
    merged = {**ROLE_TEMPLATES, **custom_map}
    return {
        "status": "success",
        "templates": merged
    }

class CustomRoleRequest(BaseModel):
    id: str  # slug-like role id, e.g. "delivery_manager"
    name: str
    level: Optional[str] = "manager"
    description: Optional[str] = ""
    permissions: Dict[str, List[str]]

@router.post("/roles/templates")
async def save_custom_role_template(
    payload: CustomRoleRequest,
    db = Depends(verify_super_admin)
):
    """Create or update a custom role template (Super Admin only)."""
    role_id = payload.id.strip().lower().replace(" ", "_")
    if not role_id:
        raise HTTPException(status_code=400, detail="Role id is required")
    # Don't allow overwriting built-in templates
    if role_id in ROLE_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"'{role_id}' is a built-in role and cannot be overwritten. Choose a different id."
        )
    doc = {
        "id": role_id,
        "name": payload.name,
        "level": payload.level or "manager",
        "description": payload.description or "",
        "permissions": payload.permissions,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.role_templates.update_one(
        {"id": role_id},
        {"$set": doc},
        upsert=True
    )
    return {
        "status": "success",
        "message": f"Custom role '{payload.name}' saved",
        "template": doc
    }

@router.delete("/roles/templates/{role_id}")
async def delete_custom_role_template(
    role_id: str,
    db = Depends(verify_super_admin)
):
    """Delete a custom role template. Built-in templates cannot be deleted."""
    if role_id in ROLE_TEMPLATES:
        raise HTTPException(status_code=400, detail="Built-in roles cannot be deleted")
    result = await db.role_templates.delete_one({"id": role_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Custom role not found")
    return {"status": "success", "message": f"Custom role '{role_id}' deleted"}

@router.get("/roles/by-level")
async def get_roles_by_level_endpoint():
    """Get roles grouped by level (admin, manager, staff)"""
    return {
        "status": "success",
        "roles": get_roles_by_level()
    }

@router.get("/permissions/modules")
async def get_permission_modules():
    """Get all available permission modules"""
    return {
        "status": "success",
        "modules": PERMISSION_MODULES
    }

@router.get("/permissions/by-category")
async def get_permissions_by_category():
    """Get permission modules grouped by category"""
    return {
        "status": "success",
        "categories": get_modules_by_category()
    }

@router.post("/admins/custom-role")
async def create_admin_with_custom_role(
    admin_data: Dict[str, Any],
    db = Depends(verify_super_admin)
):
    """Create admin with custom role and permissions"""
    try:
        # Validate required fields
        required_fields = ["email", "password", "name", "role", "permissions"]
        for field in required_fields:
            if field not in admin_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Check if admin already exists
        existing = await db.admins.find_one({"email": admin_data["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Admin with this email already exists")
        
        # Create admin
        admin = {
            "id": str(uuid.uuid4()),
            "email": admin_data["email"],
            "password": simple_hash(admin_data["password"]),
            "name": admin_data["name"],
            "role": admin_data["role"],
            "custom_permissions": admin_data["permissions"],  # Store custom permissions
            "is_active": admin_data.get("is_active", True),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.admins.insert_one(admin)
        
        # Return without password
        admin.pop("password")
        admin.pop("_id", None)
        
        return {
            "status": "success",
            "message": "Admin created successfully with custom permissions",
            "admin": admin
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")

        return {
            "status": "success",
            "message": f"Admin {admin.get('email')} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting admin: {str(e)}")

@router.get("/check-permission/{permission}")
async def check_permission_endpoint(permission: str, admin_id: str, db = Depends(get_db)):
    """Check if an admin has a specific permission"""
    try:
        admin = await db.admins.find_one({"id": admin_id}, {"_id": 0})
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        permissions = admin.get("permissions", [])
        has_permission = "all" in permissions or permission in permissions
        
        return {
            "status": "success",
            "admin_id": admin_id,
            "permission": permission,
            "has_permission": has_permission,
            "admin_permissions": permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking permission: {str(e)}")


# ============ CUSTOM ROLES ENDPOINTS ============

class CustomRoleRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    level: str = "staff"  # admin, manager, staff
    permissions: Dict[str, List[str]] = {}

@router.get("/custom-roles")
async def get_custom_roles(db = Depends(get_db)):
    """Get all custom roles"""
    try:
        roles = await db.custom_roles.find({}, {"_id": 0}).to_list(None)
        return {
            "status": "success",
            "roles": roles or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom-roles")
async def create_custom_role(role_data: CustomRoleRequest, db = Depends(get_db)):
    """Create a new custom role"""
    try:
        # Generate role ID from name
        role_id = role_data.name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if role already exists
        existing = await db.custom_roles.find_one({"id": role_id})
        if existing:
            raise HTTPException(status_code=400, detail="Role with this name already exists")
        
        # Also check built-in roles
        if role_id in ROLE_TEMPLATES:
            raise HTTPException(status_code=400, detail="Cannot use a built-in role name")
        
        custom_role = {
            "id": role_id,
            "name": role_data.name,
            "description": role_data.description,
            "level": role_data.level,
            "permissions": role_data.permissions,
            "is_custom": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.custom_roles.insert_one(custom_role)
        custom_role.pop("_id", None)
        
        return {
            "status": "success",
            "message": f"Custom role '{role_data.name}' created successfully",
            "role": custom_role
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/custom-roles/{role_id}")
async def update_custom_role(role_id: str, role_data: CustomRoleRequest, db = Depends(get_db)):
    """Update a custom role"""
    try:
        existing = await db.custom_roles.find_one({"id": role_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Custom role not found")
        
        update_fields = {
            "name": role_data.name,
            "description": role_data.description,
            "level": role_data.level,
            "permissions": role_data.permissions,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.custom_roles.update_one({"id": role_id}, {"$set": update_fields})
        
        return {
            "status": "success",
            "message": "Custom role updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/custom-roles/{role_id}")
async def delete_custom_role(role_id: str, db = Depends(get_db)):
    """Delete a custom role"""
    try:
        # Check if any users are using this role
        users_with_role = await db.store_users.count_documents({"role": role_id})
        if users_with_role > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete role. {users_with_role} user(s) are assigned this role."
            )
        
        result = await db.custom_roles.delete_one({"id": role_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Custom role not found")
        
        return {
            "status": "success",
            "message": "Custom role deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
