import shutil, os
p = "/app/backend/server.py"
src = open(p).read()
if "customer_password_router" in src:
    raise SystemExit("already patched")
a = "api_router.include_router(auth_router)\n"
if src.count(a) != 1:
    raise SystemExit(f"ABORT: anchor found {src.count(a)} times")
os.makedirs("/app/_backup/pw", exist_ok=True)
shutil.copy(p, "/app/_backup/pw/server.py")
src = src.replace(a, a + "from customer_password_routes import router as customer_password_router\n"
                        "api_router.include_router(customer_password_router)\n")
open(p, "w").write(src); print("server.py patched")
