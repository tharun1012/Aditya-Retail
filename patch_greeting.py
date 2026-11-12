import shutil, os
p = "/app/frontend/src/components/HomeTab.js"
s = open(p).read()
old = "{user && (user.name || user.full_name) ? (user.name || user.full_name) : 'there'}"
print("anchor count:", s.count(old))
if s.count(old) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
new = "{(user && (user.first_name || (user.email || '').split('@')[0])) || 'there'}"
os.makedirs("/app/_backup/greeting", exist_ok=True)
shutil.copy(p, "/app/_backup/greeting/HomeTab.js")
open(p, "w").write(s.replace(old, new, 1))
print("written OK")
