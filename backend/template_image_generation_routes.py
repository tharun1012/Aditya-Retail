"""
Template-Based Image Generation for Social Media
Uses Pillow to generate professional social media images
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from database import get_db
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO
import base64
import textwrap

router = APIRouter(prefix="/template-image-generation", tags=["Template Image Generation"])

class TemplateImageRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    product_price: Optional[float] = None
    product_mrp: Optional[float] = None
    product_image_url: str
    post_text: str
    platform: str  # instagram, facebook, twitter, linkedin
    template_style: str = "professional"  # professional, vibrant, minimal, festive, sale
    offer_text: Optional[str] = None
    brand_name: str = "Aditya Retail"
    brand_logo_url: Optional[str] = None

@router.post("/generate")
async def generate_template_image(request: TemplateImageRequest, db = Depends(get_db)):
    """
    Generate social media image using Pillow + product photo
    Returns base64 encoded image data URL
    """
    try:
        # Determine dimensions based on platform
        dimensions = {
            "instagram": {"width": 1080, "height": 1080, "name": "Instagram Square"},
            "facebook": {"width": 1200, "height": 630, "name": "Facebook Post"},
            "twitter": {"width": 1200, "height": 675, "name": "Twitter Post"},
            "linkedin": {"width": 1200, "height": 627, "name": "LinkedIn Post"}
        }
        
        platform_config = dimensions.get(request.platform, dimensions["instagram"])
        width = platform_config["width"]
        height = platform_config["height"]
        
        # Generate the image using Pillow
        image_data = await generate_social_media_image(
            width=width,
            height=height,
            product_name=request.product_name,
            product_price=request.product_price,
            product_mrp=request.product_mrp,
            product_image_url=request.product_image_url,
            post_text=request.post_text,
            offer_text=request.offer_text,
            brand_name=request.brand_name,
            template_style=request.template_style
        )
        
        # Convert to base64 for easy frontend usage
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        image_data_url = f"data:image/png;base64,{image_base64}"
        
        # Save generation record to database
        template_doc = {
            "product_id": request.product_id,
            "product_name": request.product_name,
            "post_text": request.post_text,
            "platform": request.platform,
            "template_style": request.template_style,
            "offer_text": request.offer_text,
            "product_image_url": request.product_image_url,
            "dimensions": platform_config,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.template_images.insert_one(template_doc)
        
        return {
            "status": "success",
            "message": "Social media image generated successfully",
            "image_url": image_data_url,
            "dimensions": platform_config
        }
        
    except Exception as e:
        print(f"[Template Image Gen Error] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")

async def generate_social_media_image(
    width: int,
    height: int,
    product_name: str,
    product_price: Optional[float],
    product_mrp: Optional[float],
    product_image_url: str,
    post_text: str,
    offer_text: Optional[str],
    brand_name: str,
    template_style: str
) -> bytes:
    """Generate social media image using Pillow"""
    
    # Style configurations
    style_configs = {
        "professional": {
            "bg_color": (255, 255, 255),
            "accent_color": (37, 99, 235),  # Blue
            "text_color": (31, 41, 55),
            "secondary_text": (107, 114, 128),
        },
        "vibrant": {
            "bg_color": (255, 107, 107),
            "accent_color": (254, 200, 74),  # Yellow
            "text_color": (255, 255, 255),
            "secondary_text": (243, 244, 246),
        },
        "minimal": {
            "bg_color": (249, 250, 251),
            "accent_color": (17, 24, 39),
            "text_color": (17, 24, 39),
            "secondary_text": (156, 163, 175),
        },
        "festive": {
            "bg_color": (255, 107, 157),
            "accent_color": (254, 200, 74),
            "text_color": (255, 255, 255),
            "secondary_text": (254, 243, 199),
        },
        "sale": {
            "bg_color": (220, 38, 38),  # Red
            "accent_color": (254, 240, 138),  # Yellow
            "text_color": (255, 255, 255),
            "secondary_text": (254, 226, 226),
        }
    }
    
    style = style_configs.get(template_style, style_configs["professional"])
    
    # Create base image
    img = Image.new('RGB', (width, height), color=style["bg_color"])
    draw = ImageDraw.Draw(img)
    
    # Try to load product image
    product_img = None
    try:
        response = requests.get(product_image_url, timeout=10)
        if response.status_code == 200:
            product_img = Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"[Image Gen] Failed to load product image: {e}")
    
    # Layout calculations
    margin = int(width * 0.05)
    
    # Add product image (top half)
    if product_img:
        # Calculate product image size (take 50% of height)
        img_height = int(height * 0.5)
        img_width = int(width * 0.8)
        
        # Resize product image maintaining aspect ratio
        product_img.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
        
        # Center the product image
        img_x = (width - product_img.width) // 2
        img_y = margin
        
        # Paste product image
        if product_img.mode == 'RGBA':
            img.paste(product_img, (img_x, img_y), product_img)
        else:
            img.paste(product_img, (img_x, img_y))
    
    # Text area starts below product image
    text_start_y = int(height * 0.55)
    
    # Load fonts (use default if custom not available)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(width * 0.04))
        price_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(width * 0.05))
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(width * 0.025))
        brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(width * 0.03))
        offer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(width * 0.045))
    except Exception:
        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()
        offer_font = ImageFont.load_default()
    
    # Draw product name (centered)
    name_lines = textwrap.wrap(product_name, width=30)
    current_y = text_start_y
    for line in name_lines[:2]:  # Max 2 lines
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, current_y), line, fill=style["text_color"], font=title_font)
        current_y += int(width * 0.05)
    
    # Draw price
    current_y += int(width * 0.02)
    if product_price:
        # Calculate discount
        discount_text = ""
        if product_mrp and product_mrp > product_price:
            discount_percent = int(((product_mrp - product_price) / product_mrp) * 100)
            discount_text = f"{discount_percent}% OFF"
        
        # Price text
        price_text = f"₹{int(product_price):,}"
        if product_mrp and product_mrp > product_price:
            price_text += f"  MRP: ₹{int(product_mrp):,}"
        
        bbox = draw.textbbox((0, 0), price_text, font=price_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, current_y), price_text, fill=style["accent_color"], font=price_font)
        
        # Strike through MRP if discount
        if product_mrp and product_mrp > product_price:
            mrp_text = f"₹{int(product_mrp):,}"
            mrp_start_x = x + draw.textbbox((0, 0), f"₹{int(product_price):,}  MRP: ", font=price_font)[2]
            mrp_width = draw.textbbox((0, 0), mrp_text, font=price_font)[2]
            draw.line([(mrp_start_x, current_y + int(width * 0.025)), 
                      (mrp_start_x + mrp_width, current_y + int(width * 0.025))], 
                      fill=style["secondary_text"], width=3)
        
        current_y += int(width * 0.06)
        
        # Discount badge
        if discount_text:
            bbox = draw.textbbox((0, 0), discount_text, font=offer_font)
            badge_width = bbox[2] - bbox[0] + int(width * 0.04)
            badge_height = bbox[3] - bbox[1] + int(width * 0.02)
            badge_x = (width - badge_width) // 2
            badge_y = current_y
            
            # Draw badge background
            draw.rounded_rectangle(
                [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
                radius=10,
                fill=style["accent_color"]
            )
            
            # Draw badge text
            text_x = badge_x + int(width * 0.02)
            text_y = badge_y + int(width * 0.01)
            draw.text((text_x, text_y), discount_text, fill=style["text_color"] if template_style == "minimal" else (255, 255, 255), font=offer_font)
            current_y += badge_height + int(width * 0.03)
    
    # Draw offer text if present
    if offer_text:
        current_y += int(width * 0.02)
        offer_lines = textwrap.wrap(offer_text, width=40)
        for line in offer_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=text_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, current_y), line, fill=style["secondary_text"], font=text_font)
            current_y += int(width * 0.03)
    
    # Draw brand name at bottom
    brand_y = height - int(width * 0.08)
    bbox = draw.textbbox((0, 0), brand_name, font=brand_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, brand_y), brand_name, fill=style["text_color"], font=brand_font)
    
    # Convert to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG', quality=95)
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def get_template_config(style, platform, product_name, product_price, product_mrp, post_text, offer_text, brand_name):
    """Generate template configuration based on style"""
    
    # Base colors and fonts for each style
    styles = {
        "professional": {
            "name": "Professional",
            "background": {"type": "solid", "color": "#FFFFFF"},
            "accent_color": "#2563EB",
            "text_color": "#1F2937",
            "secondary_text": "#6B7280",
            "font_primary": "Inter, sans-serif",
            "font_secondary": "Georgia, serif",
            "overlay_opacity": 0.95,
            "border_radius": 8,
            "shadow": "0 4px 12px rgba(0,0,0,0.1)"
        },
        "vibrant": {
            "name": "Vibrant",
            "background": {"type": "gradient", "colors": ["#FF6B6B", "#FEC84A", "#FF6B6B"]},
            "accent_color": "#FFFFFF",
            "text_color": "#FFFFFF",
            "secondary_text": "#F3F4F6",
            "font_primary": "Poppins, sans-serif",
            "font_secondary": "Poppins, sans-serif",
            "overlay_opacity": 0.9,
            "border_radius": 16,
            "shadow": "0 8px 24px rgba(0,0,0,0.2)"
        },
        "minimal": {
            "name": "Minimal",
            "background": {"type": "solid", "color": "#F9FAFB"},
            "accent_color": "#111827",
            "text_color": "#111827",
            "secondary_text": "#9CA3AF",
            "font_primary": "Helvetica, Arial, sans-serif",
            "font_secondary": "Helvetica, Arial, sans-serif",
            "overlay_opacity": 0.98,
            "border_radius": 4,
            "shadow": "none"
        },
        "festive": {
            "name": "Festive",
            "background": {"type": "gradient", "colors": ["#FF6B9D", "#C084FC", "#FEC84A"]},
            "accent_color": "#FFFFFF",
            "text_color": "#FFFFFF",
            "secondary_text": "#FEF3C7",
            "font_primary": "Comic Sans MS, cursive",
            "font_secondary": "Comic Sans MS, cursive",
            "overlay_opacity": 0.85,
            "border_radius": 20,
            "shadow": "0 8px 32px rgba(0,0,0,0.3)"
        },
        "sale": {
            "name": "Sale Banner",
            "background": {"type": "solid", "color": "#DC2626"},
            "accent_color": "#FEF08A",
            "text_color": "#FFFFFF",
            "secondary_text": "#FEE2E2",
            "font_primary": "Impact, sans-serif",
            "font_secondary": "Arial, sans-serif",
            "overlay_opacity": 0.95,
            "border_radius": 12,
            "shadow": "0 10px 40px rgba(220,38,38,0.4)"
        }
    }
    
    style_config = styles.get(style, styles["professional"])
    
    # Calculate discount if both prices available
    discount_percent = 0
    if product_mrp and product_price and product_mrp > product_price:
        discount_percent = round(((product_mrp - product_price) / product_mrp) * 100)
    
    # Build template configuration
    config = {
        "style": style_config,
        "layout": {
            "product_image_area": {"top": "10%", "left": "10%", "width": "80%", "height": "50%"},
            "text_area": {"top": "65%", "left": "5%", "width": "90%", "height": "30%"},
            "brand_area": {"bottom": "3%", "right": "5%", "width": "20%", "height": "5%"}
        },
        "content": {
            "product_name": product_name[:50],  # Truncate if too long
            "product_price": f"₹{int(product_price):,}" if product_price else None,
            "product_mrp": f"₹{int(product_mrp):,}" if product_mrp else None,
            "discount_percent": discount_percent if discount_percent > 0 else None,
            "post_text": post_text[:100],  # Truncate if too long
            "offer_text": offer_text[:80] if offer_text else None,
            "brand_name": brand_name
        },
        "effects": {
            "show_discount_badge": discount_percent > 0,
            "show_offer_banner": bool(offer_text),
            "show_price_strikethrough": product_mrp and product_price and product_mrp > product_price
        }
    }
    
    return config

@router.get("/history")
async def get_template_history(limit: int = 50, db = Depends(get_db)):
    """Get history of generated template images"""
    try:
        images = await db.template_images.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {
            "status": "success",
            "images": images,
            "total": len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_available_templates():
    """Get list of available template styles"""
    templates = [
        {
            "id": "professional",
            "name": "Professional",
            "description": "Clean, corporate design with white background",
            "best_for": "B2B, Premium products, Corporate posts"
        },
        {
            "id": "vibrant",
            "name": "Vibrant",
            "description": "Bold colors and eye-catching gradients",
            "best_for": "Sales, Promotions, Youth audience"
        },
        {
            "id": "minimal",
            "name": "Minimal",
            "description": "Simple, elegant with lots of white space",
            "best_for": "Luxury products, Modern brands"
        },
        {
            "id": "festive",
            "name": "Festive",
            "description": "Colorful, celebratory design",
            "best_for": "Festivals, Special occasions, Celebrations"
        },
        {
            "id": "sale",
            "name": "Sale Banner",
            "description": "Bold red with strong discount emphasis",
            "best_for": "Flash sales, Limited offers, Clearance"
        }
    ]
    
    return {
        "status": "success",
        "templates": templates
    }
