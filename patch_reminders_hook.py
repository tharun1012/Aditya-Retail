import shutil, py_compile, os
p = "/app/backend/server.py"
s = open(p).read()
if "customer_reminders" in s:
    raise SystemExit("already patched")
a = '''            logger.warning(f"⚠️ Shiprocket tracking loop init failed: {_sr_le}")
'''
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
add = '''
        # Customer reminders: warranty expiry + consumable reorder emails (daily 9 AM IST)
        try:
            from customer_reminders import reminders_loop
            asyncio.create_task(reminders_loop(db))
            logger.info("⏰ Customer reminders loop started (daily 9 AM IST)")
        except Exception as _rm_e:
            logger.warning(f"⚠️ Customer reminders loop init failed: {_rm_e}")
'''
new = s.replace(a, a + add, 1)
open("/tmp/server_test.py", "w").write(new)
py_compile.compile("/tmp/server_test.py", doraise=True)
os.makedirs("/app/_backup/reminders", exist_ok=True)
shutil.copy(p, "/app/_backup/reminders/server.py")
open(p, "w").write(new)
print("written OK")
