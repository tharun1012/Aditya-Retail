import re, shutil, py_compile, os
p = "/app/backend/customer_dashboard_routes.py"
src = open(p).read()
if "verify_self" in src:
    raise SystemExit("already patched")
imp = "from database import get_db"
if src.count(imp) != 1:
    raise SystemExit("ABORT: import anchor not unique, nothing written")

pat = re.compile(r"(async def (\w+)\()(.*?)(\)\s*:\n)", re.S)
done, skipped = [], []
def fix(m):
    name, params = m.group(2), m.group(3)
    if "user_id" not in params:
        return m.group(0)
    if "database = Depends(get_db)" in params:
        params = params.replace("database = Depends(get_db)",
                                "database = Depends(get_db), _auth = Depends(verify_self)", 1)
        done.append(name)
        return m.group(1) + params + m.group(4)
    skipped.append(name)
    return m.group(0)

new = pat.sub(fix, src)
new = new.replace(imp, imp + "\nfrom customer_auth_guard import verify_self", 1)
print("patched:", len(done), done)
print("NOT patched (check manually):", skipped)

tmp = "/tmp/cdr_test.py"
open(tmp, "w").write(new)
py_compile.compile(tmp, doraise=True)
os.makedirs("/app/_backup/guard", exist_ok=True)
shutil.copy(p, "/app/_backup/guard/customer_dashboard_routes.py")
open(p, "w").write(new)
print("written OK")
