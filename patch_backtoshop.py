import shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "Back to Shop" in s:
    raise SystemExit("already patched")
a = '''        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">'''
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
new_block = '''        <div className="max-w-7xl mx-auto px-4 py-8">
          <Link to="/" className="inline-flex items-center gap-1 text-sm text-blue-100 hover:text-white mb-4">
            &larr; Back to Shop
          </Link>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">'''
os.makedirs("/app/_backup/backtoshop", exist_ok=True)
shutil.copy(p, "/app/_backup/backtoshop/CustomerDashboard.js")
open(p, "w").write(s.replace(a, new_block, 1))
print("written OK")
