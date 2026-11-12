import os, shutil
p = "/app/frontend/src/components/CustomerDashboard.js"
src = open(p).read()
if "AskAIAssistant" in src:
    raise SystemExit("already patched")
a = "import ChangePasswordCard from './ChangePasswordCard';"
b = "            {/* Addresses Tab */}"
print("anchors:", src.count(a), src.count(b))
if src.count(a) != 1 or src.count(b) != 1:
    raise SystemExit("ABORT: anchors not unique, nothing written")
os.makedirs("/app/_backup/aiui", exist_ok=True)
shutil.copy(p, "/app/_backup/aiui/CustomerDashboard.js")
src = src.replace(a, a + "\nimport AskAIAssistant from './AskAIAssistant';")
src = src.replace(b, "            {user && <AskAIAssistant user={user} />}\n\n" + b)
open(p, "w").write(src); print("patched")
