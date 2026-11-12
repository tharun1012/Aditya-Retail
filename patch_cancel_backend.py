import shutil, py_compile, os
p = "/app/backend/customer_dashboard_routes.py"
s = open(p).read()
if "def cancel_my_order" in s:
    raise SystemExit("already patched")
a = '@router.delete("/addresses/{address_id}")'
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
route = '''@router.post("/orders/{order_id}/cancel")
async def cancel_my_order(order_id: str, user_id: str, reason: Optional[str] = None, database = Depends(get_db), _auth = Depends(verify_self)):
    """Customer cancels their own order, only before it ships"""
    try:
        order = await database.orders.find_one({"id": order_id, "customer_id": user_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        status = str(order.get("order_status") or "placed").lower()
        allowed = ["placed", "pending", "confirmed"]
        if status not in allowed or order.get("sr_awb_code") or order.get("shiprocket_order_id"):
            raise HTTPException(status_code=400, detail="This order is already being processed or shipped. Please contact support to cancel it.")
        now = datetime.now(timezone.utc).isoformat()
        why = (reason or "Cancelled by customer").strip()[:200]
        paid = str(order.get("payment_status") or "").lower() in ("completed", "paid", "success", "captured", "successful")
        set_fields = {"order_status": "cancelled", "status": "cancelled", "updated_at": now,
                      "cancelled_at": now, "cancel_reason": why}
        if paid:
            set_fields["refund_status"] = "pending"
        res = await database.orders.update_one(
            {"id": order_id, "customer_id": user_id, "order_status": {"$in": allowed}},
            {"$set": set_fields,
             "$push": {"timeline": {"status": "cancelled", "timestamp": now,
                                    "message": f"Order cancelled by customer. Reason: {why}",
                                    "updated_by": "customer"}}})
        if res.modified_count != 1:
            raise HTTPException(status_code=400, detail="This order can no longer be cancelled.")
        for item in order.get("items", []):
            try:
                if item.get("product_id"):
                    await database.products.update_one(
                        {"id": item["product_id"]}, {"$inc": {"stock": int(item.get("quantity") or 1)}})
            except Exception as e:
                print(f"Stock restore error (non-blocking): {e}")
        try:
            from notifications_routes import notify_order_status_change
            await notify_order_status_change(database, order, status, "cancelled")
        except Exception as e:
            print(f"Cancel notification error (non-blocking): {e}")
        return {"status": "success",
                "message": "Order cancelled." + (" Your refund will be processed by our team." if paid else "")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''
new = s.replace(a, route + a, 1)
open("/tmp/cdr_test.py", "w").write(new)
py_compile.compile("/tmp/cdr_test.py", doraise=True)
os.makedirs("/app/_backup/cancel", exist_ok=True)
shutil.copy(p, "/app/_backup/cancel/customer_dashboard_routes.py")
open(p, "w").write(new)
print("written OK")
