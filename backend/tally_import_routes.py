"""
Tally Data Import Routes
Import Sales, Purchase, Customer, and Product data from Tally exports (CSV/XLS)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
import pandas as pd
import uuid
import os
import tempfile
import io
import json
import logging

router = APIRouter(prefix="/tally-import", tags=["Tally Import"])
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOAD_DIR = "/app/backend/uploads/tally_imports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
TEMPLATES_DIR = "/app/backend/uploads/tally_templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)

class ImportResult(BaseModel):
    total_rows: int
    imported: int
    skipped: int
    errors: List[str]

class ImportResponse(BaseModel):
    status: str
    message: str
    result: ImportResult


# ============ TEMPLATE GENERATION ============

@router.get("/templates/sales")
async def download_sales_template():
    """Download CSV template for Sales/Invoice import - Includes B2B (with GST/MSME) and B2C examples"""
    template_data = {
        "invoice_number": ["INV-2026-001", "INV-2026-002", "INV-2026-003", "INV-2026-004"],
        "invoice_date": ["2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04"],
        "customer_name": ["ABC Electronics Pvt Ltd", "XYZ Home Appliances", "Ramesh Kumar", "Quick Mart MSME"],
        "customer_phone": ["9876543210", "9876543211", "9876543212", "9876543214"],
        "customer_email": ["accounts@abcelectronics.com", "orders@xyzhome.com", "ramesh@gmail.com", "purchase@quickmart.com"],
        "customer_gstin": ["29AABCA1234F1ZP", "33AABCX5678G1ZQ", "", "29AABCQ9012H1ZR"],
        "customer_msme_udyam": ["", "", "", "UDYAM-KA-01-0012345"],
        "customer_address": ["123 MG Road", "456 Anna Nagar", "789 JP Nagar", "555 HSR Layout"],
        "customer_city": ["Bangalore", "Chennai", "Mysore", "Bangalore"],
        "customer_state": ["Karnataka", "Tamil Nadu", "Karnataka", "Karnataka"],
        "customer_pincode": ["560001", "600040", "570001", "560102"],
        "product_name": ["Bosch 8kg Washing Machine", "Siemens Refrigerator 500L", "Samsung AC 1.5 Ton", "Water Purifier Filter"],
        "product_model": ["WAJ2846SIN", "KA92NVQ30I", "AR18CYLANWK", "WP-FILTER-01"],
        "hsn_code": ["84501900", "84182100", "84151010", "84212100"],
        "quantity": [5, 2, 1, 10],
        "unit_price": [45000, 85000, 42000, 2000],
        "discount_percent": [5, 10, 0, 0],
        "tax_rate": [18, 18, 28, 5],
        "cgst": [4050, 1530, 0, 50],
        "sgst": [4050, 0, 5880, 50],
        "igst": [0, 3060, 0, 0],
        "payment_mode": ["Bank Transfer", "Bank Transfer", "UPI", "Bank Transfer"],
        "payment_status": ["completed", "completed", "completed", "pending"],
        "due_date": ["2026-02-15", "2026-02-17", "", "2026-03-22"],
        "order_status": ["delivered", "shipped", "delivered", "delivered"],
        "notes": ["B2B Same State - CGST+SGST", "B2B Inter-state - IGST", "B2C Consumer Sale", "B2B MSME - 45 day payment"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{TEMPLATES_DIR}/sales_import_template.csv"
    df.to_csv(template_path, index=False)
    
    return FileResponse(
        template_path, 
        filename="sales_import_template.csv",
        media_type="text/csv"
    )


@router.get("/templates/sales-orders")
async def download_sales_orders_template():
    """Download CSV template for Sales Order import - For FY transition and store-specific SOs"""
    template_data = {
        "so_number": ["HRBR-SO-2025-0001", "HRBR-SO-2025-0002", "ARP-SO-2025-0001"],
        "so_date": ["2025-03-15", "2025-03-20", "2025-03-25"],
        "store_code": ["HRBR", "HRBR", "ARP"],
        "customer_name": ["Ramesh Kumar", "Suresh Sharma", "ABC Electronics"],
        "customer_phone": ["9876543210", "9876543211", "9876543212"],
        "customer_email": ["ramesh@gmail.com", "suresh@gmail.com", "accounts@abc.com"],
        "customer_gstin": ["", "", "29AABCA1234F1ZP"],
        "billing_address": ["123 MG Road, Bangalore", "456 JP Nagar, Bangalore", "789 Industrial Area"],
        "billing_city": ["Bangalore", "Bangalore", "Bangalore"],
        "billing_state": ["Karnataka", "Karnataka", "Karnataka"],
        "billing_pincode": ["560001", "570001", "560102"],
        "shipping_address": ["Same as billing", "456 JP Nagar, Bangalore", "789 Industrial Area"],
        "product_name": ["Bosch 8kg Washing Machine", "Samsung AC 1.5 Ton", "LG Refrigerator 500L"],
        "product_model": ["WAJ2846SIN", "AR18CYLANWK", "GL-T502FPZX"],
        "hsn_code": ["84501900", "84151010", "84182100"],
        "quantity": [1, 2, 1],
        "unit_price": [45000, 42000, 85000],
        "discount_percent": [5, 0, 10],
        "tax_rate": [18, 28, 18],
        "delivery_charges": [500, 0, 1000],
        "expected_delivery_date": ["2025-03-20", "2025-03-25", "2025-04-01"],
        "immediate_delivery": ["yes", "no", "no"],
        "payment_mode": ["Cash", "UPI", "Bank Transfer"],
        "payment_status": ["pending", "partially_paid", "pending"],
        "advance_paid": [10000, 20000, 0],
        "notes": ["FY 2025-26 SO", "Customer requested weekend delivery", "B2B order - 15 day credit"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{TEMPLATES_DIR}/sales_orders_import_template.csv"
    df.to_csv(template_path, index=False)
    
    return FileResponse(
        template_path, 
        filename="sales_orders_import_template.csv",
        media_type="text/csv"
    )


@router.post("/sales-orders", response_model=ImportResponse)
async def import_sales_orders(
    file: UploadFile = File(...),
    default_store_code: str = Form(default="HRBR"),
    update_existing: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import Sales Orders from CSV/Excel - Goes to offline_invoices collection with store assignment.
    
    IMPORTANT: This is for importing historical SOs with custom numbering (FY transition).
    The SO numbers in the file will be used as-is (no auto-generation).
    
    Supports:
    - Custom SO numbers (your old FY format)
    - Custom dates (backdating)
    - Store assignment (store_code column or default)
    - Multi-line items per SO
    """
    try:
        df = read_file_to_dataframe(file)
        
        logger.info(f"Sales Order import - columns found: {list(df.columns)}")
        
        imported = 0
        skipped = 0
        errors = []
        
        # Column mapping for SO import
        column_mapping = {
            'so_number': ['so_number', 'sales_order_number', 'order_number', 'document_no', 'invoice_number'],
            'so_date': ['so_date', 'order_date', 'date', 'invoice_date'],
            'store_code': ['store_code', 'store', 'branch', 'location'],
            'customer_name': ['customer_name', 'customer', 'party_name', 'buyer_name', 'name'],
            'customer_phone': ['customer_phone', 'phone', 'mobile', 'contact'],
            'customer_email': ['customer_email', 'email'],
            'customer_gstin': ['customer_gstin', 'gstin', 'gst_number', 'gst'],
            'billing_address': ['billing_address', 'address', 'bill_to_address'],
            'billing_city': ['billing_city', 'city'],
            'billing_state': ['billing_state', 'state'],
            'billing_pincode': ['billing_pincode', 'pincode', 'pin'],
            'shipping_address': ['shipping_address', 'ship_to_address', 'delivery_address'],
            'product_name': ['product_name', 'product', 'item_name', 'item', 'particular'],
            'product_model': ['product_model', 'model', 'model_number', 'sku'],
            'hsn_code': ['hsn_code', 'hsn', 'hsn_sac'],
            'quantity': ['quantity', 'qty', 'units'],
            'unit_price': ['unit_price', 'price', 'rate', 'selling_price'],
            'discount_percent': ['discount_percent', 'discount', 'disc_%'],
            'tax_rate': ['tax_rate', 'gst_rate', 'gst_%', 'tax'],
            'delivery_charges': ['delivery_charges', 'shipping', 'freight'],
            'expected_delivery_date': ['expected_delivery_date', 'delivery_date', 'due_date'],
            'immediate_delivery': ['immediate_delivery', 'immediate'],
            'payment_mode': ['payment_mode', 'payment_method', 'mode'],
            'payment_status': ['payment_status', 'status'],
            'advance_paid': ['advance_paid', 'advance', 'paid_amount'],
            'notes': ['notes', 'remarks', 'narration']
        }
        
        def get_column_value(row, field_name):
            """Get value from row using flexible column mapping"""
            possible_columns = column_mapping.get(field_name, [field_name])
            for col in possible_columns:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val):
                        return val
                matching_cols = [c for c in df.columns if c.lower().strip() == col.lower()]
                for match_col in matching_cols:
                    val = row.get(match_col)
                    if pd.notna(val):
                        return val
            return None
        
        # Find SO number column
        so_col = None
        for col in column_mapping['so_number']:
            if col in df.columns:
                so_col = col
                break
            matching = [c for c in df.columns if c.lower().strip() == col.lower()]
            if matching:
                so_col = matching[0]
                break
        
        # Group by SO number for multi-item orders
        if so_col:
            grouped = df.groupby(so_col)
        else:
            grouped = [(f"SO-IMPORT-{i+1}", df.iloc[[i]]) for i in range(len(df))]
        
        for so_number, group in grouped:
            try:
                first_row = group.iloc[0]
                
                # Check if SO already exists
                existing = await db.offline_invoices.find_one({"invoice_number": str(so_number)})
                if existing and not update_existing:
                    skipped += 1
                    errors.append(f"SO {so_number} already exists - skipped")
                    continue
                
                # Get store code
                store_code = str(get_column_value(first_row, 'store_code') or default_store_code).upper()
                
                # Validate store exists
                store = await db.stores.find_one({"code": store_code})
                if not store:
                    # Try to find by partial match
                    store = await db.stores.find_one({"code": {"$regex": f"^{store_code}", "$options": "i"}})
                    if not store:
                        errors.append(f"Store '{store_code}' not found for SO {so_number}")
                        skipped += 1
                        continue
                
                # Build items
                items = []
                subtotal = 0
                tax_total = 0
                
                for _, row in group.iterrows():
                    qty = int(get_column_value(row, 'quantity') or 1)
                    unit_price = float(get_column_value(row, 'unit_price') or 0)
                    tax_rate = float(get_column_value(row, 'tax_rate') or 18)
                    discount_pct = float(get_column_value(row, 'discount_percent') or 0)
                    
                    # Calculate amounts (assuming inclusive pricing like store billing)
                    gross_amount = unit_price * qty
                    discount_amount = gross_amount * (discount_pct / 100)
                    final_price = gross_amount - discount_amount
                    
                    # GST is inclusive
                    taxable_amount = final_price / (1 + tax_rate / 100)
                    tax_amount = final_price - taxable_amount
                    
                    items.append({
                        "product_name": str(get_column_value(row, 'product_name') or 'Unknown Product'),
                        "model_number": str(get_column_value(row, 'product_model') or ''),
                        "hsn_code": str(get_column_value(row, 'hsn_code') or ''),
                        "quantity": qty,
                        "rate": unit_price,
                        "discount": discount_pct,
                        "tax_rate": tax_rate,
                        "gross_amount": round(gross_amount, 2),
                        "discount_amount": round(discount_amount, 2),
                        "taxable_amount": round(taxable_amount, 2),
                        "tax_amount": round(tax_amount, 2),
                        "cgst": round(tax_amount / 2, 2),
                        "sgst": round(tax_amount / 2, 2),
                        "total": round(final_price, 2)
                    })
                    
                    subtotal += taxable_amount
                    tax_total += tax_amount
                
                # Parse dates
                so_date = get_column_value(first_row, 'so_date')
                if so_date:
                    if hasattr(so_date, 'strftime'):
                        so_date = so_date.strftime('%Y-%m-%d')
                    else:
                        so_date = str(so_date)[:10]  # Take YYYY-MM-DD part
                else:
                    so_date = datetime.now().strftime('%Y-%m-%d')
                
                delivery_date = get_column_value(first_row, 'expected_delivery_date')
                if delivery_date:
                    if hasattr(delivery_date, 'strftime'):
                        delivery_date = delivery_date.strftime('%Y-%m-%d')
                    else:
                        delivery_date = str(delivery_date)[:10]
                else:
                    delivery_date = so_date
                
                # Check immediate delivery flag
                immediate_str = str(get_column_value(first_row, 'immediate_delivery') or 'yes').lower()
                immediate_delivery = immediate_str in ['yes', 'true', '1', 'y']
                
                # Delivery charges
                delivery_charges = float(get_column_value(first_row, 'delivery_charges') or 0)
                
                # Calculate delivery charges GST (18%)
                delivery_taxable = delivery_charges / 1.18
                delivery_gst = delivery_charges - delivery_taxable
                
                # Final total
                items_total = sum(item['total'] for item in items)
                total_amount = items_total + delivery_charges
                
                # Build customer object
                customer = {
                    "name": str(get_column_value(first_row, 'customer_name') or 'Walk-in Customer'),
                    "phone": str(get_column_value(first_row, 'customer_phone') or ''),
                    "email": str(get_column_value(first_row, 'customer_email') or ''),
                    "gstin": str(get_column_value(first_row, 'customer_gstin') or ''),
                    "billing_address": {
                        "address_line1": str(get_column_value(first_row, 'billing_address') or ''),
                        "city": str(get_column_value(first_row, 'billing_city') or ''),
                        "state": str(get_column_value(first_row, 'billing_state') or 'Karnataka'),
                        "pincode": str(get_column_value(first_row, 'billing_pincode') or '')
                    },
                    "shipping_address": {
                        "address_line1": str(get_column_value(first_row, 'shipping_address') or get_column_value(first_row, 'billing_address') or ''),
                        "city": str(get_column_value(first_row, 'billing_city') or ''),
                        "state": str(get_column_value(first_row, 'billing_state') or 'Karnataka'),
                        "pincode": str(get_column_value(first_row, 'billing_pincode') or '')
                    }
                }
                
                # Create SO document
                so_id = str(uuid.uuid4())
                so_doc = {
                    "id": so_id,
                    "invoice_number": str(so_number),
                    "store_code": store_code,
                    "document_type": "sales_order",
                    "customer": customer,
                    "items": items,
                    "subtotal": round(subtotal, 2),
                    "tax_total": round(tax_total, 2),
                    "cgst_total": round(tax_total / 2, 2),
                    "sgst_total": round(tax_total / 2, 2),
                    "delivery_charges": round(delivery_charges, 2),
                    "delivery_charges_gst": round(delivery_gst, 2),
                    "total_amount": round(total_amount, 2),
                    "payment_mode": str(get_column_value(first_row, 'payment_mode') or 'Cash'),
                    "payment_status": str(get_column_value(first_row, 'payment_status') or 'pending').lower(),
                    "advance_paid": float(get_column_value(first_row, 'advance_paid') or 0),
                    "status": "pending_delivery",
                    "immediate_delivery": immediate_delivery,
                    "expected_delivery_date": delivery_date,
                    "invoice_date": so_date,
                    "notes": str(get_column_value(first_row, 'notes') or ''),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "import_source": "tally_excel",
                    "imported_at": datetime.now(timezone.utc).isoformat()
                }
                
                if existing and update_existing:
                    await db.offline_invoices.update_one(
                        {"invoice_number": str(so_number)},
                        {"$set": so_doc}
                    )
                else:
                    await db.offline_invoices.insert_one(so_doc)
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Error importing SO {so_number}: {str(e)}")
                logger.error(f"Error importing SO {so_number}: {e}")
        
        return {
            "status": "success",
            "message": f"Imported {imported} Sales Orders to store(s)",
            "result": {
                "total_rows": len(df),
                "imported": imported,
                "skipped": skipped,
                "errors": errors[:20]  # Limit errors shown
            }
        }
        
    except Exception as e:
        logger.error(f"Sales Order import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")



async def download_purchases_template():
    """Download CSV template for Purchase Bill import - Includes B2B (with GST/MSME) and unregistered vendor examples"""
    template_data = {
        "bill_number": ["BILL-2026-001", "BILL-2026-002", "BILL-2026-003", "BILL-2026-004"],
        "bill_date": ["2026-02-01", "2026-02-02", "2026-02-03", "2026-02-04"],
        "po_number": ["PO-2026-001", "PO-2026-002", "PO-2026-003", "PO-2026-004"],
        "vendor_name": ["Bosch India Ltd", "Siemens India", "Local Spare Parts", "Filter Supplies Co"],
        "vendor_phone": ["9800000001", "9800000002", "9800000003", "9800000004"],
        "vendor_email": ["supply@bosch.in", "orders@siemens.in", "localspares@gmail.com", "sales@filtersupply.com"],
        "vendor_gst": ["29AAACB1234F1ZP", "27AABCS5678G1ZQ", "", "29AABCF3456K1ZS"],
        "vendor_msme_udyam": ["", "", "", "UDYAM-KA-02-0098765"],
        "vendor_address": ["Sector 18, Electronic City", "Worli, Mumbai", "Gandhi Nagar, Bangalore", "Industrial Area, Hubli"],
        "vendor_city": ["Bangalore", "Mumbai", "Bangalore", "Hubli"],
        "vendor_state": ["Karnataka", "Maharashtra", "Karnataka", "Karnataka"],
        "vendor_pincode": ["560100", "400018", "560032", "580020"],
        "product_name": ["Bosch 8kg Washing Machine", "Siemens Dishwasher", "Spare Parts Kit", "Water Purifier Filter"],
        "hsn_code": ["84501900", "84221100", "84509090", "84212100"],
        "quantity": [20, 10, 50, 100],
        "unit_rate": [35000, 45000, 500, 800],
        "discount_percent": [2, 3, 0, 5],
        "tax_rate": [18, 18, 18, 5],
        "cgst": [6174, 0, 450, 190],
        "sgst": [6174, 0, 450, 190],
        "igst": [0, 8082, 0, 0],
        "payment_mode": ["Bank Transfer", "Bank Transfer", "Cash", "Bank Transfer"],
        "payment_status": ["paid", "paid", "paid", "pending"],
        "due_date": ["", "2026-02-17", "", "2026-03-21"],
        "notes": ["B2B Intra-state CGST+SGST", "B2B Inter-state IGST", "Unregistered vendor - No ITC", "MSME Vendor - 45 day payment mandatory"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{TEMPLATES_DIR}/purchases_import_template.csv"
    df.to_csv(template_path, index=False)
    
    return FileResponse(
        template_path, 
        filename="purchases_import_template.csv",
        media_type="text/csv"
    )


@router.get("/templates/customers")
async def download_customers_template():
    """Download CSV template for Customer import - Includes B2B (with GST/MSME) and B2C examples"""
    template_data = {
        "customer_id": ["CUST-001", "CUST-002", "CUST-003", "CUST-004"],
        "name": ["ABC Electronics Pvt Ltd", "XYZ Home Appliances", "Ramesh Kumar", "Quick Mart MSME"],
        "phone": ["9876543210", "9876543211", "9876543212", "9876543214"],
        "email": ["accounts@abcelectronics.com", "orders@xyzhome.com", "ramesh@gmail.com", "purchase@quickmart.com"],
        "address": ["123 MG Road", "456 Anna Nagar", "789 JP Nagar", "555 HSR Layout"],
        "city": ["Bangalore", "Chennai", "Mysore", "Bangalore"],
        "state": ["Karnataka", "Tamil Nadu", "Karnataka", "Karnataka"],
        "pincode": ["560001", "600040", "570001", "560102"],
        "gst_number": ["29AABCA1234F1ZP", "33AABCX5678G1ZQ", "", "29AABCQ9012H1ZR"],
        "msme_udyam": ["", "", "", "UDYAM-KA-01-0012345"],
        "customer_type": ["b2b", "b2b", "b2c", "b2b_msme"],
        "credit_limit": [500000, 300000, 0, 100000],
        "payment_terms": ["30 days", "15 days", "immediate", "45 days"],
        "notes": ["B2B Registered - Same State", "B2B Registered - Inter-state", "B2C Consumer", "B2B MSME - 45 day payment compliance"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{TEMPLATES_DIR}/customers_import_template.csv"
    df.to_csv(template_path, index=False)
    
    return FileResponse(
        template_path, 
        filename="customers_import_template.csv",
        media_type="text/csv"
    )


@router.get("/templates/products")
async def download_products_template():
    """Download CSV template for Product/Inventory import"""
    template_data = {
        "product_id": ["PROD-001", "PROD-002"],
        "name": ["Bosch 8kg Washing Machine", "Siemens 500L Refrigerator"],
        "model_number": ["WAJ2846SIN", "KA92NVQ30I"],
        "brand": ["Bosch", "Siemens"],
        "category": ["washing-machine", "refrigerator"],
        "hsn_code": ["84501900", "84182100"],
        "purchase_price": [35000, 65000],
        "selling_price": [45000, 85000],
        "mrp": [49990, 95000],
        "stock_quantity": [25, 15],
        "reorder_level": [5, 3],
        "warranty_months": [24, 24],
        "description": ["Front load, inverter motor", "Side by side, frost free"],
        "specifications": ["Capacity:8kg,Type:Front Load", "Capacity:500L,Type:Frost Free"]
    }
    
    df = pd.DataFrame(template_data)
    template_path = f"{TEMPLATES_DIR}/products_import_template.csv"
    df.to_csv(template_path, index=False)
    
    return FileResponse(
        template_path, 
        filename="products_import_template.csv",
        media_type="text/csv"
    )


@router.get("/templates/download/{template_type}")
async def download_template_file(template_type: str):
    """Download Excel templates for B2B/B2C Sales and Purchases"""
    template_files = {
        "sales_b2b_b2c": f"{TEMPLATES_DIR}/sales_b2b_b2c_template.xlsx",
        "purchase_b2b_b2c": f"{TEMPLATES_DIR}/purchase_b2b_b2c_template.xlsx"
    }
    
    if template_type not in template_files:
        raise HTTPException(status_code=404, detail=f"Template not found. Available: {list(template_files.keys())}")
    
    file_path = template_files[template_type]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Template file not found. Please regenerate.")
    
    return FileResponse(
        file_path,
        filename=f"{template_type}_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ============ DATA IMPORT ENDPOINTS ============

def read_file_to_dataframe(file: UploadFile) -> pd.DataFrame:
    """Read uploaded CSV or Excel file into pandas DataFrame"""
    content = file.file.read()
    filename = file.filename.lower()
    
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError("Unsupported file format. Please upload CSV or Excel file.")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    return df


@router.post("/preview-columns")
async def preview_file_columns(file: UploadFile = File(...)):
    """
    Upload a file to preview what columns are detected.
    This helps diagnose import issues by showing exactly what the system sees.
    """
    try:
        df = read_file_to_dataframe(file)
        
        # Get first 5 rows as sample
        sample_data = df.head(5).to_dict(orient='records')
        
        # Clean sample data - handle NaN values
        for row in sample_data:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
                elif hasattr(value, 'item'):  # numpy types
                    row[key] = value.item()
        
        # Analyze numeric columns for GST detection
        numeric_analysis = {}
        for col in df.columns:
            try:
                if df[col].dtype in ['int64', 'float64'] or pd.to_numeric(df[col], errors='coerce').notna().any():
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    numeric_analysis[col] = {
                        "min": float(numeric_col.min()) if pd.notna(numeric_col.min()) else None,
                        "max": float(numeric_col.max()) if pd.notna(numeric_col.max()) else None,
                        "mean": float(numeric_col.mean()) if pd.notna(numeric_col.mean()) else None,
                        "sample_values": [float(v) if pd.notna(v) else None for v in numeric_col.head(3).tolist()]
                    }
            except Exception:
                pass
        
        # Identify likely column mappings
        likely_mappings = {}
        
        # Price/Rate columns
        price_keywords = ['rate', 'price', 'amount', 'value', 'mrp', 'unit']
        for col in df.columns:
            for kw in price_keywords:
                if kw in col:
                    likely_mappings[col] = "Likely price/rate field"
        
        # GST columns
        gst_keywords = ['gst', 'cgst', 'sgst', 'igst', 'tax', 'taxable']
        for col in df.columns:
            for kw in gst_keywords:
                if kw in col:
                    likely_mappings[col] = "Likely GST/tax field"
        
        return {
            "status": "success",
            "filename": file.filename,
            "total_rows": len(df),
            "columns_detected": list(df.columns),
            "column_count": len(df.columns),
            "sample_data": sample_data,
            "numeric_analysis": numeric_analysis,
            "likely_mappings": likely_mappings,
            "tip": "If your unit_price/rate column is detected but GST is being calculated wrong, ensure the 'rate' column contains prices EXCLUDING GST. If your file has CGST/SGST columns, those will be used directly instead of calculating."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview file: {str(e)}")




@router.post("/sales", response_model=ImportResponse)
async def import_sales_data(
    file: UploadFile = File(...),
    update_existing: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import Sales/Invoice data from Tally CSV/Excel export
    
    Supports flexible column names to handle various Tally export formats
    """
    try:
        df = read_file_to_dataframe(file)
        
        logger.info(f"Sales import - columns found: {list(df.columns)}")
        
        imported = 0
        skipped = 0
        errors = []
        
        # Flexible column mapping for various Tally export formats
        # NOTE: More specific variations first, generic ones last
        column_mapping = {
            'invoice_number': ['invoice_number', 'invoice_n', 'invoice_no', 'bill_no', 'bill_number', 'voucher_no', 'voucher_number', 'document_no'],
            'invoice_date': ['invoice_date', 'invoice_d', 'date', 'bill_date', 'voucher_date'],
            'customer_name': ['party_name', 'party', 'customer_name', 'customer', 'buyer_name', 'name', 'party_ledger'],
            'customer_phone': ['customer_phone', 'party_phone', 'phone', 'mobile', 'contact'],
            'customer_email': ['customer_email', 'party_email', 'email'],
            'customer_gstin': ['customer_gstin', 'party_gst', 'gstin', 'gst_number', 'gst_no', 'customer_gst', 'party_gstin'],
            'customer_msme_udyam': ['customer_msme_udyam', 'msme_udyam', 'udyam_number', 'msme_number', 'msme'],
            'customer_address': ['customer_address', 'party_address', 'address', 'billing_address'],
            'customer_city': ['customer_city', 'party_city', 'city'],
            'customer_state': ['customer_state', 'party_state', 'state', 'place_of_supply'],
            'customer_pincode': ['customer_pincode', 'party_pincode', 'pincode', 'pin'],
            'product_name': ['product_name', 'product', 'item_name', 'item', 'particular', 'particulars', 'stock_item', 'goods'],
            'product_model': ['product_model', 'model', 'model_number', 'sku'],
            'hsn_code': ['hsn_code', 'hsn', 'hsn/sac', 'sac_code', 'hsn_sac'],
            'quantity': ['quantity', 'qty', 'units', 'billed_qty'],
            'unit_price': ['unit_price', 'price', 'rate', 'mrp', 'selling_price', 'unit_rate', 'amount_per_unit', 'basic_rate'],
            'line_amount': ['amount', 'line_amount', 'line_total', 'item_amount'],  # Line total (may include GST)
            'discount_percent': ['discount_percent', 'discount', 'disc_%', 'discount_%', 'discount_per', 'disc_per'],
            'discount_amount': ['discount_amount', 'disc_amt', 'discount_amt'],
            'tax_rate': ['tax_rate', 'gst_rate', 'gst_%', 'tax_%', 'gst', 'tax', 'tax_percent', 'gst_percent'],
            'cgst': ['cgst', 'central_gst', 'cgst_amount', 'central_tax', 'cgst_amt'],
            'sgst': ['sgst', 'state_gst', 'sgst_amount', 'state_tax', 'sgst_amt'],
            'igst': ['igst', 'integrated_gst', 'igst_amount', 'integrated_tax', 'igst_amt'],
            'taxable_value': ['taxable_value', 'taxable_amount', 'assessable_value', 'taxable'],
            'payment_mode': ['payment_mode', 'payment_method', 'mode_of_payment', 'payment'],
            'payment_status': ['payment_status', 'status'],
            'due_date': ['due_date', 'payment_due_date', 'due'],
            'order_status': ['order_status', 'order_stat', 'delivery_status'],
            'notes': ['notes', 'narration', 'remarks']
        }
        
        # Log detected column mappings for debugging
        detected_mappings = {}
        for field, possible_cols in column_mapping.items():
            for col in possible_cols:
                # Case-insensitive column matching
                matching_cols = [c for c in df.columns if c.lower().strip() == col.lower()]
                if matching_cols:
                    detected_mappings[field] = matching_cols[0]
                    break
        logger.info(f"Detected column mappings for sales import: {detected_mappings}")
        
        def get_column_value(row, field_name):
            """Get value from row using flexible column mapping (case-insensitive)"""
            possible_columns = column_mapping.get(field_name, [field_name])
            for col in possible_columns:
                # Try exact match first
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val):
                        return val
                # Try case-insensitive match
                matching_cols = [c for c in df.columns if c.lower().strip() == col.lower()]
                for match_col in matching_cols:
                    val = row.get(match_col)
                    if pd.notna(val):
                        return val
            return None
        
        # Find invoice number column (case-insensitive)
        invoice_col = None
        for col in column_mapping['invoice_number']:
            if col in df.columns:
                invoice_col = col
                break
            # Case-insensitive search
            matching = [c for c in df.columns if c.lower().strip() == col.lower()]
            if matching:
                invoice_col = matching[0]
                break
        
        # Group by invoice number for multi-item orders
        if invoice_col:
            grouped = df.groupby(invoice_col)
        else:
            # No invoice column found, treat each row as separate order
            grouped = [(f"ORD-{i+1}", df.iloc[[i]]) for i in range(len(df))]
        
        for invoice_num, group in grouped:
            try:
                first_row = group.iloc[0]
                
                # Check if order already exists
                existing = await db.orders.find_one({"order_number": str(invoice_num)})
                if existing and not update_existing:
                    skipped += 1
                    continue
                
                # Build order items
                items = []
                subtotal = 0
                total_tax = 0
                
                for _, row in group.iterrows():
                    qty = int(get_column_value(row, 'quantity') or 1)
                    tax_rate = float(get_column_value(row, 'tax_rate') or 18)
                    
                    # Get unit price (EXCLUDING GST - this is how Tally exports)
                    unit_price = float(get_column_value(row, 'unit_price') or 0)
                    
                    # Check if GST amounts are provided directly in the file
                    file_cgst = float(get_column_value(row, 'cgst') or 0)
                    file_sgst = float(get_column_value(row, 'sgst') or 0)
                    file_igst = float(get_column_value(row, 'igst') or 0)
                    file_taxable = float(get_column_value(row, 'taxable_value') or 0)
                    
                    # Check if discount is provided as amount or percentage
                    discount_pct = float(get_column_value(row, 'discount_percent') or 0)
                    discount_amt_from_file = float(get_column_value(row, 'discount_amount') or 0)
                    
                    # Calculate taxable amount
                    # Priority: 1) taxable_value from file, 2) unit_price * qty - discount
                    if file_taxable > 0:
                        # Use taxable value directly from file
                        taxable_amount = file_taxable
                        if unit_price == 0 and qty > 0:
                            unit_price = taxable_amount / qty
                        discount_amt = 0  # Already factored in taxable_value
                    else:
                        item_subtotal = qty * unit_price
                        if discount_amt_from_file > 0:
                            discount_amt = discount_amt_from_file
                        else:
                            discount_amt = item_subtotal * (discount_pct / 100)
                        taxable_amount = item_subtotal - discount_amt
                    
                    # Determine GST amounts
                    # Priority: Use GST from file if provided, otherwise calculate
                    if file_cgst > 0 or file_sgst > 0 or file_igst > 0:
                        # GST amounts are provided in the file - use them directly
                        item_cgst = file_cgst
                        item_sgst = file_sgst
                        item_igst = file_igst
                        tax_amount = file_cgst + file_sgst + file_igst
                    else:
                        # Calculate GST from tax rate
                        tax_amount = taxable_amount * (tax_rate / 100)
                        
                        # Determine CGST/SGST vs IGST based on state
                        customer_state = str(get_column_value(row, 'customer_state') or get_column_value(first_row, 'customer_state') or '').upper().strip()
                        seller_state = "KARNATAKA"
                        is_inter_state = customer_state and customer_state != seller_state.upper() and customer_state not in ['', 'KA', 'KARNATAKA']
                        
                        if is_inter_state:
                            item_cgst = 0
                            item_sgst = 0
                            item_igst = tax_amount
                        else:
                            item_cgst = tax_amount / 2
                            item_sgst = tax_amount / 2
                            item_igst = 0
                    
                    item_total = taxable_amount + tax_amount
                    
                    items.append({
                        "product_id": str(uuid.uuid4()),
                        "product_name": str(get_column_value(row, 'product_name') or 'Unknown Item'),
                        "model_number": str(get_column_value(row, 'product_model') or ''),
                        "hsn_code": str(get_column_value(row, 'hsn_code') or ''),
                        "quantity": qty,
                        "price": unit_price,  # Unit price excluding GST
                        "unit_price": unit_price,  # Also store as unit_price
                        "price_inclusive": False,  # IMPORTANT: Tally prices are EXCLUDING GST
                        "discount": discount_amt,
                        "tax_rate": tax_rate,
                        "taxable_amount": round(taxable_amount, 2),
                        "tax": round(tax_amount, 2),
                        "cgst": round(item_cgst, 2),
                        "sgst": round(item_sgst, 2),
                        "igst": round(item_igst, 2),
                        "total": round(item_total, 2)
                    })
                    
                    subtotal += taxable_amount
                    total_tax += tax_amount
                
                # Calculate total GST split
                total_cgst = sum(item.get('cgst', 0) for item in items)
                total_sgst = sum(item.get('sgst', 0) for item in items)
                total_igst = sum(item.get('igst', 0) for item in items)
                
                # Parse date with flexible formats
                invoice_date = get_column_value(first_row, 'invoice_date')
                if invoice_date:
                    if hasattr(invoice_date, 'isoformat'):
                        # Already a datetime object, ensure it has timezone
                        if invoice_date.tzinfo is None:
                            invoice_date = invoice_date.replace(tzinfo=timezone.utc)
                    elif isinstance(invoice_date, str):
                        try:
                            from dateutil import parser
                            invoice_date = parser.parse(invoice_date)
                            if invoice_date.tzinfo is None:
                                invoice_date = invoice_date.replace(tzinfo=timezone.utc)
                        except Exception:
                            invoice_date = datetime.now(timezone.utc)
                    else:
                        invoice_date = datetime.now(timezone.utc)
                else:
                    invoice_date = datetime.now(timezone.utc)
                
                # Determine place of supply for GST
                customer_state = str(get_column_value(first_row, 'customer_state') or '').upper().strip()
                
                # Get B2B identifiers (GSTIN and MSME)
                customer_gstin = str(get_column_value(first_row, 'customer_gstin') or '').strip()
                customer_msme_udyam = str(get_column_value(first_row, 'customer_msme_udyam') or '').strip()
                
                # Determine customer type based on GSTIN
                customer_type = "b2c"  # Default
                if customer_gstin:
                    customer_type = "b2b_msme" if customer_msme_udyam else "b2b"
                
                # Parse due date if provided
                due_date = get_column_value(first_row, 'due_date')
                if due_date:
                    if hasattr(due_date, 'isoformat'):
                        if due_date.tzinfo is None:
                            due_date = due_date.replace(tzinfo=timezone.utc)
                    elif isinstance(due_date, str) and due_date.strip():
                        try:
                            from dateutil import parser
                            due_date = parser.parse(due_date)
                            if due_date.tzinfo is None:
                                due_date = due_date.replace(tzinfo=timezone.utc)
                        except Exception:
                            due_date = None
                    else:
                        due_date = None
                
                # Create or update order
                order_id = str(uuid.uuid4())
                order_data = {
                    "id": order_id,
                    "order_id": order_id,  # Required by MongoDB unique index
                    "order_number": str(invoice_num),
                    "customer_id": str(uuid.uuid4()),
                    "customer_name": str(get_column_value(first_row, 'customer_name') or 'Unknown'),
                    "customer_email": str(get_column_value(first_row, 'customer_email') or ''),
                    "customer_phone": str(get_column_value(first_row, 'customer_phone') or ''),
                    "customer_gstin": customer_gstin,
                    "customer_msme_number": customer_msme_udyam,
                    "customer_type": customer_type,
                    "items": items,
                    "subtotal": round(subtotal, 2),
                    "taxable_amount": round(subtotal, 2),  # Store taxable amount explicitly
                    "tax_amount": round(total_tax, 2),
                    "gst_amount": round(total_tax, 2),
                    "cgst": round(total_cgst, 2),
                    "sgst": round(total_sgst, 2),
                    "igst": round(total_igst, 2),
                    "shipping_charges": 0,
                    "discount_amount": 0,
                    "total_amount": round(subtotal + total_tax, 2),
                    "price_type": "exclusive",  # IMPORTANT: Prices are EXCLUDING GST
                    "import_source": "tally",  # Mark as Tally import
                    "payment_method": str(get_column_value(first_row, 'payment_mode') or 'cod').lower(),
                    # Default to 'completed' for Tally imports as they are historical sales
                    "payment_status": str(get_column_value(first_row, 'payment_status') or 'completed').lower(),
                    "place_of_supply": customer_state or "Karnataka",
                    "due_date": due_date.isoformat() if due_date else None,
                    "shipping_address": {
                        "name": str(get_column_value(first_row, 'customer_name') or ''),
                        "phone": str(get_column_value(first_row, 'customer_phone') or ''),
                        "address_line1": str(get_column_value(first_row, 'customer_address') or ''),
                        "city": str(get_column_value(first_row, 'customer_city') or ''),
                        "state": str(get_column_value(first_row, 'customer_state') or ''),
                        "pincode": str(get_column_value(first_row, 'customer_pincode') or ''),
                        "country": "India"
                    },
                    "order_status": str(get_column_value(first_row, 'order_status') or 'delivered').lower(),
                    "timeline": [{
                        "status": "placed",
                        "timestamp": invoice_date,
                        "message": "Order imported from Tally",
                        "updated_by": "tally_import"
                    }],
                    "customer_notes": str(get_column_value(first_row, 'notes') or ''),
                    "admin_notes": "Imported from Tally",
                    "created_at": invoice_date,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "tally_import"
                }
                
                if existing and update_existing:
                    await db.orders.update_one(
                        {"order_number": str(invoice_num)},
                        {"$set": order_data}
                    )
                else:
                    await db.orders.insert_one(order_data)
                
                # Also update/create customer record
                customer_data = {
                    "id": order_data["customer_id"],
                    "name": order_data["customer_name"],
                    "email": order_data["customer_email"],
                    "phone": order_data["customer_phone"],
                    "gst_number": customer_gstin,
                    "msme_udyam": customer_msme_udyam,
                    "customer_type": customer_type,
                    "address": str(get_column_value(first_row, 'customer_address') or ''),
                    "city": str(get_column_value(first_row, 'customer_city') or ''),
                    "state": str(get_column_value(first_row, 'customer_state') or ''),
                    "pincode": str(get_column_value(first_row, 'customer_pincode') or ''),
                    "last_order_date": invoice_date,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "tally_import"
                }
                
                # Update customer if exists, else insert
                # Use $inc which creates the field with value 0 then increments on insert
                await db.customers.update_one(
                    {"phone": customer_data["phone"]},
                    {
                        "$set": customer_data,
                        "$setOnInsert": {"created_at": invoice_date},
                        "$inc": {"order_count": 1, "total_spent": order_data["total_amount"]}
                    },
                    upsert=True
                )
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {invoice_num}: {str(e)}")
        
        return ImportResponse(
            status="success",
            message=f"Sales import completed. {imported} orders imported, {skipped} skipped.",
            result=ImportResult(
                total_rows=len(df),
                imported=imported,
                skipped=skipped,
                errors=errors[:10]  # Limit errors shown
            )
        )
        
    except Exception as e:
        logger.error(f"Sales import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/purchases", response_model=ImportResponse)
async def import_purchases_data(
    file: UploadFile = File(...),
    update_existing: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import Purchase Bill data from Tally CSV/Excel export
    Supports B2B purchases with GST/MSME fields
    """
    try:
        df = read_file_to_dataframe(file)
        
        imported = 0
        skipped = 0
        errors = []
        
        # Flexible column mapping for purchases
        column_mapping = {
            'bill_number': ['bill_number', 'bill_no', 'invoice_number', 'invoice_no', 'voucher_no'],
            'bill_date': ['bill_date', 'invoice_date', 'date', 'voucher_date'],
            'po_number': ['po_number', 'po_no', 'purchase_order'],
            'vendor_name': ['vendor_name', 'vendor', 'supplier_name', 'supplier', 'party_name'],
            'vendor_phone': ['vendor_phone', 'phone', 'mobile'],
            'vendor_email': ['vendor_email', 'email'],
            'vendor_gst': ['vendor_gst', 'vendor_gstin', 'gstin', 'gst_number', 'supplier_gst'],
            'vendor_msme_udyam': ['vendor_msme_udyam', 'msme_udyam', 'udyam_number', 'msme_number', 'vendor_msme'],
            'vendor_address': ['vendor_address', 'address', 'supplier_address'],
            'vendor_city': ['vendor_city', 'city'],
            'vendor_state': ['vendor_state', 'state', 'place_of_supply'],
            'vendor_pincode': ['vendor_pincode', 'pincode', 'pin'],
            'product_name': ['product_name', 'product', 'item_name', 'item', 'particulars'],
            'hsn_code': ['hsn_code', 'hsn', 'hsn/sac'],
            'quantity': ['quantity', 'qty', 'units'],
            'unit_rate': ['unit_rate', 'rate', 'unit_price', 'price', 'basic_rate'],
            'taxable_value': ['taxable_value', 'taxable_amount', 'assessable_value', 'taxable'],
            'discount_percent': ['discount_percent', 'discount', 'disc_%'],
            'discount_amount': ['discount_amount', 'disc_amt', 'discount_amt'],
            'tax_rate': ['tax_rate', 'gst_rate', 'tax_%', 'gst', 'gst_percent'],
            'cgst': ['cgst', 'central_gst', 'cgst_amount', 'cgst_amt'],
            'sgst': ['sgst', 'state_gst', 'sgst_amount', 'sgst_amt'],
            'igst': ['igst', 'integrated_gst', 'igst_amount', 'igst_amt'],
            'payment_mode': ['payment_mode', 'payment_method', 'mode_of_payment'],
            'payment_status': ['payment_status', 'status'],
            'due_date': ['due_date', 'payment_due_date', 'due'],
            'notes': ['notes', 'narration', 'remarks']
        }
        
        def get_col_value(row, field_name):
            """Get value from row using flexible column mapping"""
            possible_columns = column_mapping.get(field_name, [field_name])
            for col in possible_columns:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val):
                        return val
            return None
        
        # Find grouping column (bill_number or po_number)
        group_col = None
        for col in column_mapping['bill_number']:
            if col in df.columns:
                group_col = col
                break
        if not group_col:
            for col in column_mapping['po_number']:
                if col in df.columns:
                    group_col = col
                    break
        
        # Group by bill/po number
        if group_col:
            grouped = df.groupby(group_col)
        else:
            grouped = [(f"BILL-{i+1}", df.iloc[[i]]) for i in range(len(df))]
        
        for bill_num, group in grouped:
            try:
                first_row = group.iloc[0]
                
                # Check if bill exists
                existing = await db.purchase_bills.find_one({"bill_number": str(bill_num)})
                if existing and not update_existing:
                    skipped += 1
                    continue
                
                # Get vendor GST and MSME
                vendor_gst = str(get_col_value(first_row, 'vendor_gst') or '').strip()
                vendor_msme = str(get_col_value(first_row, 'vendor_msme_udyam') or '').strip()
                vendor_state = str(get_col_value(first_row, 'vendor_state') or '').upper().strip()
                
                # Determine if inter-state (for IGST) or intra-state (CGST+SGST)
                seller_state = "KARNATAKA"  # Default seller state
                is_inter_state = vendor_state and vendor_state != seller_state and vendor_state not in ['', 'KA', 'KARNATAKA']
                
                # Build purchase items
                items = []
                items_subtotal = 0
                total_cgst = 0
                total_sgst = 0
                total_igst = 0
                tax_total = 0
                
                for _, row in group.iterrows():
                    qty = int(get_col_value(row, 'quantity') or 1)
                    rate = float(get_col_value(row, 'unit_rate') or 0)
                    tax_rate = float(get_col_value(row, 'tax_rate') or 18)
                    
                    # Check if GST amounts are provided directly in the file
                    file_cgst = float(get_col_value(row, 'cgst') or 0)
                    file_sgst = float(get_col_value(row, 'sgst') or 0)
                    file_igst = float(get_col_value(row, 'igst') or 0)
                    file_taxable = float(get_col_value(row, 'taxable_value') or 0)
                    
                    # Check if discount is provided as amount or percentage
                    discount_pct = float(get_col_value(row, 'discount_percent') or 0)
                    discount_amt_from_file = float(get_col_value(row, 'discount_amount') or 0)
                    
                    # Calculate taxable amount
                    # Priority: 1) taxable_value from file, 2) rate * qty - discount
                    if file_taxable > 0:
                        taxable = file_taxable
                        if rate == 0 and qty > 0:
                            rate = taxable / qty
                        discount_amt = 0
                    else:
                        item_subtotal = qty * rate
                        if discount_amt_from_file > 0:
                            discount_amt = discount_amt_from_file
                        else:
                            discount_amt = item_subtotal * (discount_pct / 100)
                        taxable = item_subtotal - discount_amt
                    
                    # Determine GST amounts
                    # Priority: Use GST from file if provided, otherwise calculate
                    if file_cgst > 0 or file_sgst > 0 or file_igst > 0:
                        item_cgst = file_cgst
                        item_sgst = file_sgst
                        item_igst = file_igst
                        tax_amt = file_cgst + file_sgst + file_igst
                    else:
                        # Calculate GST from tax rate
                        tax_amt = taxable * (tax_rate / 100)
                        
                        if is_inter_state:
                            item_igst = tax_amt
                            item_cgst = 0
                            item_sgst = 0
                        else:
                            item_cgst = tax_amt / 2
                            item_sgst = tax_amt / 2
                            item_igst = 0
                    
                    item_total = taxable + tax_amt
                    
                    items.append({
                        "product_name": str(get_col_value(row, 'product_name') or ''),
                        "hsn_code": str(get_col_value(row, 'hsn_code') or ''),
                        "quantity": qty,
                        "rate": rate,  # Unit rate excluding GST
                        "unit_price": rate,  # Also store as unit_price
                        "discount": discount_pct,
                        "tax_rate": tax_rate,
                        "taxable_amount": round(taxable, 2),
                        "cgst": round(item_cgst, 2),
                        "sgst": round(item_sgst, 2),
                        "igst": round(item_igst, 2),
                        "tax_amount": round(tax_amt, 2),
                        "total": round(item_total, 2)
                    })
                    
                    items_subtotal += taxable
                    total_cgst += item_cgst
                    total_sgst += item_sgst
                    total_igst += item_igst
                    tax_total += tax_amt
                
                # Parse dates
                bill_date = get_col_value(first_row, 'bill_date')
                if bill_date:
                    if isinstance(bill_date, str):
                        try:
                            from dateutil import parser
                            bill_date = parser.parse(bill_date).strftime('%Y-%m-%d')
                        except Exception:
                            bill_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                    elif hasattr(bill_date, 'strftime'):
                        bill_date = bill_date.strftime('%Y-%m-%d')
                else:
                    bill_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                
                due_date = get_col_value(first_row, 'due_date')
                if due_date:
                    if isinstance(due_date, str) and due_date.strip():
                        try:
                            from dateutil import parser
                            due_date = parser.parse(due_date).strftime('%Y-%m-%d')
                        except Exception:
                            due_date = None
                    elif hasattr(due_date, 'strftime'):
                        due_date = due_date.strftime('%Y-%m-%d')
                    else:
                        due_date = None
                
                # Calculate MSME payment due date (45 days from bill date) if vendor is MSME
                msme_payment_due_date = None
                if vendor_msme:
                    try:
                        from dateutil import parser
                        bill_dt = parser.parse(bill_date)
                        msme_payment_due_date = (bill_dt + timedelta(days=45)).strftime('%Y-%m-%d')
                    except Exception:
                        pass
                
                purchase_data = {
                    "id": str(uuid.uuid4()),
                    "bill_number": str(bill_num),
                    "bill_date": bill_date,
                    "po_number": str(get_col_value(first_row, 'po_number') or ''),
                    "vendor_name": str(get_col_value(first_row, 'vendor_name') or ''),
                    "vendor": {
                        "name": str(get_col_value(first_row, 'vendor_name') or ''),
                        "phone": str(get_col_value(first_row, 'vendor_phone') or ''),
                        "email": str(get_col_value(first_row, 'vendor_email') or ''),
                        "gst_number": vendor_gst,
                        "msme_udyam": vendor_msme,
                        "address": str(get_col_value(first_row, 'vendor_address') or ''),
                        "city": str(get_col_value(first_row, 'vendor_city') or ''),
                        "state": str(get_col_value(first_row, 'vendor_state') or ''),
                        "pincode": str(get_col_value(first_row, 'vendor_pincode') or '')
                    },
                    "vendor_gst": vendor_gst,
                    "vendor_msme_number": vendor_msme,
                    "items": items,
                    "subtotal": round(items_subtotal, 2),
                    "cgst": round(total_cgst, 2),
                    "sgst": round(total_sgst, 2),
                    "igst": round(total_igst, 2),
                    "total_tax": round(tax_total, 2),
                    "grand_total": round(items_subtotal + tax_total, 2),
                    "payment_mode": str(get_col_value(first_row, 'payment_mode') or 'Bank Transfer'),
                    "payment_status": str(get_col_value(first_row, 'payment_status') or 'pending').lower(),
                    "due_date": due_date,
                    "msme_payment_due_date": msme_payment_due_date,
                    "notes": str(get_col_value(first_row, 'notes') or ''),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "tally_import",
                    "source": "tally_import"
                }
                
                if existing and update_existing:
                    await db.purchase_bills.update_one(
                        {"bill_number": str(bill_num)},
                        {"$set": purchase_data}
                    )
                else:
                    await db.purchase_bills.insert_one(purchase_data)
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Bill {bill_num}: {str(e)}")
        
        return ImportResponse(
            status="success",
            message=f"Purchase import completed. {imported} POs imported, {skipped} skipped.",
            result=ImportResult(
                total_rows=len(df),
                imported=imported,
                skipped=skipped,
                errors=errors[:10]
            )
        )
        
    except Exception as e:
        logger.error(f"Purchase import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/customers", response_model=ImportResponse)
async def import_customers_data(
    file: UploadFile = File(...),
    update_existing: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import Customer data from Tally CSV/Excel export
    Supports B2B and B2C customers with GST/MSME fields
    """
    try:
        df = read_file_to_dataframe(file)
        
        imported = 0
        skipped = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                phone = str(row.get('phone', '')).strip()
                if not phone:
                    errors.append(f"Row {idx+1}: Missing phone number")
                    continue
                
                # Check if customer exists
                existing = await db.customers.find_one({"phone": phone})
                if existing and not update_existing:
                    skipped += 1
                    continue
                
                # Get GST and MSME numbers
                gst_number = str(row.get('gst_number', row.get('gstin', ''))).strip()
                msme_udyam = str(row.get('msme_udyam', row.get('udyam_number', ''))).strip()
                
                # Determine customer type
                customer_type = str(row.get('customer_type', '')).lower().strip()
                if not customer_type:
                    if gst_number:
                        customer_type = "b2b_msme" if msme_udyam else "b2b"
                    else:
                        customer_type = "b2c"
                
                customer_data = {
                    "id": str(row.get('customer_id', uuid.uuid4())),
                    "name": str(row.get('name', '')),
                    "phone": phone,
                    "email": str(row.get('email', '')),
                    "address": str(row.get('address', '')),
                    "city": str(row.get('city', '')),
                    "state": str(row.get('state', '')),
                    "pincode": str(row.get('pincode', '')),
                    "gst_number": gst_number,
                    "msme_udyam": msme_udyam,
                    "customer_type": customer_type,
                    "credit_limit": float(row.get('credit_limit', 0) or 0),
                    "payment_terms": str(row.get('payment_terms', 'immediate')),
                    "notes": str(row.get('notes', '')),
                    "total_spent": 0,
                    "order_count": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "tally_import"
                }
                
                if existing and update_existing:
                    await db.customers.update_one(
                        {"phone": phone},
                        {"$set": customer_data}
                    )
                else:
                    await db.customers.insert_one(customer_data)
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")
        
        return ImportResponse(
            status="success",
            message=f"Customer import completed. {imported} customers imported, {skipped} skipped.",
            result=ImportResult(
                total_rows=len(df),
                imported=imported,
                skipped=skipped,
                errors=errors[:10]
            )
        )
        
    except Exception as e:
        logger.error(f"Customer import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products", response_model=ImportResponse)
async def import_products_data(
    file: UploadFile = File(...),
    update_existing: bool = Form(default=False),
    db = Depends(get_db)
):
    """
    Import Product/Inventory data from Tally CSV/Excel export
    """
    try:
        df = read_file_to_dataframe(file)
        
        imported = 0
        skipped = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                model_number = str(row.get('model_number', '')).strip()
                product_name = str(row.get('name', '')).strip()
                
                if not product_name:
                    errors.append(f"Row {idx+1}: Missing product name")
                    continue
                
                # Check if product exists
                existing = await db.products.find_one({
                    "$or": [
                        {"model_number": model_number},
                        {"name": product_name}
                    ]
                }) if model_number else await db.products.find_one({"name": product_name})
                
                if existing and not update_existing:
                    skipped += 1
                    continue
                
                # Parse specifications
                specs_str = str(row.get('specifications', ''))
                specifications = []
                if specs_str:
                    for spec in specs_str.split(','):
                        if ':' in spec:
                            name, value = spec.split(':', 1)
                            specifications.append({
                                "name": name.strip(),
                                "value": value.strip()
                            })
                
                product_data = {
                    "id": str(row.get('product_id', uuid.uuid4())),
                    "name": product_name,
                    "model_number": model_number,
                    "brand": str(row.get('brand', '')),
                    "category": str(row.get('category', '')).lower().replace(' ', '-'),
                    "hsn_code": str(row.get('hsn_code', '')),
                    "purchase_price": float(row.get('purchase_price', 0)),
                    "price": float(row.get('selling_price', 0)),
                    "mrp": float(row.get('mrp', 0)),
                    "stock_quantity": int(row.get('stock_quantity', 0)),
                    "reorder_level": int(row.get('reorder_level', 5)),
                    "warranty_period": f"{int(row.get('warranty_months', 24))} months",
                    "description": str(row.get('description', '')),
                    "specifications": specifications,
                    "images": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": "tally_import",
                    # Hide from storefront until reviewed in Incomplete Products Manager
                    "is_listed": False,
                    "review_status": "pending_review",
                }
                
                if existing and update_existing:
                    await db.products.update_one(
                        {"_id": existing["_id"]},
                        {"$set": product_data}
                    )
                else:
                    await db.products.insert_one(product_data)
                
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx+1}: {str(e)}")
        
        return ImportResponse(
            status="success",
            message=f"Product import completed. {imported} products imported, {skipped} skipped.",
            result=ImportResult(
                total_rows=len(df),
                imported=imported,
                skipped=skipped,
                errors=errors[:10]
            )
        )
        
    except Exception as e:
        logger.error(f"Product import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ IMPORT STATUS & HISTORY ============

@router.get("/history")
async def get_import_history(db = Depends(get_db)):
    """Get history of all imports"""
    try:
        # Count imported records by source
        sales_count = await db.orders.count_documents({"source": "tally_import"})
        purchases_count = await db.purchases.count_documents({"source": "tally_import"})
        customers_count = await db.customers.count_documents({"source": "tally_import"})
        products_count = await db.products.count_documents({"source": "tally_import"})
        
        return {
            "status": "success",
            "import_summary": {
                "sales_orders": sales_count,
                "purchase_orders": purchases_count,
                "customers": customers_count,
                "products": products_count,
                "total_records": sales_count + purchases_count + customers_count + products_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/{data_type}")
async def clear_imported_data(data_type: str, db = Depends(get_db)):
    """Clear all imported data of a specific type (for testing)"""
    try:
        collection_map = {
            "sales": "orders",
            "purchases": "purchases",
            "customers": "customers",
            "products": "products"
        }
        
        if data_type not in collection_map:
            raise HTTPException(status_code=400, detail=f"Invalid data type. Use: {list(collection_map.keys())}")
        
        collection = db[collection_map[data_type]]
        result = await collection.delete_many({"source": "tally_import"})
        
        return {
            "status": "success",
            "message": f"Deleted {result.deleted_count} {data_type} records imported from Tally"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ AI SALES INVOICE SCANNER ============

import base64

SALES_INVOICE_UPLOAD_DIR = "/app/backend/uploads/sales_invoices"
os.makedirs(SALES_INVOICE_UPLOAD_DIR, exist_ok=True)

@router.post("/scan-sales-invoice")
async def scan_sales_invoice_with_ai(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    AI-powered sales invoice scanning
    Upload PDF or image of sales invoice, AI extracts all details
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename.lower()
        
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save file temporarily for AI extraction
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=file_ext, prefix="sales_invoice_", delete=False) as tmp_f:
            tmp_f.write(content)
            saved_path = tmp_f.name
        
        # Determine mime type
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Use Gemini to extract invoice data
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
            
            extraction_prompt = """You are an expert invoice data extractor. Analyze this SALES invoice/bill and extract ALL information in the following JSON format. Be precise with numbers and GST calculations.

Extract and return ONLY a valid JSON object with this structure:
{
    "invoice_number": "sales invoice/bill number from the document",
    "invoice_date": "YYYY-MM-DD format",
    "customer": {
        "name": "customer/buyer company/person name",
        "phone": "phone number if visible",
        "email": "email if visible",
        "gst_number": "GSTIN number if available (15 characters)",
        "address": "full address",
        "city": "city name",
        "state": "state name",
        "pincode": "PIN code"
    },
    "items": [
        {
            "product_name": "product/item description",
            "model_number": "model/SKU if visible",
            "hsn_code": "HSN/SAC code",
            "quantity": number,
            "unit_price": unit_price_number,
            "discount_percent": discount_percentage_number,
            "tax_rate": GST_rate_number
        }
    ],
    "subtotal": taxable_amount_number,
    "cgst": cgst_amount_number,
    "sgst": sgst_amount_number,
    "igst": igst_amount_number,
    "other_charges": shipping_or_other_charges_number,
    "round_off": round_off_amount_number,
    "grand_total": final_total_number,
    "payment_mode": "cash/upi/card/bank_transfer/credit if mentioned",
    "payment_status": "paid/pending/partial if mentioned"
}

Important:
- All number fields should be numbers, not strings
- If a field is not visible/found, use empty string for text fields and 0 for number fields
- Extract ALL line items from the invoice
- GST numbers in India are 15 characters (e.g., 29AAECB6071D1ZS)
- Parse dates carefully and convert to YYYY-MM-DD format
- Return ONLY the JSON object, no other text"""

            llm_key = os.environ.get('EMERGENT_LLM_KEY', '') or os.environ.get('LLM_KEY', '')
            
            if not llm_key:
                raise ValueError("No LLM key configured. Please configure EMERGENT_LLM_KEY in backend/.env")
            
            # Initialize LlmChat with Gemini
            session_id = f"sales_invoice_scan_{file_id}"
            llm = LlmChat(
                api_key=llm_key,
                session_id=session_id,
                system_message="You are an expert invoice data extractor. Extract data from invoices accurately."
            ).with_model("gemini", "gemini-2.5-flash")
            
            # FileContentWithMimeType requires file_path
            file_content = FileContentWithMimeType(
                file_path=saved_path,
                mime_type=mime_type
            )
            
            # Create user message with text and file
            user_msg = UserMessage(
                text=extraction_prompt,
                file_contents=[file_content]
            )
            
            # Send message with file
            response = await llm.send_message(user_message=user_msg)
            
            # Parse the response
            import re
            
            response_text = response
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                raise ValueError("Could not find JSON in AI response")
            
            extracted_data = json.loads(json_match.group())
            
            # Store the uploaded file reference
            extracted_data['uploaded_file'] = {
                'file_id': file_id,
                'filename': file.filename,
                'file_path': saved_path,
                'mime_type': mime_type,
                'uploaded_at': datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "status": "success",
                "message": "Sales invoice scanned successfully",
                "extracted_data": extracted_data
            }
            
        except Exception as ai_error:
            logger.error(f"AI extraction failed: {str(ai_error)}")
            return {
                "status": "error",
                "message": f"AI extraction failed: {str(ai_error)}",
                "extracted_data": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales invoice scan error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-scanned-sales-invoice")
async def save_scanned_sales_invoice(
    invoice_data: Dict[str, Any],
    db = Depends(get_db)
):
    """
    Save scanned sales invoice data to orders collection
    """
    try:
        invoice_number = invoice_data.get('invoice_number')
        if not invoice_number:
            raise HTTPException(status_code=400, detail="Invoice number is required")
        
        # Check if already exists
        existing = await db.orders.find_one({"order_number": invoice_number})
        if existing:
            raise HTTPException(status_code=400, detail=f"Order with invoice number {invoice_number} already exists")
        
        # Parse invoice date
        invoice_date = invoice_data.get('invoice_date')
        if invoice_date:
            try:
                from dateutil import parser
                invoice_date = parser.parse(invoice_date).replace(tzinfo=timezone.utc).isoformat()
            except Exception:
                invoice_date = datetime.now(timezone.utc).isoformat()
        else:
            invoice_date = datetime.now(timezone.utc).isoformat()
        
        # Build items
        items = []
        subtotal = 0
        total_tax = 0
        
        for item in invoice_data.get('items', []):
            qty = int(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0))
            discount_pct = float(item.get('discount_percent', 0))
            tax_rate = float(item.get('tax_rate', 18))
            
            item_subtotal = qty * unit_price
            discount_amt = item_subtotal * (discount_pct / 100)
            taxable_amount = item_subtotal - discount_amt
            tax_amount = taxable_amount * (tax_rate / 100)
            item_total = taxable_amount + tax_amount
            
            items.append({
                "product_id": str(uuid.uuid4()),
                "product_name": item.get('product_name', 'Unknown Item'),
                "model_number": item.get('model_number', ''),
                "hsn_code": item.get('hsn_code', ''),
                "quantity": qty,
                "price": unit_price,
                "discount": discount_amt,
                "tax_rate": tax_rate,
                "tax": tax_amount,
                "total": item_total
            })
            
            subtotal += taxable_amount
            total_tax += tax_amount
        
        # Get customer info
        customer = invoice_data.get('customer', {})
        
        # Create order
        order_id = str(uuid.uuid4())
        order_data = {
            "id": order_id,
            "order_id": order_id,
            "order_number": invoice_number,
            "customer_id": str(uuid.uuid4()),
            "customer_name": customer.get('name', 'Unknown'),
            "customer_email": customer.get('email', ''),
            "customer_phone": customer.get('phone', ''),
            "items": items,
            "subtotal": round(subtotal, 2),
            "tax_amount": round(total_tax, 2),
            "shipping_charges": float(invoice_data.get('other_charges', 0)),
            "discount_amount": 0,
            "total_amount": float(invoice_data.get('grand_total', subtotal + total_tax)),
            "payment_method": invoice_data.get('payment_mode', 'cash').lower(),
            "payment_status": invoice_data.get('payment_status', 'completed').lower(),
            "shipping_address": {
                "name": customer.get('name', ''),
                "phone": customer.get('phone', ''),
                "address_line1": customer.get('address', ''),
                "city": customer.get('city', ''),
                "state": customer.get('state', ''),
                "pincode": customer.get('pincode', ''),
                "country": "India"
            },
            "order_status": "delivered",
            "timeline": [{
                "status": "placed",
                "timestamp": invoice_date,
                "message": "Order imported from scanned invoice",
                "updated_by": "ai_scanner"
            }],
            "customer_notes": "",
            "admin_notes": "Imported from AI-scanned invoice",
            "created_at": invoice_date,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "ai_scan",
            "scanned_file": invoice_data.get('uploaded_file')
        }
        
        await db.orders.insert_one(order_data)
        
        # Also create/update customer record
        if customer.get('phone'):
            await db.customers.update_one(
                {"phone": customer.get('phone')},
                {
                    "$set": {
                        "name": customer.get('name', ''),
                        "email": customer.get('email', ''),
                        "phone": customer.get('phone'),
                        "address": customer.get('address', ''),
                        "city": customer.get('city', ''),
                        "state": customer.get('state', ''),
                        "pincode": customer.get('pincode', ''),
                        "gst_number": customer.get('gst_number', ''),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "source": "ai_scan"
                    },
                    "$setOnInsert": {"created_at": invoice_date},
                    "$inc": {"order_count": 1, "total_spent": order_data["total_amount"]}
                },
                upsert=True
            )
        
        return {
            "status": "success",
            "message": f"Sales invoice {invoice_number} saved successfully",
            "order_id": order_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save scanned invoice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ============ AI SALES ORDER SCANNER ============

# Create uploads directory for SO scans
SO_UPLOAD_DIR = "/app/backend/uploads/so_scans"
os.makedirs(SO_UPLOAD_DIR, exist_ok=True)


@router.post("/scan-sales-order")
async def scan_sales_order_with_ai(
    file: UploadFile = File(...),
    store_code: str = Form(default="HRBR"),
    db = Depends(get_db)
):
    """
    AI-powered Sales Order scanning for FY transition.
    Upload PDF or image of old SO, AI extracts all details and creates the SO.
    
    - Supports PDF, PNG, JPG, JPEG, WEBP
    - Uses custom SO number from document (for old FY SOs)
    - Backdates to the date in the document
    - Assigns to specified store
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename.lower()
        
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Validate store exists
        store = await db.stores.find_one({"code": store_code.upper()})
        if not store:
            store = await db.stores.find_one({"code": {"$regex": f"^{store_code}", "$options": "i"}})
            if not store:
                raise HTTPException(status_code=400, detail=f"Store '{store_code}' not found")
        
        store_code = store.get("code", store_code.upper())
        
        # Save file temporarily for AI extraction
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=file_ext, prefix="so_scan_", delete=False) as tmp_f:
            tmp_f.write(content)
            saved_path = tmp_f.name
        
        # Determine mime type
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Use Gemini to extract SO data
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
            
            extraction_prompt = """You are an expert Sales Order data extractor. Analyze this Sales Order document and extract ALL information in the following JSON format. Be precise with numbers and GST calculations.

Extract and return ONLY a valid JSON object with this structure:
{
    "so_number": "Sales Order number from the document (IMPORTANT: use the EXACT number shown)",
    "so_date": "YYYY-MM-DD format (date when SO was created)",
    "expected_delivery_date": "YYYY-MM-DD format if mentioned, else null",
    "customer": {
        "name": "customer/buyer name",
        "phone": "phone number if visible",
        "email": "email if visible",
        "gstin": "GSTIN number (15 characters) if visible",
        "billing_address": "billing address",
        "billing_city": "city",
        "billing_state": "state",
        "billing_pincode": "PIN code",
        "shipping_address": "shipping/delivery address if different"
    },
    "items": [
        {
            "product_name": "product/item description",
            "model_number": "model number/SKU if visible",
            "hsn_code": "HSN/SAC code if visible",
            "quantity": number,
            "unit_price": price_per_unit_number,
            "discount_percent": discount_percentage_number_or_0,
            "tax_rate": GST_rate_number_usually_18_or_28
        }
    ],
    "delivery_charges": delivery_or_shipping_charges_number_or_0,
    "discount_amount": overall_discount_amount_or_0,
    "subtotal": subtotal_before_tax_number,
    "total_tax": total_gst_amount_number,
    "grand_total": final_total_amount_number,
    "payment_mode": "Cash/UPI/Card/Bank Transfer/Credit - if visible",
    "advance_paid": advance_amount_paid_or_0,
    "notes": "any additional notes or remarks visible on the SO"
}

Important:
- All number fields should be numbers, not strings
- If a field is not visible/found, use empty string for text fields and 0 for number fields
- Extract ALL line items from the SO
- The SO_NUMBER is CRITICAL - extract the exact document number shown (e.g., "HRBR-SO-2025-0045")
- Parse dates carefully and convert to YYYY-MM-DD format (Indian dates may be DD/MM/YYYY)
- GST numbers in India are 15 characters
- Return ONLY the JSON object, no other text"""

            llm_key = os.environ.get('EMERGENT_LLM_KEY', '') or os.environ.get('LLM_KEY', '')
            
            if not llm_key:
                raise ValueError("No LLM key configured. Please configure EMERGENT_LLM_KEY.")
            
            # Initialize LlmChat with Gemini
            session_id = f"so_scan_{file_id}"
            llm = LlmChat(
                api_key=llm_key,
                session_id=session_id,
                system_message="You are an expert Sales Order data extractor. Extract data accurately."
            ).with_model("gemini", "gemini-2.5-flash")
            
            # FileContentWithMimeType with saved file
            file_content = FileContentWithMimeType(
                file_path=saved_path,
                mime_type=mime_type
            )
            
            # Create user message with text and file
            user_msg = UserMessage(
                text=extraction_prompt,
                file_contents=[file_content]
            )
            
            # Send message with file
            response = await llm.send_message(user_message=user_msg)
            
            # Parse the response
            import re
            
            response_text = response
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract JSON from AI response")
            
            # Add metadata
            extracted_data['so_file_url'] = f"/api/tally-import/so-file/{file_id}{file_ext}"
            extracted_data['extraction_status'] = 'success'
            extracted_data['store_code'] = store_code
            
            return {
                "status": "success",
                "message": "Sales Order scanned successfully",
                "extracted_data": extracted_data
            }
            
        except ImportError:
            logger.error("emergentintegrations not installed")
            raise HTTPException(
                status_code=500, 
                detail="AI service not available. Please configure LLM integration."
            )
        except Exception as ai_error:
            logger.error(f"AI extraction failed: {ai_error}")
            # Return partial success with file saved
            return {
                "status": "partial",
                "message": "File uploaded but AI extraction failed. Please enter details manually.",
                "so_file_url": f"/api/tally-import/so-file/{file_id}{file_ext}",
                "store_code": store_code,
                "error": str(ai_error)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SO scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/so-file/{filename}")
async def get_so_file(filename: str):
    """Serve uploaded SO files"""
    file_path = f"{SO_UPLOAD_DIR}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@router.post("/save-scanned-invoice-store")
async def save_scanned_sales_invoice_store(
    so_data: dict,
    db = Depends(get_db)
):
    """
    Save the AI-extracted document data as a STORE SALES INVOICE (offline_invoices,
    document_type='invoice'). Mirrors save_scanned_sales_order but writes an invoice.
    """
    try:
        so_number = so_data.get('so_number') or so_data.get('invoice_number')
        store_code = so_data.get('store_code', 'HRBR')

        if not so_number:
            raise HTTPException(status_code=400, detail="Invoice number is required")

        existing = await db.offline_invoices.find_one({"invoice_number": so_number})
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Document {so_number} already exists"
            )

        store = await db.stores.find_one({"code": store_code.upper()})
        if not store:
            store = await db.stores.find_one({})
            store_code = store.get("code", "HRBR") if store else "HRBR"

        store_details = {}
        if store:
            store_details = {
                "code": store.get("code", store_code.upper()),
                "name": store.get("name", ""),
                "type": store.get("type", "Store"),
                "address": store.get("address", ""),
                "city": store.get("city", ""),
                "state": store.get("state", ""),
                "pincode": store.get("pincode", ""),
                "phone": store.get("phone", ""),
                "email": store.get("email", ""),
                "invoice_prefix": store.get("invoice_prefix", store_code.upper()),
                "so_prefix": store.get("so_prefix", ""),
                "gst_number": store.get("gst_number", ""),
                "pan_number": store.get("pan_number", ""),
                "tagline": store.get("tagline", ""),
                "is_warehouse": store.get("is_warehouse", False)
            }

        customer_data = so_data.get('customer', {})
        billing_address_str = customer_data.get('billing_address', '')
        billing_city = customer_data.get('billing_city', '')
        billing_state = customer_data.get('billing_state', 'Karnataka')
        billing_pincode = customer_data.get('billing_pincode', '')
        shipping_address_str = customer_data.get('shipping_address') or billing_address_str
        customer = {
            "name": customer_data.get('name', 'Walk-in Customer'),
            "phone": customer_data.get('phone', ''),
            "email": customer_data.get('email', ''),
            "gstin": customer_data.get('gstin', ''),
            "address": billing_address_str,
            "city": billing_city,
            "state": billing_state,
            "pincode": billing_pincode,
            "billing_name": '',
            "billing_address": billing_address_str,
            "billing_city": billing_city,
            "billing_state": billing_state,
            "billing_pincode": billing_pincode,
            "shipping_same_as_billing": not bool(customer_data.get('shipping_address')),
            "shipping_name": '',
            "shipping_address": shipping_address_str,
            "shipping_city": billing_city,
            "shipping_state": billing_state,
            "shipping_pincode": billing_pincode,
        }

        raw_items = so_data.get('items', [])
        items = []
        subtotal = 0
        tax_total = 0

        for item in raw_items:
            qty = int(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0))  # taxable (pre-tax) amount per unit, as extracted by AI
            tax_rate = float(item.get('tax_rate', 18))
            discount_pct = float(item.get('discount_percent', 0))

            gross_taxable = unit_price * qty
            discount_amount = gross_taxable * (discount_pct / 100)
            taxable_amount = gross_taxable - discount_amount
            tax_amount = taxable_amount * (tax_rate / 100)
            final_price = taxable_amount + tax_amount

            items.append({
                "product_name": item.get('product_name', 'Unknown Product'),
                "model_number": item.get('model_number', ''),
                "hsn_code": item.get('hsn_code', ''),
                "quantity": qty,
                "rate": unit_price,
                "discount": discount_pct,
                "tax_rate": tax_rate,
                "gross_amount": round(gross_taxable, 2),
                "discount_amount": round(discount_amount, 2),
                "taxable_amount": round(taxable_amount, 2),
                "tax_amount": round(tax_amount, 2),
                "cgst": round(tax_amount / 2, 2),
                "sgst": round(tax_amount / 2, 2),
                "total": round(final_price, 2)
            })

            subtotal += taxable_amount
            tax_total += tax_amount

        delivery_charges = float(so_data.get('delivery_charges', 0))
        items_total = sum(item['total'] for item in items)
        computed_total_amount = items_total + delivery_charges

        subtotal = float(so_data.get('subtotal') or subtotal)
        tax_total = float(so_data.get('total_tax') or tax_total)
        total_amount = float(so_data.get('grand_total') or computed_total_amount)

        so_date = so_data.get('so_date') or so_data.get('invoice_date') or datetime.now().strftime('%Y-%m-%d')
        expected_delivery = so_data.get('expected_delivery_date') or so_date

        inv_id = str(uuid.uuid4())
        inv_doc = {
            "id": inv_id,
            "invoice_number": so_number,
            "store_code": store_code.upper(),
            "store_details": store_details,
            "document_type": "invoice",
            "customer": customer,
            "customer_name": customer.get('name'),
            "customer_phone": customer.get('phone'),
            "customer_email": customer.get('email'),
            "customer_address": billing_address_str,
            "items": items,
            "subtotal": round(subtotal, 2),
            "tax_total": round(tax_total, 2),
            "cgst_total": round(tax_total / 2, 2),
            "sgst_total": round(tax_total / 2, 2),
            "delivery_charges": round(delivery_charges, 2),
            "total_amount": round(total_amount, 2),
            "payment_mode": so_data.get('payment_mode', 'Cash'),
            "payment_status": so_data.get('payment_status', 'pending'),
            "advance_paid": float(so_data.get('advance_paid', 0)),
            "status": "ready_for_delivery",
            "immediate_delivery": True,
            "expected_delivery_date": expected_delivery,
            "invoice_date": so_date,
            "notes": so_data.get('notes', ''),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "import_source": "ai_scan",
            "so_file_url": so_data.get('so_file_url', ''),
            "imported_at": datetime.now(timezone.utc).isoformat()
        }

        await db.offline_invoices.insert_one(inv_doc)

        return {
            "status": "success",
            "message": f"Sales Invoice {so_number} created successfully",
            "so": {
                "id": inv_id,
                "so_number": so_number,
                "store_code": store_code,
                "total_amount": round(total_amount, 2),
                "customer_name": customer.get('name')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save invoice: {str(e)}")


@router.post("/save-scanned-so")
async def save_scanned_sales_order(
    so_data: dict,
    db = Depends(get_db)
):
    """
    Save the AI-extracted Sales Order data to database.
    This endpoint is called after user reviews/edits the extracted data.
    """
    try:
        so_number = so_data.get('so_number')
        store_code = so_data.get('store_code', 'HRBR')
        
        if not so_number:
            raise HTTPException(status_code=400, detail="SO number is required")
        
        # Check for duplicate
        existing = await db.offline_invoices.find_one({"invoice_number": so_number})
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Sales Order {so_number} already exists"
            )
        
        # Validate store
        store = await db.stores.find_one({"code": store_code.upper()})
        if not store:
            store = await db.stores.find_one({})  # Fallback to first store
            store_code = store.get("code", "HRBR") if store else "HRBR"
        
        # Parse customer data
        customer_data = so_data.get('customer', {})
        customer = {
            "name": customer_data.get('name', 'Walk-in Customer'),
            "phone": customer_data.get('phone', ''),
            "email": customer_data.get('email', ''),
            "gstin": customer_data.get('gstin', ''),
            "billing_address": {
                "address_line1": customer_data.get('billing_address', ''),
                "city": customer_data.get('billing_city', ''),
                "state": customer_data.get('billing_state', 'Karnataka'),
                "pincode": customer_data.get('billing_pincode', '')
            },
            "shipping_address": {
                "address_line1": customer_data.get('shipping_address') or customer_data.get('billing_address', ''),
                "city": customer_data.get('billing_city', ''),
                "state": customer_data.get('billing_state', 'Karnataka'),
                "pincode": customer_data.get('billing_pincode', '')
            }
        }
        
        # Parse items
        raw_items = so_data.get('items', [])
        items = []
        subtotal = 0
        tax_total = 0
        
        for item in raw_items:
            qty = int(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0))
            tax_rate = float(item.get('tax_rate', 18))
            discount_pct = float(item.get('discount_percent', 0))
            
            # Calculate (assuming inclusive pricing like store billing)
            gross_amount = unit_price * qty
            discount_amount = gross_amount * (discount_pct / 100)
            final_price = gross_amount - discount_amount
            
            # GST is inclusive
            taxable_amount = final_price / (1 + tax_rate / 100)
            tax_amount = final_price - taxable_amount
            
            items.append({
                "product_name": item.get('product_name', 'Unknown Product'),
                "model_number": item.get('model_number', ''),
                "hsn_code": item.get('hsn_code', ''),
                "quantity": qty,
                "rate": unit_price,
                "discount": discount_pct,
                "tax_rate": tax_rate,
                "gross_amount": round(gross_amount, 2),
                "discount_amount": round(discount_amount, 2),
                "taxable_amount": round(taxable_amount, 2),
                "tax_amount": round(tax_amount, 2),
                "cgst": round(tax_amount / 2, 2),
                "sgst": round(tax_amount / 2, 2),
                "total": round(final_price, 2)
            })
            
            subtotal += taxable_amount
            tax_total += tax_amount
        
        # Calculate totals
        delivery_charges = float(so_data.get('delivery_charges', 0))
        items_total = sum(item['total'] for item in items)
        total_amount = items_total + delivery_charges
        
        # Parse dates
        so_date = so_data.get('so_date', datetime.now().strftime('%Y-%m-%d'))
        expected_delivery = so_data.get('expected_delivery_date') or so_date
        
        # Create SO document
        so_id = str(uuid.uuid4())
        so_doc = {
            "id": so_id,
            "invoice_number": so_number,
            "store_code": store_code.upper(),
            "document_type": "sales_order",
            "customer": customer,
            "items": items,
            "subtotal": round(subtotal, 2),
            "tax_total": round(tax_total, 2),
            "cgst_total": round(tax_total / 2, 2),
            "sgst_total": round(tax_total / 2, 2),
            "delivery_charges": round(delivery_charges, 2),
            "total_amount": round(total_amount, 2),
            "payment_mode": so_data.get('payment_mode', 'Cash'),
            "payment_status": "pending",
            "advance_paid": float(so_data.get('advance_paid', 0)),
            "status": "pending_delivery",
            "immediate_delivery": False,
            "expected_delivery_date": expected_delivery,
            "invoice_date": so_date,
            "notes": so_data.get('notes', ''),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "import_source": "ai_scan",
            "so_file_url": so_data.get('so_file_url', ''),
            "imported_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.offline_invoices.insert_one(so_doc)
        
        return {
            "status": "success",
            "message": f"Sales Order {so_number} created successfully",
            "so": {
                "id": so_id,
                "so_number": so_number,
                "store_code": store_code,
                "total_amount": round(total_amount, 2),
                "customer_name": customer.get('name')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save scanned SO error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
