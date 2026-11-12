import shutil, py_compile, os
p = "/app/backend/customer_dashboard_routes.py"
src = open(p).read()
if "def update_address" in src:
    raise SystemExit("already patched")

a1 = '@router.delete("/addresses/{address_id}")'
a2 = '''        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Address not found")
'''
print("anchors:", src.count(a1), src.count(a2))
if src.count(a1) != 1 or src.count(a2) != 1:
    raise SystemExit("ABORT: anchors not unique, nothing written")

put_route = '''@router.put("/addresses/{address_id}")
async def update_address(address_id: str, user_id: str, address: AddressCreate, database = Depends(get_db), _auth = Depends(verify_self)):
    """Edit a saved address"""
    try:
        existing = await database.customer_addresses.find_one({"id": address_id, "user_id": user_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Address not found")
        data = address.dict()
        if existing.get("is_default"):
            data["is_default"] = True  # never leave the customer without a default
        if data.get("is_default"):
            await database.customer_addresses.update_many(
                {"user_id": user_id, "id": {"$ne": address_id}},
                {"$set": {"is_default": False}}
            )
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await database.customer_addresses.update_one({"id": address_id, "user_id": user_id}, {"$set": data})
        return {"status": "success", "message": "Address updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''
promote = a2 + '''        # if the default was deleted, make the newest remaining address the default
        if not await database.customer_addresses.find_one({"user_id": user_id, "is_default": True}):
            nxt = await database.customer_addresses.find_one({"user_id": user_id}, sort=[("created_at", -1)])
            if nxt:
                await database.customer_addresses.update_one({"id": nxt["id"]}, {"$set": {"is_default": True}})
'''
new = src.replace(a1, put_route + a1, 1).replace(a2, promote, 1)
open("/tmp/cdr_test.py", "w").write(new)
py_compile.compile("/tmp/cdr_test.py", doraise=True)
os.makedirs("/app/_backup/addr", exist_ok=True)
shutil.copy(p, "/app/_backup/addr/customer_dashboard_routes.py")
open(p, "w").write(new)
print("written OK")
