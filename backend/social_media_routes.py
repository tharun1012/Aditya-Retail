"""
Social Media Post Creator
Generate posts for manual posting on social media platforms
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from database import get_db
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import base64
import requests

router = APIRouter(prefix="/social-media", tags=["Social Media"])

class PostCreate(BaseModel):
    post_type: str  # 'product', 'offer', 'testimonial', 'educational', 'festival'
    platform: str  # 'facebook', 'instagram', 'linkedin', 'twitter', 'all'
    content_type: str  # 'sale', 'new_product', 'combo_offer', 'seasonal', 'custom'
    product_ids: Optional[List[str]] = []
    offer_details: Optional[str] = None
    custom_message: Optional[str] = None
    hashtags: Optional[List[str]] = []

@router.post("/generate-post")
async def generate_social_media_post(data: PostCreate, db = Depends(get_db)):
    """Generate AI-powered social media post"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Get product details if product_ids provided
        products = []
        if data.product_ids:
            for product_id in data.product_ids:
                product = await db.products.find_one({"id": product_id}, {"_id": 0})
                if product:
                    products.append(product)
        
        # Build context for AI
        context = f"""Create a {data.platform} post for {data.content_type}.

Post Type: {data.post_type}
Platform: {data.platform}
"""
        
        if products:
            context += "\n\nProducts:\n"
            for p in products:
                context += f"- {p.get('name')} by {p.get('brand')} - Rs. {p.get('price')}\n"
        
        if data.offer_details:
            context += f"\n\nOffer Details: {data.offer_details}\n"
        
        if data.custom_message:
            context += f"\n\nCustom Message: {data.custom_message}\n"
        
        # Platform-specific guidelines
        platform_guidelines = {
            "facebook": "Create engaging post (150-200 words). Use emojis, ask questions to encourage engagement. Casual yet professional tone.",
            "instagram": "Create short, catchy caption (100-150 words). Use 15-20 relevant hashtags. Include call-to-action. Very visual and trendy language.",
            "linkedin": "Create professional post (200-300 words). Focus on business value, features, and benefits. Formal tone. 3-5 professional hashtags.",
            "twitter": "Create concise post (250 characters max). Punchy, attention-grabbing. 2-3 hashtags. Include call-to-action.",
            "all": "Create versatile post that works across all platforms (150-200 words). Balance between casual and professional."
        }
        
        context += f"\n\n{platform_guidelines.get(data.platform, platform_guidelines['all'])}\n"
        
        # Generate post using AI
        chat = LlmChat(
            api_key=api_key,
            session_id=f"social_post_{datetime.now().timestamp()}",
            system_message="You are a social media marketing expert who creates engaging posts for home appliance brands."
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = f"""{context}

Generate:
1. Post caption/text
2. Suggested hashtags (if not for LinkedIn)
3. Call-to-action
4. Best time to post

Format as JSON:
{{
    "caption": "...",
    "hashtags": ["hashtag1", "hashtag2"],
    "cta": "...",
    "best_time": "..."
}}
"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Extract JSON from response
        import json
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            generated_content = json.loads(json_str)
        else:
            # Fallback if JSON parsing fails
            generated_content = {
                "caption": response,
                "hashtags": data.hashtags or [],
                "cta": "Visit our store or website!",
                "best_time": "10 AM - 2 PM or 6 PM - 9 PM"
            }
        
        # Save post to database
        post_doc = {
            "id": str(uuid.uuid4()),
            "post_type": data.post_type,
            "platform": data.platform,
            "content_type": data.content_type,
            "caption": generated_content.get("caption", ""),
            "hashtags": generated_content.get("hashtags", []),
            "cta": generated_content.get("cta", ""),
            "best_time": generated_content.get("best_time", ""),
            "product_ids": data.product_ids,
            "products": products,
            "offer_details": data.offer_details,
            "status": "draft",  # draft, scheduled, posted
            "posted_at": None,
            "engagement": {
                "likes": 0,
                "comments": 0,
                "shares": 0
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.social_media_posts.insert_one(post_doc)
        
        # Remove _id from response
        post_doc.pop('_id', None)
        
        return {
            "status": "success",
            "message": "Social media post generated successfully",
            "post": post_doc
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating post: {str(e)}")

@router.get("/posts")
async def get_social_media_posts(status: Optional[str] = None, db = Depends(get_db)):
    """Get all social media posts"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        posts = await db.social_media_posts.find(query, {"_id": 0}).sort([("created_at", -1)]).limit(50).to_list(50)
        
        return {
            "status": "success",
            "total": len(posts),
            "posts": posts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

@router.put("/{post_id}/mark-posted")
async def mark_post_as_posted(post_id: str, engagement_data: Optional[dict] = None, db = Depends(get_db)):
    """Mark a post as posted"""
    try:
        update_data = {
            "status": "posted",
            "posted_at": datetime.now(timezone.utc).isoformat()
        }
        
        if engagement_data:
            update_data["engagement"] = engagement_data
        
        await db.social_media_posts.update_one(
            {"id": post_id},
            {"$set": update_data}
        )
        
        return {
            "status": "success",
            "message": "Post marked as posted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating post: {str(e)}")

@router.delete("/{post_id}")
async def delete_post(post_id: str, db = Depends(get_db)):
    """Delete a post"""
    try:
        result = await db.social_media_posts.delete_one({"id": post_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {
            "status": "success",
            "message": "Post deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")

@router.post("/generate-post-image")
async def generate_post_image(data: dict, db = Depends(get_db)):
    """Generate visual post design with product data (placeholder for advanced implementation)"""
    try:
        # Get post details
        caption = data.get('caption', '')
        platform = data.get('platform', 'instagram')
        product_ids = data.get('product_ids', [])
        
        # Get product images if provided
        product_images = []
        products = []
        if product_ids:
            for product_id in product_ids[:3]:  # Max 3 products
                product = await db.products.find_one({"id": product_id}, {"_id": 0})
                if product:
                    products.append(product)
                    product_images.append({
                        "url": product.get('image', ''),
                        "name": product.get('name', '')
                    })
        
        # Return post design data (will be enhanced with AI image generation)
        return {
            "status": "success",
            "design_data": {
                "background_image": None,  # Will add AI generation later
                "caption": caption,
                "platform": platform,
                "product_images": product_images,
                "products": products,
                "brand_name": "Aditya Retail",
                "brand_tagline": "Quality Home Appliances",
                "headline": products[0].get('name') if products else "Amazing Products",
                "cta": "Shop Now",
                "hashtags": data.get('hashtags', []),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating post image: {str(e)}")
