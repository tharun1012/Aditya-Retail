import re

path = "/app/backend/orders_routes.py"
with open(path, "r") as f:
    content = f.read()

marker = '@router.get("/{order_id}")'
assert marker in content, "Could not find insertion marker"

export_route = '''
@router.get("/export")
async def export_orders(
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    store_code: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    format: str = "xlsx"
):
    """Export ALL orders matching filters (no pagination) as XLSX or CSV."""
    try:
        def normalize_offline(doc):
            return {
                "id": doc.get("id"),
                "order_number": doc.get("invoice_number"),
                "order_type": "offline",
                "customer_details": {
                    "name": (doc.get("customer") or {}).get("name"),
                    "email": (doc.get("customer") or {}).get("email"),
                    "phone": (doc.get("customer") or {}).get("phone"),
                },
                "items": doc.get("items", []),
                "total_amount": doc.get("total_amount"),
                "payment_status": doc.get("payment_status"),
                "order_status": doc.get("status"),
                "store_code": doc.get("store_code"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            }

        def date_range_filter():
            rng = {}
            if date_from:
                rng["$gte"] = f"{date_from}T00:00:00"
            if date_to:
                rng["$lte"] = f"{date_to}T23:59:59.999999"
            return rng

        date_filter = date_range_filter()
        online_docs = []
        offline_docs = []

        if order_type in (None, "all", "online"):
            online_query = {
                "$or": [
                    {"order_type": {"$ne": "offline"}},
                    {"order_type": {"$exists": False}},
                ]
            }
            if status:
                online_query["order_status"] = {"$in": ["placed", "pending"]} if status == "pending" else status
            if store_code:
                online_query["store_code"] = store_code
            if date_filter:
                online_query["created_at"] = date_filter
            cursor = db.orders.find(online_query, {"_id": 0}).sort("created_at", -1)
            online_docs = await cursor.to_list(length=None)

        if order_type in (None, "all", "offline"):
            offline_query = {"document_type": "invoice"}
            if status:
                offline_query["status"] = {"$in": ["pending_delivery"]} if status == "pending" else status
            if store_code:
                offline_query["store_code"] = store_code
            if date_filter:
                offline_query["created_at"] = date_filter
            cursor = db.offline_invoices.find(offline_query, {"_id": 0}).sort("created_at", -1)
            raw_offline = await cursor.to_list(length=None)
            offline_docs = [normalize_offline(d) for d in raw_offline]

        combined = online_docs + offline_docs
        combined.sort(key=lambda d: d.get("created_at") or "", reverse=True)

        headers = ["Order ID", "Customer Name", "Email", "Phone", "Date", "Items", "Total", "Order Status", "Payment Status", "Channel", "Store"]
        rows = []
        for o in combined:
            cust = o.get("customer_details") or {}
            rows.append({
                "Order ID": o.get("order_number") or o.get("id"),
                "Customer Name": cust.get("name"),
                "Email": cust.get("email"),
                "Phone": cust.get("phone"),
                "Date": (o.get("created_at") or "")[:10],
                "Items": len(o.get("items") or []),
                "Total": o.get("total_amount"),
                "Order Status": o.get("order_status"),
                "Payment Status": o.get("payment_status"),
                "Channel": o.get("order_type"),
                "Store": o.get("store_code"),
            })

        if format == "csv":
            buf = io.StringIO()
            writer = csv_module.DictWriter(buf, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
            byte_buf = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
            return StreamingResponse(
                byte_buf,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
            )
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Orders"
            ws.append(headers)
            for r in rows:
                ws.append([r[h] for h in headers])
            byte_buf = io.BytesIO()
            wb.save(byte_buf)
            byte_buf.seek(0)
            return StreamingResponse(
                byte_buf,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=orders_export.xlsx"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''

content = content.replace(marker, export_route + marker, 1)

with open(path, "w") as f:
    f.write(content)

print("Patched successfully.")
