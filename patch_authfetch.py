import shutil, os
base = "/app/frontend/src/components/"
targets = {
  "CustomerDashboard.js": "import ChangePasswordCard from './ChangePasswordCard';",
  "AskAIAssistant.js": "import React, { useState, useRef, useEffect } from 'react';",
}
os.makedirs("/app/_backup/authfetch", exist_ok=True)
plan = {}
for f, anchor in targets.items():
    s = open(base + f).read()
    if "authFetch" in s:
        print(f, "already patched"); continue
    if s.count(anchor) != 1:
        raise SystemExit(f"ABORT: anchor in {f} found {s.count(anchor)} times, nothing written")
    plan[f] = s
for f, s in plan.items():
    shutil.copy(base + f, f"/app/_backup/authfetch/{f}")
    n = s.count("fetch(`${BACKEND_URL}/api/customer/")
    s = s.replace("fetch(`${BACKEND_URL}/api/customer/", "authFetch(`${BACKEND_URL}/api/customer/")
    a = targets[f]
    s = s.replace(a, a + "\nimport authFetch from './authFetch';", 1)
    open(base + f, "w").write(s)
    print(f, "->", n, "calls updated")
