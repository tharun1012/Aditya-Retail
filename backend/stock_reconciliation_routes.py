"""
Stock Reconciliation Routes
Auto-link purchase bill items to products, add missing items to catalog
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from database import get_db
import uuid
import logging
import re

router = APIRouter(prefix="/stock-reconciliation", tags=["Stock Reconciliation"])
logger = logging.getLogger(__name__)


class LinkItemRequest(BaseModel):
    purchase_bill_id: str
    item_index: int
    product_id: str


class AddToProductCatalogRequest(BaseModel):
    item_name: str
    model_number: Optional[str] = ""
    hsn_code: Optional[str] = ""
    category: Optional[str] = "uncategorized"
    brand: Optional[str] = ""
    purchase_price: float = 0
    selling_price: float = 0
    item_type: str = "product"  # product, part, consumable


class BulkAutoLinkRequest(BaseModel):
    dry_run: bool = True  # If true, just show what would be linked


# ============ RECONCILIATION ANALYSIS ============

@router.get("/analysis")
async def get_reconciliation_analysis(db = Depends(get_db)):
    """
    Analyze purchase bill items vs product catalog
    Shows matched, unmatched, and linkable items
    """
    try:
        # Get all purchase bills
        bills = await db.purchase_bills.find({}).to_list(length=1000)
        
        # Get all products
        products = await db.products.find({}).to_list(length=5000)
        
        # Build product lookup indexes
        product_by_id = {p.get('id'): p for p in products}
        product_by_name = {p.get('name', '').lower(): p for p in products}
        product_by_model = {p.get('model_number', '').upper(): p for p in products if p.get('model_number')}
        
        # Analyze each purchase bill item
        matched_items = []
        unmatched_items = []
        linkable_items = []  # Items that can be auto-linked by model number
        
        item_frequency = {}  # Track how often each unmatched item appears
        
        for bill in bills:
            bill_id = bill.get('id')
            bill_number = bill.get('bill_number')
            vendor_name = bill.get('vendor', {}).get('name', 'Unknown')
            
            for idx, item in enumerate(bill.get('items', [])):
                item_name = item.get('product_name', '')
                item_name_upper = item_name.upper().strip()
                item_name_lower = item_name.lower().strip()
                
                # Check if already linked
                if item.get('linked_product_id'):
                    product = product_by_id.get(item.get('linked_product_id'))
                    matched_items.append({
                        'bill_id': bill_id,
                        'bill_number': bill_number,
                        'item_index': idx,
                        'item_name': item_name,
                        'linked_product_id': item.get('linked_product_id'),
                        'linked_product_name': product.get('name') if product else 'Unknown',
                        'quantity': item.get('quantity', 0),
                        'rate': item.get('rate', 0)
                    })
                    continue
                
                # Try to find a match
                matched_product = None
                match_type = None
                
                # 1. Exact model number match
                if item_name_upper in product_by_model:
                    matched_product = product_by_model[item_name_upper]
                    match_type = 'model_number'
                
                # 2. Exact name match
                elif item_name_lower in product_by_name:
                    matched_product = product_by_name[item_name_lower]
                    match_type = 'exact_name'
                
                # 3. Partial model number match (item name contains model number)
                else:
                    for model, product in product_by_model.items():
                        if model and len(model) >= 5:  # Only match significant model numbers
                            if model in item_name_upper or item_name_upper in model:
                                matched_product = product
                                match_type = 'partial_model'
                                break
                
                if matched_product:
                    linkable_items.append({
                        'bill_id': bill_id,
                        'bill_number': bill_number,
                        'vendor_name': vendor_name,
                        'item_index': idx,
                        'item_name': item_name,
                        'suggested_product_id': matched_product.get('id'),
                        'suggested_product_name': matched_product.get('name'),
                        'suggested_model': matched_product.get('model_number'),
                        'match_type': match_type,
                        'quantity': item.get('quantity', 0),
                        'rate': item.get('rate', 0),
                        'hsn_code': item.get('hsn_code', '')
                    })
                else:
                    unmatched_items.append({
                        'bill_id': bill_id,
                        'bill_number': bill_number,
                        'vendor_name': vendor_name,
                        'item_index': idx,
                        'item_name': item_name,
                        'quantity': item.get('quantity', 0),
                        'rate': item.get('rate', 0),
                        'hsn_code': item.get('hsn_code', '')
                    })
                    
                    # Track frequency
                    key = item_name_upper
                    if key not in item_frequency:
                        item_frequency[key] = {'name': item_name, 'count': 0, 'total_qty': 0, 'total_value': 0}
                    item_frequency[key]['count'] += 1
                    item_frequency[key]['total_qty'] += item.get('quantity', 0)
                    item_frequency[key]['total_value'] += item.get('quantity', 0) * item.get('rate', 0)
        
        # Sort unmatched by frequency
        frequent_unmatched = sorted(
            item_frequency.values(), 
            key=lambda x: x['count'], 
            reverse=True
        )[:50]
        
        return {
            "status": "success",
            "summary": {
                "total_bills": len(bills),
                "total_products": len(products),
                "already_linked": len(matched_items),
                "can_auto_link": len(linkable_items),
                "unmatched": len(unmatched_items),
                "unique_unmatched": len(item_frequency)
            },
            "linkable_items": linkable_items[:100],  # Limit for performance
            "unmatched_items": unmatched_items[:100],
            "frequent_unmatched": frequent_unmatched,
            "matched_items": matched_items[:50]
        }
        
    except Exception as e:
        logger.error(f"Reconciliation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-link")
async def auto_link_items(request: BulkAutoLinkRequest, db = Depends(get_db)):
    """
    Automatically link purchase bill items to products by model number
    """
    try:
        # Get analysis first
        bills = await db.purchase_bills.find({}).to_list(length=1000)
        products = await db.products.find({}).to_list(length=5000)
        
        product_by_model = {p.get('model_number', '').upper(): p for p in products if p.get('model_number')}
        
        links_to_create = []
        
        for bill in bills:
            bill_id = bill.get('id')
            items = bill.get('items', [])
            items_updated = False
            
            for idx, item in enumerate(items):
                # Skip already linked items
                if item.get('linked_product_id'):
                    continue
                
                item_name = item.get('product_name', '').upper().strip()
                
                # Check for model number match
                if item_name in product_by_model:
                    product = product_by_model[item_name]
                    links_to_create.append({
                        'bill_id': bill_id,
                        'bill_number': bill.get('bill_number'),
                        'item_index': idx,
                        'item_name': item.get('product_name'),
                        'product_id': product.get('id'),
                        'product_name': product.get('name'),
                        'model_number': product.get('model_number')
                    })
                    
                    if not request.dry_run:
                        items[idx]['linked_product_id'] = product.get('id')
                        items[idx]['linked_product_name'] = product.get('name')
                        items_updated = True
            
            # Update bill if items were linked
            if items_updated and not request.dry_run:
                await db.purchase_bills.update_one(
                    {"id": bill_id},
                    {"$set": {"items": items, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
        
        return {
            "status": "success",
            "dry_run": request.dry_run,
            "message": f"{'Would link' if request.dry_run else 'Linked'} {len(links_to_create)} items to products",
            "links": links_to_create[:100]
        }
        
    except Exception as e:
        logger.error(f"Auto-link failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/link-item")
async def link_single_item(request: LinkItemRequest, db = Depends(get_db)):
    """
    Manually link a purchase bill item to a product
    """
    try:
        # Get the bill
        bill = await db.purchase_bills.find_one({"id": request.purchase_bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Purchase bill not found")
        
        # Get the product
        product = await db.products.find_one({"id": request.product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update the item
        items = bill.get('items', [])
        if request.item_index >= len(items):
            raise HTTPException(status_code=400, detail="Invalid item index")
        
        items[request.item_index]['linked_product_id'] = product.get('id')
        items[request.item_index]['linked_product_name'] = product.get('name')
        
        await db.purchase_bills.update_one(
            {"id": request.purchase_bill_id},
            {"$set": {"items": items, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "status": "success",
            "message": f"Linked '{items[request.item_index].get('product_name')}' to '{product.get('name')}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-to-catalog")
async def add_item_to_catalog(request: AddToProductCatalogRequest, db = Depends(get_db)):
    """
    Add an unmatched item to the product catalog
    """
    try:
        # Check if product already exists
        existing = await db.products.find_one({
            "$or": [
                {"name": request.item_name},
                {"model_number": request.model_number} if request.model_number else {"_id": None}
            ]
        })
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Product already exists: {existing.get('name')}"
            )
        
        # Create product
        product_id = str(uuid.uuid4())
        product_data = {
            "id": product_id,
            "name": request.item_name,
            "model_number": request.model_number or request.item_name,
            "brand": request.brand or "Unknown",
            "category": request.category,
            "hsn_code": request.hsn_code,
            "purchase_price": request.purchase_price,
            "price": request.selling_price or request.purchase_price * 1.2,  # 20% markup default
            "mrp": request.selling_price or request.purchase_price * 1.3,
            "stock_quantity": 0,
            "item_type": request.item_type,
            "description": "Added from purchase bill reconciliation",
            "images": [],
            "specifications": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "reconciliation",
            # Hide from storefront until an admin reviews & approves the product
            # via the Incomplete Products Manager. Admin can either AI-Enhance,
            # paste a URL to auto-extract data, or fill in details manually,
            # then click "Approve & Publish".
            "is_listed": False,
            "review_status": "pending_review",
        }
        
        await db.products.insert_one(product_data)
        
        return {
            "status": "success",
            "message": f"Product '{request.item_name}' added to catalog",
            "product_id": product_id,
            "product": {
                "id": product_id,
                "name": request.item_name,
                "model_number": request.model_number,
                "category": request.category,
                "item_type": request.item_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to catalog failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-add-to-catalog")
async def bulk_add_to_catalog(
    items: List[AddToProductCatalogRequest],
    db = Depends(get_db)
):
    """
    Add multiple unmatched items to the product catalog
    """
    try:
        added = []
        skipped = []
        
        for item in items:
            try:
                # Check if exists
                existing = await db.products.find_one({
                    "$or": [
                        {"name": item.item_name},
                        {"model_number": item.model_number} if item.model_number else {"_id": None}
                    ]
                })
                
                if existing:
                    skipped.append({
                        "name": item.item_name,
                        "reason": f"Already exists as: {existing.get('name')}"
                    })
                    continue
                
                product_id = str(uuid.uuid4())
                product_data = {
                    "id": product_id,
                    "name": item.item_name,
                    "model_number": item.model_number or item.item_name,
                    "brand": item.brand or "Unknown",
                    "category": item.category,
                    "hsn_code": item.hsn_code,
                    "purchase_price": item.purchase_price,
                    "price": item.selling_price or item.purchase_price * 1.2,
                    "mrp": item.selling_price or item.purchase_price * 1.3,
                    "stock_quantity": 0,
                    "item_type": item.item_type,
                    "description": "Added from purchase bill reconciliation",
                    "images": [],
                    "specifications": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "reconciliation",
                    # Hide from storefront until reviewed in Incomplete Products Manager
                    "is_listed": False,
                    "review_status": "pending_review",
                }
                
                await db.products.insert_one(product_data)
                added.append({
                    "id": product_id,
                    "name": item.item_name,
                    "model_number": item.model_number
                })
                
            except Exception as e:
                skipped.append({
                    "name": item.item_name,
                    "reason": str(e)
                })
        
        return {
            "status": "success",
            "message": f"Added {len(added)} products, skipped {len(skipped)}",
            "added": added,
            "skipped": skipped
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/search")
async def search_products(q: str, db = Depends(get_db)):
    """
    Search products for manual linking
    """
    try:
        query = {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"model_number": {"$regex": q, "$options": "i"}},
                {"brand": {"$regex": q, "$options": "i"}}
            ]
        }
        
        products = await db.products.find(query).limit(20).to_list(length=20)
        
        # Remove _id from results
        for p in products:
            p.pop('_id', None)
        
        return {
            "status": "success",
            "products": products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories(db = Depends(get_db)):
    """
    Get list of existing product categories
    """
    try:
        categories = await db.products.distinct("category")
        return {
            "status": "success",
            "categories": [c for c in categories if c]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
