"""
Admin Data Management Routes
Super Admin only - Delete data, manage backups, control edit permissions
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict
from database import get_db
from datetime import datetime, timezone
import json
import os
import jwt

router = APIRouter(prefix="/admin", tags=["Admin Data Management"])

JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "your-secret-key")

class DeleteDataRequest(BaseModel):
    collections: List[str]

class EditPermissionsRequest(BaseModel):
    permissions: Dict[str, str]

async def verify_admin(authorization: str = Header(None)):
    """Verify the user is an admin (any role: admin, super_admin, accountant, store_manager)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_super_admin(authorization: str = Header(None)):
    """Verify the user is a super_admin"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Check role from token
        if payload.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Super Admin access required")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/data-stats")
async def get_data_stats(
    db=Depends(get_db),
    admin=Depends(verify_admin)
):
    """Get count of records in each collection"""
    try:
        collections = [
            'orders', 'offline_invoices', 'quotations',
            'purchase_orders', 'purchase_bills',
            'vouchers', 'journal_entries', 'credit_debit_notes', 'expenses',
            'stock_transfers', 'delivery_challans'
        ]
        
        stats = {}
        for coll in collections:
            try:
                count = await db[coll].count_documents({})
                stats[coll] = count
            except Exception:
                stats[coll] = 0
        
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete-data")
async def delete_data(
    request: DeleteDataRequest,
    db=Depends(get_db),
    admin=Depends(verify_super_admin)
):
    """Delete data from selected collections - Super Admin only"""
    try:
        allowed_collections = [
            'orders', 'offline_invoices', 'quotations',
            'purchase_orders', 'purchase_bills',
            'vouchers', 'journal_entries', 'credit_debit_notes', 'expenses',
            'stock_transfers', 'delivery_challans'
        ]
        
        # Validate collections
        for coll in request.collections:
            if coll not in allowed_collections:
                raise HTTPException(status_code=400, detail=f"Collection '{coll}' is not allowed to be deleted")
        
        # Log the deletion action
        await db.audit_logs.insert_one({
            "action": "data_deletion",
            "collections": request.collections,
            "performed_by": admin.get("sub"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Delete data from each collection
        deleted_counts = {}
        for coll in request.collections:
            result = await db[coll].delete_many({})
            deleted_counts[coll] = result.deleted_count
        
        return {
            "status": "success",
            "message": "Data deleted successfully",
            "deleted_counts": deleted_counts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/edit-permissions")
async def get_edit_permissions(
    db=Depends(get_db),
    admin=Depends(verify_admin)
):
    """Get current edit permissions - Any admin can view"""
    try:
        settings = await db.system_settings.find_one({"type": "edit_permissions"}, {"_id": 0})
        
        if not settings:
            # Default permissions - all locked by default, only admin can edit
            default_permissions = {
                "vouchers": "admin",
                "journal_entries": "admin",
                "invoices": "admin",
                "orders": "admin",
                "quotations": "admin",
                "purchase_orders": "admin",
                "purchase_bills": "admin",
                "credit_debit_notes": "admin",
                "expenses": "admin"
            }
            return {"status": "success", "permissions": default_permissions}
        
        return {"status": "success", "permissions": settings.get("permissions", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/can-edit/{document_type}")
async def check_can_edit(
    document_type: str,
    db=Depends(get_db),
    user=Depends(verify_admin)
):
    """Check if current user can edit a specific document type"""
    try:
        user_role = user.get("role", "")
        
        # Get permissions settings
        settings = await db.system_settings.find_one({"type": "edit_permissions"}, {"_id": 0})
        
        if not settings:
            # Default: only admin can edit
            required_role = "admin"
        else:
            permissions = settings.get("permissions", {})
            required_role = permissions.get(document_type, "admin")
        
        # Role hierarchy: admin > accountant > store_manager
        role_hierarchy = {
            "admin": 4,
            "super_admin": 4,
            "accountant": 3,
            "store_manager": 2,
            "none": 0  # No one can edit
        }
        
        # If required_role is "none", no one can edit
        if required_role == "none":
            return {
                "can_edit": False,
                "reason": "This document type is locked and cannot be edited",
                "required_role": required_role,
                "user_role": user_role
            }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 4)
        
        can_edit = user_level >= required_level
        
        return {
            "can_edit": can_edit,
            "reason": "Access granted" if can_edit else f"Requires {required_role} or higher permission",
            "required_role": required_role,
            "user_role": user_role
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit-permissions")
async def save_edit_permissions(
    request: EditPermissionsRequest,
    db=Depends(get_db),
    admin=Depends(verify_admin)
):
    """Save edit permissions - Admin only"""
    try:
        # Only admin role can change permissions
        if admin.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Only Admin can modify edit permissions")
        
        await db.system_settings.update_one(
            {"type": "edit_permissions"},
            {
                "$set": {
                    "type": "edit_permissions",
                    "permissions": request.permissions,
                    "updated_by": admin.get("sub"),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return {"status": "success", "message": "Permissions saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backups")
async def get_backups(
    db=Depends(get_db),
    admin=Depends(verify_super_admin)
):
    """Get list of manual backups"""
    try:
        backups = await db.backups.find({}, {"_id": 0}).sort("created_at", -1).limit(20).to_list(20)
        
        formatted_backups = []
        for backup in backups:
            formatted_backups.append({
                "id": backup.get("id"),
                "name": backup.get("name", "Backup"),
                "date": backup.get("created_at", ""),
                "size": backup.get("size", "N/A"),
                "type": backup.get("type", "manual")
            })
        
        return {"status": "success", "backups": formatted_backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-backup")
async def create_backup(
    db=Depends(get_db),
    admin=Depends(verify_super_admin)
):
    """Create a manual backup - Super Admin only"""
    try:
        import uuid
        backup_id = str(uuid.uuid4())
        
        # Collections to backup
        collections_to_backup = [
            'orders', 'offline_invoices', 'quotations', 'customers',
            'purchase_orders', 'purchase_bills', 'vendors',
            'vouchers', 'journal_entries', 'credit_debit_notes', 'expenses',
            'products', 'categories', 'stores', 'store_users',
            'stock_transfers', 'delivery_challans', 'ledger_entries'
        ]
        
        backup_data = {}
        total_records = 0
        
        for coll in collections_to_backup:
            try:
                records = await db[coll].find({}, {"_id": 0}).to_list(None)
                backup_data[coll] = records
                total_records += len(records)
            except Exception:
                backup_data[coll] = []
        
        # Estimate size
        size_bytes = len(json.dumps(backup_data, default=str))
        size_str = f"{size_bytes / 1024 / 1024:.2f} MB" if size_bytes > 1024*1024 else f"{size_bytes / 1024:.2f} KB"
        
        # Store backup metadata
        backup_record = {
            "id": backup_id,
            "name": f"Manual Backup - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": admin.get("sub"),
            "size": size_str,
            "total_records": total_records,
            "type": "manual",
            "collections": list(backup_data.keys())
        }
        
        await db.backups.insert_one(backup_record)
        
        # Store backup data separately
        await db.backup_data.insert_one({
            "backup_id": backup_id,
            "data": backup_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup_id": backup_id,
            "size": size_str,
            "total_records": total_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-backup/{backup_id}")
async def download_backup(
    backup_id: str,
    format: str = "json",
    db=Depends(get_db),
    admin=Depends(verify_super_admin)
):
    """Download a backup in JSON or Tally XML format"""
    from fastapi.responses import StreamingResponse
    import io
    
    try:
        backup_data = await db.backup_data.find_one({"backup_id": backup_id}, {"_id": 0})
        
        if not backup_data:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        data = backup_data.get("data", {})
        
        if format == "json":
            # JSON format
            content = json.dumps(data, indent=2, default=str)
            media_type = "application/json"
            filename = f"backup_{backup_id}.json"
        
        elif format == "tally":
            # Tally XML format
            content = generate_tally_xml(data)
            media_type = "application/xml"
            filename = f"backup_{backup_id}_tally.xml"
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'tally'")
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_tally_xml(data: dict) -> str:
    """Generate Tally-compatible XML from backup data"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<ENVELOPE>')
    xml_parts.append('<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>')
    xml_parts.append('<BODY>')
    xml_parts.append('<IMPORTDATA>')
    xml_parts.append('<REQUESTDESC><REPORTNAME>All Masters</REPORTNAME></REQUESTDESC>')
    xml_parts.append('<REQUESTDATA>')
    
    # Export Customers as Ledgers (Sundry Debtors)
    if 'customers' in data:
        for customer in data['customers']:
            xml_parts.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml_parts.append('<LEDGER NAME="{}" ACTION="Create">'.format(escape_xml(customer.get('name', ''))))
            xml_parts.append('<PARENT>Sundry Debtors</PARENT>')
            xml_parts.append('<ADDRESS.LIST><ADDRESS>{}</ADDRESS></ADDRESS.LIST>'.format(
                escape_xml(customer.get('address', ''))
            ))
            xml_parts.append('<LEDSTATENAME>{}</LEDSTATENAME>'.format(escape_xml(customer.get('state', ''))))
            xml_parts.append('<PINCODE>{}</PINCODE>'.format(customer.get('pincode', '')))
            xml_parts.append('<LEDGERPHONE>{}</LEDGERPHONE>'.format(customer.get('phone', '')))
            xml_parts.append('<EMAIL>{}</EMAIL>'.format(customer.get('email', '')))
            if customer.get('gstin'):
                xml_parts.append('<PARTYGSTIN>{}</PARTYGSTIN>'.format(customer.get('gstin', '')))
            xml_parts.append('<OPENINGBALANCE>0</OPENINGBALANCE>')
            xml_parts.append('</LEDGER>')
            xml_parts.append('</TALLYMESSAGE>')
    
    # Export Vendors as Ledgers (Sundry Creditors)
    if 'vendors' in data:
        for vendor in data['vendors']:
            xml_parts.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml_parts.append('<LEDGER NAME="{}" ACTION="Create">'.format(escape_xml(vendor.get('name', ''))))
            xml_parts.append('<PARENT>Sundry Creditors</PARENT>')
            xml_parts.append('<ADDRESS.LIST><ADDRESS>{}</ADDRESS></ADDRESS.LIST>'.format(
                escape_xml(vendor.get('address', ''))
            ))
            if vendor.get('gstin'):
                xml_parts.append('<PARTYGSTIN>{}</PARTYGSTIN>'.format(vendor.get('gstin', '')))
            xml_parts.append('<OPENINGBALANCE>0</OPENINGBALANCE>')
            xml_parts.append('</LEDGER>')
            xml_parts.append('</TALLYMESSAGE>')
    
    # Export Products as Stock Items
    if 'products' in data:
        for product in data['products']:
            xml_parts.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml_parts.append('<STOCKITEM NAME="{}" ACTION="Create">'.format(escape_xml(product.get('name', ''))))
            xml_parts.append('<PARENT>{}</PARENT>'.format(escape_xml(product.get('category', 'Primary'))))
            xml_parts.append('<BASEUNITS>Nos</BASEUNITS>')
            if product.get('hsn_code'):
                xml_parts.append('<GSTDETAILS.LIST><HSNCODE>{}</HSNCODE></GSTDETAILS.LIST>'.format(product.get('hsn_code')))
            xml_parts.append('<OPENINGBALANCE>{} Nos</OPENINGBALANCE>'.format(product.get('stock', 0)))
            xml_parts.append('<OPENINGRATE>{}</OPENINGRATE>'.format(product.get('price', 0)))
            xml_parts.append('</STOCKITEM>')
            xml_parts.append('</TALLYMESSAGE>')
    
    # Export Sales Vouchers
    if 'offline_invoices' in data or 'orders' in data:
        invoices = data.get('offline_invoices', []) + data.get('orders', [])
        for invoice in invoices:
            if not invoice.get('total_amount'):
                continue
            xml_parts.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml_parts.append('<VOUCHER VCHTYPE="Sales" ACTION="Create">')
            xml_parts.append('<DATE>{}</DATE>'.format(format_tally_date(invoice.get('created_at', ''))))
            xml_parts.append('<VOUCHERNUMBER>{}</VOUCHERNUMBER>'.format(
                invoice.get('invoice_number') or invoice.get('order_number', '')
            ))
            xml_parts.append('<PARTYLEDGERNAME>{}</PARTYLEDGERNAME>'.format(
                escape_xml(invoice.get('customer_name', 'Cash'))
            ))
            
            # Ledger entries
            xml_parts.append('<ALLLEDGERENTRIES.LIST>')
            xml_parts.append('<LEDGERNAME>{}</LEDGERNAME>'.format(escape_xml(invoice.get('customer_name', 'Cash'))))
            xml_parts.append('<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>')
            xml_parts.append('<AMOUNT>-{}</AMOUNT>'.format(invoice.get('total_amount', 0)))
            xml_parts.append('</ALLLEDGERENTRIES.LIST>')
            
            xml_parts.append('<ALLLEDGERENTRIES.LIST>')
            xml_parts.append('<LEDGERNAME>Sales Account</LEDGERNAME>')
            xml_parts.append('<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>')
            xml_parts.append('<AMOUNT>{}</AMOUNT>'.format(invoice.get('subtotal', invoice.get('total_amount', 0))))
            xml_parts.append('</ALLLEDGERENTRIES.LIST>')
            
            if invoice.get('tax_amount'):
                xml_parts.append('<ALLLEDGERENTRIES.LIST>')
                xml_parts.append('<LEDGERNAME>Output GST</LEDGERNAME>')
                xml_parts.append('<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>')
                xml_parts.append('<AMOUNT>{}</AMOUNT>'.format(invoice.get('tax_amount', 0)))
                xml_parts.append('</ALLLEDGERENTRIES.LIST>')
            
            xml_parts.append('</VOUCHER>')
            xml_parts.append('</TALLYMESSAGE>')
    
    # Export Purchase Vouchers
    if 'purchase_bills' in data:
        for bill in data['purchase_bills']:
            if not bill.get('total_amount'):
                continue
            xml_parts.append('<TALLYMESSAGE xmlns:UDF="TallyUDF">')
            xml_parts.append('<VOUCHER VCHTYPE="Purchase" ACTION="Create">')
            xml_parts.append('<DATE>{}</DATE>'.format(format_tally_date(bill.get('created_at', ''))))
            xml_parts.append('<VOUCHERNUMBER>{}</VOUCHERNUMBER>'.format(bill.get('bill_number', '')))
            xml_parts.append('<PARTYLEDGERNAME>{}</PARTYLEDGERNAME>'.format(
                escape_xml(bill.get('vendor_name', 'Cash'))
            ))
            
            xml_parts.append('<ALLLEDGERENTRIES.LIST>')
            xml_parts.append('<LEDGERNAME>{}</LEDGERNAME>'.format(escape_xml(bill.get('vendor_name', 'Cash'))))
            xml_parts.append('<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>')
            xml_parts.append('<AMOUNT>{}</AMOUNT>'.format(bill.get('total_amount', 0)))
            xml_parts.append('</ALLLEDGERENTRIES.LIST>')
            
            xml_parts.append('<ALLLEDGERENTRIES.LIST>')
            xml_parts.append('<LEDGERNAME>Purchase Account</LEDGERNAME>')
            xml_parts.append('<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>')
            xml_parts.append('<AMOUNT>-{}</AMOUNT>'.format(bill.get('subtotal', bill.get('total_amount', 0))))
            xml_parts.append('</ALLLEDGERENTRIES.LIST>')
            
            xml_parts.append('</VOUCHER>')
            xml_parts.append('</TALLYMESSAGE>')
    
    xml_parts.append('</REQUESTDATA>')
    xml_parts.append('</IMPORTDATA>')
    xml_parts.append('</BODY>')
    xml_parts.append('</ENVELOPE>')
    
    return '\n'.join(xml_parts)


def escape_xml(text: str) -> str:
    """Escape special XML characters"""
    if not text:
        return ''
    text = str(text)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def format_tally_date(date_str: str) -> str:
    """Format date for Tally (YYYYMMDD)"""
    try:
        if not date_str:
            return datetime.now().strftime('%Y%m%d')
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y%m%d')
    except Exception:
        return datetime.now().strftime('%Y%m%d')
