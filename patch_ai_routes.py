import os, shutil
p = "/app/backend/server.py"
src = open(p).read()
if "customer_ai_router" in src:
    raise SystemExit("already patched")
a = "api_router.include_router(customer_password_router)\n"
if src.count(a) != 1:
    raise SystemExit(f"ABORT: anchor found {src.count(a)} times")
os.makedirs("/app/_backup/ai", exist_ok=True)
shutil.copy(p, "/app/_backup/ai/server.py")
src = src.replace(a, a + "from customer_ai_routes import router as customer_ai_router\n"
                        "api_router.include_router(customer_ai_router)\n")
open(p, "w").write(src); print("server.py patched")
