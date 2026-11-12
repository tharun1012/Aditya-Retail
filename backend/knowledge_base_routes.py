"""
Knowledge Base Management for AI Agents
Upload product manuals, technical documents, warranty info for agent training
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
import tempfile
import PyPDF2
import docx
from database import get_db

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

class KnowledgeDocument(BaseModel):
    title: str
    document_type: str  # manual, warranty, troubleshooting, installation, faq
    product_ids: Optional[List[str]] = None  # Associated products
    brand: Optional[str] = None
    category: Optional[str] = None
    content: str  # Extracted text content
    file_url: Optional[str] = None

@router.post("/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = None,
    document_type: str = "manual",
    product_ids: Optional[str] = None,  # Comma-separated
    brand: Optional[str] = None,
    category: Optional[str] = None,
    db = Depends(get_db)
):
    """Upload and parse product documents for AI knowledge"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX, and TXT files are supported"
            )
        
        # Save to a temp file for text extraction
        content = await file.read()
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
            tmp.write(content)
            file_path = tmp.name
        
        # Extract text content based on file type
        extracted_text = ""
        
        if file_extension == '.pdf':
            extracted_text = await _extract_pdf_text(file_path)
        elif file_extension == '.docx':
            extracted_text = await _extract_docx_text(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        
        os.remove(file_path)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from document")
        
        # Parse product_ids
        product_id_list = []
        if product_ids:
            product_id_list = [pid.strip() for pid in product_ids.split(',')]
        
        # Create knowledge document
        kb_doc = {
            "id": str(uuid.uuid4()),
            "title": title or file.filename,
            "document_type": document_type,
            "product_ids": product_id_list,
            "brand": brand,
            "category": category,
            "content": extracted_text,
            "file_url": None,
            "filename": file.filename,
            "file_size": len(content),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.knowledge_base.insert_one(kb_doc)
        
        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "document_id": kb_doc["id"],
            "content_length": len(extracted_text),
            "words": len(extracted_text.split())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def _extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

async def _extract_docx_text(file_path: str) -> str:
    """Extract text from DOCX"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

@router.get("/")
async def get_all_knowledge_documents(
    document_type: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    db = Depends(get_db)
):
    """Get all knowledge base documents"""
    try:
        query = {}
        if document_type:
            query["document_type"] = document_type
        if brand:
            query["brand"] = brand
        if category:
            query["category"] = category
        
        documents = await db.knowledge_base.find(query, {"_id": 0, "content": 0}).sort("created_at", -1).to_list(100)
        
        return {
            "status": "success",
            "total": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

@router.get("/{document_id}")
async def get_knowledge_document(document_id: str, db = Depends(get_db)):
    """Get single knowledge document with full content"""
    try:
        document = await db.knowledge_base.find_one({"id": document_id}, {"_id": 0})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "status": "success",
            "document": document
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/search/query")
async def search_knowledge_base(
    query: str,
    document_type: Optional[str] = None,
    limit: int = 10,
    db = Depends(get_db)
):
    """Search knowledge base content"""
    try:
        # Build MongoDB text search query
        search_query = {
            "$text": {"$search": query}
        }
        
        if document_type:
            search_query["document_type"] = document_type
        
        # Search documents
        documents = await db.knowledge_base.find(
            search_query,
            {"_id": 0, "score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).to_list(limit)
        
        return {
            "status": "success",
            "query": query,
            "results": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_knowledge_document(document_id: str, db = Depends(get_db)):
    """Delete knowledge document"""
    try:
        document = await db.knowledge_base.find_one({"id": document_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from filesystem
        if document.get("file_url"):
            file_path = f"/app/backend{document['file_url']}"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete from database
        await db.knowledge_base.delete_one({"id": document_id})
        
        return {
            "status": "success",
            "message": "Document deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/product/{product_id}/documents")
async def get_product_knowledge(product_id: str, db = Depends(get_db)):
    """Get all knowledge documents for a specific product"""
    try:
        documents = await db.knowledge_base.find(
            {"product_ids": product_id},
            {"_id": 0}
        ).to_list(100)
        
        return {
            "status": "success",
            "product_id": product_id,
            "total": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
