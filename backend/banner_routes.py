"""
Dynamic Banner Management
Upload and manage homepage banners for promotions, sales, new products
Includes AI-powered banner image generation via OpenAI GPT Image 1
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
import shutil
import base64
from dotenv import load_dotenv
from database import get_db
from file_storage import save_upload, serve_upload

load_dotenv()

router = APIRouter(prefix="/banners", tags=["Banners"])

class BannerCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = ""
    link_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    banner_type: str = "promotional"  # promotional, sale, new_product, seasonal
    link_type: Optional[str] = "custom"  # brand, category, product, offer, custom
    link_value: Optional[str] = None

class AIBannerRequest(BaseModel):
    prompt: str
    banner_type: str = "promotional"
    style: str = "modern"  # modern, minimal, bold, elegant

@router.post("/generate-ai")
async def generate_ai_banner(request: AIBannerRequest):
    """Generate a banner image using AI (OpenAI GPT Image 1)"""
    try:
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

        # Build an optimized prompt for banner generation
        full_prompt = (
            f"Create a professional, high-quality e-commerce website banner image. "
            f"Style: {request.style}, clean and modern design suitable for a premium home appliances retail store. "
            f"The banner should be visually striking with good contrast for text overlay. "
            f"Content: {request.prompt}. "
            f"Important: This is a BANNER IMAGE only — do NOT include any text, words, letters, or typography in the image. "
            f"Focus on product imagery, lifestyle photography, and visual atmosphere. "
            f"Aspect ratio: wide landscape format for a website hero banner."
        )

        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=full_prompt,
            model="gpt-image-1",
            number_of_images=1
        )

        if not images or len(images) == 0:
            raise HTTPException(status_code=500, detail="No image was generated")

        # Save to GridFS so it survives redeploys
        unique_filename = f"ai_banner_{uuid.uuid4().hex[:8]}.png"
        await save_upload(unique_filename, images[0], "image/png")
        image_url = f"/api/banners/image/{unique_filename}"
        image_base64 = base64.b64encode(images[0]).decode("utf-8")

        return {
            "status": "success",
            "image_url": image_url,
            "image_base64": image_base64,
            "prompt_used": full_prompt
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/upload")
async def upload_banner_image(file: UploadFile = File(...)):
    """Upload banner image"""
    try:
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, WEBP allowed")
        
        # Generate unique filename
        unique_filename = f"banner_{uuid.uuid4().hex[:8]}{file_extension}"
        mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}[file_extension]
        content = await file.read()
        await save_upload(unique_filename, content, mime)
        
        return {
            "status": "success",
            "filename": unique_filename,
            "url": f"/api/banners/image/{unique_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading banner: {str(e)}")


@router.get("/image/{filename}")
async def get_banner_image(filename: str):
    return await serve_upload(filename)

@router.post("/")
async def create_banner(banner: BannerCreate, db = Depends(get_db)):
    """Create a new banner entry"""
    try:
        banner_doc = {
            "id": str(uuid.uuid4()),
            "title": banner.title,
            "description": banner.description,
            "image_url": banner.image_url or "",
            "link_url": banner.link_url,
            "link_type": banner.link_type,
            "link_value": banner.link_value,
            "display_order": banner.display_order,
            "is_active": banner.is_active,
            "valid_from": banner.valid_from or datetime.now(timezone.utc).isoformat(),
            "valid_until": banner.valid_until,
            "banner_type": banner.banner_type,
            "views": 0,
            "clicks": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.banners.insert_one(banner_doc)
        
        # Remove _id from response
        banner_doc.pop('_id', None)
        
        return {
            "status": "success",
            "message": "Banner created successfully",
            "banner": banner_doc
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating banner: {str(e)}")

@router.get("/")
async def get_banners(active_only: bool = False, db = Depends(get_db)):
    """Get all banners"""
    try:
        query = {}
        if active_only:
            query["is_active"] = True
            current_date = datetime.now(timezone.utc).isoformat()
            query["valid_from"] = {"$lte": current_date}
            # Only include if valid_until is not set or is in the future
            query["$or"] = [
                {"valid_until": None},
                {"valid_until": {"$gte": current_date}}
            ]
        
        banners = await db.banners.find(query, {"_id": 0}).sort([("display_order", 1), ("created_at", -1)]).to_list(100)
        
        return {
            "status": "success",
            "total": len(banners),
            "banners": banners
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching banners: {str(e)}")

@router.get("/active/homepage")
async def get_active_homepage_banners(db = Depends(get_db)):
    """Get active banners for homepage display"""
    try:
        current_date = datetime.now(timezone.utc).isoformat()
        
        banners = await db.banners.find({
            "is_active": True,
            "valid_from": {"$lte": current_date},
            "$or": [
                {"valid_until": None},
                {"valid_until": {"$gte": current_date}}
            ]
        }, {"_id": 0}).sort([("display_order", 1)]).limit(10).to_list(10)
        
        return {
            "status": "success",
            "total": len(banners),
            "banners": banners
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active banners: {str(e)}")

@router.put("/{banner_id}")
async def update_banner(banner_id: str, updates: dict, db = Depends(get_db)):
    """Update banner"""
    try:
        banner = await db.banners.find_one({"id": banner_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")
        
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.banners.update_one(
            {"id": banner_id},
            {"$set": updates}
        )
        
        updated_banner = await db.banners.find_one({"id": banner_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Banner updated successfully",
            "banner": updated_banner
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating banner: {str(e)}")

@router.delete("/{banner_id}")
async def delete_banner(banner_id: str, db = Depends(get_db)):
    """Delete banner"""
    try:
        banner = await db.banners.find_one({"id": banner_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")
        
        # Soft delete
        await db.banners.update_one(
            {"id": banner_id},
            {"$set": {
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": "success",
            "message": "Banner deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting banner: {str(e)}")

@router.post("/{banner_id}/track-view")
async def track_banner_view(banner_id: str, db = Depends(get_db)):
    """Track banner view"""
    try:
        await db.banners.update_one(
            {"id": banner_id},
            {"$inc": {"views": 1}}
        )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking view: {str(e)}")

@router.post("/{banner_id}/track-click")
async def track_banner_click(banner_id: str, db = Depends(get_db)):
    """Track banner click"""
    try:
        await db.banners.update_one(
            {"id": banner_id},
            {"$inc": {"clicks": 1}}
        )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking click: {str(e)}")
