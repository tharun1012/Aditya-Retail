import re, shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "HomeTab" in s:
    raise SystemExit("already patched")
imp   = "import AskAIAssistant from './AskAIAssistant';"
dflt  = "useState('orders')"
tabre = re.compile(r"\{ id: 'orders', label:")
render = "{activeTab === 'orders' && ("
counts = {"import": s.count(imp), "default": s.count(dflt), "tab": len(tabre.findall(s)), "render": s.count(render)}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")
s = s.replace(imp, imp + "\nimport HomeTab from './HomeTab';\nimport { Home as HomeIcon } from 'lucide-react';", 1)
s = s.replace(dflt, "useState('home')", 1)
s = tabre.sub("{ id: 'home', label: 'Home', icon: HomeIcon },\n                  { id: 'orders', label:", s, count=1)
s = s.replace(render, "{activeTab === 'home' && user && (\n              <HomeTab user={user} orders={orders} myProducts={myProducts} serviceRequests={serviceRequests} suggestions={consumableSuggestions} setActiveTab={setActiveTab} onViewOrder={fetchOrderDetail} />\n            )}\n\n            " + render, 1)
os.makedirs("/app/_backup/home", exist_ok=True)
open("/app/_backup/home/CustomerDashboard.js", "w").write(open(p).read())
open(p, "w").write(s)
print("written OK")
