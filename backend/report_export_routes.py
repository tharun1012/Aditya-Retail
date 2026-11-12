"""
Report Export Routes - PDF and Excel export for Advanced Reports
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from database import get_db
from io import BytesIO
import uuid

router = APIRouter(prefix="/reports/export", tags=["Report Export"])

# ============ PDF GENERATION ============

def generate_report_pdf(title: str, headers: List[str], data: List[List], summary: Dict = None):
    """Generate a PDF report using reportlab"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor('#1e3a5f')
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary section if provided
    if summary:
        summary_text = " | ".join([f"<b>{k}:</b> {v}" for k, v in summary.items()])
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Create table with headers
    table_data = [headers] + data
    
    # Calculate column widths
    available_width = landscape(A4)[0] - 60  # Account for margins
    col_width = available_width / len(headers)
    col_widths = [col_width] * len(headers)
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Style the table
    table_style = TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Data row styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#1e3a5f')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1e3a5f')),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
    elements.append(Paragraph("Aditya Retail - Premium Bosch & Siemens Products", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============ EXCEL GENERATION ============

def generate_report_excel(title: str, headers: List[str], data: List[List], summary: Dict = None):
    """Generate an Excel report using openpyxl"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]  # Excel limit
    
    # Styles
    header_fill = PatternFill(start_color="1e3a5f", end_color="1e3a5f", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    data_font = Font(size=10)
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    row_num = 1
    
    # Title
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.cell(row=1, column=1, value=title).font = Font(bold=True, size=14)
    row_num += 1
    
    # Generated date
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    ws.cell(row=2, column=1, value=f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}").font = Font(size=9, color="666666")
    row_num += 1
    
    # Summary if provided
    if summary:
        row_num += 1
        for col, (key, value) in enumerate(summary.items(), start=1):
            ws.cell(row=row_num, column=col, value=f"{key}: {value}").font = Font(bold=True, size=10)
        row_num += 1
    
    row_num += 1  # Blank row
    
    # Headers
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    row_num += 1
    
    # Data rows
    alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    for idx, row_data in enumerate(data):
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_num, column=col, value=value)
            cell.font = data_font
            cell.border = thin_border
            if idx % 2 == 1:
                cell.fill = alt_fill
        row_num += 1
    
    # Auto-adjust column widths
    for col in range(1, len(headers) + 1):
        max_length = max(
            len(str(headers[col - 1])),
            max((len(str(row[col - 1])) for row in data), default=0)
        )
        ws.column_dimensions[get_column_letter(col)].width = min(max_length + 2, 50)
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ============ EXPORT ENDPOINTS ============

@router.get("/sales/{report_type}")
async def export_sales_report(
    report_type: str,  # daily, monthly, yearly, item-wise
    format: str = Query("excel", enum=["pdf", "excel"]),
    date: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    store_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Export sales reports in PDF or Excel format"""
    try:
        from dateutil import parser
        
        now = datetime.now(timezone.utc)
        
        # Determine date range based on report type
        if report_type == "daily":
            if date:
                report_date = parser.parse(date).replace(tzinfo=timezone.utc)
            else:
                report_date = now
            start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = report_date.replace(hour=23, minute=59, second=59)
            title = f"Daily Sales Report - {start.strftime('%d %B %Y')}"
            
        elif report_type == "monthly":
            year = year or now.year
            month = month or now.month
            start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
            if month == 12:
                end = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(seconds=1)
            else:
                end = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(seconds=1)
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            title = f"Monthly Sales Report - {month_names[month-1]} {year}"
            
        elif report_type == "yearly":
            year = year or now.year
            start = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            title = f"Yearly Sales Report - {year}"
            
        elif report_type == "item-wise":
            if from_date:
                start = parser.parse(from_date).replace(tzinfo=timezone.utc)
            else:
                start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            if to_date:
                end = parser.parse(to_date).replace(tzinfo=timezone.utc)
            else:
                end = now
            title = f"Item-wise Sales Report ({start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')})"
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Build query
        match_query = {
            "created_at": {"$gte": start, "$lte": end},
            "payment_status": {"$in": ["completed", "paid"]}
        }
        if store_id:
            match_query["store_id"] = store_id
        
        # Fetch data based on report type
        if report_type == "item-wise":
            pipeline = [
                {"$match": match_query},
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "quantity_sold": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "order_count": {"$sum": 1},
                    "avg_price": {"$avg": "$items.price"}
                }},
                {"$sort": {"total_revenue": -1}},
                {"$limit": 500}
            ]
            results = await db.orders.aggregate(pipeline).to_list(None)
            
            headers = ["Product Name", "Qty Sold", "Orders", "Avg Price (₹)", "Total Revenue (₹)"]
            data = []
            for r in results:
                data.append([
                    r.get("product_name", "Unknown")[:40],
                    r.get("quantity_sold", 0),
                    r.get("order_count", 0),
                    f"₹{r.get('avg_price', 0):,.0f}",
                    f"₹{r.get('total_revenue', 0):,.0f}"
                ])
            
            summary = {
                "Total Products": len(results),
                "Total Qty Sold": sum(r.get("quantity_sold", 0) for r in results),
                "Total Revenue": f"₹{sum(r.get('total_revenue', 0) for r in results):,.0f}"
            }
        else:
            # Order-based reports
            orders = await db.orders.find(
                match_query,
                {"_id": 0, "order_number": 1, "customer_name": 1, "total_amount": 1, 
                 "payment_method": 1, "order_status": 1, "created_at": 1}
            ).sort("created_at", -1).limit(1000).to_list(None)
            
            headers = ["Order #", "Customer", "Date", "Amount (₹)", "Payment", "Status"]
            data = []
            for o in orders:
                data.append([
                    o.get("order_number", "N/A"),
                    (o.get("customer_name") or "N/A")[:30],
                    o.get("created_at").strftime("%d-%b-%Y") if o.get("created_at") else "N/A",
                    f"₹{o.get('total_amount', 0):,.0f}",
                    o.get("payment_method", "N/A"),
                    o.get("order_status", "N/A")
                ])
            
            total_sales = sum(o.get("total_amount", 0) for o in orders)
            summary = {
                "Total Orders": len(orders),
                "Total Sales": f"₹{total_sales:,.0f}",
                "Avg Order Value": f"₹{(total_sales / len(orders) if orders else 0):,.0f}"
            }
        
        # Generate file
        if format == "pdf":
            buffer = generate_report_pdf(title, headers, data, summary)
            filename = f"sales_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:
            buffer = generate_report_excel(title, headers, data, summary)
            filename = f"sales_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchases/{report_type}")
async def export_purchases_report(
    report_type: str,  # item-wise, vendor-wise, date-wise
    format: str = Query("excel", enum=["pdf", "excel"]),
    store_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Export purchases reports"""
    try:
        from dateutil import parser
        
        now = datetime.now(timezone.utc)
        if from_date:
            start = parser.parse(from_date).replace(tzinfo=timezone.utc)
        else:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        if to_date:
            end = parser.parse(to_date).replace(tzinfo=timezone.utc)
        else:
            end = now
        
        match_query = {"created_at": {"$gte": start, "$lte": end}}
        if store_id:
            match_query["store_id"] = store_id
        
        title = f"Purchases Report - {report_type.replace('-', ' ').title()} ({start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')})"
        
        if report_type == "item-wise":
            pipeline = [
                {"$match": match_query},
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "quantity": {"$sum": "$items.quantity"},
                    "total_cost": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "avg_price": {"$avg": "$items.price"}
                }},
                {"$sort": {"total_cost": -1}},
                {"$limit": 500}
            ]
            results = await db.purchase_bills.aggregate(pipeline).to_list(None)
            
            headers = ["Product Name", "Qty Purchased", "Avg Price (₹)", "Total Cost (₹)"]
            data = [[
                r.get("product_name", "Unknown")[:40],
                r.get("quantity", 0),
                f"₹{r.get('avg_price', 0):,.0f}",
                f"₹{r.get('total_cost', 0):,.0f}"
            ] for r in results]
            
            summary = {
                "Total Items": len(results),
                "Total Cost": f"₹{sum(r.get('total_cost', 0) for r in results):,.0f}"
            }
        else:
            # Bill-based
            bills = await db.purchase_bills.find(
                match_query,
                {"_id": 0, "bill_number": 1, "vendor_name": 1, "total_amount": 1, 
                 "payment_status": 1, "created_at": 1}
            ).sort("created_at", -1).limit(1000).to_list(None)
            
            headers = ["Bill #", "Vendor", "Date", "Amount (₹)", "Payment Status"]
            data = [[
                b.get("bill_number", "N/A"),
                (b.get("vendor_name") or "N/A")[:30],
                b.get("created_at").strftime("%d-%b-%Y") if b.get("created_at") else "N/A",
                f"₹{b.get('total_amount', 0):,.0f}",
                b.get("payment_status", "N/A")
            ] for b in bills]
            
            summary = {
                "Total Bills": len(bills),
                "Total Amount": f"₹{sum(b.get('total_amount', 0) for b in bills):,.0f}"
            }
        
        # Generate file
        if format == "pdf":
            buffer = generate_report_pdf(title, headers, data, summary)
            filename = f"purchases_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:
            buffer = generate_report_excel(title, headers, data, summary)
            filename = f"purchases_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending/{report_type}")
async def export_pending_report(
    report_type: str,  # deliveries, purchase-orders, purchase-bills
    format: str = Query("excel", enum=["pdf", "excel"]),
    store_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Export pending reports"""
    try:
        if report_type == "deliveries":
            query = {
                "order_status": {"$in": ["confirmed", "processing", "shipped", "out_for_delivery"]},
                "payment_status": {"$in": ["completed", "paid", "cod"]}
            }
            if store_id:
                query["store_id"] = store_id
            
            orders = await db.orders.find(query, {"_id": 0}).sort("created_at", 1).to_list(None)
            
            title = "Pending Deliveries Report"
            headers = ["Order #", "Customer", "Date", "Amount (₹)", "Status", "City"]
            data = [[
                o.get("order_number", "N/A"),
                (o.get("customer_name") or "N/A")[:25],
                o.get("created_at").strftime("%d-%b-%Y") if o.get("created_at") else "N/A",
                f"₹{o.get('total_amount', 0):,.0f}",
                o.get("order_status", "N/A"),
                o.get("shipping_address", {}).get("city", "N/A")[:15] if isinstance(o.get("shipping_address"), dict) else "N/A"
            ] for o in orders]
            
            summary = {
                "Total Pending": len(orders),
                "Total Amount": f"₹{sum(o.get('total_amount', 0) for o in orders):,.0f}"
            }
            
        elif report_type == "purchase-orders":
            query = {"status": {"$in": ["pending", "partial", "approved"]}}
            if store_id:
                query["store_id"] = store_id
            
            pos = await db.purchases.find(query, {"_id": 0}).sort("created_at", -1).to_list(None)
            
            title = "Pending Purchase Orders Report"
            headers = ["PO #", "Vendor", "Date", "Amount (₹)", "Status"]
            data = [[
                p.get("po_number", "N/A"),
                (p.get("vendor_name") or "N/A")[:30],
                p.get("created_at").strftime("%d-%b-%Y") if p.get("created_at") else "N/A",
                f"₹{p.get('total_amount', 0):,.0f}",
                p.get("status", "N/A")
            ] for p in pos]
            
            summary = {
                "Total POs": len(pos),
                "Total Amount": f"₹{sum(p.get('total_amount', 0) for p in pos):,.0f}"
            }
            
        elif report_type == "purchase-bills":
            query = {"payment_status": {"$in": ["pending", "partial"]}}
            if store_id:
                query["store_id"] = store_id
            
            bills = await db.purchase_bills.find(query, {"_id": 0}).sort("due_date", 1).to_list(None)
            
            title = "Pending Purchase Bills Report"
            now = datetime.now(timezone.utc)
            headers = ["Bill #", "Vendor", "Due Date", "Amount (₹)", "Status", "Overdue"]
            data = []
            for b in bills:
                due_date = b.get("due_date")
                is_overdue = "Yes" if due_date and due_date < now else "No"
                data.append([
                    b.get("bill_number", "N/A"),
                    (b.get("vendor_name") or "N/A")[:30],
                    due_date.strftime("%d-%b-%Y") if due_date else "N/A",
                    f"₹{b.get('total_amount', 0):,.0f}",
                    b.get("payment_status", "N/A"),
                    is_overdue
                ])
            
            summary = {
                "Total Bills": len(bills),
                "Total Due": f"₹{sum(b.get('total_amount', 0) for b in bills):,.0f}"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Generate file
        if format == "pdf":
            buffer = generate_report_pdf(title, headers, data, summary)
            filename = f"pending_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:
            buffer = generate_report_excel(title, headers, data, summary)
            filename = f"pending_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inventory")
async def export_inventory_report(
    format: str = Query("excel", enum=["pdf", "excel"]),
    store_id: Optional[str] = None,
    low_stock_only: bool = False,
    db = Depends(get_db)
):
    """Export inventory report"""
    try:
        if store_id:
            # Single store inventory
            inventory = await db.store_inventory.find_one({"store_id": store_id})
            store = await db.stores.find_one({"id": store_id})
            store_name = store.get("name") if store else "Unknown Store"
            title = f"Inventory Report - {store_name}"
        else:
            # All stores combined
            inventories = await db.store_inventory.find({}, {"_id": 0}).to_list(None)
            combined = {}
            for inv in inventories:
                for product_id, qty in inv.get("products", {}).items():
                    combined[product_id] = combined.get(product_id, 0) + qty
            inventory = {"products": combined}
            title = "Inventory Report - All Stores"
        
        if not inventory or not inventory.get("products"):
            raise HTTPException(status_code=404, detail="No inventory data found")
        
        # Get product details
        product_ids = list(inventory.get("products", {}).keys())
        products = await db.products.find(
            {"id": {"$in": product_ids}},
            {"_id": 0, "id": 1, "name": 1, "sku": 1, "category": 1, "price": 1}
        ).to_list(None)
        
        product_map = {p["id"]: p for p in products}
        
        headers = ["Product Name", "SKU", "Category", "Price (₹)", "Qty", "Stock Value (₹)", "Status"]
        data = []
        total_value = 0
        
        for product_id, qty in inventory.get("products", {}).items():
            product = product_map.get(product_id, {})
            is_low_stock = qty < 5
            
            if low_stock_only and not is_low_stock:
                continue
            
            price = product.get("price", 0)
            stock_value = qty * price
            total_value += stock_value
            
            data.append([
                product.get("name", "Unknown")[:35],
                product.get("sku", "N/A"),
                product.get("category", "N/A")[:15],
                f"₹{price:,.0f}",
                qty,
                f"₹{stock_value:,.0f}",
                "LOW STOCK" if is_low_stock else "OK"
            ])
        
        # Sort by quantity (low first)
        data.sort(key=lambda x: x[4])
        
        summary = {
            "Total Products": len(data),
            "Total Stock": sum(d[4] for d in data),
            "Total Value": f"₹{total_value:,.0f}",
            "Low Stock Items": len([d for d in data if d[6] == "LOW STOCK"])
        }
        
        # Generate file
        if format == "pdf":
            buffer = generate_report_pdf(title, headers, data, summary)
            filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:
            buffer = generate_report_excel(title, headers, data, summary)
            filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
