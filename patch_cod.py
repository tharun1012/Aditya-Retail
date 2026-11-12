import shutil, py_compile, os
p = "/app/backend/customer_lifecycle.py"
s = open(p).read()
if "cod_collected_at" in s:
    raise SystemExit("already patched")
a = '    """Idempotent. Registers appliances (warranty) and records consumable purchases (reorder reminders)."""\n'
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
add = '''    try:
        _pm = str(order.get("payment_method") or "").lower()
        _ps = str(order.get("payment_status") or "pending").lower()
        if order.get("id") and _ps in ("pending", "unpaid", "") and ("cod" in _pm or "cash" in _pm):
            await db.orders.update_one(
                {"id": order["id"]},
                {"$set": {"payment_status": "completed", "cod_collected_at": _now().isoformat()}})
    except Exception as _e:
        print(f"COD payment update error (non-blocking): {_e}")
'''
new = s.replace(a, a + add, 1)
open("/tmp/cl_test.py", "w").write(new)
py_compile.compile("/tmp/cl_test.py", doraise=True)
os.makedirs("/app/_backup/cod", exist_ok=True)
shutil.copy(p, "/app/_backup/cod/customer_lifecycle.py")
open(p, "w").write(new)
print("written OK")
