from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import List
import os
import shutil
from pathlib import Path
import uuid
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from database import db
from file_storage import save_upload, serve_upload

router = APIRouter(prefix="/upload", tags=["Upload"])

IMAGES_DIR = Path("/app/frontend/public/product-images")
DOCUMENTS_DIR = Path("/app/frontend/public/product-documents")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

fs_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="images")


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        filename = file.filename or str(uuid.uuid4())
        file_id = await fs_bucket.upload_from_stream(
            filename,
            contents,
            metadata={"content_type": file.content_type}
        )

        image_url = f"/api/upload/image/{file_id}"

        return {
            "status": "success",
            "image_url": image_url,
            "message": "Image uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images")
async def upload_images(files: List[UploadFile] = File(...)):
    try:
        uploaded_urls = []

        for file in files:
            if not file.content_type.startswith('image/'):
                continue

            contents = await file.read()
            if not contents:
                continue

            filename = file.filename or str(uuid.uuid4())
            file_id = await fs_bucket.upload_from_stream(
                filename,
                contents,
                metadata={"content_type": file.content_type}
            )

            uploaded_urls.append(f"/api/upload/image/{file_id}")

        return {
            "status": "success",
            "urls": uploaded_urls,
            "count": len(uploaded_urls),
            "message": f"{len(uploaded_urls)} image(s) uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{file_id}")
async def get_image(file_id: str):
    try:
        oid = ObjectId(file_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid image id")

    try:
        grid_out = await fs_bucket.open_download_stream(oid)
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    data = await grid_out.read()
    content_type = "application/octet-stream"
    if grid_out.metadata and grid_out.metadata.get("content_type"):
        content_type = grid_out.metadata["content_type"]

    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"}
    )


@router.post("/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = []

        for file in files:
            allowed_types = ['application/pdf', 'application/msword',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

            if file.content_type not in allowed_types:
                continue

            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            content = await file.read()
            await save_upload(unique_filename, content, file.content_type)

            document_url = f"/api/upload/document/{unique_filename}"
            uploaded_files.append({
                "url": document_url,
                "filename": file.filename,
                "content_type": file.content_type
            })

        return {
            "status": "success",
            "files": uploaded_files,
            "count": len(uploaded_files),
            "message": f"{len(uploaded_files)} document(s) uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{filename}")
async def get_document(filename: str):
    return await serve_upload(filename)
