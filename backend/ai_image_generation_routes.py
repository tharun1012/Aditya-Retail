"""
AI Image Generation for Social Media
Uses OpenAI gpt-image-1 with Emergent LLM Key
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import os
import base64
from datetime import datetime, timezone
from database import get_db
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ai-image-generation", tags=["AI Image Generation"])

class SocialMediaImageRequest(BaseModel):
    product_id: Optional[str] = None
    post_text: str
    platform: str  # instagram, facebook, twitter, linkedin
    style: str = "professional"  # professional, vibrant, minimal, festive, modern
    include_product_image: bool = True
    brand_colors: Optional[List[str]] = ["#2563eb", "#ffffff"]  # Default blue & white
    offer_text: Optional[str] = None

@router.post("/generate-social-image")
async def generate_social_media_image(request: SocialMediaImageRequest, db = Depends(get_db)):
    """
    Generate AI-powered social media graphics using OpenAI gpt-image-1
    """
    try:
        # Get Emergent LLM Key
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")
        
        # Get product details if product_id provided
        product = None
        if request.product_id:
            product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
        
        # Determine image dimensions based on platform
        dimensions = {
            "instagram": "1080x1080",  # Square
            "facebook": "1200x630",    # Landscape
            "twitter": "1200x675",     # 16:9
            "linkedin": "1200x627"     # Landscape
        }
        
        size = dimensions.get(request.platform, "1080x1080")
        
        # Build the prompt for image generation
        prompt = build_image_prompt(
            product=product,
            post_text=request.post_text,
            style=request.style,
            offer_text=request.offer_text,
            platform=request.platform
        )
        
        print(f"[AI Image Gen] Prompt: {prompt[:200]}...")
        
        # Use LiteLLM directly with Emergent proxy for image generation
        try:
            import litellm
            
            # Set API key
            litellm.api_key = api_key
            
            # For Emergent keys, use the proxy
            if api_key.startswith('sk-emergent'):
                api_base = "https://llm.kindo.ai"
            else:
                api_base = None
            
            # Generate image using litellm
            response = await litellm.aimage_generation(
                model="gpt-image-1",
                prompt=prompt,
                api_key=api_key,
                api_base=api_base,
                n=1
            )
            
            # Extract image URL or base64
            if response and hasattr(response, 'data') and len(response.data) > 0:
                image_data = response.data[0]
                
                # Check if we have URL or b64_json
                if hasattr(image_data, 'url') and image_data.url:
                    image_url = image_data.url
                elif hasattr(image_data, 'b64_json') and image_data.b64_json:
                    image_url = f"data:image/png;base64,{image_data.b64_json}"
                else:
                    raise HTTPException(status_code=500, detail="No image URL or data in response")
            else:
                raise HTTPException(status_code=500, detail="No image generated")
                
        except Exception as litellm_error:
            print(f"[AI Image Gen] LiteLLM Error: {str(litellm_error)}")
            raise HTTPException(status_code=500, detail=f"Image generation failed: {str(litellm_error)}")
        
        # Save to database
        image_doc = {
            "product_id": request.product_id,
            "post_text": request.post_text,
            "platform": request.platform,
            "style": request.style,
            "image_url": image_url,
            "prompt": prompt,
            "size": size,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.social_media_images.insert_one(image_doc)
        
        return {
            "status": "success",
            "message": "Social media image generated successfully",
            "image_url": image_url,
            "size": size,
            "platform": request.platform
        }
        
    except Exception as e:
        print(f"[AI Image Gen Error] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

def build_image_prompt(product, post_text, style, offer_text, platform):
    """Build detailed prompt for image generation"""
    
    # Base style descriptions
    style_descriptions = {
        "professional": "clean, professional, high-end photography, studio lighting, white or minimal background",
        "vibrant": "colorful, energetic, bold colors, dynamic composition, eye-catching gradients",
        "minimal": "minimalist design, lots of white space, simple geometric shapes, modern and elegant",
        "festive": "celebratory, festive colors, decorative elements, joyful atmosphere, seasonal theme",
        "modern": "contemporary, sleek design, gradient backgrounds, abstract shapes, trendy aesthetics"
    }
    
    style_desc = style_descriptions.get(style, style_descriptions["professional"])
    
    # Platform-specific requirements
    platform_notes = {
        "instagram": "Instagram post format, engaging and visually appealing for social feed",
        "facebook": "Facebook cover format, attention-grabbing for timeline",
        "twitter": "Twitter header format, concise and impactful",
        "linkedin": "LinkedIn professional format, business-appropriate and credible"
    }
    
    platform_note = platform_notes.get(platform, "")
    
    # Build prompt
    if product:
        prompt = f"""
Create a high-quality social media marketing image for {platform}.

Product: {product.get('name', 'Premium Home Appliance')}
Brand: {product.get('brand', 'Premium Brand')}
Category: {product.get('category', 'Home Appliance')}

Marketing Message: {post_text}

{f"Special Offer: {offer_text}" if offer_text else ""}

Style: {style_desc}

Requirements:
- {platform_note}
- Include the product as the main focal point
- Modern e-commerce aesthetic
- Clean and professional design
- {f"Highlight the offer: {offer_text}" if offer_text else "Emphasize premium quality"}
- Add subtle branding elements
- Make it scroll-stopping and eye-catching
- Photorealistic product rendering
- Proper lighting and shadows
- High resolution and sharp details

Do not include any text or words in the image. Pure visual design only.
"""
    else:
        prompt = f"""
Create a high-quality social media marketing image for {platform}.

Marketing Message: {post_text}

{f"Special Offer: {offer_text}" if offer_text else ""}

Style: {style_desc}

Requirements:
- {platform_note}
- Abstract or conceptual design representing home appliances/lifestyle
- Modern e-commerce aesthetic
- {f"Visually represent the offer: {offer_text}" if offer_text else "Premium and aspirational feel"}
- Eye-catching and engaging
- Professional and polished
- Make it scroll-stopping

Do not include any text or words in the image. Pure visual design only.
"""
    
    return prompt.strip()

@router.get("/history")
async def get_generated_images(limit: int = 50, db = Depends(get_db)):
    """Get history of generated images"""
    try:
        images = await db.social_media_images.find(
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

@router.delete("/{image_id}")
async def delete_generated_image(image_id: str, db = Depends(get_db)):
    """Delete a generated image"""
    try:
        result = await db.social_media_images.delete_one({"image_url": image_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return {
            "status": "success",
            "message": "Image deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
