import shutil, os
p = "/app/frontend/src/App.js"
src = open(p).read()
if "ResetPassword" in src:
    raise SystemExit("already patched")
a = "import LoginPage from './components/LoginPage';"
b = '<Route path="/my-account" element={<CustomerDashboard />} />'
print("import anchor:", src.count(a), "| route anchor:", src.count(b))
if src.count(a) != 1 or src.count(b) != 1:
    raise SystemExit("ABORT: anchors not unique, nothing written")
os.makedirs("/app/_backup/fe", exist_ok=True)
shutil.copy(p, "/app/_backup/fe/App.js")
src = src.replace(a, a + "\nimport ResetPassword from './components/ResetPassword';")
src = src.replace(b, '<Route path="/reset-password" element={<ResetPassword />} />\n          ' + b)
open(p, "w").write(src)
print("App.js patched")
