"""
Blog Routes - SEO-optimized blog system with AI content generation
"""
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os
import re
import jwt

from database import get_db

router = APIRouter(prefix="/blog", tags=["Blog"])

JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "your-secret-key")

# ======================= MODELS =======================

class BlogFAQ(BaseModel):
    question: str
    answer: str

class BlogPostCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = []
    status: str = "draft"  # draft, published
    author: Optional[str] = None
    published_at: Optional[str] = None
    faqs: Optional[List[BlogFAQ]] = []

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    faqs: Optional[List[BlogFAQ]] = None
    status: Optional[str] = None

class AIBlogGenerateRequest(BaseModel):
    topic: str
    keywords: Optional[List[str]] = []
    tone: str = "professional"  # professional, casual, informative
    length: str = "medium"  # short, medium, long
    include_product_links: bool = True
    outline_only: bool = False

# ======================= HELPERS =======================

def generate_slug(title: str) -> str:
    """Generate SEO-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug

def generate_excerpt(content: str, max_length: int = 160) -> str:
    """Generate excerpt from content"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    # Remove markdown
    text = re.sub(r'[#*_`]', '', text)
    # Truncate
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    return text

async def verify_admin(authorization: str = Header(None)):
    """Verify admin token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ======================= PUBLIC ENDPOINTS =======================


# Section labels that AI-generated content commonly emits as bold paragraphs
# instead of real heading tags. This list can be extended over time.
KNOWN_SECTION_LABELS = [
    "Overview", "Quick Comparison Summary", "Key Features", "Premium Technologies", "Advantages",
    "Limitations", "Best For", "Who Should Avoid", "Who Should Upgrade",
    "Common Mistakes Buyers Make", "Maintenance Tips", "Final Recommendation",
]

def normalize_headings(html: str) -> str:
    """
    Upgrade <p><strong>Label</strong></p> (and minor variants) into <h3>Label</h3>
    for known recurring section labels, so spacing/semantics are correct
    regardless of how the content was authored (AI generation or manual edit).
    """
    if not html:
        return html

    for label in KNOWN_SECTION_LABELS:
        escaped = re.escape(label)
        # Matches: <p><strong>Label</strong></p> or <p><strong>Label:</strong></p>
        # with optional trailing colon and optional <br> before closing </p>
        pattern = re.compile(
            r'<p>\s*<strong>\s*' + escaped + r'\s*:?\s*</strong>\s*(?:<br\s*/?>)?\s*</p>',
            re.IGNORECASE
        )
        html = pattern.sub(f'<h3>{label}</h3>', html)

    return html

@router.get("/posts")
async def get_published_posts(
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db = Depends(get_db)
):
    """Get published blog posts (public)"""
    try:
        skip = (page - 1) * limit
        
        query = {"status": "published"}
        
        if category:
            query["category"] = category
        if tag:
            query["tags"] = tag
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}},
                {"excerpt": {"$regex": search, "$options": "i"}}
            ]
        
        posts = await db.blog_posts.find(
            query,
            {"_id": 0, "content": 0}  # Exclude full content for listing
        ).sort("published_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.blog_posts.count_documents(query)
        
        return {
            "status": "success",
            "posts": posts,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/post/{slug}")
async def get_post_by_slug(slug: str, db = Depends(get_db)):
    """Get a single blog post by slug (public)"""
    try:
        post = await db.blog_posts.find_one(
            {"slug": slug, "status": "published"},
            {"_id": 0}
        )
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Increment view count
        await db.blog_posts.update_one(
            {"slug": slug},
            {"$inc": {"views": 1}}
        )
        
        # Get related posts (same category or tags)
        related_query = {
            "status": "published",
            "slug": {"$ne": slug},
            "$or": [
                {"category": post.get("category")},
                {"tags": {"$in": post.get("tags", [])}}
            ]
        }
        related = await db.blog_posts.find(
            related_query,
            {"_id": 0, "content": 0}
        ).limit(3).to_list(3)
        
        post["related_posts"] = related
        
        return {"status": "success", "post": post}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(db = Depends(get_db)):
    """Get all blog categories with post counts"""
    try:
        pipeline = [
            {"$match": {"status": "published", "category": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = await db.blog_posts.aggregate(pipeline).to_list(100)
        
        return {
            "status": "success",
            "categories": [{"name": c["_id"], "count": c["count"]} for c in categories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags")
async def get_tags(db = Depends(get_db)):
    """Get all blog tags with post counts"""
    try:
        pipeline = [
            {"$match": {"status": "published"}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 50}
        ]
        tags = await db.blog_posts.aggregate(pipeline).to_list(50)
        
        return {
            "status": "success",
            "tags": [{"name": t["_id"], "count": t["count"]} for t in tags]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======================= ADMIN ENDPOINTS =======================

@router.get("/admin/posts")
async def admin_get_all_posts(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Get all blog posts (admin)"""
    try:
        skip = (page - 1) * limit
        
        query = {}
        if status:
            query["status"] = status
        
        posts = await db.blog_posts.find(
            query,
            {"_id": 0, "content": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        total = await db.blog_posts.count_documents(query)
        
        return {
            "status": "success",
            "posts": posts,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/post/{post_id}")
async def admin_get_post(
    post_id: str,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Get a single post by ID (admin)"""
    try:
        post = await db.blog_posts.find_one({"id": post_id}, {"_id": 0})
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"status": "success", "post": post}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/posts")
async def create_post(
    post: BlogPostCreate,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Create a new blog post"""
    try:
        post_id = str(uuid.uuid4())
        slug = post.slug or generate_slug(post.title)
        
        # Check slug uniqueness
        existing = await db.blog_posts.find_one({"slug": slug})
        if existing:
            slug = f"{slug}-{post_id[:8]}"
        
        # Normalize section-label paragraphs into real heading tags
        post.content = normalize_headings(post.content)

        # Generate excerpt if not provided
        excerpt = post.excerpt or generate_excerpt(post.content)
        
        now = datetime.now(timezone.utc).isoformat()
        
        blog_post = {
            "id": post_id,
            "title": post.title,
            "slug": slug,
            "content": post.content,
            "excerpt": excerpt,
            "featured_image": post.featured_image,
            "category": post.category,
            "tags": post.tags or [],
            "meta_title": post.meta_title or post.title,
            "meta_description": post.meta_description or excerpt,
            "meta_keywords": post.meta_keywords or [],
            "status": post.status,
            "author": post.author or admin.get("email", "Admin"),
            "views": 0,
            "created_at": now,
            "updated_at": now,
            "published_at": post.published_at or (now if post.status == "published" else None),
            "faqs": [f.dict() for f in (post.faqs or [])]
        }
        
        await db.blog_posts.insert_one(blog_post)
        
        return {
            "status": "success",
            "message": "Post created successfully",
            "post": {k: v for k, v in blog_post.items() if k != "_id"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/admin/posts/{post_id}")
async def update_post(
    post_id: str,
    post: BlogPostUpdate,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Update a blog post"""
    try:
        existing = await db.blog_posts.find_one({"id": post_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Post not found")
        
        update_data = {k: v for k, v in post.dict().items() if v is not None}
        
        # Handle slug update
        if "title" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["title"])
        
        # Normalize section-label paragraphs into real heading tags
        if "content" in update_data:
            update_data["content"] = normalize_headings(update_data["content"])

        # Handle excerpt update
        if "content" in update_data and "excerpt" not in update_data:
            update_data["excerpt"] = generate_excerpt(update_data["content"])
        
        # Handle publish
        if update_data.get("status") == "published" and existing.get("status") != "published":
            update_data["published_at"] = datetime.now(timezone.utc).isoformat()
        
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.blog_posts.update_one(
            {"id": post_id},
            {"$set": update_data}
        )
        
        updated = await db.blog_posts.find_one({"id": post_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": "Post updated successfully",
            "post": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/posts/{post_id}")
async def delete_post(
    post_id: str,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Delete a blog post"""
    try:
        result = await db.blog_posts.delete_one({"id": post_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"status": "success", "message": "Post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================= ONE-TIME MIGRATION =======================

@router.post("/admin/migrate-normalize-headings")
async def migrate_normalize_headings(
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """One-time migration: normalize bold-paragraph section labels into
    real heading tags across all existing blog posts. Idempotent/safe to re-run."""
    try:
        posts = await db.blog_posts.find({}).to_list(1000)
        changed = []

        for p in posts:
            original = p.get("content", "")
            updated = normalize_headings(original)
            if updated != original:
                await db.blog_posts.update_one(
                    {"id": p["id"]},
                    {"$set": {"content": updated}}
                )
                changed.append(p.get("title"))

        return {
            "status": "success",
            "total_posts_checked": len(posts),
            "posts_updated": len(changed),
            "updated_titles": changed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======================= AI CONTENT GENERATION =======================

@router.post("/admin/generate")
async def generate_blog_with_ai(
    request: AIBlogGenerateRequest,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Generate blog content using AI"""
    try:
        from emergentintegrations.llm.chat import chat, LLMProvider
        
        # Get product info for internal linking if requested
        product_context = ""
        if request.include_product_links:
            products = await db.products.find(
                {},
                {"name": 1, "category": 1, "brand": 1, "slug": 1}
            ).limit(20).to_list(20)
            
            product_list = "\n".join([
                f"- {p.get('name')} ({p.get('brand')}) - Category: {p.get('category')}"
                for p in products
            ])
            product_context = f"""
Available products for internal linking (use format [Product Name](/product/slug)):
{product_list}
"""
        
        # Determine content length
        word_count = {"short": 500, "medium": 1000, "long": 2000}.get(request.length, 1000)
        
        # Build prompt based on outline_only flag
        if request.outline_only:
            prompt = f"""Create a detailed blog post OUTLINE for the topic: "{request.topic}"

Target keywords to include: {', '.join(request.keywords) if request.keywords else 'None specified'}
Tone: {request.tone}

Generate an SEO-optimized outline with:
1. Suggested Title (H1)
2. Meta Description (under 160 characters)
3. Introduction hook
4. Main sections (H2 headings) with bullet points for each
5. Suggested internal links to products
6. Conclusion with call-to-action
7. Suggested tags and category

Format as a structured outline the marketing team can expand on."""
        else:
            prompt = f"""Write a complete, SEO-optimized blog post about: "{request.topic}"

Target keywords to naturally include: {', '.join(request.keywords) if request.keywords else 'None specified'}
Tone: {request.tone}
Target length: approximately {word_count} words

{product_context}

Requirements:
1. Start with an engaging H1 title
2. Write a compelling meta description (under 160 characters)
3. Structure with clear H2 and H3 headings. This is critical: EVERY subsection
   label (e.g. "Overview", "Quick Comparison Summary", "Key Features", "Advantages", "Limitations", "Best For",
   "Who Should Avoid", "Maintenance Tips") MUST be a real <h3> or <h4> HTML tag.
   NEVER use a bold paragraph like <p><strong>Advantages</strong></p> as a substitute
   for a heading — this breaks visual spacing on the live site.
4. Include relevant internal links to products where natural
5. Write for humans first, search engines second
6. Include a strong call-to-action at the end
7. Add suggested tags (comma-separated)
8. Suggest a category

Format the response as:
---
TITLE: [Your title here]
META_DESCRIPTION: [Meta description here]
CATEGORY: [Suggested category]
TAGS: [tag1, tag2, tag3]
---
[Full blog content with HTML formatting]
---"""
        
        # Call LLM
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")
        
        response = chat(
            api_key=emergent_key,
            provider=LLMProvider.GEMINI,
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer for a premium kitchen appliances e-commerce store (Aditya Retail). Write engaging, informative content that helps customers make purchase decisions while being optimized for search engines."},
                {"role": "user", "content": prompt}
            ]
        )
        
        generated_content = response.message
        
        # Parse the response to extract structured data
        result = {
            "status": "success",
            "generated": {
                "raw_content": generated_content,
                "outline_only": request.outline_only
            }
        }
        
        # Try to parse structured content if full article
        if not request.outline_only and "---" in generated_content:
            parts = generated_content.split("---")
            if len(parts) >= 3:
                meta_section = parts[1]
                content_section = parts[2] if len(parts) > 2 else ""
                
                # Extract metadata
                title_match = re.search(r'TITLE:\s*(.+)', meta_section)
                meta_desc_match = re.search(r'META_DESCRIPTION:\s*(.+)', meta_section)
                category_match = re.search(r'CATEGORY:\s*(.+)', meta_section)
                tags_match = re.search(r'TAGS:\s*(.+)', meta_section)
                
                result["generated"]["parsed"] = {
                    "title": title_match.group(1).strip() if title_match else request.topic,
                    "meta_description": meta_desc_match.group(1).strip() if meta_desc_match else "",
                    "category": category_match.group(1).strip() if category_match else "General",
                    "tags": [t.strip() for t in tags_match.group(1).split(",")] if tags_match else [],
                    "content": content_section.strip()
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"AI Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/admin/generate-outline")
async def generate_blog_outline(
    request: AIBlogGenerateRequest,
    db = Depends(get_db),
    admin = Depends(verify_admin)
):
    """Generate blog outline only"""
    request.outline_only = True
    return await generate_blog_with_ai(request, db, admin)
