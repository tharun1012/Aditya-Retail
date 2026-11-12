"""
One-time migration: apply normalize_headings() to all existing published
blog posts, upgrading bold-paragraph section labels into real heading tags.
Safe to re-run — it's idempotent (already-converted headings won't match
the <p><strong>Label</strong></p> pattern a second time).
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from blog_routes import normalize_headings

async def main():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "startup_template")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    posts = await db.blog_posts.find({}).to_list(1000)
    print(f"Found {len(posts)} blog posts to check")

    changed = 0
    for post in posts:
        original = post.get("content", "")
        updated = normalize_headings(original)
        if updated != original:
            await db.blog_posts.update_one(
                {"id": post["id"]},
                {"$set": {"content": updated}}
            )
            changed += 1
            print(f"  Updated: {post.get('title')}")

    print(f"\nDone. {changed} of {len(posts)} posts had headings normalized.")

if __name__ == "__main__":
    asyncio.run(main())
