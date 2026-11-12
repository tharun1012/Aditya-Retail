"""Persistent file storage backed by MongoDB GridFS (survives redeploys)."""
from fastapi import HTTPException
from fastapi.responses import Response
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from gridfs.errors import NoFile
from database import db

uploads_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="uploads")


async def save_upload(filename: str, content: bytes, content_type: str) -> str:
    await uploads_bucket.upload_from_stream(
        filename, content, metadata={"content_type": content_type}
    )
    return filename


async def serve_upload(filename: str) -> Response:
    try:
        stream = await uploads_bucket.open_download_stream_by_name(filename)
    except NoFile:
        raise HTTPException(status_code=404, detail="File not found")
    data = await stream.read()
    content_type = (stream.metadata or {}).get("content_type", "application/octet-stream")
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
