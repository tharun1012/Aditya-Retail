from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from database import get_db

router = APIRouter(prefix="/settings", tags=["settings"])

class SiteSettings(BaseModel):
    site_name: Optional[str] = "Aditya Retail"
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    support_email: Optional[str] = None
    currency: Optional[str] = "INR"
    timezone: Optional[str] = "Asia/Kolkata"

class PaymentSettings(BaseModel):
    phonepe_enabled: Optional[bool] = True
    phonepe_merchant_id: Optional[str] = None
    cod_enabled: Optional[bool] = True
    cod_limit: Optional[float] = 50000

class ShippingSettings(BaseModel):
    free_shipping_threshold: Optional[float] = 5000
    standard_shipping_cost: Optional[float] = 0
    express_shipping_cost: Optional[float] = 200
    shiprocket_enabled: Optional[bool] = False

class TaxSettings(BaseModel):
    gst_enabled: Optional[bool] = True
    gst_rate: Optional[float] = 18.0
    cgst_rate: Optional[float] = 9.0
    sgst_rate: Optional[float] = 9.0

class EmailSettings(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = "Aditya Retail"

@router.get("/site")
async def get_site_settings(
    database = Depends(get_db)
):
    """Get site settings"""
    try:
        settings = await database.settings.find_one({"type": "site"})
        if not settings:
            # Return defaults
            return {
                "success": True,
                "data": {
                    "site_name": "Aditya Retail",
                    "site_description": "Premium Bosch & Siemens Products",
                    "contact_email": "contact@adityaretail.com",
                    "contact_phone": "+91 22 1234 5678",
                    "support_email": "support@adityaretail.com",
                    "currency": "INR",
                    "timezone": "Asia/Kolkata"
                }
            }
        
        if "_id" in settings:
            del settings["_id"]
        
        return {
            "success": True,
            "data": settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/site")
async def update_site_settings(
    settings: SiteSettings,
    database = Depends(get_db)
):
    """Update site settings"""
    try:
        settings_dict = settings.dict(exclude_none=True)
        settings_dict["type"] = "site"
        settings_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await database.settings.update_one(
            {"type": "site"},
            {"$set": settings_dict},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Site settings updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.get("/payment")
async def get_payment_settings(
    database = Depends(get_db)
):
    """Get payment settings"""
    try:
        settings = await database.settings.find_one({"type": "payment"})
        if not settings:
            return {
                "success": True,
                "data": {
                    "phonepe_enabled": True,
                    "phonepe_merchant_id": "M224EIU0W7NHS",
                    "cod_enabled": True,
                    "cod_limit": 50000
                }
            }
        
        if "_id" in settings:
            del settings["_id"]
        
        return {
            "success": True,
            "data": settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/payment")
async def update_payment_settings(
    settings: PaymentSettings,
    database = Depends(get_db)
):
    """Update payment settings"""
    try:
        settings_dict = settings.dict(exclude_none=True)
        settings_dict["type"] = "payment"
        settings_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await database.settings.update_one(
            {"type": "payment"},
            {"$set": settings_dict},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Payment settings updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.get("/shipping")
async def get_shipping_settings(
    database = Depends(get_db)
):
    """Get shipping settings"""
    try:
        settings = await database.settings.find_one({"type": "shipping"})
        if not settings:
            return {
                "success": True,
                "data": {
                    "free_shipping_threshold": 5000,
                    "standard_shipping_cost": 0,
                    "express_shipping_cost": 200,
                    "shiprocket_enabled": False
                }
            }
        
        if "_id" in settings:
            del settings["_id"]
        
        return {
            "success": True,
            "data": settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/shipping")
async def update_shipping_settings(
    settings: ShippingSettings,
    database = Depends(get_db)
):
    """Update shipping settings"""
    try:
        settings_dict = settings.dict(exclude_none=True)
        settings_dict["type"] = "shipping"
        settings_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await database.settings.update_one(
            {"type": "shipping"},
            {"$set": settings_dict},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Shipping settings updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.get("/tax")
async def get_tax_settings(
    database = Depends(get_db)
):
    """Get tax settings"""
    try:
        settings = await database.settings.find_one({"type": "tax"})
        if not settings:
            return {
                "success": True,
                "data": {
                    "gst_enabled": True,
                    "gst_rate": 18.0,
                    "cgst_rate": 9.0,
                    "sgst_rate": 9.0
                }
            }
        
        if "_id" in settings:
            del settings["_id"]
        
        return {
            "success": True,
            "data": settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/tax")
async def update_tax_settings(
    settings: TaxSettings,
    database = Depends(get_db)
):
    """Update tax settings"""
    try:
        settings_dict = settings.dict(exclude_none=True)
        settings_dict["type"] = "tax"
        settings_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await database.settings.update_one(
            {"type": "tax"},
            {"$set": settings_dict},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Tax settings updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.get("/email")
async def get_email_settings(
    database = Depends(get_db)
):
    """Get email settings (hide password)"""
    try:
        settings = await database.settings.find_one({"type": "email"})
        if not settings:
            return {
                "success": True,
                "data": {
                    "smtp_host": "",
                    "smtp_port": 587,
                    "smtp_username": "",
                    "from_email": "noreply@adityaretail.com",
                    "from_name": "Aditya Retail"
                }
            }
        
        if "_id" in settings:
            del settings["_id"]
        
        # Hide password
        if "smtp_password" in settings:
            settings["smtp_password"] = "********"
        
        return {
            "success": True,
            "data": settings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/email")
async def update_email_settings(
    settings: EmailSettings,
    database = Depends(get_db)
):
    """Update email settings"""
    try:
        settings_dict = settings.dict(exclude_none=True)
        settings_dict["type"] = "email"
        settings_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await database.settings.update_one(
            {"type": "email"},
            {"$set": settings_dict},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Email settings updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
