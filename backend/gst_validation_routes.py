"""
GST validation routes - Search Taxpayer via Whitebooks GST API.
Used to validate GSTINs on entry for purchase bills/vendors and B2B invoices.
"""
from fastapi import APIRouter, HTTPException, Query
from services.whitebooks_client import WhitebooksClient, WhitebooksAPIError, WhitebooksAuthError

router = APIRouter(prefix="/gst", tags=["GST Validation"])


@router.get("/validate")
async def validate_gstin(gstin: str = Query(..., min_length=15, max_length=15)):
    client = WhitebooksClient()
    try:
        result = client.search_taxpayer(gstin)
    except (WhitebooksAPIError, WhitebooksAuthError) as e:
        raise HTTPException(status_code=502, detail=f"GST validation service error: {str(e)}")
    return result
