"""
Data Export Routes
Comprehensive export functionality for Tally, GSTR-1, Excel with date range support
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from database import get_db
import json
import io
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as escape_xml

router = APIRouter(prefix="/export", tags=["Data Export"])


# ============ HELPER FUNCTIONS ============

def format_tally_date(date_str: str) -> str:
    """Convert ISO date to Tally date format (YYYYMMDD)"""
    if not date_str:
        return datetime.now().strftime("%Y%m%d")
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%Y%m%d")
    except Exception:
        return datetime.now().strftime("%Y%m%d")


def format_date_display(date_str: str) -> str:
    """Format date for display"""
    if not date_str:
        return ""
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%d-%b-%Y")
    except Exception:
        return date_str[:10] if date_str else ""


def safe_xml(value) -> str:
    """Safely escape XML content"""
    if value is None:
        return ""
    return escape_xml(str(value))


def get_financial_year(date: datetime) -> str:
    """Get financial year string (e.g., 2025-26)"""
    if date.month >= 4:
        return f"{date.year}-{str(date.year + 1)[2:]}"
    else:
        return f"{date.year - 1}-{str(date.year)[2:]}"


def get_gst_month(date: datetime) -> str:
    """Get GST return period (MMYYYY format)"""
    return date.strftime("%m%Y")


# ============ DATE RANGE EXPORT ============

@router.get("/date-range")
async def export_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    data_type: str = Query("all", description="Data type: sales, purchases, all"),
    format: str = Query("excel", description="Format: excel, tally, json"),
    store_code: Optional[str] = None,
    db = Depends(get_db)
):
    """Export data for a specific date range"""
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        data = {"period": {"start": start_date, "end": end_date}}
        
        # Build date query
        date_query = {
            "$or": [
                {"created_at": {"$gte": start_dt.isoformat(), "$lte": end_dt.isoformat()}},
                {"invoice_date": {"$gte": start_date, "$lte": end_date}},
                {"bill_date": {"$gte": start_date, "$lte": end_date}}
            ]
        }
        
        if store_code:
            date_query["store_code"] = store_code
        
        # Fetch sales data
        if data_type in ["sales", "all"]:
            invoices = await db.offline_invoices.find(
                {**date_query, "document_type": {"$in": ["invoice", "sales_order"]}},
                {"_id": 0}
            ).sort("created_at", 1).to_list(None)
            data["sales_invoices"] = invoices
            data["sales_summary"] = {
                "total_invoices": len([i for i in invoices if i.get("document_type") == "invoice"]),
                "total_sales_orders": len([i for i in invoices if i.get("document_type") == "sales_order"]),
                "total_amount": sum(i.get("grand_total", 0) or i.get("total_amount", 0) for i in invoices),
                "total_tax": sum(i.get("total_gst", 0) or i.get("tax_amount", 0) for i in invoices)
            }
        
        # Fetch purchase data
        if data_type in ["purchases", "all"]:
            purchase_bills = await db.purchase_bills.find(
                date_query,
                {"_id": 0}
            ).sort("created_at", 1).to_list(None)
            data["purchase_bills"] = purchase_bills
            
            purchase_orders = await db.purchase_orders.find(
                date_query,
                {"_id": 0}
            ).sort("created_at", 1).to_list(None)
            data["purchase_orders"] = purchase_orders
            
            data["purchase_summary"] = {
                "total_bills": len(purchase_bills),
                "total_pos": len(purchase_orders),
                "total_amount": sum(b.get("grand_total", 0) or b.get("total_amount", 0) for b in purchase_bills),
                "total_tax": sum(b.get("tax_amount", 0) for b in purchase_bills)
            }
        
        # Generate output based on format
        if format == "json":
            content = json.dumps(data, indent=2, default=str)
            media_type = "application/json"
            filename = f"export_{start_date}_to_{end_date}.json"
        
        elif format == "tally":
            content = generate_tally_xml_from_data(data)
            media_type = "application/xml"
            filename = f"tally_export_{start_date}_to_{end_date}.xml"
        
        elif format == "excel":
            content = generate_excel_from_data(data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"export_{start_date}_to_{end_date}.xlsx"
            
            return StreamingResponse(
                io.BytesIO(content),
                media_type=media_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ============ DIRECT TALLY EXPORT ============

@router.get("/tally/sales")
async def export_sales_to_tally(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    store_code: Optional[str] = None,
    db = Depends(get_db)
):
    """Direct Tally XML export for Sales Vouchers"""
    try:
        query = {"document_type": "invoice"}
        
        if start_date and end_date:
            query["$or"] = [
                {"created_at": {"$gte": start_date, "$lte": end_date + "T23:59:59"}},
                {"invoice_date": {"$gte": start_date, "$lte": end_date}}
            ]
        
        if store_code:
            query["store_code"] = store_code
        
        invoices = await db.offline_invoices.find(query, {"_id": 0}).sort("created_at", 1).to_list(None)
        
        xml_content = generate_sales_vouchers_xml(invoices)
        
        filename = f"tally_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        return StreamingResponse(
            io.BytesIO(xml_content.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tally export failed: {str(e)}")


@router.get("/tally/purchases")
async def export_purchases_to_tally(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Direct Tally XML export for Purchase Vouchers"""
    try:
        query = {}
        
        if start_date and end_date:
            query["$or"] = [
                {"created_at": {"$gte": start_date, "$lte": end_date + "T23:59:59"}},
                {"bill_date": {"$gte": start_date, "$lte": end_date}}
            ]
        
        bills = await db.purchase_bills.find(query, {"_id": 0}).sort("created_at", 1).to_list(None)
        
        xml_content = generate_purchase_vouchers_xml(bills)
        
        filename = f"tally_purchases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        return StreamingResponse(
            io.BytesIO(xml_content.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tally export failed: {str(e)}")


@router.get("/tally/masters")
async def export_masters_to_tally(db = Depends(get_db)):
    """Export Customers, Vendors, Products as Tally Masters"""
    try:
        customers = await db.customers.find({}, {"_id": 0}).to_list(None)
        vendors = await db.vendors.find({}, {"_id": 0}).to_list(None)
        products = await db.products.find({}, {"_id": 0}).to_list(None)
        
        xml_content = generate_masters_xml(customers, vendors, products)
        
        filename = f"tally_masters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        return StreamingResponse(
            io.BytesIO(xml_content.encode('utf-8')),
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tally export failed: {str(e)}")


# ============ GSTR-1 EXPORT ============

@router.get("/gstr1")
async def export_gstr1(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, description="Year"),
    store_code: Optional[str] = None,
    format: str = Query("json", description="Format: json, excel"),
    db = Depends(get_db)
):
    """Export GSTR-1 format data for GST filing"""
    try:
        # Calculate date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        query = {
            "document_type": "invoice",
            "$or": [
                {"created_at": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}},
                {"invoice_date": {"$gte": start_date.strftime("%Y-%m-%d"), "$lte": end_date.strftime("%Y-%m-%d")}}
            ]
        }
        
        if store_code:
            query["store_code"] = store_code
        
        invoices = await db.offline_invoices.find(query, {"_id": 0}).sort("created_at", 1).to_list(None)
        
        # Categorize invoices for GSTR-1
        gstr1_data = {
            "gstin": "",  # Will be filled from store config
            "fp": f"{month:02d}{year}",  # Filing period
            "version": "GST3.0.4",
            "hash": "hash",
            "b2b": [],     # B2B Invoices (with GSTIN)
            "b2cl": [],    # B2C Large (> 2.5L, without GSTIN)
            "b2cs": [],    # B2C Small (consolidated)
            "cdnr": [],    # Credit/Debit Notes (registered)
            "cdnur": [],   # Credit/Debit Notes (unregistered)
            "exp": [],     # Exports
            "at": [],      # Advances Received
            "nil": [],     # Nil Rated
            "hsn": [],     # HSN Summary
            "doc_issue": []  # Document Summary
        }
        
        # Process each invoice
        b2cs_summary = {}  # For consolidating B2C small
        hsn_summary = {}   # For HSN-wise summary
        
        for inv in invoices:
            customer = inv.get("customer", {})
            customer_gstin = customer.get("gst_number") or customer.get("gstin") or ""
            grand_total = inv.get("grand_total", 0) or inv.get("total_amount", 0)
            taxable_value = inv.get("subtotal", 0) or inv.get("taxable_amount", 0)
            
            # Get tax amounts
            igst = inv.get("igst", 0)
            
            invoice_date = inv.get("invoice_date") or inv.get("created_at", "")[:10]
            
            if customer_gstin and len(customer_gstin) == 15:
                # B2B Invoice
                b2b_inv = {
                    "ctin": customer_gstin,
                    "inv": [{
                        "inum": inv.get("invoice_number", ""),
                        "idt": format_date_display(invoice_date),
                        "val": round(grand_total, 2),
                        "pos": customer_gstin[:2],  # Place of supply from GSTIN
                        "rchrg": "N",
                        "inv_typ": "R",
                        "itms": []
                    }]
                }
                
                # Add items with tax rates
                for item in inv.get("items", []):
                    gst_rate = item.get("gst_rate", 18)
                    item_taxable = item.get("taxable_amount", 0) or item.get("total", 0) / (1 + gst_rate/100)
                    b2b_inv["inv"][0]["itms"].append({
                        "num": 1,
                        "itm_det": {
                            "rt": gst_rate,
                            "txval": round(item_taxable, 2),
                            "camt": round(item_taxable * gst_rate / 200, 2),
                            "samt": round(item_taxable * gst_rate / 200, 2),
                            "iamt": 0,
                            "csamt": 0
                        }
                    })
                
                gstr1_data["b2b"].append(b2b_inv)
            
            elif grand_total > 250000:
                # B2C Large (> 2.5 Lakhs)
                state_code = customer.get("state_code", "29")  # Default Karnataka
                gstr1_data["b2cl"].append({
                    "pos": state_code,
                    "inv": [{
                        "inum": inv.get("invoice_number", ""),
                        "idt": format_date_display(invoice_date),
                        "val": round(grand_total, 2),
                        "itms": [{
                            "num": 1,
                            "itm_det": {
                                "rt": 18,
                                "txval": round(taxable_value, 2),
                                "iamt": round(igst, 2) if igst else 0,
                                "csamt": 0
                            }
                        }]
                    }]
                })
            
            else:
                # B2C Small - Consolidate by rate and state
                state_code = customer.get("state_code", "29")
                for item in inv.get("items", []):
                    gst_rate = item.get("gst_rate", 18)
                    item_taxable = item.get("taxable_amount", 0) or item.get("total", 0) / (1 + gst_rate/100)
                    
                    key = f"{state_code}_{gst_rate}"
                    if key not in b2cs_summary:
                        b2cs_summary[key] = {
                            "sply_ty": "INTRA",
                            "pos": state_code,
                            "rt": gst_rate,
                            "txval": 0,
                            "camt": 0,
                            "samt": 0,
                            "csamt": 0
                        }
                    
                    b2cs_summary[key]["txval"] += item_taxable
                    b2cs_summary[key]["camt"] += item_taxable * gst_rate / 200
                    b2cs_summary[key]["samt"] += item_taxable * gst_rate / 200
            
            # HSN Summary
            for item in inv.get("items", []):
                hsn_code = item.get("hsn_code", "")
                if hsn_code:
                    gst_rate = item.get("gst_rate", 18)
                    qty = item.get("quantity", 1)
                    item_taxable = item.get("taxable_amount", 0) or item.get("total", 0) / (1 + gst_rate/100)
                    
                    if hsn_code not in hsn_summary:
                        hsn_summary[hsn_code] = {
                            "num": 1,
                            "hsn_sc": hsn_code,
                            "desc": item.get("product_name", ""),
                            "uqc": "NOS",
                            "qty": 0,
                            "val": 0,
                            "txval": 0,
                            "iamt": 0,
                            "camt": 0,
                            "samt": 0,
                            "csamt": 0
                        }
                    
                    hsn_summary[hsn_code]["qty"] += qty
                    hsn_summary[hsn_code]["val"] += item.get("total", 0)
                    hsn_summary[hsn_code]["txval"] += item_taxable
                    hsn_summary[hsn_code]["camt"] += item_taxable * gst_rate / 200
                    hsn_summary[hsn_code]["samt"] += item_taxable * gst_rate / 200
        
        # Add consolidated B2CS
        for key, data in b2cs_summary.items():
            data["txval"] = round(data["txval"], 2)
            data["camt"] = round(data["camt"], 2)
            data["samt"] = round(data["samt"], 2)
            gstr1_data["b2cs"].append(data)
        
        # Add HSN summary
        for hsn_code, data in hsn_summary.items():
            data["qty"] = round(data["qty"], 2)
            data["val"] = round(data["val"], 2)
            data["txval"] = round(data["txval"], 2)
            data["camt"] = round(data["camt"], 2)
            data["samt"] = round(data["samt"], 2)
            gstr1_data["hsn"].append(data)
        
        # Add summary stats
        gstr1_data["summary"] = {
            "total_invoices": len(invoices),
            "b2b_count": len(gstr1_data["b2b"]),
            "b2cl_count": len(gstr1_data["b2cl"]),
            "b2cs_count": len(gstr1_data["b2cs"]),
            "total_taxable_value": round(sum(inv.get("subtotal", 0) for inv in invoices), 2),
            "total_tax": round(sum(inv.get("total_gst", 0) for inv in invoices), 2),
            "period": f"{month:02d}/{year}"
        }
        
        if format == "json":
            content = json.dumps(gstr1_data, indent=2, default=str)
            media_type = "application/json"
            filename = f"GSTR1_{month:02d}{year}.json"
        
        elif format == "excel":
            content = generate_gstr1_excel(gstr1_data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"GSTR1_{month:02d}{year}.xlsx"
            
            return StreamingResponse(
                io.BytesIO(content),
                media_type=media_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GSTR-1 export failed: {str(e)}")


# ============ EXPORT SUMMARY ============

@router.get("/summary")
async def get_export_summary(
    start_date: str = Query(...),
    end_date: str = Query(...),
    store_code: Optional[str] = None,
    db = Depends(get_db)
):
    """Get summary of data available for export"""
    try:
        query = {
            "$or": [
                {"created_at": {"$gte": start_date, "$lte": end_date + "T23:59:59"}},
                {"invoice_date": {"$gte": start_date, "$lte": end_date}},
                {"bill_date": {"$gte": start_date, "$lte": end_date}}
            ]
        }
        
        if store_code:
            query["store_code"] = store_code
        
        # Count documents
        invoice_count = await db.offline_invoices.count_documents({
            **query, "document_type": "invoice"
        })
        so_count = await db.offline_invoices.count_documents({
            **query, "document_type": "sales_order"
        })
        purchase_bill_count = await db.purchase_bills.count_documents(query)
        purchase_order_count = await db.purchase_orders.count_documents(query)
        
        # Get totals
        invoices = await db.offline_invoices.find(
            {**query, "document_type": "invoice"},
            {"grand_total": 1, "total_gst": 1}
        ).to_list(None)
        
        total_sales = sum(i.get("grand_total", 0) for i in invoices)
        total_tax = sum(i.get("total_gst", 0) for i in invoices)
        
        return {
            "status": "success",
            "period": {"start": start_date, "end": end_date},
            "counts": {
                "invoices": invoice_count,
                "sales_orders": so_count,
                "purchase_bills": purchase_bill_count,
                "purchase_orders": purchase_order_count
            },
            "totals": {
                "sales_amount": round(total_sales, 2),
                "tax_collected": round(total_tax, 2)
            },
            "available_exports": [
                {"type": "excel", "description": "Excel spreadsheet with all data"},
                {"type": "tally", "description": "Tally-compatible XML for import"},
                {"type": "json", "description": "Raw JSON data"},
                {"type": "gstr1", "description": "GSTR-1 format for GST filing"}
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ XML GENERATORS ============

def generate_tally_xml_from_data(data: dict) -> str:
    """Generate Tally XML from export data"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<ENVELOPE>')
    xml_parts.append('<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>')
    xml_parts.append('<BODY>')
    xml_parts.append('<IMPORTDATA>')
    xml_parts.append('<REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>')
    xml_parts.append('<REQUESTDATA>')
    
    # Sales vouchers
    for inv in data.get("sales_invoices", []):
        xml_parts.append(generate_sales_voucher_xml(inv))
    
    # Purchase vouchers
    for bill in data.get("purchase_bills", []):
        xml_parts.append(generate_purchase_voucher_xml(bill))
    
    xml_parts.append('</REQUESTDATA>')
    xml_parts.append('</IMPORTDATA>')
    xml_parts.append('</BODY>')
    xml_parts.append('</ENVELOPE>')
    
    return '\n'.join(xml_parts)


def generate_sales_voucher_xml(invoice: dict) -> str:
    """Generate single sales voucher XML"""
    customer_name = invoice.get("customer", {}).get("name", "Cash")
    invoice_num = invoice.get("invoice_number", "")
    invoice_date = format_tally_date(invoice.get("created_at", ""))
    grand_total = invoice.get("grand_total", 0) or invoice.get("total_amount", 0)
    subtotal = invoice.get("subtotal", 0) or grand_total * 0.85
    tax_amount = invoice.get("total_gst", 0) or grand_total - subtotal
    
    xml = f'''<TALLYMESSAGE xmlns:UDF="TallyUDF">
<VOUCHER VCHTYPE="Sales" ACTION="Create">
<DATE>{invoice_date}</DATE>
<VOUCHERNUMBER>{safe_xml(invoice_num)}</VOUCHERNUMBER>
<PARTYLEDGERNAME>{safe_xml(customer_name)}</PARTYLEDGERNAME>
<VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
<NARRATION>Invoice {safe_xml(invoice_num)}</NARRATION>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{safe_xml(customer_name)}</LEDGERNAME>
<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
<AMOUNT>-{grand_total}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Sales Account</LEDGERNAME>
<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
<AMOUNT>{subtotal}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Output CGST</LEDGERNAME>
<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
<AMOUNT>{round(tax_amount/2, 2)}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Output SGST</LEDGERNAME>
<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
<AMOUNT>{round(tax_amount/2, 2)}</AMOUNT>
</ALLLEDGERENTRIES.LIST>'''
    
    # Add inventory entries for each item
    for item in invoice.get("items", []):
        item_name = item.get("product_name", "") or item.get("model_number", "")
        quantity = item.get("quantity", 1)
        rate = item.get("unit_price", 0) or item.get("rate", 0)
        xml += f'''
<ALLINVENTORYENTRIES.LIST>
<STOCKITEMNAME>{safe_xml(item_name)}</STOCKITEMNAME>
<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
<RATE>{rate}/Nos</RATE>
<AMOUNT>{round(rate * quantity, 2)}</AMOUNT>
<ACTUALQTY>{quantity} Nos</ACTUALQTY>
<BILLEDQTY>{quantity} Nos</BILLEDQTY>
</ALLINVENTORYENTRIES.LIST>'''
    
    xml += '\n</VOUCHER>\n</TALLYMESSAGE>'
    return xml


def generate_purchase_voucher_xml(bill: dict) -> str:
    """Generate single purchase voucher XML"""
    vendor_name = bill.get("vendor", {}).get("name", "") or bill.get("vendor_name", "Cash")
    bill_num = bill.get("bill_number", "")
    bill_date = format_tally_date(bill.get("created_at", ""))
    grand_total = bill.get("grand_total", 0) or bill.get("total_amount", 0)
    subtotal = bill.get("subtotal", 0) or grand_total * 0.85
    tax_amount = bill.get("tax_amount", 0) or grand_total - subtotal
    
    xml = f'''<TALLYMESSAGE xmlns:UDF="TallyUDF">
<VOUCHER VCHTYPE="Purchase" ACTION="Create">
<DATE>{bill_date}</DATE>
<VOUCHERNUMBER>{safe_xml(bill_num)}</VOUCHERNUMBER>
<PARTYLEDGERNAME>{safe_xml(vendor_name)}</PARTYLEDGERNAME>
<VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>
<NARRATION>Bill {safe_xml(bill_num)}</NARRATION>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>{safe_xml(vendor_name)}</LEDGERNAME>
<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
<AMOUNT>{grand_total}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Purchase Account</LEDGERNAME>
<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
<AMOUNT>-{subtotal}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Input CGST</LEDGERNAME>
<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
<AMOUNT>-{round(tax_amount/2, 2)}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
<ALLLEDGERENTRIES.LIST>
<LEDGERNAME>Input SGST</LEDGERNAME>
<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
<AMOUNT>-{round(tax_amount/2, 2)}</AMOUNT>
</ALLLEDGERENTRIES.LIST>
</VOUCHER>
</TALLYMESSAGE>'''
    return xml


def generate_sales_vouchers_xml(invoices: list) -> str:
    """Generate Tally XML for multiple sales vouchers"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<ENVELOPE>')
    xml_parts.append('<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>')
    xml_parts.append('<BODY>')
    xml_parts.append('<IMPORTDATA>')
    xml_parts.append('<REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>')
    xml_parts.append('<REQUESTDATA>')
    
    for inv in invoices:
        xml_parts.append(generate_sales_voucher_xml(inv))
    
    xml_parts.append('</REQUESTDATA>')
    xml_parts.append('</IMPORTDATA>')
    xml_parts.append('</BODY>')
    xml_parts.append('</ENVELOPE>')
    
    return '\n'.join(xml_parts)


def generate_purchase_vouchers_xml(bills: list) -> str:
    """Generate Tally XML for multiple purchase vouchers"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<ENVELOPE>')
    xml_parts.append('<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>')
    xml_parts.append('<BODY>')
    xml_parts.append('<IMPORTDATA>')
    xml_parts.append('<REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>')
    xml_parts.append('<REQUESTDATA>')
    
    for bill in bills:
        xml_parts.append(generate_purchase_voucher_xml(bill))
    
    xml_parts.append('</REQUESTDATA>')
    xml_parts.append('</IMPORTDATA>')
    xml_parts.append('</BODY>')
    xml_parts.append('</ENVELOPE>')
    
    return '\n'.join(xml_parts)


def generate_masters_xml(customers: list, vendors: list, products: list) -> str:
    """Generate Tally XML for master data"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<ENVELOPE>')
    xml_parts.append('<HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>')
    xml_parts.append('<BODY>')
    xml_parts.append('<IMPORTDATA>')
    xml_parts.append('<REQUESTDESC><REPORTNAME>All Masters</REPORTNAME></REQUESTDESC>')
    xml_parts.append('<REQUESTDATA>')
    
    # Customers as Sundry Debtors
    for cust in customers:
        name = cust.get("name", "")
        if not name:
            continue
        xml_parts.append(f'''<TALLYMESSAGE xmlns:UDF="TallyUDF">
<LEDGER NAME="{safe_xml(name)}" ACTION="Create">
<PARENT>Sundry Debtors</PARENT>
<ADDRESS.LIST><ADDRESS>{safe_xml(cust.get("address", ""))}</ADDRESS></ADDRESS.LIST>
<LEDSTATENAME>{safe_xml(cust.get("state", ""))}</LEDSTATENAME>
<PINCODE>{cust.get("pincode", "")}</PINCODE>
<LEDGERPHONE>{cust.get("phone", "")}</LEDGERPHONE>
<EMAIL>{cust.get("email", "")}</EMAIL>
<PARTYGSTIN>{cust.get("gst_number", "")}</PARTYGSTIN>
<OPENINGBALANCE>0</OPENINGBALANCE>
</LEDGER>
</TALLYMESSAGE>''')
    
    # Vendors as Sundry Creditors
    for vendor in vendors:
        name = vendor.get("name", "")
        if not name:
            continue
        xml_parts.append(f'''<TALLYMESSAGE xmlns:UDF="TallyUDF">
<LEDGER NAME="{safe_xml(name)}" ACTION="Create">
<PARENT>Sundry Creditors</PARENT>
<ADDRESS.LIST><ADDRESS>{safe_xml(vendor.get("address", ""))}</ADDRESS></ADDRESS.LIST>
<PARTYGSTIN>{vendor.get("gst_number", "")}</PARTYGSTIN>
<OPENINGBALANCE>0</OPENINGBALANCE>
</LEDGER>
</TALLYMESSAGE>''')
    
    # Products as Stock Items
    for prod in products:
        name = prod.get("name", "") or prod.get("model_number", "")
        if not name:
            continue
        xml_parts.append(f'''<TALLYMESSAGE xmlns:UDF="TallyUDF">
<STOCKITEM NAME="{safe_xml(name)}" ACTION="Create">
<PARENT>{safe_xml(prod.get("category", "Primary"))}</PARENT>
<BASEUNITS>Nos</BASEUNITS>
<GSTDETAILS.LIST><HSNCODE>{prod.get("hsn_code", "")}</HSNCODE></GSTDETAILS.LIST>
<OPENINGBALANCE>{prod.get("stock", 0)} Nos</OPENINGBALANCE>
<OPENINGRATE>{prod.get("price", 0)}</OPENINGRATE>
</STOCKITEM>
</TALLYMESSAGE>''')
    
    xml_parts.append('</REQUESTDATA>')
    xml_parts.append('</IMPORTDATA>')
    xml_parts.append('</BODY>')
    xml_parts.append('</ENVELOPE>')
    
    return '\n'.join(xml_parts)


# ============ EXCEL GENERATORS ============

def generate_excel_from_data(data: dict) -> bytes:
    """Generate Excel file from export data"""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    
    wb = openpyxl.Workbook()
    
    # Header style
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    
    # Sales Invoices Sheet
    if "sales_invoices" in data:
        ws = wb.active
        ws.title = "Sales Invoices"
        
        headers = ["Invoice #", "Date", "Customer", "GSTIN", "Taxable Value", "CGST", "SGST", "Total", "Status"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        for row, inv in enumerate(data["sales_invoices"], 2):
            customer = inv.get("customer", {})
            ws.cell(row=row, column=1, value=inv.get("invoice_number", ""))
            ws.cell(row=row, column=2, value=format_date_display(inv.get("created_at", "")))
            ws.cell(row=row, column=3, value=customer.get("name", ""))
            ws.cell(row=row, column=4, value=customer.get("gst_number", ""))
            ws.cell(row=row, column=5, value=inv.get("subtotal", 0))
            ws.cell(row=row, column=6, value=inv.get("cgst", 0))
            ws.cell(row=row, column=7, value=inv.get("sgst", 0))
            ws.cell(row=row, column=8, value=inv.get("grand_total", 0))
            ws.cell(row=row, column=9, value=inv.get("status", ""))
        
        # Auto-fit columns
        for col in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 30)
    
    # Purchase Bills Sheet
    if "purchase_bills" in data and data["purchase_bills"]:
        ws = wb.create_sheet("Purchase Bills")
        
        headers = ["Bill #", "Date", "Vendor", "GSTIN", "Taxable Value", "Tax", "Total", "Status"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
        
        for row, bill in enumerate(data["purchase_bills"], 2):
            vendor = bill.get("vendor", {})
            ws.cell(row=row, column=1, value=bill.get("bill_number", ""))
            ws.cell(row=row, column=2, value=format_date_display(bill.get("created_at", "")))
            ws.cell(row=row, column=3, value=vendor.get("name", "") or bill.get("vendor_name", ""))
            ws.cell(row=row, column=4, value=vendor.get("gst_number", ""))
            ws.cell(row=row, column=5, value=bill.get("subtotal", 0))
            ws.cell(row=row, column=6, value=bill.get("tax_amount", 0))
            ws.cell(row=row, column=7, value=bill.get("grand_total", 0))
            ws.cell(row=row, column=8, value=bill.get("status", ""))
    
    # Summary Sheet
    ws = wb.create_sheet("Summary")
    ws.cell(row=1, column=1, value="Export Summary").font = Font(bold=True, size=14)
    ws.cell(row=3, column=1, value="Period:")
    ws.cell(row=3, column=2, value=f"{data.get('period', {}).get('start', '')} to {data.get('period', {}).get('end', '')}")
    
    if "sales_summary" in data:
        ws.cell(row=5, column=1, value="SALES").font = Font(bold=True)
        ws.cell(row=6, column=1, value="Total Invoices:")
        ws.cell(row=6, column=2, value=data["sales_summary"].get("total_invoices", 0))
        ws.cell(row=7, column=1, value="Total Amount:")
        ws.cell(row=7, column=2, value=data["sales_summary"].get("total_amount", 0))
        ws.cell(row=8, column=1, value="Total Tax:")
        ws.cell(row=8, column=2, value=data["sales_summary"].get("total_tax", 0))
    
    if "purchase_summary" in data:
        ws.cell(row=10, column=1, value="PURCHASES").font = Font(bold=True)
        ws.cell(row=11, column=1, value="Total Bills:")
        ws.cell(row=11, column=2, value=data["purchase_summary"].get("total_bills", 0))
        ws.cell(row=12, column=1, value="Total Amount:")
        ws.cell(row=12, column=2, value=data["purchase_summary"].get("total_amount", 0))
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.read()


def generate_gstr1_excel(data: dict) -> bytes:
    """Generate GSTR-1 Excel file"""
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    
    wb = openpyxl.Workbook()
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # B2B Sheet
    ws = wb.active
    ws.title = "B2B"
    headers = ["GSTIN", "Invoice Number", "Invoice Date", "Invoice Value", "Place of Supply", "Reverse Charge", "Invoice Type", "Taxable Value", "Tax Rate", "CGST", "SGST"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    row = 2
    for b2b in data.get("b2b", []):
        for inv in b2b.get("inv", []):
            for itm in inv.get("itms", []):
                det = itm.get("itm_det", {})
                ws.cell(row=row, column=1, value=b2b.get("ctin", ""))
                ws.cell(row=row, column=2, value=inv.get("inum", ""))
                ws.cell(row=row, column=3, value=inv.get("idt", ""))
                ws.cell(row=row, column=4, value=inv.get("val", 0))
                ws.cell(row=row, column=5, value=inv.get("pos", ""))
                ws.cell(row=row, column=6, value=inv.get("rchrg", "N"))
                ws.cell(row=row, column=7, value=inv.get("inv_typ", "R"))
                ws.cell(row=row, column=8, value=det.get("txval", 0))
                ws.cell(row=row, column=9, value=det.get("rt", 0))
                ws.cell(row=row, column=10, value=det.get("camt", 0))
                ws.cell(row=row, column=11, value=det.get("samt", 0))
                row += 1
    
    # B2CS Sheet
    ws = wb.create_sheet("B2CS")
    headers = ["Type", "Place of Supply", "Tax Rate", "Taxable Value", "CGST", "SGST"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    for row, b2cs in enumerate(data.get("b2cs", []), 2):
        ws.cell(row=row, column=1, value=b2cs.get("sply_ty", ""))
        ws.cell(row=row, column=2, value=b2cs.get("pos", ""))
        ws.cell(row=row, column=3, value=b2cs.get("rt", 0))
        ws.cell(row=row, column=4, value=b2cs.get("txval", 0))
        ws.cell(row=row, column=5, value=b2cs.get("camt", 0))
        ws.cell(row=row, column=6, value=b2cs.get("samt", 0))
    
    # HSN Sheet
    ws = wb.create_sheet("HSN")
    headers = ["HSN Code", "Description", "UQC", "Quantity", "Total Value", "Taxable Value", "CGST", "SGST"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
    
    for row, hsn in enumerate(data.get("hsn", []), 2):
        ws.cell(row=row, column=1, value=hsn.get("hsn_sc", ""))
        ws.cell(row=row, column=2, value=hsn.get("desc", ""))
        ws.cell(row=row, column=3, value=hsn.get("uqc", "NOS"))
        ws.cell(row=row, column=4, value=hsn.get("qty", 0))
        ws.cell(row=row, column=5, value=hsn.get("val", 0))
        ws.cell(row=row, column=6, value=hsn.get("txval", 0))
        ws.cell(row=row, column=7, value=hsn.get("camt", 0))
        ws.cell(row=row, column=8, value=hsn.get("samt", 0))
    
    # Summary Sheet
    ws = wb.create_sheet("Summary")
    summary = data.get("summary", {})
    ws.cell(row=1, column=1, value="GSTR-1 Summary").font = Font(bold=True, size=14)
    ws.cell(row=3, column=1, value="Period:")
    ws.cell(row=3, column=2, value=summary.get("period", ""))
    ws.cell(row=4, column=1, value="Total Invoices:")
    ws.cell(row=4, column=2, value=summary.get("total_invoices", 0))
    ws.cell(row=5, column=1, value="B2B Count:")
    ws.cell(row=5, column=2, value=summary.get("b2b_count", 0))
    ws.cell(row=6, column=1, value="B2CL Count:")
    ws.cell(row=6, column=2, value=summary.get("b2cl_count", 0))
    ws.cell(row=7, column=1, value="B2CS Count:")
    ws.cell(row=7, column=2, value=summary.get("b2cs_count", 0))
    ws.cell(row=8, column=1, value="Total Taxable Value:")
    ws.cell(row=8, column=2, value=summary.get("total_taxable_value", 0))
    ws.cell(row=9, column=1, value="Total Tax:")
    ws.cell(row=9, column=2, value=summary.get("total_tax", 0))
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.read()
